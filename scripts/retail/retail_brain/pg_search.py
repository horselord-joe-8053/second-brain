"""Production ticket search: pgvector dense leg + pluggable keyword index + Python RRF.

Flow for hybrid modes (``rrf_*``):
  1. ``vector_ids`` — embed query, ORDER BY ``query_embedding <-> query`` on ``service_queries``.
  2. ``lexical_ids`` — ordered ticket ids from ``RETAIL_LEXICAL_BACKEND`` (default Tantivy on disk).
  3. ``_fuse_pg`` — reciprocal rank fusion; optional V1.2 term boost uses ``search_text`` from PG.

Postgres full-text search is intentionally **not** used for the keyword leg; see ``lexical_search/``.
``lexical_ids`` keeps a ``cur`` parameter so callers (eval, reload scripts) need not change signatures.
"""

from __future__ import annotations

import os
import sys
from typing import Any, Dict, List, Optional, Set

from retail_brain.embeddings import embed_text
from retail_brain.rrf import code_boost_scores, reciprocal_rank_fusion
from retail_brain.search_mode import (
    code_boost_enabled,
    is_hybrid_mode,
    lexical_code_boost_lambda,
    resolve_ticket_search_mode,
    rrf_list_weights,
)


def _connect(dsn: str):
    """Open a psycopg2 connection to the retail Postgres DSN."""
    import psycopg2  # type: ignore

    return psycopg2.connect(dsn)


def _vector_literal(emb: List[float]) -> str:
    """pgvector text literal for a query embedding."""
    return "[" + ",".join(str(x) for x in emb) + "]"


def vector_ids(
    cur,
    query: str,
    *,
    model_filter: Optional[str],
    brand_filter: Optional[str] = None,
    limit: int,
    query_embedding: Optional[List[float]] = None,
) -> List[str]:
    """Dense retrieval leg: nearest neighbors in ``service_queries.query_embedding``.

    Pass ``query_embedding`` to reuse one Gemini call across legs (answer bundle path).
    """
    emb = query_embedding or embed_text(query, task_type="RETRIEVAL_QUERY")
    emb_literal = _vector_literal(emb)
    brand = (brand_filter or "").strip()
    if model_filter and brand:
        cur.execute(
            """
            SELECT ticket_id FROM service_queries
            WHERE status = 'resolved' AND brand = %s AND model = %s
            ORDER BY query_embedding <-> %s::vector
            LIMIT %s
            """,
            (brand, model_filter, emb_literal, limit),
        )
    elif model_filter:
        cur.execute(
            """
            SELECT ticket_id FROM service_queries
            WHERE status = 'resolved' AND model = %s
            ORDER BY query_embedding <-> %s::vector
            LIMIT %s
            """,
            (model_filter, emb_literal, limit),
        )
    else:
        cur.execute(
            """
            SELECT ticket_id FROM service_queries
            WHERE status = 'resolved'
            ORDER BY query_embedding <-> %s::vector
            LIMIT %s
            """,
            (emb_literal, limit),
        )
    return [r[0] for r in cur.fetchall()]


def lexical_scored(
    query: str,
    *,
    model_filter: Optional[str],
    limit: int,
) -> List[tuple[str, float]]:
    """Keyword leg with BM25-style scores when the backend exposes ``search_scored`` (Tantivy)."""
    from retail_brain.lexical_search import open_lexical_index

    index = open_lexical_index()
    scored = getattr(index, "search_scored", None)
    if scored is not None:
        return scored(query, k=limit, model_filter=model_filter)
    ids = index.search_ids(query, k=limit, model_filter=model_filter)
    return [(tid, 0.0) for tid in ids]


def lexical_ids(
    cur,
    query: str,
    *,
    model_filter: Optional[str],
    limit: int,
) -> List[str]:
    """Keyword ids from the selected lexical backend. Does not run Postgres full-text search.

    `cur` stays in the signature so callers do not change. Ranking no longer uses it.
    """
    del cur
    ids = [tid for tid, _ in lexical_scored(query, model_filter=model_filter, limit=limit)]
    if os.environ.get("RETAIL_LEXICAL_TRACE", "").strip().lower() in ("1", "true", "yes"):
        scored = lexical_scored(query, model_filter=model_filter, limit=min(limit, 5))
        backend = os.environ.get("RETAIL_LEXICAL_BACKEND", "tantivy")
        top = ", ".join(f"{tid}:{score:.4f}" for tid, score in scored[:5])
        print(f"[lexical_trace backend={backend}] top={top}", file=sys.stderr)
    return ids


