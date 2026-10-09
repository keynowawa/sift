# Local verification — Phase A5, October 10, 2026

This is a record of actual checks on macOS 26.1, Apple M1 (8 CPU/8 GPU cores), 8 GB RAM, Python 3.13.1 and Ollama 0.40.2. It is not a Windows or clean-machine certification. No features/API fields were added in Phase A5. A network-related correction was necessary: see the telemetry finding below.

## Verified versus unverified

| Claim | Evidence/status |
|---|---|
| Deterministic backend behavior | 17 stub-based/unit tests passed after the telemetry correction, 7.52 seconds; one upstream TestClient/httpx deprecation warning. |
| Pinned setup used | All 40 installed versions match requirements.txt; pip check found no broken requirements. Temporary non-cloud venv described below. |
| Preinstalled model | /api/tags before testing reports nomic-embed-text:v1.5, F16, 137M, 768 dimensions, installed size 274302450 bytes, digest 0a109f422b47e3a30ba2b10eca18548e944e8a23073ee3f3e947efcf3c45e59f. No model/dependency pull in these runs. |
| Fresh real inference | Separate Uvicorn process on loopback port 8766, fresh temporary SQLite index, per-run UUID source text and filenames, real Ollama and OCR. See the final HTTP record below and API_EXAMPLES.md. |
| Operation with external access disabled for the backend | Actual macOS sandbox-exec profile denies outbound connections except loopback and is inherited by the backend. A separate probe to external TCP returned PermissionError errno 1; 127.0.0.1:11434 remained accessible. Real OCR, embeddings and queries succeeded inside that profile. |
| Physical offline operation | **Passed on macOS, user-confirmed interface state.** The user confirms Wi-Fi, Ethernet and VPN were disconnected throughout the successful local-copy retry recorded below. Saved real HTTP/index/query results were inspected. No OS interface snapshot/capture was recorded in that retry; earlier preparation checks showing Wi-Fi on belong to earlier runs. |
| Backend/Ollama OS traffic | OS nettop/lsof and ps observed real loopback connections and inference processes. There was also pre-fix backend external HTTPS; see below. Final observer runs outside the sandbox because an observer inside it failed with NStatManagerCreate failed. |
| Browser/full frontend traffic | **Unverified.** Chrome network-process nettop sampling included a loopback connection with zero bytes, plus existing unrelated external sockets. Chrome and in-app browser controls both returned ERR_BLOCKED_BY_CLIENT for the local API URL. No frontend build exists in this backend checkout. No successful frontend UI or browser-only-local claim follows. |
| Packet contents / unrestricted post-fix zero egress | **Unverified.** tcpdump could not open /dev/bpf0 (permission denied). nettop samples socket metadata, not packet payloads, and can miss short-lived connections. Sandbox denial gives a stronger backend restriction for that run, but does not constrain the separate existing Ollama service or browser. |
| macOS desktop actions | Phase A4 real synthetic-file open/reveal dispatch passed; source hashes unchanged. Dispatch is not proof of Finder selection or application rendering. |
| Windows compatibility | **Unverified.** Only source/API review and package availability were checked. Actual install/OCR/path/desktop/network tests require Windows. |

## Phase A5 unit-test coverage

These tests inject StubEmbedder only in test code; they do not establish local-model quality. The genuine integration and scale runs below instantiate the production Embedder and call actual Ollama.

| Required category | Test(s) |
|---|---|
| Root scoping | root_replace_reset_and_path_guards; symlink_and_hidden_skip; mac_action_guards_and_manual_picker_fallback; mac_action_rejects_replaced_root_and_dispatch_failure |
| No source modifications | real_text_roundtrip_cache_changed_deleted_readonly; duplicate_names_filters_and_source_readonly; separate integration/scale SHA-256 snapshots |
| Bad-file isolation | failures_visible_and_bad_file_isolated; genuine fresh integration malformed TXT plus supported files |
| Cache reuse/invalidation | real_text_roundtrip_cache_changed_deleted_readonly; model_configuration_change_requires_reindex |
| Deleted-file removal | real_text_roundtrip_cache_changed_deleted_readonly; scale change/add/delete rescan |
| Job cancellation/restart | cancel_conflict_reload_and_restart; cancel_long_file_between_embedding_batches; scale cancel/resume |
| Labeled retrieval | no_match_and_uncached_query; weak_ambiguous_semantic_matches_abstain_but_versions_do_not; fusion_groups_best_chunk_and_rejects_weak_lexical_overlap; genuine split evaluation in SEARCH_EVALUATION.md |
| Ollama failure | failures_visible_and_bad_file_isolated; model_missing_health_and_picker (injected failures, not a claim that the installed Ollama service was stopped) |
| Safe OS arguments | desktop_safe_args_and_missing_file; mac_action_guards_and_manual_picker_fallback; actual macOS smoke in Phase A4 |

