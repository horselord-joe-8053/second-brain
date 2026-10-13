"""CSV + JSONL retrieval eval (offline rows). For Postgres-backed eval use ``pg_search.run_eval_pg``."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence

from retail_brain.eval_scoring import aggregate_recall, score_top1
from retail_brain.hybrid_search import search_ticket_ids
from retail_brain.search_mode import resolve_ticket_search_mode
from retail_brain.ticket_store import load_ticket_rows


@dataclass
class EvalCaseResult:
    """Per-case strict/acceptable hit flags from one retrieval run."""

    eval_id: str
    stratum: str
    hit: bool
    top_ticket_id: str | None
    hit_strict: bool
    hit_acceptable: bool | None = None


def load_eval_cases(path: Path) -> List[dict]:
    """Load ticket retrieval eval JSONL into a list of case dicts."""
    cases: List[dict] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                cases.append(json.loads(line))
    return cases


def run_eval(
    *,
    tickets_csv: Path,
    eval_jsonl: Path,
    top_k: int = 5,
) -> Dict[str, Any]:
    """Score recall@1 offline over CSV tickets and JSONL eval cases."""
    rows = load_ticket_rows(tickets_csv)
    cases = load_eval_cases(eval_jsonl)
    mode = resolve_ticket_search_mode()
    results: List[EvalCaseResult] = []
    for case in cases:
        if case.get("stratum") == "sql_routed":
            continue
        model_filter = case.get("model_filter")
        ranked = search_ticket_ids(
            case["query"],
            rows,
            model_filter=model_filter,
            limit=top_k,
        )
        top = ranked[0] if ranked else None
        hit_strict, hit_acceptable = score_top1(case, top)
        results.append(
            EvalCaseResult(
                eval_id=case["eval_id"],
                stratum=case["stratum"],
                hit=hit_strict,
                top_ticket_id=top,
                hit_strict=hit_strict,
                hit_acceptable=hit_acceptable,
            )
        )
    case_dicts = [r.__dict__ for r in results]
    by_stratum: Dict[str, List[bool]] = {}
    for r in results:
        by_stratum.setdefault(r.stratum, []).append(r.hit_strict)
    summary = {
        "mode": mode,
        "search_mode": mode,
        "hybrid_flag": os.environ.get("RETAIL_TICKET_HYBRID_SEARCH", "0"),
        **aggregate_recall(case_dicts),
        "by_stratum": {
            k: sum(1 for b in v if b) / len(v) if v else 0.0 for k, v in by_stratum.items()
        },
        "cases": case_dicts,
    }
    return summary


def write_report(path: Path, report: Dict[str, Any]) -> None:
    """Write eval summary JSON for A/B reports."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
