"""Tests for harness embedding client."""

from __future__ import annotations

from tests.retail_multi_profiles.lib.raw_embed import embed_model_id, embed_texts_batch


def test_embed_model_id_label() -> None:
    """Stable embed model label for index metadata."""
    cfg = {"provider": "openai", "model": "text-embedding-3-small"}
    assert embed_model_id(cfg) == "openai:text-embedding-3-small"


def test_embed_batch_mock(monkeypatch) -> None:
    """Batch length matches input when embed API succeeds."""

    def fake_batch(texts, *, model, timeout_sec=120.0, dimensions=None):
        return [[0.1, 0.2, 0.3] for _ in texts]

    monkeypatch.setattr(
        "tests.retail_multi_profiles.lib.raw_embed.openai_embed_batch",
        fake_batch,
    )
    vecs = embed_texts_batch(["a", "b"], {"provider": "openai", "model": "m"})
    assert len(vecs) == 2
    assert len(vecs[0]) == 3
