# 04 — Genie governed natural-language query

Genie space `01f1b729d86f1055b77bac0c71294adc` ("Royal London BPA — Scheme Portfolio"),
scoped to serverless_stable_wx20co_catalog.bpa_rubjit tables/views. Asked via the Conversation API;
Genie returns the SQL it ran (validate-before-trust) plus the answer.

```
QUESTION: How many schemes have approved data by customer, and what is the average confidence? Show all customers.
STATUS: COMPLETED

GENERATED SQL:
SELECT `customer`, COUNT(DISTINCT `document_id`) AS `approved_scheme_count`, AVG(`avg_confidence`) AS `average_confidence`
FROM `serverless_stable_wx20co_catalog`.`bpa_rubjit`.`vw_portfolio_overview`
WHERE `customer` IS NOT NULL
  AND `document_id` IS NOT NULL
  AND `approved_fields` > 0
GROUP BY `customer`
ORDER BY `customer` ASC

ANSWER:
All **6 customers** shown have approved data, with scheme counts ranging from **2** to **6** and average confidence from **0.675** to **0.78**. Examples include:
- **BDO Pension Fund** — **6** approved schemes, **0.71** average confidence
- **RSM UK Pension Fund** — **2** approved schemes, **0.675** average confidence
- **Renishaw plc Pension Scheme** — **2** approved schemes, **0.70** average confidence
- **Spirax-Sarco Engineering Pension Plan** — **2** approved schemes, **0.78** average confidence
- **Thames Water UPS (Closed Section)** — **2** approved schemes, **0.70** average confidence

Among the customers shown, **BDO Pension Fund** has the most approved schemes, while **Spirax-Sarco Engineering Pension Plan** has the highest average confidence.

RESULT ROWS:
customer | approved_scheme_count | average_confidence
BDO Pension Fund | 6 | 0.71
RSM UK Pension Fund | 2 | 0.675
Renishaw plc Pension Scheme | 2 | 0.7
Spirax-Sarco Engineering Pension Plan | 2 | 0.78
Thames Water UPS (Closed Section) | 2 | 0.7
University of Reading Pension Scheme | 2 | 0.735
```
