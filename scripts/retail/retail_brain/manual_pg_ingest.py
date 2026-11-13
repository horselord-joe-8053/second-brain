"""Ingest manual raw chunks into Postgres manual_chunks (manifest parity with Lance)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tests.retail_multi_profiles.lib.lanes import Lane  # noqa: E402
from tests.retail_multi_profiles.lib.raw_chunking import chunks_for_source_file  # noqa: E402
from tests.retail_multi_profiles.lib.raw_corpus import iter_raw_source_files  # noqa: E402
from tests.retail_multi_profiles.lib.raw_embed import embed_model_id, embed_texts_batch  # noqa: E402
from tests.retail_multi_profiles.lib.raw_manifest import (  # noqa: E402
    build_manifest,
    manifest_fingerprint,
)
from tests.retail_multi_profiles.lib.raw_policy import RAW_RAG_DIRNAME  # noqa: E402
from tests.retail_multi_profiles.lib.raw_chunking import chunk_policy_version  # noqa: E402

from retail_brain.manual_pg_db import (  # noqa: E402
    apply_manual_chunks_schema,
    delete_manual_chunks_for_lane,
    upsert_manual_chunks,
)


def manual_pg_meta_path(lane: Lane) -> Path:
    """JSON metadata for PG ingest freshness (mirrors Lance index_meta.json)."""
    return lane.project_path / RAW_RAG_DIRNAME / "manual_pg_meta.json"


def read_manual_pg_meta(lane: Lane) -> dict[str, Any] | None:
    """Load manual_pg_meta.json when present."""
    path = manual_pg_meta_path(lane)
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_manual_pg_meta(lane: Lane, meta: dict[str, Any]) -> None:
    """Persist PG ingest metadata after a successful lane build."""
    path = manual_pg_meta_path(lane)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(meta, indent=2), encoding="utf-8")


def pg_index_is_fresh(lane: Lane, *, embed_cfg: dict[str, Any], force: bool = False) -> bool:
    """True when PG meta matches manifest, chunk policy, and embed model."""
    if force:
        return False
    meta = read_manual_pg_meta(lane)
    if not meta:
        return False
    manifest = build_manifest(lane)
    fp = manifest_fingerprint(manifest)
    if meta.get("manifest_fingerprint") != fp:
        return False
    if meta.get("chunk_policy_version") != chunk_policy_version():
        return False
    if meta.get("embed_model_id") != embed_model_id(embed_cfg):
        return False
    return True


def _collect_chunk_rows(
    lane: Lane,
    embed_cfg: dict[str, Any],
    *,
    embed_fn: Any | None = None,
) -> list[dict[str, Any]]:
    """Chunk lane corpus and embed for PG upsert."""
    sources = iter_raw_source_files(lane.project_path, lane.raw_glob)
    all_chunks = []
    for src in sources:
        all_chunks.extend(chunks_for_source_file(src))
    texts = [c.text for c in all_chunks]
    if embed_fn is not None:
        vectors = embed_fn(texts)
    else:
        vectors = embed_texts_batch(texts, embed_cfg)
    from retail_brain.product_scope import product_for_ingest_key

    rows: list[dict[str, Any]] = []
    for chunk, vec in zip(all_chunks, vectors):
        pf = product_for_ingest_key(chunk.model_id)
        rows.append(
            {
                "chunk_id": chunk.chunk_id,
                "lane_id": lane.lane_id,
                "source_relpath": chunk.source_relpath,
                "model_id": chunk.model_id,
                "brand": (pf.brand if pf else "") or "",
                "oem_model": (pf.oem_model if pf else "") or "",
                "chunk_index": chunk.chunk_index,
                "text": chunk.text,
                "content_hash": chunk.content_hash,
                "embedding": vec,
            }
        )
    return rows


def ingest_lane_to_pg(
    dsn: str,
    lane: Lane,
    embed_cfg: dict[str, Any],
    *,
    embed_fn: Any | None = None,
) -> dict[str, Any]:
    """Full lane rebuild: upsert chunks + delete stale ids + write meta."""
    import psycopg2  # type: ignore

    rows = _collect_chunk_rows(lane, embed_cfg, embed_fn=embed_fn)
    keep_ids = {str(r["chunk_id"]) for r in rows}
    conn = psycopg2.connect(dsn)
    try:
        with conn.cursor() as cur:
            apply_manual_chunks_schema(cur)
            delete_manual_chunks_for_lane(cur, lane_id=lane.lane_id, keep_ids=keep_ids)
            upsert_manual_chunks(cur, rows)
        conn.commit()
    finally:
        conn.close()

    manifest = build_manifest(lane)
    meta = {
        "lane_id": lane.lane_id,
        "chunk_policy_version": chunk_policy_version(),
        "embed_model_id": embed_model_id(embed_cfg),
        "manifest_fingerprint": manifest_fingerprint(manifest),
        "chunk_count": len(rows),
    }
    write_manual_pg_meta(lane, meta)
    return meta


def ensure_manual_pg_fresh(
    dsn: str,
    lane: Lane,
    embed_cfg: dict[str, Any],
    *,
    force: bool = False,
    skip_check: bool = False,
    embed_fn: Any | None = None,
) -> dict[str, Any]:
    """Rebuild PG manual index when corpus or config drifted."""
    if skip_check:
        return read_manual_pg_meta(lane) or {}
    if pg_index_is_fresh(lane, embed_cfg=embed_cfg, force=force):
        return read_manual_pg_meta(lane) or {}
    return ingest_lane_to_pg(dsn, lane, embed_cfg, embed_fn=embed_fn)
