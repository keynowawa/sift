# Real API responses — Phase A5

Recorded from a genuine Uvicorn HTTP integration on macOS with real preinstalled Ollama and bundled OCR. The backend ran under OS-enforced external-network denial except loopback. Evaluation port was 8766 with matching SIFT_PORT; normal launch remains 8765. No stub inference was used for these responses. Request bodies, status codes, IDs, times and snippets below are transcribed from the generated integration_results.json; whitespace/JSON escaping is formatting only.

Each run makes unique synthetic sources and an empty temporary index. This index was removed afterward: use IDs/root/job IDs returned by your own session. A completed job can contain failed/skipped files; the deliberately malformed TXT and unsupported JSON prove partial success behavior. Search may include weaker neighbors; no confidence scores are exposed. See VERIFY_LOCAL.md for physical offline/browser/Windows limitations.

Final run nonce: `7e2cfd43d48d4efaae57d5ad57eecc8b`; backend PID `12401`; 25 recorded HTTP requests; source SHA-256 snapshots unchanged. Desktop actions were omitted in this fresh run; real earlier HTTP desktop examples are retained separately below.

## 1. GET /api/health

HTTP 200

Response:
```json
{
  "status": "ready",
  "platform": "macos",
  "embedding": {
    "ready": true,
    "model": "nomic-embed-text:v1.5"
  },
  "ocr": {
    "ready": true
  },
  "capabilities": {
    "folder_picker": false,
    "open_file": true,
    "reveal_file": true
  },
  "setup_steps": []
}
```

## 2. GET /api/index

HTTP 200

Response:
```json
{
  "root": null,
  "indexed_files": 0,
  "searchable_files": 0,
  "total_chunks": 0,
  "last_updated": null,
  "active_job_id": null
}
```

## 3. GET /api/activity

HTTP 200

Response:
```json
{
  "embedding_model": "nomic-embed-text:v1.5",
  "embedding_calls": 0,
  "ocr_files": 0,
  "chunks_embedded": 0,
  "last_call_ms": null
}
```

## 4. POST /api/search

HTTP 200

Request:
```json
{
  "query": "bassoon repair receipt",
  "limit": 3,
  "file_types": []
}
```

Response:
```json
{
  "results": [],
  "elapsed_ms": 121,
  "searchable_files": 0,
  "index_in_progress": false
}
```

## 5. GET /api/activity

HTTP 200

Response:
```json
{
  "embedding_model": "nomic-embed-text:v1.5",
  "embedding_calls": 1,
  "ocr_files": 0,
  "chunks_embedded": 0,
  "last_call_ms": 120
}
```

## 6. POST /api/index/start

HTTP 202

Request:
```json
{
  "root": "/private/var/folders/93/d0gv24jd0wz7n3f_z4wj1tfw0000gn/T/sift-integration-d_1xvibl/unseen corpus ü",
  "replace_index": false
}
```

Response:
```json
{
  "job_id": "66b71473491e48529dc2ce690326bd03"
}
```

## 7. GET /api/index/status?job_id=66b71473491e48529dc2ce690326bd03

HTTP 200

Response:
```json
{
  "job_id": "66b71473491e48529dc2ce690326bd03",
  "state": "completed",
  "phase": "finished",
  "discovered": 8,
  "processed": 8,
  "searchable": 6,
  "skipped": 1,
  "failed": 1,
  "current_file": null,
  "elapsed_ms": 2380,
  "errors": [
    {
      "relative_path": "bad.txt",
      "message": "'utf-8' codec can't decode byte 0xff in position 0: invalid start byte"
    },
    {
      "relative_path": "manifest.json",
      "message": "Unsupported file type"
    }
  ]
}
```

## 8. GET /api/index

HTTP 200

Response:
```json
{
  "root": "/private/var/folders/93/d0gv24jd0wz7n3f_z4wj1tfw0000gn/T/sift-integration-d_1xvibl/unseen corpus ü",
  "indexed_files": 8,
  "searchable_files": 6,
  "total_chunks": 6,
  "last_updated": "2026-10-09T21:23:21.760943Z",
  "active_job_id": null
}
```

## 9. POST /api/search

HTTP 200

Request:
```json
{
  "query": "proof I paid to fix my notebook computer",
  "limit": 3,
  "file_types": [
    "txt"
  ]
}
```

