"""Postgres ticket search adapter — normalized EvidencePackage (Phase 2 P2.1)."""

from __future__ import annotations

import time
from typing import Any, Callable

from retail_brain.pg_search import search_ticket_hits_pg

from .types import EvidenceChunk, EvidencePackage

SearchFn = Callable[..., tuple[str, list[dict[str, Any]]]]


class TicketEvidenceRetriever:
    """Wrap ``search_ticket_hits_pg`` (or injectable search fn) for the evidence stack."""

    def __init__(
        self,
        dsn: str,
        *,
        search_fn: SearchFn | None = None,
        top_k: int = 5,
        rank_fn: Callable[[str, list[dict[str, Any]]], str] | None = None,
    ) -> None:
        self.dsn = dsn
        self._search = search_fn or search_ticket_hits_pg
        self.top_k = top_k
        self.rank_fn = rank_fn

    def retrieve(self, query: str, *, model_filter: str) -> EvidencePackage:
        """Run ticket hybrid search and map hits to EvidencePackage."""
        t0 = time.perf_counter()
        mode, hits = self._search(
            self.dsn,
            query,
            model_filter=model_filter or None,
            limit=self.top_k * 2 if self.rank_fn else self.top_k,
        )
        d5_rerank = False
        if hits and self.rank_fn is not None:
            from retail_brain.rerank import listwise_rerank

            hits = listwise_rerank(
                query,
                hits,
                rank_fn=self.rank_fn,
                max_candidates=self.top_k * 2,
            )[: self.top_k]
            d5_rerank = True
        else:
            hits = hits[: self.top_k]
        chunks = _ticket_hits_to_chunks(hits)
        ms = int((time.perf_counter() - t0) * 1000)
        return EvidencePackage(
            query=query,
            model_id=model_filter,
            mode=mode,
            chunks=chunks,
            latency_ms=ms,
            meta={"search_mode": mode, "hit_count": len(hits), "d5_rerank": d5_rerank},
        )


def _ticket_hits_to_chunks(hits: list[dict[str, Any]]) -> list[EvidenceChunk]:
    """Map pg_search hit dicts into shared EvidenceChunk rows."""
    out: list[EvidenceChunk] = []
    for i, h in enumerate(hits, start=1):
        tid = str(h.get("ticket_id") or "")
        cq = str(h.get("customer_query_text") or "")
        res = str(h.get("resolution_text") or "")
        text = cq if not res else f"{cq}\n\nResolution: {res}"
        scores: dict[str, float] = {}
        if h.get("fused_score") is not None:
            scores["fused_score"] = float(h["fused_score"])
        if h.get("cosine_similarity") is not None:
            scores["cosine_similarity"] = float(h["cosine_similarity"])
        out.append(
            EvidenceChunk(
                chunk_id=tid,
                source_relpath=f"ticket://{tid}",
                model_id=str(h.get("model") or ""),
                text=text,
                rank=i,
                scores=scores,
            )
        )
    return out
