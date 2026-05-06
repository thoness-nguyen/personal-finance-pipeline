# =============================================================================
# Purpose: Provides helper functions for uploading and downloading files from
#          Google Cloud Storage (GCS) using the google-cloud-storage SDK.
#          Bucket name and credentials are read from environment variables.
# =============================================================================

import os
from google.cloud import storage
from dotenv import load_dotenv

load_dotenv()


def _get_bucket():
    bucket_name = os.getenv("GCS_BUCKET_NAME")
    if not bucket_name:
        raise ValueError("GCS_BUCKET_NAME environment variable is not set.")
    client = storage.Client()
    return client.bucket(bucket_name)


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
    blob.upload_from_string(file_bytes)

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