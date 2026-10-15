"""Layout contract for brain/retail Nashsu project root."""

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RETAIL = REPO / "brain" / "retail"

FRIDGE_SKUS = (
    "samsung_RF28K9070SG",
    "ge_GNE27JYMFS",
    "kitchenaid_KRFF507HPS",
)


def test_retail_brain_layout() -> None:
    """FRU corpus expects purpose, wiki stub, and three fridge PDF folders."""
    assert (RETAIL / "purpose.md").is_file()
    assert (RETAIL / "wiki" / "index.md").is_file()
    for folder in FRIDGE_SKUS:
        base = RETAIL / "raw" / "sources" / "fridge-docs" / folder
        assert base.is_dir()
        assert (base / "user-guide.pdf").is_file()
        assert (base / "repair-guide.pdf").is_file()


def test_personal_profile_sibling_present() -> None:
    """Personal corpus lives beside retail under brain/personal/."""
    assert (REPO / "brain" / "personal" / "purpose.md").is_file()
    assert (REPO / "brain" / "personal" / "wiki").is_dir()
