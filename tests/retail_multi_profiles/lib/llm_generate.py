"""Route benchmark LLM calls by provider (openai | gemini) with retries."""

from __future__ import annotations

import time

from .llm_gemini import gemini_generate
from .llm_openai import openai_generate


def llm_generate(
    prompt: str,
    *,
    provider: str,
    model: str,
    temperature: float = 0.0,
    timeout_sec: float = 300.0,
    max_attempts: int = 3,
) -> str:
    """Dispatch to the configured provider; retry transient timeouts."""
    p = (provider or "gemini").strip().lower()
    last_err: Exception | None = None
    for attempt in range(1, max(1, max_attempts) + 1):
        try:
            if p == "openai":
                return openai_generate(
                    prompt, model=model, temperature=temperature, timeout_sec=timeout_sec
                )
            if p == "gemini":
                return gemini_generate(
                    prompt, model=model, temperature=temperature, timeout_sec=timeout_sec
                )
            raise ValueError(f"unsupported LLM provider {provider!r}; use openai or gemini")
        except (TimeoutError, OSError) as e:
            last_err = e
            if attempt >= max_attempts:
                break
            time.sleep(min(2.0 * attempt, 8.0))
    assert last_err is not None
    raise last_err
