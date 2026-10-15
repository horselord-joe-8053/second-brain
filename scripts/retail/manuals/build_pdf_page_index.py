#!/usr/bin/env python3.12
"""Build brain/retail/manifests/pdf_page_index.jsonl — one row per page of each fridge PDF.

Operator/CLI step (needs ``pypdf``); CI only reads the committed JSONL via ``retail_brain.pdf_pages``.
Rows: ``pdf_path`` (relative to the retail brain root), ``sku``, ``guide``, ``page`` (1-based),
``sha256`` (file hash), ``duplicate_of`` (first path with the same hash, else null), ``text``.

Identical files (same hash) are extracted once; output order is sorted by (pdf_path, page) so the
file is byte-stable across runs.

Usage:
  python3.12 scripts/retail/manuals/build_pdf_page_index.py [--brain-root brain/retail] [--out …]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_BRAIN = ROOT / "brain" / "retail"
DOCS_SUBDIR = Path("raw") / "sources" / "fridge-docs"


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


# The GE manual embeds fonts whose glyphs extract 29 code points low ("$XWRPDWLF" = "Automatic",
# space → \x03). Runs are maximal stretches of that shifted alphabet; real spaces and newlines
# delimit them (a real newline would otherwise decode to an apostrophe).
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
    """Decode shifted-glyph runs; keep real all-caps words, codes, and part numbers untouched.

    A run holding a shifted space/control char is always decoded. A bare one-word run is decoded only
    when the result is a manual word and the original is not (``,FHPDNHU`` → ``Icemaker`` but
    ``TROUBLESHOOTING`` stays).
    """

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
    """Return raw text per page (1 entry per page, possibly empty); cleaning happens in ``build_rows``."""
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
    print(f"build_pdf_page_index: {pdf.parent.name}/{pdf.name} {len(pages)} pages "
          f"({time.monotonic() - t0:.1f}s)", file=sys.stderr, flush=True)
    return pages


def build_rows(brain_root: Path, *, workers: int = 4) -> List[Dict[str, object]]:
    """Index every ``fridge-docs/<sku>/<guide>.pdf`` under ``brain_root``."""
    pdfs = sorted((brain_root / DOCS_SUBDIR).glob("*/*.pdf"), key=_canonical_order)
    if not pdfs:
        raise FileNotFoundError(f"no PDFs under {brain_root / DOCS_SUBDIR}")
    digests = {pdf: _sha256(pdf) for pdf in pdfs}
    first_path: Dict[str, str] = {}
    unique: Dict[str, Path] = {}
    for pdf in pdfs:
        if digests[pdf] not in unique:
            unique[digests[pdf]] = pdf
            first_path[digests[pdf]] = pdf.relative_to(brain_root).as_posix()
    # Image-heavy manuals take ~1 s/page in pypdf; one process per unique file bounds wall time.
    with ProcessPoolExecutor(max_workers=max(1, min(workers, len(unique)))) as pool:
        raw = dict(zip(unique, pool.map(_extract_timed, unique.values())))
    vocab = manual_vocab([t for pages in raw.values() for t in pages])
    cache = {d: [_clean(repair_shifted_glyphs(t, vocab)) for t in pages] for d, pages in raw.items()}
    rows: List[Dict[str, object]] = []
    for pdf in pdfs:
        rel = pdf.relative_to(brain_root).as_posix()
        digest = digests[pdf]
        if first_path[digest] != rel:
            print(f"build_pdf_page_index: {rel} duplicate of {first_path[digest]}", file=sys.stderr)
        duplicate_of = first_path[digest] if first_path[digest] != rel else None
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


def main(argv: List[str] | None = None) -> int:
    """CLI entry: build and write the page index."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--brain-root", type=Path, default=DEFAULT_BRAIN)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args(argv)
    out = args.out or (args.brain_root / "manifests" / "pdf_page_index.jsonl")
    rows = build_rows(args.brain_root)
    write_jsonl(rows, out)
    print(f"build_pdf_page_index: wrote {len(rows)} rows → {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
