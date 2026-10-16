"""Manual leg of the ``retail_answer.v1`` bundle: wiki evidence cited to ``.txt`` doc path (E14).

1. ``llm_wiki_search`` over compiled wiki (injected ``WikiSearchClient``).
2. Keep pages whose frontmatter ``sources:`` point at ``fridge-docs/<sku>/*.txt``.
3. No page numbers — ``raw_origin.pages`` is always ``[]``.
4. No usable wiki hit → SKU-scoped search over ``.txt`` files (``source: raw_txt``).

Wiki hits and raw hits are never mixed: wiki evidence wins when it exists.
The leg never raises for backend trouble; failures go in ``diagnostics.notes``.
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

from retail_brain.pdf_pages import tokenize
from retail_brain.txt_docs import TxtDocIndex, archive_pdf_for_doc

RAW_PREFIX = "raw/sources/"
EXCERPT_MAX_CHARS = 500
WIKI_RELEVANCE_FLOOR = 0.34
TXT_MATCH_FLOOR = 0.2
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

    def __init__(
        self,
        project: str,
        *,
        api_base: Optional[str] = None,
        token: Optional[str] = None,
        timeout: float = 20.0,
    ) -> None:
        """``project`` is the project UUID or its absolute path (the API accepts both)."""
        self.project = project
        self.api_base = (
            api_base or os.environ.get("LLM_WIKI_API_BASE_URL") or "http://127.0.0.1:19828/api/v1"
        ).rstrip("/")
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
        return cls(
            {
                f"wiki/sources/{p.relative_to(root).as_posix()}": p.read_text(encoding="utf-8")
                for p in sorted(root.rglob("*.md"))
            }
        )

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
    """``sources: ["fridge-docs/…txt", …]`` from Nashsu page frontmatter (paths relative to raw/sources)."""
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
    return page_text[m.end() :] if m else (page_text or "")


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
    """Raw-doc excerpt: the best-matching sentence plus following ones up to the char cap."""
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


def _sku_doc_paths(sources: Sequence[str], sku: str) -> List[str]:
    """Frontmatter sources under ``fridge-docs/<sku>/`` as brain-root-relative ``.txt`` paths."""
    prefix = f"fridge-docs/{sku}/"
    out: List[str] = []
    for s in sources:
        if not s.startswith(prefix):
            continue
        low = s.lower()
        if low.endswith(".txt"):
            out.append(RAW_PREFIX + s)
        elif low.endswith(".pdf"):
            out.append(RAW_PREFIX + s[:-4] + ".txt")
    return out


def _raw_origin_for_doc(doc_path: str) -> Dict[str, Any]:
    """Doc-level citation payload (no pages)."""
    return {
        "doc_path": doc_path,
        "archive_pdf_path": archive_pdf_for_doc(doc_path),
        "pages": [],
    }


def _pick_doc(doc_paths: Sequence[str], excerpt: str, query: str, txt_index: TxtDocIndex) -> Dict[str, Any]:
    """Choose the ``.txt`` whose content best matches excerpt or query."""
    if len(doc_paths) == 1:
        return _raw_origin_for_doc(doc_paths[0])
    best_path = doc_paths[0]
    best_score = 0.0
    for doc in sorted(doc_paths):
        hits = txt_index.search_docs(excerpt or query, sku=None, k=1, min_score=0.0)
        for row, score in hits:
            if row.doc_path == doc and score > best_score:
                best_score = score
                best_path = doc
    return _raw_origin_for_doc(best_path)


def _wiki_hits(
    query: str,
    sku: str,
    wiki: WikiSearchClient,
    txt_index: TxtDocIndex,
    k: int,
    notes: List[str],
) -> List[Dict[str, Any]]:
    """SKU-scoped, relevant wiki hits with doc-level raw-origin (may be empty)."""
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
        docs = _sku_doc_paths(parse_frontmatter_sources(text), sku)
        if not docs:
            continue
        excerpt, cov = best_excerpt(_body(text), query)
        if cov < WIKI_RELEVANCE_FLOOR:
            continue
        origin = _pick_doc(docs, excerpt, query, txt_index)
        hits.append(
            {
                "source": "wiki",
                "wiki_path": path,
                "excerpt": excerpt,
                "wiki_score": round(float(r.get("score") or 0.0), SCORE_DP),
                "raw_origin": origin,
            }
        )
        if len(hits) == k:
            break
    if results and not hits:
        notes.append(f"wiki returned {len(results)} page(s) but none relevant for {sku}")
    return hits


def _raw_txt_hits(query: str, sku: str, txt_index: TxtDocIndex, k: int) -> List[Dict[str, Any]]:
    """Direct ``.txt`` file hits (SKU-scoped)."""
    out = []
    for row, score in txt_index.search_docs(query, sku=sku, k=k, min_score=TXT_MATCH_FLOOR):
        out.append(
            {
                "source": "raw_txt",
                "wiki_path": None,
                "excerpt": _sentence_window(row.text, query),
                "wiki_score": None,
                "raw_origin": _raw_origin_for_doc(row.doc_path),
            }
        )
    return out


def manual_leg(
    query: str,
    *,
    sku: Optional[str],
    wiki: Optional[WikiSearchClient],
    txt_index: TxtDocIndex,
    k: int = 3,
) -> Dict[str, Any]:
    """Build ``{"hits": [...], "diagnostics": {...}}`` for the manual plane (ranked, ≤k hits)."""
    notes: List[str] = []
    wiki_available = False
    hits: List[Dict[str, Any]] = []
    if not sku:
        notes.append("no fridge model resolved; manual search skipped")
        return {"hits": [], "diagnostics": {"manual_leg_ok": False, "wiki_available": False, "notes": notes}}
    model_code = sku.split("_", 1)[-1]
    query = re.sub(rf"\b{re.escape(model_code)}\b", " ", query, flags=re.IGNORECASE)
    if wiki is not None:
        try:
            hits = _wiki_hits(query, sku, wiki, txt_index, k, notes)
            wiki_available = True
        except WikiUnavailable as e:
            notes.append(f"wiki unavailable: {e}")
    else:
        notes.append("wiki unavailable: no client configured")
    if not hits:
        hits = _raw_txt_hits(query, sku, txt_index, k)
    for i, h in enumerate(hits, start=1):
        h["rank"] = i
    ordered = [{key: h[key] for key in ("rank", "source", "wiki_path", "excerpt", "wiki_score", "raw_origin")} for h in hits]
    return {
        "hits": ordered,
        "diagnostics": {"manual_leg_ok": True, "wiki_available": wiki_available, "notes": notes},
    }
