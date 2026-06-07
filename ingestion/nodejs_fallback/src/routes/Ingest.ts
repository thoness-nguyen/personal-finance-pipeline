// =============================================================================
// File: src/routes/Ingest.ts
// Purpose: Generic manifest-driven ingestion endpoints.
//
//   POST /ingest/all           � run the full pipeline (all enabled sources)
//   POST /ingest/:source_id    � run a single source by id
//
//   All execution logic lives in engine/Runner.ts which reads pipeline_manifest.json.
// =============================================================================

import { Router, Request, Response } from "express";
import { runPipeline } from "../engine/Runner";

const router = Router();

// POST /ingest/all
router.post("/all", async (_req: Request, res: Response) => {
  try {
    const results = await runPipeline();
    const statuses = Object.values(results).map((r) => r.status);
    const allOk    = statuses.every((s) => s === "ok");
    return res.status(allOk ? 200 : 207).json({
      status:   allOk ? "ok" : "partial",
      fallback: true,
      sources:  results,
    });
  } catch (err: any) {
    console.error("[Ingest] /all failed:", err);
    return res.status(500).json({ status: "error", message: err.message });
  }
});

// POST /ingest/:source_id
router.post("/:source_id", async (req: Request, res: Response) => {
  const source_id = req.params["source_id"] as string;
  try {
    const results = await runPipeline([source_id]);
    const result  = results[source_id];
    if (!result) {
      return res.status(404).json({ status: "error", message: `Source '${source_id}' not found or disabled.` });
    }
    return res.status(result.status === "ok" ? 200 : 500).json({
      fallback: true,
      ...result,
    });
  } catch (err: any) {
    console.error(`[Ingest] /${source_id} failed:`, err);
    return res.status(500).json({ status: "error", message: err.message });
  }
});

export default router;
