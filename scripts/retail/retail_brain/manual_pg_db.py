"""Postgres helpers for manual_chunks (schema apply, CRUD, vector search)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Sequence

RETAIL_ROOT = Path(__file__).resolve().parents[1]
MIGRATION_SQL = RETAIL_ROOT / "schema" / "005_manual_chunks.sql"
BRAND_MODEL_SQL = RETAIL_ROOT / "schema" / "006_product_brand_model.sql"

MANUAL_EMBED_DIM = 1536


def _parse_pgvector(raw: Any) -> list[float]:
    """Normalize pgvector column values from psycopg2 (str, list, or None)."""
    if raw is None:
        return []
    if isinstance(raw, (list, tuple)):
        return [float(x) for x in raw]
    s = str(raw).strip()
    if not s or s == "None":
        return []
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1]
    if not s.strip():
        return []
    return [float(x) for x in s.split(",")]


def _migration_sql() -> str:
    """Load 005_manual_chunks.sql from disk."""
    return MIGRATION_SQL.read_text(encoding="utf-8")


def apply_manual_chunks_schema(cur) -> None:
    """Idempotently create manual_chunks table and indexes."""
    cur.execute(_migration_sql())
    if BRAND_MODEL_SQL.is_file():
        cur.execute(BRAND_MODEL_SQL.read_text(encoding="utf-8"))


def _vector_literal(vec: Sequence[float]) -> str:
    """pgvector text literal for query embedding."""
    return "[" + ",".join(str(float(x)) for x in vec) + "]"


def upsert_manual_chunks(cur, rows: Iterable[dict[str, Any]]) -> int:
    """Insert or update chunk rows; returns number of rows touched."""
    n = 0
    for row in rows:
        emb = row.get("embedding")
        brand = str(row.get("brand") or "")
        oem_model = str(row.get("oem_model") or "")
        base = (
            row["chunk_id"],
            row["lane_id"],
            row["source_relpath"],
            row["model_id"],
            brand,
            oem_model,
            int(row["chunk_index"]),
            row["text"],
            row["content_hash"],
            row["text"],
        )
        if emb:
            lit = _vector_literal(emb)
            cur.execute(
                """
                INSERT INTO manual_chunks (
                  chunk_id, lane_id, source_relpath, model_id, brand, oem_model, chunk_index,
                  text, content_hash, embedding, chunk_tsv
                ) VALUES (
                  %s, %s, %s, %s, %s, %s, %s,
                  %s, %s, %s::vector,
                  to_tsvector('english', %s)
                )
                ON CONFLICT (chunk_id) DO UPDATE SET
                  lane_id = EXCLUDED.lane_id,
                  source_relpath = EXCLUDED.source_relpath,
                  model_id = EXCLUDED.model_id,
                  brand = EXCLUDED.brand,
                  oem_model = EXCLUDED.oem_model,
                  chunk_index = EXCLUDED.chunk_index,
                  text = EXCLUDED.text,
                  content_hash = EXCLUDED.content_hash,
                  embedding = EXCLUDED.embedding,
                  chunk_tsv = EXCLUDED.chunk_tsv,
                  updated_at = now()
                """,
                (*base[:-1], lit, base[-1]),
            )
        else:
            cur.execute(
                """
                INSERT INTO manual_chunks (
                  chunk_id, lane_id, source_relpath, model_id, brand, oem_model, chunk_index,
                  text, content_hash, embedding, chunk_tsv
                ) VALUES (
                  %s, %s, %s, %s, %s, %s, %s,
                  %s, %s, NULL,
                  to_tsvector('english', %s)
                )
                ON CONFLICT (chunk_id) DO UPDATE SET
                  lane_id = EXCLUDED.lane_id,
                  source_relpath = EXCLUDED.source_relpath,
                  model_id = EXCLUDED.model_id,
                  brand = EXCLUDED.brand,
                  oem_model = EXCLUDED.oem_model,
                  chunk_index = EXCLUDED.chunk_index,
                  text = EXCLUDED.text,
                  content_hash = EXCLUDED.content_hash,
                  embedding = EXCLUDED.embedding,
                  chunk_tsv = EXCLUDED.chunk_tsv,
                  updated_at = now()
                """,
                base,
            )
        n += 1
    return n


def delete_manual_chunks_for_lane(cur, *, lane_id: str, keep_ids: set[str]) -> int:
    """Remove stale chunks for a lane not present in keep_ids."""
    if not keep_ids:
        cur.execute("DELETE FROM manual_chunks WHERE lane_id = %s", (lane_id,))
        return cur.rowcount
    cur.execute(
        """
        DELETE FROM manual_chunks
        WHERE lane_id = %s AND NOT (chunk_id = ANY(%s))
        """,
        (lane_id, list(keep_ids)),
    )
    return cur.rowcount


def list_manual_chunks(
    cur,
    *,
    lane_id: str,
    limit: int = 5000,
    brand: str | None = None,
    oem_model: str | None = None,
) -> list[dict[str, Any]]:
    """Load chunk rows for hybrid pool; optional brand+OEM SQL filter (evo-18 T0)."""
    clauses = ["lane_id = %s"]
    params: list[Any] = [lane_id]
    if (brand or "").strip():
        clauses.append("brand = %s")
        params.append(brand.strip())
    if (oem_model or "").strip():
        clauses.append("oem_model = %s")
        params.append(oem_model.strip())
    params.append(limit)
    cur.execute(
        f"""
        SELECT chunk_id, source_relpath, model_id, brand, oem_model, text, embedding
        FROM manual_chunks
        WHERE {" AND ".join(clauses)}
        LIMIT %s
        """,
        tuple(params),
    )
    out: list[dict[str, Any]] = []
    for chunk_id, rel, model_id, brand, oem_model, text, emb in cur.fetchall():
        vec = _parse_pgvector(emb)
        out.append(
            {
                "chunk_id": chunk_id,
                "source_relpath": rel,
                "model_id": model_id,
                "brand": brand,
                "oem_model": oem_model,
                "text": text,
                "vector": vec,
            }
        )
    return out


def knn_manual_chunks(
    cur,
    *,
    lane_id: str,
    query_vector: Sequence[float],
    limit: int,
    brand: str | None = None,
    oem_model: str | None = None,
) -> list[dict[str, Any]]:
    """Dense leg: cosine distance order on manual_chunks.embedding with optional product filter."""
    lit = _vector_literal(query_vector)
    clauses = ["lane_id = %s", "embedding IS NOT NULL"]
    params: list[Any] = [lit, lane_id]
    if (brand or "").strip():
        clauses.append("brand = %s")
        params.append(brand.strip())
    if (oem_model or "").strip():
        clauses.append("oem_model = %s")
        params.append(oem_model.strip())
    params.extend([lit, limit])
    cur.execute(
        f"""
        SELECT chunk_id, source_relpath, model_id, brand, oem_model, text,
               (embedding <=> %s::vector) AS distance
        FROM manual_chunks
        WHERE {" AND ".join(clauses)}
        ORDER BY embedding <=> %s::vector
        LIMIT %s
        """,
        tuple(params),
    )
    out: list[dict[str, Any]] = []
    for chunk_id, rel, model_id, brand_val, oem_val, text, dist in cur.fetchall():
        d = float(dist)
        out.append(
            {
                "chunk_id": chunk_id,
                "source_relpath": rel,
                "model_id": model_id,
                "brand": brand_val,
                "oem_model": oem_val,
                "text": text,
                "distance": d,
                "vector_score": 1.0 / (1.0 + d),
            }
        )
    return out


def fetch_manual_chunks_by_ids(
    cur,
    *,
    lane_id: str,
    chunk_ids: Sequence[str],
) -> list[dict[str, Any]]:
    """Hydrate chunk rows for RRF merge after id-only lexical search."""
    ids = [str(c) for c in chunk_ids if str(c).strip()]
    if not ids:
        return []
    cur.execute(
        """
        SELECT chunk_id, source_relpath, model_id, brand, oem_model, text, embedding
        FROM manual_chunks
        WHERE lane_id = %s AND chunk_id = ANY(%s)
        """,
        (lane_id, ids),
    )
    out: list[dict[str, Any]] = []
    for chunk_id, rel, model_id, brand_val, oem_val, text, emb in cur.fetchall():
        vec = _parse_pgvector(emb)
        out.append(
            {
                "chunk_id": chunk_id,
                "source_relpath": rel,
                "model_id": model_id,
                "brand": brand_val,
                "oem_model": oem_val,
                "text": text,
                "vector": vec,
            }
        )
    return out
