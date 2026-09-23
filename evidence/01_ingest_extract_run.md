# 01 — Ingest + AI extraction run log

Driven over HTTP against the deployed app https://rlg-demo-7474653316213627.aws.databricksapps.com on 2026-09-23.
Each PDF ingest calls ai_parse_document on the SQL warehouse; DOCX/XLSX/CSV use native parsers.
Each extract calls ai_extract (Databricks SQL AI function). Field counts differ per document kind,
proving per-document-kind schema routing (server/extraction_schemas.py).

```
[ingest] id=1 bdo/bdo_benefit_spec_2024.docx kind=None (1s, 1457 chars)
[ingest] id=2 bdo/bdo_bpa_data_pack_2024.pdf kind=None (18s, 18414 chars)
[ingest] id=3 bdo/bdo_contribution_schedule_2024.csv kind=None (1s, 520 chars)
[ingest] id=4 bdo/bdo_member_data_2024.xlsx kind=None (2s, 611 chars)
[ingest] id=5 bdo/bdo_triennial_valuation_2024.pdf kind=None (9s, 22757 chars)
[ingest] id=6 bdo/bdo_funding_update_2024_12.pdf kind=None (6s, 3232 chars)
[ingest] id=7 renishaw/renishaw_benefit_spec_2024.docx kind=None (1s, 1527 chars)
[ingest] id=8 renishaw/renishaw_bpa_data_pack_2024.pdf kind=None (9s, 19311 chars)
[ingest] id=9 reading_university/reading_university_benefit_spec_2024.docx kind=None (1s, 1515 chars)
[ingest] id=10 reading_university/reading_university_summary_funding_2024.pdf kind=None (7s, 3972 chars)
[ingest] id=11 thames_water/thames_water_benefit_spec_2024.docx kind=None (1s, 1569 chars)
[ingest] id=12 thames_water/thames_water_bpa_data_pack_2024.pdf kind=None (7s, 19162 chars)
[ingest] id=13 spirax_sarco/spirax_sarco_benefit_spec_2024.docx kind=None (1s, 1521 chars)
[ingest] id=14 spirax_sarco/spirax_sarco_summary_funding_2024.pdf kind=None (7s, 3963 chars)
[ingest] id=15 rsm_uk/rsm_uk_benefit_spec_2024.docx kind=None (1s, 1452 chars)
[ingest] id=16 rsm_uk/rsm_uk_bpa_data_pack_2024.pdf kind=None (7s, 17956 chars)

=== ingested 16 docs; running ai_extract ===
[extract] id=1 bdo_benefit_spec_2024.docx kind=None -> 17 fields, 8 high-conf (10s)
[extract] id=2 bdo_bpa_data_pack_2024.pdf kind=None -> 21 fields, 11 high-conf (7s)
[extract] id=3 bdo_contribution_schedule_2024.csv kind=None -> 11 fields, 5 high-conf (3s)
[extract] id=4 bdo_member_data_2024.xlsx kind=None -> 10 fields, 4 high-conf (5s)
[extract] id=5 bdo_triennial_valuation_2024.pdf kind=None -> 18 fields, 17 high-conf (7s)
[extract] id=6 bdo_funding_update_2024_12.pdf kind=None -> 10 fields, 6 high-conf (15s)
[extract] id=7 renishaw_benefit_spec_2024.docx kind=None -> 17 fields, 9 high-conf (13s)
[extract] id=8 renishaw_bpa_data_pack_2024.pdf kind=None -> 21 fields, 12 high-conf (31s)
[extract] id=9 reading_university_benefit_spec_2024.docx kind=None -> 17 fields, 8 high-conf (15s)
[extract] id=10 reading_university_summary_funding_2024.pdf kind=None -> 8 fields, 6 high-conf (7s)
[extract] id=11 thames_water_benefit_spec_2024.docx kind=None -> 17 fields, 8 high-conf (8s)
[extract] id=12 thames_water_bpa_data_pack_2024.pdf kind=None -> 21 fields, 13 high-conf (9s)
[extract] id=13 spirax_sarco_benefit_spec_2024.docx kind=None -> 17 fields, 8 high-conf (7s)
[extract] id=14 spirax_sarco_summary_funding_2024.pdf kind=None -> 8 fields, 7 high-conf (6s)
[extract] id=15 rsm_uk_benefit_spec_2024.docx kind=None -> 17 fields, 8 high-conf (6s)
[extract] id=16 rsm_uk_bpa_data_pack_2024.pdf kind=None -> 21 fields, 11 high-conf (8s)

=== approving all docs (triggers sync-to-delta) ===
bulk-approve: 200 {'status': 'ok', 'approved': 16, 'document_ids': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]}

=== SAMPLE ai_extract output: doc 1 (bdo_benefit_spec_2024.docx) ===
  [high  ] Scheme Name: BDO Pension Fund
  [high  ] Scheme Type: Defined Benefit - Final Salary (Closed)
  [high  ] Sponsoring Employer: BDO LLP
  [low   ] Effective Date: N/A
  [high  ] Benefit Accrual Rate: 1/60th of Final Pensionable Salary per year of service
  [low   ] Salary Definition: N/A
  [medium] Normal Retirement Age: 65
  [low   ] Dependants Pension: N/A
  [high  ] Pension Increase Basis: CPI capped at 5% p.a. (RPI min 3% for pre-1997 service)
  [high  ] Revaluation Rate in Deferment: CPI capped at 2.5% p.a. in deferment
  [high  ] Commutation Factor: GBP 16 of pension commuted for GBP 256 tax-free cash
  [high  ] Early Retirement Factor: Actuarial reduction of 4% per year before NRA
  [low   ] Late Retirement Factor: N/A
  [low   ] Trust Deed Reference: N/A
  [low   ] Amending Deed Date: N/A
  [low   ] Barber Equalisation Date: N/A
  [low   ] Benefit Caveats / Discretions: N/A

INGESTED_IDS=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
```