Additional tests cover API field shape, origin/host/input checks, duplicate names/filtering, JSON API-versus-SPA routing, partial job progress, configuration invalidation, locks/permissions and manual indexing after picker failure. The suite already covered the required categories; no redundant implementation-mirroring tests were added.

## Several-hundred-file corpus: final measured run

Production inference and OCR, real-model TestClient harness, OS-enforced backend external-network restriction. TestClient is an in-memory HTTP harness; its timings are not real network HTTP latency. Sources/index live in a temporary directory and are removed afterward.

Generation: 15 copies of 20 hand-authored base topics in benchmark.DOCS, with opaque filenames in batch subfolders and copy-specific synthetic numbers/references/amounts. UTF-8 TXT/MD; minimal handwritten text-layer PDFs; Pillow 1100x600 white PNGs with font size 23. There are 300 distinct file paths but only 20 base topics. Files are small, PDFs are single-page and screenshots are clean; this does not measure large files, scanned PDFs, noisy phone photos or 300 independent real-world topics.

| Type | Count | Min bytes | Max bytes | Total bytes |
|---|---|---|---|---|
| .txt | 210 | 161 | 186 | 36918 |
| .md | 45 | 174 | 208 | 8464 |
| .pdf | 15 | 761 | 763 | 11440 |
| .png | 30 | 20556 | 22869 | 650452 |

Total source bytes: 707274. Python peak RSS: 596.56 MiB (resource.ru_maxrss / 1024² on macOS). This is the harness/backend/OCR process peak and **excludes the separate Ollama process**; no total-machine peak RAM is claimed.

| Operation | Harness wall ms | Job elapsed ms | Searchable | Failed/skipped | New embedding calls |
|---|---|---|---|---|---|
| Initial index | 30818 | 30706 | 300 | 0/0 | 300 |
| Unchanged rescan | 596 | 541 | 300 | 0/0 | 0 |
| Change/add/delete rescan | 656 | 630 | 300 | 0/0 | 2 |
| Resume after cancellation | 2768 | 2733 | 400 | 0/0 | not separately recorded |

Five uncached real-model search wall times: 194 ms, 135 ms, 144 ms, 165 ms, 125 ms. Receipt, hotel, plant and synthetic-reference targets ranked first; the submarine no-match returned empty. Weaker neighboring results remain for some positive queries.

Cancel returned HTTP 200 with {"accepted": true}; the job reached cancelled after 1 processed file, with 0 failures. That job's searchable counter counts files processed in that job, not the whole existing index. Resume completed with 400 searchable files. The harness deliberately modifies/adds/deletes fixture sources; hash snapshots before/after each backend operation verify the backend did not modify them.

Run-to-run differences (the earlier pre-fix scale run took 41,820 ms and 514.94 MiB) are not attributed to an optimization: caches, memory pressure and timing vary. Only this machine is measured. Brute-force NumPy was retained; ranking-only timing and misses are recorded in SEARCH_EVALUATION.md.

## Final fresh HTTP record and OS observations

Run nonce `7e2cfd43d48d4efaae57d5ad57eecc8b`, Uvicorn PID 12401, loopback port 8766. All 25 recorded HTTP requests/assertions passed; source hashes unchanged. The index initially returned root:null, zero indexed/searchable files and zero chunks. Empty-index search returned results:[] and still made one genuine query embedding call (0→1).

