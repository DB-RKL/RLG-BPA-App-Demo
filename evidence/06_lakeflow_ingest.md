# 06 — Lakeflow incremental ingest (Auto Loader -> bronze_documents)

A **Lakeflow Declarative Pipeline** (serverless) runs Auto Loader (`cloudFiles`, binaryFile)
over the UC Volume and ingests each new scheme document exactly once into a governed bronze
Delta table. Pipeline id 8c2f4acb-be32-47c1-af7f-60efe925f1f6, notebook
lakeflow/bronze_documents_pipeline.py, target serverless_stable_wx20co_catalog.bpa_rubjit.
New documents are simulated landing in cloud storage by scripts/simulate_document_arrivals.py.

## Two runs prove INCREMENTAL pickup (not a batch re-read)
```
Run 1 (update f564592d-8779-46cd-9eec-1e4167fdbd7a): ingested the existing 72 files.
Then scripts/simulate_document_arrivals.py landed 4 new files for a new scheme (Halfords).
Run 2 (update 549154c6-7a38-4852-a7f2-4f1cb709612a): Auto Loader checkpoint skipped the 72
already-seen files and ingested ONLY the 4 new ones.
```

## Ingest batches (distinct ingest_time = distinct pipeline run)
```
ingest_batch | files
2026-09-23T09:36:37.000Z | 72
2026-09-23T09:37:46.000Z | 4
```

## bronze_documents totals
```
total_rows | schemes
76 | 7
```

## Files per scheme in bronze (7th scheme = the new arrival)
```
customer_slug | files | sample_kind
bdo | 12 | benefit_spec
halfords | 4 | benefit_spec
reading_university | 12 | benefit_spec
renishaw | 12 | benefit_spec
rsm_uk | 12 | benefit_spec
spirax_sarco | 12 | benefit_spec
thames_water | 12 | benefit_spec
```

## The newly-arrived scheme (Halfords), ingested incrementally in run 2
```
filename | document_kind | file_type | size_bytes
halfords_benefit_spec_2025.csv | benefit_spec | csv | 513
halfords_contribution_schedule_2025.csv | contribution_schedule | csv | 189
halfords_funding_update_2025_12.csv | funding_update | csv | 168
halfords_member_data_2025.xlsx | member_data | xlsx | 6068
```
