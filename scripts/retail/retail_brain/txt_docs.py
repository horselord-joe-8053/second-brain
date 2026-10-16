"""SKU-scoped search over committed manual ``.txt`` files (doc-level, no page index at runtime).

Loads ``raw/sources/fridge-docs/<sku>/*.txt`` under the retail brain root. Scoring reuses
``PdfPageIndex`` (IDF-weighted token coverage) with one virtual page per file.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

from retail_brain.pdf_pages import PageRow, PdfPageIndex

RAW_PREFIX = "raw/sources/"
FRIDGE = "fridge-docs/"


@dataclass(frozen=True)
class TxtDocRow:
    """One manual text file relative to the retail brain root."""

    doc_path: str
    sku: str
    guide: str
    text: str


def archive_pdf_for_doc(doc_path: str) -> str:
    """Map ``raw/sources/fridge-docs/…/user-guide.txt`` → ``archive/fridge-docs/…/user-guide.pdf``."""
    if not doc_path.endswith(".txt"):
        return doc_path.replace(RAW_PREFIX, "archive/").removesuffix(".pdf") + ".pdf"
    tail = doc_path.split(FRIDGE, 1)[-1]
    return f"archive/{FRIDGE}{tail[:-4]}.pdf"


class TxtDocIndex:
    """In-memory index over whole ``.txt`` manuals with SKU-scoped search."""

    def __init__(self, rows: Sequence[TxtDocRow]) -> None:
        """Wrap each doc as a single-page ``PdfPageIndex`` row for shared scoring."""
        self.rows: List[TxtDocRow] = list(rows)
        page_rows = [PageRow(r.doc_path, r.sku, r.guide, 1, r.text) for r in self.rows]
        self._inner = PdfPageIndex(page_rows)

    def search_docs(
        self,
        query: str,
        *,
        sku: Optional[str] = None,
        k: int = 3,
        min_score: float = 0.0,
    ) -> List[Tuple[TxtDocRow, float]]:
        """Best matching ``.txt`` files for ``query`` within ``sku``."""
        hits = self._inner.search_pages(query, sku=sku, k=k, min_score=min_score)
        out: List[Tuple[TxtDocRow, float]] = []
        for row, score in hits:
            doc = next(r for r in self.rows if r.doc_path == row.pdf_path)
            out.append((doc, score))
        return out


def load_txt_docs(brain_root: Path) -> TxtDocIndex:
    """Read every ``fridge-docs/*/*.txt`` under ``brain_root/raw/sources``."""
    base = brain_root / "raw" / "sources" / "fridge-docs"
    rows: List[TxtDocRow] = []
    for path in sorted(base.glob("*/*.txt")):
        rel = path.relative_to(brain_root).as_posix()
        sku = path.parent.name
        guide = path.stem.removesuffix("-guide")
        text = path.read_text(encoding="utf-8")
        rows.append(TxtDocRow(rel, sku, guide, text))
    return TxtDocIndex(rows)


@lru_cache(maxsize=2)
def cached_txt_docs(brain_root: str = "") -> TxtDocIndex:
    """Process-wide cached docs (default retail brain root)."""
    root = Path(brain_root) if brain_root else Path(__file__).resolve().parents[3] / "brain" / "retail"
    return load_txt_docs(root)