Response:
```json
{
  "results": [
    {
      "file_id": "fe8d7f20b75d40c3a2cfd8fae007c531",
      "name": "receipt ü.txt",
      "relative_path": "receipt ü.txt",
      "file_type": "txt",
      "size_bytes": 162,
      "modified_at": "2026-10-09T21:22:43.500707Z",
      "snippet": "Laptop service invoice. Replaced damaged keyboard and cleaned cooling fan. Paid PHP 2500 at Metro Computer Clinic. Synthetic run 7e2cfd43d48d4efaae57d5ad57eecc8b.",
      "location": {
        "page": null
      },
      "match_kind": "semantic"
    },
    {
      "file_id": "cbce26d3f23742a28bac49a239ed5525",
      "name": "new instrument.txt",
      "relative_path": "new instrument.txt",
      "file_type": "txt",
      "size_bytes": 160,
      "modified_at": "2026-10-09T21:22:43.545527Z",
      "snippet": "Bassoon service receipt. Replaced the reed and repaired a damaged key on the woodwind instrument. Paid PHP 3200. Synthetic run 7e2cfd43d48d4efaae57d5ad57eecc8b.",
      "location": {
        "page": null
      },
      "match_kind": "semantic"
    }
  ],
  "elapsed_ms": 51,
  "searchable_files": 6,
  "index_in_progress": false
}
```

## 10. GET /api/files/fe8d7f20b75d40c3a2cfd8fae007c531/preview

HTTP 200

Response:
```json
{
  "file_id": "fe8d7f20b75d40c3a2cfd8fae007c531",
  "name": "receipt ü.txt",
  "relative_path": "receipt ü.txt",
  "file_type": "txt",
  "text": "Laptop service invoice. Replaced damaged keyboard and cleaned cooling fan. Paid PHP 2500 at Metro Computer Clinic. Synthetic run 7e2cfd43d48d4efaae57d5ad57eecc8b.",
  "truncated": false
}
```

## 11. POST /api/search

HTTP 200

Request:
```json
{
  "query": "electricity utility bill payment",
  "limit": 3,
  "file_types": []
}
```

Response:
```json
{
  "results": [
    {
      "file_id": "8d7a9003d5ca40e49b959fccd5d6cecd",
      "name": "bill.png",
      "relative_path": "bill.png",
      "file_type": "png",
      "size_bytes": 16788,
      "modified_at": "2026-10-09T21:22:43.532827Z",
      "snippet": "Payment successful\nElectricity utility bill\nAmount PHP 1800\nRun 7e2cfd43d48d",
      "location": {
        "page": null
      },
      "match_kind": "hybrid"
    },
    {
      "file_id": "cbce26d3f23742a28bac49a239ed5525",
      "name": "new instrument.txt",
      "relative_path": "new instrument.txt",
      "file_type": "txt",
      "size_bytes": 160,
      "modified_at": "2026-10-09T21:22:43.545527Z",
      "snippet": "Bassoon service receipt. Replaced the reed and repaired a damaged key on the woodwind instrument. Paid PHP 3200. Synthetic run 7e2cfd43d48d4efaae57d5ad57eecc8b.",
      "location": {
        "page": null
      },
      "match_kind": "semantic"
    }
  ],
  "elapsed_ms": 25,
  "searchable_files": 6,
  "index_in_progress": false
}
```

## 12. POST /api/search

HTTP 200

Request:
```json
{
  "query": "where we are staying on our Cebu trip",
  "limit": 3,
  "file_types": []
}
```

Response:
```json
{
  "results": [
    {
      "file_id": "7ad00c0b0df0407c8464ab0aae34b6cb",
      "name": "reservation.pdf",
      "relative_path": "reservation.pdf",
      "file_type": "pdf",
      "size_bytes": 696,
      "modified_at": "2026-10-09T21:22:43.501420Z",
      "snippet": "Hotel reservation confirmation. Two nights at Seaside Lodge in Cebu. Booking reference 7e2cfd43d48d4efaae57d5ad57eecc8b.",
      "location": {
        "page": 1
      },
      "match_kind": "semantic"
    }
  ],
  "elapsed_ms": 19,
  "searchable_files": 6,
  "index_in_progress": false
}
```

## 13. POST /api/search

HTTP 200

Request:
```json
{
  "query": "indie music concert admission",
  "limit": 3,
  "file_types": []
}
```

Response:
```json
{
  "results": [
    {
      "file_id": "be3525a3d1f4473bb38c2d873b98545b",
      "name": "ticket.jpg",
      "relative_path": "ticket.jpg",
      "file_type": "jpg",
      "size_bytes": 21142,
      "modified_at": "2026-10-09T21:22:43.545194Z",
      "snippet": "Concert admission\nIndie music festival\nGate opens 6 PM\nRun 7e2cfd43d48d",
      "location": {
        "page": null
      },
      "match_kind": "hybrid"
    }
  ],
  "elapsed_ms": 18,
  "searchable_files": 6,
  "index_in_progress": false
}
```

