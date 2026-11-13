"""P2.1 — TicketEvidenceRetriever wraps pg_search into EvidencePackage (mocked PG)."""

from __future__ import annotations

import os
from typing import Any

import pytest

from retail_brain.evidence.ticket_retriever import TicketEvidenceRetriever


def _fake_search(
    _dsn: str,
    query: str,
    *,
    model_filter: str | None = None,
    limit: int = 2,
) -> tuple[str, list[dict[str, Any]]]:
    assert model_filter == "GNE27JYMFS"
    assert limit == 5
    return (
        "rrf_term_boosted",
        [
            {
                "ticket_id": "T-100",
                "model": "GNE27JYMFS",
                "customer_query_text": "ice maker not making cubes",
                "resolution_text": "Reset ice maker.",
                "fused_score": 0.91,
                "cosine_similarity": 0.88,
            },
        ],
    )


def test_ticket_retriever_maps_pg_hits_to_evidence_package() -> None:
    """Search fn output becomes ranked EvidenceChunks with ticket meta."""
    retriever = TicketEvidenceRetriever(
        dsn="postgresql://test",
        search_fn=_fake_search,
        top_k=5,
    )
    pkg = retriever.retrieve("ice maker cubes", model_filter="GNE27JYMFS")
    assert pkg.mode == "rrf_term_boosted"
    assert pkg.model_id == "GNE27JYMFS"
    assert len(pkg.chunks) == 1
    ch = pkg.chunks[0]
    assert ch.chunk_id == "T-100"
    assert ch.model_id == "GNE27JYMFS"
    assert "Reset ice maker" in ch.text
    assert ch.rank == 1
    assert ch.scores.get("fused_score") == pytest.approx(0.91)
    assert ch.scores.get("cosine_similarity") == pytest.approx(0.88)
    assert pkg.meta.get("search_mode") == "rrf_term_boosted"


def test_ticket_retriever_listwise_rerank_reorders() -> None:
    """P2.3 — mock rank_fn flips top-2 ticket ids."""

    def search(_dsn: str, _q: str, *, model_filter: str | None = None, limit: int = 2) -> tuple[str, list]:
        return (
            "rrf_term_boosted",
            [
                {"ticket_id": "T-A", "model": "GNE27JYMFS", "customer_query_text": "a", "resolution_text": "r1"},
                {"ticket_id": "T-B", "model": "GNE27JYMFS", "customer_query_text": "b", "resolution_text": "r2"},
            ],
        )

    def rank_fn(_q: str, pool: list) -> str:
        return '["T-B", "T-A"]'

    retriever = TicketEvidenceRetriever(
        dsn="postgresql://test",
        search_fn=search,
        top_k=2,
        rank_fn=rank_fn,
    )
    pkg = retriever.retrieve("ice", model_filter="GNE27JYMFS")
    assert [c.chunk_id for c in pkg.chunks] == ["T-B", "T-A"]
    assert pkg.meta.get("d5_rerank") is True


@pytest.mark.skipif(not os.environ.get("RETAIL_DATABASE_URL"), reason="optional live Postgres (R24)")
def test_ticket_retriever_live_postgres_smoke() -> None:
    """One retrieve against real FRU DB when RETAIL_DATABASE_URL is set."""
    retriever = TicketEvidenceRetriever(dsn=os.environ["RETAIL_DATABASE_URL"], top_k=2)
    pkg = retriever.retrieve("ice maker not making ice", model_filter="GNE27JYMFS")
    assert pkg.mode
    assert isinstance(pkg.chunks, list)


def test_ticket_retriever_empty_hits() -> None:
    """Empty PG result yields empty chunks, not an error."""

    def empty(_dsn: str, _q: str, *, model_filter: str | None = None, limit: int = 2) -> tuple[str, list]:
        return ("vector_only", [])

    retriever = TicketEvidenceRetriever(dsn="postgresql://test", search_fn=empty)
    pkg = retriever.retrieve("anything", model_filter="GNE27JYMFS")
    assert pkg.chunks == []
    assert pkg.mode == "vector_only"
