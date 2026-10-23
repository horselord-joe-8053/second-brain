"""P1.3–P1.4 — manual evidence package, verifier, agentic budget."""

from __future__ import annotations

from pathlib import Path

import pytest

from retail_brain.evidence.agentic import AgenticRetrievalController
from retail_brain.evidence.retriever import ManualEvidenceRetriever
from retail_brain.evidence.types import EvidenceChunk, EvidencePackage
from retail_brain.evidence.verifier import verify_manual_coverage
from tests.retail_multi_profiles.lib.lanes import Lane
from tests.retail_multi_profiles.lib.raw_rag_index import build_index_for_lane

pytest.importorskip("lancedb")


def _fake_embed(texts: list[str]) -> list[list[float]]:
    return [[0.9, 0.1, 0.5, 0.25] for _ in texts]


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
        ingest_kind="external_markdown",
        raw_rag_enabled=True,
        raw_glob="raw/sources/fridge-docs_md/**/*.md",
    )


def test_evidence_package_shape(evidence_lane: Lane) -> None:
    """EvidenceRetriever returns JSON-serializable package with chunk ranks."""
    embed_cfg = {"provider": "openai", "model": "test-model"}
    build_index_for_lane(evidence_lane, embed_cfg, embed_fn=_fake_embed)
    retriever = ManualEvidenceRetriever(
        evidence_lane,
        embed_cfg=embed_cfg,
        mode="hybrid_rrf",
        top_k=3,
        embed_fn=_fake_embed,
    )
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
    build_index_for_lane(evidence_lane, embed_cfg, embed_fn=_fake_embed)
    retriever = ManualEvidenceRetriever(
        evidence_lane,
        embed_cfg=embed_cfg,
        mode="vector",
        top_k=2,
        embed_fn=_fake_embed,
    )
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
