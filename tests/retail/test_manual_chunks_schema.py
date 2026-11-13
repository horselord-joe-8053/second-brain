"""P1 — manual_chunks Postgres schema (unified PG manual embeddings plan)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
MIGRATION = REPO / "scripts" / "retail" / "schema" / "005_manual_chunks.sql"


def test_manual_chunks_migration_sql_exists() -> None:
    """Schema migration is versioned under scripts/retail/schema/."""
    assert MIGRATION.is_file()
    body = MIGRATION.read_text(encoding="utf-8")
    assert "manual_chunks" in body
    assert "vector(1536)" in body
    assert "chunk_tsv" in body


@pytest.mark.skipif(not os.environ.get("RETAIL_DATABASE_URL"), reason="optional live Postgres")
def test_manual_chunks_table_applies_and_accepts_row() -> None:
    """Apply 005 on dev PG and round-trip one empty-dimension row."""
    import psycopg2  # type: ignore

    from retail_brain.manual_pg_db import apply_manual_chunks_schema

    dsn = os.environ["RETAIL_DATABASE_URL"]
    conn = psycopg2.connect(dsn)
    try:
        with conn.cursor() as cur:
            apply_manual_chunks_schema(cur)
            cur.execute(
                """
                INSERT INTO manual_chunks (
                  chunk_id, lane_id, source_relpath, model_id, chunk_index,
                  text, content_hash, embedding
                ) VALUES (
                  'test-chunk-1', 'B', 'raw/x.md', 'sku_test', 0,
                  'hello', 'abc', NULL
                )
                ON CONFLICT (chunk_id) DO UPDATE SET text = EXCLUDED.text
                """
            )
            cur.execute("SELECT count(*) FROM manual_chunks WHERE chunk_id = %s", ("test-chunk-1",))
            assert cur.fetchone()[0] == 1
            cur.execute("DELETE FROM manual_chunks WHERE chunk_id = %s", ("test-chunk-1",))
        conn.commit()
    finally:
        conn.close()
