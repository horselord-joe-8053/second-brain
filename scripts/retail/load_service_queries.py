#!/usr/bin/env python3.12
"""Load service_queries.csv into retail Postgres (requires RETAIL_DATABASE_URL)."""

from __future__ import annotations

import argparse
import csv
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "retail"))

from retail_brain.product_scope import product_for_oem  # noqa: E402


def _ts(value: str | None) -> str | None:
    """CSV may use '' for nullable timestamptz (e.g. open tickets without closed_at)."""
    if value is None:
        return None
    value = value.strip()
    return value or None


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("csv_path", type=Path)
    args = p.parse_args()
    dsn = os.environ.get("RETAIL_DATABASE_URL")
    if not dsn:
        print("RETAIL_DATABASE_URL not set — skip load (CI uses in-memory CSV tests).", file=sys.stderr)
        return
    try:
        import psycopg2  # type: ignore
    except ImportError:
        print("psycopg2 not installed — pip install psycopg2-binary for load.", file=sys.stderr)
        sys.exit(1)
    with args.csv_path.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    conn = psycopg2.connect(dsn)
    try:
        with conn.cursor() as cur:
            for r in rows:
                state = (r.get("state") or "").strip()
                if not state:
                    raise ValueError(f"missing state for ticket {r['ticket_id']}")
                oem = r["model"]
                pf = product_for_oem(oem)
                brand = (r.get("brand") or "").strip() or (pf.brand if pf else "") or ""
                cur.execute(
                    """
                    INSERT INTO service_queries (
                      ticket_id, customer_id, item_number, store_id, city, state, brand, model,
                      status, customer_query_text, resolution_text,
                      opened_at, updated_at, closed_at
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (ticket_id) DO NOTHING
                    """,
                    (
                        r["ticket_id"],
                        (r.get("customer_id") or None) or None,
                        r["item_number"],
                        r["store_id"],
                        r["city"],
                        state,
                        brand,
                        oem,
                        r["status"],
                        r["customer_query_text"],
                        r.get("resolution_text") or None,
                        _ts(r.get("opened_at")),
                        _ts(r.get("updated_at")),
                        _ts(r.get("closed_at")),
                    ),
                )
        conn.commit()
    finally:
        conn.close()
    print(f"loaded {len(rows)} service rows")


if __name__ == "__main__":
    main()
