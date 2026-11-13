"""Checks for the five-question news briefing smoke fixture and its result rows."""

from __future__ import annotations

from typing import Any

NEWS_IDS = ("N01", "N02", "N03", "N04", "N05")
WIKI_NEWS_PREFIX = "wiki/sources/13-fridge-newsmd--"
BUNDLED_NEWS_PREFIX = "raw/sources/fridge-news_md/"
_RESULT_FIELDS = (
    "correctness_confidence",
    "top_hit_paths",
    "retrieval_ms",
    "context_chars",
    "elapsed_ms",
)


def validate_news_briefing_suite(data: dict[str, Any]) -> None:
    """Require five smoke rows whose gold answers still contain the required point."""
    if data.get("schema_version") != "news_briefing_smoke.v1":
        raise ValueError(f"unsupported schema_version: {data.get('schema_version')!r}")
    if data.get("status") != "smoke":
        raise ValueError("news briefing suite status must be smoke")
    hits = data.get("expected_hits") or {}
    if hits.get("wiki_prefix") != WIKI_NEWS_PREFIX or hits.get("bundled_prefix") != BUNDLED_NEWS_PREFIX:
        raise ValueError("expected news hit prefixes are missing")
    questions = data.get("questions")
    if not isinstance(questions, list):
        raise ValueError("questions must be a list")
    ids = [str(row.get("id") or "") for row in questions]
    if ids != list(NEWS_IDS):
        raise ValueError(f"question ids must be {list(NEWS_IDS)}, got {ids}")
    for row in questions:
        point = str(row.get("required_point") or "").strip()
        answer = str(row.get("answer") or "")
        qid = str(row.get("id") or "")
        if not point or point.casefold() not in answer.casefold():
            raise ValueError(f"{qid} gold answer drops the required point")
        criteria = row.get("criteria") or []
        if not any(isinstance(item, dict) and item.get("critical") for item in criteria):
            raise ValueError(f"{qid} needs one critical criterion")


def news_page_opened(paths: list[str], prefix: str) -> bool:
    """True when one of the top hits is a news page under the expected prefix."""
    needle = prefix.casefold()
    return any(needle in str(path).casefold() for path in paths)


def assert_smoke_result_row(row: dict[str, Any]) -> None:
    """Reject a smoke result that cannot report confidence, hits, or retrieval time."""
    for field in _RESULT_FIELDS:
        if field not in row:
            raise ValueError(f"smoke result missing {field}")
    confidence = float(row["correctness_confidence"])
    if not 0.0 <= confidence <= 1.0:
        raise ValueError("correctness_confidence must be between 0 and 1")
    if not isinstance(row["top_hit_paths"], list):
        raise ValueError("top_hit_paths must be a list")