## 14. POST /api/search

HTTP 200

Request:
```json
{
  "query": "invoice for repairing my woodwind instrument",
  "limit": 3,
  "file_types": []
}
```

Response:
```json
{
  "results": [
    {
      "file_id": "cbce26d3f23742a28bac49a239ed5525",
      "name": "new instrument.txt",
      "relative_path": "new instrument.txt",
      "file_type": "txt",
      "size_bytes": 160,
      "modified_at": "2026-10-09T21:22:43.545527Z",
      "snippet": "Bassoon service receipt. Replaced the reed and repaired a damaged key on the woodwind instrument. Paid PHP 3200. Synthetic run 7e2cfd43d48d4efaae57d5ad57eecc8b.",
      "location": {
        "page": null
      },
      "match_kind": "hybrid"
    },
    {
      "file_id": "fe8d7f20b75d40c3a2cfd8fae007c531",
      "name": "receipt ü.txt",
      "relative_path": "receipt ü.txt",
      "file_type": "txt",
      "size_bytes": 162,
      "modified_at": "2026-10-09T21:22:43.500707Z",
      "snippet": "Laptop service invoice. Replaced damaged keyboard and cleaned cooling fan. Paid PHP 2500 at Metro Computer Clinic. Synthetic run 7e2cfd43d48d4efaae57d5ad57eecc8b.",
      "location": {
        "page": null
      },
      "match_kind": "semantic"
    }
  ],
  "elapsed_ms": 20,
  "searchable_files": 6,
  "index_in_progress": false
}
```

## 15. POST /api/search

HTTP 200

Request:
```json
{
  "query": "nuclear submarine reactor maintenance schematic",
  "limit": 3,
  "file_types": []
}
```

Response:
```json
{
  "results": [],
  "elapsed_ms": 19,
  "searchable_files": 6,
  "index_in_progress": false
}
```

## 16. GET /api/activity

HTTP 200

Response:
```json
{
  "embedding_model": "nomic-embed-text:v1.5",
  "embedding_calls": 13,
  "ocr_files": 2,
  "chunks_embedded": 6,
  "last_call_ms": 16
}
```

## 17. POST /api/index/start

HTTP 202

Request:
```json
{
  "root": "/private/var/folders/93/d0gv24jd0wz7n3f_z4wj1tfw0000gn/T/sift-integration-d_1xvibl/unseen corpus ü",
  "replace_index": false
}
```

Response:
```json
{
  "job_id": "28320c2af2e943e48b8ec765aec39f35"
}
```

## 18. GET /api/index/status?job_id=28320c2af2e943e48b8ec765aec39f35

HTTP 200

Response:
```json
{
  "job_id": "28320c2af2e943e48b8ec765aec39f35",
  "state": "completed",
  "phase": "finished",
  "discovered": 8,
  "processed": 8,
  "searchable": 6,
  "skipped": 1,
  "failed": 1,
  "current_file": null,
  "elapsed_ms": 16,
  "errors": [
    {
      "relative_path": "bad.txt",
      "message": "'utf-8' codec can't decode byte 0xff in position 0: invalid start byte"
    },
    {
      "relative_path": "manifest.json",
      "message": "Unsupported file type"
    }
  ]
}
```

## 19. GET /api/activity

HTTP 200

Response:
```json
{
  "embedding_model": "nomic-embed-text:v1.5",
  "embedding_calls": 13,
  "ocr_files": 2,
  "chunks_embedded": 6,
  "last_call_ms": 16
}
```

## 20. POST /api/folder/pick

HTTP 503

Request:
```json
{}
```

Response:
```json
{
  "error": {
    "code": "FOLDER_PICKER_UNAVAILABLE",
    "message": "Native folder selection is unavailable. Enter the absolute folder path instead.",
    "retryable": false
  }
}
```

## 21. GET /api/files/nonexistent/preview

HTTP 404

Response:
```json
{
  "error": {
    "code": "FILE_NOT_FOUND",
    "message": "File not found in the active index.",
    "retryable": false
  }
}
```

## 22. POST /api/search

HTTP 400

Request:
```json
{
  "query": " "
}
```

Response:
```json
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "Invalid request fields or values.",
    "retryable": false
  }
}
```

## 23. POST /api/index/start

HTTP 409

Request:
```json
{
  "root": "/private/var/folders/93/d0gv24jd0wz7n3f_z4wj1tfw0000gn/T/sift-integration-d_1xvibl/other root",
  "replace_index": false
}
```

