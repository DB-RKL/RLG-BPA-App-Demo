import os
from typing import Optional

import asyncpg

from .config import get_oauth_token, IS_DATABRICKS_APP

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    upload_time TIMESTAMP DEFAULT NOW(),
    status TEXT DEFAULT 'uploaded',
    raw_text TEXT,
    source_path TEXT,
    document_kind TEXT
);

ALTER TABLE documents ADD COLUMN IF NOT EXISTS source_path TEXT;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS document_kind TEXT;

CREATE TABLE IF NOT EXISTS extracted_fields (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    field_name TEXT NOT NULL,
    field_category TEXT DEFAULT 'general',
    extracted_value TEXT,
    reviewed_value TEXT,
    confidence TEXT DEFAULT 'medium',
    is_approved BOOLEAN DEFAULT FALSE
);
"""


class DatabasePool:
    def __init__(self):
        self._pool: Optional[asyncpg.Pool] = None
        self._demo_mode = False
        # True once we've confirmed the `document_kind` column exists.
        # Lakebase service principals often lack ALTER on shared tables, so
        # we fall back to omitting the column from SELECT/INSERT when it's
        # missing rather than 500'ing every request.
        self._has_document_kind = False

    async def get_pool(self) -> Optional[asyncpg.Pool]:
        if not os.environ.get("PGHOST"):
            self._demo_mode = True
            return None

        if self._pool is None:
            try:
                self._pool = await asyncpg.create_pool(
                    host=os.environ["PGHOST"],
                    port=int(os.environ.get("PGPORT", "5432")),
                    database=os.environ["PGDATABASE"],
                    user=os.environ["PGUSER"],
                    password=get_oauth_token,
                    ssl="require",
                    min_size=2,
                    max_size=10,
                    max_inactive_connection_lifetime=600,
                )
            except Exception as e:
                print(f"Lakebase connection failed: {e}")
                self._demo_mode = True
                return None
        return self._pool

    async def initialize_schema(self):
        try:
            pool = await self.get_pool()
            if not pool:
                return
            async with pool.acquire() as conn:
                # Best-effort CREATE; Lakebase SPs often lack CREATE on
                # `public`, in which case the table already exists and the
                # per-statement migrations below converge the schema.
                try:
                    await conn.execute(SCHEMA_SQL)
                except Exception:
                    pass
                for stmt in (
                    "ALTER TABLE documents ADD COLUMN IF NOT EXISTS source_path TEXT",
                    "ALTER TABLE documents ADD COLUMN IF NOT EXISTS document_kind TEXT",
                    "DELETE FROM documents WHERE status = 'error'",
                ):
                    try:
                        await conn.execute(stmt)
                    except Exception:
                        pass
                # Record whether the document_kind column is actually usable.
                # When the SP doesn't own the table it can't ALTER, so we fall
                # back to synthesising the column at query time.
                try:
                    col_row = await conn.fetchrow(
                        "SELECT column_name FROM information_schema.columns "
                        "WHERE table_name='documents' AND column_name='document_kind'"
                    )
                    self._has_document_kind = bool(col_row)
                except Exception:
                    self._has_document_kind = False
        except Exception:
            pass

    async def refresh_token(self):
        if self._pool:
            await self._pool.close()
            self._pool = None
        await self.get_pool()

    @property
    def is_demo_mode(self) -> bool:
        return self._demo_mode

    @property
    def has_document_kind(self) -> bool:
        return self._has_document_kind


db = DatabasePool()
