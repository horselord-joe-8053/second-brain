"""D3.PG-H: hybrid lexical + vector on manual_chunks with RRF (U5 in-process lexical pool)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from retail_brain.manual_pg_db import list_manual_chunks  # noqa: E402
from retail_brain.rrf import reciprocal_rank_fusion  # noqa: E402
from tests.retail_multi_profiles.lib.lanes import Lane  # noqa: E402
from tests.retail_multi_profiles.lib.raw_embed import embed_texts_batch  # noqa: E402
from tests.retail_multi_profiles.lib.raw_hybrid_search import rank_chunks_vector  # noqa: E402
from tests.retail_multi_profiles.lib.raw_lexical import rank_chunks_lexical  # noqa: E402
from tests.retail_multi_profiles.lib.sku_scope import filter_chunks_by_model  # noqa: E402

from retail_brain.manual_pg_ingest import ensure_manual_pg_fresh  # noqa: E402


def hybrid_pg_rrf_search(
    dsn: str,
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
    """SKU-filtered PG pool → lexical + vector ranks → RRF merge."""
    ensure_manual_pg_fresh(
        dsn,
        lane,
        embed_cfg,
        force=force_reindex,
        skip_check=skip_index_check,
        embed_fn=embed_fn,
    )
    import psycopg2  # type: ignore

    conn = psycopg2.connect(dsn)
    try:
        with conn.cursor() as cur:
            pool = list_manual_chunks(cur, lane_id=lane.lane_id, limit=pool_limit)
    finally:
        conn.close()

    if (model_id or "").strip():
        pool = filter_chunks_by_model(pool, model_id=model_id)
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
        out.append(row)
    return out
