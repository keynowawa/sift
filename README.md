# Sift

Find the receipt, screenshot, or document you remember—even when you do not remember its filename. Sift is designed to index and search files on your own computer, without uploading them.

## Project status

The React interface and typed v1 API client are implemented. The backend and local inference are not in this checkout, so indexing and search have not been verified end to end. Do not treat the interface build as a working search product or claim Windows/macOS support based on it alone.

## Intended MVP

Choose one folder, index its supported files locally, search for remembered content, inspect a source excerpt, and open the original file through an explicit action. The planned first formats are TXT, Markdown, text-layer PDF, and PNG/JPG screenshots. Unsupported files should be reported honestly. Original files stay read-only.

Planned architecture: Python 3.11+ and FastAPI, SQLite, local OCR, Ollama embeddings, and React/TypeScript/Vite. The embedding model is still provisional; `nomic-embed-text` is a benchmark candidate, not a confirmed requirement. Builder A must record the selected model tag and query/document prefixes after testing.

## Requirements

- Windows or macOS; only platforms actually verified in [Cross-platform status](docs/CROSS_PLATFORM.md) should be considered supported.
- Python 3.11 or newer, Node.js 20.19+ (or 22.12+), npm, and Ollama.
- Internet access during dependency/model setup. Offline runtime remains a goal to verify, not a current claim.
- A local embedding model selected and documented by Builder A.

## Setup and run

Once `backend/requirements.txt` and `backend/app/main.py` are present:

```powershell
scripts\setup.ps1
scripts\run.ps1
```

On macOS:

```sh
./scripts/setup.sh
./scripts/run.sh
```

Setup installs Python packages into `.venv`, installs the frontend from `frontend/package-lock.json`, and builds the UI. It does not download an embedding model. Follow Builder A's confirmed model and prefix instructions, then install that model explicitly with Ollama. The launch scripts currently assume the backend command `python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8765`; coordinate any change with Builder A.

For frontend-only work, from `frontend/` run `npm ci`, `npm run dev`, and `npm run build`. Vite binds to `127.0.0.1:5173` and proxies `/api` to `127.0.0.1:8765`. Production uses relative `/api` paths and expects the backend to serve the built frontend.

## Privacy and storage

The design keeps file reading, OCR, embeddings, search, and previews local. Setup requires internet to obtain packages and may require a one-time model download. Runtime offline behavior has not yet been demonstrated. The planned index location is `%LOCALAPPDATA%/Sift/` on Windows and `~/Library/Application Support/Sift/` on macOS, with an explicit data-directory override for tests. Index excerpts and embeddings are local and unencrypted; source files are read-only. See [DISCLOSURES.md](DISCLOSURES.md) for current implementation details.

## Testing and demo

- Frontend build: `npm --prefix frontend run build`.
- Generate 16 varied synthetic TXT files for the first integration slice: `python demo/generate.py`. The corpus is written to ignored `demo/generated/`; its expected targets are in `demo/manifest.json`.
- Product test plan and result log: [docs/PRODUCT_TESTING.md](docs/PRODUCT_TESTING.md).
- Demo plan and known blockers: [docs/DEMO.md](docs/DEMO.md).
- Platform verification: [docs/CROSS_PLATFORM.md](docs/CROSS_PLATFORM.md).
- Backend and actual model tests are pending Builder A's implementation.

Do not use real personal files in a demo recording. Public posting and submission require the team's explicit authorization.

## Team ownership

- Builder A owns `backend/`, backend dependencies, and backend verification docs.
- Builder B owns `frontend/`, `scripts/`, `demo/`, this README, `DISCLOSURES.md`, and product/demo/platform docs.
- API contract changes require agreement and coordinated updates in both builder guides and implementations.

## References

- [Builder A backend handoff](docs/SIFT_BUILDER_A_BACKEND.md)
- [Builder B frontend handoff](docs/SIFT_BUILDER_B_FRONTEND.md)
- [AppBuildersPH Local AI guide](appbuildersph-hackathon-2026-guide.md)
