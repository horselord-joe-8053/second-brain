"""Answer-bundle E2E, CI tier (P16): FRU 1k corpus + committed ``.txt`` + fixture wiki."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pytest

pytestmark = pytest.mark.retail_answer_integration

from retail_brain.answer_bundle import build_answer_bundle, bundle_to_json
from retail_brain.answer_manuals import FixtureWikiClient
from retail_brain.answer_tickets import InMemoryTicketSource, load_issue_keys
from retail_brain.company_profile import load_company_profile
from retail_brain.ticket_store import load_ticket_rows
from retail_brain.txt_docs import cached_txt_docs

REPO = Path(__file__).resolve().parents[1]
PROFILE = REPO / "scripts" / "retail" / "sim_data" / "profiles" / "fru_us_1000_100"
GOLD = PROFILE / "answer_e2e.jsonl"
WIKI_FIXTURES = REPO / "tests" / "fixtures" / "retail_wiki"
MANUAL_GOLD_FLOOR = 0.85


@pytest.fixture(autouse=True)
def _cached_embed_stub(monkeypatch: pytest.MonkeyPatch) -> None:
    """Memoize the conftest hash stub: 1k tickets × 32 queries would otherwise re-hash ~32k texts."""
    import retail_brain.hybrid_search as hs

    stub = hs.embed_text
    cache: dict = {}

    def cached(text: str, *, task_type: str = "RETRIEVAL_DOCUMENT") -> list[float]:
        key = (text, task_type)
        if key not in cache:
            cache[key] = stub(text, task_type=task_type)
        return cache[key]

    monkeypatch.setattr(hs, "embed_text", cached)


def manual_gold_hit(bundle: dict, row: dict, profile) -> bool:
    """Manual hit cites one of the expected ``.txt`` docs (doc-level gold, P16)."""
    del profile  # reserved for anchor-tightened gold later (Phase 2)
    if not row.get("expected_manual_docs"):
        return not bundle["manuals"]["hits"]
    expected = {d["doc_path"] for d in row["expected_manual_docs"]}
    return any(h["raw_origin"].get("doc_path") in expected for h in bundle["manuals"]["hits"])


def _gold_rows() -> list[dict]:
    """Gold rows from ``build_answer_e2e.py``."""
    return [json.loads(line) for line in GOLD.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_gold_file_shape() -> None:
    """~30 rows across all strata incl. no-prior-ticket; manual expectations under the row's SKU."""
    rows = _gold_rows()
    assert 25 <= len(rows) <= 40
    assert {r["stratum"] for r in rows} == {"paraphrase", "hybrid_stress", "code_in_query", "no_prior_ticket"}
    for r in rows:
        for m in r.get("expected_manual_docs", []):
            assert m["doc_path"].startswith(f"raw/sources/fridge-docs/{r['model_sku']}/"), r["eval_id"]
        assert bool(r["expected_ticket_ids"]) == (r["stratum"] != "no_prior_ticket")


def test_answer_e2e_ci_tier(monkeypatch: pytest.MonkeyPatch) -> None:
    """Every gold row yields a contract-valid bundle; manual gold rate ≥ floor; no false prior fixes."""
    monkeypatch.setenv("RETAIL_TICKET_SEARCH_MODE", "rrf_term_boosted")
    monkeypatch.setenv("RETAIL_FAULT_CODE_PREFIX", "FRU-E")
    profile = load_company_profile()
    source = InMemoryTicketSource(
        load_ticket_rows(PROFILE / "service_queries.csv"),
        load_issue_keys(PROFILE / "ticket_manifest.jsonl"),
    )
    index = cached_txt_docs(str(REPO / "brain" / "retail"))
    wiki = FixtureWikiClient.from_dir(WIKI_FIXTURES)
    hits, scored, wiki_sourced, problems = Counter(), Counter(), 0, []
    for row in _gold_rows():
        b = build_answer_bundle(
            row["query"],
            ticket_source=source,
            txt_index=index,
            wiki=wiki,
            model=row["model"],
        )
        eid = row["eval_id"]
        if not (b["diagnostics"]["ticket_leg_ok"] and b["diagnostics"]["manual_leg_ok"]):
            problems.append(f"{eid}: leg failed {b['diagnostics']['notes']}")
        if b["model_sku"] != row["model_sku"]:
            problems.append(f"{eid}: model_sku {b['model_sku']}")
        t = b["tickets"]["hits"]
        if not 1 <= len(t) <= 2 or any(h["model"] != row["model"] for h in t):
            problems.append(f"{eid}: ticket hits {[(h['ticket_id'], h['model']) for h in t]}")
        if row["stratum"] == "no_prior_ticket" and any(h["issue_key"] == row["issue_key"] for h in t):
            problems.append(f"{eid}: claims a prior {row['issue_key']} ticket that cannot exist")
        for h in b["manuals"]["hits"]:
            o = h["raw_origin"]
            doc = o.get("doc_path")
            if not doc or not doc.startswith(f"raw/sources/fridge-docs/{row['model_sku']}/"):
                problems.append(f"{eid}: bad raw_origin {o}")
            wiki_sourced += h["source"] == "wiki"
        if row.get("expected_manual_docs"):
            scored[row["stratum"]] += 1
            hits[row["stratum"]] += manual_gold_hit(b, row, profile)
    rate = sum(hits.values()) / sum(scored.values()) if scored else 1.0
    summary = {s: f"{hits[s]}/{scored[s]}" for s in sorted(scored)}
    assert not problems, problems
    assert rate >= MANUAL_GOLD_FLOOR, (rate, summary)
    assert hits["paraphrase"] == scored["paraphrase"], summary
    assert wiki_sourced > 0, "fixture wiki never answered — wiki → doc mapping untested"


def test_answer_e2e_bundle_is_byte_stable(monkeypatch: pytest.MonkeyPatch) -> None:
    """Same gold row twice → byte-identical JSON over the real corpus and txt index."""
    monkeypatch.setenv("RETAIL_TICKET_SEARCH_MODE", "rrf_term_boosted")
    rows = load_ticket_rows(PROFILE / "service_queries.csv")
    row = _gold_rows()[0]
    kw = dict(
        txt_index=cached_txt_docs(str(REPO / "brain" / "retail")),
        wiki=FixtureWikiClient.from_dir(WIKI_FIXTURES),
        model=row["model"],
    )
    a = bundle_to_json(build_answer_bundle(row["query"], ticket_source=InMemoryTicketSource(rows), **kw))
    b = bundle_to_json(build_answer_bundle(row["query"], ticket_source=InMemoryTicketSource(rows), **kw))
    assert a == b
