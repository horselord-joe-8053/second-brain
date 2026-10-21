"""Enumerate raw/source files per lane glob and derive stable chunk ids."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

_MODEL_RE = re.compile(
    r"(ge_GNE27JYMFS|kitchenaid_KRFF507HPS|samsung_RF28K9070SG)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class RawSourceFile:
    """One file under a lane project matching raw_glob."""

    source_relpath: str
    absolute_path: Path
    model_id: str
    content_sha256: str
    size_bytes: int
    mtime_ns: int


def infer_model_id_from_path(path: Path) -> str:
    """Best-effort SKU folder token from raw path segments."""
    m = _MODEL_RE.search(str(path))
    return m.group(1) if m else ""


def sha256_file(path: Path) -> str:
    """Content hash for index manifest drift detection."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def iter_raw_source_files(project_path: Path, raw_glob: str) -> list[RawSourceFile]:
    """Walk project_path with glob relative to project root; sorted for stability."""
    if not raw_glob.strip():
        return []
    root = project_path.resolve()
    matches = sorted(root.glob(raw_glob))
    out: list[RawSourceFile] = []
    for abs_path in matches:
        if not abs_path.is_file():
            continue
        rel = abs_path.relative_to(root).as_posix()
        st = abs_path.stat()
        out.append(
            RawSourceFile(
                source_relpath=rel,
                absolute_path=abs_path,
                model_id=infer_model_id_from_path(abs_path),
                content_sha256=sha256_file(abs_path),
                size_bytes=st.st_size,
                mtime_ns=st.st_mtime_ns,
            )
        )
    return out


def stable_chunk_id(source_relpath: str, chunk_index: int) -> str:
    """Deterministic id for one text chunk within a source file."""
    raw = f"{source_relpath}#{chunk_index}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]
