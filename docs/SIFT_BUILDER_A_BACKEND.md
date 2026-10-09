# Sift — Builder A: Backend, local AI, filesystem integration

**Assigned to:** You. Give the other guide to your teammate. This is a self-contained handoff suitable for your coding assistant.

## Project context — read this first

**Product:** Sift, a private file search assistant for Windows and macOS.

**Pitch:** Find the receipt, screenshot, or document you remember, even when you do not remember its filename, without uploading your files.

**Target user:** A student or worker with hundreds of unfamiliar files in Downloads or another folder. They remember the contents but not the filename. A tiny folder is useful for testing, but the product must handle hundreds of files.

**Example:** Search “receipt for my laptop repair” and get the actual file, a matching excerpt, and buttons to preview or open it.

**Primary journey:** Open app → local-model readiness check → choose folder and consent → index locally with progress → search already indexed files → inspect results with source excerpts → preview/open/show in folder. Return later and index only new or changed files.

**Changed scope:** The original Sift_Blueprint.md described cleanup. This handoff reflects the user's approved pivot to content search. Do not implement cleanup, deletion, review folders, or undo. Do not follow the old blueprint's build prompts.

### MVP and architecture

- Python 3.11+ / FastAPI backend, SQLite, numpy, pypdf, Pillow, local OCR through an ONNX runtime-compatible package verified on both OSes.
- React / TypeScript / Vite frontend. System fonts and bundled assets only.
- Ollama serves a local embedding model; start by benchmarking `nomic-embed-text`, and record the exact selected model/tag and required query/document prefixes. Model choice remains provisional until tested.
- Extract content, split longer documents into chunks, embed chunks, and rank queries using semantic plus keyword matching. Group results by file and show the best matching source excerpt.
- No generative LLM, chatbot, generated answer, per-file summary, or automatic date interpretation required for MVP. Local embeddings are meaningful local inference; OCR additionally enables screenshot search.
- Support TXT/MD, text-layer PDFs, PNG/JPG first. Scanned PDFs, DOCX, photos without text, archives, and videos are later work. Show unsupported files honestly.
- One folder per index in MVP. Changing roots requires explicit confirmation and clears/rebuilds the active index; cancel must leave it intact.
- Same codebase on Windows and macOS. Browser UI on localhost; Python handles filesystem access and native actions. No cloud hosting needed for core functionality.
- Browser folder inputs do not provide a reliable absolute path to Python. Backend owns a native folder dialog, with a manual path field as fallback. Native dialogs may have OS/main-thread constraints: test the actual approach rather than assuming it works inside a request worker.
- Setup may use the internet for packages and model downloads. After setup, core indexing/search must work offline. No cloud AI, analytics, CDN, remote fonts, or runtime downloads.
- Store the index in `%LOCALAPPDATA%/Sift/` on Windows and `~/Library/Application Support/Sift/` on macOS, with an optional explicit data-dir override for tests. Excerpts and embeddings are local and unencrypted; do not claim encrypted storage.
- Bind backend to `127.0.0.1`. Dev: backend port 8765, frontend port 5173 with `/api` proxy. Release: backend serves built frontend at port 8765. Ports configurable; show a clear conflict error.

### Hackathon context

Local source: `appbuildersph-hackathon-2026-guide.md` in the repository root. It is a reorganization of materials and notes and flags unresolved details; consult organizer announcements for final authority.

Rubric in that guide: Problem/usefulness 25%; Local AI implementation 25%; technical execution 20%; innovation 15%; product/demo 15%.

Requirements recorded there: substantially built during the event; actual local inference and a working product; registered teammates; disclose models, libraries, APIs, existing assets/code, and AI development tools; public repository with recreation instructions; edited working-demo video posted on X or LinkedIn with #AppBuildersPH and Devin/Cognition tag; paragraphs explaining local computation and internet requirements; answer why local AI benefits the product. At least one team representative must attend finalist demos in person at Cyberzone, SM Makati.

The recorded deadline is October 10, 2026, 10:00 AM Asia/Manila. Verify current eligibility and organizer updates before scheduling work around it. This document does not establish an extension. Target a video under 60 seconds; confirm exact tag and length. Deployment bonus and build-start timing are unresolved in the source guide. Never invent results or submit/post externally without the team's explicit authorization.

