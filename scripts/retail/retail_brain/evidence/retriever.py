"""Manual-lane EvidenceRetriever — Postgres manual_chunks (D3 vector / hybrid RRF)."""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any, Callable

REPO = Path(__file__).resolve().parents[4]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tests.retail_multi_profiles.lib.lanes import Lane  # noqa: E402
from retail_brain.manual_pg_search import (  # noqa: E402
    hybrid_pg_rrf_search,
    vector_pg_search,
)
from retail_brain.product_scope import ProductFilter, resolve_product_scope  # noqa: E402

from .types import EvidenceChunk, EvidencePackage

RankFn = Callable[[str, list[dict[str, Any]]], str]


class ManualEvidenceRetriever:
    """Retrieve manual raw chunks for a lane from Postgres manual_chunks."""

    def __init__(
        self,
        lane: Lane,
        *,
        embed_cfg: dict[str, Any],
        mode: str = "vector",
        top_k: int = 5,
        page_prefix_chars: int = 8000,
        max_chars_per_chunk: int = 0,
        rank_fn: RankFn | None = None,
        embed_fn: Any | None = None,
        pg_dsn: str | None = None,
    ) -> None:
        self.lane = lane
        self.embed_cfg = embed_cfg
        self.mode = mode
        self.top_k = top_k
        self.page_prefix_chars = page_prefix_chars
        self.max_chars_per_chunk = max_chars_per_chunk
        self.rank_fn = rank_fn
        self.embed_fn = embed_fn
        self.pg_dsn = pg_dsn

    def retrieve(
        self,
        query: str,
        *,
        model_id: str,
        product_filter: ProductFilter | None = None,
        force_reindex: bool = False,
        skip_index_check: bool = False,
    ) -> EvidencePackage:
        """Run configured retrieval mode and normalize to EvidencePackage."""
        if not self.pg_dsn:
            raise RuntimeError("Manual raw RAG requires RETAIL_DATABASE_URL (Postgres manual_chunks)")
        scope = resolve_product_scope(query, suite_model=model_id or None)
        pf = product_filter or scope.manual_filter
        t0 = time.perf_counter()
        if self.mode in ("hybrid_rrf", "hybrid_rrf_rerank"):
            hits = hybrid_pg_rrf_search(
                self.pg_dsn,
                self.lane,
                query,
                model_id=model_id,
                product_filter=pf,
                ingest_key=scope.ingest_key,
                embed_cfg=self.embed_cfg,
                top_k=self.top_k,
                embed_fn=self.embed_fn,
                force_reindex=force_reindex,
                skip_index_check=skip_index_check,
            )
            if hits and self.rank_fn is not None:
                from retail_brain.rerank import listwise_rerank

                hits = listwise_rerank(query, hits, rank_fn=self.rank_fn, max_candidates=self.top_k)
            pkg_mode = "hybrid_rrf" if self.mode == "hybrid_rrf_rerank" else self.mode
            meta = {"hit_count": len(hits), "d5_rerank": self.rank_fn is not None}
        else:
            hits = vector_pg_search(
                self.pg_dsn,
                self.lane,
                query,
                model_id=model_id,
                product_filter=pf,
                ingest_key=scope.ingest_key,
                embed_cfg=self.embed_cfg,
                top_k=self.top_k,
                embed_fn=self.embed_fn,
                force_reindex=force_reindex,
                skip_index_check=skip_index_check,
            )
            pkg_mode = "vector"
            meta = {"hit_count": len(hits)}

        ms = int((time.perf_counter() - t0) * 1000)
        return EvidencePackage(
            query=query,
            model_id=model_id,
            mode=pkg_mode,
            chunks=_hits_to_chunks(hits),
            latency_ms=ms,
            meta=meta,
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
