"""D7 — universal query-unit orchestration (decompose → per-leg retrieve → aggregate).

Legs (ticket_leg, manual hybrid) stay unaware of decomposition; bundled harness calls this layer.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Sequence

from retail_brain.manual_query_decompose import split_query_units
from retail_brain.rrf import reciprocal_rank_fusion


def d7_min_ticket_cosine() -> float:
    """Minimum cosine for a sub-query ticket hit to enter the merged packet (per-unit top-k)."""
    raw = (os.environ.get("RETAIL_D7_MIN_TICKET_COSINE") or "0.28").strip()
    try:
        return float(raw)
    except ValueError:
        return 0.28


def plan_query_units(question: str, *, max_units: int = 4) -> list[str]:
    """Split bundled customer question into retrieval units (no model_id prefix)."""
    return split_query_units(question, max_units=max_units)


def should_run_decomposed(units: list[str]) -> bool:
    """True when orchestrator should fan out (more than one non-empty unit)."""
    return len([u for u in units if (u or "").strip()]) > 1


def merge_manual_chunk_rows(
    unit_hit_lists: list[list[dict[str, Any]]],
    *,
    top_k: int,
    rrf_k: int = 60,
) -> list[dict[str, Any]]:
    """RRF-merge manual hybrid hit rows from each sub-query; return top_k dict rows."""
    id_lists: list[list[str]] = []
    by_id: dict[str, dict[str, Any]] = {}
    for hits in unit_hit_lists:
        ids = [str(h["chunk_id"]) for h in hits if h.get("chunk_id")]
        id_lists.append(ids)
        for h in hits:
            by_id[str(h["chunk_id"])] = h
    if not id_lists:
        return []
    fused = reciprocal_rank_fusion(id_lists, k=rrf_k)
    out: list[dict[str, Any]] = []
    for cid, score in fused[:top_k]:
        row = dict(by_id.get(cid) or {})
        if not row:
            continue
        row["rrf_score"] = float(score)
        out.append(row)
    return out


def union_manual_chunk_rows(
    unit_hit_lists: list[list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    """Keep each unit's rows in order; a later duplicate chunk_id is dropped."""
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for hits in unit_hit_lists:
        for hit in hits:
            cid = str(hit.get("chunk_id") or "")
            if not cid or cid in seen:
                continue
            seen.add(cid)
            out.append(hit)
    return out


def select_manual_packet(
    unit_hit_lists: list[list[dict[str, Any]]],
    *,
    manual_rerank: str,
    top_k: int,
) -> list[dict[str, Any]]:
    """RRF-merge to top_k, or union per-unit lists when a rerank arm is set."""
    if (manual_rerank or "").strip():
        return union_manual_chunk_rows(unit_hit_lists)
    return merge_manual_chunk_rows(unit_hit_lists, top_k=top_k)


