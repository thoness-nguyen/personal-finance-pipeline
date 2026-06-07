# Python FastAPI – Primary Ingestion Service

This service is the **primary data ingestion endpoint** for the personal finance pipeline.

## Responsibilities

- Accept CSV / Excel file uploads via POST `/ingest`
- Upload raw files to GCS Data Lake `/raw` zone
- Clean and normalize data using pandas
- Upload cleaned files to GCS `/processed` zone
- Expose health check at GET `/health`

## Structure

```
python_api/
├── main.py          # FastAPI app entrypoint
├── routers/
│   └── ingest.py    # POST /ingest endpoint
├── APIservices/
│   ├── gcs_service.py   # GCS upload/download helpers
│   └── cleaner.py       # pandas cleaning logic
└── tests/
    └── test_ingest.py
```

## Setup

See root README.md for full setup instructions.
