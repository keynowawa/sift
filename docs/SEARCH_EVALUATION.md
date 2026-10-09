# Local retrieval evaluation

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

Not yet measured: real personal-folder benefit, manual-search comparison, non-English/Taglish retrieval, hundreds-file memory/time, Windows, and statistical generalization.
