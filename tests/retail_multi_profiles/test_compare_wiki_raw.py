"""Tests for wiki vs raw comparison report."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.retail_multi_profiles.lib.compare_wiki_raw import compare_runs, write_compare_markdown


def test_compare_missing_wiki(tmp_path: Path) -> None:
    """P6: missing baseline raises."""
    raw = tmp_path / "raw.json"
    raw.write_text(json.dumps({"rows": []}), encoding="utf-8")
    with pytest.raises(FileNotFoundError):
        compare_runs(tmp_path / "missing.json", raw)


def test_compare_delta_table(tmp_path: Path) -> None:
    """Fixture pair produces lane delta row."""
    wiki = tmp_path / "wiki.json"
    raw = tmp_path / "raw.json"
    wiki.write_text(
        json.dumps(
            {
                "run_id": "wiki1",
                "rows": [
                    {"lane": "B", "difficulty": "easy", "pass": True},
                    {"lane": "B", "difficulty": "hard", "pass": False},
                ],
            }
        ),
        encoding="utf-8",
    )
    raw.write_text(
        json.dumps(
            {
                "run_id": "raw1",
                "rows": [
                    {"lane": "B", "difficulty": "easy", "pass": True},
                    {"lane": "B", "difficulty": "hard", "pass": True},
                ],
            }
        ),
        encoding="utf-8",
    )
    payload = compare_runs(wiki, raw)
    assert payload["lanes"][0]["lane"] == "B"
    assert payload["lanes"][0]["delta_raw_minus_wiki"] == 50.0
    md = write_compare_markdown(payload, tmp_path / "compare.md")
    assert "Wiki vs raw" in md.read_text(encoding="utf-8")
