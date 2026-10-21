"""LLM sim corpus validator."""

import importlib.util
from pathlib import Path


def _load_validator():
    root = Path(__file__).resolve().parents[2]
    path = root / "scripts" / "retail" / "seed" / "validate_llm_corpus.py"
    spec = importlib.util.spec_from_file_location("validate_llm_corpus", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


def test_validate_llm_corpus_passes_on_repo_profiles() -> None:
    root = Path(__file__).resolve().parents[2]
    vlc = _load_validator()
    for name in ("data_60_10", "data_1000_100"):
        src = root / "scripts" / "retail" / "sim_data" / "profiles" / name
        if not (src / "service_queries.csv").is_file():
            continue
        assert vlc.validate(src) == []
