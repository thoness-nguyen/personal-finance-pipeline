// =============================================================================
// File: src/app.js
// Purpose: Entry point for the Express fallback ingestion service.
//          Configures middleware, mounts routes, and starts the HTTP server.
//          Used when the Python FastAPI service is unavailable.
// =============================================================================

require('dotenv').config();

const express = require('express');
const cors = require('cors');

// TODO: import ingest route once implemented
// const ingestRouter = require('./routes/ingest');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'nodejs-fallback' });
});

// TODO: Mount ingest router
// app.use('/api/v1', ingestRouter);

// TODO: Add global error-handling middleware
// app.use((err, req, res, next) => { ... });

if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`Node.js fallback service listening on port ${PORT}`);
  });
}

module.exports = app;
