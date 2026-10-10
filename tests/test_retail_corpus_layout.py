"""Layout contract for brain/retail Nashsu project root."""

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RETAIL = REPO / "brain" / "retail"


def test_retail_brain_layout() -> None:
    assert (RETAIL / "purpose.md").is_file()
    assert (RETAIL / "wiki" / "index.md").is_file()
    for model in ("a15", "a16", "a25"):
        assert (RETAIL / "raw" / "sources" / "samsung-docs" / model).is_dir()


def test_legacy_personal_brain_unchanged() -> None:
    assert (REPO / "brain" / "purpose.md").is_file()
    assert (REPO / "brain" / "wiki").is_dir()
