import * as path from "path";
import { Storage } from "@google-cloud/storage";
import dotenv from "dotenv";
import Papa from "papaparse";

const DEDUP_KEY_COLS = ["date", "category", "sub_category", "type_payment", "balance"];

function deduplicateRows(rows: Record<string, any>[]): Record<string, any>[] {
  const seen = new Map<string, Record<string, any>>();
  for (const row of rows) {
    // Normalize keys to lowercase so dedup works regardless of header casing
    const normalized: Record<string, any> = {};
    for (const k of Object.keys(row)) {
      normalized[k.trim().toLowerCase()] = row[k];
    }
    const key = DEDUP_KEY_COLS.map((col) => normalized[col] ?? "").join("|");
    seen.set(key, row);
  }
  return Array.from(seen.values());
}

dotenv.config({ path: path.resolve(__dirname, "../../../../.env") });

const keyFilename = process.env.GOOGLE_APPLICATION_CREDENTIALS || process.env.GOOGLE_APPLICATION_CREDENTIALS_LOCAL;
const storage = new Storage(keyFilename ? { keyFilename } : {});
const bucketName = process.env.GCS_BUCKET_NAME;

export async function appendCsvToGCS(newCsv: string, destinationPath: string) {
  let existingRows: Record<string, any>[] = [];
  try {
    const existing = await downloadCsvFromGCS(destinationPath);
    const parsed = Papa.parse<Record<string, any>>(existing.toString(), { header: true, skipEmptyLines: true });
    existingRows = parsed.data;
  } catch (err: any) {
    if (!err?.message?.includes("No such object")) {
        throw err;
    }
  }
  const newRows = Papa.parse<Record<string, any>>(newCsv, { header: true, skipEmptyLines: true }).data;
  const merged = deduplicateRows([...existingRows, ...newRows]);
  const mergedCsv = Papa.unparse(merged);
  await uploadCsvToGCS(mergedCsv, destinationPath);
}

export async function uploadCsvToGCS(csv: string, destinationPath: string) {
  const buffer = Buffer.from(csv);

  if (!bucketName) {
    throw new Error("GCS bucket name not found in environment variables");
  }

  const file = storage.bucket(bucketName).file(destinationPath);
  
  await file.save(buffer, {
    contentType: "text/csv"
  });
  // console.log(`Uploaded to gs://${bucketName}/${destinationPath}`);
}

export async function downloadCsvFromGCS(sourcePath: string): Promise<Buffer> {
  if (!bucketName) {
    throw new Error("GCS bucket name not found in environment variables");
  }
  const file = storage.bucket(bucketName).file(sourcePath)

  const [buffer] = await file.download();

  // console.log(`Downloaded gs://${bucketName}/${sourcePath}`);

  return buffer;
}
