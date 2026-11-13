#!/usr/bin/env python3.12
"""Backfill service_queries.brand and manual_chunks brand/oem_model from fru_us_service.yaml."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts" / "retail"))

from retail_brain.manual_pg_db import BRAND_MODEL_SQL  # noqa: E402
from retail_brain.product_scope import product_for_ingest_key, product_for_oem  # noqa: E402


def main() -> None:
    dsn = os.environ.get("RETAIL_DATABASE_URL")
    if not dsn:
        print("RETAIL_DATABASE_URL not set", file=sys.stderr)
        sys.exit(1)
    import psycopg2  # type: ignore

    conn = psycopg2.connect(dsn)
    try:
        with conn.cursor() as cur:
            if BRAND_MODEL_SQL.is_file():
                cur.execute(BRAND_MODEL_SQL.read_text(encoding="utf-8"))
            cur.execute("SELECT ticket_id, model FROM service_queries")
            for ticket_id, model in cur.fetchall():
                pf = product_for_oem(str(model or ""))
                brand = pf.brand if pf else ""
                cur.execute(
                    "UPDATE service_queries SET brand = %s WHERE ticket_id = %s",
                    (brand or "", ticket_id),
                )
            cur.execute("SELECT chunk_id, model_id FROM manual_chunks")
            for chunk_id, model_id in cur.fetchall():
                pf = product_for_ingest_key(str(model_id or ""))
                cur.execute(
                    """
                    UPDATE manual_chunks
                    SET brand = %s, oem_model = %s
                    WHERE chunk_id = %s
                    """,
                    (pf.brand if pf else "", pf.oem_model if pf else "", chunk_id),
                )
        conn.commit()
        print("backfill product brand/model complete")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
