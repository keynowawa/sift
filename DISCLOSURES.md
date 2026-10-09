# Implementation disclosures

This disclosure records the current repository state. Update it from actual dependency files, Builder A's verified model report, and the team's final demo setup before submission.

## Current implementation

- Frontend: React 19.3.0, React DOM 19.3.0, TypeScript 7.0.2, Vite 8.3.4, and `@vitejs/plugin-react` 6.1.2. Exact frontend package versions are locked in `frontend/package-lock.json`.
- Backend, OCR, embedding model, and runtime services: not implemented or confirmed in this checkout.
- UI assets: system fonts and CSS-built shapes; no remote assets or fonts.
- Existing assets/code: this repository's handoff documents and hackathon reference guide were present before implementation. The frontend code was created for this project with AI coding assistance; no external source assets have been incorporated.
- AI development tool: OpenAI Codex (record the model/version used by the team for the final disclosure).

## Runtime and network

The planned product uses local filesystem access, local OCR, local embedding inference through Ollama, and a local HTTP interface. No cloud AI or analytics is implemented in the frontend. Package installation requires internet. Backend behavior, runtime network activity, and offline operation remain unverified until Builder A completes and the team tests the integrated application.

## Privacy limitations

The planned search index contains extracted text and embeddings and is not encrypted. Do not claim encryption, forensic erasure, zero network traffic, or offline operation until those properties are directly verified.
