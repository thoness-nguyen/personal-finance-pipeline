// =============================================================================
// File: EtLT/transform/expenses.ts
// Source: expenses (Transactions sheet)
// Contract: export function clean(rows: Record<string, any>[]): Record<string, any>[]
//
// Receives parsed rows from the raw GCS blob, returns cleaned rows.
// The runner handles CSV serialization before and after this call.
// NOTE: The legacy Cleaner.ts (CSV-string contract) is kept for tests only.
// =============================================================================

const DROP_KEYS = [
  "input", "output", "amount_balance",
  "total_expense_monthly", "total_extra_using", "total_renting_expense",
];

function cleanAmount(value: string): number | null {
  if (!value) return null;
  const isNegative = value.includes("(") && value.includes(")");
  const cleaned = value.replace(/,/g, "").replace(/[()]/g, "").replace(/[^0-9.-]/g, "");
  const num = Number(cleaned);
  return isNaN(num) ? null : isNegative ? -num : num;
}

export function clean(rows: Record<string, any>[]): Record<string, any>[] {
  return rows.flatMap((row) => {
    // Normalize keys to lowercase with underscores
    const normalized: Record<string, any> = {};
    for (const [k, v] of Object.entries(row)) {
      const normKey = k.trim().toLowerCase().replace(/\s+/g, "_");
      normalized[normKey] = typeof v === "string" ? v.trim() : v;
    }

    // Parse and validate date; drop rows with no parseable date
    const rawDate = normalized.date ?? "";
    const parsedDate = new Date(rawDate);
    if (!rawDate || isNaN(parsedDate.getTime())) return [];

    // Parse and validate amount fields; drop rows with unparseable amounts
    for (const field of ["amount", "balance"]) {
      if (field in normalized && normalized[field]) {
        const cleaned = cleanAmount(String(normalized[field]));
        if (cleaned === null) return [];
        normalized[field] = cleaned;
      }
    }

    // Drop spreadsheet artifact columns
    for (const key of DROP_KEYS) delete normalized[key];

    return [{
      ...normalized,
      date:        parsedDate.toISOString().split("T")[0],
      source_data: "nodejs",
    }];
  });
}
