"""Contract tests for A/B/C (V1→V1.2) demo eval spec and apply script."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "scripts" / "retail" / "sim_data" / "profiles" / "data_60_10"
SPEC = ROOT / "scripts" / "retail/seed/abcd_demo_eval_spec.py"


def test_abcd_demo_spec_has_ten_unique_golds():
    """Demo ladder spec must define ten distinct gold ticket ids."""
    sys.path.insert(0, str(ROOT / "scripts" / "retail" / "seed"))
    from abcd_demo_eval_spec import ABCD_DEMO_EVAL_ROWS, DEMO_LIFT_MODES

    assert len(ABCD_DEMO_EVAL_ROWS) == 10
    golds = [r["source_ticket_id"] for r in ABCD_DEMO_EVAL_ROWS]
    assert len(set(golds)) == 10
    for r in ABCD_DEMO_EVAL_ROWS:
        assert r["demo_lift"] in DEMO_LIFT_MODES
        assert r["expected_ticket_ids"] == [r["source_ticket_id"]]
    lifts = [r["demo_lift"] for r in ABCD_DEMO_EVAL_ROWS]
    strata = [r["stratum"] for r in ABCD_DEMO_EVAL_ROWS]
    assert lifts.count("rrf_normal") >= 2
    assert lifts.count("rrf_term_boosted") >= 2
    assert strata.count("hybrid_stress") >= 3


def test_apply_abcd_demo_eval_writes_valid_jsonl(tmp_path):
    """Apply script writes JSONL that validate_llm_corpus accepts when CSV is present."""
    if not (CORPUS / "service_queries.csv").is_file():
        return
    import shutil

    work = tmp_path / "sim"
    shutil.copytree(CORPUS, work)
    subprocess.run(
        [sys.executable, str(ROOT / "scripts/retail/seed/apply_abcd_demo_eval.py"), "--corpus-dir", str(work), "--no-archive"],
        check=True,
        cwd=ROOT,
    )
    lines = (work / "ticket_retrieval.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 10
    for line in lines:
        json.loads(line)
    subprocess.run(
        [sys.executable, str(ROOT / "scripts/retail/seed/validate_llm_corpus.py"), "--corpus-dir", str(work)],
        check=True,
        cwd=ROOT,
    )
