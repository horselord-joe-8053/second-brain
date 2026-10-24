"""Factory for manual raw retrieval (D3 retriever + optional D5 rank_fn / agentic)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from retail_brain.evidence.agentic import AgenticRetrievalController
from retail_brain.evidence.retriever import ManualEvidenceRetriever
from retail_brain.rerank_registry import rank_fn_for_resolved

from .lanes import Lane
from .resolved_run_profile import ResolvedRunProfile, assert_rerank_preflight


@dataclass
class ManualRawPipeline:
    """Per-lane retriever plus optional agentic wrapper (D5.V+A)."""

    retriever: ManualEvidenceRetriever
    agentic: AgenticRetrievalController | None
    resolved: ResolvedRunProfile
    rank_fn_active: bool


def build_manual_raw_pipeline(
    lane: Lane,
    resolved: ResolvedRunProfile,
    *,
    embed_cfg: dict[str, Any],
    top_k: int,
    page_prefix_chars: int,
    raw_rag_cfg: dict[str, Any],
    answer_llm_cfg: dict[str, Any] | None = None,
    generate_fn: Any | None = None,
) -> ManualRawPipeline:
    """Wire D3 engine and D5 stack from ResolvedRunProfile (single call site for runner)."""
    rerank_llm = (raw_rag_cfg.get("rerank") or {}).get("llm") if isinstance(raw_rag_cfg.get("rerank"), dict) else {}
    if not isinstance(rerank_llm, dict) or not rerank_llm:
        rerank_llm = dict(answer_llm_cfg or {})

    rank_fn = rank_fn_for_resolved(
        rerank_enabled=resolved.d5_rerank_enabled,
        backend=resolved.d5_rerank_backend,
        rerank_llm_cfg=rerank_llm,
        generate_fn=generate_fn,
    )
    assert_rerank_preflight(resolved, rank_fn)

    retriever = ManualEvidenceRetriever(
        lane,
        embed_cfg=embed_cfg,
        mode=resolved.d3_engine,
        top_k=top_k,
        page_prefix_chars=page_prefix_chars,
        rank_fn=rank_fn,
    )

    agentic_ctrl: AgenticRetrievalController | None = None
    if resolved.d5_agentic_enabled and resolved.d5_verifier_enabled:
        agentic_ctrl = AgenticRetrievalController(
            retriever, max_loops=resolved.d5_agentic_max_loops
        )

    return ManualRawPipeline(
        retriever=retriever,
        agentic=agentic_ctrl,
        resolved=resolved,
        rank_fn_active=rank_fn is not None,
    )
