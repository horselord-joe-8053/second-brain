#!/usr/bin/env python3.12
"""Populate query_embedding and query_tsv for loaded service_queries rows (Gemini, once per row)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "retail"))

from utils.retail_fru.env import load_repo_env  # noqa: E402

load_repo_env(ROOT)

from retail_brain.embeddings import EMBEDDING_DIMENSION, embed_text  # noqa: E402
from retail_brain.market import pg_ts_config  # noqa: E402
from retail_brain.text_normalize import search_text_for_fts, text_for_embedding  # noqa: E402


def main() -> None:
    dsn = os.environ.get("RETAIL_DATABASE_URL")
    if not dsn:
        print("RETAIL_DATABASE_URL required", file=sys.stderr)
        sys.exit(1)
    try:
        import psycopg2  # type: ignore
    except ImportError:
        print("pip install psycopg2-binary", file=sys.stderr)
        sys.exit(1)
    conn = psycopg2.connect(dsn)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT ticket_id, customer_query_text FROM service_queries WHERE query_embedding IS NULL"
            )
            rows = cur.fetchall()
            ts_cfg = pg_ts_config()
            for tid, text in rows:
                emb = embed_text(
                    text_for_embedding(text or ""),
                    task_type="RETRIEVAL_DOCUMENT",
                )
                if len(emb) != EMBEDDING_DIMENSION:
                    raise RuntimeError(f"unexpected embedding size for {tid}")
                emb_literal = "[" + ",".join(str(x) for x in emb) + "]"
                fts_body = search_text_for_fts(text or "")
                cur.execute(
                    """
                    UPDATE service_queries
                    SET query_embedding = %s::vector,
                        search_text = %s,
                        query_tsv = to_tsvector(%s, coalesce(%s, ''))
                    WHERE ticket_id = %s
                    """,
                    (emb_literal, fts_body, ts_cfg, fts_body, tid),
                )
        conn.commit()
        print(f"embedded + tsvector updated for {len(rows)} rows (dim={EMBEDDING_DIMENSION})")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
