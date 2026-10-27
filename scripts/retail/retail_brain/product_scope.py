"""Unified product metadata for retrieval across manual, ticket, and bundled legs.

Filter contract: **brand + OEM model** on every leg (no POS SKU, no ingest-folder slug at query time).
``ingest_key`` (e.g. ``ge_GNE27JYMFS``) is lineage only — folder under ``fridge-docs_md``.

All callers resolve through ``resolve_product_scope`` at the query boundary.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from retail_brain.company_profile import CompanyProfile, cached_company_profile

from retail_brain.sku_scope import (  # noqa: E402
    SkuScopeError,
    canonical_model_id,
    resolve_retrieval_sku,
)


@dataclass(frozen=True)
class ProductFilter:
    """Postgres / pool filter: brand + manufacturer model code."""

    brand: str | None
    oem_model: str | None

    def active(self) -> bool:
        """True when at least OEM model is set (brand optional for transitional rows)."""
        return bool((self.oem_model or "").strip())


@dataclass(frozen=True)
class ProductScope:
    """Resolved product filters for heterogeneous legs (same incident, same brand+model)."""

    brand: str | None
    oem_model: str | None
    ingest_key: str | None
    source: str
    mentioned_ingest_keys: tuple[str, ...] = ()

    @property
    def manual_filter(self) -> ProductFilter:
        """Manual PG / raw pool filter."""
        return ProductFilter(self.brand, self.oem_model)

    @property
    def ticket_filter(self) -> ProductFilter:
        """Ticket Postgres ``service_queries`` filter (``brand`` + ``model`` columns)."""
        return ProductFilter(self.brand, self.oem_model)

    @property
    def catalog_sku(self) -> str | None:
        """Deprecated alias for ``ingest_key`` (one release)."""
        return self.ingest_key

    def to_metadata(self) -> dict[str, Any]:
        """JSON-friendly scope block for results.jsonl / retail_answer diagnostics."""
        pf = self.manual_filter
        return {
            "brand": pf.brand,
            "oem_model": pf.oem_model,
            "ingest_key": self.ingest_key,
            "catalog_sku": self.ingest_key,
            "source": self.source,
            "mentioned_ingest_keys": list(self.mentioned_ingest_keys),
        }


def product_for_ingest_key(ingest_key: str, profile: CompanyProfile | None = None) -> ProductFilter | None:
    """Map manual ingest folder id to brand + OEM model."""
    profile = profile or cached_company_profile()
    key = (ingest_key or "").strip()
    for m in profile.models:
        if m.get("docs_folder") == key:
            return ProductFilter(str(m.get("brand") or ""), str(m.get("sku") or ""))
    return None


def product_for_oem(oem_model: str, profile: CompanyProfile | None = None) -> ProductFilter | None:
    """Map ticket ``model`` column to brand + OEM (same OEM code)."""
    profile = profile or cached_company_profile()
    oem = (oem_model or "").strip()
    for m in profile.models:
        if m.get("sku") == oem:
            return ProductFilter(str(m.get("brand") or ""), oem)
    return None


def ingest_key_for_oem(oem_model: str, profile: CompanyProfile | None = None) -> str | None:
    """Manual tree folder for a ticket OEM code (ingest only)."""
    profile = profile or cached_company_profile()
    return profile.docs_folder_for_model((oem_model or "").strip())


def _catalog_from_manual_anchor(anchor_id: str) -> str | None:
    """B20 ``manual_anchor_question_id`` prefix (ge_GNE27JYMFS-E02 → ge_GNE27JYMFS)."""
    if not anchor_id:
        return None
    prefix = anchor_id.rsplit("-", 1)[0] if "-" in anchor_id else anchor_id
    return canonical_model_id(prefix)


def resolve_product_scope(
    query: str,
    *,
    suite_model: str | None = None,
    manual_anchor_question_id: str | None = None,
    allow_suite_fallback: bool = True,
    profile: CompanyProfile | None = None,
) -> ProductScope:
    """Single entry: parse query + optional gold/harness hints into brand + OEM model."""
    profile = profile or cached_company_profile()
    sku_scope = resolve_retrieval_sku(
        query,
        suite_model_id=suite_model if allow_suite_fallback else None,
        allow_suite_fallback=allow_suite_fallback,
    )
    mentioned = tuple(sku_scope.mentioned)

    ingest: str | None = sku_scope.filter_model_id
    source = sku_scope.source
    brand: str | None = None
    oem: str | None = None

    if ingest:
        pf = product_for_ingest_key(ingest, profile)
        if pf:
            brand, oem = pf.brand, pf.oem_model

    if not ingest and suite_model:
        canon = canonical_model_id(suite_model)
        if canon:
            ingest = canon
            source = "suite_catalog"
            pf = product_for_ingest_key(canon, profile)
            if pf:
                brand, oem = pf.brand, pf.oem_model
        else:
            pf = product_for_oem(suite_model, profile)
            if pf:
                brand, oem = pf.brand, pf.oem_model
                ingest = ingest_key_for_oem(suite_model, profile)
                source = "suite_oem_mapped"

    if not ingest and manual_anchor_question_id:
        anchor_cat = _catalog_from_manual_anchor(manual_anchor_question_id)
        if anchor_cat:
            ingest = anchor_cat
            source = "manual_anchor"
            pf = product_for_ingest_key(anchor_cat, profile)
            if pf:
                brand, oem = pf.brand, pf.oem_model

    if not oem and suite_model and not canonical_model_id(suite_model):
        oem = suite_model.strip()
        if not brand:
            pf = product_for_oem(oem, profile)
            if pf:
                brand = pf.brand
        if not ingest:
            ingest = ingest_key_for_oem(oem, profile)

    return ProductScope(
        brand=brand,
        oem_model=oem,
        ingest_key=ingest,
        source=source,
        mentioned_ingest_keys=mentioned,
    )


__all__ = [
    "ProductFilter",
    "ProductScope",
    "SkuScopeError",
    "ingest_key_for_oem",
    "product_for_ingest_key",
    "product_for_oem",
    "resolve_product_scope",
]
