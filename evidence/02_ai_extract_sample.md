# 02 — Real ai_extract output (verbatim, from the deployed app)

Structured fields returned by Databricks `ai_extract` for four documents of different
kinds. The label set is chosen per document kind; values are the model's real output
persisted to Lakebase. Retrieved via GET /api/documents/{id}/fields.

## doc 1 — bdo_benefit_spec_2024.docx  [kind=benefit_spec]  (benefit_spec (DOCX))
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

## doc 2 — bdo_bpa_data_pack_2024.pdf  [kind=bpa_data_pack]  (bpa_data_pack (PDF, ai_parse_document))
  [high  ] Scheme Name: BDO Pension Fund
  [high  ] Scheme Type: Defined Benefit - Final Salary (Closed)
  [high  ] Sponsoring Employer: BDO LLP
  [low   ] Scheme Reference: N/A
  [high  ] Benefit Accrual Rate: 1/60th of Final Pensionable Salary per year of service
  [medium] Normal Retirement Age: 65
  [high  ] Pension Increase Basis: CPI capped at 5% p.a. (RPI min 3% for pre-1997 service)
  [high  ] Revaluation Rate in Deferment: CPI capped at 2.5% p.a. in deferment
  [medium] Active Members Count: 0
  [high  ] Deferred Members Count: 755
  [high  ] Pensioner Members Count: 1,033
  [low   ] Average Age (Active): N/A
  [low   ] Average Age (Deferred): N/A
  [low   ] Average Age (Pensioner): N/A
  [low   ] Average Pensionable Salary: N/A
  [low   ] Total Pensions in Payment: N/A
  [low   ] Valuation Date: N/A
  [high  ] Technical Provisions: GBP 195.3m
  [high  ] Scheme Assets: GBP 180.1m
  [high  ] Funding Level: 91.3%
  [low   ] Buy-out Funding Level: N/A

## doc 5 — bdo_triennial_valuation_2024.pdf  [kind=triennial_valuation]  (triennial_valuation (PDF, ai_parse_document))
  [high  ] Scheme Name: BDO Pension Fund
  [high  ] Sponsoring Employer: BDO LLP
  [high  ] Scheme Year End: 31/03/2024
  [high  ] Valuation Date: 31/03/2024
  [high  ] Technical Provisions: GBP 195.3m
  [high  ] Scheme Assets: GBP 180.1m
  [high  ] Funding Level: 91.3%
  [high  ] Buy-out Funding Level: 80.2%
  [low   ] Self-Sufficiency Funding Level: N/A
  [high  ] Surplus / Deficit: GBP 15.2m
  [high  ] Discount Rate (Pre-Retirement): Gilts + 1.55% p.a.
  [high  ] Discount Rate (Post-Retirement): Gilts + 0.95% p.a.
  [high  ] CPI Inflation Assumption: 1.71% p.a.
  [high  ] RPI Inflation Assumption: 4.23% p.a.
  [high  ] Salary Growth Assumption: CPI + 1.0% p.a.
  [high  ] Mortality Base Table: S3PMA / S3PFA
  [high  ] CMI Improvement Model: CMI_2023
  [high  ] Long-Term Rate of Improvement: 1.25%

## doc 6 — bdo_funding_update_2024_12.pdf  [kind=funding_update]  (funding_update (PDF))
  [high  ] Scheme Name: BDO Pension Fund
  [low   ] Scheme Type: N/A
  [high  ] Report Date: 2024-12-28
  [low   ] Valuation Date: N/A
  [high  ] Technical Provisions: GBP 195.7m
  [high  ] Scheme Assets: GBP 179.5m
  [high  ] Funding Level: 91.1%
  [high  ] Buy-out Funding Level: 79.2%
  [low   ] Self-Sufficiency Funding Level: N/A
  [low   ] Surplus / Deficit: N/A

