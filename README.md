# Sift

Find the receipt, screenshot, or document you remember, even when you do not remember its filename, without uploading your files.

Sift is a planned local file search assistant for Windows and macOS. The repository currently contains the build handoffs and hackathon reference materials; the application is not implemented yet.

## Intended MVP

Choose a folder, index supported files locally, search by their contents, inspect matching source excerpts, and open the original file. Start with TXT/MD, text-layer PDFs, and PNG/JPG screenshots. User files remain read-only.

The planned stack is Python/FastAPI, SQLite, local OCR, Ollama embeddings, and React/TypeScript/Vite. Model selection and platform compatibility must be validated during implementation. Internet access is expected for dependency and model installation; offline runtime remains a goal to verify, not a current tested claim.

## Team workflow

- Builder A: backend, local inference, indexing, retrieval, and filesystem integration. See [the backend guide](docs/SIFT_BUILDER_A_BACKEND.md).
- Builder B: interface, setup scripts, product testing, documentation, and demo. See [the frontend guide](docs/SIFT_BUILDER_B_FRONTEND.md).
- Work in separate checkouts on `backend-search` and `frontend-product`; open pull requests into `main`.
- Both guides include the same API contract. Coordinate changes to it before implementation.
- First integration milestone: index one real text file, search it through the UI, preview it, and open it.

## Setup

Runnable setup instructions will be added when the first implementation is available. Do not commit personal documents, local indexes, secrets, or generated private test data.

## Hackathon reference

[AppBuildersPH Local AI guide](appbuildersph-hackathon-2026-guide.md) reorganizes supplied materials and notes and flags items to confirm with organizers. The accompanying PDF is a reference copy. Disclose existing code/assets, libraries, models, and AI development tools used in the build.
