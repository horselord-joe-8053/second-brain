"""Ticket retriever protocol — implementation in ``ticket_retriever.py`` (P2.1)."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .types import EvidencePackage


@runtime_checkable
class TicketRetrieverPolicy(Protocol):
    """Adapter around Postgres + Tantivy ticket search (see ``TicketEvidenceRetriever``)."""

    def retrieve(self, query: str, *, model_filter: str) -> EvidencePackage:
        """Return normalized ticket evidence packages."""
        ...
