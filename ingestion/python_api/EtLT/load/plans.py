# =============================================================================
# File: loaders/plans.py
# Source: plans (Monthly_Plans sheet)
# Target table: monthly_plans
# Contract: expose  load() -> int  (returns number of rows upserted)
#
# Reads from the raw GCS blob (column names already normalized to lowercase
# by gcs_service.append_to_gcs).  No FK lookups required — year + month
# are the natural key.
# =============================================================================

from io import BytesIO

import pandas as pd

from EtLT.load.db_helpers import get_connection, _parse_amount
from EtLT.staging.gcs_service import download_from_gcs

_RAW_BLOB = "raw/plans_raw.csv"

_SQL = """
    INSERT INTO monthly_plans (plan_year, plan_month, fixed_budget, savings_target, note)
    VALUES (%s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        fixed_budget   = VALUES(fixed_budget),
        savings_target = VALUES(savings_target),
        note           = VALUES(note)
"""


def load() -> int:
    file_bytes = download_from_gcs(_RAW_BLOB)
    df = pd.read_csv(BytesIO(file_bytes), encoding="utf-8-sig")
    df.columns = df.columns.str.strip().str.lower()

    if df.empty:
        raise ValueError("Plans raw CSV is empty.")

    data = []
    for _, r in df.iterrows():
        year  = r.get("year")
        month = r.get("month")
        if not year or not month:
            continue
        data.append((
            int(year),
            int(month),
            _parse_amount(r.get("fixed_budget")),
            _parse_amount(r.get("savings_target")),
            r.get("note") or None,
        ))

    if not data:
        print("[loader:plans] No valid rows to upsert.")
        return 0

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.executemany(_SQL, data)
        conn.commit()
    finally:
        conn.close()

    return len(data)
