-- AI/BI Reporting Dashboard support view
-- Target: main.bpa_rubjit on Databricks SQL Warehouse e9b34f7a2e4b0561
--
-- vw_portfolio_overview joins vw_plan_overview + vw_extraction_quality and
-- derives `customer` from filename prefix so every dashboard widget shares
-- the same customer mapping.

CREATE OR REPLACE VIEW main.bpa_rubjit.vw_portfolio_overview AS
SELECT
  p.document_id,
  p.filename,
  p.file_type,
  p.status,
  p.upload_time,
  CAST(p.upload_time AS DATE)                 AS upload_date,
  DATE_TRUNC('WEEK', p.upload_time)           AS upload_week,
  DATE_TRUNC('MONTH', p.upload_time)          AS upload_month,
  p.days_since_upload,
  p.scheme_name,
  p.scheme_type,
  p.underwriter,
  p.effective_date,
  p.total_fields,
  p.approved_fields,
  p.avg_confidence,
  p.is_fully_reviewed,
  p.confidence_band,
  COALESCE(q.pct_approved, 0)                 AS pct_approved,
  COALESCE(q.high_confidence_count, 0)        AS high_confidence_count,
  COALESCE(q.medium_confidence_count, 0)      AS medium_confidence_count,
  COALESCE(q.low_confidence_count, 0)         AS low_confidence_count,
  COALESCE(q.fields_changed, 0)               AS fields_changed,
  COALESCE(q.pct_changed, 0)                  AS pct_changed,
  COALESCE(q.extraction_accuracy, 100)        AS extraction_accuracy,
  CASE
    WHEN p.filename ILIKE 'bdo%'                THEN 'BDO Pension Fund'
    WHEN p.filename ILIKE 'renishaw%'           THEN 'Renishaw plc Pension Scheme'
    WHEN p.filename ILIKE 'reading_university%' THEN 'University of Reading Pension Scheme'
    WHEN p.filename ILIKE 'thames_water%'       THEN 'Thames Water UPS (Closed Section)'
    WHEN p.filename ILIKE 'spirax_sarco%'       THEN 'Spirax-Sarco Engineering Pension Plan'
    WHEN p.filename ILIKE 'rsm_uk%'             THEN 'RSM UK Pension Fund'
    ELSE 'Other'
  END                                          AS customer,
  CASE
    WHEN p.filename ILIKE 'bdo%'                THEN 'bdo'
    WHEN p.filename ILIKE 'renishaw%'           THEN 'renishaw'
    WHEN p.filename ILIKE 'reading_university%' THEN 'reading_university'
    WHEN p.filename ILIKE 'thames_water%'       THEN 'thames_water'
    WHEN p.filename ILIKE 'spirax_sarco%'       THEN 'spirax_sarco'
    WHEN p.filename ILIKE 'rsm_uk%'             THEN 'rsm_uk'
    ELSE 'other'
  END                                          AS customer_slug
FROM main.bpa_rubjit.vw_plan_overview p
LEFT JOIN main.bpa_rubjit.vw_extraction_quality q
  ON p.document_id = q.document_id;
