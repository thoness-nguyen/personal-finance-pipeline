// =============================================================================
// File: engine/Runner.ts
// Purpose: Generic EtLT engine — mirrors Python's engine/runner.py.
//   Reads pipeline_manifest.json, resolves dependency order, and executes
//   the Extract → stage-raw → Transform → stage-processed → Load flow
//   for each enabled source.
//
//   Each source entry in the manifest declares:
//     sheet_id / sheet_name  – where to extract data from
//     raw_blob               – GCS path for the raw staged CSV
//     processed_blob         – GCS path for the cleaned CSV (null if no cleaner)
//     cleaner.enabled        – whether to run a transform step
//     cleaner.path           – dotted module path, e.g. "EtLT.transform.expenses"
//                              module must export:  clean(rows) -> rows
//     loader.enabled         – whether to load into MySQL
//     loader.path            – dotted module path, e.g. "EtLT.load.transactions"
//                              module must export:  load() -> Promise<number>
//     depends_on             – list of source ids that must run first
// =============================================================================

import * as fs from "fs";
import * as path from "path";
import Papa from "papaparse";

import { appendCsvToGCS, downloadCsvFromGCS, uploadCsvToGCS } from "../EtLT/staging/GcsService";
import { fetchSheetData, parseOjectFromSheet, parseCsvFromObject } from "../EtLT/extract/SpreadsheetService";

const MANIFEST_PATH = process.env["MANIFEST_PATH"] ??
  path.resolve(__dirname, "../../../pipeline_manifest.json");

// ─── Types ────────────────────────────────────────────────────────────────────

interface CleanerConfig { enabled: boolean; path: string | null; }
interface LoaderConfig  { enabled: boolean; path: string; }

interface Source {
  id:             string;
  enabled:        boolean;
  sheet_id:       string;
  sheet_name:     string;
  raw_blob:       string;
  processed_blob: string | null;
  cleaner:        CleanerConfig;
  loader:         LoaderConfig;
  depends_on:     string[];
}

export interface SourceResult {
  status:         "ok" | "error";
  rows_in_sheet?: number;
  gcs_raw?:       string;
  gcs_processed?: string;
  rows_loaded?:   number;
  error?:         string;
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

/** Load a module by dotted path (e.g. "EtLT.load.plans" → src/EtLT/load/plans). */
function importModule(dottedPath: string): any {
  const parts = dottedPath.split(".");
  const absolutePath = path.resolve(__dirname, "..", ...parts);
  return require(absolutePath);
}

/** Topological sort — ensures every dependency runs before its dependant. */
function topologicalOrder(sources: Source[]): Source[] {
  const sourceMap = new Map<string, Source>(sources.map((s) => [s.id, s]));
  const result:   Source[] = [];
  const visited   = new Set<string>();
  const visiting  = new Set<string>();

  function visit(id: string): void {
    if (visited.has(id)) return;
    if (visiting.has(id)) throw new Error(`[Runner] Circular dependency at '${id}'`);
    visiting.add(id);
    for (const dep of sourceMap.get(id)?.depends_on ?? []) visit(dep);
    visiting.delete(id);
    visited.add(id);
    if (sourceMap.has(id)) result.push(sourceMap.get(id)!);
  }

  for (const s of sources) visit(s.id);
  return result;
}

// ─── Single-source executor ───────────────────────────────────────────────────

export async function runSource(source: Source): Promise<SourceResult> {
  const sid       = source.id;
  const sheetId   = source.sheet_id
  const sheetName = source.sheet_name;

  // E — Extract
  console.log(`[Runner:${sid}] E — extracting from sheet '${sheetName}'`);
  const rawData = await fetchSheetData(sheetId, sheetName);
  const records = parseOjectFromSheet(rawData);
  if (!records.length) throw new Error(`Sheet '${sheetName}' returned no data.`);

  // t — Stage raw (append + deduplicate)
  const rawBlob = source.raw_blob;
  console.log(`[Runner:${sid}] t — staging raw → ${rawBlob}`);
  const rawCsv = await parseCsvFromObject(records);
  await appendCsvToGCS(rawCsv, rawBlob);
  const gcsRaw = `gs://${process.env.GCS_BUCKET_NAME}/${rawBlob}`;

  let gcsProcessed: string | undefined;

  // T — Transform (cleaner, if enabled)
  if (source.cleaner?.enabled && source.cleaner.path) {
    const cleanerPath = source.cleaner.path;
    console.log(`[Runner:${sid}] T — cleaning with '${cleanerPath}'`);
    const rawBuffer = await downloadCsvFromGCS(rawBlob);
    const rawRows   = Papa.parse<Record<string, any>>(rawBuffer.toString(), {
      header:         true,
      skipEmptyLines: true,
    }).data;

    const cleaner    = importModule(cleanerPath);
    const cleanedRows: Record<string, any>[] = cleaner.clean(rawRows);
    if (!cleanedRows?.length) {
      throw new Error(`Cleaner '${cleanerPath}' produced no rows for source '${sid}'.`);
    }

    const processedBlob = source.processed_blob!;
    console.log(`[Runner:${sid}] T — staging processed → ${processedBlob}`);
    await uploadCsvToGCS(Papa.unparse(cleanedRows), processedBlob);
    gcsProcessed = `gs://${process.env.GCS_BUCKET_NAME}/${processedBlob}`;
  } 
  else if (source.processed_blob) {
    await uploadCsvToGCS(rawCsv, source.processed_blob);
    gcsProcessed = `gs://${process.env.GCS_BUCKET_NAME}/${source.processed_blob}`;
  }

  // L — Load to MySQL
  let rowsLoaded = 0;
  if (source.loader?.enabled && source.loader.path) {
    const loaderPath = source.loader.path;
    console.log(`[Runner:${sid}] L — loading with '${loaderPath}'`);
    const loader = importModule(loaderPath);
    rowsLoaded   = await loader.load();
  }

  const result: SourceResult = {
    status:        "ok",
    rows_in_sheet: records.length,
    gcs_raw:       gcsRaw,
    rows_loaded:   rowsLoaded,
  };
  if (gcsProcessed) result.gcs_processed = gcsProcessed;

  console.log(`[Runner:${sid}] done — rows_loaded=${rowsLoaded}`);
  return result;
}

// ─── Pipeline entry point ─────────────────────────────────────────────────────

export async function runPipeline(
  sourceIds?: string[]
): Promise<Record<string, SourceResult>> {
  const manifest = JSON.parse(fs.readFileSync(MANIFEST_PATH, "utf-8"));

  let sources: Source[] = manifest.sources.filter((s: Source) => s.enabled !== false);
  if (sourceIds?.length) {
    sources = sources.filter((s) => sourceIds.includes(s.id));
  }

  const ordered = topologicalOrder(sources);
  const results: Record<string, SourceResult> = {};

  for (const source of ordered) {
    try {
      results[source.id] = await runSource(source);
    } catch (err: any) {
      results[source.id] = { status: "error", error: err.message };
      console.error(`[Runner:${source.id}] ERROR — ${err.message}`);
    }
  }

  return results;
}
