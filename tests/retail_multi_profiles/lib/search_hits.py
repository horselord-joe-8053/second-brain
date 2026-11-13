"""Compact LLM Wiki search hits for benchmark JSONL (rank signals, no page body)."""

from __future__ import annotations

from typing import Any


def is_wiki_source_path(path: str) -> bool:
    """True when the hit lives under the wiki sources tree."""
    normalized = (path or "").replace("\\", "/").lstrip("/")
    return normalized.startswith("wiki/sources/") or "/wiki/sources/" in f"/{normalized}"


def source_only_hits(hits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Drop entity, concept, and index hits; keep wiki/sources pages in rank order."""
    return [hit for hit in hits if is_wiki_source_path(str(hit.get("path") or ""))]


def compact_search_hit(hit: dict[str, Any]) -> dict[str, Any]:
    """Keep fused score, vector score, and title match from one API hit."""
    compact: dict[str, Any] = {
        "path": hit.get("path"),
        "title": hit.get("title"),
        "score": hit.get("score"),
        "vector_score": hit.get("vectorScore", hit.get("vector_score")),
        "title_match": hit.get("titleMatch", hit.get("title_match")),
    }
    graph = hit.get("graphRelatedTo", hit.get("graph_related_to"))
    if graph:
        compact["graph_related_to"] = graph
    return compact


def compact_search_hits(hits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Compact every hit in rank order."""
    return [compact_search_hit(hit) for hit in hits]
