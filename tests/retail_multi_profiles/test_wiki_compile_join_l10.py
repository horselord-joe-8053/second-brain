"""Contract tests for wiki compilation join suite (multi-layer gold, no news-only)."""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SUITE = REPO / "tests/retail_multi_profiles/data/retail-wiki-compile-join-l10.json"
M_IDS = tuple(f"M{i:02d}" for i in range(1, 11))


def _word_count(text: str) -> int:
    return len(text.split())


def test_wiki_compile_join_suite_shape() -> None:
    """Ten rows, multi wiki layer provenance, gold within 75 words."""
    data = json.loads(SUITE.read_text(encoding="utf-8"))
    assert data.get("construct") == "wiki_compile_join"
    assert data.get("gold_max_words") == 75
    assert data.get("answer_max_words") == 150
    gold_cap = int(data["gold_max_words"])
    ids = [str(q["id"]) for q in data["questions"]]
    assert ids == list(M_IDS)
    for row in data["questions"]:
        layers = row.get("gold_wiki_layers") or []
        assert len(layers) >= 2, f"{row['id']} needs at least two wiki layers"
        for path in layers:
            assert path.startswith("wiki/"), path
            assert "newsmd" not in path and "fridge-news" not in path
        answer = str(row["answer"])
        assert _word_count(answer) <= gold_cap, f"{row['id']} gold has {_word_count(answer)} words"
        crit = row.get("criteria") or []
        assert any(isinstance(c, dict) and c.get("critical") for c in crit)
