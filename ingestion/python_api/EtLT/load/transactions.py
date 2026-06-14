# =============================================================================
# File: loaders/transactions.py
# Source: expenses (Transactions sheet)
# Target table: transactions
# Contract: expose  load() -> int  (returns number of rows inserted)
#
# Reads from the processed GCS blob (output of cleaners/expenses.py).
# FK lookups: account_id, category_id, subcategory_id, plan_id.
# =============================================================================

from io import BytesIO

import pandas as pd

from EtLT.load.db_helpers import get_connection, _build_lookup_maps, _resolve, _parse_amount
from EtLT.staging.gcs_service import download_from_gcs

_PROCESSED_BLOB = "processed/expenses_cleaned.csv"

_SQL = """
    INSERT IGNORE INTO transactions
        (transaction_date, account_id, transaction_type, spending_type,
         plan_id, category_id, subcategory_id, amount,
         payment_method, note, is_regretted, source_data)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""


def load() -> int:
    file_bytes = download_from_gcs(_PROCESSED_BLOB)
    if not file_bytes:
        raise ValueError("Processed CSV blob is empty or missing.")

    df = pd.read_csv(BytesIO(file_bytes), encoding="utf-8-sig")
    if df.empty:
        raise ValueError("Processed CSV contains no data rows.")

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            maps = _build_lookup_maps(cursor)
            data = []

            for _, row in df.iterrows():
                account_id     = _resolve(maps["account"],
                                          str(row.get("account", "")), "account")
                category_id    = _resolve(maps["category"],
                                          str(row.get("category", "")), "category")
                subcategory_id = _resolve(maps["subcategory"],
                                          str(row.get("sub_category", "")), "subcategory")

                plan_id  = None
                txn_date = row.get("date")
                if txn_date:
                    try:
                        d = pd.to_datetime(txn_date)
                        plan_id = maps["plan"].get((d.year, d.month))
                    except Exception:
                        pass

                regret = str(row.get("regret", "")).strip().lower() in ("true", "1", "yes")

                data.append((
                    txn_date,
                    account_id,
                    row.get("transaction_type") or None,
                    row.get("spending_type")    or None,
                    plan_id,
                    category_id,
                    subcategory_id,
                    _parse_amount(row.get("amount")),
                    row.get("type_payment")     or None,
                    row.get("note")             or None,
                    int(regret),
                    "python",  # always stamp python-api as the source; do not read from CSV
                ))

            cursor.executemany(_SQL, data)
        conn.commit()
    finally:
        conn.close()

    return len(data)
