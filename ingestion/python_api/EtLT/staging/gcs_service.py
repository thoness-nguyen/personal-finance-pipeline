# =============================================================================
# Purpose: Provides helper functions for uploading and downloading files from
#          Google Cloud Storage (GCS) using the google-cloud-storage SDK.
#          Bucket name and credentials are read from environment variables.
# =============================================================================

from io import BytesIO
import os
import pandas as pd
from google.cloud import storage
from dotenv import load_dotenv

load_dotenv()


def _get_bucket():
    bucket_name = os.getenv("GCS_BUCKET_NAME")
    if not bucket_name:
        raise ValueError("GCS_BUCKET_NAME environment variable is not set.")
    client = storage.Client()
    return client.bucket(bucket_name)

_DEDUP_KEY_COLS = ["date", "account", "transaction_type", "amount", "type_payment", "category", "sub_category"]

def append_to_gcs(new_df: pd.DataFrame, blob_name: str) -> str:
    """Download existing CSV, append new rows, deduplicate by key columns, re-upload."""
    # Normalize column names on incoming data
    new_df = new_df.copy()
    new_df.columns = new_df.columns.str.strip().str.lower()

    try:
        existing_bytes = download_from_gcs(blob_name)
        existing_df = pd.read_csv(BytesIO(existing_bytes), encoding="utf-8-sig")
        # Normalize existing columns so merge aligns correctly
        existing_df.columns = existing_df.columns.str.strip().str.lower()
        merged_df = pd.concat([existing_df, new_df], ignore_index=True)
    except FileNotFoundError:
        merged_df = new_df  # first run, no existing file

    # Deduplicate on key columns; fall back to all columns if keys are absent
    key_cols = [c for c in _DEDUP_KEY_COLS if c in merged_df.columns]
    if key_cols:
        merged_df = merged_df.drop_duplicates(subset=key_cols, keep="last")
    else:
        str_df = merged_df.astype(str)
        merged_df = merged_df.loc[~str_df.duplicated()]

    file_bytes = merged_df.to_csv(index=False).encode("utf-8-sig")
    return upload_to_gcs(file_bytes, blob_name)

def upload_to_gcs(file_bytes: bytes, destination_blob_name: str) -> str:
    """
    Upload raw bytes to a GCS bucket.

    Args:
        file_bytes: Raw bytes of the file to upload.
        destination_blob_name: Target path/name inside the GCS bucket.

    Returns:
        gs:// URI of the uploaded object.
    """
    if not file_bytes:
        raise ValueError("file_bytes cannot be empty.")

    if not destination_blob_name:
        raise ValueError("destination_blob_name is required.")

    bucket = _get_bucket()
    blob = bucket.blob(destination_blob_name)

    # Upload from memory
    blob.upload_from_string(file_bytes, content_type="text/csv")

    return f"gs://{bucket.name}/{destination_blob_name}"


def download_from_gcs(source_blob_name: str) -> bytes:
    """
    Download a file from GCS and return its bytes.

    Args:
        source_blob_name: Path/name of the blob inside the GCS bucket.

    Returns:
        Raw bytes of the downloaded file.
    """
    if not source_blob_name:
        raise ValueError("source_blob_name is required.")

    bucket = _get_bucket()
    blob = bucket.blob(source_blob_name)

    if not blob.exists():
        raise FileNotFoundError(f"Blob '{source_blob_name}' does not exist.")

    return blob.download_as_bytes()