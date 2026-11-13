"""Brain-profiles layout contract: brain/ holds only personal/, retail/, and shared files."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BRAINS = REPO / "brain"

# Lane roots from config/retail-ingest-lanes.yaml (besides legacy ``retail`` wiki profile).
PROFILES = ("personal", "retail", "retail-md", "retail-txt", "retail-md-learned")
SHARED_FILES = (".gitignore", "README.md")
# Hidden runtime dirs other tools may drop at the root; never tracked.
IGNORED_ROOT_ENTRIES = (".DS_Store",)


def test_brain_has_only_profiles_and_shared() -> None:
    """No profile content (wiki/, raw/, purpose.md, …) remains directly under brain/."""
    entries = {p.name for p in BRAINS.iterdir()} - set(IGNORED_ROOT_ENTRIES)
    assert entries == set(PROFILES) | set(SHARED_FILES), sorted(entries)


def test_each_profile_is_a_nashsu_root() -> None:
    """Legacy full wiki profiles carry the minimum LLM Wiki project shape."""
    for name in ("personal", "retail"):
        root = BRAINS / name
        assert (root / "purpose.md").is_file(), name
        assert (root / "schema.md").is_file(), name
        assert (root / "wiki" / "index.md").is_file(), name
        assert (root / "raw" / "sources").is_dir(), name
        assert (root / "manifests").is_dir(), name


def test_lane_ingest_profiles_have_purpose_and_raw() -> None:
    """A/B/C/D lane roots (``retail-ingest-lanes.yaml``) expose purpose + raw/sources."""
    for name in ("retail-md", "retail-txt", "retail-md-learned"):
        root = BRAINS / name
        assert (root / "purpose.md").is_file(), name
        assert (root / "raw" / "sources").is_dir(), name


def test_retail_profile_complete() -> None:
    """Retail profile names the answer bundle and FRU corpus in its purpose."""
    purpose = (BRAINS / "retail" / "purpose.md").read_text(encoding="utf-8")
    assert "retail_answer.v1" in purpose
    assert "fru_us_1k" in purpose


def test_shared_gitignore_is_profile_relative() -> None:
    """Personal binaries stay ignored; retail fridge PDFs stay committable."""
    text = (BRAINS / ".gitignore").read_text(encoding="utf-8")
    assert "personal/raw/sources/**/*.pdf" in text
    assert "\nraw/sources/**/*.pdf" not in text
    assert ".llm-wiki/" in text


def test_readme_documents_brain_profile_switch() -> None:
    """Shared README explains BRAIN_PROFILE and the default."""
    text = (BRAINS / "README.md").read_text(encoding="utf-8")
    assert "BRAIN_PROFILE" in text
    assert "retail" in text and "personal" in text
