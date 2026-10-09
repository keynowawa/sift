# Sift — Builder B: Interface, setup, product testing, demo

**Assigned to:** Your teammate. Builder A owns backend and local AI. This is a self-contained handoff suitable for your coding assistant.

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

Own `frontend/` including package/lock files, `scripts/`, `demo/`, root `README.md`, root `DISCLOSURES.md`, and `docs/PRODUCT_TESTING.md`, `docs/DEMO.md`, `docs/CROSS_PLATFORM.md`. Own the browser interface, typed API client, platform setup/launch scripts, synthetic demo data, and final submission preparation.

Do not edit `backend/`, backend requirements, `.gitignore`, or Builder A's docs without agreement. Report backend defects with the request, actual response, expected behavior, and steps to reproduce. Builder A implements native folder picking, file actions, and static serving; you implement their buttons and error handling.

Suggested frontend layout: `frontend/src/{App,api,types}.tsx/ts` with small components as needed. Use React/TypeScript/Vite, minimal CSS or a small locally bundled component approach. No remote assets or unnecessary state-management framework.

## Phase B1 — Interface skeleton and typed contract

1. Create the Vite app and typed API client for the shared v1 contract. Proxy `/api` to `http://127.0.0.1:8765` in development. Use relative `/api` URLs in release.
2. Build ready/setup-required, folder selection, indexing, search results, empty, and error states.
3. While endpoints are unavailable, use an explicit opt-in development fixture mode with a visible banner. Disable it by default and prevent its inclusion/activation in the submitted production flow. Never silently substitute data on network failure.
4. Add health retry, missing-model commands from `setup_steps`, OCR warning, folder picker plus manual path fallback, and consent.

**Gate:** UI compiles and connects to real backend health. Share a contract mismatch immediately rather than patching around it silently.

## Phase B2 — Real vertical slice

Wire index start/status, search, preview, and open/reveal for the first TXT file. Poll status roughly once a second while active, stop on terminal states, and fetch active index summary on reload. Use `active_job_id` from `/api/index` to reconnect to an active job; do not rely on client-only job history.

Keep the selected folder separate from the currently indexed root. A different root requires a clear replacement confirmation before `replace_index:true`. Do not clear results when the user cancels selection. Disable duplicate start/reset requests and show cancel acknowledgement separately from cancelled completion.

**Gate:** A user chooses a folder, indexes a real TXT file, searches it, reads the source preview, and opens it through the real backend.

## Phase B3 — Search product UX

- Make search the main action after indexing. Example placeholder: “Describe the document or screenshot you remember…”
- Display filename, relative folder, type, matching excerpt, and PDF page if available. Long paths must remain readable through wrapping/truncation and accessible full text.
- Label file modified dates as such. Do not suggest a June filter understands a date inside a receipt until that feature exists.
- Results are file cards, not a chatbot. Never display similarity as “95% accurate.”
- Support filter chips for supported types if time allows. Search must work without them.
- Keep search available over committed records during indexing and show “Searching 42 indexed files; indexing continues.”
- Empty state distinguishes no indexed/searchable files, no results, and backend/model failure.
- Reject blank queries locally; prevent stale responses replacing newer searches using cancellation or request ordering.
- Preview is extracted text/OCR in MVP. Render it as escaped text, never raw HTML. Highlighting must also escape content. Do not fetch arbitrary filesystem paths from the browser.
- “Open file” and “Show in folder” are explicit user actions. If capability is false or the file disappeared, show a useful explanation.
- Keyboard access, visible focus, readable contrast, labeled inputs, and restrained progress announcements. System fonts, locally bundled icons, no network-dependent polish.

**Gate:** A teammate unfamiliar with the interface can find a file and explain why the result matches.

## Phase B4 — Setup, launch, and demo dataset

Create `scripts/setup.sh` and `scripts/setup.ps1`, plus `scripts/run.sh` and `scripts/run.ps1`. Scripts must handle spaces in repo paths, stop on failures, keep dependencies in `.venv`, validate Python 3.11+, and report missing Node/npm/Ollama. Do not install system packages silently or require administrator access unnecessarily.

Setup: create venv → install Builder A's pinned requirements → install frontend from lockfile → build frontend → check Ollama/model → print exact model-install/start steps or download only when explicitly requested by the user running setup. Default setup may need internet; runtime must not. Run: start backend using the agreed command and open the loopback UI. Do not forcibly kill unrelated processes on port conflicts. Initial model load must remain visible.

Generate clearly synthetic TXT/PDF/screenshot demo files with uninformative names and a manifest of expected search targets. Suggested tasks: laptop repair receipt, class notes about photosynthesis, booking confirmation with a particular hotel. Use enough distractors to demonstrate retrieval; duplicates of one template do not establish real corpus variety. Keep a separate fresh set for offline proof. Coordinate additional generator dependencies with Builder A; do not modify backend requirements yourself.

Use a small corpus for live-demo speed and a separate larger corpus for scale measurements. Never claim the small demo alone proves hundreds-file performance.

**Gate:** A clean checkout can be set up following the README, with precise model prerequisites and recoverable errors.

## Phase B5 — User testing, cross-platform QA, submission

Run predefined file-finding tasks manually and through Sift. Include initial indexing time, repeat searches, success rate, and user effort. Record corpus size/composition and whether the user had seen the files. Report results honestly, including failures.

On actual Windows and macOS machines, check setup, folder paths with spaces/Unicode, index/search/preview, open/reveal, reload during scan, changed/deleted files, model-off errors, offline runtime, and incremental rescan. Share backend failures with Builder A. Mark any missing platform access as unverified, not passed.

README must explain product, actual requirements, OS support status, setup/run commands, exact model, supported formats, index location, privacy limitations, test/demo commands, and known failures. DISCLOSURES lists exact models, versions, dependencies, existing code/assets, AI coding tools, and runtime services based on actual implementation. Use Builder A's verified facts rather than anticipated claims.

Prepare a roughly 55-second video:
1. 0–8s: unfamiliar filenames and a concrete missing-document task.
2. 8–18s: real folder indexing/progress; disclose any time cut.
3. 18–35s: natural-language search → correct source excerpt → open file.
4. 35–48s: fresh file indexed and searched with network disabled and visible local activity.
5. 48–55s: product name, local benefit, hashtag/tag once confirmed.

Cached results can explain the product, but visibly distinguish them from the fresh-input inference proof. Do not record fabricated speed or output. Prepare a backup recording and a five-minute live pitch with real limits.

Prepare submission fields and links; team members explicitly handle/authorize public posting and final submission. Do not publish personal documents or the index. Reserve time for final clean-checkout verification.

## First prompt to your coding assistant

> Read this entire guide and any repository AGENTS.md. Work only in Builder B's ownership. Inspect existing files, then implement Phase B1 and integrate Phase B2 as soon as Builder A's real endpoints are available. Follow the shared v1 API. Focus on content search, source evidence, and Windows/macOS setup. Do not implement cleanup, generated chat, or silent mock fallback. Finish with files changed, checks run, backend dependencies/blockers, and the next integration step.
