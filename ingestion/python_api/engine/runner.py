# =============================================================================
# File: engine/runner.py
# Purpose: Generic EtLT engine.  Reads pipeline_manifest.json, resolves the
#          dependency order, and executes the Extract → stage-raw → Transform
#          → stage-processed → Load flow for each enabled source.
#
#   Each source entry in the manifest declares:
#     sheet_id / sheet_name  – where to extract data from
#     raw_blob               – GCS path for the raw staged CSV
#     processed_blob         – GCS path for the cleaned CSV (null if no cleaner)
#     cleaner.enabled        – whether to run a transform step
#     cleaner.path           – dotted module path, e.g. "EtLT.transform.expenses"
#                              module must expose:  clean(df) -> df
#     loader.enabled         – whether to load into MySQL
#     loader.path            – dotted module path, e.g. "EtLT.load.transactions"
#                              module must expose:  load() -> int
#     depends_on             – list of source ids that must run first
# =============================================================================

import importlib
import json
import os
import sys
from graphlib import TopologicalSorter
from io import BytesIO
from pathlib import Path

import pandas as pd

from EtLT.staging.gcs_service import append_to_gcs, download_from_gcs, upload_to_gcs
from EtLT.extract.spreadsheet_service import fetch_sheet_data, dataframe_to_csv_bytes

_MANIFEST_PATH = Path(os.getenv("MANIFEST_PATH", str(Path(__file__).parent.parent.parent / "pipeline_manifest.json")))


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _import_module(dotted_path: str):
    """Import a module by dotted path (e.g. 'transform.expenses')."""
    return importlib.import_module(dotted_path)


def _topological_order(sources: list) -> list:
    """Return sources sorted so that every dependency runs before its dependant."""
    graph = {s["id"]: set(s.get("depends_on", [])) for s in sources}
    ts = TopologicalSorter(graph)
    order = list(ts.static_order())
    source_map = {s["id"]: s for s in sources}
    return [source_map[sid] for sid in order if sid in source_map]


# ─── Single-source executor ───────────────────────────────────────────────────

def run_source(source: dict) -> dict:
    """
    Execute the full EtLT flow for one manifest entry.
    Returns a result dict with status, row counts, and GCS URIs.
    """
    sid = source["id"]
    creds = os.getenv("GOOGLE_SHEETS_CREDENTIALS") or os.getenv("GOOGLE_SHEETS_CREDENTIALS_LOCAL")
    sheet_id = source["sheet_id"]
    sheet_name = source["sheet_name"]

    # Extract
    print(f"[runner:{sid}] E — extracting from sheet '{sheet_name}'")
    df = fetch_sheet_data(sheet_id, sheet_name, creds, as_type="dataframe")
    if df is None or df.empty:
        raise ValueError(f"Sheet '{sheet_name}' returned no data.")

    # Stage raw (append + deduplicate)
    raw_blob = source["raw_blob"]
    print(f"[runner:{sid}] t — staging raw → {raw_blob}")
    gcs_raw_uri = append_to_gcs(new_df=df, blob_name=raw_blob)

    gcs_processed_uri = None

    # Transform (cleaner, if enabled)
    cleaner_cfg = source.get("cleaner", {})
    if cleaner_cfg.get("enabled"):
        cleaner_path = cleaner_cfg["path"]
        print(f"[runner:{sid}] T — cleaning with '{cleaner_path}'")
        raw_bytes = download_from_gcs(raw_blob)
        raw_df = pd.read_csv(BytesIO(raw_bytes), encoding="utf-8-sig")
        cleaner = _import_module(cleaner_path)
        cleaned_df = cleaner.clean(raw_df)
        if cleaned_df is None or cleaned_df.empty:
            raise ValueError(
                f"Cleaner '{cleaner_path}' produced an empty DataFrame for source '{sid}'."
            )
        processed_blob = source["processed_blob"]
        print(f"[runner:{sid}] T — staging processed → {processed_blob}")
        gcs_processed_uri = upload_to_gcs(
            file_bytes=dataframe_to_csv_bytes(cleaned_df),
            destination_blob_name=processed_blob,
        )
    elif source.get("processed_blob"):
        # If no cleaner but processed_blob is defined, copy raw to processed for downstream steps
        processed_blob = source["processed_blob"]
        print(f"[runner:{sid}] T — no cleaner, copying raw → {processed_blob}")
        raw_bytes = download_from_gcs(raw_blob)
        gcs_processed_uri = upload_to_gcs(
            file_bytes=raw_bytes,
            destination_blob_name=processed_blob,
        )

    # Load to MySQL 
    loader_cfg  = source.get("loader", {})
    rows_loaded = 0
    if loader_cfg.get("enabled"):
        loader_path = loader_cfg["path"]
        print(f"[runner:{sid}] L — loading with '{loader_path}'")
        loader = _import_module(loader_path)
        rows_loaded = loader.load()

    result = {
        "status": "ok",
        "rows_in_sheet": len(df),
        "gcs_raw": gcs_raw_uri,
        "rows_loaded": rows_loaded,
    }
    if gcs_processed_uri:
        result["gcs_processed"] = gcs_processed_uri

    print(f"[runner:{sid}] done — rows_loaded={rows_loaded}")
    return result


# ─── Pipeline entry point ─────────────────────────────────────────────────────

def run_pipeline(source_ids: list = None) -> dict:
    """
    Run the EtLT pipeline for all enabled sources (or a filtered subset).

    Execution order respects each source's depends_on list.
    Failures are isolated: one failed source does not abort the rest.

    Args:
        source_ids: Optional list of source IDs to run.  If None, all
                    enabled sources in the manifest are executed.

    Returns:
        Dict mapping source_id → result dict with keys:
          status ("ok" | "error"), rows_in_sheet, gcs_raw,
          rows_loaded, gcs_processed (if applicable), error (if failed).
    """
    with open(_MANIFEST_PATH, encoding="utf-8") as f:
        manifest = json.load(f)

    sources = [s for s in manifest["sources"] if s.get("enabled", True)]
    if source_ids:
        sources = [s for s in sources if s["id"] in source_ids]

    ordered = _topological_order(sources)
    results: dict = {}

    for source in ordered:
        sid = source["id"]
        try:
            results[sid] = run_source(source)
        except Exception as exc:
            results[sid] = {"status": "error", "error": str(exc)}
            print(f"[runner:{sid}] ERROR — {exc}", file=sys.stderr)

    return results
