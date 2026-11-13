"""Bounded ticket re-search when applicability verifier fails (Phase 2 P2.4)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .ticket_retriever import TicketEvidenceRetriever
from .ticket_verifier import TicketVerifierResult, verify_ticket_applicability
from .types import EvidencePackage

_FRU_RE = re.compile(r"FRU-E\d{3,4}", re.IGNORECASE)


@dataclass
class TicketAgenticResult:
    """Ticket retrieval after optional single sub-search."""

    package: EvidencePackage
    verifier: TicketVerifierResult
    subquery_used: str | None = None
    loops: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "package": self.package.to_dict(),
            "verifier": self.verifier.to_dict(),
            "subquery_used": self.subquery_used,
            "loops": self.loops,
        }


class TicketAgenticController:
    """At most one extra ticket search when top hit is not applicable (R4)."""

    def __init__(self, retriever: TicketEvidenceRetriever, *, max_loops: int = 1) -> None:
        self.retriever = retriever
        self.max_loops = max(0, int(max_loops))

    def retrieve_with_verifier(self, query: str, *, model_filter: str) -> TicketAgenticResult:
        """Retrieve tickets, verify applicability; optionally one subquery."""
        pkg = self.retriever.retrieve(query, model_filter=model_filter)
        verdict = verify_ticket_applicability(pkg, query)
        if verdict.applicable or self.max_loops < 1:
            return TicketAgenticResult(package=pkg, verifier=verdict, loops=0)

        subquery = _ticket_subquery(query, pkg)
        if not subquery or subquery.strip() == query.strip():
            return TicketAgenticResult(package=pkg, verifier=verdict, loops=0)

        pkg2 = self.retriever.retrieve(subquery, model_filter=model_filter)
        merged = _merge_ticket_packages(pkg, pkg2)
        verdict2 = verify_ticket_applicability(merged, query)
        return TicketAgenticResult(
            package=merged,
            verifier=verdict2,
            subquery_used=subquery,
            loops=1,
        )


def _ticket_subquery(query: str, package: EvidencePackage) -> str:
    """Prefer FRU code in query; else append model id for a narrower symptom search."""
    m = _FRU_RE.search(query)
    if m:
        return m.group(0).upper()
    return f"{package.model_id} {query}".strip()


def _merge_ticket_packages(a: EvidencePackage, b: EvidencePackage) -> EvidencePackage:
    """Dedupe ticket chunks by id; preserve first-seen order."""
    seen: set[str] = set()
    chunks = []
    for c in a.chunks + b.chunks:
        if c.chunk_id in seen:
            continue
        seen.add(c.chunk_id)
        chunks.append(c)
    for i, c in enumerate(chunks, start=1):
        c.rank = i
    return EvidencePackage(
        query=a.query,
        model_id=a.model_id,
        mode=a.mode,
        chunks=chunks,
        latency_ms=a.latency_ms + b.latency_ms,
        meta={**a.meta, "merged": True},
    )
