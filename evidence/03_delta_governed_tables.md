# 03 — Governed Delta tables + reporting views (query results)

All queries run on warehouse ced20c73f16a2915 against serverless_stable_wx20co_catalog.bpa_rubjit.
Populated by the app's approve → sync-to-delta step (server/routes/sync.py).

## Row counts (base Delta tables)
```
tbl | rows
benefit_plans_summary | 16
benefit_plans_detail | 251
```

## Portfolio by scheme (vw_portfolio_overview)
```
customer | docs | avg_conf | total_fields | approved_fields
BDO Pension Fund | 6 | 0.71 | 87 | 87
RSM UK Pension Fund | 2 | 0.675 | 38 | 38
Renishaw plc Pension Scheme | 2 | 0.7 | 38 | 38
Spirax-Sarco Engineering Pension Plan | 2 | 0.78 | 25 | 25
Thames Water UPS (Closed Section) | 2 | 0.7 | 38 | 38
University of Reading Pension Scheme | 2 | 0.735 | 25 | 25
```

## Extraction quality — confidence bands (vw_plan_overview)
```
confidence_band | docs
Medium | 13
High | 3
```

## Category completeness (vw_category_summary)
```
category_label | docs | avg_conf
Scheme Information | 16 | 0.89
Benefits | 10 | 0.80
Funding Position | 8 | 0.76
Membership | 6 | 0.49
Exclusions | 6 | 0.30
Actuarial Assumptions | 1 | 1.00
Contributions | 1 | 0.58
```

## Field-level lineage sample (vw_field_detail, BDO benefit spec, high-confidence)
```
field_name | final_value | confidence
Scheme Name | BDO Pension Fund | high
Scheme Type | Defined Benefit - Final Salary (Closed) | high
Sponsoring Employer | BDO LLP | high
Benefit Accrual Rate | 1/60th of Final Pensionable Salary per year of service | high
Pension Increase Basis | CPI capped at 5% p.a. (RPI min 3% for pre-1997 service) | high
Revaluation Rate in Deferment | CPI capped at 2.5% p.a. in deferment | high
Commutation Factor | GBP 16 of pension commuted for GBP 256 tax-free cash | high
Early Retirement Factor | Actuarial reduction of 4% per year before NRA | high
```
