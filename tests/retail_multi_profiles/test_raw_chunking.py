"""Tests for raw corpus chunking."""

from __future__ import annotations

from pathlib import Path

from tests.retail_multi_profiles.lib.raw_chunking import chunk_text_windows, chunks_for_source_file
from tests.retail_multi_profiles.lib.raw_corpus import RawSourceFile, iter_raw_source_files


def test_empty_glob_yields_no_files(tmp_path: Path) -> None:
    """P1 red: no matches → empty list."""
    files = iter_raw_source_files(tmp_path, "missing/**/*.md")
    assert files == []


def test_chunk_windows_stable() -> None:
    """Overlapping windows produce multiple chunks."""
    text = "a" * 2500
    parts = chunk_text_windows(text, max_chars=2000, overlap_chars=200)
    assert len(parts) >= 2
    assert parts[0] == "a" * 2000


def test_fixture_file_chunks(tmp_path: Path) -> None:
    """Fixture md produces stable chunk ids."""
    fixture = (
        Path(__file__).parent / "fixtures" / "raw_chunks" / "sample_ge.md"
    )
    src = RawSourceFile(
        source_relpath="raw/sources/sample_ge.md",
        absolute_path=fixture,
        model_id="ge_GNE27JYMFS",
        content_sha256="abc",
        size_bytes=fixture.stat().st_size,
        mtime_ns=fixture.stat().st_mtime_ns,
    )
    chunks = chunks_for_source_file(src)
    assert len(chunks) >= 1
    assert chunks[0].chunk_id
    assert "door alarm" in chunks[0].text.lower()
