"""Retail embedding config — fail fast without API key (no mock in production)."""

import pytest

from utils.retail_fru import embeddings as gem


@pytest.mark.no_embed_stub
def test_embed_text_fails_without_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.setenv("EMBEDDING_MODEL", "gemini-embedding-2")
    with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
        gem.embed_text("hello")
