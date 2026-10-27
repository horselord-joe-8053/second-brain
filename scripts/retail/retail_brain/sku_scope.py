"""Catalog SKU parsing and chunk filtering (canonical ids: ge_GNE27JYMFS, …).

Prefer ``product_scope.resolve_product_scope`` when both manual and ticket legs need filters.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

# Canonical catalog ids (ingest folder names under fridge-docs_md / manual_chunks.model_id).
LEGIT_CATALOG_SKUS: tuple[str, ...] = (
    "ge_GNE27JYMFS",
    "kitchenaid_KRFF507HPS",
    "samsung_RF28K9070SG",
)

# Back-compat alias used in M90 docs and tests.
LEGIT_MODEL_IDS = LEGIT_CATALOG_SKUS

LEGIT_MODEL_ID_SET: frozenset[str] = frozenset(LEGIT_CATALOG_SKUS)

_CANON_BY_LOWER: dict[str, str] = {m.lower(): m for m in LEGIT_CATALOG_SKUS}

LEGIT_MODEL_ID_PATTERN: re.Pattern[str] = re.compile(
    r"(ge_GNE27JYMFS|kitchenaid_KRFF507HPS|samsung_RF28K9070SG)",
    re.IGNORECASE,
)

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
    """Resolved catalog SKU filter for manual retrieval (open pool when multi-SKU)."""

    filter_model_id: str | None
    mentioned: tuple[str, ...]
    source: str


def normalize_model_id(model_id: str) -> str:
    """Lowercase trim; map legit catalog ids back to canonical casing."""
    raw = (model_id or "").strip()
    if not raw:
        return ""
    return _CANON_BY_LOWER.get(raw.lower(), raw.lower())


def canonical_model_id(model_id: str) -> str | None:
    """Return canonical catalog sku when input matches; else None."""
    key = (model_id or "").strip().lower()
    return _CANON_BY_LOWER.get(key)


def canonical_catalog_sku(value: str) -> str | None:
    """Alias for ``canonical_model_id`` (preferred name for new code)."""
    return canonical_model_id(value)


def infer_model_id_from_path_text(path_text: str) -> str:
    """Best-effort catalog sku token from a raw path string."""
    m = LEGIT_MODEL_ID_PATTERN.search(path_text)
    return _CANON_BY_LOWER[m.group(1).lower()] if m else ""


def find_legit_mentions(text: str) -> list[str]:
    """Unique catalog skus in order of first appearance in text."""
    out: list[str] = []
    seen: set[str] = set()
    for m in LEGIT_MODEL_ID_PATTERN.finditer(text or ""):
        canon = _CANON_BY_LOWER[m.group(1).lower()]
        if canon not in seen:
            seen.add(canon)
            out.append(canon)
    return out


def find_unknown_vendor_skus(text: str) -> list[str]:
    """Tokens like samsung_FOO that are not one of the three legit catalog ids."""
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
    """Parse query for catalog SKU scope; optional suite hint (catalog or OEM form)."""
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
        from retail_brain.company_profile import cached_company_profile

        folder = cached_company_profile().docs_folder_for_model(suite_model_id.strip())
        if folder:
            return RetrievalSkuScope(folder, (), "suite_oem_fallback")
    return RetrievalSkuScope(None, (), "none_open")


def sku_scope_to_dict(scope: RetrievalSkuScope) -> dict[str, Any]:
    """JSON-friendly metadata for results.jsonl search_meta."""
    return {
        "filter_model_id": scope.filter_model_id,
        "catalog_sku": scope.filter_model_id,
        "mentioned": list(scope.mentioned),
        "source": scope.source,
    }


def filter_chunks_by_model(
    chunks: list[dict[str, Any]],
    *,
    model_id: str | None,
) -> list[dict[str, Any]]:
    """Legacy: keep rows matching ingest ``model_id`` slug; prefer ``filter_chunks_by_product``."""
    want = normalize_model_id(model_id or "")
    if not want:
        return list(chunks)
    out: list[dict[str, Any]] = []
    for row in chunks:
        mid = normalize_model_id(str(row.get("model_id") or ""))
        if mid == want:
            out.append(row)
    return out


def filter_chunks_by_product(
    chunks: list[dict[str, Any]],
    *,
    brand: str | None,
    oem_model: str | None,
    ingest_key: str | None = None,
) -> list[dict[str, Any]]:
    """Keep manual chunk rows matching brand + OEM model; fall back to ingest slug if columns empty."""
    oem = (oem_model or "").strip()
    if not oem:
        return filter_chunks_by_model(chunks, model_id=ingest_key)
    b = (brand or "").strip()
    out: list[dict[str, Any]] = []
    for row in chunks:
        row_brand = str(row.get("brand") or "").strip()
        row_oem = str(row.get("oem_model") or "").strip()
        if row_oem and row_oem == oem and (not b or not row_brand or row_brand == b):
            out.append(row)
            continue
        if not row_oem and ingest_key:
            mid = normalize_model_id(str(row.get("model_id") or ""))
            if mid == normalize_model_id(ingest_key):
                out.append(row)
    return out
