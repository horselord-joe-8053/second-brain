"""Map cited wiki paths to audit-registry uncertainty labels for answer prompts."""

from __future__ import annotations

import json
from pathlib import Path

DEFAULT_LABEL = "[audit: contradicted claims on cited wiki pages]"


def _page_keys(path: str) -> set[str]:
    """Normalize wiki API paths for registry lookup."""
    p = (path or "").replace("\\", "/").lstrip("/")
    keys = {p}
    if p.startswith("wiki/"):
        keys.add(p)
    else:
        keys.add(f"wiki/{p}")
    return keys


def contradicted_pages(registry_path: Path) -> set[str]:
    """Pages with at least one contradicted claim row."""
    bad: set[str] = set()
    if not registry_path.is_file():
        return bad
    with registry_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if str(row.get("status") or "") != "contradicted":
                continue
            page = str(row.get("page_relpath") or "")
            if page:
                bad.add(page.replace("\\", "/"))
    return bad


def uncertainty_label_for_hits(
    hit_paths: list[str],
    *,
    registry_path: Path,
    enabled: bool = True,
    label: str = DEFAULT_LABEL,
) -> str | None:
    """Return label when any cited path has contradicted claims in the registry."""
    if not enabled:
        return None
    bad = contradicted_pages(registry_path)
    if not bad:
        return None
    for raw in hit_paths:
        for key in _page_keys(raw):
            if key in bad:
                return label
    return None
