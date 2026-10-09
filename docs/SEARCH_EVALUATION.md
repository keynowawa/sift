# Retrieval evaluation — Phase A4/A5, 2026-10-10

Synthetic, hand-authored evidence only. v1 responses are unchanged: no numeric scores or confidence percentages are exposed. Search can return `results: []`; result limits are applied only after acceptance and file aggregation.

## Current fusion and abstention

`backend/app/retrieval.py` computes BM25 per source chunk (k1=1.2, b=.75). IDF counts distinct files containing each query token, so extra chunks do not multiply document frequency. Query tokens are unique, lowercased, with the existing stop words removed. Normalize BM25 as L=B/(B+2); fuse F=0.8*cosine+0.2*L. Cosine uses normalized float32 Ollama embeddings.

Accept a chunk only if F>=0.35 AND either (a) cosine>=0.53 with the existing semantic ambiguity gate, or (b) at least half of unique query tokens occur in that chunk and BM25>0. The ambiguity gate allows the best cosine>=0.60 or a gap>=0.08 from the best different content cluster; chunks with cosine>=0.92 to the best chunk are treated as copies for this comparison. This gate applies to semantic eligibility, not the keyword route. These internal cutoffs are heuristics, not probabilities.

Sort accepted chunks by fused score, then stable file ID/page/text ties. Keep the maximum-scoring accepted chunk for each file; its real source text and page become the snippet/location. Apply top-k to distinct accepted files. No arbitrary result is added to fill k. Long files cannot occupy multiple results, though their extra chances to match can still bias max-chunk aggregation.

## Calibration and split integrity

Reproducer: `PYTHONPATH=backend python backend/evaluation/phase_a4.py`, using the installed local `nomic-embed-text:v1.5`, unchanged prefixes/context/model digest documented below. Eighteen new short synthetic TXT-equivalent passages are embedded through actual Ollama; this isolates retrieval and does not retest OCR/PDF extraction. Eight positive plus five no-match tuning queries are separate from ten positive plus five final held-out queries. All labels and query lists are committed in the script.

Retain cosine threshold 0.53. Grid: keyword weights 0.20/0.35/0.50 and fused cutoffs 0.35/0.40/0.45/0.50/0.55/0.60. Objective = positive top-3 fraction + 2*correct no-match fraction, emphasizing abstention; ties prefer the original weight, then lowest cutoff. Selected w=0.20, F=0.35; tuning yielded 8/8 positives and 5/5 abstentions. At w=.20, cutoffs .35 through .50 tied; .55 lost two positives and .60 lost three. The sample does not identify a uniquely optimal cutoff.

An initial exploratory run also included cutoff zero, which tied on tuning; it retrieved all ten exploratory positives but falsely matched a duck recipe to the bread recipe. We then required a nonzero fused cutoff and authored a new held-out query list before running it. The initial list is explicitly `EXPLORATORY`, never presented as pristine held-out evidence. Final parameters were frozen before final held-out embeddings/results, and were not changed after seeing its failures. The final held-out queries are still authored by the implementer after exploration, not an independent blind benchmark. The original 20-file evaluation below is historical regression evidence, not fresh held-out data.

| Split | Method | Positive top-3 hits | Correct no-match abstentions |
|---|---|---|---|
| tuning | keyword | 4/8 | 2/5 |
| tuning | semantic | 8/8 | 5/5 |
| tuning | hybrid | 8/8 | 5/5 |
| held_out | keyword | 9/10 | 1/5 |
| held_out | semantic | 10/10 | 4/5 |
| held_out | hybrid | 10/10 | 4/5 |
| exploratory | keyword | 5/10 | 1/5 |
| exploratory | semantic | 10/10 | 4/5 |
| exploratory | hybrid | 10/10 | 4/5 |

Hybrid ties semantic-only on this sample; fusion has no demonstrated advantage here. Final held-out false match: “insurance policy for an aircraft” returns car insurance (i.txt) and employee onboarding (f.txt). Exploratory false match: “recipe for roasting a duck” returns bread (h.txt). All positive final targets were retrieved, but these absent-topic false matches show that successful easy no-match queries do not establish reliable abstention. No topic-specific exceptions were added. Keyword misses the final paraphrase “where the bride and groom celebrate.”

## Final held-out query record

