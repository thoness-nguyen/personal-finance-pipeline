// =============================================================================
// File: EtLT/load/plans.ts
// Source: plans (Monthly_Plans sheet)
// Target table: monthly_plans
// Contract: export async function load(): Promise<number>
//
// Reads from the raw GCS blob. No FK lookups — year + month are natural key.
// =============================================================================

import Papa from "papaparse";
import { downloadCsvFromGCS } from "../staging/GcsService";
import { getConnection, parseAmount } from "./DbHelpers";

const RAW_BLOB = "raw/plans_raw.csv";

const SQL = `
  INSERT INTO monthly_plans (plan_year, plan_month, fixed_budget, savings_target, note)
  VALUES (?, ?, ?, ?, ?)
  ON DUPLICATE KEY UPDATE
    fixed_budget   = VALUES(fixed_budget),
    savings_target = VALUES(savings_target),
    note           = VALUES(note)
`;

export async function load(): Promise<number> {
  const buffer = await downloadCsvFromGCS(RAW_BLOB);
  const { data: rows } = Papa.parse<Record<string, any>>(buffer.toString(), {
    header:          true,
    skipEmptyLines:  true,
    transformHeader: (h) => h.trim().toLowerCase(),
  });

  if (!rows.length) throw new Error("Plans raw CSV is empty.");

  const conn = await getConnection();
  let count = 0;
  try {
    for (const r of rows) {
      const year  = parseInt(r.year  ?? "", 10);
      const month = parseInt(r.month ?? "", 10);
      if (isNaN(year) || isNaN(month)) continue;
      await conn.execute(SQL, [
        year,
        month,
        parseAmount(r.fixed_budget),
        parseAmount(r.savings_target),
        r.note || null,
      ]);
      count++;
    }
    await conn.commit?.();
  } finally {
    await conn.end();
  }
  return count;
}
