"""Manual leg of the retail answer bundle (P13): wiki → ``.txt`` doc, ``raw_txt`` fallback."""

from __future__ import annotations

from typing import Any, Dict, List

import pytest

pytestmark = pytest.mark.retail_manual_leg

from retail_brain.answer_manuals import WikiUnavailable, manual_leg, parse_frontmatter_sources
from retail_brain.txt_docs import TxtDocRow, TxtDocIndex

SAM = "samsung_RF28K9070SG"
GE = "ge_GNE27JYMFS"
SAM_TXT = f"raw/sources/fridge-docs/{SAM}/user-guide.txt"
GE_TXT = f"raw/sources/fridge-docs/{GE}/user-guide.txt"


def _index() -> TxtDocIndex:
    """Samsung + GE user guides with ice maker / door content (one row per file)."""
    return TxtDocIndex(
        [
            TxtDocRow(
                SAM_TXT,
                SAM,
                "user",
                "Safety instructions read all before use. "
                "Ice maker not making ice check water supply line and shutoff valve. "
                "Door alarm beeping close the door firmly.",
            ),
            TxtDocRow(GE_TXT, GE, "user", "Ice maker not making ice lower the feeler arm to on position"),
        ]
    )


def _page(sources: List[str], body: str) -> str:
    """Compiled wiki page text with Nashsu-style frontmatter."""
    src = ", ".join(f'"{s}"' for s in sources)
    return f"---\ntype: source\ntitle: T\nsources: [{src}]\n---\n# T\n\n{body}\n"


class FakeWiki:
    """In-memory WikiSearchClient: fixed search results + page bodies."""

    def __init__(self, results: List[Dict[str, Any]], pages: Dict[str, str]) -> None:
        """Store canned search results and page contents."""
        self.results = results
        self.pages = pages

    def search(self, query: str, *, limit: int) -> List[Dict[str, Any]]:
        """Return canned results (already ranked)."""
        return self.results[:limit]

    def read(self, path: str) -> str:
        """Return page content by wiki path."""
        return self.pages[path]


class DownWiki:
    """Client whose app is not running."""

    def search(self, query: str, *, limit: int) -> List[Dict[str, Any]]:
        """Simulate the LLM Wiki API being unreachable."""
        raise WikiUnavailable("connection refused")

    def read(self, path: str) -> str:
        """Never reached."""
        raise WikiUnavailable("connection refused")


def test_parse_frontmatter_sources() -> None:
    """Frontmatter ``sources:`` list is parsed; missing frontmatter → empty."""
    assert parse_frontmatter_sources(_page(["fridge-docs/a/user-guide.txt"], "x")) == ["fridge-docs/a/user-guide.txt"]
    assert parse_frontmatter_sources("# no frontmatter") == []


def test_wiki_hit_cites_doc_path() -> None:
    """Wiki excerpt → ``doc_path`` in raw_origin; ``pages`` empty."""
    wiki = FakeWiki(
        [{"path": "wiki/sources/sam-user.md", "snippet": "", "score": 0.9}],
        {
            "wiki/sources/sam-user.md": _page(
                [f"fridge-docs/{SAM}/user-guide.txt"],
                "## Ice maker\nIf the ice maker is not making ice, check the water supply line and shutoff valve.\n\n"
                "## Door\nClose the door firmly to stop the alarm.",
            ),
        },
    )
    leg = manual_leg("ice maker not making ice", sku=SAM, wiki=wiki, txt_index=_index())
    assert leg["diagnostics"]["wiki_available"] is True
    top = leg["hits"][0]
    assert top["source"] == "wiki"
    assert top["wiki_path"] == "wiki/sources/sam-user.md"
    assert "water supply" in top["excerpt"]
    assert top["raw_origin"]["doc_path"] == SAM_TXT
    assert top["raw_origin"]["pages"] == []


def test_wrong_sku_wiki_pages_are_filtered_then_raw_fallback() -> None:
    """A GE wiki page never answers a Samsung ticket; raw ``.txt`` search fills in."""
    wiki = FakeWiki(
        [{"path": "wiki/sources/ge.md", "snippet": "", "score": 0.9}],
        {"wiki/sources/ge.md": _page([f"fridge-docs/{GE}/user-guide.txt"], "Ice maker: lower the feeler arm.")},
    )
    leg = manual_leg("ice maker not making ice", sku=SAM, wiki=wiki, txt_index=_index())
    assert leg["hits"], leg
    assert all(h["raw_origin"]["doc_path"].startswith(f"raw/sources/fridge-docs/{SAM}/") for h in leg["hits"])
    assert leg["hits"][0]["source"] == "raw_txt"


def test_wiki_down_uses_raw_txt_and_notes_it() -> None:
    """Wiki down → ``raw_txt`` hit and a diagnostic note."""
    leg = manual_leg("door alarm beeping", sku=SAM, wiki=DownWiki(), txt_index=_index())
    assert any("wiki unavailable" in n for n in leg["diagnostics"]["notes"])
    assert leg["hits"][0]["source"] == "raw_txt"


def test_no_wiki_client_still_searches_txt() -> None:
    """``wiki=None`` → raw ``.txt`` search only."""
    leg = manual_leg("bluetooth pairing", sku=SAM, wiki=None, txt_index=_index())
    assert leg["diagnostics"]["wiki_available"] is False


def test_manual_leg_is_deterministic() -> None:
    """Same inputs → identical hit ordering and excerpts."""
    a = manual_leg("ice maker not making ice", sku=SAM, wiki=None, txt_index=_index())
    b = manual_leg("ice maker not making ice", sku=SAM, wiki=None, txt_index=_index())
    assert a == b
