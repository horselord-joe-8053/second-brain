#!/usr/bin/env python3
"""Generate synthetic service CSV + ticket manifest (deterministic seed)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts" / "retail"))

from retail_brain.seed import generate_tickets, write_manifest, write_service_csv  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--count", type=int, default=500)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out-dir", type=Path, default=Path(__file__).resolve().parent / "generated")
    args = p.parse_args()
    rows = generate_tickets(count=args.count, seed=args.seed)
    write_service_csv(args.out_dir / "service_queries.csv", rows)
    write_manifest(args.out_dir / "ticket_manifest.jsonl", rows, seed=args.seed)
    print(f"wrote {len(rows)} tickets under {args.out_dir}")


if __name__ == "__main__":
    main()
