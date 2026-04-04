# =============================================================================
# File: tests/test_ingest.py
# Purpose: Stub test file for the ingestion API endpoints and services.
#          Uses pytest + httpx (AsyncClient) to test the FastAPI app.
# =============================================================================

# TODO: import pytest
# TODO: from httpx import AsyncClient
# TODO: from main import app


# TODO: Test case – health endpoint returns 200 with {"status": "ok"}
# async def test_health_check():
#     async with AsyncClient(app=app, base_url="http://test") as client:
#         response = await client.get("/health")
#     assert response.status_code == 200
#     assert response.json()["status"] == "ok"


# TODO: Test case – POST /api/v1/ingest with a valid CSV returns 200
# async def test_ingest_valid_csv():
#     ...


# TODO: Test case – POST /api/v1/ingest with an invalid file type returns 422
# async def test_ingest_invalid_file_type():
#     ...


# TODO: Test case – clean_expenses strips whitespace and flags bad amounts
# def test_clean_expenses_flags_bad_amounts():
#     ...


# TODO: Test case – clean_expenses drops fully duplicate rows
# def test_clean_expenses_drops_duplicates():
#     ...


# TODO: Test case – upload_to_gcs raises NotImplementedError until implemented
# def test_upload_to_gcs_not_implemented():
#     ...
