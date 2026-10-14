"""Simulated-data profile resolution (prag_gen vs llm_gen)."""

import pytest

from retail_brain.sim_data_profile import (
    DEFAULT_PROFILE,
    RRF_DATA_LLM_GEN,
    RRF_DATA_LLM_GEN_1K,
    RRF_DATA_LLM_GEN_60_10,
    RRF_DATA_PRAG_GEN,
    repo_root,
    resolve_sim_data_profile,
)


def test_default_profile_is_1k(monkeypatch: pytest.MonkeyPatch) -> None:
    """Scale branch defaults to the 1000/100 profile."""
    monkeypatch.delenv("RETAIL_SIM_DATA_PROFILE", raising=False)
    assert resolve_sim_data_profile().profile_id == DEFAULT_PROFILE == RRF_DATA_LLM_GEN_1K


def test_prag_gen_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RETAIL_SIM_DATA_PROFILE", RRF_DATA_PRAG_GEN)
    prof = resolve_sim_data_profile()
    root = repo_root()
    assert prof.service_queries_csv == root / "scripts/retail/seed/generated/service_queries.csv"
    assert prof.reports_dir == root / "scripts/retail/eval/reports/prag_gen"


def test_llm_gen_60_10_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RETAIL_SIM_DATA_PROFILE", RRF_DATA_LLM_GEN_60_10)
    prof = resolve_sim_data_profile()
    root = repo_root()
    p = root / "scripts/retail/sim_data/profiles/data_60_10"
    assert prof.service_queries_csv == p / "service_queries.csv"
    assert prof.reports_dir == p / "reports"


def test_llm_gen_alias_maps_to_60_10(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RETAIL_SIM_DATA_PROFILE", RRF_DATA_LLM_GEN)
    prof = resolve_sim_data_profile()
    assert prof.profile_id == RRF_DATA_LLM_GEN_60_10


def test_llm_gen_1k_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RETAIL_SIM_DATA_PROFILE", RRF_DATA_LLM_GEN_1K)
    prof = resolve_sim_data_profile()
    root = repo_root()
    p = root / "scripts/retail/sim_data/profiles/data_1000_100"
    assert prof.service_queries_csv == p / "service_queries.csv"


def test_unknown_profile_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RETAIL_SIM_DATA_PROFILE", "invalid")
    with pytest.raises(ValueError, match="Unknown RETAIL_SIM_DATA_PROFILE"):
        resolve_sim_data_profile()
