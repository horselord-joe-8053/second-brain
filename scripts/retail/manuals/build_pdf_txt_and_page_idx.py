#!/usr/bin/env python3.12
"""Build full-manual ``.txt`` under ``raw/sources/fridge-docs/`` from PDFs in ``archive/fridge-docs/``.

Operator/CLI (needs ``pypdf``). Optionally writes page-level JSONL to ``archive/pdf_page_index.jsonl``
when ``WRITE_PAGE_INDEX=1`` (default **off**, decision E15).

Usage:
  python3.12 scripts/retail/manuals/build_pdf_txt_and_page_idx.py [--brain-root brain/retail]
  WRITE_PAGE_INDEX=1 python3.12 scripts/retail/manuals/build_pdf_txt_and_page_idx.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Dict, List

_MANUALS_DIR = Path(__file__).resolve().parent
if str(_MANUALS_DIR) not in sys.path:
    sys.path.insert(0, str(_MANUALS_DIR))

from multilingual_trim import apply_multilingual_trim  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_BRAIN = ROOT / "brain" / "retail"
ARCHIVE_SUBDIR = Path("archive") / "fridge-docs"
TXT_SUBDIR = Path("raw") / "sources" / "fridge-docs"
DEFAULT_JSONL = Path("archive") / "pdf_page_index.jsonl"


def _sha256(path: Path) -> str:
    """Hex sha256 of a file (streamed)."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _clean(text: str) -> str:
    """Collapse whitespace so page text is one stable line."""
    return " ".join((text or "").split())


_SHIFT = 29
_SHIFTED_RUN = re.compile(r"[\x03-\x08\x0b\x0c\x0e-\x1f\x21-\x5d]+")
_WORDLIKE = re.compile(r"[(\"']?[A-Za-z][a-z]+[.,:;!?)\"']*")


def _core(word: str) -> str:
    """Lowercase letters only (vocabulary lookup key)."""
    return re.sub(r"[^a-z]", "", word.lower())


def manual_vocab(pages: List[str]) -> frozenset[str]:
    """Lowercase words (≥3 letters) seen in normal, unshifted manual text."""
    return frozenset(w for text in pages for w in re.findall(r"[a-z]{3,}", text))


def repair_shifted_glyphs(text: str, vocab: frozenset[str]) -> str:
    """Decode shifted-glyph runs; keep real all-caps words, codes, and part numbers untouched."""

    def fix(m: re.Match[str]) -> str:
        run = m.group(0)
        decoded = "".join(chr(ord(c) + _SHIFT) for c in run)
        if any(ord(c) < 0x20 for c in run):
            return decoded
        if len(run) >= 3 and _WORDLIKE.fullmatch(decoded) and _core(decoded) in vocab and _core(run) not in vocab:
            return decoded
        return run

    return _SHIFTED_RUN.sub(fix, text or "")


def extract_pages(pdf: Path) -> List[str]:
    """Return raw text per page (1 entry per page, possibly empty)."""
    from pypdf import PdfReader  # operator-only dependency

    reader = PdfReader(str(pdf))
    return [page.extract_text() or "" for page in reader.pages]


def _canonical_order(pdf: Path) -> tuple[str, bool, str]:
    """Per SKU, ``user-guide.pdf`` first so byte-identical copies cite the user guide as canonical."""
    return (pdf.parent.name, pdf.stem != "user-guide", pdf.name)


def _extract_timed(pdf: Path) -> List[str]:
    """``extract_pages`` with a progress line (runs in a worker process)."""
    t0 = time.monotonic()
    pages = extract_pages(pdf)
    print(
        f"build_pdf_txt_and_page_idx: {pdf.parent.name}/{pdf.name} {len(pages)} pages "
        f"({time.monotonic() - t0:.1f}s)",
        file=sys.stderr,
        flush=True,
    )
    return pages


def _archive_pdf_paths(brain_root: Path) -> List[Path]:
    """Every ``archive/fridge-docs/<sku>/*.pdf``."""
    pdfs = sorted((brain_root / ARCHIVE_SUBDIR).glob("*/*.pdf"), key=_canonical_order)
    if not pdfs:
        raise FileNotFoundError(f"no PDFs under {brain_root / ARCHIVE_SUBDIR}")
    return pdfs


def _cleaned_pages(raw_pages: List[str], vocab: frozenset[str]) -> List[str]:
    """Per-page cleaned text after glyph repair."""
    return [_clean(repair_shifted_glyphs(t, vocab)) for t in raw_pages]


def _maybe_archive_multilingual(
    brain_root: Path, pdf: Path, stem: str, full_body: str, cut_at: int
) -> None:
    """Write ``archive/fridge-docs/<sku>/<stem>.mul.txt`` before trimming ``raw`` English."""
    mul = brain_root / ARCHIVE_SUBDIR / pdf.parent.name / f"{stem}.mul.txt"
    mul.parent.mkdir(parents=True, exist_ok=True)
    mul.write_text(full_body + ("\n" if not full_body.endswith("\n") else ""), encoding="utf-8")
    print(
        f"build_pdf_txt_and_page_idx: archived multilingual → {mul.relative_to(brain_root).as_posix()} "
        f"(trimmed {len(full_body) - cut_at} chars from raw .txt)",
        file=sys.stderr,
    )


