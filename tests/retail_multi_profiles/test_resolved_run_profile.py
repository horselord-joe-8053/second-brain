"""P1.0b — ResolvedRunProfile merge and D5 flags from YAML."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]


def test_coerce_bool_rejects_string_false() -> None:
    """Regression: bool('false') must not enable agentic."""
    from tests.retail_multi_profiles.lib.config_coerce import coerce_bool

    assert coerce_bool("false") is False
    assert coerce_bool("true") is True


def test_hybrid_profile_d5_off() -> None:
    """MANUAL_B_RAW_HYBRID is D3.R-H with D5.0 when d5 block disables stack."""
    from tests.retail_multi_profiles.lib.resolved_run_profile import resolve_effective_profile
    from tests.retail_multi_profiles.lib.run_config import load_merged_run_config

    cfg = load_merged_run_config(REPO)
    r = resolve_effective_profile(
        cfg,
        profile_id="MANUAL_B_RAW_HYBRID",
        lane_ids=["B"],
    )
    assert r.d3_engine == "hybrid_rrf"
    assert r.d5_rerank_enabled is False
    assert r.d5_verifier_enabled is False
    assert r.d5_agentic_enabled is False


def test_rerank_profile_d5_rva() -> None:
    """MANUAL_B_RAW_HYBRID_RERANK enables D5.R+V+A with default llm_listwise backend."""
    from tests.retail_multi_profiles.lib.resolved_run_profile import resolve_effective_profile
    from tests.retail_multi_profiles.lib.run_config import load_merged_run_config

    cfg = load_merged_run_config(REPO)
    r = resolve_effective_profile(
        cfg,
        profile_id="MANUAL_B_RAW_HYBRID_RERANK",
        lane_ids=["B"],
    )
    assert r.d3_engine == "hybrid_rrf"
    assert r.d5_rerank_enabled is True
    assert r.d5_rerank_backend == "llm_listwise"
    assert r.d5_verifier_enabled is True
    assert r.d5_agentic_enabled is True


def test_global_agentic_string_false_stays_off(monkeypatch: pytest.MonkeyPatch) -> None:
    """Merged config coerces retail_raw_rag.agentic.enabled string false."""
    from tests.retail_multi_profiles.lib.run_config import load_merged_run_config

    cfg = load_merged_run_config(REPO)
    assert cfg["retail_raw_rag"]["agentic"]["enabled"] is False


def test_build_rank_fn_returns_callable() -> None:
    """llm_listwise backend yields rank_fn when generate_fn stubbed."""
    from retail_brain.rerank_registry import build_rank_fn

    def stub(_prompt: str) -> str:
        return '["bbb", "aaa"]'

    fn = build_rank_fn("llm_listwise", llm_cfg={"provider": "openai", "model": "m"}, generate_fn=stub)
    assert fn is not None
    out = fn("q", [{"chunk_id": "aaa"}, {"chunk_id": "bbb"}])
    assert "bbb" in out


def test_preflight_raises_when_rerank_on_without_fn() -> None:
    from tests.retail_multi_profiles.lib.resolved_run_profile import (
        ResolvedRunProfile,
        assert_rerank_preflight,
    )

    r = ResolvedRunProfile(
        profile_id="t",
        retrieval_mode="raw_rag",
        d3_engine="hybrid_rrf",
        lane_ids=["B"],
        d5_rerank_enabled=True,
    )
    with pytest.raises(RuntimeError, match="rank_fn"):
        assert_rerank_preflight(r, None)
