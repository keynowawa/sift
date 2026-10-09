# Product testing

## Status

No end-to-end user test has been run. The backend and real local embedding flow are not yet available in this checkout. The frontend production build succeeds, but that does not verify indexing, retrieval quality, previews, or native file actions.

## Repeatable tasks

Use only synthetic files in a disposable test folder. Record corpus size and composition, OS and hardware, whether the participant has seen the files, indexing duration, search duration, task success, and participant effort. Do not infer hundreds-file performance from the small live-demo set.

1. Find a laptop repair receipt from the remembered phrase “replacement keyboard, PHP 2,500.”
2. Find class notes that mention photosynthesis and light energy.
3. Find a hotel booking confirmation for a named property.
4. Open the source preview and point to the excerpt that explains each match.
5. Add or change a synthetic file, rescan, and verify the changed content is searchable.
6. Search while indexing continues and verify committed files remain available.

## Results log

| Date / OS | Corpus | Task success | Initial index time | Repeat search time | Effort / notes |
| --- | --- | --- | --- | --- | --- |
| Not run | — | — | — | — | Waiting for backend integration |

Report failures and skipped files alongside successful searches. Do not convert semantic similarity into an accuracy percentage.
