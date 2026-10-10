"""Pytest fixtures shared across Second Brain tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
RETAIL_PKG = REPO / "scripts" / "retail"
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
if str(RETAIL_PKG) not in sys.path:
    sys.path.insert(0, str(RETAIL_PKG))

from retail_brain.eval_gen import build_eval_rows, write_eval_jsonl  # noqa: E402
from retail_brain.seed import generate_tickets, write_manifest, write_service_csv  # noqa: E402


@pytest.fixture(autouse=True)
def _retail_test_embed_stub(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> None:
    """Pytest-only deterministic vectors — production code always calls Gemini (no mock fallback)."""
    if request.node.get_closest_marker("no_embed_stub"):
        return
    import hashlib
    import math

    from utils.retail_fru import embeddings as gem

    def fake_embed(text: str, *, task_type: str = "RETRIEVAL_DOCUMENT") -> list[float]:
        digest = hashlib.sha256((text or "").encode("utf-8")).digest()
        vals = [(digest[i % len(digest)] / 127.5 - 1.0) for i in range(gem.EMBEDDING_DIMENSION)]
        norm = math.sqrt(sum(v * v for v in vals)) or 1.0
        return [v / norm for v in vals]

    for target in (
        "utils.retail_fru.embeddings.embed_text",
        "retail_brain.embeddings.embed_text",
        "retail_brain.hybrid_search.embed_text",
        "retail_brain.pg_search.embed_text",
    ):
        monkeypatch.setattr(target, fake_embed)


@pytest.fixture
def retail_seed_dir(tmp_path: Path) -> Path:
    rows = generate_tickets(count=40, seed=99)
    write_service_csv(tmp_path / "service_queries.csv", rows)
    write_manifest(tmp_path / "ticket_manifest.jsonl", rows, seed=99)
    eval_rows = build_eval_rows(tmp_path / "ticket_manifest.jsonl", max_rows=15)
    write_eval_jsonl(tmp_path / "ticket_retrieval.jsonl", eval_rows)
    return tmp_path
