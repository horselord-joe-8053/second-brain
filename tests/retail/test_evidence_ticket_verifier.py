"""P2.2 — Ticket applicability verifier on frozen-style snippets."""

from __future__ import annotations

from retail_brain.evidence.ticket_verifier import verify_ticket_applicability
from retail_brain.evidence.types import EvidenceChunk, EvidencePackage


def _pkg(chunks: list[EvidenceChunk], *, model_id: str = "GNE27JYMFS") -> EvidencePackage:
    return EvidencePackage(
        query="ice maker not producing cubes",
        model_id=model_id,
        mode="rrf_term_boosted",
        chunks=chunks,
    )


def test_applicable_when_model_symptom_and_resolution_present() -> None:
    """Top hit matches model, symptom overlap, and has resolution text."""
    chunks = [
        EvidenceChunk(
            chunk_id="T-1",
            source_relpath="ticket://T-1",
            model_id="GNE27JYMFS",
            text="Customer: ice maker stopped making cubes\n\nResolution: Reset ice maker.",
            rank=1,
            scores={"fused_score": 0.9},
        ),
    ]
    result = verify_ticket_applicability(_pkg(chunks), "ice maker not producing cubes")
    assert result.applicable is True
    assert not result.escalate


def test_not_applicable_when_model_mismatch() -> None:
    """Wrong SKU on top hit → not applicable."""
    chunks = [
        EvidenceChunk(
            chunk_id="T-2",
            source_relpath="ticket://T-2",
            model_id="KRFF507HPS",
            text="ice maker stopped\n\nResolution: cleared auger",
            rank=1,
            scores={},
        ),
    ]
    result = verify_ticket_applicability(_pkg(chunks), "ice maker not producing cubes")
    assert result.applicable is False
    assert any("model" in r.lower() for r in result.reasons)


def test_escalate_when_no_resolution_on_top_hit() -> None:
    """Symptom match but empty resolution → escalate suggestion."""
    chunks = [
        EvidenceChunk(
            chunk_id="T-3",
            source_relpath="ticket://T-3",
            model_id="GNE27JYMFS",
            text="ice maker not producing cubes",
            rank=1,
            scores={},
        ),
    ]
    result = verify_ticket_applicability(_pkg(chunks), "ice maker not producing cubes")
    assert result.applicable is False
    assert result.escalate is True
