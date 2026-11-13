"""Bounded agentic re-search when verifier reports insufficient coverage."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .retriever import ManualEvidenceRetriever
from .types import EvidencePackage
from .verifier import VerifierResult, verify_manual_coverage


@dataclass
class AgenticResult:
    """Final package after optional single subquery loop."""

    package: EvidencePackage
    verifier: VerifierResult
    subquery_used: str | None = None
    loops: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "package": self.package.to_dict(),
            "verifier": self.verifier.to_dict(),
            "subquery_used": self.subquery_used,
            "loops": self.loops,
        }


class AgenticRetrievalController:
    """At most one extra retrieval when manual verifier fails (R4)."""

    def __init__(self, retriever: ManualEvidenceRetriever, *, max_loops: int = 1) -> None:
        self.retriever = retriever
        self.max_loops = max(0, int(max_loops))

    def retrieve_with_verifier(
        self,
        query: str,
        question: str,
        *,
        model_id: str,
        force_reindex: bool = False,
        skip_index_check: bool = False,
    ) -> AgenticResult:
        """Retrieve, verify; optionally one subquery from missing terms."""
        pkg = self.retriever.retrieve(
            query,
            model_id=model_id,
            force_reindex=force_reindex,
            skip_index_check=skip_index_check,
        )
        verdict = verify_manual_coverage(pkg, question)
        loops = 0
        subquery: str | None = None
        if verdict.sufficient or self.max_loops < 1 or not verdict.missing_terms:
            return AgenticResult(package=pkg, verifier=verdict, loops=loops)

        subquery = f"{model_id} " + " ".join(verdict.missing_terms[:3])
        loops = 1
        pkg2 = self.retriever.retrieve(
            subquery,
            model_id=model_id,
            force_reindex=False,
            skip_index_check=True,
        )
        merged = _merge_packages(pkg, pkg2)
        verdict2 = verify_manual_coverage(merged, question)
        return AgenticResult(
            package=merged,
            verifier=verdict2,
            subquery_used=subquery,
            loops=loops,
        )


def _merge_packages(a: EvidencePackage, b: EvidencePackage) -> EvidencePackage:
    """Dedupe chunks by id; preserve order from first then second."""
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
