"""Manual leg of the ``retail_answer.v1`` bundle: wiki evidence cited back to raw PDF path + page.

Decision E4 (brain-profiles plan):
  1. ``llm_wiki_search`` over the compiled ``brain/retail/wiki`` (via an injected ``WikiSearchClient``).
  2. Keep pages whose frontmatter ``sources:`` point into ``fridge-docs/<sku>/`` (SKU scope).
  3. Map the chosen wiki excerpt to page(s) of that PDF with ``pdf_pages.PdfPageIndex.best_pages``.
  4. No usable wiki hit (app down, no SKU page, nothing relevant) → search PDF pages directly
     (``source: raw_pdf``).
Wiki hits and raw hits are never mixed in one leg: wiki evidence wins when it exists.

The leg never raises for backend trouble; it records it in ``diagnostics.notes``.
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Sequence, Tuple

from retail_brain.pdf_pages import PdfPageIndex, tokenize

RAW_PREFIX = "raw/sources/"
EXCERPT_MAX_CHARS = 500
WIKI_RELEVANCE_FLOOR = 0.34  # share of query tokens an excerpt must contain to count as an answer
PAGE_MATCH_FLOOR = 0.2
SCORE_DP = 4


class WikiUnavailable(RuntimeError):
    """LLM Wiki app/API not reachable or project not open."""


class WikiSearchClient(Protocol):
    """Minimal wiki surface the manual leg needs (mirrors ``llm_wiki_search`` + ``llm_wiki_read_file``)."""

    def search(self, query: str, *, limit: int) -> List[Dict[str, Any]]:
        """Ranked hits ``[{"path": "wiki/…md", "snippet": str, "score": float}, …]``."""
        ...

    def read(self, path: str) -> str:
        """Full text of a project-relative wiki page."""
        ...


class LlmWikiHttpClient:
    """Live client for the LLM Wiki desktop API (``POST …/search``, ``GET …/files/content``)."""

    def __init__(self, project: str, *, api_base: Optional[str] = None, token: Optional[str] = None,
                 timeout: float = 20.0) -> None:
        """``project`` is the project UUID or its absolute path (the API accepts both)."""
        self.project = project
        self.api_base = (api_base or os.environ.get("LLM_WIKI_API_BASE_URL") or "http://127.0.0.1:19828/api/v1").rstrip("/")
        self.token = token if token is not None else os.environ.get("LLM_WIKI_API_TOKEN", "")
        self.timeout = timeout

    def _request(self, method: str, url: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """JSON request with Bearer auth; network/HTTP errors become ``WikiUnavailable``."""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            raise WikiUnavailable(f"HTTP {e.code} from {url}") from e
        except (urllib.error.URLError, OSError, ValueError) as e:
            raise WikiUnavailable(f"{type(e).__name__}: {e}") from e

    def _project_url(self) -> str:
        """``…/projects/<url-encoded id or path>``."""
        return f"{self.api_base}/projects/{urllib.parse.quote(self.project, safe='')}"

    def search(self, query: str, *, limit: int) -> List[Dict[str, Any]]:
        """Hybrid wiki search; returns the API's ``results`` list."""
        out = self._request("POST", f"{self._project_url()}/search", {"query": query, "topK": limit})
        return list(out.get("results") or [])

    def read(self, path: str) -> str:
        """Read one wiki page's text."""
        q = urllib.parse.urlencode({"path": path})
        return str(self._request("GET", f"{self._project_url()}/files/content?{q}").get("content") or "")


