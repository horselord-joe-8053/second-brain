"""P2.4 — Ticket agentic controller: at most one sub-search."""

from __future__ import annotations

from typing import Any

from retail_brain.evidence.ticket_agentic import TicketAgenticController
from retail_brain.evidence.ticket_retriever import TicketEvidenceRetriever

_CALLS: list[str] = []


def _search(_dsn: str, query: str, *, model_filter: str | None = None, limit: int = 2) -> tuple[str, list[dict[str, Any]]]:
    _CALLS.append(query)
    if len(_CALLS) == 1:
        return ("rrf_term_boosted", [])
    return (
        "rrf_term_boosted",
        [
            {
                "ticket_id": "T-9",
                "model": "GNE27JYMFS",
                "customer_query_text": "FRU-E101 ice maker fault",
                "resolution_text": "Replaced board.",
            },
        ],
    )


def test_agentic_runs_one_subsearch_when_first_pass_empty() -> None:
    """Second retrieve uses subquery; loops == 1."""
    _CALLS.clear()
    retriever = TicketEvidenceRetriever(dsn="postgresql://x", search_fn=_search, top_k=3)
    ctrl = TicketAgenticController(retriever, max_loops=1)
    result = ctrl.retrieve_with_verifier("FRU-E101 ice maker", model_filter="GNE27JYMFS")
    assert result.loops == 1
    assert result.subquery_used == "FRU-E101"
    assert len(_CALLS) == 2
    assert result.verifier.applicable is True


def test_agentic_blocks_second_loop_when_max_zero() -> None:
    """max_loops=0 never calls search twice."""
    _CALLS.clear()

    def once(_dsn: str, _q: str, *, model_filter: str | None = None, limit: int = 2) -> tuple[str, list]:
        _CALLS.append("once")
        return ("vector_only", [])

    retriever = TicketEvidenceRetriever(dsn="postgresql://x", search_fn=once)
    ctrl = TicketAgenticController(retriever, max_loops=0)
    result = ctrl.retrieve_with_verifier("symptom", model_filter="GNE27JYMFS")
    assert result.loops == 0
    assert len(_CALLS) == 1
