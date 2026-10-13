"""bm25x keyword index on Python 3.12. Same contract as Tantivy."""

from __future__ import annotations

from pathlib import Path

from retail_brain.lexical_search.bm25x_index import Bm25xLexicalIndex

ROWS = [
    ("T-1001", "Galaxy A15 battery drains by noon", "Galaxy A15 5G"),
    ("T-1002", "Galaxy A16 screen flicker", "Galaxy A16 5G"),
]


def test_search_returns_matching_ticket(tmp_path: Path) -> None:
    index = Bm25xLexicalIndex(tmp_path / "bm25x")
    index.rebuild(ROWS)
    reloaded = Bm25xLexicalIndex(tmp_path / "bm25x")
    ids = reloaded.search_ids("battery drains", k=5)
    assert ids[0] == "T-1001"


def test_model_filter_excludes_other_model(tmp_path: Path) -> None:
    index = Bm25xLexicalIndex(tmp_path / "bm25x")
    index.rebuild(ROWS)
    ids = index.search_ids("Galaxy battery screen", k=5, model_filter="Galaxy A16 5G")
    assert ids == ["T-1002"]
