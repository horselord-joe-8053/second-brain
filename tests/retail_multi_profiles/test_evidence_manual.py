"""P1.3–P1.4 — manual evidence package, verifier, agentic budget (Postgres D3)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from retail_brain.evidence.agentic import AgenticRetrievalController
from retail_brain.evidence.retriever import ManualEvidenceRetriever
from retail_brain.evidence.types import EvidenceChunk, EvidencePackage
from retail_brain.evidence.verifier import verify_manual_coverage
from retail_brain.manual_pg_ingest import _collect_chunk_rows
from tests.retail_multi_profiles.lib.lanes import Lane


def _fake_embed(texts: list[str]) -> list[list[float]]:
    return [[0.9, 0.1, 0.5, 0.25] * 384 for _ in texts]


@pytest.fixture
def evidence_lane(tmp_path: Path) -> Lane:
    raw_dir = tmp_path / "raw" / "sources" / "fridge-docs_md" / "samsung_RF28K9070SG"
    raw_dir.mkdir(parents=True)
    (raw_dir / "guide.md").write_text(
        "Ice maker reset and water filter replacement steps.\n" * 30,
        encoding="utf-8",
    )
    return Lane(
        lane_id="T",
        project_path=tmp_path,
        brain_relpath="brain/retail-md",
        ingest_kind="external_markdown",
        raw_rag_enabled=True,
        raw_glob="raw/sources/fridge-docs_md/**/*.md",
    )


def _pg_pool(lane: Lane, embed_cfg: dict) -> list[dict]:
    rows = _collect_chunk_rows(lane, embed_cfg, embed_fn=_fake_embed)
    return [
        {
            "chunk_id": r["chunk_id"],
            "source_relpath": r["source_relpath"],
            "model_id": r["model_id"],
            "brand": "Samsung",
            "oem_model": "RF28K9070SG",
            "text": r["text"],
            "vector": r["embedding"],
        }
        for r in rows
    ]


class _FakePgConn:
    def cursor(self):
        return self

    def __enter__(self):
        return self

    def __exit__(self, *_a) -> None:
        return None

    def close(self) -> None:
        return None


def test_evidence_package_shape(evidence_lane: Lane, monkeypatch: pytest.MonkeyPatch) -> None:
    """EvidenceRetriever returns JSON-serializable package with chunk ranks."""
    monkeypatch.setenv("RETAIL_MANUAL_LEXICAL_BACKEND", "overlap")
    embed_cfg = {"provider": "openai", "model": "test-model"}
    pool = _pg_pool(evidence_lane, embed_cfg)
    retriever = ManualEvidenceRetriever(
        evidence_lane,
        embed_cfg=embed_cfg,
        mode="hybrid_rrf",
        top_k=3,
        embed_fn=_fake_embed,
        pg_dsn="postgresql://fake",
    )
    with patch("retail_brain.manual_pg_search.ensure_manual_pg_fresh", return_value={}):
        with patch("retail_brain.manual_pg_search.list_manual_chunks", return_value=pool):
            with patch("psycopg2.connect", return_value=_FakePgConn()):
                pkg = retriever.retrieve(
                    "samsung_RF28K9070SG ice maker reset",
                    model_id="samsung_RF28K9070SG",
                    skip_index_check=True,
                )
    data = pkg.to_dict()
    assert data["mode"] == "hybrid_rrf"
    assert data["chunks"]
    assert data["chunks"][0]["rank"] == 1


def test_agentic_at_most_one_subquery(evidence_lane: Lane, monkeypatch: pytest.MonkeyPatch) -> None:
    """Second loop must not run when max_loops=1 and first pass already sufficient."""
    embed_cfg = {"provider": "openai", "model": "test-model"}
    pool = _pg_pool(evidence_lane, embed_cfg)

    def _fake_knn(_cur, *, lane_id, query_vector, limit, brand=None, oem_model=None):
        return [
            {
                "chunk_id": r["chunk_id"],
                "source_relpath": r["source_relpath"],
                "model_id": r["model_id"],
                "brand": r.get("brand"),
                "oem_model": r.get("oem_model"),
                "text": r["text"],
                "distance": 0.1,
                "vector_score": 0.9,
            }
            for r in pool[:limit]
        ]

    monkeypatch.setattr("retail_brain.manual_pg_search.knn_manual_chunks", _fake_knn)
    retriever = ManualEvidenceRetriever(
        evidence_lane,
        embed_cfg=embed_cfg,
        mode="vector",
        top_k=2,
        embed_fn=_fake_embed,
        pg_dsn="postgresql://fake",
    )
    with patch("retail_brain.manual_pg_search.ensure_manual_pg_fresh", return_value={}):
        with patch("retail_brain.manual_pg_search.list_manual_chunks", return_value=pool):
            with patch("psycopg2.connect", return_value=_FakePgConn()):
                calls: list[str] = []
                orig = retriever.retrieve

                def counted(*args, **kwargs):
                    calls.append(str(kwargs.get("query") or args[0]))
                    return orig(*args, **kwargs)

                monkeypatch.setattr(retriever, "retrieve", counted)
                ctrl = AgenticRetrievalController(retriever, max_loops=1)
                result = ctrl.retrieve_with_verifier(
                    "samsung_RF28K9070SG ice maker",
                    "How do I reset the ice maker?",
                    model_id="samsung_RF28K9070SG",
                    skip_index_check=True,
                )
    assert result.loops <= 1
    assert len(calls) <= 2


def test_verifier_flags_missing_terms() -> None:
    """Hard-tier style question with no overlapping chunk text fails coverage."""
    pkg = EvidencePackage(
        query="q",
        model_id="samsung_RF28K9070SG",
        mode="vector",
        chunks=[
            EvidenceChunk(
                chunk_id="1",
                source_relpath="x.md",
                model_id="samsung_RF28K9070SG",
                text="unrelated warranty paragraph",
                rank=1,
            )
        ],
    )
    verdict = verify_manual_coverage(pkg, "Explain defrost thermostat calibration procedure")
    assert verdict.sufficient is False
    assert verdict.missing_terms
