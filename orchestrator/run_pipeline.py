# =============================================================================
# File: orchestrator/run_pipeline.py
# Purpose: Top-level pipeline orchestrator. Tries to call the primary Python
#          FastAPI ingestion service; if it fails (connection error or non-200
#          response), falls back to the Node.js service.
#          Accepts CLI arguments for file path and optional service override.
# =============================================================================

import argparse
import sys

# TODO: import httpx
# TODO: from dotenv import load_dotenv
# TODO: import os


def run_python_api(file_path: str) -> dict:
    """
    POST the file at file_path to the Python API /api/v1/ingest endpoint.

    TODO: Read PYTHON_API_URL from environment (default http://localhost:8000).
    TODO: Open file and POST as multipart form data using httpx.
    TODO: Raise on non-200 status.
    TODO: Return parsed JSON response.
    """
    # TODO: Implement Python API call
    raise NotImplementedError("run_python_api is not yet implemented")


def run_nodejs_fallback(file_path: str) -> dict:
    """
    POST the file at file_path to the Node.js fallback /api/v1/ingest endpoint.

    TODO: Read NODEJS_API_URL from environment (default http://localhost:3000).
    TODO: Open file and POST as multipart form data using httpx.
    TODO: Raise on non-200 status.
    TODO: Return parsed JSON response.
    """
    # TODO: Implement Node.js fallback call
    raise NotImplementedError("run_nodejs_fallback is not yet implemented")


def main():
    """
    CLI entry point.

    TODO: load_dotenv() to populate environment variables.
    TODO: Parse --file (required) and --service (optional: python|nodejs|auto) args.
    TODO: If service == 'python' or service == 'auto': call run_python_api().
    TODO: On failure when service == 'auto': log warning and call run_nodejs_fallback().
    TODO: Print result summary to stdout.
    TODO: Exit with code 0 on success, 1 on failure.
    """
    parser = argparse.ArgumentParser(
        description="Personal Finance Pipeline Orchestrator"
    )
    parser.add_argument("--file", required=True, help="Path to the expense file")
    parser.add_argument(
        "--service",
        choices=["python", "nodejs", "auto"],
        default="auto",
        help="Which ingestion service to use (default: auto)",
    )

    # TODO: Parse args and implement orchestration logic
    args = parser.parse_args()
    print(f"[orchestrator] file={args.file} service={args.service}")
    print("[orchestrator] TODO: implement orchestration logic")
    sys.exit(0)


if __name__ == "__main__":
    main()
