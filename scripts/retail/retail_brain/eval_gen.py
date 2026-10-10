"""Build eval JSONL from manifest with paraphrase queries (anti-leakage)."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Unique case ref lives on stored tickets; exam questions omit it (customer wording).
_CASE_REF_SUFFIX = re.compile(
    r"\s*Case ref ITM-\d+ / T-\d+-\d+\.\s*$",
    re.IGNORECASE,
)

from retail_brain.market import market_profile
from retail_brain.models import RESOLVED
from retail_brain.seed import iter_manifest


def paraphrase_query(manifest_text: str, ticket_id: str, *, market: str | None = None) -> str:
    """Deterministic paraphrase — must differ from manifest customer_query_text."""
    profile = market_profile(market)
    prefix = profile["customer_query_prefix"]
    core = manifest_text.replace(prefix, "").strip()
    core = _CASE_REF_SUFFIX.sub("", core).strip()
    return profile["paraphrase_template"].format(core=core, ref=ticket_id[-6:])


def equivalence_key(model: str, customer_query_text: str) -> Tuple[str, str]:
    """Stable cluster id: same stored complaint text on the same phone model."""
    return (model, customer_query_text.strip())


def build_equivalence_index(manifest_records: List[dict]) -> Dict[Tuple[str, str], List[str]]:
    """Map (model, customer_query_text) → sorted ticket_ids for resolved rows (LLM author hint only)."""
    index: Dict[Tuple[str, str], List[str]] = {}
    for rec in manifest_records:
        if rec.get("status") != RESOLVED:
            continue
        key = equivalence_key(rec["model"], rec["customer_query_text"])
        index.setdefault(key, []).append(rec["ticket_id"])
    for key in index:
        index[key] = sorted(index[key])
    return index


def build_eval_rows(manifest_path: Path, *, max_rows: int = 50) -> List[dict]:
    """CI / default gold: strict single source ticket per row (D6 primary metric)."""
    rows: List[dict] = []
    for i, rec in enumerate(iter_manifest(manifest_path)):
        if rec.get("status") != RESOLVED:
            continue
        if len(rows) >= max_rows:
            break
        tid = rec["ticket_id"]
        original = rec["customer_query_text"]
        query = paraphrase_query(original, tid)
        if query.strip() == original.strip():
            raise ValueError(f"eval leakage: verbatim query for {tid}")
        stratum = "literal_token" if "SM-" in original else "paraphrase"
        rows.append(
            {
                "eval_id": f"eval-{i:04d}",
                "query": query,
                "model_filter": rec["model"],
                "expected_ticket_ids": [tid],
                "stratum": stratum,
                "source_ticket_id": tid,
            }
        )
    return rows


def write_eval_jsonl(path: Path, rows: List[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
