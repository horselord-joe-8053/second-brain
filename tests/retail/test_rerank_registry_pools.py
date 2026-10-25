"""Shared rerank_registry — manual vs ticket candidate rows."""

from __future__ import annotations

from retail_brain.rerank_registry import candidate_row_id, candidate_row_snippet


def test_candidate_row_id_prefers_ticket_id() -> None:
    row = {"ticket_id": "T-1", "chunk_id": "c1"}
    assert candidate_row_id(row) == "T-1"


def test_candidate_snippet_from_ticket_fields() -> None:
    row = {
        "ticket_id": "T-1",
        "customer_query_text": "ice maker broken",
        "resolution_text": "reset unit",
    }
    snip = candidate_row_snippet(row)
    assert "ice maker" in snip
    assert "reset unit" in snip
