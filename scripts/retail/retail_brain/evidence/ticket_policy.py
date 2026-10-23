"""Ticket retriever policy stub (Phase 2 — HG-P1)."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .types import EvidencePackage


@runtime_checkable
class TicketRetrieverPolicy(Protocol):
    """Phase 2 adapter around Postgres + Tantivy ticket search."""

    def retrieve(self, query: str, *, model_filter: str) -> EvidencePackage:
        """Return normalized ticket evidence packages."""
        ...
