"""File-level BM25/cosine fusion. Scores stay internal, never confidence values."""
import math
import re
from collections import Counter, defaultdict
import numpy as np

STOP = set('the a an of for my to and in on is was i me it that with about from where find document file'.split())
KEYWORD_WEIGHT = 0.20
MIN_FUSED_SCORE = 0.35  # Calibrated on tuning queries by evaluation/phase_a4.py.


def tokens(text):
    return [t for t in re.findall(r'\w+', text.lower()) if t not in STOP]


def rank(query, vector, rows, threshold=0.53, mode='hybrid', *, keyword_weight=None, min_fused_score=None):
    """Max-chunk file aggregation: (fused_score, best_source_row, kind, cosine, BM25).

    BM25 k1=1.2, b=.75; IDF counts files rather than chunks. Normalize lexical
    scores by B/(B+2), then F=(1-w)*cosine + w*normalized_BM25. Acceptance
    gates are independent of rank/limit: semantic threshold + ambiguity test,
    or >=.5 unique query-token coverage, plus a calibrated hybrid F cutoff.
    """
    if not rows:
        return []
    weight = KEYWORD_WEIGHT if keyword_weight is None else keyword_weight
    cutoff = MIN_FUSED_SCORE if min_fused_score is None else min_fused_score
    terms = set(tokens(query))
    bags = [Counter(tokens(r['text'])) for r in rows]
    lengths = np.array([sum(b.values()) for b in bags], dtype=np.float32)
    avg_len = max(float(lengths.mean()), 1.0)
    file_terms = defaultdict(set)
    for row, bag in zip(rows, bags):
        file_terms[row['file_id']].update(bag)
    file_count = len(file_terms)
    idfs = {t: math.log(1 + (file_count - sum(t in b for b in file_terms.values()) + .5) /
                              (sum(t in b for b in file_terms.values()) + .5)) for t in terms}

    # Brute-force contiguous numpy matrix: no vector database or ANN approximation.
    matrix = np.asarray([r['vector'] for r in rows], dtype=np.float32)
    vector = np.asarray(vector, dtype=np.float32)
    similarities = matrix @ vector
    best = int(np.argmax(similarities))
    different_cluster = (matrix @ matrix[best]) < .92
    separation = float(similarities[best] - np.max(similarities[different_cluster])) if different_cluster.any() else float('inf')
    semantic_clear = similarities[best] >= .60 or separation >= .08
    scored = []
    for i, (row, bag) in enumerate(zip(rows, bags)):
        lexical = 0.0
        for term in terms:
            freq = bag[term]
            if freq:
                lexical += idfs[term] * freq * 2.2 / (freq + 1.2 * (.25 + .75 * lengths[i] / avg_len))
        sem = float(similarities[i])
        semantic_gate = sem >= threshold and semantic_clear
        coverage = len(terms & bag.keys()) / max(len(terms), 1)
        lexical_gate = coverage >= .5 and lexical > 0
        if mode == 'keyword':
            eligible, score = lexical > 0, lexical
        elif mode == 'semantic':
            eligible, score = semantic_gate, sem
        else:
            score = (1-weight) * sem + weight * lexical / (lexical + 2)
            eligible = (semantic_gate or lexical_gate) and score >= cutoff
        if eligible:
            kind = 'hybrid' if semantic_gate and lexical_gate else ('semantic' if semantic_gate else 'keyword')
            scored.append((float(score), row, kind, sem, float(lexical)))
    # A long file cannot crowd out other files. Ties select deterministic source/page.
    scored.sort(key=lambda x: (-x[0], x[1]['file_id'], x[1].get('page') or 0, x[1]['text']))
    unique = {}
    for hit in scored:
        unique.setdefault(hit[1]['file_id'], hit)
    return list(unique.values())