def write_txt_files(brain_root: Path, *, workers: int = 4) -> int:
    """Extract each archive PDF to ``raw/sources/fridge-docs/<sku>/<guide>.txt``; return file count."""
    pdfs = _archive_pdf_paths(brain_root)
    digests = {pdf: _sha256(pdf) for pdf in pdfs}
    unique: Dict[str, Path] = {}
    for pdf in pdfs:
        if digests[pdf] not in unique:
            unique[digests[pdf]] = pdf
    with ProcessPoolExecutor(max_workers=max(1, min(workers, len(unique)))) as pool:
        raw = dict(zip(unique, pool.map(_extract_timed, unique.values())))
    vocab = manual_vocab([t for pages in raw.values() for t in pages])
    cache = {d: _cleaned_pages(pages, vocab) for d, pages in raw.items()}
    written = 0
    for pdf in pdfs:
        rel_txt = (TXT_SUBDIR / pdf.parent.name / f"{pdf.stem}.txt").as_posix()
        out = brain_root / rel_txt
        out.parent.mkdir(parents=True, exist_ok=True)
        body = "\n\n".join(t for t in cache[digests[pdf]] if t)
        sku_folder = pdf.parent.name
        english, cut = apply_multilingual_trim(body, sku_folder, pdf.stem)
        if cut is not None:
            _maybe_archive_multilingual(brain_root, pdf, pdf.stem, body, cut)
            body = english
        out.write_text(body + ("\n" if not body.endswith("\n") else ""), encoding="utf-8")
        written += 1
        print(f"build_pdf_txt_and_page_idx: wrote {rel_txt} ({len(body)} chars)", file=sys.stderr)
    return written


def build_jsonl_rows(brain_root: Path, *, workers: int = 4) -> List[Dict[str, object]]:
    """Page index rows with ``pdf_path`` under ``archive/fridge-docs/``."""
    pdfs = _archive_pdf_paths(brain_root)
    digests = {pdf: _sha256(pdf) for pdf in pdfs}
    first_path: Dict[str, str] = {}
    unique: Dict[str, Path] = {}
    for pdf in pdfs:
        if digests[pdf] not in unique:
            unique[digests[pdf]] = pdf
            first_path[digests[pdf]] = pdf.relative_to(brain_root).as_posix()
    with ProcessPoolExecutor(max_workers=max(1, min(workers, len(unique)))) as pool:
        raw = dict(zip(unique, pool.map(_extract_timed, unique.values())))
    vocab = manual_vocab([t for pages in raw.values() for t in pages])
    cache = {d: _cleaned_pages(pages, vocab) for d, pages in raw.items()}
    rows: List[Dict[str, object]] = []
    for pdf in pdfs:
        rel = pdf.relative_to(brain_root).as_posix()
        digest = digests[pdf]
        duplicate_of = first_path[digest] if first_path[digest] != rel else None
        if duplicate_of:
            print(f"build_pdf_txt_and_page_idx: {rel} duplicate of {duplicate_of}", file=sys.stderr)
        for i, text in enumerate(cache[digest], start=1):
            rows.append(
                {
                    "pdf_path": rel,
                    "sku": pdf.parent.name,
                    "guide": pdf.stem.removesuffix("-guide"),
                    "page": i,
                    "sha256": digest,
                    "duplicate_of": duplicate_of,
                    "text": text,
                }
            )
    rows.sort(key=lambda r: (str(r["pdf_path"]), int(r["page"])))
    return rows


def write_jsonl(rows: List[Dict[str, object]], out: Path) -> None:
    """Write rows as sorted-key JSON lines (UTF-8, trailing newline)."""
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_page_index_enabled(argv_flag: bool | None) -> bool:
    """True when CLI ``--write-page-index`` or env ``WRITE_PAGE_INDEX`` is truthy."""
    if argv_flag is not None:
        return argv_flag
    return os.environ.get("WRITE_PAGE_INDEX", "0").strip().lower() in ("1", "true", "yes", "on")


def main(argv: List[str] | None = None) -> int:
    """CLI: always refresh ``.txt``; JSONL only when enabled."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--brain-root", type=Path, default=DEFAULT_BRAIN)
    ap.add_argument("--jsonl-out", type=Path, default=None)
    ap.add_argument("--write-page-index", action="store_true", default=None)
    ap.add_argument("--no-write-page-index", action="store_true", default=False)
    args = ap.parse_args(argv)
    flag = None if not args.write_page_index and not args.no_write_page_index else args.write_page_index
    if args.no_write_page_index:
        flag = False
    n_txt = write_txt_files(args.brain_root)
    if write_page_index_enabled(flag):
        out = args.jsonl_out or (args.brain_root / DEFAULT_JSONL)
        rows = build_jsonl_rows(args.brain_root)
        write_jsonl(rows, out)
        print(f"build_pdf_txt_and_page_idx: wrote {len(rows)} index rows → {out}", file=sys.stderr)
    else:
        print("build_pdf_txt_and_page_idx: WRITE_PAGE_INDEX off — skipped JSONL", file=sys.stderr)
    print(f"build_pdf_txt_and_page_idx: wrote {n_txt} .txt file(s)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