class FixtureWikiClient:
    """Offline ``WikiSearchClient`` over in-memory pages (CI tier); ranks by query-token coverage."""

    def __init__(self, pages: Dict[str, str]) -> None:
        """``pages`` maps project-relative wiki paths (``wiki/sources/x.md``) to page text."""
        self.pages = dict(pages)

    @classmethod
    def from_dir(cls, directory: Path) -> "FixtureWikiClient":
        """Load ``*.md`` under ``directory`` as ``wiki/sources/<relative path>``."""
        root = Path(directory)
        return cls({f"wiki/sources/{p.relative_to(root).as_posix()}": p.read_text(encoding="utf-8")
                    for p in sorted(root.rglob("*.md"))})

    def search(self, query: str, *, limit: int) -> List[Dict[str, Any]]:
        """Pages with any query-token overlap, best coverage first (ties → path)."""
        q = frozenset(tokenize(query))
        scored = [(_coverage(q, _body(text)), path) for path, text in self.pages.items()]
        ranked = sorted((s for s in scored if s[0] > 0), key=lambda s: (-s[0], s[1]))
        return [{"path": p, "snippet": "", "score": round(s, SCORE_DP)} for s, p in ranked[:limit]]

    def read(self, path: str) -> str:
        """Page text by path."""
        return self.pages[path]


_FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_SOURCES_LINE = re.compile(r"^sources:\s*\[(.*)\]\s*$", re.MULTILINE)


def parse_frontmatter_sources(page_text: str) -> List[str]:
    """``sources: ["fridge-docs/…pdf", …]`` from Nashsu page frontmatter (paths relative to raw/sources)."""
    m = _FRONTMATTER.match(page_text or "")
    if not m:
        return []
    s = _SOURCES_LINE.search(m.group(1))
    if not s:
        return []
    return [p.strip().strip('"').strip("'") for p in s.group(1).split(",") if p.strip()]


def _body(page_text: str) -> str:
    """Page text without frontmatter."""
    m = _FRONTMATTER.match(page_text or "")
    return page_text[m.end():] if m else (page_text or "")


def _coverage(query_tokens: frozenset[str], text: str) -> float:
    """Share of query tokens present in ``text`` (0–1, unweighted)."""
    if not query_tokens:
        return 0.0
    return len(query_tokens & set(tokenize(text))) / len(query_tokens)


def _clip(text: str) -> str:
    """Single-line excerpt capped at ``EXCERPT_MAX_CHARS`` on a word boundary."""
    flat = " ".join(text.split())
    if len(flat) <= EXCERPT_MAX_CHARS:
        return flat
    cut = flat[:EXCERPT_MAX_CHARS].rsplit(" ", 1)[0]
    return cut + " …"


def best_excerpt(text: str, query: str) -> Tuple[str, float]:
    """Most query-relevant paragraph/section of ``text`` → ``(excerpt, coverage)``; ties → earliest."""
    q = frozenset(tokenize(query))
    blocks = [b for b in re.split(r"\n\s*\n|\n(?=#)", text) if b.strip()]
    best, best_score = "", 0.0
    for block in blocks:
        score = _coverage(q, block)
        if score > best_score:
            best, best_score = block, score
    return _clip(re.sub(r"^#+\s*", "", best, flags=re.MULTILINE)), round(best_score, SCORE_DP)


def _sentence_window(text: str, query: str) -> str:
    """Raw-page excerpt: the best-matching sentence plus following ones up to the char cap."""
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()] or [text]
    q = frozenset(tokenize(query))
    scores = [_coverage(q, s) for s in sentences]
    start = max(range(len(sentences)), key=lambda i: (scores[i], -i))
    out = ""
    for s in sentences[start:]:
        if out and len(out) + len(s) + 1 > EXCERPT_MAX_CHARS:
            break
        out = f"{out} {s}".strip()
    return _clip(out)


def _sku_pdfs(sources: Sequence[str], sku: str) -> List[str]:
    """Frontmatter sources under ``fridge-docs/<sku>/`` as brain-root-relative PDF paths."""
    prefix = f"fridge-docs/{sku}/"
    return [RAW_PREFIX + s for s in sources if s.startswith(prefix) and s.lower().endswith(".pdf")]


