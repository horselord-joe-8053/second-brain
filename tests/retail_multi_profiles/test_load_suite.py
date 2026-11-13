"""Contract tests for TYPE_A_M90 / M90-technical-singlefact suite loader."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.retail_multi_profiles.lib.eval_suites import TYPE_A_M90, TYPE_A_M90_LONG
from tests.retail_multi_profiles.lib.load_suite import iter_questions, load_suite

REPO = Path(__file__).resolve().parents[2]
SUITE = REPO / "tests/retail_multi_profiles/data/retail-manual-qa-test-suite.json"


def test_load_suite_has_ninety_questions() -> None:
    """Vendored retail manual QA suite must expose 90 questions."""
    data = load_suite(SUITE)
    assert data.get("eval_suite_id") == TYPE_A_M90
    assert data.get("eval_suite_long_name") == TYPE_A_M90_LONG
    rows = list(iter_questions(data))
    assert len(rows) == 90


def test_load_suite_rejects_bad_schema(tmp_path: Path) -> None:
    """Invalid schema_version fails fast."""
    bad = tmp_path / "bad.json"
    bad.write_text('{"schema_version": "9.9", "models": []}', encoding="utf-8")
    with pytest.raises(ValueError, match="schema_version"):
        load_suite(bad)
