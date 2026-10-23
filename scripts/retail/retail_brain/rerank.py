"""Listwise LLM rerank for retrieval candidates (manual + ticket pools)."""

from __future__ import annotations

import json
import re
from typing import Any, Callable, Sequence

RankFn = Callable[[str, Sequence[dict[str, Any]]], list[str]]


def _default_id(row: dict[str, Any]) -> str:
    return str(row.get("chunk_id") or row.get("ticket_id") or row.get("id") or "")


def parse_ranked_ids_from_llm(text: str, *, valid_ids: set[str]) -> list[str]:
    """Extract ordered ids from JSON array or line-delimited model output."""
    text = (text or "").strip()
    if not text:
        return []
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return [str(x) for x in parsed if str(x) in valid_ids]
    except json.JSONDecodeError:
        pass
    ids: list[str] = []
    for line in text.splitlines():
        token = line.strip().strip(",").strip('"')
        if token in valid_ids and token not in ids:
            ids.append(token)
    if ids:
        return ids
    for token in re.findall(r"[a-f0-9]{16,32}", text):
        if token in valid_ids and token not in ids:
            ids.append(token)
    return ids


def listwise_rerank(
    query: str,
    candidates: Sequence[dict[str, Any]],
    *,
    rank_fn: RankFn | None = None,
    id_fn: Callable[[dict[str, Any]], str] = _default_id,
    max_candidates: int = 20,
) -> list[dict[str, Any]]:
    """Return candidates reordered by listwise ranker; unknown ids trail in original order."""
    if not candidates:
        return []
    pool = list(candidates[:max_candidates])
    if rank_fn is None:
        return pool
    valid = {id_fn(r) for r in pool if id_fn(r)}
    if not valid:
        return pool
    ordered_ids = parse_ranked_ids_from_llm(rank_fn(query, pool), valid_ids=valid)
    by_id = {id_fn(r): r for r in pool}
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for cid in ordered_ids:
        if cid in by_id and cid not in seen:
            out.append(by_id[cid])
            seen.add(cid)
    for r in pool:
        cid = id_fn(r)
        if cid not in seen:
            out.append(r)
            seen.add(cid)
    return out
