"""Retail embeddings — delegates to utils.retail_fru (Gemini only)."""

from utils.retail_fru.embeddings import (  # noqa: F401
    EMBEDDING_DIMENSION,
    cosine_distance,
    embed_text,
    embedding_model_id,
)

__all__ = ["EMBEDDING_DIMENSION", "cosine_distance", "embed_text", "embedding_model_id"]
