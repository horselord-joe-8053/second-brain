"""Contract tests for the twenty-question limit-join v2 suite (gold cap + answer cap metadata)."""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SUITE = REPO / "tests/retail_multi_profiles/data/retail-limit-join-v2.json"
V2_IDS = tuple(f"V{i:02d}" for i in range(1, 21))


def _word_count(text: str) -> int:
    return len(text.split())


def test_limit_join_v2_suite_shape() -> None:
    """Twenty rows, bare codes only, gold within 75 words, critical criterion present."""
    data = json.loads(SUITE.read_text(encoding="utf-8"))
    assert data.get("construct") == "limit_join_v2"
    assert data.get("gold_max_words") == 75
    assert data.get("answer_max_words") == 150
    gold_cap = int(data["gold_max_words"])
    ids = [str(q["id"]) for q in data["questions"]]
    assert ids == list(V2_IDS)
    for row in data["questions"]:
        qtext = str(row["question"])
        assert "samsung_RF28K9070SG" not in qtext
        assert "ge_GNE27JYMFS" not in qtext
        answer = str(row["answer"])
        assert _word_count(answer) <= gold_cap, f"{row['id']} gold has {_word_count(answer)} words"
        crit = row.get("criteria") or []
        assert any(isinstance(c, dict) and c.get("critical") for c in crit)


def test_limit_join_v2_answer_prompt_includes_cap() -> None:
    """Insight answers pick up the suite word cap without changing retrieval."""
    from tests.retail_multi_profiles.lib.answer_pipeline import answer_from_context

    called: list[str] = []

    def fake(_prompt: str, **_kw: object) -> str:
        called.append(_prompt)
        return "ok"

    answer_from_context(
        "test?",
        "ctx",
        provider="openai",
        model="gpt-4o-mini",
        insight_mode=True,
        answer_max_words=150,
        generate=fake,
    )
    assert called and "150 words" in called[0]
