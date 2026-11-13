"""Minimal Gemini generateContent helper for answer + judge calls."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


def gemini_generate(
    prompt: str,
    *,
    model: str,
    temperature: float = 0.0,
    timeout_sec: float = 300.0,
) -> str:
    """Single-turn Gemini text generation."""
    api_key = (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )
    body: dict[str, Any] = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature},
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"Gemini HTTP {e.code}: {detail}") from e
    parts = (((data.get("candidates") or [{}])[0].get("content") or {}).get("parts") or [])
    return "\n".join(str(p.get("text") or "") for p in parts if isinstance(p, dict)).strip()
