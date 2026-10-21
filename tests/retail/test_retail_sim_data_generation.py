"""Generation contracts for sim_data profiles."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "retail"))

PROFILES = ROOT / "scripts" / "retail" / "sim_data" / "profiles"


def test_issue_index_matches_historical_generator():
    """CSV reload uses the same issue index rule as ``generate_historical``."""
    from sim_data.generation.tickets import generate_historical, issue_index_for_ticket_id

    rows = generate_historical(seed=20261014, count=1000)
    for r in rows:
        assert r.issue_index == issue_index_for_ticket_id(r.ticket_id)


def test_data_60_10_frozen_counts():
    """Archived mini profile keeps 60 historical and 10 eval rows."""
    d = PROFILES / "data_60_10"
    rows = list(csv.DictReader((d / "service_queries.csv").open(encoding="utf-8")))
    eval_lines = (d / "ticket_retrieval.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(rows) == 60
    assert len(eval_lines) == 10


def test_eval_only_leaves_historical_csv_bytes_unchanged(tmp_path):
    """``--eval-only`` must not rewrite committed historical tickets."""
    import hashlib
    import subprocess
    import sys

    csv = PROFILES / "data_1000_100" / "service_queries.csv"
    before = hashlib.sha256(csv.read_bytes()).hexdigest()
    subprocess.run(
        [
            sys.executable,
            "-m",
            "sim_data.generation.cli",
            "--profile",
            "data_1000_100",
            "--eval-only",
        ],
        check=True,
        cwd=ROOT / "scripts" / "retail",
        env={**dict(__import__("os").environ), "PYTHONPATH": str(ROOT / "scripts" / "retail")},
    )
    after = hashlib.sha256(csv.read_bytes()).hexdigest()
    assert before == after


def test_data_1000_100_scale_counts():
    """Scale profile has 1000 historical and 100 ABC eval rows."""
    d = PROFILES / "data_1000_100"
    rows = list(csv.DictReader((d / "service_queries.csv").open(encoding="utf-8")))
    eval_lines = (d / "ticket_retrieval.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(rows) == 1000
    assert len(eval_lines) == 100
    lifts = [json.loads(ln)["demo_lift"] for ln in eval_lines]
    assert lifts.count("vector_only") == 50
    assert lifts.count("rrf_normal") == 30
    assert lifts.count("rrf_term_boosted") == 20


def test_abc_eval_hybrid_gold_matches_teaching_pairs():
    """Hybrid rows use catalog bait→gold issue indices on low-collision tickets."""
    from sim_data.generation.catalog import HYBRID_GOLD_BY_BAIT_IDX
    from sim_data.generation.eval_abc import generate_abc_eval
    from sim_data.generation.tickets import generate_historical

    rows = generate_historical(seed=20261014, count=1000)
    eval_rows = generate_abc_eval(rows, seed=20261014, n_paraphrase=50, n_hybrid=30, n_code=20)
    hybrid = [r for r in eval_rows if r["stratum"] == "hybrid_stress"]
    assert len(hybrid) == 30
    by_id = {r.ticket_id: r for r in rows}
    gold_issue_idxs = {pair[1] for pair in HYBRID_GOLD_BY_BAIT_IDX}
    for i, er in enumerate(hybrid):
        gold = by_id[er["source_ticket_id"]]
        _, expected_gold_idx = HYBRID_GOLD_BY_BAIT_IDX[i % len(HYBRID_GOLD_BY_BAIT_IDX)]
        assert gold.issue_index == expected_gold_idx
        assert gold.issue_index in gold_issue_idxs


def test_abc_eval_gold_signatures_prefer_rare():
    """Eval gold tickets are not all drawn from the most common model/city/issue bucket."""
    from sim_data.generation.eval_abc import generate_abc_eval
    from sim_data.generation.eval_gold import build_rich_signature_counts, rich_signature
    from sim_data.generation.tickets import generate_historical

    rows = generate_historical(seed=20261014, count=1000)
    resolved = [r for r in rows if r.status == "resolved"]
    rich_counts = build_rich_signature_counts(resolved)
    eval_rows = generate_abc_eval(rows, seed=20261014, n_paraphrase=50, n_hybrid=30, n_code=20)
    by_id = {r.ticket_id: r for r in rows}
    for er in eval_rows:
        gold = by_id[er["source_ticket_id"]]
        cap = 2 if er["stratum"] in ("hybrid_stress", "code_in_query") else 1
        assert rich_counts[rich_signature(gold)] <= cap
