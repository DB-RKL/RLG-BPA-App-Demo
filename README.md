# BPA - Benefit Plan Administration

Databricks App that uses AI to extract structured data from insurance benefit specification PDFs/Excel files, presents a human-review UI, and exports clean data to Power BI via SQL Warehouse.

## Quick Start (Local)

### 1. Install dependencies

```bash
# Backend
cd BPA
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### 2. Set Databricks profile

```bash
export DATABRICKS_PROFILE=your-profile-name
```

### 3. Start backend

```bash
uvicorn app:app --reload --port 8000
```

### 4. Start frontend (dev)

```bash
cd frontend
npm run dev
```

Open http://localhost:5173

### 5. Generate mock PDFs (optional)

```bash
python mock_data/generate_mock_pdfs.py
```

## Deploy to Databricks Apps

```bash
databricks apps create bpa-demo -p your-profile
databricks sync . /Users/you@example.com/bpa-demo \
  --exclude node_modules --exclude .venv --exclude __pycache__ \
  --exclude .git --exclude "frontend/src" --exclude "frontend/public" \
  -p your-profile
cd frontend && npm run build && cd ..
databricks workspace import-dir frontend/dist /Users/you@example.com/bpa-demo/frontend/dist -p your-profile
databricks apps deploy bpa-demo --source-code-path /Workspace/Users/you@example.com/bpa-demo -p your-profile
```

Then add Lakebase database and Foundation Model serving endpoint as app resources in the Databricks UI.

## Power BI Integration

1. Run the SQL views in `sql/reporting_views.sql` against your SQL Warehouse
2. In Fabric: New Report > Get Data > Databricks > enter SQL Warehouse connection
3. Select `benefit_plans_summary` and `benefit_plans_detail` views
4. Use DirectQuery mode for live updates
