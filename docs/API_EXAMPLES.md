# Real API examples — macOS integration run

These are recorded responses from the real local model and synthetic files, not production fixtures. IDs/timestamps vary on each run. The temporary integration index was removed when the test ended; reuse IDs from your own run. All examples retain the v1 contract.

## GET /api/health

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

## POST /api/index/start

HTTP 202

Request:
```json
{
  "root": "/Users/kyanntagle/Documents/AB-LocalAI/backend/evaluation/generated",
  "replace_index": false
}
```

Response:
```json
{
  "job_id": "ba62b13b48734334a36113cfa576f0e5"
}
```

## GET /api/index/status?job_id=ba62b13b48734334a36113cfa576f0e5

HTTP 200

Response:
```json
{
  "job_id": "ba62b13b48734334a36113cfa576f0e5",
  "state": "completed",
  "phase": "finished",
  "discovered": 21,
  "processed": 21,
  "searchable": 20,
  "skipped": 1,
  "failed": 0,
  "current_file": null,
  "elapsed_ms": 2372,
  "errors": [
    {
      "relative_path": "manifest.json",
      "message": "Unsupported file type"
    }
  ]
}
```

## GET /api/index

HTTP 200

Response:
```json
{
  "root": "/Users/kyanntagle/Documents/AB-LocalAI/backend/evaluation/generated",
  "indexed_files": 21,
  "searchable_files": 20,
  "total_chunks": 20,
  "last_updated": "2026-10-09T19:08:27.418928Z",
  "active_job_id": null
}
```

## POST /api/search

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
      "file_id": "c88d7b88f61c445ebf015841f6dd452d",
      "name": "item_001.txt",
      "relative_path": "item_001.txt",
      "file_type": "txt",
      "size_bytes": 114,
      "modified_at": "2026-10-09T19:07:54.674321Z",
      "snippet": "Laptop service invoice. Replaced damaged keyboard and cleaned cooling fan. Paid PHP 2500 at Metro Computer Clinic.",
      "location": {
        "page": null
      },
      "match_kind": "semantic"
    },
    {
      "file_id": "1d3b02322bb94cc38db4e5c3f669c0f2",
      "name": "item_014.txt",
      "relative_path": "item_014.txt",
      "file_type": "txt",
      "size_bytes": 108,
      "modified_at": "2026-10-09T19:07:54.694565Z",
      "snippet": "Bank transfer confirmation. Tuition payment to university registrar. PHP 22000. Transaction reference TU721.",
      "location": {
        "page": null
      },
      "match_kind": "semantic"
    }
  ],
  "elapsed_ms": 25,
  "searchable_files": 20,
  "index_in_progress": false
}
```

## GET /api/files/c88d7b88f61c445ebf015841f6dd452d/preview

HTTP 200

Response:
```json
{
  "file_id": "c88d7b88f61c445ebf015841f6dd452d",
  "name": "item_001.txt",
  "relative_path": "item_001.txt",
  "file_type": "txt",
  "text": "Laptop service invoice. Replaced damaged keyboard and cleaned cooling fan. Paid PHP 2500 at Metro Computer Clinic.",
  "truncated": false
}
```

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

## POST /api/search

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
      "file_id": "33b30a8b9c514074b3da3b493fbd3b6b",
      "name": "IMG_004.png",
      "relative_path": "IMG_004.png",
      "file_type": "png",
      "size_bytes": 15134,
      "modified_at": "2026-10-09T19:07:54.687966Z",
      "snippet": "Payment successful\nElectricity utility bill\nAmount PHP 1800\nAccount 440012",
      "location": {
        "page": null
      },
      "match_kind": "hybrid"
    },
    {
      "file_id": "e5ca00a5354c440784e6147a26bb252a",
      "name": "item_019.txt",
      "relative_path": "item_019.txt",
      "file_type": "txt",
      "size_bytes": 98,
      "modified_at": "2026-10-09T19:07:54.694960Z",
      "snippet": "Grocery receipt. Rice, eggs, milk and bread. Total PHP 640. Paid cash at neighborhood supermarket.",
      "location": {
        "page": null
      },
      "match_kind": "semantic"
    },
    {
      "file_id": "c88d7b88f61c445ebf015841f6dd452d",
      "name": "item_001.txt",
      "relative_path": "item_001.txt",
      "file_type": "txt",
      "size_bytes": 114,
      "modified_at": "2026-10-09T19:07:54.674321Z",
      "snippet": "Laptop service invoice. Replaced damaged keyboard and cleaned cooling fan. Paid PHP 2500 at Metro Computer Clinic.",
      "location": {
        "page": null
      },
      "match_kind": "semantic"
    }
  ],
  "elapsed_ms": 170,
  "searchable_files": 20,
  "index_in_progress": false
}
```

