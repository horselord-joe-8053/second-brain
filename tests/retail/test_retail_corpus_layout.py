"""Layout contract for brain/retail Nashsu project root (txt-wiki track P11)."""

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RETAIL = REPO / "brain" / "retail"

FRIDGE_SKUS = (
    "samsung_RF28K9070SG",
    "ge_GNE27JYMFS",
    "kitchenaid_KRFF507HPS",
)


def test_retail_brain_layout() -> None:
    """Lane A (``brain/retail``): wiki stub, PDF archive under ``archive/pdf/``, raw manuals present."""
    assert (RETAIL / "purpose.md").is_file()
    assert (RETAIL / "wiki" / "index.md").is_file()
    for folder in FRIDGE_SKUS:
        raw = RETAIL / "raw" / "sources" / "fridge-docs" / folder
        arch = RETAIL / "archive" / "pdf" / "fridge-docs" / folder
        assert raw.is_dir()
        assert arch.is_dir()
        assert (arch / "user-guide.pdf").is_file()
        raw_txt = raw / "user-guide.txt"
        raw_pdf = raw / "user-guide.pdf"
        assert raw_txt.is_file() or raw_pdf.is_file(), folder
        if folder == "samsung_RF28K9070SG":
            assert (arch / "repair-guide.pdf").is_file()
            assert (raw / "repair-guide.txt").is_file() or (raw / "repair-guide.pdf").is_file()


def test_personal_profile_sibling_present() -> None:
    """Personal corpus lives beside retail under brain/personal/."""
    assert (REPO / "brain" / "personal" / "purpose.md").is_file()
    assert (REPO / "brain" / "personal" / "wiki").is_dir()
