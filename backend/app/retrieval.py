import re
import math
from collections import Counter
import numpy as np

STOP = set('the a an of for my to and in on is was i me it that with about from where find document file'.split())

def tokens(text):
    return [t for t in re.findall(r'\w+', text.lower()) if t not in STOP]

def rank(query, vector, rows, threshold=0.5, mode='hybrid'):
    """BM25 + cosine fusion; abstention gate uses meaningful lexical/semantic evidence."""
    if not rows:
        return []
    terms = tokens(query)
    bags = [Counter(tokens(r['text'])) for r in rows]
    avg_len = sum(sum(b.values()) for b in bags) / max(len(bags), 1)
    df = {t: sum(t in b for b in bags) for t in set(terms)}
    # Weak semantic matches need separation from a different content cluster.
    # Near-identical versions must not make a good query appear ambiguous.
    vectors = [np.asarray(row['vector'], dtype=np.float32) for row in rows]
    similarities = [float(v @ vector) if v.shape == vector.shape else -1.0 for v in vectors]
    best = max(range(len(rows)), key=lambda i: similarities[i])
    alternatives = [similarities[i] for i, v in enumerate(vectors)
                    if v.shape == vectors[best].shape and float(v @ vectors[best]) < 0.92]
    separation = similarities[best] - max(alternatives, default=-1.0)
    semantic_clear = similarities[best] >= 0.60 or separation >= 0.08
    scored = []
    for index, (row, bag) in enumerate(zip(rows, bags)):
        lexical = 0.0
        for term in terms:
            freq = bag[term]
            if freq:
                idf = math.log(1 + (len(rows) - df[term] + 0.5) / (df[term] + 0.5))
                lexical += idf * freq * 2.2 / (freq + 1.2 * (0.25 + 0.75 * sum(bag.values()) / max(avg_len, 1)))
        sem = similarities[index]
        semantic_gate = sem >= threshold and semantic_clear
        coverage = len(set(terms) & bag.keys()) / max(len(set(terms)), 1)
        lexical_gate = coverage >= 0.5 and lexical > 0
        if mode == 'keyword':
            eligible, score = lexical > 0, lexical
        elif mode == 'semantic':
            eligible, score = semantic_gate, sem
        else:
            eligible = semantic_gate or lexical_gate
            score = 0.8 * sem + 0.2 * lexical / (lexical + 2)
        if eligible:
            kind = 'hybrid' if semantic_gate and lexical_gate else ('semantic' if semantic_gate else 'keyword')
            scored.append((score, row, kind, sem, lexical))
    scored.sort(key=lambda x: (-x[0], x[1]['file_id']))
    unique = {}
    for hit in scored:
        unique.setdefault(hit[1]['file_id'], hit)
    return list(unique.values())
