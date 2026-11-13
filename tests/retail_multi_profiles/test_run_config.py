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
    assert cfg["k_manuals"] == 5
    assert cfg["k_tickets"] == 2
    assert cfg["page_prefix_chars"] == 8000
    assert cfg["context_max_chars_per_chunk"] == 2000
    assert "{model_id}" in cfg["query_template"]
    assert cfg["insufficient_literal"] == "Insufficient_Information_Based_On_Given_PDF"
    assert cfg["answer"]["provider"] == "openai"
    assert cfg["answer"]["model"] == "gpt-4o-mini"
    assert cfg["judge"]["provider"] == "gemini"
    assert cfg["retail_raw_rag"]["embedding"]["model"] == "text-embedding-3-small"
    assert "MANUAL_B_RAW_HYBRID" in (cfg.get("run_profiles") or {})
    assert "MANUAL_B_RAW_PG_HYBRID" in (cfg.get("run_profiles") or {})
    assert cfg.get("default_run_profile") == "MANUAL_B_RAW_PG_HYBRID_RERANK"


def test_effective_run_profile_id_hg_p1_default() -> None:
    """Omitting --profile on raw_rag uses default_run_profile (HG-P1); wiki stays unset."""
    from tests.retail_multi_profiles.lib.run_config import load_merged_run_config
    from tests.retail_multi_profiles.lib.run_profiles import effective_run_profile_id

    cfg = load_merged_run_config(REPO)
    assert (
        effective_run_profile_id(cfg, cli_profile="", retrieval_mode="raw_rag")
        == "MANUAL_B_RAW_PG_HYBRID_RERANK"
    )
    assert effective_run_profile_id(cfg, cli_profile="", retrieval_mode="llm_wiki") == ""
    assert (
        effective_run_profile_id(cfg, cli_profile="MANUAL_B_RAW_HYBRID", retrieval_mode="raw_rag")
        == "MANUAL_B_RAW_HYBRID"
    )


def test_pg_run_profile_sets_manual_d3_backend() -> None:
    """PG A/B profiles select manual_d3_backend=pg in ResolvedRunProfile."""
    from tests.retail_multi_profiles.lib.resolved_run_profile import resolve_effective_profile
    from tests.retail_multi_profiles.lib.run_config import load_merged_run_config

    cfg = load_merged_run_config(REPO)
    resolved = resolve_effective_profile(
        cfg,
        profile_id="MANUAL_B_RAW_PG_HYBRID_RERANK",
        lane_ids=["B"],
        retrieval_mode="raw_rag",
    )
    assert resolved.manual_d3_backend == "pg"
    assert resolved.d5_rerank_enabled is True


def test_lane_b_hybrid_rerank_profile_uses_pg_backend() -> None:
    """After P5 cutover, legacy profile ids on Lane B resolve to manual_d3_backend=pg."""
    from tests.retail_multi_profiles.lib.resolved_run_profile import resolve_effective_profile
    from tests.retail_multi_profiles.lib.run_config import load_merged_run_config

    cfg = load_merged_run_config(REPO)
    resolved = resolve_effective_profile(
        cfg,
        profile_id="MANUAL_B_RAW_HYBRID_RERANK",
        lane_ids=["B"],
        retrieval_mode="raw_rag",
    )
    assert resolved.manual_d3_backend == "pg"


def test_run_profile_resolves_raw_flags() -> None:
    """P1.0 — profile id maps to retrieval_mode and raw_retrieval."""
    from tests.retail_multi_profiles.lib.run_config import load_merged_run_config
    from tests.retail_multi_profiles.lib.run_profiles import resolve_run_profile

    cfg = load_merged_run_config(REPO)
    prof = resolve_run_profile(cfg, "MANUAL_B_RAW_HYBRID_RERANK")
    assert prof["retrieval_mode"] == "raw_rag"
    assert prof["raw_retrieval"] == "hybrid_rrf"
    assert prof["lanes"] == "B"
    from tests.retail_multi_profiles.lib.config_coerce import coerce_bool

    assert coerce_bool(prof["d5"]["rerank"]["enabled"]) is True


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
