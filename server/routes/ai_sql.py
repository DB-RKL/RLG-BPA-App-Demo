"""Wrappers around Databricks SQL AI functions (``ai_parse_document`` and
``ai_extract``).

The app used to parse PDFs locally with ``pdfplumber`` and then call the
Foundation Model API directly with a hand-rolled prompt. This module replaces
those two steps with the native Databricks SQL functions so the entire
extraction pipeline runs on the Data Intelligence Platform:

* ``ai_parse_document`` — runs on the SQL warehouse, reads the file straight
  from Unity Catalog Volumes, and returns markdown text.
* ``ai_extract`` — runs on the SQL warehouse, extracts the requested labels
  from the parsed text, and returns a struct keyed by label.
"""

import asyncio
import json
import os
from typing import Any

import aiohttp

from ..config import get_oauth_token, get_workspace_host


WAREHOUSE_ID = os.environ.get("DATABRICKS_WAREHOUSE_ID", "ced20c73f16a2915")


def _escape_sql(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "''") + "'"


async def _run_statement(
    statement: str,
    wait_timeout: str = "50s",
    poll_timeout: float = 240.0,
) -> dict:
    """Submit a SQL statement and block until it reaches a terminal state."""
    host = get_workspace_host()
    token = get_oauth_token()
    base = f"{host}/api/2.0/sql/statements"
    headers = {"Authorization": f"Bearer {token}"}

    async with aiohttp.ClientSession() as session:
        async with session.post(
            base,
            json={
                "warehouse_id": WAREHOUSE_ID,
                "statement": statement,
                "wait_timeout": wait_timeout,
            },
            headers=headers,
        ) as resp:
            result = await resp.json()

        statement_id = result.get("statement_id")
        loop = asyncio.get_event_loop()
        deadline = loop.time() + poll_timeout

        while True:
            state = (result.get("status") or {}).get("state")
            if state in ("SUCCEEDED", "FAILED", "CANCELED", "CLOSED"):
                if state != "SUCCEEDED":
                    err = (result.get("status") or {}).get("error") or {}
                    raise RuntimeError(
                        f"ai_sql statement {state}: {err.get('message', result)}"
                    )
                return result
            if loop.time() > deadline:
                raise TimeoutError(f"Statement {statement_id} did not complete")
            await asyncio.sleep(1.5)
            async with session.get(
                f"{base}/{statement_id}", headers=headers
            ) as resp:
                result = await resp.json()


def _first_cell(result: dict) -> Any:
    rows = (result.get("result") or {}).get("data_array") or []
    if not rows or not rows[0]:
        return None
    return rows[0][0]


async def ai_parse_pdf_from_volume(volume_path: str) -> str:
    """Run ``ai_parse_document`` on a PDF sitting in a UC Volume and return
    the markdown text it produces."""
    path_literal = _escape_sql(volume_path)
    stmt = (
        "WITH raw AS ("
        f"  SELECT content FROM read_files({path_literal}, format => 'binaryFile')"
        ") "
        "SELECT CAST(ai_parse_document(content) AS STRING) FROM raw"
    )
    res = await _run_statement(stmt)
    return _first_cell(res) or ""


AI_EXTRACT_MAX_LABELS_PER_CALL = 15


async def _ai_extract_chunk(text_literal: str, labels: list[str]) -> dict[str, Any]:
    """Call ai_extract for a single chunk of labels (<= 20) and return parsed JSON."""
    labels_array = "ARRAY(" + ", ".join(_escape_sql(f) for f in labels) + ")"
    stmt = f"SELECT TO_JSON(ai_extract({text_literal}, {labels_array}))"
    res = await _run_statement(stmt)
    raw_json = _first_cell(res) or "{}"
    try:
        return json.loads(raw_json)
    except json.JSONDecodeError:
        return {}


async def ai_extract_fields(
    raw_text: str, field_names: list[str]
) -> dict[str, str]:
    """Call ``ai_extract(text, ARRAY(labels...))`` and return a ``{label: value}``
    dict.

    Databricks' ``ai_extract`` caps the output struct schema at 20 fields, so we
    chunk ``field_names`` into batches of ``AI_EXTRACT_MAX_LABELS_PER_CALL``
    and merge the results. Chunks are issued concurrently since they're
    independent warehouse calls.
    """
    if not raw_text.strip() or not field_names:
        return {name: "" for name in field_names}

    # ai_extract handles large inputs but we trim to keep the warehouse call
    # snappy during the speed-run demo.
    truncated = raw_text[:15000]
    text_literal = _escape_sql(truncated)

    chunk_size = AI_EXTRACT_MAX_LABELS_PER_CALL
    chunks: list[list[str]] = [
        field_names[i : i + chunk_size]
        for i in range(0, len(field_names), chunk_size)
    ]

    merged: dict[str, Any] = {}
    results = await asyncio.gather(
        *[_ai_extract_chunk(text_literal, chunk) for chunk in chunks],
        return_exceptions=True,
    )
    chunk_errors: list[str] = []
    for chunk, result in zip(chunks, results):
        if isinstance(result, Exception):
            chunk_errors.append(f"{len(chunk)} labels: {type(result).__name__}: {result}")
            continue
        merged.update(result)

    if chunk_errors and not merged:
        # Everything failed — surface the first error so extract.py can delete
        # the document and the reviewer can retry.
        raise RuntimeError(f"ai_extract failed for all chunks: {chunk_errors[0]}")

    # Build a lookup keyed by several normalisations so we can match regardless
    # of whether ai_extract preserves the label verbatim or underscores it.
    def _norm(s: str) -> str:
        return "".join(c.lower() for c in s if c.isalnum())

    key_lookup: dict[str, Any] = {}
    for k, v in merged.items():
        key_lookup[k] = v
        key_lookup[_norm(k)] = v

    normalised: dict[str, str] = {}
    for name in field_names:
        value = key_lookup.get(name)
        if value is None:
            value = key_lookup.get(_norm(name))
        if value is None:
            normalised[name] = ""
        elif isinstance(value, (str, int, float, bool)):
            normalised[name] = str(value)
        else:
            normalised[name] = json.dumps(value, ensure_ascii=False)
    return normalised
