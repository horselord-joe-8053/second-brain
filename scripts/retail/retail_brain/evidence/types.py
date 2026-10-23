"""JSON-shaped evidence packages for manual and ticket policies."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class EvidenceChunk:
    """One retrieved passage with rank metadata."""

    chunk_id: str
    source_relpath: str
    model_id: str
    text: str
    rank: int
    scores: dict[str, float] = field(default_factory=dict)


@dataclass
class EvidencePackage:
    """Normalized retrieval output for verifier + answer pipeline."""

    query: str
    model_id: str
    mode: str
    chunks: list[EvidenceChunk]
    latency_ms: int = 0
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize for JSONL / ops runs."""
        return {
            "query": self.query,
            "model_id": self.model_id,
            "mode": self.mode,
            "latency_ms": self.latency_ms,
            "meta": self.meta,
            "chunks": [
                {
                    **asdict(c),
                }
                for c in self.chunks
            ],
        }
