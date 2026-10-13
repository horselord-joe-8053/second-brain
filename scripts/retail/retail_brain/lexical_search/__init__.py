"""Pluggable keyword (lexical) backends for ticket retrieval.

Contract for every backend class:
  - ``rebuild(rows)`` — ``rows`` are ``(ticket_id, customer_query_text, model)`` from Postgres reload.
  - ``search_ids(query, k, model_filter)`` — ordered ticket ids only; fusion happens in ``pg_search``.

``RETAIL_LEXICAL_BACKEND``: ``bm25x`` | ``tantivy`` | ``parade_db`` | ``open_search`` (default ``tantivy``).
Postgres remains the system of record; indexes are disposable copies under ``tmp/retail_lexical/`` or external URLs.
"""

from __future__ import annotations

import os
from typing import Optional, Sequence, Tuple

# ticket_id, raw customer_query_text, model (optional filter dimension)
TicketRow = Tuple[str, str, Optional[str]]
ALLOWED = ("bm25x", "tantivy", "parade_db", "open_search")


def lexical_backend_name() -> str:
    """Resolved ``RETAIL_LEXICAL_BACKEND`` with validation; default ``tantivy``."""
    raw = os.environ.get("RETAIL_LEXICAL_BACKEND", "").strip() or "tantivy"
    if raw not in ALLOWED:
        allowed = ", ".join(ALLOWED)
        raise ValueError(f"RETAIL_LEXICAL_BACKEND must be one of {allowed}; got {raw!r}")
    return raw


def open_lexical_index():
    """Build the selected backend. Import is lazy so unused engines are not required."""
    name = lexical_backend_name()
    if name == "tantivy":
        from retail_brain.lexical_search.tantivy_index import TantivyLexicalIndex

        return TantivyLexicalIndex()
    if name == "bm25x":
        from retail_brain.lexical_search.bm25x_index import Bm25xLexicalIndex

        return Bm25xLexicalIndex()
    if name == "parade_db":
        from retail_brain.lexical_search.parade_db import ParadeDbLexicalIndex

        return ParadeDbLexicalIndex()
    from retail_brain.lexical_search.open_search import OpenSearchLexicalIndex

    return OpenSearchLexicalIndex()


def rebuild_active(rows: Sequence[TicketRow]) -> None:
    """Rebuild only the backend named by RETAIL_LEXICAL_BACKEND."""
    open_lexical_index().rebuild(list(rows))
