"""Env overrides for answer (OpenAI) vs judge (Gemini)."""

from __future__ import annotations

import os

from tests.retail_multi_profiles.lib.eval_models import resolve_eval_llms


def test_openai_model_env_overrides_answer(monkeypatch) -> None:
    """OPENAI_MODEL wins for openai answer provider."""
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    cfg = {
        "answer": {"provider": "openai", "model": "gpt-4o-mini", "temperature": 0},
        "judge": {"provider": "gemini", "model": "gemini-3.1-flash-lite", "temperature": 0},
    }
    ans, judge = resolve_eval_llms(cfg)
    assert ans.provider == "openai"
    assert ans.model == "gpt-4o-mini"
    assert judge.provider == "gemini"


def test_retail_judge_model_override(monkeypatch) -> None:
    """RETAIL_JUDGE_MODEL applies to judge step regardless of provider."""
    monkeypatch.setenv("RETAIL_JUDGE_MODEL", "custom-judge")
    cfg = {
        "answer": {"provider": "openai", "model": "gpt-4o-mini"},
        "judge": {"provider": "gemini", "model": "gemini-3.1-flash-lite"},
    }
    _, judge = resolve_eval_llms(cfg)
    assert judge.model == "custom-judge"
