# =============================================================================
# Purpose: Defines the POST /ingest endpoint that accepts CSV/Excel file uploads,
#          delegates cleaning to services/cleaner.py, and uploads to GCS via
#          services/gcs_service.py.
# =============================================================================

from datetime import datetime
from io import BytesIO
import os
import pandas as pd

from fastapi import APIRouter, UploadFile, File, HTTPException
from services.cleaner import clean_expenses
from services.gcs_service import upload_to_gcs, download_from_gcs, append_to_gcs
from services.spreadsheet_service import fetch_sheet_data, dataframe_to_csv_bytes

router = APIRouter()

SHEET_ID = os.getenv("SHEET_ID")
GOOGLE_SHEETS_CREDENTIALS = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
SHEET_NAME = os.getenv("SHEET_NAME")

@router.post("/ingest")
async def ingest_file():
    raw_result = push_raw_data_to_gcs()
    
    processed_result = push_processed_data_to_gcs(raw_result["blob_name"])
    
    return {
        "raw_upload": raw_result,
        "processed_upload": processed_result
    }

def push_processed_data_to_gcs(source_blob: str):
    raw_bytes = download_from_gcs(source_blob)
    
    if not raw_bytes:
        raise HTTPException(status_code=400, detail="Downloaded blob is empty.")
    
    # Convert raw bytes to DataFrame
    raw_df = pd.read_csv(BytesIO(raw_bytes), encoding="utf-8-sig")
    
    if raw_df.empty:
        raise HTTPException(status_code=400, detail="Raw dataframe is empty.")
    
    # Clean data
    cleaned_df = clean_expenses(raw_df)
    
    if cleaned_df is None or cleaned_df.empty:
        raise HTTPException(status_code=400, detail="Cleaning resulted in an empty DataFrame.")
    
    # Convert DataFrame -> CSV bytes
    file_bytes = dataframe_to_csv_bytes(cleaned_df)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    destination_blob_name = (
        f"processed/expenses_cleaned_ver_old.csv"
    )
    
    # Overwrite processed CSV (mirrors Node.js behaviour)
    gcs_uri = upload_to_gcs(file_bytes=file_bytes, destination_blob_name=destination_blob_name)
    
    return {
        "status": "success",
        "rows_processed": len(cleaned_df),
        "gcs_uri": gcs_uri
    }
    
def push_raw_data_to_gcs():
    # Fetch raw data from Google Sheets
    raw_df = fetch_sheet_data(SHEET_ID, SHEET_NAME, GOOGLE_SHEETS_CREDENTIALS)
    
    if raw_df is None or raw_df.empty:
        raise HTTPException(status_code=400, detail="Uploaded file is empty or invalid.")
    
    # Convert DataFrame -> CSV bytes
    file_bytes = dataframe_to_csv_bytes(raw_df)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    destination_blob_name = (
        f"raw/expenses_raw_ver_old.csv"
    )
    
    # Append+deduplicate raw CSV before any cleaning (mirrors Node.js behaviour)
    gcs_uri = append_to_gcs(new_df=raw_df, blob_name=destination_blob_name)
    
    return {
        "status": "success",
        "rows": len(raw_df),
        "gcs_uri": gcs_uri,
        "blob_name": destination_blob_name
    }