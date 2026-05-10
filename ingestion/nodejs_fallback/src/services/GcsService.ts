import * as path from "path";
import { Storage } from "@google-cloud/storage";
import dotenv from "dotenv";

dotenv.config({ path: path.resolve(__dirname, "../../../../.env") });

const keyFilename = process.env.GOOGLE_APPLICATION_CREDENTIALS || process.env.GOOGLE_APPLICATION_CREDENTIALS_LOCAL;
const storage = new Storage(keyFilename ? { keyFilename } : {});
const bucketName = process.env.GCS_BUCKET_NAME;

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
