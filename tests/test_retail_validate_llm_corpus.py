"""LLM sim corpus validator."""

import importlib.util
from pathlib import Path


def _load_validator():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "retail" / "seed" / "validate_llm_corpus.py"
    spec = importlib.util.spec_from_file_location("validate_llm_corpus", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


def test_validate_llm_corpus_passes_on_repo_profile() -> None:
    root = Path(__file__).resolve().parents[1]
    src = root / "tmp" / "simulated_data"
    if not (src / "service_queries.csv").is_file():
        return
    vlc = _load_validator()
    assert vlc.validate(src) == []
