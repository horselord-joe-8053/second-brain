"""Ticket applicability checks before suggesting past-case reuse (Phase 2 P2.2)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .types import EvidencePackage

_TOKEN_RE = re.compile(r"[a-z0-9]{3,}", re.IGNORECASE)


@dataclass
class TicketVerifierResult:
    """Whether top ticket evidence is safe to reuse for this query."""

    applicable: bool
    reasons: list[str] = field(default_factory=list)
    escalate: bool = False

    def to_dict(self) -> dict:
        return {
            "applicable": self.applicable,
            "reasons": list(self.reasons),
            "escalate": self.escalate,
        }


def _symptom_terms(query: str, *, model_id: str) -> list[str]:
    skip = set((model_id or "").lower().replace("_", " ").split())
    terms: list[str] = []
    for t in _TOKEN_RE.findall(query):
        low = t.lower()
        if low in skip or len(low) < 3:
            continue
        if low not in terms:
            terms.append(low)
    return terms


def verify_ticket_applicability(package: EvidencePackage, query: str) -> TicketVerifierResult:
    """Check model alignment, symptom overlap, and resolution presence on top hit."""
    if not package.chunks:
        return TicketVerifierResult(
            applicable=False,
            reasons=["no_ticket_hits"],
            escalate=True,
        )
    top = package.chunks[0]
    reasons: list[str] = []
    expected_model = (package.model_id or "").strip()
    if expected_model and top.model_id and top.model_id != expected_model:
        return TicketVerifierResult(
            applicable=False,
            reasons=[f"model_mismatch: top={top.model_id!r} expected={expected_model!r}"],
        )
    text_low = top.text.lower()
    if "resolution:" not in text_low and len(text_low.strip()) < 40:
        return TicketVerifierResult(
            applicable=False,
            reasons=["missing_resolution_text"],
            escalate=True,
        )
    terms = _symptom_terms(query, model_id=package.model_id)
    if terms:
        hit = [t for t in terms if t in text_low]
        if len(hit) < max(1, len(terms) // 3):
            reasons.append("weak_symptom_overlap")
            return TicketVerifierResult(applicable=False, reasons=reasons, escalate=False)
    if "resolution:" not in text_low:
        return TicketVerifierResult(
            applicable=False,
            reasons=["missing_resolution_text"],
            escalate=True,
        )
    return TicketVerifierResult(applicable=True, reasons=["model_ok", "symptom_ok", "resolution_present"])
