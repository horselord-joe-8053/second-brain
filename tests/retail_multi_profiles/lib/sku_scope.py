"""Central SKU catalog, query parsing, and chunk filtering for M90 fridge raw RAG."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

# Canonical suite model ids (folder names under fridge-docs_md).
LEGIT_MODEL_IDS: tuple[str, ...] = (
    "ge_GNE27JYMFS",
    "kitchenaid_KRFF507HPS",
    "samsung_RF28K9070SG",
)

LEGIT_MODEL_ID_SET: frozenset[str] = frozenset(LEGIT_MODEL_IDS)

_CANON_BY_LOWER: dict[str, str] = {m.lower(): m for m in LEGIT_MODEL_IDS}

LEGIT_MODEL_ID_PATTERN: re.Pattern[str] = re.compile(
    r"(ge_GNE27JYMFS|kitchenaid_KRFF507HPS|samsung_RF28K9070SG)",
    re.IGNORECASE,
)

# Vendor-prefixed tokens that are not one of the three legit ids (reject early).
_UNKNOWN_VENDOR_SKU_PATTERN: re.Pattern[str] = re.compile(
    r"\b(ge|kitchenaid|samsung)_[A-Za-z0-9]+\b",
    re.IGNORECASE,
)


class SkuScopeError(ValueError):
    """Query mentions an unknown SKU or an invalid multi-SKU scope."""

    def __init__(self, message: str, *, code: str = "unknown_sku") -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class RetrievalSkuScope:
    """Resolved SKU filter for retrieval (filter may be open when multi-SKU or no hint)."""

    filter_model_id: str | None
    mentioned: tuple[str, ...]
    source: str


def normalize_model_id(model_id: str) -> str:
    """Lowercase trim for comparisons; map legit ids back to canonical casing."""
    raw = (model_id or "").strip()
    if not raw:
        return ""
    return _CANON_BY_LOWER.get(raw.lower(), raw.lower())


def canonical_model_id(model_id: str) -> str | None:
    """Return canonical legit id when input matches catalog; else None."""
    key = (model_id or "").strip().lower()
    return _CANON_BY_LOWER.get(key)


def infer_model_id_from_path_text(path_text: str) -> str:
    """Best-effort SKU folder token from a raw path string."""
    m = LEGIT_MODEL_ID_PATTERN.search(path_text)
    return _CANON_BY_LOWER[m.group(1).lower()] if m else ""


def find_legit_mentions(text: str) -> list[str]:
    """Unique legit SKUs in order of first appearance in text."""
    out: list[str] = []
    seen: set[str] = set()
    for m in LEGIT_MODEL_ID_PATTERN.finditer(text or ""):
        canon = _CANON_BY_LOWER[m.group(1).lower()]
        if canon not in seen:
            seen.add(canon)
            out.append(canon)
    return out


def find_unknown_vendor_skus(text: str) -> list[str]:
    """Tokens like samsung_FOO that are not one of the three legit model ids."""
    unknown: list[str] = []
    seen: set[str] = set()
    for m in _UNKNOWN_VENDOR_SKU_PATTERN.finditer(text or ""):
        token = m.group(0)
        key = token.lower()
        if key in _CANON_BY_LOWER or key in seen:
            continue
        seen.add(key)
        unknown.append(token)
    return unknown


def resolve_retrieval_sku(
    query: str,
    *,
    suite_model_id: str | None = None,
    allow_suite_fallback: bool = True,
) -> RetrievalSkuScope:
    """Parse query for SKU scope: single-SKU filter, open pool, or suite fallback."""
    unknown = find_unknown_vendor_skus(query)
    if unknown:
        raise SkuScopeError(
            f"Unknown SKU token(s) in query: {', '.join(unknown)}",
            code="unknown_sku",
        )
    mentioned = find_legit_mentions(query)
    if len(mentioned) >= 2:
        return RetrievalSkuScope(None, tuple(mentioned), "query_multi_open")
    if len(mentioned) == 1:
        return RetrievalSkuScope(mentioned[0], tuple(mentioned), "query_single")
    if allow_suite_fallback and suite_model_id:
        canon = canonical_model_id(suite_model_id)
        if canon:
            return RetrievalSkuScope(canon, (), "suite_fallback")
    return RetrievalSkuScope(None, (), "none_open")


def sku_scope_to_dict(scope: RetrievalSkuScope) -> dict[str, Any]:
    """JSON-friendly metadata for results.jsonl search_meta."""
    return {
        "filter_model_id": scope.filter_model_id,
        "mentioned": list(scope.mentioned),
        "source": scope.source,
    }


def filter_chunks_by_model(
    chunks: list[dict[str, Any]],
    *,
    model_id: str | None,
) -> list[dict[str, Any]]:
    """Keep rows matching filter_model_id; empty filter returns the full list."""
    want = normalize_model_id(model_id or "")
    if not want:
        return list(chunks)
    out: list[dict[str, Any]] = []
    for row in chunks:
        mid = normalize_model_id(str(row.get("model_id") or ""))
        if mid == want:
            out.append(row)
    return out
