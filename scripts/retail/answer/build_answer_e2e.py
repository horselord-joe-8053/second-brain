#!/usr/bin/env python3.12
"""Build ``answer_e2e.jsonl`` — gold rows for the answer-bundle E2E tests (CI + live tiers).

Manual gold: ``.txt`` doc paths whose full text contains an author-owned ``manual_anchors`` phrase
(``fru_us_service.yaml``). Empty ``expected_manual_docs`` means the manual has nothing on the topic.

Usage:
  scripts/py scripts/retail/answer/build_answer_e2e.py [--per-stratum 9] [--out …]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts" / "retail"))

from retail_brain.company_profile import CompanyProfile, FruIssue, load_company_profile  # noqa: E402
from retail_brain.txt_docs import TxtDocIndex, load_txt_docs  # noqa: E402

PROFILE_DIR = ROOT / "scripts" / "retail" / "sim_data" / "profiles" / "fru_us_1000_100"
DEFAULT_OUT = PROFILE_DIR / "answer_e2e.jsonl"
DEFAULT_BRAIN = ROOT / "brain" / "retail"
STRATA = ("paraphrase", "hybrid_stress", "code_in_query")
NO_PRIOR = (
    ("filter_alert_stuck", "GNE27JYMFS"),
    ("water_dispenser_slow", "KRFF507HPS"),
    ("interior_light_out", "KRFF507HPS"),
    ("eco_mode_confusion", "GNE27JYMFS"),
    ("freezer_frost_wall", "GNE27JYMFS"),
)


def anchor_docs(issue: FruIssue, docs_folder: str, index: TxtDocIndex) -> List[Dict[str, str]]:
    """``[{"doc_path"}]`` for ``.txt`` files whose text contains any anchor phrase."""
    pats = [re.compile(re.escape(a), re.IGNORECASE) for a in issue.manual_anchors]
    out: List[Dict[str, str]] = []
    seen: set[str] = set()
    for row in index.rows:
        if row.sku != docs_folder or row.doc_path in seen:
            continue
        if any(p.search(row.text) for p in pats):
            seen.add(row.doc_path)
            out.append({"doc_path": row.doc_path})
    return sorted(out, key=lambda d: d["doc_path"])


def described_issue(query: str, profile: CompanyProfile, fallback: FruIssue) -> FruIssue:
    """Issue whose symptom/paraphrase text appears last in the query."""
    q = query.lower()
    best, best_pos = fallback, -1
    for issue in profile.issues:
        for phrase in (issue.symptom, issue.paraphrase):
            pos = q.rfind(phrase.lower())
            if pos > best_pos:
                best, best_pos = issue, pos
    return best


def build_rows(profile: CompanyProfile, index: TxtDocIndex, per_stratum: int) -> List[Dict[str, object]]:
    """Deterministic gold rows (sorted by eval_id within each block)."""
    manifest = {}
    with (PROFILE_DIR / "ticket_manifest.jsonl").open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                d = json.loads(line)
                manifest[d["ticket_id"]] = d
    evals = [
        json.loads(l)
        for l in (PROFILE_DIR / "ticket_retrieval.jsonl").read_text(encoding="utf-8").splitlines()
        if l.strip()
    ]
    rows: List[Dict[str, object]] = []
    for stratum in STRATA:
        picked = sorted((e for e in evals if e["stratum"] == stratum), key=lambda e: e["eval_id"])[:per_stratum]
        for e in picked:
            issue = profile.issue_by_key(manifest[e["source_ticket_id"]]["issue_key"])
            manual_issue = described_issue(e["query"], profile, issue)
            folder = profile.docs_folder_for_model(e["model_filter"])
            rows.append(
                {
                    "eval_id": e["eval_id"],
                    "stratum": stratum,
                    "query": e["query"],
                    "model": e["model_filter"],
                    "model_sku": folder,
                    "issue_key": issue.key,
                    "manual_issue_key": manual_issue.key,
                    "expected_ticket_ids": list(e["expected_ticket_ids"]),
                    "expected_manual_docs": anchor_docs(manual_issue, folder, index),
                }
            )
    for n, (key, model) in enumerate(NO_PRIOR, start=1):
        issue = profile.issue_by_key(key)
        assert model not in issue.models, (key, model)
        folder = profile.docs_folder_for_model(model)
        rows.append(
            {
                "eval_id": f"noprior-{n:02d}",
                "stratum": "no_prior_ticket",
                "query": f"Customer with {model}: {issue.paraphrase}.",
                "model": model,
                "model_sku": folder,
                "issue_key": key,
                "manual_issue_key": key,
                "expected_ticket_ids": [],
                "expected_manual_docs": anchor_docs(issue, folder, index),
            }
        )
    return rows


def main(argv: List[str] | None = None) -> int:
    """CLI entry: write the gold JSONL (sorted keys, one row per line)."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--per-stratum", type=int, default=9)
    ap.add_argument("--brain-root", type=Path, default=DEFAULT_BRAIN)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args(argv)
    rows = build_rows(load_company_profile(), load_txt_docs(args.brain_root), args.per_stratum)
    with args.out.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n")
    print(f"build_answer_e2e: wrote {len(rows)} rows → {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
