"""D3.PG-H: hybrid lexical + vector on manual_chunks with RRF (SQL product filter + Tantivy or overlap)."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from retail_brain.manual_pg_db import (  # noqa: E402
    fetch_manual_chunks_by_ids,
    knn_manual_chunks,
    list_manual_chunks,
)
from retail_brain.rrf import reciprocal_rank_fusion  # noqa: E402
from tests.retail_multi_profiles.lib.lanes import Lane  # noqa: E402
from tests.retail_multi_profiles.lib.raw_embed import embed_texts_batch  # noqa: E402
from tests.retail_multi_profiles.lib.raw_vector_rank import rank_chunks_vector  # noqa: E402
from tests.retail_multi_profiles.lib.raw_lexical import rank_chunks_lexical  # noqa: E402
from retail_brain.product_scope import ProductFilter  # noqa: E402
from retail_brain.sku_scope import filter_chunks_by_model, filter_chunks_by_product  # noqa: E402

from retail_brain.manual_pg_ingest import ensure_manual_pg_fresh  # noqa: E402
from retail_brain.manual_page_pack import apply_page_pack_to_ranked_rows  # noqa: E402
from tests.retail_multi_profiles.lib.raw_policy import (  # noqa: E402
    d7_query_mode,
    manual_d2_chunk_policy,
    manual_d2_page_pack_mode,
)


def manual_lexical_backend_name() -> str:
    """``tantivy`` (evo-18 T0 default) or ``overlap`` (legacy in-process scorer)."""
    return (os.environ.get("RETAIL_MANUAL_LEXICAL_BACKEND") or "tantivy").strip().lower()


def _product_sql_filters(
    product_filter: ProductFilter | None,
) -> tuple[str | None, str | None]:
    """Return (brand, oem_model) when the filter is active for SQL predicates."""
    if product_filter and product_filter.active():
        return product_filter.brand, product_filter.oem_model
    return None, None


def _load_pg_pool(
    dsn: str,
    lane: Lane,
    embed_cfg: dict[str, Any],
    *,
    pool_limit: int,
    embed_fn: Any | None,
    force_reindex: bool,
    skip_index_check: bool,
    product_filter: ProductFilter | None = None,
) -> list[dict[str, Any]]:
    """Ensure PG ingest fresh and return chunk rows (SQL-filtered when product scope set)."""
    ensure_manual_pg_fresh(
        dsn,
        lane,
        embed_cfg,
        force=force_reindex,
        skip_check=skip_index_check,
        embed_fn=embed_fn,
    )
    brand, oem = _product_sql_filters(product_filter)
    import psycopg2  # type: ignore

    conn = psycopg2.connect(dsn)
    try:
        with conn.cursor() as cur:
            return list_manual_chunks(
                cur,
                lane_id=lane.lane_id,
                limit=pool_limit,
                brand=brand,
                oem_model=oem,
            )
    finally:
        conn.close()


def _apply_product_pool_filter(
    pool: list[dict[str, Any]],
    *,
    product_filter: ProductFilter | None,
    model_id: str,
    ingest_key: str | None,
) -> list[dict[str, Any]]:
    """Narrow chunk pool when SQL filter was not used (legacy slug-only path)."""
    if product_filter and product_filter.active():
        return filter_chunks_by_product(
            pool,
            brand=product_filter.brand,
            oem_model=product_filter.oem_model,
            ingest_key=ingest_key,
        )
    if (model_id or "").strip():
        return filter_chunks_by_model(pool, model_id=model_id)
    return list(pool)


def _lexical_rank_ids_tantivy(
    query: str,
    *,
    brand: str | None,
    oem_model: str | None,
    top_n: int,
) -> list[str]:
    """BM25 leg via manual Tantivy index (chunk_id as stable id)."""
    from retail_brain.lexical_search.manual_tantivy_index import ManualTantivyLexicalIndex

    idx = ManualTantivyLexicalIndex()
    scored = idx.search_scored(
        query,
        k=top_n,
        brand_filter=brand,
        oem_model_filter=oem_model,
    )
    return [cid for cid, _ in scored]


def _vector_rank_ids_knn(
    dsn: str,
    lane: Lane,
    qvec: list[float],
    *,
    brand: str | None,
    oem_model: str | None,
    top_n: int,
) -> list[str]:
    """Dense leg via pgvector KNN with optional product SQL filter."""
    import psycopg2  # type: ignore

    conn = psycopg2.connect(dsn)
    try:
        with conn.cursor() as cur:
            ranked = knn_manual_chunks(
                cur,
                lane_id=lane.lane_id,
                query_vector=qvec,
                limit=top_n,
                brand=brand,
                oem_model=oem_model,
            )
    finally:
        conn.close()
    return [str(r["chunk_id"]) for r in ranked if r.get("chunk_id")]


def _maybe_page_pack(ranked: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Apply D2.page_pack when chunk policy is page_heading."""
    if manual_d2_chunk_policy() != "page_heading":
        return ranked
    return apply_page_pack_to_ranked_rows(
        ranked, mode=manual_d2_page_pack_mode(), per_page_k=5
    )


