"""Routes for browsing and ingesting files from a Unity Catalog Volume."""

import os

from fastapi import APIRouter, HTTPException

from ..config import get_workspace_client
from ..db import db
from ..models import DocumentOut

router = APIRouter(tags=["volume"])

# Allow per-workspace overrides via env vars so the same source tree can run
# against any FE-VM / demo workspace without code edits.
_CATALOG = os.environ.get("BPA_CATALOG", "main")
_SCHEMA = os.environ.get("BPA_SCHEMA", "bpa_rubjit")
_VOLUME = os.environ.get("BPA_VOLUME", "documents")
VOLUME_PATH = f"/Volumes/{_CATALOG}/{_SCHEMA}/{_VOLUME}"

SUPPORTED_EXTENSIONS = (".pdf", ".xlsx", ".xls", ".csv", ".docx")


def _is_supported(name: str) -> bool:
    return name.lower().endswith(SUPPORTED_EXTENSIONS)


def _customer_display(slug: str) -> str:
    """Convert a folder slug into a human readable customer name."""
    if not slug:
        return ""
    overrides = {
        "bdo": "BDO Pension Fund",
        "renishaw": "Renishaw plc Pension Scheme",
        "reading_university": "University of Reading Pension Scheme",
        "thames_water": "Thames Water UPS (Closed Section)",
        "spirax_sarco": "Spirax-Sarco Engineering Pension Plan",
        "rsm_uk": "RSM UK Pension Fund",
    }
    if slug in overrides:
        return overrides[slug]
    return slug.replace("_", " ").title()


@router.get("/volume-files")
async def list_volume_files():
    """List files in the root of the volume plus one level of subfolders.

    Each file entry includes a `customer` slug (empty string for root-level
    files) and `display` name. The frontend uses these to group files.
    """
    try:
        client = get_workspace_client()
        files: list[dict] = []

        root_entries = list(client.files.list_directory_contents(VOLUME_PATH))

        for entry in root_entries:
            path = entry.path or ""
            name = path.rstrip("/").split("/")[-1] if path else ""

            is_directory = bool(getattr(entry, "is_directory", False))

            if is_directory:
                try:
                    sub_entries = list(
                        client.files.list_directory_contents(f"{VOLUME_PATH}/{name}")
                    )
                except Exception:
                    continue
                for sub in sub_entries:
                    sub_path = sub.path or ""
                    sub_name = sub_path.rstrip("/").split("/")[-1] if sub_path else ""
                    if _is_supported(sub_name) and not getattr(sub, "is_directory", False):
                        files.append({
                            "name": sub_name,
                            "path": sub_path,
                            "size": getattr(sub, "file_size", None),
                            "customer": name,
                            "customer_display": _customer_display(name),
                            "relative_path": f"{name}/{sub_name}",
                        })
            elif _is_supported(name):
                files.append({
                    "name": name,
                    "path": path,
                    "size": getattr(entry, "file_size", None),
                    "customer": "",
                    "customer_display": "Uncategorised",
                    "relative_path": name,
                })

        return {"volume_path": VOLUME_PATH, "files": files}
    except Exception as e:
        raise HTTPException(500, f"Failed to list volume files: {e}")


@router.post("/upload-from-volume")
async def upload_from_volume(filename: str):
    """Ingest a file from the volume by relative path.

    `filename` can be either a bare filename (root of the volume) or a
    `<customer>/<filename>` subpath.
    """
    from .upload import EXT_TO_TYPE, EXTRACTORS
    from .ai_sql import ai_parse_pdf_from_volume

    relative = filename.lstrip("/")
    file_path = f"{VOLUME_PATH}/{relative}"

    base_name = relative.rsplit("/", 1)[-1]
    ext = base_name.rsplit(".", 1)[-1].lower() if "." in base_name else ""
    file_type = EXT_TO_TYPE.get(ext)
    if not file_type:
        raise HTTPException(400, f"Unsupported file type: .{ext}")

    # For PDFs we let Databricks do the heavy lifting end-to-end: the SQL
    # warehouse reads the file directly from the UC Volume and runs
    # ``ai_parse_document`` on it, returning markdown text. No local parser,
    # no extra download round trip.
    try:
        if file_type == "pdf":
            raw_text = await ai_parse_pdf_from_volume(file_path)
        else:
            client = get_workspace_client()
            resp = client.files.download(file_path)
            content = resp.contents.read()
            raw_text = await EXTRACTORS[file_type](content)
    except Exception as e:
        raise HTTPException(500, f"Failed to parse document: {e}")

    if not raw_text.strip():
        raise HTTPException(422, "No text could be extracted from the file")

    pool = await db.get_pool()
    if not pool:
        raise HTTPException(503, "Database not available")

    kind_expr = (
        "document_kind" if db.has_document_kind else "NULL::text AS document_kind"
    )
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                f"""
                INSERT INTO documents (filename, file_type, status, raw_text, source_path)
                VALUES ($1, $2, 'uploaded', $3, $4)
                RETURNING id, filename, file_type, upload_time, status, raw_text,
                          {kind_expr}
                """,
                base_name,
                file_type,
                raw_text,
                file_path,
            )
    except Exception as e:
        raise HTTPException(500, f"DB insert failed: {e}")

    return DocumentOut(**dict(row))
