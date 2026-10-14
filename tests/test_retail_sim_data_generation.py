"""Generation contracts for sim_data profiles."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "retail"))

PROFILES = ROOT / "scripts" / "retail" / "sim_data" / "profiles"


def test_data_60_10_frozen_counts():
    """Archived mini profile keeps 60 historical and 10 eval rows."""
    d = PROFILES / "data_60_10"
    rows = list(csv.DictReader((d / "service_queries.csv").open(encoding="utf-8")))
    eval_lines = (d / "ticket_retrieval.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(rows) == 60
    assert len(eval_lines) == 10


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
