-- SQL Warehouse reporting views for Power BI integration.
-- Run these against the SQL Warehouse once the Lakebase tables are populated.
-- Adjust the catalog/schema path to match your Lakebase database.

-- View 1: One row per document with key summary metrics
CREATE OR REPLACE VIEW benefit_plans_summary AS
SELECT
    d.id AS document_id,
    d.filename,
    d.file_type,
    d.status,
    d.upload_time,
    MAX(CASE WHEN ef.field_name = 'Plan Name' THEN COALESCE(ef.reviewed_value, ef.extracted_value) END) AS plan_name,
    MAX(CASE WHEN ef.field_name = 'Plan Type' THEN COALESCE(ef.reviewed_value, ef.extracted_value) END) AS plan_type,
    MAX(CASE WHEN ef.field_name = 'Carrier / Insurer' THEN COALESCE(ef.reviewed_value, ef.extracted_value) END) AS carrier,
    MAX(CASE WHEN ef.field_name = 'Effective Date' THEN COALESCE(ef.reviewed_value, ef.extracted_value) END) AS effective_date,
    MAX(CASE WHEN ef.field_name = 'Premium - Employee Only' THEN COALESCE(ef.reviewed_value, ef.extracted_value) END) AS premium_employee,
    MAX(CASE WHEN ef.field_name = 'Premium - Family' THEN COALESCE(ef.reviewed_value, ef.extracted_value) END) AS premium_family,
    MAX(CASE WHEN ef.field_name = 'Deductible - Individual In-Network' THEN COALESCE(ef.reviewed_value, ef.extracted_value) END) AS deductible_individual,
    MAX(CASE WHEN ef.field_name = 'Deductible - Family In-Network' THEN COALESCE(ef.reviewed_value, ef.extracted_value) END) AS deductible_family,
    MAX(CASE WHEN ef.field_name = 'OOP Max - Individual In-Network' THEN COALESCE(ef.reviewed_value, ef.extracted_value) END) AS oop_max_individual,
    MAX(CASE WHEN ef.field_name = 'OOP Max - Family In-Network' THEN COALESCE(ef.reviewed_value, ef.extracted_value) END) AS oop_max_family,
    COUNT(ef.id) AS total_fields,
    COUNT(ef.id) FILTER (WHERE ef.is_approved = TRUE) AS approved_fields,
    ROUND(AVG(CASE
        WHEN ef.confidence = 'high' THEN 1.0
        WHEN ef.confidence = 'medium' THEN 0.6
        ELSE 0.3
    END), 2) AS avg_confidence
FROM documents d
LEFT JOIN extracted_fields ef ON ef.document_id = d.id
GROUP BY d.id, d.filename, d.file_type, d.status, d.upload_time;


-- View 2: One row per extracted field with the final reviewed/extracted value
CREATE OR REPLACE VIEW benefit_plans_detail AS
SELECT
    d.id AS document_id,
    d.filename,
    d.status AS document_status,
    ef.id AS field_id,
    ef.field_name,
    ef.field_category,
    ef.extracted_value,
    ef.reviewed_value,
    COALESCE(ef.reviewed_value, ef.extracted_value) AS final_value,
    ef.confidence,
    ef.is_approved
FROM documents d
JOIN extracted_fields ef ON ef.document_id = d.id
ORDER BY d.id, ef.id;
