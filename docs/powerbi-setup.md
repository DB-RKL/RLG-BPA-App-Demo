# Power BI Connection Guide -- BPA Benefit Plans

## Prerequisites

- Power BI Desktop (latest version)
- Databricks SQL ODBC driver or the built-in Databricks connector in Power BI
- A Databricks Personal Access Token (PAT) or OAuth credentials

## Connection Details

| Parameter       | Value                                                    |
|-----------------|----------------------------------------------------------|
| Server Hostname | `e2-demo-field-eng.cloud.databricks.com`                 |
| HTTP Path       | `/sql/1.0/warehouses/e9b34f7a2e4b0561`                  |
| Port            | `443`                                                    |
| Catalog         | `main`                                                   |
| Schema          | `bpa_rubjit`                                             |

## Step-by-step Setup

### 1. Open Power BI Desktop

Go to **Home > Get Data > More...** and search for **"Azure Databricks"** (or just **"Databricks"**).

### 2. Enter connection details

- **Server Hostname**: `e2-demo-field-eng.cloud.databricks.com`
- **HTTP Path**: `/sql/1.0/warehouses/e9b34f7a2e4b0561`

Click **OK**.

### 3. Authenticate

Choose **Personal Access Token** and paste your Databricks PAT.

To generate a PAT:
1. In the Databricks workspace, click your username (top right) > **Settings**
2. Go to **Developer** > **Access Tokens** > **Generate New Token**
3. Copy the token and paste it into Power BI

### 4. Select tables/views

Navigate to **main > bpa_rubjit** and select these views:

| View                       | Purpose                                      |
|----------------------------|----------------------------------------------|
| `vw_plan_overview`         | Summary row per document with key fields      |
| `vw_field_detail`          | Every extracted field with confidence scores  |
| `vw_extraction_quality`    | Quality metrics per document                  |
| `vw_category_summary`      | Completeness per category per document        |

Select all four and click **Load** (Import mode) or **Transform Data** if you want to preview first.

### 5. Data Connectivity Mode

Select **DirectQuery** when prompted. This ensures the dashboard always shows live data from the Delta tables without manual refreshes.

Note: The SQL Warehouse must be running for DirectQuery to work. It auto-starts on first query but has a ~30 second cold start. Set a longer Auto Stop timeout in the Databricks warehouse settings to keep it warm during demos.

### 6. Publishing to Power BI Service (optional)

After publishing:
1. Go to your dataset settings in Power BI Service
2. Under **Gateway and cloud connections**, bind to your Databricks connection
3. DirectQuery datasets do not need scheduled refresh -- they query live on every interaction

## Data Model Relationships

After loading, set up these relationships in Power BI Model view:

```
vw_plan_overview.document_id  -->  vw_field_detail.document_id      (1:many)
vw_plan_overview.document_id  -->  vw_extraction_quality.document_id (1:1)
vw_plan_overview.document_id  -->  vw_category_summary.document_id  (1:many)
```

All relationships should be **single direction** (one-to-many from plan_overview to the others).

## Troubleshooting

| Issue                      | Fix                                                       |
|----------------------------|-----------------------------------------------------------|
| "Warehouse not found"      | Ensure the SQL warehouse is running (auto-starts on query)|
| "Authentication failed"    | Regenerate PAT; check it hasn't expired                   |
| Empty tables               | Approve documents in the BPA app and sync to Delta first  |
| Slow queries               | Use Import mode instead of DirectQuery                    |
