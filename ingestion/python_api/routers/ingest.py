# =============================================================================
# File: routers/ingest.py
# Purpose: Defines the POST /ingest endpoint that accepts CSV/Excel file uploads,
#          delegates cleaning to services/cleaner.py, and uploads to GCS via
#          services/gcs_service.py.
# =============================================================================

from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter()


@router.post("/ingest")
async def ingest_file(file: UploadFile = File(...)):
    """
    Accept a CSV or Excel expense file, clean it, and upload to GCS.

    TODO: Validate file extension (csv, xlsx).
    TODO: Read file contents into a pandas DataFrame.
    TODO: Call clean_expenses(df) from services/cleaner.py.
    TODO: Call upload_to_gcs(cleaned_df, filename) from services/gcs_service.py.
    TODO: Persist metadata record to MySQL via SQLAlchemy.
    TODO: Return a structured JSON response with upload details.
    """
    # TODO: Implement ingestion logic
    raise HTTPException(status_code=501, detail="Not implemented yet")
