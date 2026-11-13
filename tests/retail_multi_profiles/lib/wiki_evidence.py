"""Harness-only wiki hit filters (sources_only / rerank) after LLM Wiki search."""

from __future__ import annotations

from typing import Any, Callable

from .search_hits import is_wiki_source_path, source_only_hits

RankFn = Callable[[str, list[dict[str, Any]]], list[dict[str, Any]]]


def apply_wiki_evidence_mode(
    hits: list[dict[str, Any]],
    *,
    mode: str,
    sources_prefix: str = "wiki/sources/",
    rank_fn: RankFn | None = None,
) -> list[dict[str, Any]]:
    """Filter and optionally rerank wiki search hits before page read."""
    mode = (mode or "full").strip().lower()
    out = list(hits)
    if mode in ("sources_only", "sources_rerank"):
        out = source_only_hits(out)
        if sources_prefix:
            prefix = sources_prefix.strip("/")
            out = [
                h
                for h in out
                if str(h.get("path") or "").replace("\\", "/").startswith(prefix)
                or is_wiki_source_path(str(h.get("path") or ""))
            ]
    if mode == "sources_rerank" and rank_fn is not None and out:
        out = rank_fn("", out)
    elif mode == "sources_rerank" and out:
        out = sorted(out, key=lambda h: float(h.get("score") or 0.0), reverse=True)
    return out


def wiki_evidence_settings(cfg: dict[str, Any]) -> dict[str, Any]:
    """Normalize ``wiki_evidence`` block from merged run-config."""
    block = cfg.get("wiki_evidence") or {}
    if not isinstance(block, dict):
        block = {}
    mode = str(block.get("mode") or "full").strip().lower()
    return {
        "mode": mode,
        "sources_prefix": str(block.get("sources_prefix") or "wiki/sources/"),
        "rerank": bool(block.get("rerank")),
    }
