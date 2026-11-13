"""Manual rerank probe contracts: 20-hit pool, keep 5, union vs merge."""

from __future__ import annotations

import json


def _pool() -> list[dict[str, str]]:
    """Twenty chunk rows; index 11 is fused rank 12."""
    return [{"chunk_id": f"c{i:02d}", "text": f"chunk {i}"} for i in range(1, 21)]


def test_cross_encoder_promotes_rank_12_into_top_5() -> None:
    """A fake pair-scorer moves the rank-12 id to the front of the kept five."""
    from retail_brain.rerank import cross_encoder_rerank

    pool = _pool()
    gold = pool[11]["chunk_id"]

    def score_fn(query: str, rows: list[dict[str, str]]) -> list[float]:
        return [10.0 if row["chunk_id"] == gold else 0.0 for row in rows]

    ordered = cross_encoder_rerank("ambient range", pool, score_fn=score_fn)
    top5 = [row["chunk_id"] for row in ordered[:5]]
    assert ordered[0]["chunk_id"] == gold
    assert gold in top5


def test_listwise_rank_fn_promotes_rank_12_into_top_5() -> None:
    """A fake listwise rank_fn promotes rank 12 and the trace keeps pre and post ids."""
    from retail_brain.rerank import rerank_manual_candidates

    pool = _pool()
    gold = pool[11]["chunk_id"]

    def rank_fn(query: str, cands: list[dict[str, str]]) -> str:
        ids = [row["chunk_id"] for row in cands]
        return json.dumps([gold] + [cid for cid in ids if cid != gold])

    kept, meta = rerank_manual_candidates(
        "ambient range",
        pool,
        backend="llm_listwise",
        keep=5,
        rank_fn=rank_fn,
        model_id="gpt-4o-mini",
    )
    assert [row["chunk_id"] for row in kept][0] == gold
    assert len(kept) == 5
    assert meta["pre_rerank_chunk_ids"][11] == gold
    assert meta["post_rerank_chunk_ids"][0] == gold
    assert meta["rerank_backend"] == "llm_listwise"
    assert meta["rerank_model"] == "gpt-4o-mini"
    assert meta["candidate_count"] == 20
    assert isinstance(meta["rerank_ms"], int)


def test_no_manual_rerank_merges_to_top_k() -> None:
    """Rows without manual_rerank still RRF-merge down to top_k."""
    from retail_brain.query_unit_orchestrator import select_manual_packet

    unit_a = [{"chunk_id": f"a{i}"} for i in range(5)]
    unit_b = [{"chunk_id": f"b{i}"} for i in range(5)]
    merged = select_manual_packet([unit_a, unit_b], manual_rerank="", top_k=5)
    assert len(merged) == 5


def test_manual_rerank_unions_each_units_top() -> None:
    """A rerank arm keeps each unit's five instead of one global five."""
    from retail_brain.query_unit_orchestrator import select_manual_packet

    unit_a = [{"chunk_id": f"a{i}"} for i in range(5)]
    unit_b = [{"chunk_id": f"b{i}"} for i in range(5)]
    packet = select_manual_packet([unit_a, unit_b], manual_rerank="cross_encoder", top_k=5)
    ids = [row["chunk_id"] for row in packet]
    assert ids == [f"a{i}" for i in range(5)] + [f"b{i}" for i in range(5)]


def test_probe_keeps_two_chunks_and_10000_char_budget() -> None:
    """Rerank arms keep two chunks per subquery and a 10000-character manual budget."""
    from retail_brain.rerank import MANUAL_RERANK_CONTEXT_CHARS, MANUAL_RERANK_KEEP

    assert MANUAL_RERANK_KEEP == 2
    assert MANUAL_RERANK_CONTEXT_CHARS == 10000


def test_preflight_allows_cross_encoder_when_rank_fn_present() -> None:
    """D5 preflight accepts cross_encoder once a rank_fn exists."""
    from tests.retail_multi_profiles.lib.resolved_run_profile import (
        ResolvedRunProfile,
        assert_rerank_preflight,
    )

    resolved = ResolvedRunProfile(
        profile_id="t",
        retrieval_mode="raw_rag",
        d3_engine="hybrid_rrf",
        lane_ids=["B"],
        d5_rerank_enabled=True,
        d5_rerank_backend="cross_encoder",
    )
    assert_rerank_preflight(resolved, lambda query, rows: "[]")
