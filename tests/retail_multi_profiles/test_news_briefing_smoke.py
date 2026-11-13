"""Contract for the five-question news briefing smoke."""

from __future__ import annotations

import copy
from pathlib import Path

import pytest

from tests.retail_multi_profiles.lib.lanes import load_lanes
from tests.retail_multi_profiles.lib.load_cos_insight_suite import load_cos_insight_suite
from tests.retail_multi_profiles.lib.news_briefing import (
    assert_smoke_result_row,
    validate_news_briefing_suite,
)
from tests.retail_multi_profiles.lib.raw_corpus import iter_raw_source_files

REPO = Path(__file__).resolve().parents[2]
SUITE = REPO / "tests" / "retail_multi_profiles" / "data" / "retail-news-briefing-n5.json"
NEWS_FILES = (
    "raw/sources/fridge-news_md/GE_GNE27JYMFS_news.md",
    "raw/sources/fridge-news_md/KitchenAid_KRFF507HPS_news.md",
    "raw/sources/fridge-news_md/Samsung_RF28K9070SG_news.md",
)


def test_news_fixture_has_five_questions_and_hit_prefixes() -> None:
    """The smoke fixture is five news questions, not the twenty-question W20 suite."""
    data = load_cos_insight_suite(SUITE)
    ids = [str(row["id"]) for row in data["questions"]]
    assert ids == ["N01", "N02", "N03", "N04", "N05"]
    assert data["expected_hits"]["wiki_prefix"] == "wiki/sources/13-fridge-newsmd--"
    assert data["expected_hits"]["bundled_prefix"] == "raw/sources/fridge-news_md/"
    assert data["status"] == "smoke"


def test_news_gold_must_keep_the_required_point() -> None:
    """A gold answer that drops the required point is not a valid smoke row."""
    data = load_cos_insight_suite(SUITE)
    broken = copy.deepcopy(data)
    broken["questions"][2]["answer"] = "Yes. The new GE Profile features can be added to this model."
    with pytest.raises(ValueError, match="N03"):
        validate_news_briefing_suite(broken)


def test_lane_b_includes_news_markdown_and_existing_manuals() -> None:
    """Lane B must see the news files and the manuals through one glob."""
    lane = load_lanes(REPO)["B"]
    rels = {
        item.source_relpath
        for item in iter_raw_source_files(lane.project_path, lane.raw_glob)
    }
    assert lane.raw_glob == "raw/sources/**/*.md"
    for news in NEWS_FILES:
        assert news in rels
    assert any(path.startswith("raw/sources/fridge-docs_md/") for path in rels)


def test_smoke_result_row_requires_confidence_hits_and_latency() -> None:
    """A smoke result is incomplete without confidence, paths, and retrieval time."""
    ok = {
        "correctness_confidence": 0.8,
        "top_hit_paths": ["wiki/sources/13-fridge-newsmd--16-gegne27jymfsnews--1j33fyx.md"],
        "retrieval_ms": 120,
        "context_chars": 400,
        "elapsed_ms": 900,
    }
    assert_smoke_result_row(ok)
    missing = dict(ok)
    del missing["correctness_confidence"]
    with pytest.raises(ValueError, match="correctness_confidence"):
        assert_smoke_result_row(missing)
