"""P1.2 — listwise rerank stable ordering with mock LLM."""

from __future__ import annotations

from retail_brain.rerank import listwise_rerank


def test_listwise_rerank_reorders_by_mock_llm() -> None:
    """hybrid_rrf_rerank path uses reranker to promote second candidate."""
    candidates = [
        {"chunk_id": "aaa", "text": "first"},
        {"chunk_id": "bbb", "text": "second"},
        {"chunk_id": "ccc", "text": "third"},
    ]

    def mock_rank(_query: str, rows: list) -> str:
        return '["bbb", "ccc", "aaa"]'

    out = listwise_rerank("ice maker", candidates, rank_fn=mock_rank)
    assert [r["chunk_id"] for r in out] == ["bbb", "ccc", "aaa"]
