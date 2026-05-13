-- Power BI Reporting Views for BPA
-- Target: main.bpa_rubjit on Databricks SQL Warehouse e9b34f7a2e4b0561
-- Run each statement separately against the warehouse.

-- ============================================================
-- VIEW 1: vw_plan_overview
-- One row per approved document with clean column aliases,
-- computed flags, and human-readable labels.
-- ============================================================
CREATE OR REPLACE VIEW main.bpa_rubjit.vw_plan_overview AS
SELECT
  document_id,
  filename,
  file_type,
  status,
  upload_time,
  DATEDIFF(CURRENT_DATE(), CAST(upload_time AS DATE))  AS days_since_upload,
  scheme_name,
  scheme_type,
  underwriter,
  effective_date,
  employer_contribution,
  employee_contribution,
  benefit_level,
  max_benefit_cap,
  deferred_period,
  free_cover_limit,
  total_fields,
  approved_fields,
  ROUND(avg_confidence, 2)                              AS avg_confidence,
  CASE
    WHEN approved_fields = total_fields THEN TRUE
    ELSE FALSE
  END                                                    AS is_fully_reviewed,
  CASE
    WHEN avg_confidence >= 0.8 THEN 'High'
    WHEN avg_confidence >= 0.5 THEN 'Medium'
    ELSE 'Low'
  END                                                    AS confidence_band
FROM main.bpa_rubjit.benefit_plans_summary;


-- ============================================================
-- VIEW 2: vw_field_detail
-- One row per extracted field with a numeric confidence score,
-- human-readable category labels, and change detection.
-- ============================================================
CREATE OR REPLACE VIEW main.bpa_rubjit.vw_field_detail AS
SELECT
  document_id,
  filename,
  document_status,
  field_name,
  field_category,
  CASE field_category
    WHEN 'scheme_info'     THEN 'Scheme Information'
    WHEN 'benefits'        THEN 'Benefits'
    WHEN 'contributions'   THEN 'Contributions'
    WHEN 'premium_rates'   THEN 'Premium Rates'
    WHEN 'investment'      THEN 'Investment'
    WHEN 'rehabilitation'  THEN 'Rehabilitation'
    WHEN 'exclusions'      THEN 'Exclusions'
    ELSE INITCAP(REPLACE(field_category, '_', ' '))
  END                                                    AS category_label,
  extracted_value,
  reviewed_value,
  final_value,
  confidence,
  CASE confidence
    WHEN 'high'   THEN 1.0
    WHEN 'medium' THEN 0.6
    WHEN 'low'    THEN 0.3
    ELSE 0.5
  END                                                    AS confidence_score,
  is_approved,
  CASE
    WHEN reviewed_value IS NOT NULL
     AND extracted_value IS NOT NULL
     AND reviewed_value <> extracted_value THEN TRUE
    ELSE FALSE
  END                                                    AS was_changed_in_review
FROM main.bpa_rubjit.benefit_plans_detail;


-- ============================================================
-- VIEW 3: vw_extraction_quality
-- Aggregated quality metrics per document: confidence
-- distribution, approval rate, and change rate.
-- ============================================================
CREATE OR REPLACE VIEW main.bpa_rubjit.vw_extraction_quality AS
SELECT
  d.document_id,
  d.filename,
  d.upload_time,
  d.scheme_name,
  d.total_fields,
  d.approved_fields,
  ROUND(d.approved_fields * 100.0 / NULLIF(d.total_fields, 0), 1) AS pct_approved,
  d.avg_confidence,
  COUNT(CASE WHEN f.confidence = 'high'   THEN 1 END)             AS high_confidence_count,
  COUNT(CASE WHEN f.confidence = 'medium' THEN 1 END)             AS medium_confidence_count,
  COUNT(CASE WHEN f.confidence = 'low'    THEN 1 END)             AS low_confidence_count,
  COUNT(CASE
    WHEN f.reviewed_value IS NOT NULL
     AND f.extracted_value IS NOT NULL
     AND f.reviewed_value <> f.extracted_value THEN 1
  END)                                                              AS fields_changed,
  ROUND(
    COUNT(CASE
      WHEN f.reviewed_value IS NOT NULL
       AND f.extracted_value IS NOT NULL
       AND f.reviewed_value <> f.extracted_value THEN 1
    END) * 100.0 / NULLIF(d.total_fields, 0), 1
  )                                                                 AS pct_changed,
  ROUND(
    (d.total_fields - COUNT(CASE
      WHEN f.reviewed_value IS NOT NULL
       AND f.extracted_value IS NOT NULL
       AND f.reviewed_value <> f.extracted_value THEN 1
    END)) * 100.0 / NULLIF(d.total_fields, 0), 1
  )                                                                 AS extraction_accuracy
FROM main.bpa_rubjit.benefit_plans_summary d
LEFT JOIN main.bpa_rubjit.benefit_plans_detail f
  ON d.document_id = f.document_id
GROUP BY
  d.document_id, d.filename, d.upload_time, d.scheme_name,
  d.total_fields, d.approved_fields, d.avg_confidence;


-- ============================================================
-- VIEW 4: vw_category_summary
-- Completeness per document per category: how many fields
-- were extracted vs how many are expected.
-- ============================================================
CREATE OR REPLACE VIEW main.bpa_rubjit.vw_category_summary AS
WITH expected_counts AS (
  SELECT 'scheme_info'    AS field_category, 8  AS expected_fields UNION ALL
  SELECT 'benefits',                          8  UNION ALL
  SELECT 'contributions',                     7  UNION ALL
  SELECT 'premium_rates',                     6  UNION ALL
  SELECT 'investment',                        5  UNION ALL
  SELECT 'rehabilitation',                    4  UNION ALL
  SELECT 'exclusions',                        5
),
actual AS (
  SELECT
    document_id,
    filename,
    field_category,
    COUNT(*)                                                         AS extracted_fields,
    COUNT(CASE WHEN final_value IS NOT NULL AND final_value <> '' THEN 1 END) AS populated_fields,
    COUNT(CASE WHEN is_approved THEN 1 END)                          AS approved_fields,
    ROUND(AVG(CASE confidence
      WHEN 'high'   THEN 1.0
      WHEN 'medium' THEN 0.6
      WHEN 'low'    THEN 0.3
      ELSE 0.5
    END), 2)                                                         AS avg_category_confidence
  FROM main.bpa_rubjit.benefit_plans_detail
  GROUP BY document_id, filename, field_category
)
SELECT
  a.document_id,
  a.filename,
  a.field_category,
  CASE a.field_category
    WHEN 'scheme_info'     THEN 'Scheme Information'
    WHEN 'benefits'        THEN 'Benefits'
    WHEN 'contributions'   THEN 'Contributions'
    WHEN 'premium_rates'   THEN 'Premium Rates'
    WHEN 'investment'      THEN 'Investment'
    WHEN 'rehabilitation'  THEN 'Rehabilitation'
    WHEN 'exclusions'      THEN 'Exclusions'
    ELSE INITCAP(REPLACE(a.field_category, '_', ' '))
  END                                                                AS category_label,
  e.expected_fields,
  a.extracted_fields,
  a.populated_fields,
  a.approved_fields,
  ROUND(a.populated_fields * 100.0 / NULLIF(e.expected_fields, 0), 1) AS pct_complete,
  a.avg_category_confidence
FROM actual a
LEFT JOIN expected_counts e ON a.field_category = e.field_category;
