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
        const parsedDate = new Date(row.date);
        const amountFields = ["amount", "balance"]

        if (!row.date || isNaN(parsedDate.getTime())) {
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
            date: parsedDate.toLocaleDateString("en-US"),
            source_api: "nodejs",
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