def hybrid_pg_rrf_search(
    dsn: str,
    lane: Lane,
    query: str,
    *,
    model_id: str = "",
    product_filter: ProductFilter | None = None,
    ingest_key: str | None = None,
    embed_cfg: dict[str, Any],
    top_k: int = 5,
    rrf_k: int = 60,
    pool_limit: int = 200,
    embed_fn: Any | None = None,
    force_reindex: bool = False,
    skip_index_check: bool = False,
    _skip_d7_decompose: bool = False,
) -> list[dict[str, Any]]:
    """Product-scoped PG hybrid: Tantivy+KNN when filtered, else pool overlap+vector RRF."""
    if not _skip_d7_decompose and d7_query_mode() == "decompose":
        from retail_brain.manual_query_decompose import split_query_units

        units = split_query_units(query)
        if len(units) > 1:
            id_lists: list[list[str]] = []
            by_id: dict[str, dict[str, Any]] = {}
            for unit in units:
                sub = hybrid_pg_rrf_search(
                    dsn,
                    lane,
                    unit,
                    model_id=model_id,
                    product_filter=product_filter,
                    ingest_key=ingest_key,
                    embed_cfg=embed_cfg,
                    top_k=top_k,
                    rrf_k=rrf_k,
                    pool_limit=pool_limit,
                    embed_fn=embed_fn,
                    force_reindex=force_reindex,
                    skip_index_check=skip_index_check,
                    _skip_d7_decompose=True,
                )
                ids = [str(h["chunk_id"]) for h in sub if h.get("chunk_id")]
                id_lists.append(ids)
                for h in sub:
                    by_id[str(h["chunk_id"])] = h
            fused = reciprocal_rank_fusion(id_lists, k=rrf_k)
            out: list[dict[str, Any]] = []
            for cid, score in fused[:top_k]:
                row = dict(by_id.get(cid) or {})
                if not row:
                    continue
                row["rrf_score"] = float(score)
                row["d7_decompose"] = True
                out.append(row)
            return out

    brand, oem = _product_sql_filters(product_filter)
    use_sql_product = bool((oem or "").strip())
    backend = manual_lexical_backend_name()

    if embed_fn is not None:
        qvec = embed_fn([query])[0]
    else:
        qvec = embed_texts_batch([query], embed_cfg)[0]

    cand_n = max(top_k * 4, 20)

    if use_sql_product and backend == "tantivy":
        lex_ids = _lexical_rank_ids_tantivy(query, brand=brand, oem_model=oem, top_n=cand_n)
        vec_ids = _vector_rank_ids_knn(
            dsn, lane, qvec, brand=brand, oem_model=oem, top_n=cand_n
        )
        import psycopg2  # type: ignore

        conn = psycopg2.connect(dsn)
        try:
            with conn.cursor() as cur:
                union_ids = list(dict.fromkeys(lex_ids + vec_ids))
                pool_rows = fetch_manual_chunks_by_ids(
                    cur, lane_id=lane.lane_id, chunk_ids=union_ids
                )
        finally:
            conn.close()
        by_cid = {str(r["chunk_id"]): r for r in pool_rows}
        lex_ranked = _maybe_page_pack([by_cid[c] for c in lex_ids if c in by_cid])
        vec_ranked = _maybe_page_pack([by_cid[c] for c in vec_ids if c in by_cid])
        lex_ids = [str(r["chunk_id"]) for r in lex_ranked]
        vec_ids = [str(r["chunk_id"]) for r in vec_ranked]
        fused = reciprocal_rank_fusion([lex_ids, vec_ids], k=rrf_k, lexical_rank_order=lex_ids)
        import psycopg2  # type: ignore

        conn = psycopg2.connect(dsn)
        try:
            with conn.cursor() as cur:
                need_ids = [cid for cid, _ in fused[:top_k]]
                pool = fetch_manual_chunks_by_ids(cur, lane_id=lane.lane_id, chunk_ids=need_ids)
        finally:
            conn.close()
        by_id = {str(r["chunk_id"]): r for r in pool}
        out: list[dict[str, Any]] = []
        for cid, rrf_score in fused[:top_k]:
            row = dict(by_id.get(cid) or {})
            if not row:
                continue
            row["rrf_score"] = float(rrf_score)
            out.append(row)
        return out

    pool = _load_pg_pool(
        dsn,
        lane,
        embed_cfg,
        pool_limit=pool_limit,
        embed_fn=embed_fn,
        force_reindex=force_reindex,
        skip_index_check=skip_index_check,
        product_filter=product_filter if use_sql_product else None,
    )
    if not use_sql_product:
        pool = _apply_product_pool_filter(
            pool, product_filter=product_filter, model_id=model_id, ingest_key=ingest_key
        )
    if not pool:
        return []

    if backend == "tantivy" and use_sql_product:
        lex_ids = _lexical_rank_ids_tantivy(query, brand=brand, oem_model=oem, top_n=cand_n)
        lex_ranked = [r for r in pool if str(r.get("chunk_id")) in lex_ids]
        lex_ranked.sort(key=lambda r: lex_ids.index(str(r["chunk_id"])))
    else:
        lex_ranked = rank_chunks_lexical(query, pool, top_n=min(len(pool), cand_n))

    vec_ranked = rank_chunks_vector(qvec, pool, top_n=min(len(pool), cand_n))
    lex_ranked = _maybe_page_pack(lex_ranked)
    vec_ranked = _maybe_page_pack(vec_ranked)

    lex_ids = [str(r["chunk_id"]) for r in lex_ranked if r.get("chunk_id")]
    vec_ids = [str(r["chunk_id"]) for r in vec_ranked if r.get("chunk_id")]
    fused = reciprocal_rank_fusion([lex_ids, vec_ids], k=rrf_k, lexical_rank_order=lex_ids)
    by_id = {str(r["chunk_id"]): r for r in pool if r.get("chunk_id")}

    out = []
    for cid, rrf_score in fused[:top_k]:
        row = dict(by_id.get(cid) or {})
        if not row:
            continue
        row["rrf_score"] = float(rrf_score)
        out.append(row)
    return out


