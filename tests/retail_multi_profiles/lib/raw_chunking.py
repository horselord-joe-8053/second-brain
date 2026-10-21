"""Character-window chunking for raw manual files (markdown or text)."""

from __future__ import annotations

from dataclasses import dataclass

from .raw_corpus import RawSourceFile, stable_chunk_id
from .raw_policy import CHUNK_POLICY_VERSION


@dataclass(frozen=True)
class RawChunk:
    """One embeddable slice of a raw source file."""

    chunk_id: str
    source_relpath: str
    model_id: str
    chunk_index: int
    text: str
    content_hash: str


def chunk_text_windows(
    text: str,
    *,
    max_chars: int = 2000,
    overlap_chars: int = 200,
) -> list[str]:
    """Split text into overlapping character windows."""
    if not text:
        return []
    if max_chars <= 0:
        raise ValueError("max_chars must be positive")
    overlap = max(0, min(overlap_chars, max_chars - 1))
    step = max_chars - overlap
    chunks: list[str] = []
    start = 0
    while start < len(text):
        piece = text[start : start + max_chars]
        if piece.strip():
            chunks.append(piece)
        if start + max_chars >= len(text):
            break
        start += step
    return chunks


def chunks_for_source_file(
    src: RawSourceFile,
    *,
    max_chars: int = 2000,
    overlap_chars: int = 200,
) -> list[RawChunk]:
    """Read file and emit RawChunk rows with stable ids."""
    text = src.absolute_path.read_text(encoding="utf-8", errors="replace")
    windows = chunk_text_windows(text, max_chars=max_chars, overlap_chars=overlap_chars)
    out: list[RawChunk] = []
    for idx, window in enumerate(windows):
        out.append(
            RawChunk(
                chunk_id=stable_chunk_id(src.source_relpath, idx),
                source_relpath=src.source_relpath,
                model_id=src.model_id,
                chunk_index=idx,
                text=window,
                content_hash=src.content_sha256,
            )
        )
    return out


def chunk_policy_version() -> str:
    """Version tag stored in Lance index metadata."""
    return CHUNK_POLICY_VERSION
