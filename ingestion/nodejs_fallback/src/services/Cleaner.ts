import Papa from "papaparse";

export function cleanExpense(data: string) {
    if (!data || data.trim().length === 0) {
        throw new Error("Data is empty!");
    }

    const results = Papa.parse<Record<string, any>>(data, {
        header: true,
        skipEmptyLines: true,
        transformHeader: (header) => header
            .trim()
            .toLocaleLowerCase()
            .replace(/\s+/g, "_")
    });

    const dropKeys = [
        "input",
        "output",
        "amount_balance",
        "note",
        "total_expense_monthly",
        "total_extra_using",
        "total_renting_expense",
    ];

    results.data = results.data.flatMap((row) => {
        const trimmedDate = row.date?.trim() ?? "";
        const parsedDate = new Date(trimmedDate);
        const amountFields = ["amount", "balance"]

        if (!trimmedDate || isNaN(parsedDate.getTime())) {
            return [];
        }

        for (const field of amountFields) {
            if (field in row && row[field]) {
                const cleaned = cleanAmount(row[field]);
                if (cleaned === null) {
                    return [];
                }

                row[field] = cleaned;
            }
        }

        dropKeys.forEach((key) => {
            delete row[key];
        });

        return [{
            ...row,
            date: parsedDate.toISOString().split("T")[0],
            source_data: "nodejs",
        }]
    })
    return { headers: results.meta.fields, data: results.data };
}

function cleanAmount(value: string): number | null {
    if (!value) {
        return null;
    }

    const isNegative = value.includes("(") && value.includes(")");
    const cleaned = value
        .replace(/,/g, "")
        .replace(/[()]/g, "")
        .replace(/[^0-9.-]/g, "");
    const numberValue = Number(cleaned);

    if (isNaN(numberValue)) {
        return null;
    }

    return isNegative ? -numberValue : numberValue
}