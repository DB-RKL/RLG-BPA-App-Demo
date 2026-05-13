import asyncio
import io

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from ..config import get_workspace_client
from ..db import db
from ..models import DocumentOut, ExtractedFieldOut, FieldUpdate, BulkApprove, BulkApproveDocs


def _schedule_background_sync() -> None:
    """Kick off sync_to_delta() as a detached task so the HTTP response can
    return immediately. Any exception is swallowed (demo context)."""
    from .sync import sync_to_delta

    async def _runner():
        try:
            await sync_to_delta()
        except Exception as e:
            print(f"[BACKGROUND-SYNC] failed: {type(e).__name__}: {e}", flush=True)

    try:
        asyncio.create_task(_runner())
    except RuntimeError:
        pass

router = APIRouter(tags=["documents"])


@router.get("/documents", response_model=list[DocumentOut])
async def list_documents():
    pool = await db.get_pool()
    if not pool:
        raise HTTPException(503, "Database not available")

    kind_expr = (
        "document_kind" if db.has_document_kind else "NULL::text AS document_kind"
    )
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            f"SELECT id, filename, file_type, upload_time, status, raw_text, "
            f"{kind_expr} "
            f"FROM documents ORDER BY upload_time DESC"
        )
    return [DocumentOut(**dict(r)) for r in rows]


@router.get("/documents/{document_id}", response_model=DocumentOut)
async def get_document(document_id: int):
    pool = await db.get_pool()
    if not pool:
        raise HTTPException(503, "Database not available")

    kind_expr = (
        "document_kind" if db.has_document_kind else "NULL::text AS document_kind"
    )
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            f"SELECT id, filename, file_type, upload_time, status, raw_text, "
            f"{kind_expr} "
            f"FROM documents WHERE id = $1",
            document_id,
        )
    if not row:
        raise HTTPException(404, "Document not found")
    return DocumentOut(**dict(row))


MEDIA_TYPES = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "xls": "application/vnd.ms-excel",
    "csv": "text/csv",
    "txt": "text/plain",
}


@router.get("/documents/{document_id}/source")
async def get_document_source(document_id: int):
    """Stream the original document bytes from the Unity Catalog Volume."""
    pool = await db.get_pool()
    if not pool:
        raise HTTPException(503, "Database not available")

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT filename, file_type, source_path FROM documents WHERE id = $1",
            document_id,
        )
    if not row:
        raise HTTPException(404, "Document not found")

    source_path = row["source_path"]
    if not source_path:
        raise HTTPException(404, "No source file recorded for this document")

    try:
        client = get_workspace_client()
        resp = client.files.download(source_path)
        content = resp.contents.read()
    except Exception as e:
        raise HTTPException(500, f"Failed to read source file: {e}")

    file_type = (row["file_type"] or "").lower()
    media_type = MEDIA_TYPES.get(file_type, "application/octet-stream")
    filename = row["filename"] or f"document-{document_id}"

    return StreamingResponse(
        io.BytesIO(content),
        media_type=media_type,
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


@router.get("/documents/{document_id}/fields", response_model=list[ExtractedFieldOut])
async def get_document_fields(document_id: int):
    pool = await db.get_pool()
    if not pool:
        raise HTTPException(503, "Database not available")

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT id, document_id, field_name, field_category, "
            "extracted_value, reviewed_value, confidence, is_approved "
            "FROM extracted_fields WHERE document_id = $1 "
            "ORDER BY id",
            document_id,
        )
    return [ExtractedFieldOut(**dict(r)) for r in rows]


@router.patch("/fields/{field_id}", response_model=ExtractedFieldOut)
async def update_field(field_id: int, update: FieldUpdate):
    pool = await db.get_pool()
    if not pool:
        raise HTTPException(503, "Database not available")

    async with pool.acquire() as conn:
        existing = await conn.fetchrow(
            "SELECT id FROM extracted_fields WHERE id = $1", field_id
        )
        if not existing:
            raise HTTPException(404, "Field not found")

        sets: list[str] = []
        args: list = []
        idx = 1

        if update.reviewed_value is not None:
            sets.append(f"reviewed_value = ${idx}")
            args.append(update.reviewed_value)
            idx += 1

        if update.is_approved is not None:
            sets.append(f"is_approved = ${idx}")
            args.append(update.is_approved)
            idx += 1

        if not sets:
            raise HTTPException(400, "No fields to update")

        args.append(field_id)
        query = (
            f"UPDATE extracted_fields SET {', '.join(sets)} "
            f"WHERE id = ${idx} "
            f"RETURNING id, document_id, field_name, field_category, "
            f"extracted_value, reviewed_value, confidence, is_approved"
        )
        row = await conn.fetchrow(query, *args)

    return ExtractedFieldOut(**dict(row))


@router.post("/documents/{document_id}/approve-all")
async def approve_all_fields(document_id: int):
    pool = await db.get_pool()
    if not pool:
        raise HTTPException(503, "Database not available")

    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE extracted_fields SET is_approved = TRUE WHERE document_id = $1",
            document_id,
        )
        await conn.execute(
            "UPDATE documents SET status = 'approved' WHERE id = $1",
            document_id,
        )

    _schedule_background_sync()
    return {"status": "ok", "message": "All fields approved"}


@router.post("/documents/bulk-approve-docs")
async def bulk_approve_docs(payload: BulkApproveDocs):
    """Approve every field for each document in `document_ids` and mark the
    documents as approved. A single Delta sync is scheduled in the background
    so the HTTP response returns in ~200ms."""
    if not payload.document_ids:
        return {"status": "ok", "approved": 0}

    pool = await db.get_pool()
    if not pool:
        raise HTTPException(503, "Database not available")

    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE extracted_fields SET is_approved = TRUE "
            "WHERE document_id = ANY($1::int[])",
            payload.document_ids,
        )
        await conn.execute(
            "UPDATE documents SET status = 'approved' "
            "WHERE id = ANY($1::int[])",
            payload.document_ids,
        )

    _schedule_background_sync()
    return {
        "status": "ok",
        "approved": len(payload.document_ids),
        "document_ids": payload.document_ids,
    }


@router.post("/fields/bulk-approve")
async def bulk_approve_fields(payload: BulkApprove):
    pool = await db.get_pool()
    if not pool:
        raise HTTPException(503, "Database not available")

    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE extracted_fields SET is_approved = TRUE WHERE id = ANY($1::int[])",
            payload.field_ids,
        )

    return {"status": "ok", "approved": len(payload.field_ids)}
