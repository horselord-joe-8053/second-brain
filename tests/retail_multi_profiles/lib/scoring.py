"""Tiered scoring: exact insufficient literal or Gemini judge."""

from __future__ import annotations

import re

from .llm_generate import llm_generate


def normalize_insufficient(text: str) -> str:
    """Collapse whitespace for negative-item exact match."""
    return re.sub(r"\s+", " ", (text or "").strip()).lower()


def score_negative(candidate: str, *, literal: str) -> tuple[bool, str]:
    """Pass when candidate matches the insufficient-information literal."""
    ok = normalize_insufficient(candidate) == normalize_insufficient(literal)
    return ok, "exact insufficient literal" if ok else "expected insufficient literal"


def score_judged(
    question: str,
    gold: str,
    candidate: str,
    *,
    provider: str,
    model: str,
    temperature: float = 0.0,
) -> tuple[bool, str]:
    """LLM-as-judge: factual consistency with gold, paraphrase OK."""
    prompt = (
        "You are a strict grader. Reply with JSON only: "
        '{"pass": true|false, "rationale": "one sentence"}\n'
        f"Question: {question}\nGold answer: {gold}\nCandidate answer: {candidate}\n"
        "Pass if the candidate is factually consistent with the gold and does not add unsupported claims."
    )
    raw = llm_generate(prompt, provider=provider, model=model, temperature=temperature)
    try:
        import json

        parsed = json.loads(raw.strip().strip("`").removeprefix("json"))
        return bool(parsed.get("pass")), str(parsed.get("rationale") or raw)
    except Exception:
        ok = "true" in raw.lower() and "pass" in raw.lower()
        return ok, raw[:300]