def _search_text_map(cur, ticket_ids: Set[str]) -> Dict[str, str]:
    """Hydrate ``search_text`` for fusion candidates (code-boost compares SAM-E tokens)."""
    if not ticket_ids:
        return {}
    cur.execute(
        "SELECT ticket_id, coalesce(search_text, '') FROM service_queries WHERE ticket_id = ANY(%s)",
        (list(ticket_ids),),
    )
    return {row[0]: row[1] for row in cur.fetchall()}


def _fuse_pg(
    cur,
    query: str,
    v: List[str],
    l: List[str],
    *,
    mode: str,
    limit: int,
) -> List[str]:
    """Merge vector and lexical rank lists; weights and code boost depend on ``mode``."""
    w_v, w_l = rrf_list_weights(mode)
    extra: Dict[str, float] = {}
    if code_boost_enabled(mode):
        ids = set(v) | set(l)
        texts = _search_text_map(cur, ids)
        extra = code_boost_scores(
            query,
            list(ids),
            id_to_search_text=texts,
            lambda_boost=lexical_code_boost_lambda(),
        )
    fused = reciprocal_rank_fusion(
        [v, l],
        list_weights=[w_v, w_l],
        lexical_rank_order=l,
        extra_score_by_id=extra,
    )
    return [tid for tid, _ in fused[:limit]]


def _fuse_pg_scored(
    cur, query: str, v: List[str], l: List[str], *, mode: str, limit: int
) -> List[tuple[str, float]]:
    """Same fusion as ``_fuse_pg`` but keeps the fused score per id."""
    w_v, w_l = rrf_list_weights(mode)
    extra: Dict[str, float] = {}
    if code_boost_enabled(mode):
        ids = set(v) | set(l)
        extra = code_boost_scores(
            query,
            list(ids),
            id_to_search_text=_search_text_map(cur, ids),
            lambda_boost=lexical_code_boost_lambda(),
        )
    fused = reciprocal_rank_fusion([v, l], list_weights=[w_v, w_l], lexical_rank_order=l, extra_score_by_id=extra)
    return fused[:limit]


def hydrate_with_cosine(cur, query_embedding: List[float], ticket_ids: List[str]) -> Dict[str, Dict[str, Any]]:
    """Ticket fields + ``1 - cosine distance`` to the query for each id (pgvector ``<=>``)."""
    if not ticket_ids:
        return {}
    cur.execute(
        """
        SELECT ticket_id, model, customer_query_text, coalesce(resolution_text, ''),
               1 - (query_embedding <=> %s::vector) AS cosine
        FROM service_queries WHERE ticket_id = ANY(%s)
        """,
        (_vector_literal(query_embedding), list(ticket_ids)),
    )
    return {
        r[0]: {"model": r[1], "customer_query_text": r[2], "resolution_text": r[3], "cosine_similarity": float(r[4])}
        for r in cur.fetchall()
    }


def search_ticket_hits_pg(
    dsn: str,
    query: str,
    *,
    model_filter: Optional[str] = None,
    brand_filter: Optional[str] = None,
    limit: int = 2,
) -> tuple[str, List[Dict[str, Any]]]:
    """Ranked hits for the answer bundle: ``(mode, [{ticket_id, fused_score, cosine_similarity, …}])``."""
    mode = resolve_ticket_search_mode()
    q_emb = embed_text(query, task_type="RETRIEVAL_QUERY")
    conn = _connect(dsn)
    try:
        with conn.cursor() as cur:
            if mode == "vector_only":
                ids = vector_ids(
                    cur,
                    query,
                    model_filter=model_filter,
                    brand_filter=brand_filter,
                    limit=limit,
                    query_embedding=q_emb,
                )
                scored: List[tuple[str, Optional[float]]] = [(tid, None) for tid in ids]
            else:
                v = vector_ids(
                    cur,
                    query,
                    model_filter=model_filter,
                    brand_filter=brand_filter,
                    limit=limit * 2,
                    query_embedding=q_emb,
                )
                l = lexical_ids(cur, query, model_filter=model_filter, limit=limit * 2)
                scored = list(_fuse_pg_scored(cur, query, v, l, mode=mode, limit=limit))
            fields = hydrate_with_cosine(cur, q_emb, [tid for tid, _ in scored])
    finally:
        conn.close()
    hits = [{"ticket_id": tid, "fused_score": fs, **fields[tid]} for tid, fs in scored if tid in fields]
    return mode, hits


