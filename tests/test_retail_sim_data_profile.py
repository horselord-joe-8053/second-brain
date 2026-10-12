"""Simulated-data profile resolution (prag_gen vs llm_gen)."""

import os

import pytest

from retail_brain.sim_data_profile import (
    DEFAULT_PROFILE,
    RRF_DATA_LLM_GEN,
    RRF_DATA_PRAG_GEN,
    repo_root,
    resolve_sim_data_profile,
)


def test_default_profile_is_llm_gen(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("RETAIL_SIM_DATA_PROFILE", raising=False)
    assert resolve_sim_data_profile().profile_id == DEFAULT_PROFILE == RRF_DATA_LLM_GEN


def test_prag_gen_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RETAIL_SIM_DATA_PROFILE", RRF_DATA_PRAG_GEN)
    prof = resolve_sim_data_profile()
    root = repo_root()
    assert prof.service_queries_csv == root / "scripts/retail/seed/generated/service_queries.csv"
    assert prof.reports_dir == root / "scripts/retail/eval/reports/prag_gen"


def test_llm_gen_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RETAIL_SIM_DATA_PROFILE", RRF_DATA_LLM_GEN)
    prof = resolve_sim_data_profile()
    root = repo_root()
    assert prof.service_queries_csv == root / "tmp/simulated_data/service_queries.csv"
    assert prof.reports_dir == root / "tmp/simulated_data/reports"


def test_unknown_profile_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RETAIL_SIM_DATA_PROFILE", "invalid")
    with pytest.raises(ValueError, match="Unknown RETAIL_SIM_DATA_PROFILE"):
        resolve_sim_data_profile()
