"""Gemini embedding API for retail ticket search — real vectors only; fail fast if misconfigured."""

from __future__ import annotations

import json
import math
import os
import urllib.error
import urllib.request
from typing import List

EMBEDDING_DIMENSION = 768


def embedding_model_id() -> str:
    model = (
        os.environ.get("EMBEDDING_MODEL", "").strip()
        or os.environ.get("RETAIL_EMBEDDING_MODEL", "").strip()
    )
    if not model:
        raise RuntimeError(
            "Set EMBEDDING_MODEL=gemini-embedding-2 (or RETAIL_EMBEDDING_MODEL) in repo .env — "
            "retail search does not use mock embeddings."
        )
    return model


def _api_key() -> str:
    key = (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or "").strip()
    if not key:
        raise RuntimeError(
            "Set GEMINI_API_KEY in repo .env — retail embedding calls Gemini and does not fall back to mocks."
        )
    return key


def embed_text(text: str, *, task_type: str = "RETRIEVAL_DOCUMENT") -> List[float]:
    """One Gemini embedContent call; returns EMBEDDING_DIMENSION floats."""
    model = embedding_model_id()
    key = _api_key()
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:embedContent?key={key}"
    )
    body = {
        "content": {"parts": [{"text": text or ""}]},
        "outputDimensionality": EMBEDDING_DIMENSION,
        "taskType": task_type,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            payload = json.load(resp)
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(
            f"Gemini embedContent failed HTTP {e.code} for model {model}: {detail}"
        ) from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Gemini embedContent network error: {e}") from e

    values = payload.get("embedding", {}).get("values")
    if not values:
        raise RuntimeError(f"Gemini embedContent returned no embedding values: {payload!r}")
    if len(values) != EMBEDDING_DIMENSION:
        raise RuntimeError(
            f"Expected {EMBEDDING_DIMENSION} dimensions, got {len(values)} from {model}"
        )
    norm = math.sqrt(sum(v * v for v in values)) or 1.0
    return [float(v) / norm for v in values]


def cosine_distance(a: List[float], b: List[float]) -> float:
    if len(a) != len(b):
        raise ValueError("embedding length mismatch")
    dot = sum(x * y for x, y in zip(a, b))
    return 1.0 - dot
