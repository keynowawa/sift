# Sift backend — Phase A5 handoff

## Status

Implemented locally on `backend-search`. All v1 endpoints retain the supplied field names and shapes. A real HTTP integration run indexed TXT/MD, a text-layer PDF, and PNG screenshots, queried the real Ollama embedding model, previewed a matching TXT, dispatched macOS open/reveal, and verified unchanged source hashes. TextEdit's actual receipt window was inspected successfully.

Tested environment: macOS 26.1 / Apple M1 CPU (8 cores), Apple M1 GPU (8 cores, Metal), 8 GB RAM. Project `.venv` uses Python 3.13.1. Homebrew's default Python changed to 3.14.8 during the user's installation; use the tested venv rather than recreating it with an unverified interpreter. Windows has not been run or verified.

## Run from repository root

```bash
source .venv/bin/activate
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8765
```

Fresh environment: create a Python 3.13 venv, activate it, then `python -m pip install -r backend/requirements.txt`. Python 3.11+ is the project goal; only 3.13.1 has been tested with these pins. Model/runtime prerequisites: Ollama running on loopback and `ollama pull nomic-embed-text:v1.5` completed. Do not download dependencies/models during normal app runtime.

Keep the agreed launch command unchanged. For a non-default port, set `SIFT_PORT` and also pass the same value to uvicorn's `--port`; validation uses that configured port. Uvicorn reports address-in-use on conflicts and must not kill unrelated processes. Do not run multiple backend workers: one process owns the indexing thread and database operations.

Data lives in `~/Library/Application Support/Sift` on macOS and `%LOCALAPPDATA%/Sift` on Windows. `SIFT_DATA_DIR` overrides it for isolated tests. This local store is unencrypted. Reset deletes index rows and vacuums its SQLite database; source files are untouched. It is not forensic secure erasure. No WAL mode is used. Activity counters are process-session counters, reset on process restart or explicit index reset.

## Frontend integration

1. Proxy `/api` from Vite port 5173 to loopback port 8765; use relative URLs in release.
2. Read health, then `/api/index`. Read `active_job_id` to reconnect to indexing after browser reload.
3. Native folder dialog is honestly unavailable on the tested Python: importing Tk fails because `_tkinter` is not installed. `folder_picker:false`; the pick endpoint returns a standard 503 error. Use the manual absolute-path field. No extra GUI dependency was installed and no dialog was fabricated.
4. POST start with `root` and `replace_index`; poll status. Search can run over committed files during indexing.
5. POST search; show returned snippets as escaped source text. Preview/open/reveal use opaque file IDs, never arbitrary browser-supplied paths.
6. See API_EXAMPLES.md for actual successful requests/responses. No contract fields were added, renamed, or changed.

Missing OCR permits TXT/MD/PDF indexing and reports screenshot skips. Missing embeddings blocks starting the job and makes search return MODEL_UNAVAILABLE. Installed models are never auto-pulled. Standard errors cover invalid input, unknown IDs, root confirmation conflicts, job conflicts, missing models, unsupported picker, stale previews, and desktop failures. Unknown API paths stay JSON even with the frontend built. Built `frontend/dist` is served if it exists; Builder B owns that build.

## Implementation notes

- SQLite persists files, chunk vectors, content hashes, extraction/model signature, jobs, and full job errors. Startup marks queued/running jobs interrupted; it does not auto-resume unknown work. Rescan reuses committed records.
- File hash plus extraction/chunk/model signature controls cache reuse. Successful unchanged rescans do not re-embed. Modified/deleted source files are excluded from query output; rescan refreshes/removes records. Failed/skipped files are retried on rescans.
- UTF-8/UTF-8 BOM and UTF-16 BOM TXT/MD; text-layer PDF with 1-based pages; bundled local RapidOCR on PNG/JPG. Encrypted/scanned PDFs, textless images, unsupported extensions, and files above 25 MB are reported. Extracted text capped at 200,000 characters; previews report truncation.
- Chunks are 1,000 characters with 150-character overlap, split within PDF pages; at most eight chunks per embedding call. Model context explicitly 2,048 tokens and truncation false. This conservative character bound suits WordPiece tokens; arbitrary tokenizer/model substitution is not supported.
- Query prefix `search_query: `; document prefix `search_document: `. Every search makes a genuine uncached query embedding call, even for empty indexes. Float32 normalized vectors, cosine similarity, BM25 keyword scores, and hybrid fusion. Group results by file. Threshold 0.53 selected only on the synthetic tuning set.
- Root scoping, symlink rejection, hidden/system-folder skips, JSON mutation checks, Host/Origin checks, no wildcard CORS, no proxy-environment use for Ollama, safe OS subprocess argument arrays, and executable/unknown-type refusal. CLI requests without Origin are supported; browser cross-site requests are rejected. This is not a hardened multi-user service; keep it bound to loopback.
- API error lists cap at 100 records. The `job_errors` table holds complete errors locally, queryable by `job_id`; files also store individual error messages. No private extraction text is written to job error messages intentionally.

