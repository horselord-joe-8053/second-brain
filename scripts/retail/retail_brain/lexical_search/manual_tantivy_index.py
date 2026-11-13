"""Tantivy BM25 index for manual_chunks (separate from ticket keyword index)."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional, Sequence

from retail_brain.lexical_search.paths import backend_index_dir
from retail_brain.text_normalize import fts_query_text, search_text_for_fts

ManualChunkRow = tuple[str, str, str, str]


class ManualTantivyLexicalIndex:
    """Embedded BM25 over manual chunk bodies; filter by brand + OEM model at query time."""

    def __init__(self, path: Path | str | None = None) -> None:
        """Default path ``tmp/retail_lexical/manual_tantivy`` (override via env in rebuild script)."""
        self.path = Path(path) if path else backend_index_dir("manual_tantivy")

    def rebuild(self, rows: Sequence[ManualChunkRow]) -> None:
        """Wipe and rebuild; ``rows`` are (chunk_id, text, brand, oem_model)."""
        import tantivy

        if self.path.exists():
            shutil.rmtree(self.path)
        self.path.mkdir(parents=True)
        builder = tantivy.SchemaBuilder()
        builder.add_text_field("body", stored=True)
        builder.add_text_field("chunk_id", stored=True, tokenizer_name="raw")
        builder.add_text_field("brand", stored=True, tokenizer_name="raw")
        builder.add_text_field("oem_model", stored=True, tokenizer_name="raw")
        index = tantivy.Index(builder.build(), path=str(self.path))
        writer = index.writer(15_000_000)
        for chunk_id, text, brand, oem_model in rows:
            writer.add_document(
                tantivy.Document(
                    body=search_text_for_fts(text or ""),
                    chunk_id=chunk_id,
                    brand=brand or "",
                    oem_model=oem_model or "",
                )
            )
        writer.commit()
        index.reload()

    def search_scored(
        self,
        query: str,
        *,
        k: int,
        brand_filter: str | None = None,
        oem_model_filter: str | None = None,
    ) -> list[tuple[str, float]]:
        """Return (manual_chunk_id, bm25_score) hits."""
        import tantivy

        meta = self.path / "meta.json"
        if not meta.is_file():
            raise FileNotFoundError(
                f"Manual Tantivy index missing at {self.path}. Rebuild after manual PG ingest."
            )
        index = tantivy.Index.open(str(self.path))
        parsed = index.parse_query(
            self._expr(query, brand_filter, oem_model_filter),
            ["body", "brand", "oem_model"],
        )
        searcher = index.searcher()
        hits = searcher.search(parsed, k).hits
        out: list[tuple[str, float]] = []
        for score, addr in hits:
            doc = searcher.doc(addr)
            out.append((doc["chunk_id"][0], float(score)))
        return out

    @staticmethod
    def _sanitize_body_query(text: str) -> str:
        """Strip Tantivy field-syntax triggers while keeping tokens."""
        cleaned = text.replace(":", " ")
        for ch in '()+[]{}^~"\\':
            cleaned = cleaned.replace(ch, " ")
        return " ".join(cleaned.split())

    @classmethod
    def _expr(
        cls,
        query: str,
        brand_filter: str | None,
        oem_model_filter: str | None,
    ) -> str:
        """Body term search with optional brand and OEM model clauses."""
        body = fts_query_text(query) or query
        safe = cls._sanitize_body_query(body)
        parts = [f"body:({safe})"]
        if brand_filter:
            b = brand_filter.replace("\\", "\\\\").replace('"', '\\"')
            parts.append(f'brand:"{b}"')
        if oem_model_filter:
            m = oem_model_filter.replace("\\", "\\\\").replace('"', '\\"')
            parts.append(f'oem_model:"{m}"')
        return " AND ".join(parts)
