"""Resolve answer/judge provider, model, and temperature from merged config + env."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class EvalLlm:
    """One eval LLM step (answer or judge)."""

    provider: str
    model: str
    temperature: float


def _block(cfg: dict[str, Any], key: str) -> dict[str, Any]:
    """Named retail_eval subsection as a dict."""
    raw = cfg.get(key) or {}
    return raw if isinstance(raw, dict) else {}


def resolve_eval_llms(cfg: dict[str, Any]) -> tuple[EvalLlm, EvalLlm]:
    """Apply env overrides: OPENAI_MODEL / GEMINI_MODEL (answer), RETAIL_JUDGE_MODEL (judge)."""
    ans = _block(cfg, "answer")
    judge = _block(cfg, "judge")
    ans_provider = str(ans.get("provider") or "gemini").strip().lower()
    judge_provider = str(judge.get("provider") or ans_provider).strip().lower()

    ans_model = str(ans.get("model") or "gpt-4o-mini").strip()
    if ans_provider == "openai":
        ans_model = (os.environ.get("OPENAI_MODEL") or ans_model).strip()
    else:
        ans_model = (os.environ.get("GEMINI_MODEL") or ans_model).strip()

    judge_model = str(judge.get("model") or ans_model).strip()
    override_judge = (os.environ.get("RETAIL_JUDGE_MODEL") or "").strip()
    if override_judge:
        judge_model = override_judge

    ans_temp = float(ans.get("temperature") if ans.get("temperature") is not None else 0)
    judge_temp = float(judge.get("temperature") if judge.get("temperature") is not None else 0)
    return (
        EvalLlm(provider=ans_provider, model=ans_model, temperature=ans_temp),
        EvalLlm(provider=judge_provider, model=judge_model, temperature=judge_temp),
    )
