#!/usr/bin/env python3.12
"""One-off: build ``fru_customers.jsonl`` from ultra-fru sales CSV (150 rows, 3 SKUs).

Run locally when refreshing the seed; committed JSONL is the CI source of truth.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

ALLOWED_MODELS = ("RF28K9070SG", "GNE27JYMFS", "KRFF507HPS")
_PER_SKU = 50
_ADDR = re.compile(r",\s*([^,]+),\s*([A-Z]{2})\s+\d{5}")


def _parse_city_state(address: str) -> tuple[str, str]:
    m = _ADDR.search(address or "")
    if not m:
        return "Unknown", "XX"
    return m.group(1).strip(), m.group(2).strip()


def extract(csv_path: Path) -> list[dict[str, str]]:
    """Return up to 150 customer rows (50 per allowed SKU)."""
    by_model: dict[str, list[dict[str, str]]] = {m: [] for m in ALLOWED_MODELS}
    with csv_path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            model = row["FRIDGE_MODEL"].strip()
            if model not in ALLOWED_MODELS:
                continue
            if len(by_model[model]) >= _PER_SKU:
                continue
            city, state = _parse_city_state(row["STORE_ADDRESS"])
            by_model[model].append(
                {
                    "customer_id": row["CUSTOMER_ID"].strip(),
                    "fridge_model": model,
                    "store_name": row["STORE_NAME"].strip(),
                    "city": city,
                    "state": state,
                    "sales_date": row["SALES_DATE"].strip(),
                }
            )
    out: list[dict[str, str]] = []
    for model in ALLOWED_MODELS:
        out.extend(by_model[model])
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--csv",
        type=Path,
        default=Path(
            "/Users/jjw8053/projects/ultra-fru-genai-analytics-new/core_app/data/raw/fridge_sales_with_rating.csv"
        ),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parent / "fru_customers.jsonl",
    )
    args = p.parse_args()
    rows = extract(args.csv)
    if len(rows) != 150:
        raise SystemExit(f"expected 150 rows, got {len(rows)}")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} -> {args.out}")


if __name__ == "__main__":
    main()
