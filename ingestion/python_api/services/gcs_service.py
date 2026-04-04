# =============================================================================
# File: services/gcs_service.py
# Purpose: Provides helper functions for uploading and downloading files from
#          Google Cloud Storage (GCS) using the google-cloud-storage SDK.
#          Bucket name and credentials are read from environment variables.
# =============================================================================

import os

# TODO: from google.cloud import storage


def upload_to_gcs(file_bytes: bytes, destination_blob_name: str) -> str:
    """
    Upload raw bytes to a GCS bucket.

    Args:
        file_bytes: Raw bytes of the file to upload.
        destination_blob_name: Target path/name inside the GCS bucket.

    Returns:
        Public or signed URL of the uploaded object.

    TODO: Instantiate google.cloud.storage.Client().
    TODO: Get bucket from env var GCS_BUCKET_NAME.
    TODO: Upload file_bytes to the specified blob.
    TODO: Return the gs:// URI or a signed URL.
    """
    # TODO: Implement GCS upload
    raise NotImplementedError("upload_to_gcs is not yet implemented")


def download_from_gcs(source_blob_name: str) -> bytes:
    """
    Download a file from GCS and return its bytes.

    Args:
        source_blob_name: Path/name of the blob inside the GCS bucket.

    Returns:
        Raw bytes of the downloaded file.

    TODO: Instantiate google.cloud.storage.Client().
    TODO: Get bucket from env var GCS_BUCKET_NAME.
    TODO: Download and return blob bytes.
    """
    # TODO: Implement GCS download
    raise NotImplementedError("download_from_gcs is not yet implemented")