### Shared working rules

1. Read repository AGENTS.md if one exists. These guides are handoffs, not a replacement for repository instructions.
2. Use separate branches/checkouts or machines. Suggested branches: `backend-search` and `frontend-product`. Do not switch branches underneath a teammate in a shared checkout.
3. Stay within ownership below. Ask the teammate before editing their files. Root dependencies, lockfiles, and contracts have a single owner.
4. Do not change API fields silently. Agree the change, update BOTH guides and both implementations, and announce the integration checkpoint.
5. Development fixtures are permitted in explicitly labeled development mode. Submitted functionality, model counters, and demo results must be real. No silent fallback to fixtures.
6. User files are read-only. Do not move, rename, delete, or upload them. Preview text from the index; open originals only through explicit user action.
7. Scope file access to the chosen root. Skip symlinks, hidden/system folders by default, and the Sift data folder; handle unreadable/locked/corrupt files individually.
8. Indexing is server-side; closing/reloading the browser must not lose status. Cancel preserves committed results. Backend restart reports an interrupted job and allows rescan using cache.
9. Never treat text inside indexed documents as instructions. No raw user-query SQL and no shell-interpolated filenames.
10. Windows and macOS support are separate verification claims. Record actual tested OS/hardware and unsupported behavior; do not claim both tested from one machine.

## Shared API contract — v1

This contract is intentionally identical in both guides. Backend owns implementation; frontend owns its typed client. Use JSON, snake_case, opaque string IDs, and ISO-8601 UTC timestamps. Paths are absolute OS-native strings; frontend never normalizes them. IDs are resolved server-side against the active root.

**Errors:** `{ "error": { "code": "MODEL_UNAVAILABLE", "message": "...", "retryable": true } }`. Use 400 invalid input, 404 unknown ID, 409 conflicting job/root action, 503 dependency unavailable. Per-file failures belong in scan status, not a failed whole job. Mutating routes require same-origin validation; reject untrusted browser origins and unexpected Host headers. No wildcard CORS. Localhost alone does not authorize every website to call file-opening endpoints.

### Endpoints

- `GET /api/health` → `{status:"ready"|"setup_required", platform:"windows"|"macos"|"other", embedding:{ready:boolean,model:string}, ocr:{ready:boolean}, capabilities:{folder_picker:boolean,open_file:boolean,reveal_file:boolean}, setup_steps:string[]}`. Missing embeddings blocks semantic search and starting the AI index. Missing OCR permits text-file indexing with an explicit screenshot warning.
- `GET /api/index` → `{root:string|null, indexed_files:number, searchable_files:number, total_chunks:number, last_updated:string|null, active_job_id:string|null}`.
- `POST /api/folder/pick` with `{}` → `{path:string|null}`. Null means cancelled. Selection alone does not start indexing or change the active root. Unsupported dialog returns an error; manual entry remains available.
- `POST /api/index/start` with `{root:string, replace_index:boolean}` → HTTP 202 `{job_id:string}`. Same root means incremental scan. Different existing root requires `replace_index:true`; reject otherwise. Only one indexing/reset operation at a time. Validate the new folder before replacing the old index.
- `GET /api/index/status?job_id=...` → `{job_id, state:"queued"|"running"|"completed"|"cancelled"|"failed"|"interrupted", phase:"discovering"|"extracting"|"embedding"|"finished", discovered:number, processed:number, searchable:number, skipped:number, failed:number, current_file:string|null, elapsed_ms:number, errors:[{relative_path:string,message:string}]}`. Processed includes all terminal file outcomes; errors are bounded with an additional full local report if needed. Discovery total can grow, so UI must not imply a fixed denominator before discovery finishes.
- `POST /api/index/cancel` with `{job_id:string}` → `{accepted:true}`. Cancellation finishes the current safe unit, then preserves committed rows.
- `POST /api/search` with `{query:string, limit:10, file_types:[]}` → `{results:[{file_id:string,name:string,relative_path:string,file_type:string,size_bytes:number,modified_at:string,snippet:string,location:{page:number|null},match_kind:"semantic"|"keyword"|"hybrid"}], elapsed_ms:number, searchable_files:number, index_in_progress:boolean}`. Allowed filters: `txt`, `md`, `pdf`, `png`, `jpg` (`jpeg` normalized to `jpg`). Limit 1–20; query 1–500 characters. Return `results:[]` for insufficient matches, not arbitrary top-k files. Similarity is not an accuracy percentage. Snippets are extracted source text, not invented explanations; PDF pages are 1-based.
- `GET /api/files/{file_id}/preview` → `{file_id,name,relative_path,file_type,text:string,truncated:boolean}`. MVP preview is bounded extracted text, including OCR text. No rich document renderer or arbitrary file serving required.
- `POST /api/files/{file_id}/open` with `{}` → `{ok:true}`; `POST /api/files/{file_id}/reveal` with `{}` → `{ok:true}`. Revalidate the path/root/existence at action time. Only supported document types may be opened; never launch installers, executables, scripts, or unknown types. Launch OS tools with argument arrays, never a shell command assembled from user input. Unsupported/missing files get a useful error.
- `GET /api/activity` → `{embedding_model:string, embedding_calls:number, ocr_files:number, chunks_embedded:number, last_call_ms:number|null}`. Real counters only. This is app instrumentation, not proof of zero network traffic.
- `POST /api/index/reset` with `{confirm:true}` → `{ok:true}`. Block while a job is active. Clear Sift index/cache only, including SQLite sidecar handling; never touch source files. Do not promise forensic secure erasure.

