import { google } from "googleapis";
import * as path from "path";
import dotenv from "dotenv";

dotenv.config({ path: path.resolve(__dirname, "../../../../.env") });
const SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly"
]

// Get credentials — prefer LOCAL path (local dev), fall back to Docker mount path
const sheetsCredentials = process.env.GOOGLE_SHEETS_CREDENTIALS_LOCAL
    || process.env.GOOGLE_SHEETS_CREDENTIALS;

if (!sheetsCredentials) {
    throw new Error("Google Sheets credentials not found: set GOOGLE_SHEETS_CREDENTIALS_LOCAL or GOOGLE_SHEETS_CREDENTIALS");
}

const auth = new google.auth.GoogleAuth({
    keyFile: sheetsCredentials,
    scopes: SCOPES
})

export async function fetchSheetData(sheetId: string, worksheetName: string): Promise<string[][]> {
    // Create spreadsheets client
    const worksheets = google.sheets({
        version: "v4",
        auth
    })

    // Read spreadsheet data
    const response = await worksheets.spreadsheets.values.get({
        spreadsheetId: sheetId,
        range: `${worksheetName}!A:Z`
    })

    if (response.status !== 200 || !response.data.values) {
        throw new Error(`Failed to fetch sheet data: ${response.statusText}`);
    }

    //console.log("DEBUG response:", response.data.values.length);
    return response.data.values;
}

export async function parseCsvFromObject(records: Record<string, string>[]) {
    if (records.length == 0) {
        throw new Error("No records found");
    }

    const headers = Object.keys(records[0]);

    const csvRows = [
        headers.join(","),
        ...records.map(record => headers
            .map(header => `"${(record[header] ?? "").toString().replace(/"/g, '""')}"`)
            .join(",")
        )
    ];
    return csvRows.join("\n");
}

export function parseOjectFromSheet(data: string[][]) {
    if (!data || data.length === 0) {
        throw new Error("Data is empty!");
    }

    const headers = data[0];
    //console.log("DEBUG headers:", headers);
    const remaining = data.slice(1);

    const records = remaining.map(row => {
        const record: any = {};

        headers.forEach((header, index) => {
            record[header] = row[index] || "";
        });
        return record;
    });
    
    //console.log("DEBUG records:", records.length);
    return records;
}   

// //Test run locally
// if (require.main === module) {
//     (async () => {
//         const data = await fetchSheetData(process.env.SHEET_ID!, process.env.SHEET_NAME!);
//         if (data) {
//             const records = parseOjectFromSheet(data);
//             if (records) {
//                 parseCsvFromObject(records);
//             }
//         } else {
//             console.error("No data returned from fetchSheetData");
//         }
//     })();
// }