"""Per-page text index over the retail fridge PDFs, used to cite manual evidence by page.

The index is a committed JSONL (``brain/retail/manifests/pdf_page_index.jsonl``) built once by
``scripts/retail/manuals/build_pdf_page_index.py``; this module only reads it, so CI never needs
``pypdf``.

Scoring is IDF-weighted query-token coverage: ``sum(idf(t) for t in query ∩ page) / sum(idf(t)
for t in query)``. It lies in [0, 1], is comparable across queries, and is deterministic
(ties → lower page number, then path).
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

DEFAULT_INDEX_PATH = (
    Path(__file__).resolve().parents[3] / "brain" / "retail" / "manifests" / "pdf_page_index.jsonl"
)

_TOKEN = re.compile(r"[a-z0-9]+")
# Function words plus manual boilerplate that would otherwise match every page.
_STOPWORDS = frozenset(
    """a an and are as at be been but by can do does for from has have how i if in into is it its
    my not of on or our so that the their them then there these this to too was we were what when
    which will with you your me us out up off very just also any all one two no yes
    please help customer reports need issue problem""".split()
)


@dataclass(frozen=True)
class PageRow:
    """One PDF page: path relative to the retail brain root, SKU folder, guide kind, 1-based page."""

    pdf_path: str
    sku: str
    guide: str
    page: int
    text: str


@lru_cache(maxsize=65536)
def _stem(t: str) -> str:
    """Light suffix stemmer (drips/dripping → drip, leaks/leaking → leak); applied to queries and pages alike."""
    if t.isdigit() or len(t) <= 3:
        return t
    if t.endswith("ies") and len(t) > 4:
        return t[:-3] + "y"
    for suf, min_len in (("ing", 6), ("ed", 5)):
        if t.endswith(suf) and len(t) >= min_len:
            t = t[: -len(suf)]
            if len(t) > 2 and t[-1] == t[-2] and t[-1] not in "lsz":
                t = t[:-1]
            return t
    if t.endswith("s") and not t.endswith("ss"):
        return t[:-1]
    return t


def tokenize(text: str) -> List[str]:
    """Lowercase, stemmed alphanumeric tokens without stopwords or 1-char noise."""
    return [_stem(t) for t in _TOKEN.findall((text or "").lower()) if len(t) > 1 and t not in _STOPWORDS]


class PdfPageIndex:
    """In-memory page index with SKU-scoped search and excerpt → page mapping."""

    def __init__(self, rows: Sequence[PageRow], *, duplicate_paths: Iterable[str] = ()) -> None:
        """Pre-tokenize pages and compute IDF; ``duplicate_paths`` are byte-copies hidden from raw search."""
        self.rows: List[PageRow] = list(rows)
        self.duplicate_paths: frozenset[str] = frozenset(duplicate_paths)
        seqs = [tokenize(r.text) for r in self.rows]
        self._tokens: List[frozenset[str]] = [frozenset(s) for s in seqs]
        self._bigrams: List[frozenset[Tuple[str, str]]] = [frozenset(zip(s, s[1:])) for s in seqs]
        self._density: List[Dict[str, float]] = []
        for s in seqs:
            counts: Dict[str, int] = {}
            for t in s:
                counts[t] = counts.get(t, 0) + 1
            self._density.append({t: c / len(s) for t, c in counts.items()})
        df: Dict[str, int] = {}
        for toks in self._tokens:
            for t in toks:
                df[t] = df.get(t, 0) + 1
        n = max(len(self.rows), 1)
        self._idf: Dict[str, float] = {t: math.log(1.0 + n / c) for t, c in df.items()}
        self._unseen_idf = math.log(1.0 + n)

    def _score(self, query_tokens: frozenset[str], i: int) -> float:
        """IDF-weighted share of the query's *indexed* tokens present on page ``i``.

        Tokens on no page at all (city names, FRU fault codes, ticket boilerplate) cannot tell pages
        apart; counting them would push every page under the floor for long ticket texts.
        """
        known = [t for t in query_tokens if t in self._idf]
        total = sum(self._idf[t] for t in known)
        hit = sum(self._idf[t] for t in query_tokens & self._tokens[i])
        return hit / total if total else 0.0

    def _ranked(
        self, query: str, indices: Iterable[int], k: int, min_score: float
    ) -> List[Tuple[PageRow, float]]:
        """Score candidate pages, drop weak ones, sort by score desc then page/path asc.

        Coverage saturates at 1.0 on long manuals (index and TOC pages contain every word), so ties
        break on query-phrase bigrams found on the page, then on query-term density.
        """
        seq = tokenize(query)
        q = frozenset(seq)
        q_bigrams = frozenset(zip(seq, seq[1:]))
        scored = []
        for i in indices:
            s = round(self._score(q, i), 4)
            if s <= 0 or s < min_score:
                continue
            phrase = len(q_bigrams & self._bigrams[i])
            density = round(sum(self._density[i].get(t, 0.0) for t in q), 6)
            scored.append((self.rows[i], s, phrase, density))
        scored.sort(key=lambda x: (-x[1], -x[2], -x[3], x[0].page, x[0].pdf_path))
        return [(r, s) for r, s, _, _ in scored[:k]]

    def search_pages(
        self,
        query: str,
        *,
        sku: Optional[str] = None,
        k: int = 3,
        min_score: float = 0.0,
        include_duplicates: bool = False,
    ) -> List[Tuple[PageRow, float]]:
        """Best pages for ``query`` within ``sku`` (all SKUs when None)."""
        idx = [
            i
            for i, r in enumerate(self.rows)
            if (sku is None or r.sku == sku) and (include_duplicates or r.pdf_path not in self.duplicate_paths)
        ]
        return self._ranked(query, idx, k, min_score)

    def best_pages(
        self, excerpt: str, pdf_path: str, *, k: int = 2, min_score: float = 0.0
    ) -> List[Tuple[int, float]]:
        """Pages of ``pdf_path`` that best match ``excerpt`` → ``[(page, score), …]``."""
        idx = [i for i, r in enumerate(self.rows) if r.pdf_path == pdf_path]
        return [(r.page, s) for r, s in self._ranked(excerpt, idx, k, min_score)]

    def pdf_paths(self, sku: Optional[str] = None) -> List[str]:
        """Sorted distinct PDF paths (optionally for one SKU)."""
        return sorted({r.pdf_path for r in self.rows if sku is None or r.sku == sku})


def load_page_index(path: Path = DEFAULT_INDEX_PATH) -> PdfPageIndex:
    """Read the builder's JSONL; rows flagged ``duplicate_of`` are kept but hidden from raw search."""
    rows: List[PageRow] = []
    dups: set[str] = set()
    with Path(path).open(encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            d = json.loads(line)
            rows.append(PageRow(d["pdf_path"], d["sku"], d["guide"], int(d["page"]), d.get("text", "")))
            if d.get("duplicate_of"):
                dups.add(d["pdf_path"])
    return PdfPageIndex(rows, duplicate_paths=dups)


@lru_cache(maxsize=2)
def cached_page_index(path: str = str(DEFAULT_INDEX_PATH)) -> PdfPageIndex:
    """Process-wide cached index (the committed file is read-only at runtime)."""
    return load_page_index(Path(path))