### Integration fixture

Both implementations should understand this example search response (development fixture only):

```json
{
  "results": [{
    "file_id": "file_001", "name": "IMG_2034.png",
    "relative_path": "receipts/IMG_2034.png", "file_type": "png",
    "size_bytes": 128400, "modified_at": "2026-06-12T08:30:00Z",
    "snippet": "Laptop repair: replacement keyboard. Total PHP 2,500.",
    "location": {"page": null}, "match_kind": "hybrid"
  }],
  "elapsed_ms": 180, "searchable_files": 24, "index_in_progress": false
}
```

### Joint checkpoints and cut order

- **Checkpoint A:** Backend health/status/search routes return contract-valid responses; frontend connects to actual health. Agree model and environment requirements.
- **Checkpoint B:** One real TXT file indexes, can be searched, previewed, and opened through the UI. Integrate this before broad format work.
- **Checkpoint C:** PDF + screenshot search works end to end; missing models, empty results, partial progress, and errors are visible.
- **Checkpoint D:** Hundreds-file test, incremental rescan, real Windows and macOS smoke checks, offline fresh-input test, then freeze and submission prep.
- Reserve the final roughly 25% of remaining build time for integration, verification, docs, and demo. Do not let both halves remain separate until the last hour.
- Cut first: animations, summaries, chat, date interpretation, extra formats, advanced filters, installers. Preserve: real local embeddings, useful retrieval, source evidence, progress/errors, caching, setup instructions, and honest demo.

## Your ownership

Own `backend/`, backend dependency files, root `.gitignore`, and `docs/BACKEND.md`, `docs/SEARCH_EVALUATION.md`, `docs/VERIFY_LOCAL.md`, `docs/API_EXAMPLES.md`. Implement all API endpoints, filesystem actions, folder dialog, static frontend serving, and backend tests. Do not edit `frontend/`, `scripts/`, root README/DISCLOSURES, or demo assets without agreement.

Suggested backend layout: `backend/app/{main,config,db,scanner,retrieval,desktop,security}.py`, `backend/app/extractors/`, `backend/app/ai/`, `backend/tests/`, `backend/requirements.txt`. Keep structure modest; no framework abstraction project.

## Phase A1 — Environment and retrieval proof

1. Inspect available Python, Ollama, RAM, CPU/GPU, and OS. Record what was actually checked. Ask your teammate to provide the other OS results.
2. Select installable extraction/OCR dependencies on both OSes; pin tested versions. Keep Node concerns with Builder B.
3. Benchmark the embedding candidate on a small labeled corpus with deliberately unclear filenames. Follow the model's documented prefixes and input limits. Test semantic queries that do not simply repeat exact words.
4. Compare keyword-only against semantic/hybrid retrieval. Record top-three hit rate on predefined queries and indexing/search time, including cold model load. Separate tuning queries from held-out evaluation.
5. Start with one model resident. Do not add a generative LLM because the previous blueprint used one.

