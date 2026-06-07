// =============================================================================
// File: src/App.ts
// Purpose: Entry point for the Express fallback ingestion service.
//          Configures middleware, mounts routes, and starts the HTTP server.
//          Used when the Python FastAPI service is unavailable.
// =============================================================================

import * as path from "path";
import dotenv from "dotenv";
dotenv.config({ path: path.resolve(__dirname, "../../../.env") });

import express, { Request, Response, NextFunction } from "express";
import cors from "cors";
import ingestRouter from "./routes/Ingest";

const app = express();
const PORT = process.env.NODE_API_PORT || 3000;

app.use(cors());
app.use(express.json());

// Health check
app.get("/health", (_req: Request, res: Response) => {
  res.json({ status: "ok", service: "nodejs-fallback" });
});

// Routes
app.use("/api/v1/ingest", ingestRouter);

// Global error handler
app.use((err: Error, _req: Request, res: Response, _next: NextFunction) => {
  console.error(err.stack);
  res.status(500).json({ error: err.message });
});

if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`Node.js fallback service listening on port ${PORT}`);
  });
}

export default app;