def search_ticket_ids_pg(
    dsn: str,
    query: str,
    *,
    model_filter: Optional[str] = None,
    brand_filter: Optional[str] = None,
    limit: int = 10,
) -> List[str]:
    """Top ticket ids from PG: vector-only or hybrid RRF per ``RETAIL_TICKET_SEARCH_MODE``."""
    mode = resolve_ticket_search_mode()
    conn = _connect(dsn)
    try:
        with conn.cursor() as cur:
            if mode == "vector_only":
                return vector_ids(
                    cur, query, model_filter=model_filter, brand_filter=brand_filter, limit=limit
                )
            # Prefetch 2× final k so RRF has depth before truncation (matches offline hybrid_search).
            v = vector_ids(
                cur, query, model_filter=model_filter, brand_filter=brand_filter, limit=limit * 2
            )
            l = lexical_ids(cur, query, model_filter=model_filter, limit=limit * 2)
            return _fuse_pg(cur, query, v, l, mode=mode, limit=limit)
    finally:
        conn.close()


def trace_search_legs(
    cur,
    query: str,
    *,
    model_filter: Optional[str],
    gold_ticket_id: Optional[str] = None,
    limit: int = 5,
) -> Dict[str, Any]:
    """Debug snapshot: vector order, lexical BM25 scores (Tantivy), and gold rank in each leg."""
    v = vector_ids(cur, query, model_filter=model_filter, limit=limit)
    lex_scored = lexical_scored(query, model_filter=model_filter, limit=limit)
    l = [tid for tid, _ in lex_scored]
    out: Dict[str, Any] = {
        "vector_top": v,
        "lexical_top": l,
        "lexical_scored": [{"ticket_id": tid, "score": score} for tid, score in lex_scored],
        "lexical_backend": os.environ.get("RETAIL_LEXICAL_BACKEND", "tantivy"),
    }
    if gold_ticket_id:
        out["gold_rank_vector"] = v.index(gold_ticket_id) + 1 if gold_ticket_id in v else None
        out["gold_rank_lexical"] = l.index(gold_ticket_id) + 1 if gold_ticket_id in l else None
    return out


def run_eval_pg(
    dsn: str,
    eval_cases: List[dict],
    *,
    top_k: int = 5,
) -> Dict[str, Any]:
    """Run retrieval eval against live PG; reports ``lexical_leg_nonempty`` when hybrid is on."""
    from retail_brain.eval_harness import EvalCaseResult
    from retail_brain.eval_scoring import aggregate_recall, score_top1

    mode = resolve_ticket_search_mode()
    hybrid_on = is_hybrid_mode(mode)
    trace_legs = os.environ.get("RETAIL_EVAL_TRACE_LEGS", "").strip().lower() in ("1", "true", "yes")
    results: List[EvalCaseResult] = []
    case_dicts: List[Dict[str, Any]] = []
    lexical_nonempty = 0
    conn = _connect(dsn)
    try:
        for case in eval_cases:
            if case.get("stratum") == "sql_routed":
                continue
            query = case["query"]
            model_filter = case.get("model_filter")
            if hybrid_on:
                # Separate probe: did the keyword index return anything? (A/B health signal.)
                with conn.cursor() as cur:
                    lex = lexical_ids(
                        cur,
                        query,
                        model_filter=model_filter,
                        limit=top_k,
                    )
                if lex:
                    lexical_nonempty += 1
            ranked = search_ticket_ids_pg(
                dsn,
                query,
                model_filter=model_filter,
                limit=top_k,
            )
            top = ranked[0] if ranked else None
            hit_strict, hit_acceptable = score_top1(case, top)
            row = EvalCaseResult(
                eval_id=case["eval_id"],
                stratum=case["stratum"],
                hit=hit_strict,
                top_ticket_id=top,
                hit_strict=hit_strict,
                hit_acceptable=hit_acceptable,
            )
            results.append(row)
            row_dict: Dict[str, Any] = dict(row.__dict__)
            if trace_legs:
                gold = (case.get("expected_ticket_ids") or [None])[0]
                with conn.cursor() as cur:
                    row_dict["leg_trace"] = trace_search_legs(
                        cur,
                        query,
                        model_filter=model_filter,
                        gold_ticket_id=gold,
                        limit=top_k,
                    )
            case_dicts.append(row_dict)
    finally:
        conn.close()
    by_stratum: Dict[str, List[bool]] = {}
    for r in results:
        by_stratum.setdefault(r.stratum, []).append(r.hit_strict)
    out: Dict[str, Any] = {
        "mode": mode,
        "backend": "postgres",
        "search_mode": mode,
        "hybrid_flag": os.environ.get("RETAIL_TICKET_HYBRID_SEARCH", "0"),
        **aggregate_recall(case_dicts),
        "by_stratum": {
            k: sum(1 for b in v if b) / len(v) if v else 0.0 for k, v in by_stratum.items()
        },
        "cases": case_dicts,
    }
    if hybrid_on:
        out["lexical_leg_nonempty"] = lexical_nonempty
        out["lexical_leg_nonempty_rate"] = (
            lexical_nonempty / len(results) if results else 0.0
        )
    return out
