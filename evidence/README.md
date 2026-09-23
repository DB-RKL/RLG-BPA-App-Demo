# Execution Evidence — Royal London BPA on Databricks (wx20co)

This directory contains **committed text evidence that the build actually ran** end-to-end
in the `fevm-serverless-stable-wx20co` workspace on 2026-09-23. Every file is plain text
(query results, run logs, real model output) — no screenshots.

## The customer problem (specific, one industry)

**UK life insurer, Bulk Purchase Annuity (BPA) pricing.** When a defined-benefit pension
scheme moves to an insurer, actuaries must transcribe ~40 structured fields per scheme
(benefit bases, revaluation rules, commutation factors, funding position…) out of PDFs,
Excel, Word and CSV packs into a master workbook before they can price. That re-keying is
the bottleneck that caps how many schemes the team can quote inside tight exclusivity
windows. This build turns *raw scheme document → priced-scheme-ready structured data in
minutes, with full lineage*.

## The end-to-end journey (all six stages, integrated)

| Stage | Databricks primitive | Where it is in this repo / workspace | Evidence |
|-------|---------------------|--------------------------------------|----------|
| **Ingest (Lakeflow-style)** | Unity Catalog **Volume** — governed file landing | `/Volumes/serverless_stable_wx20co_catalog/bpa_rubjit/documents/<customer>/` (72 files, 6 schemes) | `01_ingest_extract_run.md` |
| **Govern** | **Unity Catalog** — schema, volume, Delta tables, views, grants | `serverless_stable_wx20co_catalog.bpa_rubjit` | `03_delta_governed_tables.md`, `05_deploy_and_resources.md` |
| **Serve (operational)** | **Lakebase** Postgres — live document/field state | instance `rlg-lakebase`, tables `documents` + `extracted_fields` | `01_ingest_extract_run.md`, `05_deploy_and_resources.md` |
| **Intelligent (GenAI)** | **`ai_parse_document`** + **`ai_extract`** on a serverless SQL warehouse | `server/routes/ai_sql.py` | `02_ai_extract_sample.md` |
| **Queryable (NL)** | **Genie** — governed text-to-SQL | space `01f1b729d86f1055b77bac0c71294adc` | `04_genie_nl_query.md` |
| **Surface to business** | **Databricks App** (FastAPI + React) + **AI/BI Lakeview dashboard** | app `rlg-demo`, dashboard `01f1b72a2a1d100fb06e1284b208e373` | `05_deploy_and_resources.md` |

## Live endpoints (wx20co)

- **App:** https://rlg-demo-7474653316213627.aws.databricksapps.com (state RUNNING)
- **Lakeview dashboard:** `/embed/dashboardsv3/01f1b72a2a1d100fb06e1284b208e373`
- **Genie space:** `/embed/genie/rooms/01f1b729d86f1055b77bac0c71294adc`

## What ran (summary)

- 72 documents uploaded to the UC Volume across 6 pension-scheme prospects.
- 16 documents ingested through the deployed app (`ai_parse_document` on PDFs, native parsers
  on DOCX/XLSX/CSV), `ai_extract` producing 251 structured fields, then reviewed & approved.
- Approval synced 16 summary rows + 251 detail rows into governed Delta tables.
- 5 reporting views + a published Lakeview dashboard + a Genie space over the same tables.
- Genie answered a natural-language portfolio question with governed SQL (verbatim in `04_…`).

Reproduce: retarget `app.yaml` env, run the SQL DDL in `sql/`, upload the corpus to the
volume, deploy the app to `rlg-demo`, then drive the workflow (upload → extract → approve).
