"""Ticket leg of the ``retail_answer.v1`` bundle: top-2 similar resolved tickets with scores.

Two interchangeable sources:
  - ``InMemoryTicketSource`` — CSV/``TicketRow`` lists (CI tier; embeddings stubbed in pytest).
  - ``PgTicketSource`` — Postgres ``service_queries`` + pgvector + lexical backend (live tier).

Each hit carries ``cosine_similarity`` (query vs ticket embedding, comparable across queries — use it
for any cutoff) and ``fused_score`` (RRF score in hybrid modes; None in ``vector_only``). Order is the
search mode's rank order.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Protocol, Sequence, Tuple

from retail_brain.hybrid_search import TicketRow, cosine_similarities, search_ticket_scored
from retail_brain.models import RESOLVED
from retail_brain.search_mode import resolve_ticket_search_mode

COSINE_DP = 4
FUSED_DP = 6  # RRF scores are ~1/60; 4 dp would collapse distinct ranks.


class TicketSource(Protocol):
    """Backend that returns ranked, hydrated ticket hits for a query."""

    def hits(self, query: str, *, model: Optional[str], limit: int) -> Tuple[str, List[Dict[str, Any]]]:
        """Return ``(search_mode, hits)`` with ticket fields, ``cosine_similarity``, ``fused_score``."""
        ...


def load_issue_keys(manifest_path: Path) -> Dict[str, str]:
    """``ticket_id → issue_key`` from a corpus ``ticket_manifest.jsonl`` (rows without a key skipped)."""
    out: Dict[str, str] = {}
    with Path(manifest_path).open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                d = json.loads(line)
                if d.get("issue_key"):
                    out[d["ticket_id"]] = d["issue_key"]
    return out


class InMemoryTicketSource:
    """Offline source over ``TicketRow`` lists (same ranking code as the CSV eval harness)."""

    def __init__(self, rows: Sequence[TicketRow], issue_keys: Optional[Mapping[str, str]] = None) -> None:
        """Keep rows and an optional ``ticket_id → issue_key`` map."""
        self.rows = list(rows)
        self.issue_keys = dict(issue_keys or {})
        self._by_id = {r.ticket_id: r for r in self.rows}

    def hits(self, query: str, *, model: Optional[str], limit: int) -> Tuple[str, List[Dict[str, Any]]]:
        """Rank with ``search_ticket_scored`` then attach cosine + row fields."""
        mode = resolve_ticket_search_mode()
        scored = search_ticket_scored(query, self.rows, model_filter=model, limit=limit)
        rows = [self._by_id[tid] for tid, _ in scored]
        cos = cosine_similarities(query, rows)
        hits = [
            {
                "ticket_id": tid,
                "fused_score": fs,
                "cosine_similarity": cos[tid],
                "model": self._by_id[tid].model,
                "customer_query_text": self._by_id[tid].customer_query_text,
                "resolution_text": self._by_id[tid].resolution_text,
                "status": self._by_id[tid].status,
            }
            for tid, fs in scored
        ]
        return mode, hits


class PgTicketSource:
    """Live source: Postgres ``service_queries`` (needs ``RETAIL_DATABASE_URL`` + Gemini key)."""

    def __init__(self, dsn: str, issue_keys: Optional[Mapping[str, str]] = None) -> None:
        """Store the DSN and an optional ``ticket_id → issue_key`` map (PG has no issue column)."""
        self.dsn = dsn
        self.issue_keys = dict(issue_keys or {})

    def hits(self, query: str, *, model: Optional[str], limit: int) -> Tuple[str, List[Dict[str, Any]]]:
        """Delegate to ``pg_search.search_ticket_hits_pg`` (already resolved-only)."""
        from retail_brain.pg_search import search_ticket_hits_pg

        mode, hits = search_ticket_hits_pg(self.dsn, query, model_filter=model, limit=limit)
        for h in hits:
            h.setdefault("status", RESOLVED)
        return mode, hits


def ticket_leg(query: str, source: TicketSource, *, model: Optional[str] = None, k: int = 2) -> Dict[str, Any]:
    """Build ``{"search_mode", "hits": [...]}`` — ≤k resolved hits, ranked, rounded, hydrated."""
    mode, raw = source.hits(query, model=model, limit=max(k * 2, k))
    issue_keys = getattr(source, "issue_keys", {}) or {}
    hits: List[Dict[str, Any]] = []
    for h in raw:
        if h.get("status", RESOLVED) != RESOLVED:
            continue
        if model and h.get("model") != model:
            continue
        hits.append(
            {
                "rank": len(hits) + 1,
                "ticket_id": h["ticket_id"],
                "cosine_similarity": round(float(h["cosine_similarity"]), COSINE_DP),
                "fused_score": None if h.get("fused_score") is None else round(float(h["fused_score"]), FUSED_DP),
                "model": h.get("model"),
                "issue_key": issue_keys.get(h["ticket_id"]),
                "customer_query_text": h.get("customer_query_text", ""),
                "resolution_text": h.get("resolution_text", ""),
            }
        )
        if len(hits) == k:
            break
    return {"search_mode": mode, "hits": hits}