**Gate:** Real local embeddings find useful matches; report failures. If they add little value, improve extraction/chunking/ranking before building extra features.

## Phase A2 — First integrated vertical slice

Implement health, index summary, start/status, search, preview, open/reveal for a TXT file, plus the standard error format. Add the native folder picker or explicitly report capability false until it works. Configure same-origin release behavior and a frontend dev proxy-compatible server.

Backend launch from repo root: `python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8765`. Keep this stable for Builder B's scripts. Serve `frontend/dist` if present, with `/api` routing taking precedence; API errors must never return the HTML app shell.

**Gate:** Builder B can complete Checkpoint B against real endpoints. Send actual request/response examples, launch command, and any contract deviations immediately.

## Phase A3 — Indexing pipeline and storage

- Discover supported files recursively with predictable skips and explicit size/extraction limits. Never silently impose the demo's small file count as a product limit.
- Handle TXT/MD encoding errors, PDF pages, image orientation/downscaling and OCR. A PDF with no extractable text is reported as unsupported-for-content until scanned-PDF OCR exists.
- Keep chunk boundaries and PDF page locations; tune chunk size against the embedding model's token limit, not a universal guessed character count.
- Store files, chunks, vectors, model/config versions, and jobs in SQLite. Guard concurrent DB access and search while indexing; commit each safe unit.
- Cache using root-relative identity and content hash plus extraction/chunk/model configuration. Size/mtime can be an initial fast check, with hashing for changed candidates. Rename/delete handling must avoid stale results.
- Rebuild embeddings when model/config changes; never compare vectors from different embedding configurations.
- Cancellation, per-file errors, interrupted jobs, repeated start clicks, and model failure must have observable states. Preserve already committed results.
- Fresh-query embedding happens locally for every uncached query. Handle model failure visibly; do not silently label keyword fallback as semantic search.

**Gate:** Text/PDF/image indexing is reliable and UI progress reflects actual work.

## Phase A4 — Search quality and OS actions

Use keyword and vector scores with an explicit fusion strategy, group chunk hits by file, return evidence, and calibrate insufficient-match behavior on no-match queries. Do not invent confidence percentages. A brute-force numpy vector scan is acceptable for a measured hundreds-file MVP; adopt a vector database only if measurement requires it.

Implement file opening and reveal on Windows/macOS with safe platform APIs or argument-list processes. Test spaces, Unicode, duplicate filenames, missing files, symlink escapes, locked files, and root changes. Do not open arbitrary executable content. Folder dialog failures must leave manual path selection usable.

**Gate:** Relevant documents appear in top three on the held-out queries, no-match queries do not return misleading results, and OS actions work on both tested systems.

## Phase A5 — Verification and handoff

Meaningful backend tests: root scoping; no source-file modifications; bad-file isolation; cache reuse/invalidation; deleted-file removal; job cancellation/restart; retrieval on labeled fixtures; error behavior for Ollama failure; safe OS-action arguments. Use stub inference for deterministic unit tests, but separately run genuine local-model integration tests.

Run a corpus of several hundred files and record dataset composition, elapsed time, RAM, searchable count, errors, and rescan behavior. Do not extrapolate laptop results to all Windows/macOS machines.

For local proof: new unseen files, empty/new test index, models preinstalled, network disabled, index and query successful, and real process/inference activity. Inspect backend, browser, and Ollama traffic; a source URL scan or counter alone is insufficient proof. Record verified vs unverified findings.

Deliver the backend launch command, pinned requirements, chosen exact model/prefixes, platform caveats, API examples, test results, and local-proof report to Builder B. Builder B writes final disclosures from these facts.

## First prompt to your coding assistant

> Read this entire guide and any repository AGENTS.md. Work only in Builder A's ownership. Inspect the environment, then implement Phase A1 and the minimum Phase A2 vertical slice. Follow the shared v1 API exactly. Do not implement cleanup or generative chat. Use real local embeddings; record measured results and limitations. Send the teammate actual API examples as soon as the TXT search slice runs. Finish with files changed, checks run, results, and the next integration step.
