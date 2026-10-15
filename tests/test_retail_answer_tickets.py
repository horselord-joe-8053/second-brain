"""Ticket leg of the retail answer bundle (brain-profiles P5): real scores, top-2, resolved only."""

from __future__ import annotations

import pytest

import retail_brain.embeddings as emb_mod
from retail_brain.answer_tickets import InMemoryTicketSource, ticket_leg
from retail_brain.embeddings import cosine_distance
from retail_brain.hybrid_search import TicketRow, search_ticket_scored
from retail_brain.text_normalize import text_for_embedding

ROWS = [
    TicketRow("T-1", "GNE27JYMFS", "resolved", "ice maker stopped producing cubes FRU-E101", "Reset ice maker."),
    TicketRow("T-2", "GNE27JYMFS", "resolved", "water dispenser runs very slowly", "Replaced filter."),
    TicketRow("T-3", "GNE27JYMFS", "received", "ice maker stopped producing cubes", ""),
    TicketRow("T-4", "KRFF507HPS", "resolved", "ice maker stopped producing cubes", "Cleared auger."),
    TicketRow("T-5", "GNE27JYMFS", "resolved", "freezer not staying cold", "Replaced fan."),
]
ISSUES = {"T-1": "ice_maker_no_ice", "T-2": "water_dispenser_slow"}


@pytest.fixture(params=["vector_only", "rrf_normal", "rrf_term_boosted"])
def mode(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> str:
    """Run each contract under all three ticket search modes."""
    monkeypatch.setenv("RETAIL_TICKET_SEARCH_MODE", request.param)
    return request.param


def test_ticket_leg_top2_resolved_and_model_scoped(mode: str) -> None:
    """≤2 hits, ranks 1..n, resolved only, all from the requested model."""
    leg = ticket_leg("ice maker stopped producing cubes", InMemoryTicketSource(ROWS, ISSUES), model="GNE27JYMFS")
    assert leg["search_mode"] == mode
    hits = leg["hits"]
    assert 1 <= len(hits) <= 2
    assert [h["rank"] for h in hits] == list(range(1, len(hits) + 1))
    assert {h["ticket_id"] for h in hits} <= {"T-1", "T-2", "T-5"}
    assert all(h["model"] == "GNE27JYMFS" for h in hits)


def test_cosine_is_real_not_stub(mode: str) -> None:
    """cosine_similarity equals 1 - cosine_distance(query, ticket) (rounded 4 dp)."""
    q = "ice maker stopped producing cubes"
    leg = ticket_leg(q, InMemoryTicketSource(ROWS, ISSUES), model="GNE27JYMFS")
    by_id = {r.ticket_id: r for r in ROWS}
    q_emb = emb_mod.embed_text(q, task_type="RETRIEVAL_QUERY")
    for h in leg["hits"]:
        d_emb = emb_mod.embed_text(text_for_embedding(by_id[h["ticket_id"]].customer_query_text))
        assert h["cosine_similarity"] == round(1.0 - cosine_distance(q_emb, d_emb), 4)
    if mode == "vector_only":
        assert all(h["fused_score"] is None for h in leg["hits"])
        sims = [h["cosine_similarity"] for h in leg["hits"]]
        assert sims == sorted(sims, reverse=True)
    else:
        assert all(isinstance(h["fused_score"], float) and h["fused_score"] > 0 for h in leg["hits"])


def test_ticket_leg_hydrates_fields_and_is_deterministic(mode: str) -> None:
    """Hits carry text + issue_key; two calls give identical output."""
    src = InMemoryTicketSource(ROWS, ISSUES)
    a = ticket_leg("FRU-E101 ice maker", src, model="GNE27JYMFS")
    b = ticket_leg("FRU-E101 ice maker", src, model="GNE27JYMFS")
    assert a == b
    top = a["hits"][0]
    assert set(top) == {
        "rank", "ticket_id", "cosine_similarity", "fused_score", "model", "issue_key",
        "customer_query_text", "resolution_text",
    }
    if top["ticket_id"] in ISSUES:
        assert top["issue_key"] == ISSUES[top["ticket_id"]]


def test_search_ticket_scored_matches_id_order(mode: str) -> None:
    """Scored search keeps the legacy id order used by the eval harness."""
    from retail_brain.hybrid_search import search_ticket_ids

    scored = search_ticket_scored("ice maker", ROWS, model_filter="GNE27JYMFS", limit=3)
    assert [tid for tid, _ in scored] == search_ticket_ids("ice maker", ROWS, model_filter="GNE27JYMFS", limit=3)


def test_sidecar_semantic_search_reports_real_distance() -> None:
    """Sidecar no longer returns the constant 0.2 distance stub."""
    from retail_brain.sidecar_logic import semantic_search

    out = semantic_search(ROWS, query_text="ice maker stopped producing cubes", model_filter="GNE27JYMFS",
                          similarity_threshold=2.0)
    assert out["rows"]
    assert all(r["distance"] != 0.2 for r in out["rows"])
    assert all(0.0 <= r["distance"] <= 2.0 for r in out["rows"])
