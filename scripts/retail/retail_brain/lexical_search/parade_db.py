"""ParadeDB keyword client. Talks to RETAIL_PARADEDB_URL, not the retail Postgres on 5433.

The retail database stays pgvector. ParadeDB is a separate server. Unit tests pass a
fake cursor so verify does not start Docker.
"""

from __future__ import annotations

import os
from typing import Any, Optional, Sequence

from retail_brain.text_normalize import fts_query_text, search_text_for_fts

TicketRow = tuple[str, str, Optional[str]]


class ParadeDbLexicalIndex:
    """ParadeDB BM25 via SQL ``@@@``; table ``lexical_tickets`` must exist on the Parade server."""

    def __init__(self, cursor: Any | None = None) -> None:
        """Optional injected DB cursor for unit tests."""
        self._cursor = cursor

    def rebuild(self, rows: Sequence[TicketRow]) -> None:
        """Full replace: DELETE all rows then INSERT (same pattern as corpus reload)."""
        cur = self._cur()
        cur.execute("DELETE FROM lexical_tickets")
        for ticket_id, text, model in rows:
            cur.execute(
                "INSERT INTO lexical_tickets (ticket_id, search_text, model) VALUES (%s, %s, %s)",
                (ticket_id, search_text_for_fts(text or ""), model or ""),
            )
        conn = getattr(cur, "connection", None)
        if conn is not None:
            conn.commit()

    def search_ids(self, query: str, *, k: int, model_filter: str | None = None) -> list[str]:
        """ParadeDB BM25 search via ``search_text @@@ query``."""
        cur = self._cur()
        q = fts_query_text(query) or query
        cur.execute(
            """
            SELECT ticket_id
            FROM lexical_tickets
            WHERE search_text @@@ %s
              AND (%s::text IS NULL OR model = %s)
            ORDER BY pdb.score(id) DESC
            LIMIT %s
            """,
            (q, model_filter, model_filter, k),
        )
        return [row[0] for row in cur.fetchall()]

    def _cur(self) -> Any:
        """Tests inject ``cursor``; live use opens psycopg2 to ``RETAIL_PARADEDB_URL`` (not retail :5433)."""
        if self._cursor is not None:
            return self._cursor
        url = os.environ.get("RETAIL_PARADEDB_URL", "").strip()
        if not url:
            raise RuntimeError(
                "RETAIL_PARADEDB_URL is not set. ParadeDB is a separate database; "
                "the retail Postgres on 5433 does not provide this keyword index."
            )
        import psycopg2

        conn = psycopg2.connect(url)
        return conn.cursor()