A fresh corpus contained two TXT, one MD, one text PDF, one PNG, one JPG, plus one deliberately malformed TXT and one unsupported JSON manifest: eight discovered/processed records, six searchable, one failed and one skipped. The initial job took 2,380 ms. Five positive query targets were found (receipt, electricity PNG, reservation PDF, concert JPG, new woodwind repair receipt); search response times were 51/25/19/18/20 ms. Submarine no-match returned [] in 19 ms. Unchanged rescan took 16 job ms, with embedding_calls staying 13, OCR files staying 2 and chunks_embedded staying 6. Malformed/unsupported files were retried and reported again; caching does not silently turn them into successes. Disposable index reset returned success and then zero indexed files. Real picker 503, missing file 404, invalid input 400 and root-confirmation 409 were recorded.

An external nettop observer collected 45 samples across Python.12401, ollama.1807 and llama-server.11429 during the restricted run. The observed sockets were loopback only: backend API 8766, Ollama API 11434 and resident inference runner 59936; listener wildcards were bound to 127.0.0.1. Socket byte counts changed during calls. ps observed nonzero CPU activity in Python, Ollama and the inference runner; these snapshots are activity observations, not peak CPU or RAM measurements. The runner command used the installed model blob, embedding mode and context 2048; /api/ps also reported the actual model resident. Sampling and this backend-only sandbox do not prove all-system zero traffic. Browser controls remained blocked; no real UI action is included in those HTTP requests.

## Network finding and correction

Before the telemetry correction, OS nettop attributed a connection from backend Python PID 11754 to 20.42.65.90:443; sampled bytes changed from 9091/5286 to 9605/5473 in/out. The HTTP integration otherwise succeeded. Payload was encrypted and was not inspected. This observation prevents a claim that the original backend made only local requests.