| Query | Target | Hybrid top three | Correct |
|---|---|---|---|
| coverage for damage to my vehicle | i.txt | i.txt, p.txt, c.txt | True |
| exercises for playing the piano | j.txt | j.txt, q.txt, h.txt | True |
| signup for beginner swimming instruction | k.txt | k.txt, f.txt | True |
| consular appointment renewal requirements | l.txt | l.txt, f.txt | True |
| notes on volcanic eruptions | m.txt | m.txt | True |
| how many boxes are in the warehouse | n.txt | n.txt | True |
| where the bride and groom celebrate | o.txt | o.txt | True |
| fiber connection repair report | p.txt | p.txt, c.txt | True |
| morning mindfulness routine | q.txt | q.txt | True |
| cleaning mineral deposits from a coffee boiler | r.txt | r.txt, m.txt, b.txt | True |
| wedding dress sewing pattern | none | none | True |
| telescope lens manufacturing specification | none | none | True |
| warehouse forklift operator license | none | none | True |
| insurance policy for an aircraft | none | i.txt, f.txt | False |
| dinosaur fossil excavation map | none | none | True |

## Phase A5 final scale follow-up

After the telemetry opt-out correction, the real 300-file scale test ran with OS-enforced external-network denial except loopback. Index: 30,818 harness ms (30,706 job ms), 300 searchable, zero failed/skipped; peak Python RSS 596.56 MiB excluding Ollama. Searches: 194/135/144/165/125 ms. Unchanged rescan: 596 ms, zero embedding calls. Change/add/delete: 656 ms, two calls. Cancel succeeded; resume reached 400 searchable in 2,768 ms. These are measured on this Mac and differ from earlier warm runs; no optimization or total-system RAM claim follows. Full composition/byte sizes and protocol are in VERIFY_LOCAL.md. Fusion/parameters and held-out results were not changed based on these follow-up searches.

## Current performance and desktop checks

Ranking only, 30 calls on this macOS 26.1 M1/8 GB machine, using repeated **real** passage vectors/text. This is a controlled ranking-cost test, not 300 independent source topics, inference throughput, or HTTP latency.

| Distinct files | Chunks | Median ranking ms | p95 ranking ms |
|---|---|---|---|
| 300 | 300 | 1.79 | 2.91 |
| 300 | 1200 | 7.63 | 9.56 |

Updated real 300-file workload (`backend/evaluation/scale.py`): 210 TXT, 45 MD, 15 text PDFs and 30 PNGs, using 15 variants of 20 base topics. Indexing took 35,563 ms. Five TestClient end-to-end searches took 218/152/182/219/174 ms, including real query embeddings, database access and ranking. The submarine no-match returned empty; the receipt/hotel/plants targets ranked first. The exact synthetic reference query returned its intended file first, with weaker neighboring results also present. This is not an independent 300-topic accuracy test or real HTTP network latency. Unchanged rescan: 694 ms and zero embedding calls. Change/add/delete rescan: 575 ms and two embedding calls. Cancel/resume reached 400 searchable files in 5,615 ms on resume. Source hashes were unchanged; Python peak RSS was 458.91 MiB, excluding Ollama. These timings are one warm run, not an optimization claim or performance guarantee.

Brute-force NumPy remains appropriate at this measured scale. Both matrix-vector cosine passes, tokenization, BM25, filtering, sorting and file grouping are included. Matrix construction is included; SQLite fetch and query embedding are excluded. Repeated content and warm caches limit generalization.

17 backend tests pass, preserving response field checks, caching, model failures and cancellation. New cases test best source chunk/page, explicit weak-match rejection, spaces/Unicode/literal shell punctuation, duplicate filenames, missing files, unsupported types, symlink escapes, unreadable and exclusively advisory-locked files, replaced roots, root switching/stale IDs, dispatch timeout, and picker failure followed by manual indexing. OS dispatch is mocked in unit tests; locks and permissions are real macOS checks.

`backend/evaluation/desktop_smoke.py` separately performed four real macOS dispatches (open/reveal for duplicate names in two subfolders with spaces/Unicode/punctuation). All succeeded; hashes stayed unchanged. Missing/unsupported/symlink/replaced-root actions were rejected, as were exclusive advisory locks and mode-000 unreadable files. Success proves OS dispatch, not that Finder selection or application contents were visually inspected in this run. Actual macOS applications may still show their own errors after asynchronous dispatch.

