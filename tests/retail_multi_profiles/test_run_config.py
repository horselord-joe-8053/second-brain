"""Merge brain-stack retail evidence defaults with harness eval overrides."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]


def test_merged_config_includes_evidence_from_brain_stack_example() -> None:
    """Shared retrieval knobs live in brain-stack.example.yaml, not only run-config."""
    from tests.retail_multi_profiles.lib.run_config import load_merged_run_config

    cfg = load_merged_run_config(REPO)
    assert cfg["search_top_k"] == 5
    assert cfg["page_prefix_chars"] == 8000
    assert "{model_id}" in cfg["query_template"]
    assert cfg["insufficient_literal"] == "Insufficient_Information_Based_On_Given_PDF"
    assert cfg["answer"]["provider"] == "openai"
    assert cfg["answer"]["model"] == "gpt-4o-mini"
    assert cfg["judge"]["provider"] == "gemini"
    assert cfg["retail_raw_rag"]["embedding"]["model"] == "text-embedding-3-small"


def test_run_config_eval_overrides_answer_model(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Harness run-config retail_eval wins over example defaults for judge/answer."""
    from tests.retail_multi_profiles.lib import run_config as rc

    fake = tmp_path / "run-config.yaml"
    fake.write_text(
        'schema_version: "1.0"\n'
        "retail_eval:\n"
        "  answer:\n"
        "    model: custom-answer-model\n"
        "  judge:\n"
        "    model: custom-judge-model\n",
        encoding="utf-8",
    )
    cfg = rc.load_merged_run_config(REPO, run_config_path=fake)
    assert cfg["answer"]["model"] == "custom-answer-model"
    assert cfg["judge"]["model"] == "custom-judge-model"