def vector_pg_search(
    dsn: str,
    lane: Lane,
    query: str,
    *,
    model_id: str = "",
    product_filter: ProductFilter | None = None,
    ingest_key: str | None = None,
    embed_cfg: dict[str, Any],
    top_k: int = 5,
    pool_limit: int = 200,
    embed_fn: Any | None = None,
    force_reindex: bool = False,
    skip_index_check: bool = False,
) -> list[dict[str, Any]]:
    """Product-filtered PG pool → vector top-k (D3 vector baseline on Postgres)."""
    brand, oem = _product_sql_filters(product_filter)
    if brand and oem:
        if embed_fn is not None:
            qvec = embed_fn([query])[0]
        else:
            qvec = embed_texts_batch([query], embed_cfg)[0]
        import psycopg2  # type: ignore

        conn = psycopg2.connect(dsn)
        try:
            with conn.cursor() as cur:
                return knn_manual_chunks(
                    cur,
                    lane_id=lane.lane_id,
                    query_vector=qvec,
                    limit=top_k,
                    brand=brand,
                    oem_model=oem,
                )
        finally:
            conn.close()

    pool = _load_pg_pool(
        dsn,
        lane,
        embed_cfg,
        pool_limit=pool_limit,
        embed_fn=embed_fn,
        force_reindex=force_reindex,
        skip_index_check=skip_index_check,
        product_filter=product_filter,
    )
    pool = _apply_product_pool_filter(
        pool, product_filter=product_filter, model_id=model_id, ingest_key=ingest_key
    )
    if not pool:
        return []
    if embed_fn is not None:
        qvec = embed_fn([query])[0]
    else:
        qvec = embed_texts_batch([query], embed_cfg)[0]
    return rank_chunks_vector(qvec, pool, top_n=top_k)
