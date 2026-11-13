"""Minimal OpenAI chat completions helper for benchmark answer + judge calls."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


def openai_generate(
    prompt: str,
    *,
    model: str,
    temperature: float = 0.0,
    timeout_sec: float = 300.0,
) -> str:
    """Single-turn OpenAI chat completion text."""
    api_key = (os.environ.get("OPENAI_API_KEY") or "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    url = "https://api.openai.com/v1/chat/completions"
    body: dict[str, Any] = {
        "model": model,
        "temperature": temperature,
        "messages": [{"role": "user", "content": prompt}],
    }
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
        raise RuntimeError(f"OpenAI HTTP {e.code}: {detail}") from e
    choices = data.get("choices") or []
    if not choices:
        raise RuntimeError("OpenAI returned no choices")
    msg = choices[0].get("message") or {}
    return str(msg.get("content") or "").strip()