Response:
```json
{
  "error": {
    "code": "ROOT_CONFIRMATION_REQUIRED",
    "message": "Confirm replacement before changing the indexed folder.",
    "retryable": false
  }
}
```

## 24. POST /api/index/reset

HTTP 200

Request:
```json
{
  "confirm": true
}
```

Response:
```json
{
  "ok": true
}
```

## 25. GET /api/index

HTTP 200

Response:
```json
{
  "root": null,
  "indexed_files": 0,
  "searchable_files": 0,
  "total_chunks": 0,
  "last_updated": null,
  "active_job_id": null
}
```

## Cancel and resume — separate real-model scale run

These are real response bodies from the genuine Ollama scale test using FastAPI TestClient (in-memory HTTP harness), not the separate Uvicorn TCP integration above. The index/source paths were disposable. Cancellation was issued while a new job was active; it is not guaranteed accepted for an already completed job.

POST /api/index/cancel, request:
```json
{
  "job_id": "7b9735086c584b838cef5cec2a2e79d6"
}
```

HTTP 200 response:
```json
{
  "accepted": true
}
```

GET /api/index/status for that job, HTTP 200:
```json
{
  "job_id": "7b9735086c584b838cef5cec2a2e79d6",
  "state": "cancelled",
  "phase": "finished",
  "discovered": 400,
  "processed": 1,
  "searchable": 1,
  "skipped": 0,
  "failed": 0,
  "current_file": null,
  "elapsed_ms": 37,
  "errors": []
}
```

After an actual rescan/resume, GET /api/index/status returned HTTP 200:
```json
{
  "job_id": "95331d3f93ff459f81754ccc2543de2e",
  "state": "completed",
  "phase": "finished",
  "discovered": 400,
  "processed": 400,
  "searchable": 400,
  "skipped": 0,
  "failed": 0,
  "current_file": null,
  "elapsed_ms": 2733,
  "errors": []
}
```

## Historical real desktop HTTP responses

These successful open/reveal responses were captured in the earlier 20-document integration, before Phase A4 hardening. The v1 response shape remains unchanged; Phase A4 separately tested the hardened macOS dispatch with real synthetic documents. This section does not claim Windows execution or desktop rendering in the Phase A5 run. Reuse the current search result file_id when making an action.

## POST /api/files/c88d7b88f61c445ebf015841f6dd452d/open

HTTP 200

Request:
```json
{}
```

Response:
```json
{
  "ok": true
}
```


## POST /api/files/c88d7b88f61c445ebf015841f6dd452d/reveal

HTTP 200

Request:
```json
{}
```

Response:
```json
{
  "ok": true
}
```


## Frontend interpretation

- folder_picker:false and FOLDER_PICKER_UNAVAILABLE mean keep manual absolute-path entry usable.
- state:completed with failed/skipped counts is partial success, not all documents searchable.
- Root replacement without confirmation returns HTTP 409; confirm via replace_index:true only after the user's choice.
- Empty results are valid for both an empty index and insufficient matches; use searchable_files to distinguish them.
- Poll job status and refresh index/activity from current responses. Jobs and counters in these examples are not durable IDs for your app session.
- Invalid input, missing file, picker failure and root-confirmation errors above are actual JSON error envelopes. MODEL_UNAVAILABLE behavior is covered by injected unit failures; no installed Ollama service was intentionally stopped for these examples.

## Later physical offline run — user-confirmed

The user confirmed Wi-Fi/Ethernet/VPN disconnection throughout this later real-model HTTP run. Saved results were inspected; no OS traffic capture or browser UI was part of it. The local-copy source manifest was verified. These are actual responses from that disposable index, not replacements for IDs in the earlier examples.

GET /api/index/status?job_id=8efe778058a847bb8104215e3aeb6032, HTTP 200:
```json
{
  "job_id": "8efe778058a847bb8104215e3aeb6032",
  "state": "completed",
  "phase": "finished",
  "discovered": 8,
  "processed": 8,
  "searchable": 6,
  "skipped": 1,
  "failed": 1,
  "current_file": null,
  "elapsed_ms": 2874,
  "errors": [
    {
      "relative_path": "bad.txt",
      "message": "'utf-8' codec can't decode byte 0xff in position 0: invalid start byte"
    },
    {
      "relative_path": "manifest.json",
      "message": "Unsupported file type"
    }
  ]
}
```

GET /api/activity, HTTP 200:
```json
{
  "embedding_model": "nomic-embed-text:v1.5",
  "embedding_calls": 13,
  "ocr_files": 2,
  "chunks_embedded": 6,
  "last_call_ms": 15
}
```
