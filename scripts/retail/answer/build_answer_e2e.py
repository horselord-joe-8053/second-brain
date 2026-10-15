#!/usr/bin/env python3.12
"""Build ``answer_e2e.jsonl`` — gold rows for the answer-bundle E2E tests (CI + live tiers).

Rows come from the FRU ticket-retrieval eval (first ``--per-stratum`` rows of each stratum, by
eval_id) plus "no prior ticket" rows: an issue asked about on a model that has no tickets for it.

Manual gold is derived, not guessed: pages of the model's manuals (canonical PDFs only) whose text
contains one of the issue's author-owned ``manual_anchors`` (``fru_us_service.yaml``). An empty
``expected_manual_pages`` means the manual has nothing on the topic (e.g. Wi-Fi on a non-smart fridge).

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
from retail_brain.pdf_pages import DEFAULT_INDEX_PATH, PdfPageIndex, load_page_index  # noqa: E402

PROFILE_DIR = ROOT / "scripts" / "retail" / "sim_data" / "profiles" / "fru_us_1000_100"
DEFAULT_OUT = PROFILE_DIR / "answer_e2e.jsonl"
STRATA = ("paraphrase", "hybrid_stress", "code_in_query")
# (issue_key, model) pairs outside the issue's ticket models — the bundle must not claim a prior fix.
NO_PRIOR = (
    ("filter_alert_stuck", "GNE27JYMFS"),
    ("water_dispenser_slow", "KRFF507HPS"),
    ("interior_light_out", "KRFF507HPS"),
    ("eco_mode_confusion", "GNE27JYMFS"),
    ("freezer_frost_wall", "GNE27JYMFS"),
)


def anchor_pages(issue: FruIssue, docs_folder: str, index: PdfPageIndex) -> List[Dict[str, object]]:
    """``[{"pdf_path", "pages"}]`` of canonical PDFs whose pages contain any anchor phrase."""
    pats = [re.compile(rf"\b{re.escape(a)}\b", re.IGNORECASE) for a in issue.manual_anchors]
    by_pdf: Dict[str, List[int]] = {}
    for r in index.rows:
        if r.sku != docs_folder or r.pdf_path in index.duplicate_paths:
            continue
        if any(p.search(r.text) for p in pats):
            by_pdf.setdefault(r.pdf_path, []).append(r.page)
    return [{"pdf_path": p, "pages": sorted(pg)} for p, pg in sorted(by_pdf.items())]


def described_issue(query: str, profile: CompanyProfile, fallback: FruIssue) -> FruIssue:
    """Issue whose symptom/paraphrase text appears last in the query (what a technician would look up).

    ``hybrid_stress`` rows put a decoy symptom first and the open problem last; ``code_in_query`` rows
    describe a decoy symptom while the fault code points at another ticket — manuals carry no FRU codes,
    so manual gold follows the described symptom, ticket gold follows the source ticket.
    """
    q = query.lower()
    best, best_pos = fallback, -1
    for issue in profile.issues:
        for phrase in (issue.symptom, issue.paraphrase):
            pos = q.rfind(phrase.lower())
            if pos > best_pos:
                best, best_pos = issue, pos
    return best


def build_rows(profile: CompanyProfile, index: PdfPageIndex, per_stratum: int) -> List[Dict[str, object]]:
    """Deterministic gold rows (sorted by eval_id within each block)."""
    manifest = {}
    with (PROFILE_DIR / "ticket_manifest.jsonl").open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                d = json.loads(line)
                manifest[d["ticket_id"]] = d
    evals = [json.loads(l) for l in (PROFILE_DIR / "ticket_retrieval.jsonl").read_text(encoding="utf-8").splitlines()
             if l.strip()]
    rows: List[Dict[str, object]] = []
    for stratum in STRATA:
        picked = sorted((e for e in evals if e["stratum"] == stratum), key=lambda e: e["eval_id"])[:per_stratum]
        for e in picked:
            issue = profile.issue_by_key(manifest[e["source_ticket_id"]]["issue_key"])
            manual_issue = described_issue(e["query"], profile, issue)
            folder = profile.docs_folder_for_model(e["model_filter"])
            rows.append({
                "eval_id": e["eval_id"], "stratum": stratum, "query": e["query"], "model": e["model_filter"],
                "model_sku": folder, "issue_key": issue.key, "manual_issue_key": manual_issue.key,
                "expected_ticket_ids": list(e["expected_ticket_ids"]),
                "expected_manual_pages": anchor_pages(manual_issue, folder, index),
            })
    for n, (key, model) in enumerate(NO_PRIOR, start=1):
        issue = profile.issue_by_key(key)
        assert model not in issue.models, (key, model)
        folder = profile.docs_folder_for_model(model)
        rows.append({
            "eval_id": f"noprior-{n:02d}", "stratum": "no_prior_ticket",
            "query": f"Customer with {model}: {issue.paraphrase}.", "model": model, "model_sku": folder,
            "issue_key": key, "manual_issue_key": key, "expected_ticket_ids": [], "expected_manual_pages": anchor_pages(issue, folder, index),
        })
    return rows


def main(argv: List[str] | None = None) -> int:
    """CLI entry: write the gold JSONL (sorted keys, one row per line)."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--per-stratum", type=int, default=9)
    ap.add_argument("--page-index", type=Path, default=DEFAULT_INDEX_PATH)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args(argv)
    rows = build_rows(load_company_profile(), load_page_index(args.page_index), args.per_stratum)
    with args.out.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n")
    print(f"build_answer_e2e: wrote {len(rows)} rows → {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
