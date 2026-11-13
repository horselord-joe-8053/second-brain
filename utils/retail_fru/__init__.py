"""Shared retail ticket search helpers (FRU-style sidecar, real embeddings only)."""

from utils.retail_fru.embeddings import EMBEDDING_DIMENSION, cosine_distance, embed_text, embedding_model_id

__all__ = [
    "EMBEDDING_DIMENSION",
    "cosine_distance",
    "embed_text",
    "embedding_model_id",
]
