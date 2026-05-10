import { cleanExpense } from "../services/Cleaner";

// ─── Helpers ────────────────────────────────────────────────────────────────

const sampleCsv = `
DATE,CATEGORY,SUB_CATEGORY,TYPE_PAYMENT,INPUT,OUTPUT,BALANCE,AMOUNT_BALANCE,NOTE,TOTAL EXPENSE MONTHLY,TOTAL EXTRA USING,TOTAL RENTING EXPENSE
"10/1/2023","Debt Payments","Personal Loans","Loan","6,000,000","","6,000,000","2,214,000","","","","-3,856,000"
"10/1/2023","Food","Daily meals","Income","","61,000","(61,000)","","","","",""
"10/1/2023","Household Expenses","Others","Income","","383,000","(383,000)","","","","",""
"10/1/2023","Income","Salary","Income","3,500,000","","3,500,000","","","","",""
"10/1/2023","Household Expenses","Rent/Mortgage","Income","","3,150,000","(3,150,000)","","","","",""
`.trim();

// ─── Test cases ─────────────────────────────────────────────────────────────

describe("cleanExpense()", () => {

    it("parses finance CSV correctly", () => {
        const { headers, data } = cleanExpense(sampleCsv);

        expect(headers).toEqual([
            "DATE",
            "CATEGORY",
            "SUB_CATEGORY",
            "TYPE_PAYMENT",
            "INPUT",
            "OUTPUT",
            "BALANCE",
            "AMOUNT_BALANCE",
            "NOTE",
            "TOTAL EXPENSE MONTHLY",
            "TOTAL EXTRA USING",
            "TOTAL RENTING EXPENSE",
        ]);

        expect(data).toHaveLength(5);
    });

    it("parses quoted values with commas correctly", () => {
        const { data } = cleanExpense(sampleCsv);

        expect((data[0] as Record<string, string>)["INPUT"])
            .toBe("6,000,000");

        expect((data[0] as Record<string, string>)["BALANCE"])
            .toBe("6,000,000");
    });

    it("handles empty fields correctly", () => {
        const { data } = cleanExpense(sampleCsv);

        expect((data[0] as Record<string, string>)["OUTPUT"])
            .toBe("");

        expect((data[1] as Record<string, string>)["INPUT"])
            .toBe("");
    });

    it("parses negative values wrapped in parentheses", () => {
        const { data } = cleanExpense(sampleCsv);

        expect((data[1] as Record<string, string>)["BALANCE"])
            .toBe("(61,000)");

        expect((data[4] as Record<string, string>)["BALANCE"])
            .toBe("(3,150,000)");
    });

    it("returns correct row data", () => {
        const { data } = cleanExpense(sampleCsv);

        expect((data[0] as Record<string, string>)["CATEGORY"])
            .toBe("Debt Payments");

        expect((data[3] as Record<string, string>)["SUB_CATEGORY"])
            .toBe("Salary");
    });

    it("returns correct number of columns", () => {
        const { headers } = cleanExpense(sampleCsv);

        expect(headers).toHaveLength(12);
    });

    it("throws error for empty input", () => {
        expect(() => cleanExpense("")).toThrow("Data is empty!");
    });

    it("handles CSV with only headers", () => {
        const csv =
            "DATE,CATEGORY,SUB_CATEGORY,TYPE_PAYMENT,INPUT,OUTPUT,BALANCE";

        const { data } = cleanExpense(csv);

        expect(data).toHaveLength(0);
    });

});