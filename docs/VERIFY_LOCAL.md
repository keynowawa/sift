# Local inference verification — current evidence and remaining checks

## Verified on macOS 26.1 / M1 / 8 GB / Python 3.13.1

- Installed Ollama tag `nomic-embed-text:v1.5`, digest recorded in SEARCH_EVALUATION.md; only this embedding model observed resident during the benchmark. No generative LLM added.
- Genuine extraction/OCR and document/query embeddings on a newly generated, clearly synthetic 20-file corpus. Actual HTTP integration run with a new temporary SQLite data directory, uncached query embedding, real source snippets, open/reveal requests, and unchanged source SHA-256 hashes.
- Real call instrumentation and Ollama resident process observed during inference. API counters change on genuine calls; they do not report network status. Query search does not use a fixture fallback.
- RapidOCR 3.10.0 and onnxruntime 1.31.0 installed and executed on this Mac. Bundled models: PP-OCRv6_det_small.onnx, ch_ppocr_mobile_v2.0_cls_mobile.onnx, PP-OCRv6_rec_small.onnx. Explicit local model paths bypass the package's automatic-download branch. Package/model files are installed during setup, not runtime.
- Official PyPI metadata advertises universal RapidOCR wheels, and Windows/macOS wheels for onnxruntime, OpenCV-headless, numpy, and Pillow at the pinned versions. That is packaging evidence only; actual Windows installation and OCR behavior are unverified.

## Additional Python-process socket test

With Python socket connections restricted to loopback for a standalone test process, bundled screenshot OCR returned `Payment successful / Electricity utility bill / Amount PHP 1800 / Account 440012`. A new synthetic violin-service sentence and a paraphrased query each produced a real `(1, 768)` embedding. No non-loopback connection attempts were recorded. This verifies that particular Python-process path; it does not cover native-library traffic, the separate Ollama process, or physical network disconnection. No guard or zero-traffic counter was added to the API.

## Not established by this evidence

An activity counter, a source-code inspection, or a loopback API URL does not prove every process is offline. The computer's Wi-Fi was not disabled by this work. No full browser/OS packet capture was performed. Native libraries and Ollama are separate from Python-only socket tests. Do not claim “verified zero external requests” or verified Windows compatibility yet.

## Required full offline test before submission

1. Install dependencies and selected model while online. Start the app with an isolated `SIFT_DATA_DIR` and real model. Use only synthetic files for a public demo.
2. Disable Wi-Fi and other network interfaces manually. Keep loopback available.
3. Generate new files the index has never seen; do not reuse cached embeddings. Start indexing and confirm real source snippets, OCR text, and changed call/chunk counters.
4. Search with a paraphrase; show the target in results and its source excerpt. Confirm preview/open/reveal work.
5. Observe Ollama process activity and inspect browser Network plus OS connections/firewall capture. Browser should call only same-origin/local API; inspect Ollama separately. This covers the tested operation, not unrelated OS software.
6. Repeat on an actual Windows machine. Record exact versions, corpus, commands, outcomes, elapsed time, and failures separately.
7. Re-enable networking after testing when appropriate.

## Current reproducible integration checks

From repo root with the project venv activated:

```bash
python -m pytest -q backend/tests
PYTHONPATH=backend python backend/evaluation/benchmark.py
PYTHONPATH=backend python backend/evaluation/integration.py
```

The integration test uses a fresh temporary database and real loopback HTTP service, tests read-only source hashes and unchanged rescan caching, and deliberately opens/reveals a synthetic receipt. Generated corpora and raw results are ignored by Git; request/response records are in API_EXAMPLES.md. No personal files are required.

Index reset removes Sift index/cache rows only; no secure-erasure guarantee. Native folder picking is unavailable on the tested interpreter; manual paths remain usable. A 300-file synthetic scale test and cancellation/resume to 400 files passed; independent user testing remains pending. The corpus repeats 20 base topics and does not establish real-world scale accuracy.

Follow-up checks ran in `/private/tmp/sift-backend-venv` because the Documents environment contained offloaded dependency files. Physical offline and actual Windows verification are still pending. Retrieval abstention was corrected after an expanded-corpus false positive; see SEARCH_EVALUATION.md.