[Microsoft's ONNX Runtime privacy documentation](https://github.com/microsoft/onnxruntime/blob/main/docs/Privacy.md) describes default-on non-Windows HTTPS telemetry and recommends ORT_DISABLE_TELEMETRY=1 before initialization; API suppression alone may be too late for an initialization event. This is consistent with the observed connection, not a payload-level attribution. The extractor now forces that environment setting at module import and invokes disable_telemetry_events before creating OCR sessions, including the Windows API opt-out. Windows behavior remains untested. No runtime downloads or cloud inference were introduced.

Automatic approval review refused an unrestricted rerun because unknown telemetry could recur. Subsequent genuine tests ran with OS-enforced outbound denial except loopback. They establish useful local operation under that restriction; they do not prove the fix eliminates every possible unrestricted external attempt. Existing user-started servers were not stopped; restart them to load the correction.

## Reproduce the checks

Activate a Python 3.13 environment installed from backend/requirements.txt. This machine used /private/tmp/sift-backend-venv because Documents/.venv contained cloud-offloaded dependency files. The temporary env may disappear after cleanup; use a permanent non-cloud venv for normal setup.

```bash
python -m pytest -q backend/tests
python -m pip check
PYTHONPATH=backend python backend/evaluation/phase_a4.py
```

macOS restricted integration (empty temporary index, unique synthetic files, default evaluation port 8766, no desktop actions unless --desktop):

```bash
PYTHONPATH=backend /usr/bin/sandbox-exec   -p '(version 1)(allow default)(deny network-outbound)(allow network-outbound (remote ip "localhost:*"))'   python backend/evaluation/integration.py --fresh --hold-seconds 20
```

Use the same sandbox prefix with backend/evaluation/scale.py for the hundreds-file run. sandbox-exec is a macOS test mechanism, not a portable app installer or a Windows guarantee. Do not add --traffic inside this profile: nettop needs OS facilities blocked by it. In another Terminal, use the printed backend PID, Ollama service PID and resident inference-runner PID with `nettop -n -L 45 -p PID -J bytes_in,bytes_out`. Inspect all interfaces, not only loopback. `lsof -nP -a -p PID -i` snapshots endpoints; `ps -p PID -o pid=,pcpu=,rss=,comm=` shows process activity. Counters alone do not prove locality.

## User-run local-copy retry — physical offline success, user-confirmed

The user executed the prepared `/private/tmp/sift-offline-check` copy with `integration.py --fresh`. Saved results agree with the pasted output: nonce `abb42d6668234278a3ef612eda38ef37`, backend PID 14753, port 8766, 25 recorded successful request/assertion checks, source hashes unchanged. The 16 copied source hashes match their prepared manifest. Raw results were preserved as ignored `backend/evaluation/offline_results.json`.

The fresh index began empty. Its first search returned [] and made a real embedding call (0→1); it took 1,612 ms, not an independently isolated model-load measurement. Initial indexing took 2,874 job ms: eight files processed, six searchable, deliberately malformed bad.txt failed, unsupported manifest.json skipped. Five positive targets were retrieved in 25/24/20/18/17 ms; the submarine no-match returned [] in 18 ms. Two screenshot OCR calls and six document chunks were recorded; embedding_calls reached 13. Cached rescan took 15 job ms and made zero new embedding calls. The 15 ms in the user's final output is that rescan, not initial indexing. Reset then returned an empty index.

The user explicitly confirmed that Wi-Fi, Ethernet and VPN were disconnected throughout the successful run. This establishes physical offline operation with user-confirmed interface state and inspected genuine run results. No network-state snapshot or OS observer was captured during this retry (`os_nettop:null`). READY_FOR_TRAFFIC_CAPTURE is just a script marker, not evidence that capture ran. Independently observed interface/packet checks, browser UI and complete traffic proof remain outstanding; this retry does not establish all-process zero external attempts.

## Remaining physical offline/browser procedure

### October 10 offline attempt: source hydration failure

The user ran the integration command after the offline-test instructions, but it failed during imports with `TimeoutError: [Errno 60] Operation timed out`, before any indexing or query. Inspection found `compressed,dataless` flags on the Documents source files, including benchmark.py, integration.py and app/ai/ollama.py. Thus the original procedure also needed locally materialized application source, not just a non-cloud venv. This failed attempt establishes no offline inference success; the user's paste does not independently establish interface state.

While Wi-Fi was observed on again, all 16 application/evaluation Python source files were read as bytes and written outside Documents to `/private/tmp/sift-offline-check/backend`, with byte comparisons and SHA-256 source_manifest.json. The integration script's `--help` completed successfully there, exercising its imports. The copied key source files, ONNX Runtime initializer, three OCR model files and Ollama model blob showed no dataless flag. No product code was changed for this fix. Use that temporary project copy for the retry; it may be removed by system cleanup. Keep the preinstalled environment and Ollama running. The retry passed with user-confirmed physical disconnection, as recorded above.

```bash
cd /private/tmp/sift-offline-check
source /private/tmp/sift-backend-venv/bin/activate
PYTHONPATH=backend python backend/evaluation/integration.py --fresh
```

1. Preinstall the exact pinned dependencies, chosen Ollama model and bundled OCR models. Start Ollama. Check /api/tags. Ensure dependency/source files are locally available rather than cloud-offloaded.
2. Manually turn off Wi-Fi and disconnect Ethernet/VPN. Record networksetup/scutil (macOS), or actual interface state on Windows. Keep loopback available. No agent command here changes networking.
3. From a local Terminal run integration.py --fresh with an unused port and fresh SIFT_DATA_DIR (the script creates its own). It makes new UUID-bearing documents and an empty index, so neither source nor index is reused. Capture actual output; allow the intentionally malformed TXT failure and unsupported JSON skip, while requiring all six supported files searchable.
4. Observe Ollama and the backend with an OS tool during index/query. With appropriate local administrator permission, packet capture can supplement nettop; the attempted tcpdump capture on this run failed permissions. Do not infer zero traffic from a source scan, counters, or failed capture.
5. Test the actual frontend build in a browser: index new files, paraphrase search, empty/no-match, source previews and manual path fallback. Inspect browser Network and OS traffic for the browser, backend, Ollama and inference runner. Existing browser tabs create unrelated traffic; isolate the app session when interpreting observations.
6. Restore network connectivity when appropriate, then preserve the measured record. Repeat on actual Windows and label its results separately. No Windows numbers are supplied here.

Results apply only to the observed operations. Describe this core physical offline success as user-confirmed. Do not claim independent OS/browser offline verification, zero external requests across all processes, independent real-world retrieval accuracy or complete cross-platform support until the remaining checks are actually performed.
