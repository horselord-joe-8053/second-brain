"""Adapter over the PyPI bm25x package (CPython 3.12 wheels only).

The section 11.4 sketch matches the constructor (index path, method="lucene")
and search(query, k=, subset=). Persistence is save/load plus a tickets.json
id map, because a new process cannot recover ticket ids from the extension alone.
Postgres remains the ticket store.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Optional, Sequence

from retail_brain.lexical_search.paths import backend_index_dir
from retail_brain.text_normalize import fts_query_text, search_text_for_fts

TicketRow = tuple[str, str, Optional[str]]


class Bm25xLexicalIndex:
    """CPython 3.12-only ``bm25x`` adapter; doc ids are positional — see ``tickets.json``."""

    def __init__(self, path: Path | str | None = None) -> None:
        """Use ``path`` or the default ``tmp/retail_lexical/bm25x`` directory."""
        self.path = Path(path) if path else backend_index_dir("bm25x")
        self._bm25 = None
        self._tickets: list[dict[str, str]] = []

    def rebuild(self, rows: Sequence[TicketRow]) -> None:
        """Build bm25x index on disk and write ``tickets.json`` id map."""
        from bm25x import BM25

        if self.path.exists():
            shutil.rmtree(self.path)
        self.path.mkdir(parents=True)
        index_dir = self.path / "index"
        self._bm25 = BM25(index=str(index_dir), method="lucene")
        texts = [search_text_for_fts(text or "") for _tid, text, _model in rows]
        self._bm25.add(texts)
        self._bm25.save(str(index_dir))
        # Extension stores vectors only; map doc index → ticket_id for search_ids.
        self._tickets = [
            {"ticket_id": ticket_id, "model": model or ""} for ticket_id, _text, model in rows
        ]
        (self.path / "tickets.json").write_text(json.dumps(self._tickets), encoding="utf-8")

    def search_ids(self, query: str, *, k: int, model_filter: str | None = None) -> list[str]:
        """Return top ``k`` ticket ids by bm25x score, optionally filtered by model."""
        self._ensure_loaded()
        assert self._bm25 is not None
        q = fts_query_text(query) or query
        # bm25x.search(subset=...) restricts to doc indices before top-k (model-scoped retrieval).
        subset = None
        if model_filter is not None:
            subset = [i for i, row in enumerate(self._tickets) if row["model"] == model_filter]
        hits = self._bm25.search(q, k=k, subset=subset) if subset is not None else self._bm25.search(q, k=k)
        out: list[str] = []
        for doc_id, _score in hits:
            out.append(self._tickets[int(doc_id)]["ticket_id"])
        return out

    def _ensure_loaded(self) -> None:
        """Lazy-load ``BM25`` and ``tickets.json`` from disk on first search."""
        if self._bm25 is not None and self._tickets:
            return
        meta = self.path / "tickets.json"
        if not meta.is_file():
            raise FileNotFoundError(
                f"bm25x index missing at {self.path}. Reload the corpus so the keyword index is rebuilt."
            )
        from bm25x import BM25

        self._tickets = json.loads(meta.read_text(encoding="utf-8"))
        self._bm25 = BM25.load(str(self.path / "index"))
