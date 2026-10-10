"""Ticket search against PostgreSQL (pgvector + optional tsvector RRF)."""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from retail_brain.embeddings import embed_text
from retail_brain.hybrid_search import hybrid_enabled
from retail_brain.market import pg_ts_config
from retail_brain.rrf import reciprocal_rank_fusion
from retail_brain.text_normalize import fts_query_text


def _connect(dsn: str):
    import psycopg2  # type: ignore

    return psycopg2.connect(dsn)


def vector_ids(
    cur,
    query: str,
    *,
    model_filter: Optional[str],
    limit: int,
) -> List[str]:
    emb = embed_text(query, task_type="RETRIEVAL_QUERY")
    emb_literal = "[" + ",".join(str(x) for x in emb) + "]"
    if model_filter:
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


def lexical_ids(
    cur,
    query: str,
    *,
    model_filter: Optional[str],
    limit: int,
) -> List[str]:
    cfg = pg_ts_config()
    q = fts_query_text(query)
    if model_filter:
        cur.execute(
            f"""
            SELECT ticket_id FROM service_queries
            WHERE status = 'resolved' AND model = %s
              AND query_tsv @@ websearch_to_tsquery(%s, %s)
            ORDER BY ts_rank_cd(query_tsv, websearch_to_tsquery(%s, %s)) DESC
            LIMIT %s
            """,
            (model_filter, cfg, q, cfg, q, limit),
        )
    else:
        cur.execute(
            f"""
            SELECT ticket_id FROM service_queries
            WHERE status = 'resolved'
              AND query_tsv @@ websearch_to_tsquery(%s, %s)
            ORDER BY ts_rank_cd(query_tsv, websearch_to_tsquery(%s, %s)) DESC
            LIMIT %s
            """,
            (cfg, q, cfg, q, limit),
        )
    return [r[0] for r in cur.fetchall()]


def search_ticket_ids_pg(
    dsn: str,
    query: str,
    *,
    model_filter: Optional[str] = None,
    limit: int = 10,
) -> List[str]:
    conn = _connect(dsn)
    try:
        with conn.cursor() as cur:
            if not hybrid_enabled():
                return vector_ids(cur, query, model_filter=model_filter, limit=limit)
            v = vector_ids(cur, query, model_filter=model_filter, limit=limit * 2)
            l = lexical_ids(cur, query, model_filter=model_filter, limit=limit * 2)
            fused = reciprocal_rank_fusion([v, l])
            return [tid for tid, _ in fused[:limit]]
    finally:
        conn.close()


def run_eval_pg(
    dsn: str,
    eval_cases: List[dict],
    *,
    top_k: int = 5,
) -> Dict[str, Any]:
    from retail_brain.eval_harness import EvalCaseResult
    from retail_brain.eval_scoring import aggregate_recall, score_top1

    mode = "hybrid" if hybrid_enabled() else "vector"
    hybrid_on = hybrid_enabled()
    results: List[EvalCaseResult] = []
    lexical_nonempty = 0
    conn = _connect(dsn)
    try:
        for case in eval_cases:
            if case.get("stratum") == "sql_routed":
                continue
            query = case["query"]
            model_filter = case.get("model_filter")
            if hybrid_on:
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
            results.append(
                EvalCaseResult(
                    eval_id=case["eval_id"],
                    stratum=case["stratum"],
                    hit=hit_strict,
                    top_ticket_id=top,
                    hit_strict=hit_strict,
                    hit_acceptable=hit_acceptable,
                )
            )
    finally:
        conn.close()
    case_dicts = [r.__dict__ for r in results]
    by_stratum: Dict[str, List[bool]] = {}
    for r in results:
        by_stratum.setdefault(r.stratum, []).append(r.hit_strict)
    out: Dict[str, Any] = {
        "mode": mode,
        "backend": "postgres",
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
