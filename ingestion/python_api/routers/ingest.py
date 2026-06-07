# =============================================================================
# Purpose: FastAPI ingestion router — config-driven EtLT.
#
#   Endpoints:
#     POST /ingest/all          – run every enabled source in the manifest
#     POST /ingest/{source_id}  – run a single source by its manifest id
#
#   All pipeline logic lives in engine/runner.py.
#   Sources, blob paths, cleaners, and loaders are declared in
#   pipeline_manifest.json — no code changes required to add a new sheet.
# =============================================================================

from fastapi import APIRouter, HTTPException

from engine.runner import run_pipeline

router = APIRouter()


@router.post("/ingest/all")
async def ingest_all():
    """Run the full EtLT pipeline for every enabled source in the manifest."""
    try:
        results = run_pipeline()
        failed = [sid for sid, r in results.items() if r.get("status") == "error"]
        status = "partial_failure" if failed else "ok"
        return {"status": status, "sources": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest/{source_id}")
async def ingest_source(source_id: str):
    """Run the EtLT pipeline for a single source declared in the manifest."""
    try:
        results = run_pipeline(source_ids=[source_id])
        if source_id not in results:
            raise HTTPException(
                status_code=404,
                detail=f"Source '{source_id}' not found or not enabled in the manifest.",
            )
        result = results[source_id]
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result["error"])
        return {"status": "ok", **result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
