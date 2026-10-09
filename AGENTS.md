# Working instructions

Read README.md and the relevant builder guide in docs/ before making changes. This project is a content-search assistant; do not implement the old cleanup concept.

- Backend ownership: backend/, backend dependency files, .gitignore, docs/BACKEND.md, docs/SEARCH_EVALUATION.md, docs/VERIFY_LOCAL.md, and docs/API_EXAMPLES.md.
- Frontend/product ownership: frontend/, scripts/, demo/, README.md, DISCLOSURES.md, docs/PRODUCT_TESTING.md, docs/DEMO.md, and docs/CROSS_PLATFORM.md.
- Respect the shared API contract in both guides. Update both copies together when an agreed change is necessary.
- Keep user files read-only and restrict filesystem access to the selected root. Never upload indexed content or add cloud inference.
- Use actual local inference. Development fixtures must be explicitly labeled and never silently substitute for real results.
- Preserve error, loading, empty, and partial-progress states. Report tested and unverified behavior honestly.
- Avoid committing personal files, generated indexes, secrets, dependencies, or local caches.
- Run checks appropriate to each change and report results. Windows and macOS support each require actual verification.
- Do not edit the other builder's owned files without coordination.
