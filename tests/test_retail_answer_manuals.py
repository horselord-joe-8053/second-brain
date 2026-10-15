"""Manual leg of the retail answer bundle (brain-profiles P6): wiki → raw PDF page, raw fallback."""

from __future__ import annotations

from typing import Any, Dict, List

from retail_brain.answer_manuals import (
    WikiUnavailable,
    manual_leg,
    parse_frontmatter_sources,
)
from retail_brain.pdf_pages import PageRow, PdfPageIndex

SAM = "samsung_RF28K9070SG"
GE = "ge_GNE27JYMFS"
SAM_PDF = f"raw/sources/fridge-docs/{SAM}/user-guide.pdf"
GE_PDF = f"raw/sources/fridge-docs/{GE}/user-guide.pdf"


def _index() -> PdfPageIndex:
    """Pages: Samsung p2 = ice maker water supply, p3 = door alarm; GE p1 = ice maker arm."""
    return PdfPageIndex(
        [
            PageRow(SAM_PDF, SAM, "user", 1, "Safety instructions read all before use"),
            PageRow(SAM_PDF, SAM, "user", 2, "Ice maker not making ice check water supply line and shutoff valve"),
            PageRow(SAM_PDF, SAM, "user", 3, "Door alarm beeping close the door firmly"),
            PageRow(GE_PDF, GE, "user", 1, "Ice maker not making ice lower the feeler arm to on position"),
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
    assert parse_frontmatter_sources(_page(["fridge-docs/a/user-guide.pdf"], "x")) == ["fridge-docs/a/user-guide.pdf"]
    assert parse_frontmatter_sources("# no frontmatter") == []


def test_wiki_hit_cites_pdf_path_and_page() -> None:
    """Wiki excerpt → raw PDF from frontmatter → page from the page index."""
    wiki = FakeWiki(
        [{"path": "wiki/sources/sam-user.md", "snippet": "", "score": 0.9}],
        {"wiki/sources/sam-user.md": _page(
            [f"fridge-docs/{SAM}/user-guide.pdf"],
            "## Ice maker\nIf the ice maker is not making ice, check the water supply line and shutoff valve.\n\n"
            "## Door\nClose the door firmly to stop the alarm.",
        )},
    )
    leg = manual_leg("ice maker not making ice", sku=SAM, wiki=wiki, page_index=_index())
    assert leg["diagnostics"]["wiki_available"] is True
    top = leg["hits"][0]
    assert top["source"] == "wiki"
    assert top["wiki_path"] == "wiki/sources/sam-user.md"
    assert "water supply" in top["excerpt"]
    assert top["raw_origin"]["pdf_path"] == SAM_PDF
    assert top["raw_origin"]["pages"][0] == 2


def test_wrong_sku_wiki_pages_are_filtered_then_raw_fallback() -> None:
    """A GE wiki page never answers a Samsung ticket; raw page search fills in."""
    wiki = FakeWiki(
        [{"path": "wiki/sources/ge.md", "snippet": "", "score": 0.9}],
        {"wiki/sources/ge.md": _page([f"fridge-docs/{GE}/user-guide.pdf"], "Ice maker: lower the feeler arm.")},
    )
    leg = manual_leg("ice maker not making ice", sku=SAM, wiki=wiki, page_index=_index())
    assert leg["hits"], leg
    assert all(h["raw_origin"]["pdf_path"].startswith(f"raw/sources/fridge-docs/{SAM}/") for h in leg["hits"])
    assert leg["hits"][0]["source"] == "raw_pdf"
    assert leg["hits"][0]["wiki_path"] is None
    assert leg["hits"][0]["raw_origin"]["pages"] == [2]


def test_wiki_down_uses_raw_pdf_and_notes_it() -> None:
    """App not running → raw-PDF hits + diagnostics note; never raises."""
    leg = manual_leg("door alarm beeping", sku=SAM, wiki=DownWiki(), page_index=_index())
    assert leg["diagnostics"]["wiki_available"] is False
    assert any("wiki unavailable" in n for n in leg["diagnostics"]["notes"])
    assert leg["hits"][0]["source"] == "raw_pdf"
    assert leg["hits"][0]["raw_origin"]["pages"] == [3]
    assert "door" in leg["hits"][0]["excerpt"].lower()


def test_no_wiki_client_and_no_match_gives_empty_hits() -> None:
    """Unrelated query + no wiki → empty hits, still a well-formed leg."""
    leg = manual_leg("bluetooth pairing", sku=SAM, wiki=None, page_index=_index())
    assert leg["hits"] == []
    assert leg["diagnostics"]["manual_leg_ok"] is True


def test_manual_leg_is_deterministic() -> None:
    """Same inputs → identical leg dict."""
    a = manual_leg("ice maker not making ice", sku=SAM, wiki=None, page_index=_index())
    b = manual_leg("ice maker not making ice", sku=SAM, wiki=None, page_index=_index())
    assert a == b
