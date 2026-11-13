"""Unit tests for ABC ladder checker (F15)."""

import json
from pathlib import Path

from eval.check_abc_ladder import check_ladder


def _report(recall: float, *, hybrid: float | None = None, code: float | None = None) -> dict:
    by_stratum: dict[str, float] = {}
    if hybrid is not None:
        by_stratum["hybrid_stress"] = hybrid
    if code is not None:
        by_stratum["code_in_query"] = code
    return {
        "recall_at_1": recall,
        "total": 100,
        "lexical_backend": "tantivy",
        "by_stratum": by_stratum,
    }


def test_ladder_passes(tmp_path: Path) -> None:
    d = tmp_path
    (d / "pg_baseline_v1.json").write_text(json.dumps(_report(0.27, hybrid=0.20)), encoding="utf-8")
    (d / "pg_ab_v1_1_normal.json").write_text(
        json.dumps(_report(0.39, hybrid=0.35, code=0.25)), encoding="utf-8"
    )
    (d / "pg_ab_v1_2_term_boosted.json").write_text(
        json.dumps(_report(0.58, hybrid=0.35, code=0.55)), encoding="utf-8"
    )
    ok, _ = check_ladder(d)
    assert ok


def test_ladder_fails_overall_order(tmp_path: Path) -> None:
    d = tmp_path
    (d / "pg_baseline_v1.json").write_text(json.dumps(_report(0.50)), encoding="utf-8")
    (d / "pg_ab_v1_1_normal.json").write_text(json.dumps(_report(0.40)), encoding="utf-8")
    (d / "pg_ab_v1_2_term_boosted.json").write_text(json.dumps(_report(0.60)), encoding="utf-8")
    ok, msgs = check_ladder(d)
    assert not ok
    assert any("A < B < C" in m for m in msgs)
