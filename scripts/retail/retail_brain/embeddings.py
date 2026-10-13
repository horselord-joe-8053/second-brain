"""Retail embeddings facade — re-exports ``utils.retail_fru.embeddings`` (Gemini, no mock in prod)."""

from utils.retail_fru.embeddings import (  # noqa: F401
    EMBEDDING_DIMENSION,
    cosine_distance,
    embed_text,
    embedding_model_id,
)

__all__ = ["EMBEDDING_DIMENSION", "cosine_distance", "embed_text", "embedding_model_id"]
