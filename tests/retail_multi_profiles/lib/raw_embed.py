"""Batch text embeddings for raw RAG (harness-owned; no LLM Wiki)."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import Any, Callable


EmbedFn = Callable[[list[str]], list[list[float]]]


def embed_model_id(cfg: dict[str, Any]) -> str:
    """Stable label stored in index metadata."""
    provider = str(cfg.get("provider") or "openai")
    model = str(cfg.get("model") or "text-embedding-3-small")
    return f"{provider}:{model}"


def openai_embed_batch(
    texts: list[str],
    *,
    model: str,
    timeout_sec: float = 120.0,
    dimensions: int | None = None,
) -> list[list[float]]:
    """OpenAI /v1/embeddings for a batch of strings."""
    api_key = (os.environ.get("OPENAI_API_KEY") or "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    url = "https://api.openai.com/v1/embeddings"
    body: dict[str, Any] = {"model": model, "input": texts}
    if dimensions is not None:
        body["dimensions"] = dimensions
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"OpenAI embeddings HTTP {e.code}: {detail}") from e
    rows = data.get("data") or []
    rows.sort(key=lambda r: int(r.get("index", 0)))
    return [list(r.get("embedding") or []) for r in rows]


def embed_texts_batch(
    texts: list[str],
    embed_cfg: dict[str, Any],
    *,
    max_attempts: int = 3,
    batch_size: int = 32,
) -> list[list[float]]:
    """Embed all texts with retries; only OpenAI provider in v1."""
    if not texts:
        return []
    provider = str(embed_cfg.get("provider") or "openai").strip().lower()
    model = str(embed_cfg.get("model") or "text-embedding-3-small")
    timeout = float(embed_cfg.get("timeout_sec") or 120.0)
    batch_size = int(embed_cfg.get("batch_size") or batch_size)
    dims_raw = embed_cfg.get("dimensions")
    dimensions = int(dims_raw) if dims_raw is not None else None

    if provider != "openai":
        raise ValueError(f"raw RAG embedding provider {provider!r} not supported in v1")

    out: list[list[float]] = []
    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]
        last_err: Exception | None = None
        for attempt in range(1, max_attempts + 1):
            try:
                vecs = openai_embed_batch(
                    batch, model=model, timeout_sec=timeout, dimensions=dimensions
                )
                if len(vecs) != len(batch):
                    raise RuntimeError(f"embedding count mismatch {len(vecs)} != {len(batch)}")
                out.extend(vecs)
                break
            except (TimeoutError, OSError, RuntimeError) as e:
                last_err = e
                if attempt >= max_attempts:
                    raise
                time.sleep(min(2.0 * attempt, 8.0))
        else:
            if last_err:
                raise last_err
    return out
