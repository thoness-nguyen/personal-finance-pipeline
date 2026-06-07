# =============================================================================
# File: loaders/plan_items.py
# Source: plan_items (Plan_Items sheet)
# Target table: monthly_plan_items
# Contract: expose  load() -> int  (returns number of rows upserted)
#
# Reads from the raw GCS blob (column names already normalized to lowercase).
# FK lookups: category_id (via category name), plan_id (via year + month).
# NOTE: plans must be loaded first so that plan_id FKs exist.
# =============================================================================

from io import BytesIO

import pandas as pd

from EtLT.load.db_helpers import get_connection, _build_lookup_maps, _resolve, _parse_amount
from EtLT.staging.gcs_service import download_from_gcs

_RAW_BLOB = "raw/plan_items_raw.csv"

_SQL = """
    INSERT INTO monthly_plan_items (plan_id, category_id, budgeted, note)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        budgeted = VALUES(budgeted),
        note     = VALUES(note)
"""


def load() -> int:
    file_bytes = download_from_gcs(_RAW_BLOB)
    df = pd.read_csv(BytesIO(file_bytes), encoding="utf-8-sig")
    df.columns = df.columns.str.strip().str.lower()

    if df.empty:
        raise ValueError("Plan items raw CSV is empty.")

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            maps    = _build_lookup_maps(cursor)
            data    = []
            skipped = 0

            for _, r in df.iterrows():
                year     = r.get("year")
                month    = r.get("month")
                cat_name = str(r.get("category") or "")

                if not year or not month:
                    skipped += 1
                    continue

                plan_id     = maps["plan"].get((int(year), int(month)))
                category_id = _resolve(maps["category"], cat_name, "category")

                if plan_id is None:
                    print(
                        f"[loader:plan_items] No plan for {year}/{month} — "
                        "run plans loader first. Skipping row."
                    )
                    skipped += 1
                    continue
                if category_id is None:
                    skipped += 1
                    continue

                data.append((
                    plan_id,
                    category_id,
                    _parse_amount(r.get("budgeted")),
                    r.get("note") or None,
                ))

            if data:
                cursor.executemany(_SQL, data)
        conn.commit()
    finally:
        conn.close()

    if skipped:
        print(f"[loader:plan_items] {skipped} rows skipped (missing plan or category).")
    return len(data)
