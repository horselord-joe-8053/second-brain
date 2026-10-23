"""Hybrid lexical + vector retrieval with RRF on raw Lance chunks."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[3]
RETAIL_PKG = REPO / "scripts" / "retail"
if str(RETAIL_PKG) not in sys.path:
    sys.path.insert(0, str(RETAIL_PKG))

from retail_brain.rrf import reciprocal_rank_fusion  # noqa: E402

from .lanes import Lane
from .raw_embed import embed_texts_batch
from .raw_lexical import rank_chunks_lexical
from .raw_rag_index import _cosine_distance, ensure_index_fresh, list_index_chunks


def _normalize_model_id(model_id: str) -> str:
    return (model_id or "").strip().lower()


def filter_chunks_by_model(
    chunks: list[dict[str, Any]],
    *,
    model_id: str,
) -> list[dict[str, Any]]:
    """Keep rows matching suite model_id; empty model_id rows are excluded when filter set."""
    want = _normalize_model_id(model_id)
    if not want:
        return chunks
    out: list[dict[str, Any]] = []
    for row in chunks:
        mid = _normalize_model_id(str(row.get("model_id") or ""))
        if mid == want:
            out.append(row)
    return out


def rank_chunks_vector(
    query_vector: list[float],
    chunks: list[dict[str, Any]],
    *,
    top_n: int,
) -> list[dict[str, Any]]:
    """Order in-memory chunk rows by cosine distance to query vector."""
    scored: list[tuple[float, str, dict[str, Any]]] = []
    for row in chunks:
        vec = list(row.get("vector") or [])
        if not vec:
            continue
        dist = _cosine_distance(query_vector, vec)
        cid = str(row.get("chunk_id") or "")
        scored.append((dist, cid, {**row, "distance": dist, "vector_score": 1.0 / (1.0 + dist)}))
    scored.sort(key=lambda x: (x[0], x[1]))
    return [row for _, _, row in scored[:top_n]]


def hybrid_rrf_search(
    lane: Lane,
    query: str,
    *,
    model_id: str,
    embed_cfg: dict[str, Any],
    top_k: int = 5,
    rrf_k: int = 60,
    pool_limit: int = 200,
    embed_fn: Any | None = None,
    force_reindex: bool = False,
    skip_index_check: bool = False,
) -> list[dict[str, Any]]:
    """SKU-filtered pool → lexical + vector ranks → RRF merge."""
    ensure_index_fresh(
        lane,
        embed_cfg,
        force=force_reindex,
        skip_check=skip_index_check,
        embed_fn=embed_fn,
    )
    pool = filter_chunks_by_model(list_index_chunks(lane, limit=pool_limit), model_id=model_id)
    if not pool:
        return []

    if embed_fn is not None:
        qvec = embed_fn([query])[0]
    else:
        qvec = embed_texts_batch([query], embed_cfg)[0]

    lex_ranked = rank_chunks_lexical(query, pool, top_n=min(len(pool), top_k * 4))
    vec_ranked = rank_chunks_vector(qvec, pool, top_n=min(len(pool), top_k * 4))

    lex_ids = [str(r["chunk_id"]) for r in lex_ranked if r.get("chunk_id")]
    vec_ids = [str(r["chunk_id"]) for r in vec_ranked if r.get("chunk_id")]
    fused = reciprocal_rank_fusion([lex_ids, vec_ids], k=rrf_k, lexical_rank_order=lex_ids)
    by_id = {str(r["chunk_id"]): r for r in pool if r.get("chunk_id")}

    out: list[dict[str, Any]] = []
    for cid, rrf_score in fused[:top_k]:
        row = dict(by_id.get(cid) or {})
        if not row:
            continue
        row["rrf_score"] = float(rrf_score)
        row.setdefault("distance", row.get("distance"))
        row.setdefault("vector_score", row.get("vector_score"))
        out.append(row)
    return out
