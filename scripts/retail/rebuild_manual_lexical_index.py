#!/usr/bin/env python3.12
"""Rebuild manual_chunks Tantivy index from Postgres (evo-18 T0)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO / "scripts" / "retail") not in sys.path:
    sys.path.insert(0, str(REPO / "scripts" / "retail"))

from retail_brain.lexical_search.manual_tantivy_index import ManualTantivyLexicalIndex  # noqa: E402
from retail_brain.manual_pg_db import list_manual_chunks  # noqa: E402


def main() -> None:
    """Load all manual_chunks rows and rebuild the manual Tantivy directory."""
    dsn = (os.environ.get("RETAIL_PG_DSN") or os.environ.get("RETAIL_DATABASE_URL") or "").strip()
    if not dsn:
        raise SystemExit("RETAIL_DATABASE_URL (or RETAIL_PG_DSN) required")
    lane_id = os.environ.get("RETAIL_MANUAL_LEXICAL_LANE", "B").strip() or "B"
    import psycopg2  # type: ignore

    conn = psycopg2.connect(dsn)
    try:
        with conn.cursor() as cur:
            rows_db = list_manual_chunks(cur, lane_id=lane_id, limit=500_000)
    finally:
        conn.close()
    tantivy_rows = [
        (str(r["chunk_id"]), str(r.get("text") or ""), str(r.get("brand") or ""), str(r.get("oem_model") or ""))
        for r in rows_db
    ]
    idx = ManualTantivyLexicalIndex()
    print(f"[manual_lexical] rebuilding {len(tantivy_rows)} chunks lane={lane_id}", file=sys.stderr)
    idx.rebuild(tantivy_rows)
    print("[manual_lexical] rebuild complete", file=sys.stderr)


if __name__ == "__main__":
    main()