## Checks and limits

17 backend tests passed, including lifecycle/caching, query calls/no-match, model failure, per-file failure, symlink/root checks, origin/host checks, cancellation/reset conflicts, restart interruption, safe desktop arguments, API-vs-HTML routing, duplicate filenames, read-only hashes, and configuration invalidation. Test inference is injected only inside tests, never selected by runtime environment/configuration. TestClient currently emits one upstream deprecation warning about httpx; tests still pass.

Real integration: 20 searchable files + one unsupported synthetic JSON manifest; all 21 discovered records processed, zero failed files. An unchanged rescan reused embeddings. macOS open visibly verified; reveal successfully dispatched to Finder, but Finder selection was not visually inspected. No Windows OS action is claimed tested.

Still incomplete: native folder picker; Windows runtime testing; browser integration and OS traffic observation during physical offline operation; scanned-PDF OCR/DOCX; broad real-world retrieval validation; clean-machine setup and frontend integration. No summaries, chat, date interpretation, cleanup, moves, undo, or generative model are implemented.

## Reliability follow-up (October 10)

Cancellation now stops between embedding batches. A partial current file is not committed; previously committed files remain available and an incremental rescan retries the interrupted file. A regression test reproduced nine continued calls in the old implementation and verifies at most the in-flight batch can finish after cancellation.

Search now rejects weak semantic matches that are ambiguous across different content clusters: highest similarity must be at least 0.60, or separated by at least 0.08 from the best different cluster. Candidate vectors with cosine similarity at least 0.92 to the best candidate are treated as near-identical variants for this check. The existing 0.53 per-result threshold remains unchanged. This is a heuristic, not calibrated confidence or a guarantee of empty results for all unrelated queries. The gate may reduce recall.

Search validation uses modification metadata returned in the internal database query, avoiding one SQLite lookup per chunk. API fields remain identical; the internal mtime is not returned to frontend clients. See SEARCH_EVALUATION.md for the expanded-corpus measurements.

### Local environment issue

During the follow-up, macOS marked a required pydantic source file under the Documents `.venv` as `dataless`; process sampling showed imports blocked on a file read. The existing user-started server also timed out on `/api/index`. Its process was not stopped or changed. Relocating bytecode caches alone did not resolve dependency-source hydration.

A separate Python 3.13.1 environment was installed successfully from the same pinned requirements at `/private/tmp/sift-backend-venv`, outside Documents. All backend tests and real scale checks ran there. It is a temporary environment and may be removed after a reboot/cleanup; do not make it the distributed setup default. Builder B should keep installed dependencies outside cloud-offloaded folders when this issue occurs.

To use the tested local environment now, stop the old server with Ctrl+C in its own Terminal, then from repo root:

```bash
source /private/tmp/sift-backend-venv/bin/activate
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8765
```

This retains the agreed launch command and default application-data index. A permanent non-cloud venv plus the pinned requirements is preferable for distribution.

## Phase A4 retrieval and desktop hardening

Fusion is 0.8*cosine + 0.2*BM25/(BM25+2), with file-based IDF, a tuning-selected fused cutoff 0.35 and retained semantic cutoff/ambiguity checks. Unique-token lexical coverage must reach .5 for the keyword acceptance route. Group accepted chunks by file and expose the best source chunk/page, never scores or confidence percentages. Acceptance precedes top-k. See SEARCH_EVALUATION.md for separate tuning/held-out results, false matches and ranking measurements. NumPy brute-force remains in place.

