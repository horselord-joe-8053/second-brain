"""D7 outer orchestrator — merge rules (no Postgres)."""

from __future__ import annotations

from retail_brain.query_unit_orchestrator import (
    dedupe_ticket_hits,
    merge_manual_chunk_rows,
    merge_ticket_hits_gated,
    pfda_pick_tickets,
    plan_query_units,
    should_run_decomposed,
)


def test_plan_query_units_splits_on_question_only() -> None:
    """Sentence split applies to customer text without model prefix."""
    q = (
        "Dispenser slowed. What filter should I replace, "
        "and what room temperature range is safe?"
    )
    units = plan_query_units(q)
    assert len(units) >= 2
    assert should_run_decomposed(units)


def test_merge_ticket_hits_gated_per_unit_and_threshold() -> None:
    """Each unit may contribute up to k hits above cosine floor; dedupe globally."""
    unit_a = [
        {"ticket_id": "T-1", "cosine_similarity": 0.5},
        {"ticket_id": "T-2", "cosine_similarity": 0.1},
    ]
    unit_b = [
        {"ticket_id": "T-3", "cosine_similarity": 0.4},
        {"ticket_id": "T-1", "cosine_similarity": 0.35},
    ]
    merged = merge_ticket_hits_gated(
        [unit_a, unit_b], k_per_unit=2, min_cosine=0.28
    )
    ids = [h["ticket_id"] for h in merged]
    assert ids == ["T-1", "T-3"]
    assert "T-2" not in ids


def test_dedupe_ticket_hits_keeps_higher_cosine() -> None:
    """Anchor and decomposed legs may return the same id with different scores."""
    a = [{"ticket_id": "T-1", "cosine_similarity": 0.9}]
    b = [{"ticket_id": "T-1", "cosine_similarity": 0.4}, {"ticket_id": "T-2", "cosine_similarity": 0.5}]
    out = dedupe_ticket_hits(a, b)
    assert [h["ticket_id"] for h in out] == ["T-1", "T-2"]
    t1 = next(h for h in out if h["ticket_id"] == "T-1")
    assert t1["cosine_similarity"] == 0.9


def test_pfda_pick_tickets_listwise_then_top_k() -> None:
    """Listwise rerank on deduped pool; output length capped at k."""

    def mock_rank(_query: str, candidates: list) -> str:
        return '["T-2", "T-1"]'

    pool_a = [
        {"ticket_id": "T-1", "cosine_similarity": 0.9},
        {"ticket_id": "T-3", "cosine_similarity": 0.7},
    ]
    pool_b = [{"ticket_id": "T-2", "cosine_similarity": 0.8}]
    picked, trace = pfda_pick_tickets(
        "full question",
        decomposed_hits=pool_a,
        anchor_hits=pool_b,
        k=2,
        rank_fn=mock_rank,
    )
    assert [h["ticket_id"] for h in picked] == ["T-2", "T-1"]
    assert set(trace["pool_ids"]) == {"T-1", "T-2", "T-3"}
    assert trace["selected_ids"] == ["T-2", "T-1"]


def test_merge_manual_chunk_rows_rrf() -> None:
    """Cross-unit RRF prefers chunks strong in multiple unit lists."""
    u1 = [{"chunk_id": "a", "text": "a"}, {"chunk_id": "b", "text": "b"}]
    u2 = [{"chunk_id": "b", "text": "b"}, {"chunk_id": "c", "text": "c"}]
    out = merge_manual_chunk_rows([u1, u2], top_k=2)
    assert [h["chunk_id"] for h in out] == ["b", "a"]