def dedupe_ticket_hits(*hit_lists: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    """Union ticket hit rows by ``ticket_id``; keep the row with highest ``cosine_similarity``."""
    by_id: dict[str, dict[str, Any]] = {}
    for hits in hit_lists:
        for h in hits:
            tid = str(h.get("ticket_id") or "")
            if not tid:
                continue
            prev = by_id.get(tid)
            cos = float(h.get("cosine_similarity") or 0.0)
            if prev is None or cos > float(prev.get("cosine_similarity") or 0.0):
                by_id[tid] = dict(h)
    return list(by_id.values())


def pfda_pick_tickets(
    question: str,
    *,
    decomposed_hits: Sequence[dict[str, Any]],
    anchor_hits: Sequence[dict[str, Any]],
    k: int,
    rank_fn: Any | None,
    max_candidates: int = 20,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """PFDA — dedupe decomposed + full-question anchor pool, listwise rerank, return top ``k``."""
    from retail_brain.rerank import listwise_rerank

    pool = dedupe_ticket_hits(list(decomposed_hits), list(anchor_hits))
    trace: dict[str, Any] = {
        "mode": "llm_listwise",
        "decomposed_ids": [str(h.get("ticket_id") or "") for h in decomposed_hits],
        "anchor_ids": [str(h.get("ticket_id") or "") for h in anchor_hits],
        "pool_ids": [str(h.get("ticket_id") or "") for h in pool],
        "selected_ids": [],
    }
    if not pool:
        return [], trace
    if rank_fn is None:
        ordered = sorted(pool, key=lambda h: -float(h.get("cosine_similarity") or 0.0))
        picked = ordered[: max(0, int(k))]
        trace["selected_ids"] = [str(h.get("ticket_id") or "") for h in picked]
        trace["fallback"] = "cosine_sort_no_rank_fn"
        return picked, trace
    if len(pool) == 1:
        picked = list(pool)[: max(0, int(k))]
        trace["selected_ids"] = [str(h.get("ticket_id") or "") for h in picked]
        trace["fallback"] = "single_candidate"
        return picked, trace
    reranked = listwise_rerank(
        question,
        pool,
        rank_fn=rank_fn,
        max_candidates=max_candidates,
    )
    picked = reranked[: max(0, int(k))]
    for rank, h in enumerate(picked, start=1):
        h["rank"] = rank
    trace["selected_ids"] = [str(h.get("ticket_id") or "") for h in picked]
    return picked, trace


def merge_ticket_hits_gated(
    unit_hit_lists: list[list[dict[str, Any]]],
    *,
    k_per_unit: int,
    min_cosine: float | None = None,
) -> list[dict[str, Any]]:
    """Per sub-query: up to k_per_unit tickets at or above min_cosine; dedupe by ticket_id."""
    floor = d7_min_ticket_cosine() if min_cosine is None else float(min_cosine)
    merged: list[dict[str, Any]] = []
    seen: set[str] = set()
    for hits in unit_hit_lists:
        kept = 0
        for h in hits:
            cos = float(h.get("cosine_similarity") or 0.0)
            if cos < floor:
                continue
            tid = str(h.get("ticket_id") or "")
            if not tid or tid in seen:
                continue
            seen.add(tid)
            merged.append(dict(h))
            kept += 1
            if kept >= k_per_unit:
                break
    merged.sort(key=lambda h: -float(h.get("cosine_similarity") or 0.0))
    for rank, h in enumerate(merged, start=1):
        h["rank"] = rank
    return merged


@dataclass
class UnitTicketTrace:
    """One sub-query ticket leg outcome."""

    unit_index: int
    query: str
    hits: list[dict[str, Any]]
    kept_ticket_ids: list[str]


@dataclass
class UnitManualTrace:
    """One sub-query manual leg outcome."""

    unit_index: int
    customer_unit: str
    retrieve_query: str
    chunk_ids: list[str]
    latency_ms: int
    rerank_backend: str = ""
    rerank_model: str = ""
    candidate_count: int = 0
    rerank_ms: int = 0
    pre_rerank_chunk_ids: list[str] = field(default_factory=list)
    post_rerank_chunk_ids: list[str] = field(default_factory=list)


@dataclass
class DecomposedRetrievalTrace:
    """JSON-serializable D7 trace for bundled results.jsonl."""

    enabled: bool
    units: list[str]
    min_ticket_cosine: float
    ticket_units: list[UnitTicketTrace] = field(default_factory=list)
    manual_units: list[UnitManualTrace] = field(default_factory=list)
    merged_ticket_ids: list[str] = field(default_factory=list)
    merged_manual_chunk_ids: list[str] = field(default_factory=list)
    d7_version: str = "v3"
    pfda: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Flatten for results row embedding."""
        return {
            "enabled": self.enabled,
            "units": list(self.units),
            "min_ticket_cosine": self.min_ticket_cosine,
            "ticket_units": [
                {
                    "unit_index": u.unit_index,
                    "query": u.query,
                    "hits": [
                        {
                            "ticket_id": h.get("ticket_id"),
                            "cosine_similarity": h.get("cosine_similarity"),
                            "customer_query_text": h.get("customer_query_text"),
                            "resolution_text": h.get("resolution_text"),
                            "kept": str(h.get("ticket_id") or "")
                            in u.kept_ticket_ids,
                        }
                        for h in u.hits
                    ],
                    "kept_ticket_ids": list(u.kept_ticket_ids),
                }
                for u in self.ticket_units
            ],
            "manual_units": [
                {
                    "unit_index": u.unit_index,
                    "customer_unit": u.customer_unit,
                    "retrieve_query": u.retrieve_query,
                    "chunk_ids": list(u.chunk_ids),
                    "latency_ms": u.latency_ms,
                    "rerank_backend": u.rerank_backend,
                    "rerank_model": u.rerank_model,
                    "candidate_count": u.candidate_count,
                    "rerank_ms": u.rerank_ms,
                    "pre_rerank_chunk_ids": list(u.pre_rerank_chunk_ids),
                    "post_rerank_chunk_ids": list(u.post_rerank_chunk_ids),
                }
                for u in self.manual_units
            ],
            "merged_ticket_ids": list(self.merged_ticket_ids),
            "merged_manual_chunk_ids": list(self.merged_manual_chunk_ids),
            "d7_version": self.d7_version,
            "pfda": dict(self.pfda),
        }
