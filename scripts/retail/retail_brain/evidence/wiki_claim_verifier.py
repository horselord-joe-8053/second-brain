"""Verify compiled wiki claims against canonical lane-B raw source text."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Literal

ClaimStatus = Literal["supported", "uncertain", "contradicted", "unverified"]

_TOKEN_RE = re.compile(r"[a-z0-9]{3,}", re.IGNORECASE)


@dataclass
class WikiClaimVerdict:
    """Outcome of comparing one atomic claim to quoted source passages."""

    status: ClaimStatus
    source_relpath: str | None = None
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "source_relpath": self.source_relpath,
            "reasons": list(self.reasons),
        }


def _salient_terms(claim: str) -> list[str]:
    terms: list[str] = []
    for t in _TOKEN_RE.findall(claim or ""):
        low = t.lower()
        if low not in terms:
            terms.append(low)
    return terms


def verify_wiki_claim(claim: str, source_texts: dict[str, str]) -> WikiClaimVerdict:
    """Pass when salient claim terms appear in at least one resolved source file."""
    claim = (claim or "").strip()
    if not claim:
        return WikiClaimVerdict(status="unverified", reasons=["empty_claim"])
    if not source_texts:
        return WikiClaimVerdict(status="unverified", reasons=["no_sources"])

    terms = _salient_terms(claim)
    if not terms:
        return WikiClaimVerdict(status="uncertain", reasons=["no_salient_terms"])

    best_path: str | None = None
    best_ratio = 0.0
    norm_claim = " ".join(claim.lower().split())
    for relpath, text in source_texts.items():
        blob = (text or "").lower()
        if norm_claim in blob:
            return WikiClaimVerdict(
                status="supported",
                source_relpath=relpath,
                reasons=["substring_match"],
            )
        hit = sum(1 for t in terms if t in blob)
        ratio = hit / len(terms)
        if ratio > best_ratio:
            best_ratio = ratio
            best_path = relpath

    if best_ratio >= 0.6:
        return WikiClaimVerdict(
            status="supported",
            source_relpath=best_path,
            reasons=[f"term_coverage={best_ratio:.2f}"],
        )
    if best_ratio >= 0.25:
        return WikiClaimVerdict(
            status="uncertain",
            source_relpath=best_path,
            reasons=[f"partial_coverage={best_ratio:.2f}"],
        )
    return WikiClaimVerdict(
        status="unverified",
        source_relpath=best_path,
        reasons=[f"low_coverage={best_ratio:.2f}"],
    )
