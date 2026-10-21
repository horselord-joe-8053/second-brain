"""PDF page index contract (brain-profiles P4): committed JSONL + SKU-scoped page search."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from retail_brain.pdf_pages import PageRow, PdfPageIndex, load_page_index

REPO = Path(__file__).resolve().parents[2]
_MANUALS = REPO / "scripts" / "retail" / "manuals"
INDEX = REPO / "brain" / "retail" / "archive" / "pdf_page_index.jsonl"
SKUS = ("samsung_RF28K9070SG", "ge_GNE27JYMFS", "kitchenaid_KRFF507HPS")


def _rows() -> list[PageRow]:
    """Tiny synthetic index: two SKUs, ice maker content on known pages."""
    a = "raw/sources/fridge-docs/samsung_RF28K9070SG/user-guide.pdf"
    b = "raw/sources/fridge-docs/ge_GNE27JYMFS/user-guide.pdf"
    return [
        PageRow(a, "samsung_RF28K9070SG", "user", 1, "Safety instructions read before use"),
        PageRow(a, "samsung_RF28K9070SG", "user", 2, "Ice maker not making ice check water supply line valve"),
        PageRow(a, "samsung_RF28K9070SG", "user", 3, "Door alarm beeping close the door firmly"),
        PageRow(b, "ge_GNE27JYMFS", "user", 1, "Ice maker not making ice reset arm switch"),
    ]


def test_search_pages_is_sku_scoped_and_ranked() -> None:
    """Only the requested SKU's pages return; best match first; score in (0, 1]."""
    idx = PdfPageIndex(_rows())
    hits = idx.search_pages("ice maker stopped making ice", sku="samsung_RF28K9070SG", k=2)
    assert [h.page for h, _ in hits][0] == 2
    assert all(h.sku == "samsung_RF28K9070SG" for h, _ in hits)
    assert 0.0 < hits[0][1] <= 1.0


def test_search_pages_deterministic_and_empty_on_no_overlap() -> None:
    """Same input → same output; unrelated query → no hits."""
    idx = PdfPageIndex(_rows())
    q = "door alarm beeping"
    assert idx.search_pages(q, sku="samsung_RF28K9070SG") == idx.search_pages(q, sku="samsung_RF28K9070SG")
    assert idx.search_pages("bluetooth pairing", sku="samsung_RF28K9070SG") == []


def test_best_pages_maps_excerpt_to_page_of_given_pdf() -> None:
    """A wiki excerpt maps to the page of the cited PDF that contains its words."""
    idx = PdfPageIndex(_rows())
    pdf = "raw/sources/fridge-docs/samsung_RF28K9070SG/user-guide.pdf"
    pages = idx.best_pages("Check the water supply line and valve if the ice maker is not making ice", pdf)
    assert pages[0][0] == 2


def test_load_page_index_reads_jsonl(tmp_path: Path) -> None:
    """Loader accepts the builder's JSONL shape (extra keys ignored)."""
    p = tmp_path / "idx.jsonl"
    row = {"pdf_path": "raw/x.pdf", "sku": "s", "guide": "user", "page": 1, "text": "hello", "sha256": "x"}
    p.write_text(json.dumps(row) + "\n", encoding="utf-8")
    idx = load_page_index(p)
    assert idx.rows[0].pdf_path == "raw/x.pdf"


def _shift(s: str) -> str:
    """Encode text the way the GE manual's broken font does (every code point −29; space → \\x03)."""
    return "".join(chr(ord(c) - 29) for c in s)


def test_multilingual_trim_samsung_user_guide_marker() -> None:
    """Samsung rule: trim at ``Español <page>`` after enough English prefix."""
    import sys

    if str(_MANUALS) not in sys.path:
        sys.path.insert(0, str(_MANUALS))
    from multilingual_trim import apply_multilingual_trim

    body = "English section " * 3000 + "\nEspañol 12 Contenido traducido " + "x" * 500
    eng, cut = apply_multilingual_trim(body, "samsung_RF28K9070SG", "user-guide")
    assert cut is not None
    assert "Español" not in eng
    assert "English section" in eng


