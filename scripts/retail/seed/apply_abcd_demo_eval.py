#!/usr/bin/env python3.12
"""Write A/B/C demo eval JSONL for rrf_data_llm_gen (eval-only; keeps 60-row CSV).

Source: ``abcd_demo_eval_spec.py`` (V1 vector → V1.1 equal RRF → V1.2 term boost).
Operator: ``apply`` then ``cursor_gen/retail_v11_prep/05_run_abc_postgres.sh``.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts" / "retail" / "seed"))

from abcd_demo_eval_spec import ABCD_DEMO_EVAL_ROWS, row_to_jsonl_obj  # noqa: E402


def apply(corpus_dir: Path, *, archive: bool = True) -> Path:
    """Replace ticket_retrieval.jsonl from spec; optionally archive the previous file."""
    eval_path = corpus_dir / "ticket_retrieval.jsonl"
    if archive and eval_path.is_file():
        ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        dest = corpus_dir / f"ticket_retrieval_v2_archived_{ts}.jsonl"
        shutil.copy2(eval_path, dest)
    lines = [json.dumps(row_to_jsonl_obj(r), ensure_ascii=False) for r in ABCD_DEMO_EVAL_ROWS]
    eval_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return eval_path


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--corpus-dir",
        type=Path,
        default=ROOT / "scripts" / "retail" / "sim_data" / "profiles" / "data_60_10",
    )
    p.add_argument("--no-archive", action="store_true")
    args = p.parse_args()
    out = apply(args.corpus_dir, archive=not args.no_archive)
    print(f"apply_abcd_demo_eval: wrote {len(ABCD_DEMO_EVAL_ROWS)} rows -> {out}")


if __name__ == "__main__":
    main()
