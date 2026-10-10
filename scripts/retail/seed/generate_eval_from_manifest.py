#!/usr/bin/env python3
"""Build ticket_retrieval.jsonl from ticket_manifest.jsonl."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts" / "retail"))

from retail_brain.eval_gen import build_eval_rows, write_eval_jsonl  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--manifest",
        type=Path,
        default=Path(__file__).resolve().parent / "generated" / "ticket_manifest.jsonl",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "eval" / "ticket_retrieval.jsonl",
    )
    p.add_argument("--max-rows", type=int, default=50)
    args = p.parse_args()
    rows = build_eval_rows(args.manifest, max_rows=args.max_rows)
    write_eval_jsonl(args.out, rows)
    print(f"wrote {len(rows)} eval rows to {args.out}")


if __name__ == "__main__":
    main()
