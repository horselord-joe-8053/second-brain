"""Tantivy keyword index (default). A directory under tmp/, rebuilt from Postgres rows."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional, Sequence

from retail_brain.lexical_search.paths import backend_index_dir
from retail_brain.text_normalize import fts_query_text, search_text_for_fts

TicketRow = tuple[str, str, Optional[str]]


class TantivyLexicalIndex:
    """Default embedded BM25 index — no separate server; rebuilt on corpus reload."""

    def __init__(self, path: Path | str | None = None) -> None:
        """Use ``path`` or the default ``tmp/retail_lexical/tantivy`` directory."""
        self.path = Path(path) if path else backend_index_dir("tantivy")

    def rebuild(self, rows: Sequence[TicketRow]) -> None:
        """Wipe and rebuild index directory; body field uses ``search_text_for_fts`` token shape."""
        import tantivy

        if self.path.exists():
            shutil.rmtree(self.path)
        self.path.mkdir(parents=True)
        builder = tantivy.SchemaBuilder()
        builder.add_text_field("body", stored=True)
        # raw tokenizer: exact match for ticket_id / model filter clauses
        builder.add_text_field("ticket_id", stored=True, tokenizer_name="raw")
        builder.add_text_field("model", stored=True, tokenizer_name="raw")
        index = tantivy.Index(builder.build(), path=str(self.path))
        writer = index.writer(15_000_000)  # heap budget for bulk ingest
        for ticket_id, text, model in rows:
            writer.add_document(
                tantivy.Document(
                    body=search_text_for_fts(text or ""),
                    ticket_id=ticket_id,
                    model=model or "",
                )
            )
        writer.commit()
        index.reload()

    def search_scored(
        self, query: str, *, k: int, model_filter: str | None = None
    ) -> list[tuple[str, float]]:
        """Same as ``search_ids`` but returns ``(ticket_id, bm25_score)`` — Tantivy default scorer is BM25."""
        import tantivy

        meta = self.path / "meta.json"
        if not meta.is_file():
            raise FileNotFoundError(
                f"Tantivy index missing at {self.path}. Reload the corpus so the keyword index is rebuilt."
            )
        index = tantivy.Index.open(str(self.path))
        parsed = index.parse_query(self._expr(query, model_filter), ["body", "model"])
        searcher = index.searcher()
        hits = searcher.search(parsed, k).hits
        out: list[tuple[str, float]] = []
        for score, addr in hits:
            doc = searcher.doc(addr)
            out.append((doc["ticket_id"][0], float(score)))
        return out

    def search_ids(self, query: str, *, k: int, model_filter: str | None = None) -> list[str]:
        """Fail loud if reload never built the index (``meta.json`` missing)."""
        return [tid for tid, _ in self.search_scored(query, k=k, model_filter=model_filter)]

    @staticmethod
    def _sanitize_body_query(text: str) -> str:
        """Strip Tantivy field syntax triggers (e.g. ``help:`` in live intakes) while keeping tokens."""
        cleaned = text.replace(":", " ")
        for ch in '()+[]{}^~"\\':
            cleaned = cleaned.replace(ch, " ")
        return " ".join(cleaned.split())

    @classmethod
    def _expr(cls, query: str, model_filter: str | None) -> str:
        """Tantivy query string: body term search plus optional ``AND model:"..."``."""
        body = fts_query_text(query) or query
        safe = cls._sanitize_body_query(body)
        if not model_filter:
            return f"body:({safe})"
        model = model_filter.replace("\\", "\\\\").replace('"', '\\"')
        return f'body:({safe}) AND model:"{model}"'
