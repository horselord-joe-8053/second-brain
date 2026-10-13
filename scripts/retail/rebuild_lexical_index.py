#!/usr/bin/env python3.12
"""Rebuild the active keyword index from Postgres without re-embed.

Use after switching ``RETAIL_LEXICAL_BACKEND`` when ``service_queries`` is already loaded.
Corpus reload (truncate + load + embed) lives in ``reload_postgres_corpus.py``.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "retail"))

from utils.retail_fru.env import load_repo_env  # noqa: E402

load_repo_env(ROOT)

from retail_brain.lexical_search import lexical_backend_name, rebuild_active  # noqa: E402


def main() -> None:
    """Read resolved tickets from PG and call ``rebuild_active`` for the selected backend."""
    dsn = os.environ.get("RETAIL_DATABASE_URL")
    if not dsn:
        raise SystemExit("RETAIL_DATABASE_URL required")

    import psycopg2

    backend = lexical_backend_name()
    conn = psycopg2.connect(dsn)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT ticket_id, coalesce(customer_query_text, ''), model
                FROM service_queries
                WHERE status = 'resolved'
                """
            )
            rows = [(row[0], row[1], row[2]) for row in cur.fetchall()]
    finally:
        conn.close()

    print(f"[lexical] backend={backend} rebuilding from {len(rows)} resolved rows", file=sys.stderr)
    rebuild_active(rows)
    print("[lexical] rebuild complete", file=sys.stderr)


if __name__ == "__main__":
    main()
