#!/usr/bin/env python3.12
"""Validate tmp/simulated_data llm_gen corpus (REFACTOR_RETAIL_LLM_CORPUS_V2_NATURAL)."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts" / "retail"))

from retail_brain.text_normalize import extract_diag_code  # noqa: E402

_SAM = re.compile(r"SAM-E\d{3}", re.I)
_DEMO_LIFT = frozenset(
    {"vector_only", "rrf_normal", "rrf_weighted", "rrf_weighted_boosted"},
)
_REQUIRED_EVAL_KEYS = (
    "eval_id",
    "query",
    "model_filter",
    "expected_ticket_ids",
    "stratum",
    "source_ticket_id",
)


def _normalize_body(text: str) -> str:
    t = _SAM.sub("<CODE>", text.lower())
    t = re.sub(r"\s+", " ", t).strip()
    return t


def validate(corpus_dir: Path) -> list[str]:
    errors: list[str] = []
    csv_path = corpus_dir / "service_queries.csv"
    eval_path = corpus_dir / "ticket_retrieval.jsonl"
    if not csv_path.is_file():
        return [f"missing {csv_path}"]
    if not eval_path.is_file():
        return [f"missing {eval_path}"]

    with csv_path.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 60:
        errors.append(f"expected 60 CSV rows, got {len(rows)}")

    bodies = [_normalize_body(r["customer_query_text"]) for r in rows]
    if len(bodies) != len(set(bodies)):
        errors.append("duplicate normalized customer_query_text in CSV")

    sam_rows = sum(1 for r in rows if extract_diag_code(r["customer_query_text"]))
    if not (25 <= sam_rows <= 35):
        errors.append(f"SAM-E row count {sam_rows} outside ~50% band (25–35)")

    by_id = {r["ticket_id"]: r for r in rows}
    eval_lines = [ln for ln in eval_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if len(eval_lines) != 10:
        errors.append(f"expected 10 eval lines, got {len(eval_lines)}")

    gold_ids: list[str] = []
    for i, line in enumerate(eval_lines, start=1):
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as e:
            errors.append(f"eval line {i}: invalid JSON: {e}")
            continue
        for k in _REQUIRED_EVAL_KEYS:
            if k not in obj:
                errors.append(f"eval {obj.get('eval_id', i)}: missing key {k}")
        gid = (obj.get("expected_ticket_ids") or [None])[0]
        src = obj.get("source_ticket_id")
        if gid != src:
            errors.append(f"eval {obj.get('eval_id')}: expected_ticket_ids != source_ticket_id")
        if gid not in by_id:
            errors.append(f"eval {obj.get('eval_id')}: unknown gold {gid}")
            continue
        gold_ids.append(gid)
        gold = by_id[gid]
        if gold["status"] != "resolved":
            errors.append(f"eval {obj.get('eval_id')}: gold {gid} status={gold['status']} (need resolved)")
        q = (obj.get("query") or "").strip()
        if q.strip() == gold["customer_query_text"].strip():
            errors.append(f"eval {obj.get('eval_id')}: verbatim leakage vs gold text")
        if gold["model"] != obj.get("model_filter"):
            errors.append(f"eval {obj.get('eval_id')}: model_filter mismatch")
        lift = obj.get("demo_lift")
        if lift is not None and lift not in _DEMO_LIFT:
            errors.append(f"eval {obj.get('eval_id')}: invalid demo_lift {lift!r}")

    if len(set(gold_ids)) != len(gold_ids):
        errors.append("duplicate gold ticket_ids across eval rows")

    return errors


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--corpus-dir",
        type=Path,
        default=ROOT / "tmp" / "simulated_data",
    )
    args = p.parse_args()
    errs = validate(args.corpus_dir)
    if errs:
        for e in errs:
            print(e, file=sys.stderr)
        sys.exit(1)
    print(f"validate_llm_corpus: OK ({args.corpus_dir})")


if __name__ == "__main__":
    main()
