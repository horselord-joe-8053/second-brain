"""Load Fridges R Us US service YAML (models, issues, eval phrasing templates)."""

from __future__ import annotations

import functools
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

_RETAIL_ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_YAML = _RETAIL_ROOT / "config" / "fru_us_service.yaml"


@dataclass(frozen=True)
class FruIssue:
    """One service issue theme from the company profile."""

    key: str
    symptom: str
    resolution: str
    paraphrase: str
    weight: float
    models: tuple[str, ...]
    #: Author-owned phrases a correct manual page must contain (answer-bundle manual gold).
    manual_anchors: tuple[str, ...] = ()


@dataclass(frozen=True)
class CompanyProfile:
    """Parsed ``fru_us_service.yaml`` for synthetic ticket generation."""

    market: str
    fault_code_prefix: str
    models: tuple[dict[str, str], ...]
    issues: tuple[FruIssue, ...]
    detail_slots: tuple[str, ...]
    intake_openings: tuple[str, ...]
    code_phrasings: tuple[str, ...]
    hybrid_bait_pairs: tuple[dict[str, str], ...]
    source_path: Path

    def issues_for_model(self, sku: str) -> list[FruIssue]:
        """Issues allowed for a fridge SKU."""
        return [i for i in self.issues if sku in i.models]

    def docs_folder_for_model(self, sku: str) -> str | None:
        """Manual folder under ``fridge-docs/`` for a ticket ``model`` (e.g. GNE27JYMFS → ge_GNE27JYMFS)."""
        for m in self.models:
            if m.get("sku") == sku or m.get("docs_folder") == sku:
                return m.get("docs_folder")
        return None

    def issue_by_key(self, key: str) -> FruIssue:
        """Lookup issue by stable key (manifest / eval)."""
        for i in self.issues:
            if i.key == key:
                return i
        raise KeyError(key)


def _parse_issue(raw: dict[str, Any]) -> FruIssue:
    return FruIssue(
        key=str(raw["key"]),
        symptom=str(raw["symptom"]),
        resolution=str(raw["resolution"]),
        paraphrase=str(raw["paraphrase"]),
        weight=float(raw.get("weight", 1.0)),
        models=tuple(str(m) for m in raw["models"]),
        manual_anchors=tuple(str(a) for a in raw.get("manual_anchors") or ()),
    )


def load_company_profile(path: Path | None = None) -> CompanyProfile:
    """Load and validate the FRU US service profile YAML."""
    yaml_path = path or _DEFAULT_YAML
    if not yaml_path.is_file():
        raise FileNotFoundError(yaml_path)
    data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    required = ("market", "fault_code_prefix", "models", "issues")
    for k in required:
        if k not in data:
            raise ValueError(f"{yaml_path}: missing key {k!r}")
    issues = tuple(_parse_issue(i) for i in data["issues"])
    if len(issues) < 24:
        raise ValueError(f"{yaml_path}: expected >=24 issues, got {len(issues)}")
    return CompanyProfile(
        market=str(data["market"]),
        fault_code_prefix=str(data["fault_code_prefix"]),
        models=tuple(dict(m) for m in data["models"]),
        issues=issues,
        detail_slots=tuple(str(s) for s in data.get("detail_slots") or ()),
        intake_openings=tuple(str(s) for s in data.get("intake_openings") or ()),
        code_phrasings=tuple(str(s) for s in data.get("code_phrasings") or ()),
        hybrid_bait_pairs=tuple(dict(p) for p in data.get("hybrid_bait_pairs") or ()),
        source_path=yaml_path,
    )


@functools.lru_cache(maxsize=1)
def cached_company_profile() -> CompanyProfile:
    """Process-wide cached profile for generators and tests."""
    return load_company_profile()
