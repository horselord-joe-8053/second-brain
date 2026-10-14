"""FRU eval JSONL contract (100-row ABC mix)."""

import json
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EVAL = REPO / "scripts/retail/sim_data/profiles/fru_us_1000_100/ticket_retrieval.jsonl"
CSV = REPO / "scripts/retail/sim_data/profiles/fru_us_1000_100/service_queries.csv"


def _load_eval() -> list[dict]:
    rows = []
    with EVAL.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def test_fru_eval_strata_and_demo_lift() -> None:
    """50/30/20 strata with matching demo_lift labels."""
    rows = _load_eval()
    assert len(rows) == 100
    strata = Counter(r["stratum"] for r in rows)
    assert strata["paraphrase"] == 50
    assert strata["hybrid_stress"] == 30
    assert strata["code_in_query"] == 20
    lifts = Counter(r.get("demo_lift") for r in rows)
    assert lifts["rrf_normal"] == 80
    assert lifts["rrf_term_boosted"] == 20


def test_fru_eval_no_query_leakage() -> None:
    """Queries must not embed customer ids or ticket ids."""
    import csv

    by_id = {r["ticket_id"]: r for r in csv.DictReader(CSV.open(encoding="utf-8"))}
    for obj in _load_eval():
        q = obj["query"]
        assert "CUST" not in q
        assert "T-0042-" not in q
        assert "ITM-" not in q
        gid = obj["expected_ticket_ids"][0]
        assert q.strip() != by_id[gid]["customer_query_text"].strip()
