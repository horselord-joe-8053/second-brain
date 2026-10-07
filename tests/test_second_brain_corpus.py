"""Acceptance tests for Second Brain Hermes v1 (in-repo corpus)."""

from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
BRAIN = REPO / "brain"

SOURCE_CHANNELS = (
    "personal",
    "uploads",
    "drive",
    "gmail",
    "github",
    "web",
    "chat",
)


def test_ac_sb1_brain_layout() -> None:
    assert (BRAIN / "purpose.md").is_file()
    assert (BRAIN / "schema.md").is_file()
    assert (BRAIN / "wiki").is_dir()
    assert (BRAIN / "manifests").is_dir()
    assert (BRAIN / "raw" / "assets").is_dir()
    for ch in SOURCE_CHANNELS:
        assert (BRAIN / "raw" / "sources" / ch).is_dir()
    assert (BRAIN / ".gitignore").is_file()


def test_ac_sb2_readme_links() -> None:
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    assert "docs_manual_gen/PLAN_SECOND_BRAIN_HERMES_V1" in readme
    assert "docs_manual_gen/second-brain-llm-wiki-architecture" in readme
    assert "fabrication/references/EXECUTE_GEN" in readme


def test_ac_sb6_ingest_harness() -> None:
    skill = REPO / "harness" / "second-brain" / "skills" / "ingest-to-brain" / "SKILL.md"
    manifest = REPO / "harness" / "second-brain" / "manifests" / "example-ingest.yaml"
    assert skill.is_file()
    assert manifest.is_file()


def test_ac_sb7_backup_script() -> None:
    backup = REPO / "scripts" / "brain" / "backup.sh"
    assert backup.is_file()
    assert (REPO / "scripts" / "brain" / "ingest.sh").is_file()
