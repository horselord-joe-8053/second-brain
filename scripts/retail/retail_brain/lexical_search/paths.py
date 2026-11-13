"""On-disk paths for embedded keyword indexes (Tantivy, bm25x).

Each backend gets ``<root>/<name>/`` where ``root`` is ``RETAIL_LEXICAL_INDEX_PATH`` or
``tmp/retail_lexical`` at repo root. Not the Postgres ticket store.
"""

from __future__ import annotations

import os
from pathlib import Path

# retail_brain/lexical_search/paths.py → parents[4] = repo root
_REPO = Path(__file__).resolve().parents[4]


def backend_index_dir(name: str) -> Path:
    """Per-backend subdirectory so switching ``RETAIL_LEXICAL_BACKEND`` does not clobber another index."""
    raw = os.environ.get("RETAIL_LEXICAL_INDEX_PATH", "").strip()
    root = Path(raw) if raw else _REPO / "tmp" / "retail_lexical"
    return root / name
