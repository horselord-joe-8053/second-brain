#!/usr/bin/env python3.12
"""Verify ABC recall@1 ladder on three eval report JSON files (F15)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_REPORT_A = "pg_baseline_v1.json"
_REPORT_B = "pg_ab_v1_1_normal.json"
_REPORT_C = "pg_ab_v1_2_term_boosted.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _recall(report: dict[str, Any]) -> float:
    return float(report["recall_at_1"])


def _stratum_recall(report: dict[str, Any], stratum: str) -> float:
    by = report.get("by_stratum") or {}
    if stratum in by:
        return float(by[stratum])
    for block in report.get("strata") or []:
        if block.get("stratum") == stratum:
            return float(block["recall_at_1"])
    raise KeyError(stratum)


def check_ladder(reports_dir: Path) -> tuple[bool, list[str]]:
    """Return (ok, human messages) after validating F15 rules."""
    msgs: list[str] = []
    a_path = reports_dir / _REPORT_A
    b_path = reports_dir / _REPORT_B
    c_path = reports_dir / _REPORT_C
    for p in (a_path, b_path, c_path):
        if not p.is_file():
            return False, [f"missing report {p}"]
    a, b, c = _load(a_path), _load(b_path), _load(c_path)
    ra, rb, rc = _recall(a), _recall(b), _recall(c)
    msgs.append(f"overall recall@1: A={ra:.3f} B={rb:.3f} C={rc:.3f}")
    ok = True
    if not (ra < rb < rc):
        ok = False
        msgs.append("FAIL: overall A < B < C not strict")
    if int(a.get("total", 0)) != 100:
        ok = False
        msgs.append(f"FAIL: expected total=100, got {a.get('total')}")
    lex = a.get("lexical_backend") or b.get("lexical_backend")
    if lex != "tantivy":
        ok = False
        msgs.append(f"FAIL: lexical_backend must be tantivy, got {lex!r}")
    try:
        h_a = _stratum_recall(a, "hybrid_stress")
        h_b = _stratum_recall(b, "hybrid_stress")
        if not (h_b > h_a):
            ok = False
            msgs.append(f"FAIL: hybrid_stress B > A ({h_b:.3f} vs {h_a:.3f})")
        c_b = _stratum_recall(b, "code_in_query")
        c_c = _stratum_recall(c, "code_in_query")
        if not (c_c > c_b):
            ok = False
            msgs.append(f"FAIL: code_in_query C > B ({c_c:.3f} vs {c_b:.3f})")
        msgs.append(
            f"hybrid_stress: A={h_a:.3f} B={h_b:.3f}; code_in_query: B={c_b:.3f} C={c_c:.3f}"
        )
    except KeyError as e:
        ok = False
        msgs.append(f"FAIL: missing stratum {e}")
    return ok, msgs


def main() -> None:
    p = argparse.ArgumentParser(description="Check ABC recall ladder (F15).")
    p.add_argument("--reports-dir", type=Path, required=True)
    args = p.parse_args()
    ok, msgs = check_ladder(args.reports_dir)
    for line in msgs:
        print(line)
    if not ok:
        sys.exit(1)
    print("ladder OK")


if __name__ == "__main__":
    main()
