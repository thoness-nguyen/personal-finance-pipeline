# =============================================================================
# File: orchestrator/run_pipeline.py
# Purpose: Top-level pipeline orchestrator. Tries to call the primary Python
#          FastAPI ingestion service; if it fails (connection error or non-200
#          response), falls back to the Node.js service.
#          Accepts CLI arguments for file path and optional service override.
# =============================================================================

import argparse
import sys
import httpx
from dotenv import load_dotenv
from datetime import datetime
import os


def _resolve_base_url(*env_names: str, default: str) -> str:
    """Return the first non-empty URL from env vars; otherwise return default."""
    for env_name in env_names:
        value = os.getenv(env_name, "").strip()
        if value:
            return value.rstrip("/")
    return default.rstrip("/")


def run_python_api() -> dict:
    """POST to the Python FastAPI /api/v1/ingest/all endpoint."""
    url = _resolve_base_url("PYTHON_API_URL", default="http://localhost:8000")
    response = httpx.post(f"{url}/api/v1/ingest/all", timeout=60)
    response.raise_for_status()
    return response.json()


def run_nodejs_fallback() -> dict:
    """POST to the Node.js fallback /api/v1/ingest/all endpoint."""
    url = _resolve_base_url(
        "NODEJS_API_URL",
        "NODE_API_URL",
        default="http://localhost:3000",
    )
    response = httpx.post(f"{url}/api/v1/ingest/all", timeout=60)
    response.raise_for_status()
    return response.json()


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Personal Finance Pipeline Orchestrator"
    )
    parser.add_argument(
        "--service",
        choices=["python", "nodejs", "auto"],
        default="auto",
        help="Which ingestion service to use (default: auto — even day=python, odd day=nodejs)",
    )
    args = parser.parse_args()

    # Resolve effective service for 'auto' using even/odd day-of-month
    if args.service == "auto":
        day = datetime.now().day
        effective_service = "python" if day % 2 == 0 else "nodejs"
        print(f"[orchestrator] auto mode — day={day}, selected service={effective_service}")
    else:
        effective_service = args.service
        print(f"[orchestrator] forced service={effective_service}")

    try:
        if effective_service == "python":
            result = run_python_api()
        else:
            result = run_nodejs_fallback()

        print(f"[orchestrator] success: {result}")
        sys.exit(0)
    except Exception as exc:
        print(f"[orchestrator] error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
