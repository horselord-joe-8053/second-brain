"""Coverage-style verifier for manual evidence packages."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from .types import EvidencePackage

_TOKEN_RE = re.compile(r"[a-z0-9]{3,}", re.IGNORECASE)


@dataclass
class VerifierResult:
    """Whether retrieved chunks cover salient query terms."""

    sufficient: bool
    missing_terms: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "sufficient": self.sufficient,
            "missing_terms": list(self.missing_terms),
            "reasons": list(self.reasons),
        }


def _salient_terms(question: str, *, model_id: str) -> list[str]:
    """Question tokens minus model id noise."""
    skip = set((model_id or "").lower().replace("_", " ").split())
    terms: list[str] = []
    for t in _TOKEN_RE.findall(question):
        low = t.lower()
        if low in skip or len(low) < 3:
            continue
        if low not in terms:
            terms.append(low)
    return terms


def verify_manual_coverage(
    package: EvidencePackage,
    question: str,
    *,
    min_term_coverage: float = 0.5,
) -> VerifierResult:
    """Pass when enough salient question terms appear in top chunk text."""
    terms = _salient_terms(question, model_id=package.model_id)
    if not terms:
        return VerifierResult(sufficient=True, reasons=["no_salient_terms"])
    if not package.chunks:
        return VerifierResult(
            sufficient=False,
            missing_terms=terms,
            reasons=["no_chunks"],
        )
    blob = " ".join(c.text.lower() for c in package.chunks[:5])
    hit = [t for t in terms if t in blob]
    missing = [t for t in terms if t not in blob]
    ratio = len(hit) / len(terms)
    ok = ratio >= min_term_coverage
    reasons = [f"coverage={ratio:.2f}"]
    if not ok:
        reasons.append("missing_terms")
    return VerifierResult(sufficient=ok, missing_terms=missing, reasons=reasons)
