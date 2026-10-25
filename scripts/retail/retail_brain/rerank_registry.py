"""Build D5.R rank_fn callables from harness config (llm_listwise default)."""

from __future__ import annotations

import json
from typing import Any, Callable, Sequence

RankFn = Callable[[str, Sequence[dict[str, Any]]], str]


def candidate_row_id(row: dict[str, Any]) -> str:
    """Stable id for manual chunks or ticket rows (ticket_id wins when both present)."""
    if row.get("ticket_id"):
        return str(row["ticket_id"])
    return str(row.get("chunk_id") or row.get("id") or "")


def candidate_row_snippet(row: dict[str, Any], *, max_len: int = 500) -> str:
    """Text shown to listwise LLM — manual chunk text or ticket intake + resolution."""
    if row.get("text"):
        return str(row["text"])[:max_len].replace("\n", " ")
    parts = [str(row.get("customer_query_text") or "")]
    res = str(row.get("resolution_text") or "").strip()
    if res:
        parts.append(f"Resolution: {res}")
    return " ".join(parts)[:max_len].replace("\n", " ")


def _listwise_prompt(query: str, candidates: Sequence[dict[str, Any]]) -> str:
    """Compact listwise rerank prompt — JSON array of ids (chunk_id or ticket_id)."""
    pool = "tickets" if any(c.get("ticket_id") for c in candidates) else "manual chunks"
    lines = [
        f"Rank the following {pool} by relevance to the query.",
        "Reply with ONLY a JSON array of id strings, best first.",
        f"Query: {query}",
        "Candidates:",
    ]
    for row in candidates:
        cid = candidate_row_id(row)
        snippet = candidate_row_snippet(row)
        lines.append(f"- id={cid} text={snippet!r}")
    return "\n".join(lines)


def build_rank_fn(
    backend: str,
    *,
    llm_cfg: dict[str, Any],
    generate_fn: Any | None = None,
) -> RankFn | None:
    """Return rank_fn for D5.R backend, or None when rerank is off / unsupported."""
    b = (backend or "llm_listwise").strip().lower()
    if b != "llm_listwise":
        return None

    provider = str(llm_cfg.get("provider") or "openai")
    model = str(llm_cfg.get("model") or "gpt-4o-mini")
    temperature = float(llm_cfg.get("temperature") or 0)

    def _rank(query: str, candidates: Sequence[dict[str, Any]]) -> str:
        prompt = _listwise_prompt(query, candidates)
        if generate_fn is not None:
            return str(generate_fn(prompt))
        from tests.retail_multi_profiles.lib.llm_generate import llm_generate

        return llm_generate(
            prompt,
            provider=provider,
            model=model,
            temperature=temperature,
        )

    return _rank


def rank_fn_for_resolved(
    *,
    rerank_enabled: bool,
    backend: str,
    rerank_llm_cfg: dict[str, Any],
    generate_fn: Any | None = None,
) -> RankFn | None:
    """Harness helper — None when D5.R disabled."""
    if not rerank_enabled:
        return None
    fn = build_rank_fn(backend, llm_cfg=rerank_llm_cfg, generate_fn=generate_fn)
    return fn
