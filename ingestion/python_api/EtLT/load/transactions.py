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
    df = df.astype(object).where(pd.notnull(df), None)

    # Skip rows that are flagged as needing manual review
    if "needs_cleaning" in df.columns:
        df = df[df["needs_cleaning"].astype(str).str.lower() != "true"]

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            maps = _build_lookup_maps(cursor)

            # Load existing natural keys to prevent re-inserting rows already in MySQL.
            # Uses raw source columns (not FK-resolved IDs) so NULL account_id can't
            # cause duplicates to slip past the unique index.
            cursor.execute(
                "SELECT transaction_date, amount, transaction_type, "
                "IFNULL(spending_type,'') AS spending_type, "
                "IFNULL(payment_method,'') AS payment_method, "
                "IFNULL(note,'') AS note "
                "FROM transactions"
            )
            existing_keys = {
                (str(r["transaction_date"]), int(r["amount"]), r["transaction_type"],
                 r["spending_type"], r["payment_method"], r["note"])
                for r in cursor.fetchall()
            }

            data = []
            skipped = 0

            for _, row in df.iterrows():
                txn_date = row.get("date")
                try:
                    date_str = str(pd.to_datetime(txn_date).date())
                except Exception:
                    skipped += 1
                    continue

                nat_key = (
                    date_str,
                    _parse_amount(row.get("amount")),
                    str(row.get("transaction_type") or ""),
                    str(row.get("spending_type") or ""),
                    str(row.get("type_payment") or ""),
                    str(row.get("note") or ""),
                )
                if nat_key in existing_keys:
                    skipped += 1
                    continue

                account_id     = _resolve(maps["account"],
                                          str(row.get("account", "")), "account")
                category_id    = _resolve(maps["category"],
                                          str(row.get("category", "")), "category")
                subcategory_id = _resolve(maps["subcategory"],
                                          str(row.get("sub_category", "")), "subcategory")

                plan_id = None
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
                    "python",
                ))

            if data:
                cursor.executemany(_SQL, data)
        conn.commit()
    finally:
        conn.close()

    print(f"[loader:transactions] inserted={len(data)}, skipped={skipped}")
    return len(data)