## POST /api/search

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
      "file_id": "26f379793bde472ab6699894a1fff9a9",
      "name": "item_003.pdf",
      "relative_path": "item_003.pdf",
      "file_type": "pdf",
      "size_bytes": 693,
      "modified_at": "2026-10-09T19:07:54.674558Z",
      "snippet": "Hotel reservation confirmation. Two nights at Seaside Lodge in Cebu. Guest arrival June 12. Booking reference SL-482.",
      "location": {
        "page": 1
      },
      "match_kind": "semantic"
    },
    {
      "file_id": "72ae254e9cad40e19f04add72e1a2741",
      "name": "item_011.txt",
      "relative_path": "item_011.txt",
      "file_type": "txt",
      "size_bytes": 92,
      "modified_at": "2026-10-09T19:07:54.694339Z",
      "snippet": "Bus passenger ticket. Travel from Manila to Baguio. Departure 7 AM, platform three, seat 12.",
      "location": {
        "page": null
      },
      "match_kind": "semantic"
    }
  ],
  "elapsed_ms": 91,
  "searchable_files": 20,
  "index_in_progress": false
}
```

## POST /api/search

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
  "elapsed_ms": 46,
  "searchable_files": 20,
  "index_in_progress": false
}
```

## GET /api/activity

HTTP 200

Response:
```json
{
  "embedding_model": "nomic-embed-text:v1.5",
  "embedding_calls": 24,
  "ocr_files": 2,
  "chunks_embedded": 20,
  "last_call_ms": 27
}
```

## POST /api/index/start

HTTP 202

Request:
```json
{
  "root": "/Users/kyanntagle/Documents/AB-LocalAI/backend/evaluation/generated",
  "replace_index": false
}
```

Response:
```json
{
  "job_id": "47758634a72e459aa3e8bb06357f0596"
}
```

## GET /api/index/status?job_id=47758634a72e459aa3e8bb06357f0596

HTTP 200

Response:
```json
{
  "job_id": "47758634a72e459aa3e8bb06357f0596",
  "state": "completed",
  "phase": "finished",
  "discovered": 21,
  "processed": 21,
  "searchable": 20,
  "skipped": 1,
  "failed": 0,
  "current_file": null,
  "elapsed_ms": 35,
  "errors": [
    {
      "relative_path": "manifest.json",
      "message": "Unsupported file type"
    }
  ]
}
```

## GET /api/activity

HTTP 200

Response:
```json
{
  "embedding_model": "nomic-embed-text:v1.5",
  "embedding_calls": 24,
  "ocr_files": 2,
  "chunks_embedded": 20,
  "last_call_ms": 27
}
```

## Missing native picker

The picker is unavailable on this Python runtime. `POST /api/folder/pick` with `{}` returns HTTP 503:
```json
{
  "error": {
    "code": "FOLDER_PICKER_UNAVAILABLE",
    "message": "Native folder selection is unavailable. Enter the absolute folder path instead.",
    "retryable": false
  }
}
```

Use manual folder paths for Checkpoint B. Unknown API endpoints return JSON 404; invalid request values return the standard JSON 400 envelope. Backend unit tests exercise these errors.
