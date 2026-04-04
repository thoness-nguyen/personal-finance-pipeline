// =============================================================================
// File: src/routes/ingest.js
// Purpose: Defines the POST /ingest route for the Express fallback service.
//          Uses multer for multipart file upload handling.
//          Delegates GCS upload to services/gcsService.js.
//          Sets a fallback flag in the response to indicate this service handled
//          the request instead of the primary Python API.
// =============================================================================

const express = require('express');
const multer = require('multer');

const router = express.Router();

// TODO: const { uploadToGcs } = require('../services/gcsService');

// Store upload in memory so we can forward bytes to GCS
const upload = multer({ storage: multer.memoryStorage() });

router.post('/ingest', upload.single('file'), async (req, res) => {
  /**
   * TODO: Validate that req.file exists and has an accepted MIME type.
   * TODO: Call uploadToGcs(req.file.buffer, req.file.originalname).
   * TODO: Persist metadata to MySQL (optional at this stage).
   * TODO: Return JSON response with { success: true, fallback: true, gcsUri }.
   */

  // TODO: Implement ingestion logic
  res.status(501).json({ error: 'Not implemented yet', fallback: true });
});

module.exports = router;
