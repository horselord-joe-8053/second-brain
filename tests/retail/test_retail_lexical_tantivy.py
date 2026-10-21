"""Tantivy keyword index: temp directory, no Postgres."""

from __future__ import annotations

from pathlib import Path

from retail_brain.lexical_search import rebuild_active
from retail_brain.lexical_search.tantivy_index import TantivyLexicalIndex

ROWS = [
    ("T-1001", "Galaxy A15 battery drains by noon", "Galaxy A15 5G"),
    ("T-1002", "Galaxy A16 screen flicker", "Galaxy A16 5G"),
]


def test_search_returns_matching_ticket(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("RETAIL_LEXICAL_BACKEND", "tantivy")
    monkeypatch.setenv("RETAIL_LEXICAL_INDEX_PATH", str(tmp_path))
    rebuild_active(ROWS)
    ids = TantivyLexicalIndex(tmp_path / "tantivy").search_ids("battery drains", k=5)
    assert ids[0] == "T-1001"


def test_model_filter_excludes_other_model(tmp_path: Path) -> None:
    index = TantivyLexicalIndex(tmp_path / "tantivy")
    index.rebuild(ROWS)
    ids = index.search_ids("Galaxy", k=5, model_filter="Galaxy A16 5G")
    assert ids == ["T-1002"]
