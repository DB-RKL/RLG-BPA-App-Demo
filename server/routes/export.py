import csv
import io
import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse

from ..db import db

router = APIRouter(tags=["export"])


@router.get("/export/csv")
async def export_csv():
    pool = await db.get_pool()
    if not pool:
        raise HTTPException(503, "Database not available")

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT
                d.filename,
                d.file_type,
                d.upload_time,
                d.status AS document_status,
                ef.field_name,
                ef.field_category,
                COALESCE(ef.reviewed_value, ef.extracted_value) AS final_value,
                ef.confidence,
                ef.is_approved
            FROM documents d
            JOIN extracted_fields ef ON ef.document_id = d.id
            WHERE d.status = 'approved' AND ef.is_approved = TRUE
            ORDER BY d.id, ef.id
            """
        )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Filename", "File Type", "Upload Time", "Document Status",
        "Field Name", "Field Category", "Value", "Confidence", "Approved",
    ])
    for r in rows:
        writer.writerow([
            r["filename"], r["file_type"], str(r["upload_time"]),
            r["document_status"], r["field_name"], r["field_category"],
            r["final_value"], r["confidence"], r["is_approved"],
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=benefit_plans_export.csv"},
    )


@router.get("/export/json")
async def export_json():
    pool = await db.get_pool()
    if not pool:
        raise HTTPException(503, "Database not available")

    async with pool.acquire() as conn:
        docs = await conn.fetch(
            "SELECT id, filename, file_type, upload_time, status "
            "FROM documents WHERE status = 'approved' ORDER BY id"
        )
        result = []
        for doc in docs:
            fields = await conn.fetch(
                """
                SELECT field_name, field_category,
                       COALESCE(reviewed_value, extracted_value) AS value,
                       confidence
                FROM extracted_fields
                WHERE document_id = $1 AND is_approved = TRUE
                ORDER BY id
                """,
                doc["id"],
            )
            result.append({
                "document": {
                    "id": doc["id"],
                    "filename": doc["filename"],
                    "file_type": doc["file_type"],
                    "upload_time": str(doc["upload_time"]),
                },
                "fields": {
                    f["field_name"]: {
                        "value": f["value"],
                        "category": f["field_category"],
                        "confidence": f["confidence"],
                    }
                    for f in fields
                },
            })

    return JSONResponse(content=result)


@router.get("/export/summary")
async def export_summary():
    """Flat summary view matching the SQL Warehouse reporting view."""
    pool = await db.get_pool()
    if not pool:
        raise HTTPException(503, "Database not available")

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT
                d.id AS document_id,
                d.filename,
                d.status,
                d.upload_time,
                COUNT(ef.id) AS total_fields,
                COUNT(ef.id) FILTER (WHERE ef.is_approved) AS approved_fields,
                ROUND(AVG(CASE
                    WHEN ef.confidence = 'high' THEN 1.0
                    WHEN ef.confidence = 'medium' THEN 0.6
                    ELSE 0.3
                END)::numeric, 2) AS avg_confidence
            FROM documents d
            LEFT JOIN extracted_fields ef ON ef.document_id = d.id
            WHERE d.status IS DISTINCT FROM 'error'
            GROUP BY d.id
            ORDER BY d.upload_time DESC
            """
        )

    return [dict(r) for r in rows]