Open/reveal lock index root changes, then resolve the current ID, validate current root/containment/existence/type, open a read-only non-following handle, check regular-file identity, and dispatch. macOS uses argument arrays with shell=False; Windows uses os.startfile and native Shell PIDLs ([Microsoft API documentation](https://learn.microsoft.com/en-us/windows/win32/api/shlobj_core/nf-shlobj_core-shopenfolderandselectitems)). Windows code was reviewed but not executed, and no Windows tests are claimed. The external OS filename handoff still has a narrow race against another process replacing files/directories after validation; the index lock only serializes Sift root changes. Advisory-lock checking cannot detect applications that ignore advisory locks. macOS Finder's Locked attribute is not equivalent to an exclusive open lock; read-only documents remain eligible for opening.

Folder picker remains unavailable in this runtime; a 503 reports manual path entry as the fallback. Backend manual entry is tested after failure; frontend UI behavior is outside this backend change.

Tests/evaluations used `/private/tmp/sift-backend-venv` (same pinned requirements, Python 3.13.1) because the original Documents venv has cloud-offloaded files. One existing upstream TestClient/httpx deprecation warning remains. Source data and the user's running server were not changed.

---

# Historical evaluation (before Phase A4)

The following measurements and tables describe earlier code. They are retained for traceability and are not substituted for the current evaluation above.


Synthetic data only; not a real-world accuracy claim. Corpus generator and benchmark: `backend/evaluation/benchmark.py`. Generated data/results are ignored by Git.

## Protocol

20 documents with opaque filenames: 15 TXT, 2 MD, one text-layer PDF, and two Pillow-generated screenshots. Five positive and two no-match tuning queries; ten positive and two no-match held-out queries. Labels are predefined in the generator. Queries intentionally paraphrase content. This is a small hand-authored evaluation, not independent user validation.

Model: `nomic-embed-text:v1.5`, F16, 137M parameters, 768-dimensional vectors. Installed digest: `0a109f422b47e3a30ba2b10eca18548e944e8a23073ee3f3e947efcf3c45e59f`. Document/query prefixes: `search_document: ` and `search_query: `.

Sources: [Nomic model card](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5) specifies prefixes and extended 8,192-token capability; [Ollama model listing](https://ollama.com/library/nomic-embed-text) and the installed GGUF metadata list 2,048-token context. Installed parameters mention 8,192; this backend deliberately sets `num_ctx:2048`, with `truncate:false`, and uses bounded chunks. Do not confuse upstream extended capability with the tested runtime context.

Threshold candidates 0.35–0.75, selected using tuning positive hit rate plus no-match success, tie-breaking toward the lowest passing value. Frozen threshold: 0.53. Held-out results did not inform that selection. BM25-only baseline returns positive lexical-score results without semantic gating. Semantic uses cosine threshold; hybrid uses 0.8 × cosine + 0.2 × BM25/(BM25+2), with a semantic or lexical-coverage eligibility gate.

## Results

| Split | Method | Positive top-3 hits | Correct no-match abstentions |
|---|---|---|---|
| tuning | keyword | 5/5 | 2/2 |
| tuning | semantic | 4/5 | 2/2 |
| tuning | hybrid | 4/5 | 2/2 |
| held_out | keyword | 7/10 | 2/2 |
| held_out | semantic | 10/10 | 2/2 |
| held_out | hybrid | 10/10 | 2/2 |

Semantic retrieval improves the held-out paraphrase set from 7/10 to 10/10 relative to keyword-only. Hybrid ties semantic here, so it has no demonstrated advantage on this sample. Tuning keyword-only performs better than semantic/hybrid (5/5 versus 4/5).

**Failure:** “payment for keeping the lights on” should match IMG_004.png, but hybrid returned item_001.txt instead. Electricity bill OCR succeeded; the meaning/abstention gate failed to retrieve the target. The API integration tests screenshot extraction with a different explicit electricity-bill query; this does not repair or hide the failed paraphrase.

An initial baseline incorrectly used the hybrid lexical-coverage gate and scored 0/10. That was corrected to standard positive-score keyword ranking; the table above is the final comparison. No document-specific hardcoding was added.

## Measured timing on this Mac

- Deliberately unloaded model: cold embedding request 637 ms; Ollama-reported model load 617.7 ms.
- Final 20-file extraction/OCR/embedding benchmark: 2595 ms; zero extraction errors.
- Mean uncached query embedding time: 15.83 ms; this excludes ranking/HTTP work.
- First earlier full run took 29,789 ms; final repeated run used warmed OCR/runtime caches. This is not a claimed code optimization or a promise for new laptops.
- Separate real HTTP integration indexed all 20 supported documents plus one unsupported manifest in 2,372 ms. First paraphrased TXT API search took 25 ms; it returned the correct receipt first plus a weaker tuition-payment match.

## Reproduce

```bash
source .venv/bin/activate
PYTHONPATH=backend python backend/evaluation/benchmark.py
PYTHONPATH=backend python backend/evaluation/integration.py
```

The integration script binds port 8765 temporarily and terminates its server afterward. It opens/reveals a synthetic TXT file through the OS; run only when that desktop action is desired. Benchmark deliberately unloads only the selected embedding model to measure cold load.

## Query-level record

| Split | Query | Target | Hybrid top three | Correct |
|---|---|---|---|---|
| tuning | proof I paid to fix my notebook computer | item_001.txt | item_001.txt, item_014.txt | True |
| tuning | notes about how plants make food | item_002.md | item_002.md, item_007.txt, item_019.txt | True |
| tuning | where we are staying on our Cebu trip | item_003.pdf | item_003.pdf, item_011.txt | True |
| tuning | payment for keeping the lights on | IMG_004.png | item_001.txt | False |
| tuning | instructions for making spaghetti | item_007.txt | item_007.txt | True |
| tuning | galactic spaceship engine repair manual | none | none | True |
| tuning | archaeological excavation report of ancient pyramids | none | none | True |
| held_out | agreement for the place I live | item_005.txt | item_005.txt | True |
| held_out | pass to see bands perform live | IMG_006.png | IMG_006.png | True |
| held_out | how web addresses become numerical network locations | item_008.md | item_008.md | True |
| held_out | when I get my teeth checked | item_009.txt | item_009.txt, item_012.md, item_016.txt | True |
| held_out | coverage if my laundry appliance breaks | item_010.txt | item_010.txt, item_001.txt, item_015.txt | True |
| held_out | trip north by road to Baguio | item_011.txt | item_011.txt, item_003.pdf | True |
| held_out | money sent for school enrollment | item_014.txt | item_014.txt, item_019.txt, item_001.txt | True |
| held_out | record of my canine getting immunized | item_016.txt | item_016.txt, item_009.txt | True |
| held_out | my professional experience and programming skills | item_017.txt | item_017.txt, item_012.md | True |
| held_out | why reefs lose their color in warm seas | item_020.txt | item_020.txt, item_002.md | True |
| held_out | nuclear submarine reactor maintenance schematic | none | none | True |
| held_out | medieval sword metallurgy laboratory experiment | none | none | True |

Not yet measured: real personal-folder benefit, manual-search comparison, non-English/Taglish retrieval, Windows, and statistical generalization. The expanded synthetic scale test below is available.

## Expanded corpus and ranking reliability follow-up

300 synthetic files: 210 TXT, 45 MD, 15 text-layer PDFs, and 30 PNG screenshots. These are 15 variants of each of 20 base documents, not 300 independent documents. Generation/test code is `backend/evaluation/scale.py`; no personal source files were used. This test is not an independent accuracy benchmark.

The original fixed similarity threshold returned unrelated resume records for the submarine query when repeated synthetic metadata was added. An ambiguity gate now rejects weak semantic matches unless they separate from a different content cluster. This preserves closely related variants and continues to use 0.53 as the per-result threshold. Constants: high-score cutoff 0.60, separation 0.08, variant cosine cutoff 0.92. These are engineering heuristics derived from observed failures; additional unseen-corpus validation is needed.

The scale follow-up returns an empty result for that submarine query, while paraphrased receipt, plant-notes, and hotel queries still return the appropriate document families. Reference ZX1400 returns its exact matching record first but also weaker extra matches; the UI must show evidence, not claim all results are certainly relevant.

| Operation | Latest measured result |
|---|---|
| Initial 300-file index | 48.50 seconds; 300 searchable; zero file failures |
| Unchanged rescan | 0.707 seconds; zero new embedding calls |
| Add one / change one / remove one | 0.967 seconds; exactly two new embedding calls; 300 searchable |
| Cancel and resume after adding 100 new TXT files | cancelled successfully; resumed to 400 searchable in 3.309 seconds |
| Python-process peak memory | 434.25 MiB, including OCR/TestClient; excludes Ollama |
| Source files | SHA-256 hashes unchanged by indexing/search/rescans |

Latest end-to-end TestClient search times: 276 ms, 127 ms, 142 ms, 128 ms, 178 ms. Earlier run: 334 ms, 172 ms, 173 ms, 228 ms, 279 ms. Database lookups per chunk were removed, but these observations are not a controlled speed benchmark; filesystem/model warm-up and load vary. Earlier initial indexing took 76.43 seconds; do not attribute that entire difference to the code changes.

Cancellation of a long file was separately reproduced and fixed: old code kept running all nine embedding calls; new code checks cancellation between batches without committing incomplete file vectors. All 14 backend tests pass.

The original “held-out” set has now been inspected during follow-up work and is a regression set, not fresh independent validation. Reproduce its regression with `backend/evaluation/benchmark.py --threshold 0.53`. Running the script without a fixed threshold selects a tuning optimum for that algorithm and does not automatically change backend configuration. No model was changed.

Fixed-threshold regression after the ambiguity fix: semantic/hybrid 10/10 original test-set top-three hits and 2/2 no-match abstentions; tuning 4/5 hits and 2/2 abstentions. The lights-on query now returns no matches rather than the incorrect receipt. Cold request 1,843 ms, reported model load 1,778.11 ms, 20-file index 5,401 ms, mean query embedding 47.94 ms in that later run; timings vary with system load.
