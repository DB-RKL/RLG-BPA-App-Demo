from fastapi import APIRouter, HTTPException

from ..db import db
from ..extraction_schemas import (
    classify_document_kind,
    field_names_for_kind,
    get_category_for_field,
)
from ..models import ExtractedFieldOut
from .ai_sql import ai_extract_fields

router = APIRouter(tags=["extract"])


_MISSING_TOKENS = {"", "n/a", "na", "none", "null", "unknown", "not specified", "not found"}


def _derive_confidence(value: str) -> tuple[str, str]:
    """Map a raw ai_extract value to (normalised_value, confidence).

    ai_extract itself doesn't return confidence, so we derive a pragmatic
    signal from the value's presence and length — that keeps the existing
    confidence pill in the UI meaningful.
    """
    clean = (value or "").strip()
    if clean.lower() in _MISSING_TOKENS:
        return "N/A", "low"
    if len(clean) < 3:
        return clean, "medium"
    return clean, "high"


@router.post("/extract/{document_id}", response_model=list[ExtractedFieldOut])
async def extract_fields(document_id: int):
    pool = await db.get_pool()
    if not pool:
        raise HTTPException(503, "Database not available")

    async with pool.acquire() as conn:
        doc = await conn.fetchrow(
            "SELECT id, filename, raw_text, status FROM documents WHERE id = $1",
            document_id,
        )
        if not doc:
            raise HTTPException(404, "Document not found")

        kind = classify_document_kind(doc["filename"])
        field_names = field_names_for_kind(kind)

        # document_kind is only persisted when the Lakebase column exists
        # (the SP may not own the table and can't ALTER it to add it).
        # Classification + per-kind schema routing still works in memory.
        if db.has_document_kind:
            await conn.execute(
                "UPDATE documents SET status = 'extracting', document_kind = $2 "
                "WHERE id = $1",
                document_id,
                kind,
            )
        else:
            await conn.execute(
                "UPDATE documents SET status = 'extracting' WHERE id = $1",
                document_id,
            )

    try:
        values = await ai_extract_fields(doc["raw_text"] or "", field_names)
    except Exception as e:
        async with pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM documents WHERE id = $1", document_id
            )
        raise HTTPException(500, f"ai_extract failed: {e}")

    inserted: list[ExtractedFieldOut] = []
    async with pool.acquire() as conn:
        await conn.execute(
            "DELETE FROM extracted_fields WHERE document_id = $1", document_id
        )

        for field_name in field_names:
            raw_value = values.get(field_name, "")
            value, confidence = _derive_confidence(raw_value)
            category = get_category_for_field(field_name)

            row = await conn.fetchrow(
                """
                INSERT INTO extracted_fields
                    (document_id, field_name, field_category, extracted_value, confidence)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id, document_id, field_name, field_category,
                          extracted_value, reviewed_value, confidence, is_approved
                """,
                document_id,
                field_name,
                category,
                value,
                confidence,
            )
            inserted.append(ExtractedFieldOut(**dict(row)))

        await conn.execute(
            "UPDATE documents SET status = 'review' WHERE id = $1", document_id
        )

    return inserted