def _cite(page_index: PdfPageIndex, excerpt: str, query: str, pdf_paths: Sequence[str]) -> Dict[str, Any]:
    """Pick the cited PDF + pages whose text best matches the excerpt (fallback: the query)."""
    best: Tuple[float, str, List[int]] = (0.0, pdf_paths[0], [])
    for pdf in sorted(pdf_paths):
        for probe in (excerpt, query):
            pages = page_index.best_pages(probe, pdf, k=2, min_score=PAGE_MATCH_FLOOR)
            if pages and pages[0][1] > best[0]:
                best = (pages[0][1], pdf, sorted(p for p, _ in pages))
            if pages:
                break
    score, pdf, pages = best
    return {"pdf_path": pdf, "pages": pages, "page_match_score": round(score, SCORE_DP) if pages else None}


def _wiki_hits(query: str, sku: str, wiki: WikiSearchClient, page_index: PdfPageIndex, k: int,
               notes: List[str]) -> List[Dict[str, Any]]:
    """SKU-scoped, relevant wiki hits with raw-origin citations (may be empty)."""
    model_code = sku.split("_", 1)[-1]
    results = wiki.search(f"{query} {model_code}", limit=max(10, k * 3))
    hits: List[Dict[str, Any]] = []
    seen: set[str] = set()
    for r in results:
        path = str(r.get("path") or "")
        if not path or path in seen:
            continue
        seen.add(path)
        text = r.get("content") or wiki.read(path)
        pdfs = _sku_pdfs(parse_frontmatter_sources(text), sku)
        if not pdfs:
            continue
        excerpt, cov = best_excerpt(_body(text), query)
        if cov < WIKI_RELEVANCE_FLOOR:
            continue
        hits.append({"source": "wiki", "wiki_path": path, "excerpt": excerpt,
                     "wiki_score": round(float(r.get("score") or 0.0), SCORE_DP),
                     "raw_origin": _cite(page_index, excerpt, query, pdfs)})
        if len(hits) == k:
            break
    if results and not hits:
        notes.append(f"wiki returned {len(results)} page(s) but none relevant for {sku}")
    return hits


def _raw_hits(query: str, sku: str, page_index: PdfPageIndex, k: int) -> List[Dict[str, Any]]:
    """Direct PDF page hits (SKU-scoped, duplicate files hidden)."""
    out = []
    for row, score in page_index.search_pages(query, sku=sku, k=k, min_score=PAGE_MATCH_FLOOR):
        out.append({"source": "raw_pdf", "wiki_path": None, "excerpt": _sentence_window(row.text, query),
                    "wiki_score": None,
                    "raw_origin": {"pdf_path": row.pdf_path, "pages": [row.page], "page_match_score": score}})
    return out


def manual_leg(query: str, *, sku: Optional[str], wiki: Optional[WikiSearchClient],
               page_index: PdfPageIndex, k: int = 3) -> Dict[str, Any]:
    """Build ``{"hits": [...], "diagnostics": {...}}`` for the manual plane (ranked, ≤k hits)."""
    notes: List[str] = []
    wiki_available = False
    hits: List[Dict[str, Any]] = []
    if not sku:
        notes.append("no fridge model resolved; manual search skipped")
        return {"hits": [], "diagnostics": {"manual_leg_ok": False, "wiki_available": False, "notes": notes}}
    # The model code appears on cover/spec pages only; leaving it in biases page ranking toward them.
    model_code = sku.split("_", 1)[-1]
    query = re.sub(rf"\b{re.escape(model_code)}\b", " ", query, flags=re.IGNORECASE)
    if wiki is not None:
        try:
            hits = _wiki_hits(query, sku, wiki, page_index, k, notes)
            wiki_available = True
        except WikiUnavailable as e:
            notes.append(f"wiki unavailable: {e}")
    else:
        notes.append("wiki unavailable: no client configured")
    if not hits:
        hits = _raw_hits(query, sku, page_index, k)
    for i, h in enumerate(hits, start=1):
        h["rank"] = i
    ordered = [{key: h[key] for key in ("rank", "source", "wiki_path", "excerpt", "wiki_score", "raw_origin")}
               for h in hits]
    return {"hits": ordered, "diagnostics": {"manual_leg_ok": True, "wiki_available": wiki_available,
                                             "notes": notes}}
