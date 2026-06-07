# =============================================================================
# Purpose: Shared MySQL utilities for the finance pipeline.
#
#   Provides the database connection factory and FK-resolution helpers used
#   by all loader modules (load/plans.py, load/plan_items.py,
#   load/transactions.py).
#
#   Public API:
#     get_connection()        – pymysql.Connection
#     _build_lookup_maps()    – name→id dicts for accounts/categories/etc.
#     _resolve()              – case-insensitive name → id with warning
#     _parse_amount()         – string → int (VND, no decimals)
# =============================================================================

import os

import pymysql
import pymysql.cursors


# ─── Connection ───────────────────────────────────────────────────────────────

def get_connection() -> pymysql.Connection:
    return pymysql.connect(
        host     = os.getenv("MYSQL_HOST",     "mysql"),
        user     = os.getenv("MYSQL_USER",     "root"),
        password = os.getenv("MYSQL_PASSWORD", ""),
        database = os.getenv("MYSQL_DATABASE", "finance_db"),
        charset  = "utf8mb4",
        cursorclass = pymysql.cursors.DictCursor,
    )


# ─── Lookup helpers ───────────────────────────────────────────────────────────

def _build_lookup_maps(cursor) -> dict:
    """
    Load reference tables once per call and return name→id dicts.
    Keys in returned dict: 'account', 'category', 'subcategory', 'plan'.
    Plan map key: (year: int, month: int) → plan_id.
    """
    cursor.execute("SELECT account_id, account_name FROM accounts")
    accounts = {r["account_name"].strip().lower(): r["account_id"]
                for r in cursor.fetchall()}

    cursor.execute("SELECT category_id, category_name FROM categories")
    categories = {r["category_name"].strip().lower(): r["category_id"]
                  for r in cursor.fetchall()}

    cursor.execute("SELECT subcategory_id, subcategory_name FROM subcategories")
    subcategories = {r["subcategory_name"].strip().lower(): r["subcategory_id"]
                     for r in cursor.fetchall()}

    cursor.execute("SELECT plan_id, plan_year, plan_month FROM monthly_plans")
    plans = {(r["plan_year"], r["plan_month"]): r["plan_id"]
             for r in cursor.fetchall()}

    return {
        "account":     accounts,
        "category":    categories,
        "subcategory": subcategories,
        "plan":        plans,
    }


def _resolve(lookup_map: dict, key: str, context: str):
    """Case-insensitive name → id.  Returns None and prints a warning if missing."""
    if not key or str(key).strip() == "":
        return None
    result = lookup_map.get(str(key).strip().lower())
    if result is None:
        print(f"[db_service] WARNING: cannot resolve {context}='{key}' — will insert NULL")
    return result


def _parse_amount(value) -> int:
    """Strip commas/whitespace → int (VND has no decimals)."""
    if value is None or str(value).strip() == "":
        return 0
    cleaned = str(value).replace(",", "").replace(".", "").strip()
    try:
        return int(float(cleaned))
    except (ValueError, TypeError):
        return 0


