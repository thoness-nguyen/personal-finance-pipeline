// =============================================================================
// File: EtLT/load/transactions.ts
// Source: expenses (Transactions sheet)
// Target table: transactions
// Contract: export async function load(): Promise<number>
//
// Reads from the processed GCS blob (output of transform/expenses.ts).
// FK lookups: account_id, category_id, subcategory_id, plan_id.
// =============================================================================

import Papa from "papaparse";
import { downloadCsvFromGCS } from "../staging/GcsService";
import { getConnection, buildLookupMaps, resolve, parseAmount } from "./DbHelpers";

const PROCESSED_BLOB = "processed/expenses_cleaned.csv";

const SQL = `
  INSERT IGNORE INTO transactions
    (transaction_date, account_id, transaction_type, spending_type,
     plan_id, category_id, subcategory_id, amount,
     payment_method, note, is_regretted, source_data)
  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
`;

export async function load(): Promise<number> {
  const buffer = await downloadCsvFromGCS(PROCESSED_BLOB);
  const { data: rows } = Papa.parse<Record<string, any>>(buffer.toString(), {
    header:         true,
    skipEmptyLines: true,
  });

  if (!rows.length) throw new Error("Processed CSV has no rows.");

  const conn = await getConnection();
  let count = 0;
  try {
    const maps = await buildLookupMaps(conn);

    for (const row of rows) {
      const account_id     = resolve(maps.account,     row.account      ?? "", "account");
      const category_id    = resolve(maps.category,    row.category     ?? "", "category");
      const subcategory_id = resolve(maps.subcategory, row.sub_category ?? "", "subcategory");

      let plan_id: number | null = null;
      if (row.date) {
        const d = new Date(row.date);
        if (!isNaN(d.getTime())) {
          const planKey = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
          plan_id = maps.plan[planKey] ?? null;
        }
      }

      const regret = ["true", "1", "yes"].includes(String(row.regret ?? "").trim().toLowerCase());

      await conn.execute(SQL, [
        row.date             ?? null,
        account_id,
        row.transaction_type ?? null,
        row.spending_type    ?? null,
        plan_id,
        category_id,
        subcategory_id,
        parseAmount(row.amount),
        row.type_payment     ?? null,
        row.note             ?? null,
        regret ? 1 : 0,
        row.source_data      ?? "nodejs",
      ]);
      count++;
    }
    await conn.commit?.();
  } finally {
    await conn.end();
  }
  return count;
}
