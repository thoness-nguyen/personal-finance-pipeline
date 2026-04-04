// =============================================================================
// File: src/services/gcsService.js
// Purpose: Provides a helper function to upload files to Google Cloud Storage
//          using the @google-cloud/storage SDK.
//          Bucket name is read from the GCS_BUCKET_NAME environment variable.
// =============================================================================

// TODO: const { Storage } = require('@google-cloud/storage');
// TODO: const storage = new Storage();

/**
 * Upload a file buffer to GCS.
 *
 * @param {Buffer} fileBuffer - Raw file bytes.
 * @param {string} destinationBlobName - Target path/name inside the GCS bucket.
 * @returns {Promise<string>} gs:// URI of the uploaded object.
 *
 * TODO: Get bucket name from process.env.GCS_BUCKET_NAME.
 * TODO: Create a bucket reference and blob reference.
 * TODO: Save fileBuffer to the blob using blob.save().
 * TODO: Return the gs:// URI.
 */
async function uploadToGcs(fileBuffer, destinationBlobName) {
  // TODO: Implement GCS upload
  throw new Error('uploadToGcs is not yet implemented');
}

module.exports = { uploadToGcs };
