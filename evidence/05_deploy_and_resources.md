# 05 — Deployment, resources & governance grants (wx20co)

## Databricks App (rlg-demo)
```
url: https://rlg-demo-7474653316213627.aws.databricksapps.com
app_status: RUNNING - App has status: App is running
compute_status: ACTIVE
active_deployment: 01f1b72a35401a94ba5c2353c2f4b146 SUCCEEDED
service_principal: app-1apl7h rlg-demo cd483109-5c63-4831-a729-4fe43870f8a0
resources:
  {"database": {"database_name": "databricks_postgres", "instance_name": "rlg-lakebase", "permission": "CAN_CONNECT_AND_CREATE"}, "name": "database"}
  {"name": "serving-endpoint", "serving_endpoint": {"name": "databricks-claude-sonnet-4-5", "permission": "CAN_QUERY"}}
```

## Unity Catalog objects (serverless_stable_wx20co_catalog.bpa_rubjit)
```
database | tableName | isTemporary
bpa_rubjit | benefit_plans_detail | false
bpa_rubjit | benefit_plans_summary | false
bpa_rubjit | vw_category_summary | false
bpa_rubjit | vw_extraction_quality | false
bpa_rubjit | vw_field_detail | false
bpa_rubjit | vw_plan_overview | false
bpa_rubjit | vw_portfolio_overview | false
--- volumes ---
database | volume_name
bpa_rubjit | documents
--- views ---
namespace | viewName | isTemporary | isMaterialized | isMetric
bpa_rubjit | vw_category_summary | false | false | false
bpa_rubjit | vw_extraction_quality | false | false | false
bpa_rubjit | vw_field_detail | false | false | false
bpa_rubjit | vw_plan_overview | false | false | false
bpa_rubjit | vw_portfolio_overview | false | false | false
```

## App SP grants on the schema
```
Principal | ActionType | ObjectType | ObjectKey
cd483109-5c63-4831-a729-4fe43870f8a0 | MODIFY | SCHEMA | serverless_stable_wx20co_catalog.bpa_rubjit
cd483109-5c63-4831-a729-4fe43870f8a0 | EXECUTE | SCHEMA | serverless_stable_wx20co_catalog.bpa_rubjit
cd483109-5c63-4831-a729-4fe43870f8a0 | READ VOLUME | SCHEMA | serverless_stable_wx20co_catalog.bpa_rubjit
cd483109-5c63-4831-a729-4fe43870f8a0 | SELECT | SCHEMA | serverless_stable_wx20co_catalog.bpa_rubjit
cd483109-5c63-4831-a729-4fe43870f8a0 | USE SCHEMA | SCHEMA | serverless_stable_wx20co_catalog.bpa_rubjit
account users | ALL PRIVILEGES | CATALOG | serverless_stable_wx20co_catalog
```

## Provisioned resources
- Lakebase instance: rlg-lakebase (PG16), database databricks_postgres, tables public.documents + public.extracted_fields
- Serving endpoint: databricks-claude-sonnet-4-5 (backs ai_extract / ai_parse_document via the warehouse)
- SQL warehouse: ced20c73f16a2915 (Serverless Starter)
- Lakeview dashboard: 01f1b72a2a1d100fb06e1284b208e373 ("BPA Portfolio Insights", published)
- Genie space: 01f1b729d86f1055b77bac0c71294adc ("Royal London BPA — Scheme Portfolio")
- UC Volume corpus: 72 files across 6 schemes under /Volumes/serverless_stable_wx20co_catalog/bpa_rubjit/documents/
