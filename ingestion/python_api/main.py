"""
Personal Finance Pipeline – Python FastAPI Ingestion Service

ETL Flow:
1. User uploads CSV/Excel file via POST /ingest
2. File is read into a DataFrame, cleaned (normalized headers, parse dates, handle missing values)
3. Cleaned DataFrame is converted back to CSV bytes and uploaded to GCS
"""

from fastapi import FastAPI
from routers.ingest import router as ingest_router

app = FastAPI(
    title="Finance Ingestion API",
    description="Primary data ingestion service for personal finance pipeline",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(ingest_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "python-api"}