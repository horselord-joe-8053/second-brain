"""Character-window and page-heading chunking for raw manual files (markdown or text)."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass

from .raw_corpus import RawSourceFile, stable_chunk_id
from .raw_policy import chunk_policy_version_for_meta, manual_d2_chunk_policy

_HEADING_RE = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)


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


def chunk_text_page_heading(
    text: str,
    *,
    max_chars: int = 2000,
    overlap_chars: int = 100,
) -> list[str]:
    """Split on Markdown headings (h1–h3), then window oversized sections."""
    if not text.strip():
        return []
    sections: list[tuple[str, str]] = []
    current_heading = ""
    buf: list[str] = []
    for line in text.splitlines():
        m = re.match(r"^#{1,3}\s+", line)
        if m:
            if buf:
                sections.append((current_heading, "\n".join(buf)))
            current_heading = line.strip()
            buf = [line]
        else:
            buf.append(line)
    if buf:
        sections.append((current_heading, "\n".join(buf)))

    if not sections:
        return chunk_text_windows(text, max_chars=max_chars, overlap_chars=overlap_chars)

    out: list[str] = []
    for heading, body in sections:
        prefix = f"{heading}\n" if heading else ""
        piece = (prefix + body).strip()
        if len(piece) <= max_chars:
            if piece:
                out.append(piece)
        else:
            out.extend(
                chunk_text_windows(piece, max_chars=max_chars, overlap_chars=overlap_chars)
            )
    return out


def chunks_for_source_file(
    src: RawSourceFile,
    *,
    max_chars: int = 2000,
    overlap_chars: int = 200,
    policy: str | None = None,
) -> list[RawChunk]:
    """Read file and emit RawChunk rows with stable ids for the active D2 policy."""
    text = src.absolute_path.read_text(encoding="utf-8", errors="replace")
    pol = (policy or manual_d2_chunk_policy()).strip().lower()
    if pol == "page_heading":
        windows = chunk_text_page_heading(
            text, max_chars=max_chars, overlap_chars=min(overlap_chars, 100)
        )
    else:
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
    """Version tag stored in PG / Lance index metadata (D2 policy)."""
    return chunk_policy_version_for_meta()
