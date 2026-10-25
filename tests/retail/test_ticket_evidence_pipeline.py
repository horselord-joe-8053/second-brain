"""Ticket evidence pipeline wires rerank_registry for retriever_rerank mode."""

from __future__ import annotations

from pathlib import Path

from retail_brain.evidence.ticket_evidence_pipeline import build_ticket_evidence_stack

REPO = Path(__file__).resolve().parents[2]


def test_rerank_mode_activates_rank_fn() -> None:
    stack = build_ticket_evidence_stack(
        "postgresql://mock",
        repo_root=REPO,
        mode="retriever_rerank",
        generate_fn=lambda _p: '["T-1"]',
    )
    assert stack.rank_fn_active is True
    assert stack.retriever.rank_fn is not None


def test_retriever_mode_no_rank_fn() -> None:
    stack = build_ticket_evidence_stack(
        "postgresql://mock",
        repo_root=REPO,
        mode="retriever",
    )
    assert stack.rank_fn_active is False
    assert stack.retriever.rank_fn is None
