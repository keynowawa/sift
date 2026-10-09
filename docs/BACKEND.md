# Sift backend — Checkpoint B handoff

## Status

Implemented locally on `backend-search`. Nothing pushed externally. All v1 endpoints retain the supplied field names and shapes. A real HTTP integration run indexed TXT/MD, a text-layer PDF, and PNG screenshots, queried the real Ollama embedding model, previewed a matching TXT, dispatched macOS open/reveal, and verified unchanged source hashes. TextEdit's actual receipt window was inspected successfully.

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

14 backend tests passed, including lifecycle/caching, query calls/no-match, model failure, per-file failure, symlink/root checks, origin/host checks, cancellation/reset conflicts, restart interruption, safe desktop arguments, API-vs-HTML routing, duplicate filenames, read-only hashes, and configuration invalidation. Test inference is injected only inside tests, never selected by runtime environment/configuration. TestClient currently emits one upstream deprecation warning about httpx; tests still pass.

Real integration: 20 searchable files + one unsupported synthetic JSON manifest; all 21 discovered records processed, zero failed files. An unchanged rescan reused embeddings. macOS open visibly verified; reveal successfully dispatched to Finder, but Finder selection was not visually inspected. No Windows OS action is claimed tested.

Still incomplete: native folder picker; Windows runtime testing; physical Wi-Fi-off test with browser and OS traffic inspection; scanned-PDF OCR/DOCX; broad real-world retrieval validation; clean-machine setup and frontend integration. No summaries, chat, date interpretation, cleanup, moves, undo, or generative model are implemented.

## Reliability follow-up (October 10)

Cancellation now stops between embedding batches. A partial current file is not committed; previously committed files remain available and an incremental rescan retries the interrupted file. A regression test reproduced nine continued calls in the old implementation and verifies at most the in-flight batch can finish after cancellation.

Search now rejects weak semantic matches that are ambiguous across different content clusters: highest similarity must be at least 0.60, or separated by at least 0.08 from the best different cluster. Candidate vectors with cosine similarity at least 0.92 to the best candidate are treated as near-identical variants for this check. The existing 0.53 per-result threshold remains unchanged. This is a heuristic, not calibrated confidence or a guarantee of empty results for all unrelated queries. The gate may reduce recall.

Search validation uses modification metadata returned in the internal database query, avoiding one SQLite lookup per chunk. API fields remain identical; the internal mtime is not returned to frontend clients. See SEARCH_EVALUATION.md for the expanded-corpus measurements.

### Local environment issue

During the follow-up, macOS marked a required pydantic source file under the Documents `.venv` as `dataless`; process sampling showed imports blocked on a file read. The existing user-started server also timed out on `/api/index`. Its process was not stopped or changed. Relocating bytecode caches alone did not resolve dependency-source hydration.

A separate Python 3.13.1 environment was installed successfully from the same pinned requirements at `/private/tmp/sift-backend-venv`, outside Documents. All 14 tests and real scale checks ran there. It is a temporary environment and may be removed after a reboot/cleanup; do not make it the distributed setup default. Builder B should keep installed dependencies outside cloud-offloaded folders when this issue occurs.

To use the tested local environment now, stop the old server with Ctrl+C in its own Terminal, then from repo root:

```bash
source /private/tmp/sift-backend-venv/bin/activate
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8765
```

This retains the agreed launch command and default application-data index. A permanent non-cloud venv plus the pinned requirements is preferable for distribution.
