"""Manual-lane EvidenceRetriever — wraps raw vector / hybrid harness search."""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any, Callable

REPO = Path(__file__).resolve().parents[4]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tests.retail_multi_profiles.lib.lanes import Lane  # noqa: E402
from tests.retail_multi_profiles.lib.raw_hybrid_search import hybrid_rrf_search  # noqa: E402
from tests.retail_multi_profiles.lib.raw_rag_search import (  # noqa: E402
    retrieve_raw_context,
)

from .types import EvidenceChunk, EvidencePackage

RankFn = Callable[[str, list[dict[str, Any]]], str]


class ManualEvidenceRetriever:
    """Retrieve manual raw chunks for a lane using harness index + modes."""

    def __init__(
        self,
        lane: Lane,
        *,
        embed_cfg: dict[str, Any],
        mode: str = "vector",
        top_k: int = 5,
        page_prefix_chars: int = 8000,
        rank_fn: RankFn | None = None,
        embed_fn: Any | None = None,
    ) -> None:
        self.lane = lane
        self.embed_cfg = embed_cfg
        self.mode = mode
        self.top_k = top_k
        self.page_prefix_chars = page_prefix_chars
        self.rank_fn = rank_fn
        self.embed_fn = embed_fn

    def retrieve(
        self,
        query: str,
        *,
        model_id: str,
        force_reindex: bool = False,
        skip_index_check: bool = False,
    ) -> EvidencePackage:
        """Run configured retrieval mode and normalize to EvidencePackage."""
        t0 = time.perf_counter()
        # D3 hybrid RRF — D5 listwise rerank runs only when rank_fn is wired (not mode name).
        if self.mode in ("hybrid_rrf", "hybrid_rrf_rerank"):
            hits = hybrid_rrf_search(
                self.lane,
                query,
                model_id=model_id,
                embed_cfg=self.embed_cfg,
                top_k=self.top_k,
                embed_fn=self.embed_fn,
                force_reindex=force_reindex,
                skip_index_check=skip_index_check,
            )
            if hits and self.rank_fn is not None:
                from retail_brain.rerank import listwise_rerank

                hits = listwise_rerank(query, hits, rank_fn=self.rank_fn, max_candidates=self.top_k)
            chunks = _hits_to_chunks(hits)
            ms = int((time.perf_counter() - t0) * 1000)
            pkg_mode = "hybrid_rrf" if self.mode == "hybrid_rrf_rerank" else self.mode
            return EvidencePackage(
                query=query,
                model_id=model_id,
                mode=pkg_mode,
                chunks=chunks,
                latency_ms=ms,
                meta={"hit_count": len(hits), "d5_rerank": self.rank_fn is not None},
            )

        hits, _ctx, ms = retrieve_raw_context(
            self.lane,
            query,
            embed_cfg=self.embed_cfg,
            top_k=self.top_k,
            page_prefix_chars=self.page_prefix_chars,
            force_reindex=force_reindex,
            skip_index_check=skip_index_check,
            embed_fn=self.embed_fn,
            model_id=model_id,
        )
        return EvidencePackage(
            query=query,
            model_id=model_id,
            mode="vector",
            chunks=_hits_to_chunks(hits),
            latency_ms=ms,
            meta={"hit_count": len(hits)},
        )


def _hits_to_chunks(hits: list[dict[str, Any]]) -> list[EvidenceChunk]:
    out: list[EvidenceChunk] = []
    for i, h in enumerate(hits, start=1):
        scores = {}
        for key in ("distance", "vector_score", "rrf_score"):
            if h.get(key) is not None:
                scores[key] = float(h[key])
        out.append(
            EvidenceChunk(
                chunk_id=str(h.get("chunk_id") or ""),
                source_relpath=str(h.get("source_relpath") or ""),
                model_id=str(h.get("model_id") or ""),
                text=str(h.get("text") or ""),
                rank=i,
                scores=scores,
            )
        )
    return out
