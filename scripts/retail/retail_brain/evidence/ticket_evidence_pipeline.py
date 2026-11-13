"""Wire ticket D5 stack from shared rerank_registry (DRY with manual harness)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from retail_brain.rerank_registry import RankFn, rank_fn_for_resolved

from .ticket_agentic import TicketAgenticController
from .ticket_retriever import TicketEvidenceRetriever

EvidencePathMode = Literal["baseline", "retriever", "retriever_rerank", "agentic"]


def ticket_rerank_llm_cfg(repo_root: Path) -> dict[str, Any]:
    """Answer/rerank LLM settings — same run-config sources as manual raw pipeline."""
    from tests.retail_multi_profiles.lib.run_config import load_merged_run_config

    cfg = load_merged_run_config(repo_root)
    raw = cfg.get("retail_raw_rag") or {}
    rerank_block = raw.get("rerank") if isinstance(raw.get("rerank"), dict) else {}
    llm = rerank_block.get("llm") if isinstance(rerank_block.get("llm"), dict) else None
    if llm:
        return dict(llm)
    answer = cfg.get("answer")
    return dict(answer) if isinstance(answer, dict) else {}


def _coerce_rerank_enabled(explicit: bool | None, *, mode: EvidencePathMode) -> bool:
    """Env RETAIL_D5_RERANK_ENABLED overrides; retriever_rerank mode defaults rerank on."""
    if explicit is not None:
        return explicit
    env = os.environ.get("RETAIL_D5_RERANK_ENABLED")
    if env is not None and str(env).strip() != "":
        return str(env).strip().lower() in ("1", "true", "yes", "on")
    return mode == "retriever_rerank"


def build_ticket_rank_fn(
    repo_root: Path,
    *,
    mode: EvidencePathMode,
    rerank_enabled: bool | None = None,
    generate_fn: Any | None = None,
) -> RankFn | None:
    """Shared D5.R rank_fn for ticket pools (same registry as manual)."""
    enabled = _coerce_rerank_enabled(rerank_enabled, mode=mode)
    backend = (os.environ.get("RETAIL_D5_RERANK_BACKEND") or "llm_listwise").strip().lower()
    return rank_fn_for_resolved(
        rerank_enabled=enabled,
        backend=backend,
        rerank_llm_cfg=ticket_rerank_llm_cfg(repo_root),
        generate_fn=generate_fn,
    )


@dataclass
class TicketEvidenceStack:
    """Built retriever (+ optional agentic) for one evidence-path mode."""

    retriever: TicketEvidenceRetriever
    agentic: TicketAgenticController | None
    rank_fn_active: bool


def build_ticket_evidence_stack(
    dsn: str,
    *,
    repo_root: Path,
    mode: EvidencePathMode,
    top_k: int = 5,
    generate_fn: Any | None = None,
    search_fn: Any | None = None,
) -> TicketEvidenceStack:
    """Single factory for ticket evidence eval and future retail_answer ticket leg."""
    rank_fn = build_ticket_rank_fn(repo_root, mode=mode, generate_fn=generate_fn)
    retriever = TicketEvidenceRetriever(
        dsn,
        search_fn=search_fn,
        top_k=top_k,
        rank_fn=rank_fn if mode == "retriever_rerank" else None,
    )
    agentic: TicketAgenticController | None = None
    if mode == "agentic":
        agentic = TicketAgenticController(retriever, max_loops=1)
    return TicketEvidenceStack(
        retriever=retriever,
        agentic=agentic,
        rank_fn_active=rank_fn is not None and mode == "retriever_rerank",
    )