def test_multilingual_trim_ge_user_guide_marker() -> None:
    """GE rule: trim before French ``CONSIGNES DE SÉCURITÉ`` TOC block."""
    import sys

    if str(_MANUALS) not in sys.path:
        sys.path.insert(0, str(_MANUALS))
    from multilingual_trim import apply_multilingual_trim

    prefix = "OWNER'S MANUAL ice maker troubleshooting " * 4000
    body = prefix + "\nCONSIGNES DE SÉCURITÉ ...... 3 CONSIGNES D’UTILISATION"
    eng, cut = apply_multilingual_trim(body, "ge_GNE27JYMFS", "user-guide")
    assert cut is not None
    assert "CONSIGNES DE SÉCURITÉ" not in eng
    assert "ice maker" in eng


def test_multilingual_trim_skips_unregistered_manuals() -> None:
    """Repair guides and unknown SKUs pass through unchanged."""
    import sys

    if str(_MANUALS) not in sys.path:
        sys.path.insert(0, str(_MANUALS))
    from multilingual_trim import apply_multilingual_trim

    body = "Fast Track Troubleshooting ERROR 41 ice maker"
    same, cut = apply_multilingual_trim(body, "samsung_RF28K9070SG", "repair-guide")
    assert cut is None and same == body


def test_ge_committed_user_guide_has_no_spanish_precaucion_tail() -> None:
    """After rebuild, GE raw user guide must not contain Spanish safety section header."""
    ge = REPO / "brain" / "retail/raw/sources/fridge-docs/ge_GNE27JYMFS/user-guide.txt"
    if not ge.is_file():
        pytest.skip("run build_pdf_txt_and_page_idx to refresh corpus")
    text = ge.read_text(encoding="utf-8")
    assert "PRECAUCIÓN A fin de reducir el riesgo" not in text
    assert "CONSIGNES DE SÉCURITÉ" not in text


def test_builder_repairs_shifted_glyph_runs() -> None:
    """Shifted runs decode back to text; real all-caps words and part numbers stay as they are."""
    spec = importlib.util.spec_from_file_location(
        "bpi", REPO / "scripts/retail/manuals/build_pdf_txt_and_page_idx.py"
    )
    bpi = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bpi)
    vocab = frozenset({"icemaker", "interior", "light", "does", "not", "work", "troubleshooting", "using"})
    raw = f"TROUBLESHOOTING USING {_shift('Interior light does not work')} No power 49-1000472 {_shift('Icemaker')}"
    assert bpi.repair_shifted_glyphs(raw, vocab) == (
        "TROUBLESHOOTING USING Interior light does not work No power 49-1000472 Icemaker"
    )
    assert bpi.repair_shifted_glyphs("plain text stays", vocab) == "plain text stays"


@pytest.mark.skipif(not INDEX.is_file(), reason="page index not built yet")
def test_committed_index_has_no_shifted_glyph_runs() -> None:
    """Rebuilt index: GE troubleshooting rows are readable (no \\x03 'space' glyphs left)."""
    idx = load_page_index(INDEX)
    assert not any("\x03" in r.text for r in idx.rows)
    ge = [r for r in idx.rows if r.sku == "ge_GNE27JYMFS"]
    assert any("interior light does not work" in r.text.lower() for r in ge)


@pytest.mark.skipif(not INDEX.is_file(), reason="page index not built yet")
def test_committed_index_covers_archive_pdfs() -> None:
    """Real index: four canonical archive PDFs, contiguous 1-based pages."""
    idx = load_page_index(INDEX)
    by_pdf: dict[str, list[int]] = {}
    for r in idx.rows:
        by_pdf.setdefault(r.pdf_path, []).append(r.page)
        assert r.sku in SKUS
        assert r.pdf_path.startswith(f"archive/fridge-docs/{r.sku}/")
    assert len(by_pdf) == 4
    for pages in by_pdf.values():
        assert pages == list(range(1, len(pages) + 1))


@pytest.mark.skipif(not INDEX.is_file(), reason="page index not built yet")
def test_committed_index_finds_ice_maker_per_sku() -> None:
    """Every SKU's manuals mention the ice maker somewhere."""
    idx = load_page_index(INDEX)
    for sku in SKUS:
        assert idx.search_pages("ice maker", sku=sku, k=1), sku
