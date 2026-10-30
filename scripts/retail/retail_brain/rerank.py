"""Rerank helpers for retrieval candidates (manual + ticket pools).

``listwise_rerank`` asks a chat model for an id order. ``cross_encoder_rerank``
scores the question with each chunk using a local cross-encoder.
"""

from __future__ import annotations

import json
import re
import time
from typing import Any, Callable, Sequence

RankFn = Callable[[str, Sequence[dict[str, Any]]], list[str]]
ScoreFn = Callable[[str, Sequence[dict[str, Any]]], Sequence[float]]

# Small English cross-encoder used by the B20 manual rerank probe.
CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
MANUAL_RERANK_CANDIDATE_N = 20
# Two per subquery so a later unit is not crowded out of the answer text.
MANUAL_RERANK_KEEP = 2
MANUAL_RERANK_CONTEXT_CHARS = 10000

_cross_encoder_models: dict[str, Any] = {}


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


def cross_encoder_rerank(
    query: str,
    candidates: Sequence[dict[str, Any]],
    *,
    score_fn: ScoreFn,
    max_candidates: int = MANUAL_RERANK_CANDIDATE_N,
) -> list[dict[str, Any]]:
    """Reorder candidates by score_fn(query, rows); higher score first, ties keep input order."""
    pool = list(candidates[:max_candidates])
    if not pool:
        return []
    scores = list(score_fn(query, pool))
    if len(scores) != len(pool):
        raise ValueError("cross-encoder score_fn must return one score per candidate")
    order = sorted(range(len(pool)), key=lambda i: (-float(scores[i]), i))
    return [pool[i] for i in order]


def build_cross_encoder_score_fn(model_name: str = CROSS_ENCODER_MODEL) -> ScoreFn:
    """Return a batched scorer. MiniLM weights load on the first call and stay cached."""

    def score(query: str, rows: Sequence[dict[str, Any]]) -> list[float]:
        """Score each row's text against the query; load MiniLM once per model name."""
        model = _cross_encoder_models.get(model_name)
        if model is None:
            from sentence_transformers import CrossEncoder

            model = CrossEncoder(model_name)
            _cross_encoder_models[model_name] = model
        pairs = [(query, str(row.get("text") or "")) for row in rows]
        if not pairs:
            return []
        # Torch 2.2 on this Mac cannot call .numpy() under NumPy 2. Stay on tensors.
        raw = model.predict(
            pairs,
            show_progress_bar=False,
            convert_to_numpy=False,
            convert_to_tensor=True,
        )
        flat = raw.detach().float().cpu().reshape(-1)
        return [float(value) for value in flat.tolist()]

    return score


def rerank_manual_candidates(
    query: str,
    rows: Sequence[dict[str, Any]],
    *,
    backend: str,
    keep: int = 5,
    score_fn: ScoreFn | None = None,
    rank_fn: RankFn | None = None,
    model_id: str = "",
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Rerank one manual-unit pool and return the kept rows plus trace fields."""
    pool = list(rows)
    pre_ids = [str(row.get("chunk_id") or "") for row in pool]
    started = time.perf_counter()
    if backend == "cross_encoder":
        active = score_fn or build_cross_encoder_score_fn(model_id or CROSS_ENCODER_MODEL)
        model_id = model_id or CROSS_ENCODER_MODEL
        ordered = cross_encoder_rerank(query, pool, score_fn=active)
    elif backend == "llm_listwise":
        ordered = listwise_rerank(
            query,
            pool,
            rank_fn=rank_fn,
            max_candidates=max(len(pool), 1),
        )
    else:
        ordered = pool
    kept = list(ordered[: max(0, int(keep))])
    meta = {
        "rerank_backend": backend,
        "rerank_model": model_id,
        "candidate_count": len(pool),
        "rerank_ms": int((time.perf_counter() - started) * 1000),
        "pre_rerank_chunk_ids": pre_ids,
        "post_rerank_chunk_ids": [str(row.get("chunk_id") or "") for row in kept],
    }
    return kept, meta
