// =============================================================================
// File: src/routes/Ingest.ts
// Purpose: POST /ingest — fetches data from Google Sheets, parses it,
//          uploads raw CSV to GCS.  Mirrors the Python API ETL flow.
// =============================================================================

import { Router, Request, Response, NextFunction } from "express";
import { fetchSheetData, parseOjectFromSheet, parseCsvFromObject } from "../services/SpreadsheetService";
import { downloadCsvFromGCS, uploadCsvToGCS } from "../services/GcsService";
import { cleanExpense } from "../services/Cleaner";

const router = Router();

router.post("/ingest", async (_req: Request, res: Response, next: NextFunction) => {
  try {
    const sheetId = process.env.SHEET_ID!;
    const worksheetName = process.env.SHEET_NAME!;

    if (!sheetId || !worksheetName) {
      res.status(400).json({ error: "SHEET_ID or SHEET_NAME env var is missing." });
      return;
    }

    // Step 1: fetch raw data from Sheets and upload to GCS
    const { records, destinationBlob } = await pushRawToGCS(sheetId, worksheetName);

    // Step 2: download raw CSV, clean it, upload processed CSV
    await pushProcessedToGCS(destinationBlob);

    res.json({
      success: true,
      fallback: true,
      rows: records.length,
      gcs_uri: `gs://${process.env.GCS_BUCKET_NAME}/${destinationBlob}`,
    });
  } catch (err) {
    next(err);
  }
});

export default router;

async function pushRawToGCS(sheetId: string, worksheetName: string) {
    // 1. Fetch raw rows from Google Sheets
    const rawData = await fetchSheetData(sheetId, worksheetName);

    // 2. Parse rows into objects
    const records = parseOjectFromSheet(rawData);

    // 3. Convert to CSV string
    const csvString = await parseCsvFromObject(records);

    // 4. Upload raw CSV to GCS
    const destinationBlob = `raw/expenses_raw_nodejs.csv`;
    await uploadCsvToGCS(csvString, destinationBlob);

    return { records, destinationBlob };
}

async function pushProcessedToGCS(destinationBlob: string) {
  // 1. Download raw CSV from GCS
  const raw = await downloadCsvFromGCS(destinationBlob);

  // 2. Clean the data
  const rawString  = raw.toString();
  const cleanedData = cleanExpense(rawString);

  // 3. Convert cleaned rows to CSV string
  const cleanedCsv = await parseCsvFromObject(cleanedData.data);

  // 4. Upload processed CSV
  await uploadCsvToGCS(cleanedCsv, destinationBlob.replace("raw/", "processed/").replace("expenses_raw_nodejs.csv", "expenses_cleaned_nodejs.csv"));
}
