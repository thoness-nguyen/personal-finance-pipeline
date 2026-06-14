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

  // Skip rows flagged as needing manual review
  const cleanRows = rows.filter(
    (r) => String(r.needs_cleaning ?? "").trim().toLowerCase() !== "true"
  );

  const conn = await getConnection();
  let count = 0;
  let skipped = 0;
  try {
    const maps = await buildLookupMaps(conn);

    // Load existing natural keys to prevent re-inserting rows already in MySQL.
    // NULL-safe comparison mirrors the Python loader logic.
    const [existingRows] = await conn.execute<any[]>(
      `SELECT transaction_date, amount, transaction_type,
              IFNULL(spending_type,'') AS spending_type,
              IFNULL(payment_method,'') AS payment_method,
              IFNULL(note,'') AS note
       FROM transactions`
    );
    const existingKeys = new Set<string>(
      existingRows.map((r: any) =>
        `${r.transaction_date}|${r.amount}|${r.transaction_type}|${r.spending_type}|${r.payment_method}|${r.note}`
      )
    );

    for (const row of cleanRows) {
      let dateStr: string | null = null;
      if (row.date) {
        const d = new Date(row.date);
        if (!isNaN(d.getTime())) {
          dateStr = d.toISOString().slice(0, 10);
        }
      }
      if (!dateStr) { skipped++; continue; }

      const natKey = [
        dateStr,
        parseAmount(row.amount),
        String(row.transaction_type ?? ""),
        String(row.spending_type    ?? ""),
        String(row.type_payment     ?? ""),
        String(row.note             ?? ""),
      ].join("|");

      if (existingKeys.has(natKey)) { skipped++; continue; }

      const account_id     = resolve(maps.account,     row.account      ?? "", "account");
      const category_id    = resolve(maps.category,    row.category     ?? "", "category");
      const subcategory_id = resolve(maps.subcategory, row.sub_category ?? "", "subcategory");

      let plan_id: number | null = null;
      const d = new Date(row.date);
      if (!isNaN(d.getTime())) {
        const planKey = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
        plan_id = maps.plan[planKey] ?? null;
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
        "nodejs",
      ]);
      count++;
      existingKeys.add(natKey); // prevent in-batch dupes from the same CSV
    }
    await conn.commit?.();
  } finally {
    await conn.end();
  }
  console.log(`[loader:transactions] inserted=${count}, skipped=${skipped}`);
  return count;
}
