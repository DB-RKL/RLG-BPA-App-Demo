"""Sync approved data from Lakebase to Delta tables for Power BI."""

import json
import os

import aiohttp
from fastapi import APIRouter, HTTPException

from ..config import get_workspace_host, get_oauth_token
from ..db import db

router = APIRouter(tags=["sync"])

CATALOG = os.environ.get("BPA_CATALOG", "main")
SCHEMA = os.environ.get("BPA_SCHEMA", "bpa_rubjit")
WAREHOUSE_ID = os.environ.get("DATABRICKS_WAREHOUSE_ID", "e9b34f7a2e4b0561")

FIELD_PIVOTS = [
    ("Scheme Name", "scheme_name"),
    ("Scheme Type", "scheme_type"),
    ("Underwriter / Provider", "underwriter"),
    ("Effective Date", "effective_date"),
    ("Employer Contribution Rate", "employer_contribution"),
    ("Employee Contribution Rate", "employee_contribution"),
    ("Benefit Multiple / Percentage", "benefit_level"),
    ("Maximum Benefit Cap", "max_benefit_cap"),
    ("Deferred Period", "deferred_period"),
    ("Free Cover Limit", "free_cover_limit"),
]


async def execute_sql(statement: str) -> dict:
    host = get_workspace_host()
    token = get_oauth_token()
    url = f"{host}/api/2.0/sql/statements"

    async with aiohttp.ClientSession() as session:
        async with session.post(
            url,
            json={
                "warehouse_id": WAREHOUSE_ID,
                "statement": statement,
                "wait_timeout": "30s",
            },
            headers={"Authorization": f"Bearer {token}"},
        ) as resp:
            return await resp.json()


def escape_sql(value: str | None) -> str:
    if value is None:
        return "NULL"
    return "'" + value.replace("'", "''") + "'"


@router.post("/sync-to-delta")
async def sync_to_delta():
    pool = await db.get_pool()
    if not pool:
        raise HTTPException(503, "Database not available")

    async with pool.acquire() as conn:
        docs = await conn.fetch(
            "SELECT id, filename, file_type, status, upload_time FROM documents "
            "WHERE status = 'approved' ORDER BY id"
        )
        if not docs:
            return {"status": "ok", "message": "No approved documents to sync", "synced": 0}

        all_fields = await conn.fetch(
            "SELECT document_id, field_name, field_category, extracted_value, "
            "reviewed_value, confidence, is_approved "
            "FROM extracted_fields WHERE is_approved = TRUE ORDER BY id"
        )

    fields_by_doc: dict[int, list] = {}
    for f in all_fields:
        did = f["document_id"]
        if did not in fields_by_doc:
            fields_by_doc[did] = []
        fields_by_doc[did].append(f)

    truncate_summary = f"TRUNCATE TABLE {CATALOG}.{SCHEMA}.benefit_plans_summary"
    truncate_detail = f"TRUNCATE TABLE {CATALOG}.{SCHEMA}.benefit_plans_detail"
    await execute_sql(truncate_summary)
    await execute_sql(truncate_detail)

    conf_map = {"high": 1.0, "medium": 0.6, "low": 0.3}
    summary_rows: list[str] = []
    detail_rows: list[str] = []

    for doc in docs:
        doc_fields = fields_by_doc.get(doc["id"], [])
        field_map = {
            f["field_name"]: (f["reviewed_value"] or f["extracted_value"])
            for f in doc_fields
        }

        pivot_values = [escape_sql(field_map.get(name)) for name, _ in FIELD_PIVOTS]

        total_fields = len(doc_fields)
        approved_fields = sum(1 for f in doc_fields if f["is_approved"])
        avg_conf = (
            sum(conf_map.get(f["confidence"], 0.5) for f in doc_fields)
            / max(total_fields, 1)
        )

        summary_rows.append(
            f"({doc['id']}, {escape_sql(doc['filename'])}, "
            f"{escape_sql(doc['file_type'])}, {escape_sql(doc['status'])}, "
            f"TIMESTAMP '{doc['upload_time']}', {', '.join(pivot_values)}, "
            f"{total_fields}, {approved_fields}, {avg_conf:.2f})"
        )

        for f in doc_fields:
            final = f["reviewed_value"] or f["extracted_value"]
            detail_rows.append(
                f"({doc['id']}, {escape_sql(doc['filename'])}, "
                f"{escape_sql(doc['status'])}, 0, {escape_sql(f['field_name'])}, "
                f"{escape_sql(f['field_category'])}, {escape_sql(f['extracted_value'])}, "
                f"{escape_sql(f['reviewed_value'])}, {escape_sql(final)}, "
                f"{escape_sql(f['confidence'])}, {f['is_approved']})"
            )

    async def _bulk_insert(table: str, rows: list[str], chunk_size: int = 300) -> None:
        for i in range(0, len(rows), chunk_size):
            chunk = rows[i : i + chunk_size]
            stmt = (
                f"INSERT INTO {CATALOG}.{SCHEMA}.{table} VALUES "
                + ", ".join(chunk)
            )
            await execute_sql(stmt)

    await _bulk_insert("benefit_plans_summary", summary_rows)
    await _bulk_insert("benefit_plans_detail", detail_rows)

    return {
        "status": "ok",
        "message": f"Synced {len(docs)} documents to Delta tables",
        "synced": len(docs),
        "catalog": f"{CATALOG}.{SCHEMA}",
    }
