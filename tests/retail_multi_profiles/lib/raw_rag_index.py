"""LanceDB index for raw manual chunks under each lane project."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import pyarrow as pa

from .lanes import Lane
from .raw_chunking import RawChunk, chunk_policy_version, chunks_for_source_file
from .raw_corpus import iter_raw_source_files
from .raw_embed import embed_model_id, embed_texts_batch
from .raw_manifest import (
    build_manifest,
    manifest_fingerprint,
    read_manifest,
    write_manifest,
)
from .raw_policy import RAW_LANCE_TABLE, RAW_RAG_DIRNAME

try:
    import lancedb
except ImportError:  # pragma: no cover
    lancedb = None  # type: ignore


def raw_rag_root(project_path: Path) -> Path:
    """Directory for manifest + Lance data."""
    return project_path / RAW_RAG_DIRNAME


def manifest_path(project_path: Path) -> Path:
    """Corpus manifest JSON path."""
    return raw_rag_root(project_path) / "corpus_manifest.json"


def index_meta_path(project_path: Path) -> Path:
    """Index metadata (embed model, chunk policy, manifest fingerprint)."""
    return raw_rag_root(project_path) / "index_meta.json"


def lance_uri(project_path: Path) -> str:
    """LanceDB storage URI for this project."""
    return str(raw_rag_root(project_path) / "lancedb")


def read_index_meta(project_path: Path) -> dict[str, Any] | None:
    """Load index_meta.json if it exists."""
    path = index_meta_path(project_path)
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_index_meta(project_path: Path, meta: dict[str, Any]) -> None:
    """Persist index metadata after a successful build."""
    path = index_meta_path(project_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(meta, indent=2), encoding="utf-8")


def index_is_fresh(
    lane: Lane,
    *,
    embed_cfg: dict[str, Any],
    force: bool = False,
) -> bool:
    """True when existing Lance index matches manifest, policy, and embed model."""
    if force:
        return False
    meta = read_index_meta(lane.project_path)
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
    if lancedb is None:
        return False
    db = lancedb.connect(lance_uri(lane.project_path))
    return RAW_LANCE_TABLE in db.table_names()


def _cosine_distance(a: list[float], b: list[float]) -> float:
    """L2 distance on normalized vectors (for tests without Lance)."""
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 1.0
    cos = dot / (na * nb)
    return 1.0 - cos


def build_index_for_lane(
    lane: Lane,
    embed_cfg: dict[str, Any],
    *,
    embed_fn: Any | None = None,
) -> dict[str, Any]:
    """Chunk all raw files, embed, and write Lance table + manifest."""
    if lancedb is None:
        raise RuntimeError("lancedb is not installed; pip install lancedb")

    sources = iter_raw_source_files(lane.project_path, lane.raw_glob)
    all_chunks: list[RawChunk] = []
    for src in sources:
        all_chunks.extend(chunks_for_source_file(src))

    texts = [c.text for c in all_chunks]
    if embed_fn is not None:
        vectors = embed_fn(texts)
    else:
        vectors = embed_texts_batch(texts, embed_cfg)

    rows: list[dict[str, Any]] = []
    for chunk, vec in zip(all_chunks, vectors):
        rows.append(
            {
                "chunk_id": chunk.chunk_id,
                "source_relpath": chunk.source_relpath,
                "model_id": chunk.model_id,
                "chunk_index": chunk.chunk_index,
                "text": chunk.text,
                "content_hash": chunk.content_hash,
                "vector": vec,
            }
        )

    root = raw_rag_root(lane.project_path)
    root.mkdir(parents=True, exist_ok=True)
    db = lancedb.connect(lance_uri(lane.project_path))
    if RAW_LANCE_TABLE in db.table_names():
        db.drop_table(RAW_LANCE_TABLE)
    if rows:
        db.create_table(RAW_LANCE_TABLE, rows)
    else:
        db.create_table(RAW_LANCE_TABLE, pa.table({"chunk_id": pa.array([], type=pa.string())}))

    manifest = build_manifest(lane)
    write_manifest(manifest_path(lane.project_path), manifest)
    meta = {
        "lane_id": lane.lane_id,
        "chunk_policy_version": chunk_policy_version(),
        "embed_model_id": embed_model_id(embed_cfg),
        "manifest_fingerprint": manifest_fingerprint(manifest),
        "chunk_count": len(rows),
    }
    write_index_meta(lane.project_path, meta)
    return meta


def ensure_index_fresh(
    lane: Lane,
    embed_cfg: dict[str, Any],
    *,
    force: bool = False,
    skip_check: bool = False,
    embed_fn: Any | None = None,
) -> dict[str, Any]:
    """Rebuild index when corpus or config drifted; return index metadata."""
    if skip_check:
        return read_index_meta(lane.project_path) or {}
    if index_is_fresh(lane, embed_cfg=embed_cfg, force=force):
        return read_index_meta(lane.project_path) or {}
    return build_index_for_lane(lane, embed_cfg, embed_fn=embed_fn)


def list_index_chunks(lane: Lane, *, limit: int = 5000) -> list[dict[str, Any]]:
    """Load chunk rows from Lance (for hybrid lexical pool and tests)."""
    if lancedb is None:
        raise RuntimeError("lancedb is not installed")
    db = lancedb.connect(lance_uri(lane.project_path))
    if RAW_LANCE_TABLE not in db.table_names():
        return []
    tbl = db.open_table(RAW_LANCE_TABLE)
    arrow = tbl.to_arrow()
    n = min(int(arrow.num_rows), limit)
    rows = arrow.slice(0, n).to_pylist()
    out: list[dict[str, Any]] = []
    for row in rows:
        out.append(
            {
                "chunk_id": row.get("chunk_id"),
                "source_relpath": row.get("source_relpath"),
                "model_id": row.get("model_id"),
                "text": row.get("text"),
                "vector": list(row.get("vector") or []),
            }
        )
    return out


def vector_search(
    lane: Lane,
    query_vector: list[float],
    *,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """ANN search; returns rows with distance and text."""
    if lancedb is None:
        raise RuntimeError("lancedb is not installed")
    db = lancedb.connect(lance_uri(lane.project_path))
    if RAW_LANCE_TABLE not in db.table_names():
        return []
    tbl = db.open_table(RAW_LANCE_TABLE)
    hits = (
        tbl.search(query_vector)
        .limit(top_k)
        .to_list()
    )
    out: list[dict[str, Any]] = []
    for row in hits:
        dist = row.get("_distance")
        if dist is None:
            dist = _cosine_distance(query_vector, list(row.get("vector") or []))
        out.append(
            {
                "chunk_id": row.get("chunk_id"),
                "source_relpath": row.get("source_relpath"),
                "model_id": row.get("model_id"),
                "text": row.get("text"),
                "distance": float(dist),
                "vector_score": 1.0 / (1.0 + float(dist)),
            }
        )
    return out
