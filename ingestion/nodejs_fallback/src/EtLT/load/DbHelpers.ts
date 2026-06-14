// =============================================================================
// File: EtLT/load/DbHelpers.ts
// Purpose: Shared MySQL utilities — mirrors Python's EtLT/load/db_helpers.py.
//   Provides connection factory and FK-resolution helpers used by all
//   loader modules (plans.ts, plan_items.ts, transactions.ts).
// =============================================================================

import mysql from "mysql2/promise";

export interface LookupMaps {
  account:     Record<string, number>;
  category:    Record<string, number>;
  subcategory: Record<string, number>;
  plan:        Record<string, number>;
}

export function getConnection(): Promise<mysql.Connection> {
  return mysql.createConnection({
    host:     process.env.MYSQL_HOST     ?? "mysql",
    user:     process.env.MYSQL_USER     ?? "finance_user",
    password: process.env.MYSQL_PASSWORD ?? "",
    database: process.env.MYSQL_DATABASE ?? "finance_db",
    charset:  "utf8mb4",
  });
}

export async function buildLookupMaps(conn: mysql.Connection): Promise<LookupMaps> {
  const [accounts]      = await conn.execute<any[]>("SELECT account_id, account_name FROM accounts");
  const [categories]    = await conn.execute<any[]>("SELECT category_id, category_name FROM categories");
  const [subcategories] = await conn.execute<any[]>("SELECT subcategory_id, subcategory_name FROM subcategories");
  const [plans]         = await conn.execute<any[]>("SELECT plan_id, plan_year, plan_month FROM monthly_plans");

  return {
    account:     Object.fromEntries(accounts.map(     (r: any) => [r.account_name.trim().toLowerCase(),     r.account_id])),
    category:    Object.fromEntries(categories.map(   (r: any) => [r.category_name.trim().toLowerCase(),    r.category_id])),
    subcategory: Object.fromEntries(subcategories.map((r: any) => [r.subcategory_name.trim().toLowerCase(), r.subcategory_id])),
    plan:        Object.fromEntries(plans.map(        (r: any) => [`${r.plan_year}-${String(r.plan_month).padStart(2, "0")}`, r.plan_id])),
  };
}

/** Case-insensitive name → id. Returns null and logs a warning if missing. */
export function resolve(
  map: Record<string, number>,
  key: string,
  context: string
): number | null {
  if (!key || key.trim() === "") return null;
  const result = map[key.trim().toLowerCase()];
  if (result === undefined) {
    console.warn(`[DbHelpers] WARNING: cannot resolve ${context}='${key}' — will insert NULL`);
    return null;
  }
  return result;
}

/** Strip commas/whitespace → integer (VND has no decimals). */
export function parseAmount(value: any): number {
  if (value == null || String(value).trim() === "") return 0;
  const cleaned = String(value).replace(/,/g, "").trim();
  const num = parseFloat(cleaned);
  return isNaN(num) ? 0 : Math.round(num);
}
