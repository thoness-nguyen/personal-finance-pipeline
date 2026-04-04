"""
Personal Finance Pipeline – Python FastAPI Ingestion Service
Primary ingestion endpoint: accepts CSV/Excel uploads, cleans data, stores to GCS.

TODO:
- Implement POST /ingest endpoint in routers/ingest.py
- Implement GCS upload/download in services/gcs_service.py
- Implement pandas cleaning logic in services/cleaner.py
"""

from fastapi import FastAPI
# TODO: Uncomment once router is implemented
# from routers.ingest import router as ingest_router

app = FastAPI(
    title="Finance Ingestion API",
    description="Primary data ingestion service for personal finance pipeline",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# TODO: Include ingest router once implemented
# app.include_router(ingest_router, prefix="/api/v1")


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "python-api"}