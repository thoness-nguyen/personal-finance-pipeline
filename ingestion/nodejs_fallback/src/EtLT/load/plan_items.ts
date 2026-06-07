// =============================================================================
// File: EtLT/load/plan_items.ts
// Source: plan_items (Plan_Items sheet)
// Target table: monthly_plan_items
// Contract: export async function load(): Promise<number>
//
// Reads from the raw GCS blob.
// FK lookups: category_id (via category name), plan_id (via year + month).
// NOTE: plans must be loaded first so plan_id FKs exist.
// =============================================================================

import Papa from "papaparse";
import { downloadCsvFromGCS } from "../staging/GcsService";
import { getConnection, buildLookupMaps, resolve, parseAmount } from "./DbHelpers";

const RAW_BLOB = "raw/plan_items_raw.csv";

const SQL = `
  INSERT INTO monthly_plan_items (plan_id, category_id, budgeted, note)
  VALUES (?, ?, ?, ?)
  ON DUPLICATE KEY UPDATE
    budgeted = VALUES(budgeted),
    note     = VALUES(note)
`;

export async function load(): Promise<number> {
  const buffer = await downloadCsvFromGCS(RAW_BLOB);
  const { data: rows } = Papa.parse<Record<string, any>>(buffer.toString(), {
    header:          true,
    skipEmptyLines:  true,
    transformHeader: (h) => h.trim().toLowerCase(),
  });

  if (!rows.length) throw new Error("Plan items raw CSV is empty.");

  const conn = await getConnection();
  let count   = 0;
  let skipped = 0;
  try {
    const maps = await buildLookupMaps(conn);

    for (const r of rows) {
      const year    = parseInt(r.year  ?? "", 10);
      const month   = parseInt(r.month ?? "", 10);
      const catName = (r.category ?? "").trim();

      if (isNaN(year) || isNaN(month)) { skipped++; continue; }

      const planKey     = `${year}-${String(month).padStart(2, "0")}`;
      const plan_id     = maps.plan[planKey];
      const category_id = resolve(maps.category, catName, "category");

      if (!plan_id) {
        console.warn(`[loader:plan_items] No plan for ${year}/${month} — run plans loader first. Skipping.`);
        skipped++;
        continue;
      }
      if (!category_id) { skipped++; continue; }

      await conn.execute(SQL, [plan_id, category_id, parseAmount(r.budgeted), r.note || null]);
      count++;
    }
    await conn.commit?.();
  } finally {
    await conn.end();
  }

  if (skipped) console.warn(`[loader:plan_items] ${skipped} rows skipped (missing plan or category).`);
  return count;
}