Open/reveal serialize active-root changes, revalidate the current ID/root/path/type/existence, reject symlinks/junctions and nonregular or unreadable files, compare file identity, and dispatch through macOS argument arrays or Windows native APIs. macOS exclusive advisory locks yield a retryable desktop error. A narrow external filesystem race remains at the OS path handoff; this is not an atomic capability-based launch. Windows remains untested. Folder-picker failure still permits manual absolute-path indexing; picker capability remains false.

Optional real macOS synthetic-document action test: `PYTHONPATH=backend python backend/evaluation/desktop_smoke.py`. It launches the default text application and Finder; temporary documents are removed afterward. New split evaluation: `PYTHONPATH=backend python backend/evaluation/phase_a4.py`; no cold model unload. Generated result JSON is ignored.

## Phase A5 verified handoff (October 10, 2026)

The final 17-test suite covers every Phase A5 category; see VERIFY_LOCAL.md for the test-to-requirement map. Genuine HTTP integration runs in a separate real Uvicorn process with real Ollama and fresh nonce-bearing sources, independently of stub-based tests. Latest 300-file scale measurements include counts, byte sizes, generation, failure counts, caching and cancel/resume. Search evaluation retains the known false matches; no new features were added.

All 40 requirements are exactly pinned in `backend/requirements.txt`. Installed versions matched all pins and `pip check` reported no broken requirements. Key runtime pins: FastAPI 0.143.0, uvicorn 0.54.0, numpy 2.5.3, pypdf 6.20.0, RapidOCR 3.10.0, ONNX Runtime 1.31.0, Pillow 12.3.0. Ollama 0.40.2 is a separately installed native prerequisite, not a pip requirement. Selected model remains `nomic-embed-text:v1.5`, F16, digest `0a109f422b47e3a30ba2b10eca18548e944e8a23073ee3f3e947efcf3c45e59f`; query/document prefixes remain `search_query: ` and `search_document: `. No dependency/model download occurred in the verification runs.

**Network finding and correction:** OS nettop attributed an external HTTPS connection to the original OCR backend process. This is consistent with [ONNX Runtime's documented default telemetry](https://github.com/microsoft/onnxruntime/blob/main/docs/Privacy.md); the encrypted payload was not inspected, so do not assert what it contained. The extractor now forces `ORT_DISABLE_TELEMETRY=1` before native initialization and calls `disable_telemetry_events()` before OCR sessions. This is a local-only behavior correction, not an API or feature change. Fresh inference/index/query tests pass with OS-enforced outbound denial except loopback. This does not establish unrestricted post-fix zero egress. A later user-run local-copy test passed with Wi-Fi/Ethernet/VPN disconnected according to the user; its real saved index/query responses were inspected. No OS observer or browser UI ran during that physical offline retry; see VERIFY_LOCAL.md. Existing running servers must be restarted to load this correction.

Builder B: use the manual folder field while `folder_picker:false`; treat completed jobs with nonzero failed/skipped counts as partial success; preserve empty results and retryable errors; display source excerpts rather than numeric confidence. Current backend checkout has no frontend build, so frontend end-to-end and browser traffic proof are pending. Exact launch command remains the default 8765 command above; evaluation defaults to isolated 8766 with matching `SIFT_PORT`. Do not point the frontend at a deleted temporary test index or reuse example IDs.

Disclosures author: actual local embedding and bundled OCR were measured on this Mac; synthetic corpora, dependencies, models and AI assistance must be disclosed. Do not claim Windows testing, independent retrieval validation, independently observed physical offline/browser behavior, or verified zero external requests. The discovered pre-fix external HTTPS connection and corrective telemetry configuration belong in the honest development/verification history.

### Physical offline retry handoff

The user-confirmed disconnected run passed from `/private/tmp/sift-offline-check`, with the existing preinstalled venv and models: six supported files searchable, all 25 HTTP/assertion checks passed, initial indexing 2,874 ms, unchanged rescan 15 ms with zero new embeddings. The deliberately malformed TXT and unsupported JSON remain expected error/skip fixtures. Cloud-offloaded source files in Documents caused the first attempt to fail during import; all application source as well as dependencies must be locally materialized. No product code changed for that setup repair. Full browser/OS traffic proof and actual Windows testing remain pending.
