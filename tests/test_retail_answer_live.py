"""Answer-bundle E2E, live tier (brain-profiles P8): Postgres + Gemini + LLM Wiki on ``brain/retail``.

Skipped unless ``RUN_RETAIL_E2E=1``. Needs ``RETAIL_DATABASE_URL`` (FRU 1k loaded), ``GEMINI_API_KEY``,
and — for wiki-sourced hits — LLM Wiki running with the retail project compiled (HG-2) plus
``LLM_WIKI_API_TOKEN``. If the wiki is down the run still completes on raw PDF pages (reported).

Hard: every bundle is contract-valid (both legs ok, provenance on every manual hit). Soft (reported to
``tmp/simulated_data/reports/answer_e2e/answer_e2e_report_<mode>.json``): ticket gold@2, same-issue@2, manual gold, wiki share.

  RUN_RETAIL_E2E=1 scripts/py -m pytest -q tests/test_retail_answer_live.py -s
"""

from __future__ import annotations

import json
import os
from collections import Counter
from pathlib import Path

import pytest

from retail_brain.answer_bundle import build_answer_bundle
from retail_brain.answer_manuals import LlmWikiHttpClient
from retail_brain.answer_tickets import PgTicketSource, load_issue_keys
from retail_brain.pdf_pages import cached_page_index
from test_retail_answer_e2e import GOLD, PROFILE, manual_gold_hit

REPO = Path(__file__).resolve().parents[1]
REPORT_DIR = REPO / "tmp" / "simulated_data" / "reports" / "answer_e2e"

pytestmark = [
    pytest.mark.no_embed_stub,
    pytest.mark.skipif(os.environ.get("RUN_RETAIL_E2E") != "1", reason="live tier: set RUN_RETAIL_E2E=1"),
]


def test_answer_e2e_live(monkeypatch: pytest.MonkeyPatch) -> None:
    """All gold rows through the live stack; contract hard, quality rates reported."""
    from retail_brain.company_profile import cached_company_profile
    from utils.retail_fru.env import load_repo_env

    load_repo_env(REPO)
    if not os.environ.get("RETAIL_FAULT_CODE_PREFIX"):
        monkeypatch.setenv("RETAIL_FAULT_CODE_PREFIX", cached_company_profile().fault_code_prefix)
    dsn = os.environ.get("RETAIL_DATABASE_URL")
    assert dsn, "RETAIL_DATABASE_URL not set"
    source = PgTicketSource(dsn, load_issue_keys(PROFILE / "ticket_manifest.jsonl"))
    wiki = LlmWikiHttpClient(os.environ.get("BRAIN_ROOT") or str(REPO / "brain" / "retail"))
    index = cached_page_index()
    rows = [json.loads(line) for line in GOLD.read_text(encoding="utf-8").splitlines() if line.strip()]

    n, ticket_hit, issue_hit, manual_hit, manual_n = Counter(), Counter(), Counter(), Counter(), Counter()
    wiki_hits = raw_hits = false_prior = 0
    wiki_up = True
    problems, per_row = [], []
    for row in rows:
        b = build_answer_bundle(row["query"], ticket_source=source, page_index=index, wiki=wiki, model=row["model"])
        s, d = row["stratum"], b["diagnostics"]
        n[s] += 1
        wiki_up &= d["wiki_available"]
        if not (d["ticket_leg_ok"] and d["manual_leg_ok"]):
            problems.append(f"{row['eval_id']}: {d['notes']}")
        if any(not h["raw_origin"]["pdf_path"] for h in b["manuals"]["hits"]):
            problems.append(f"{row['eval_id']}: manual hit without pdf_path")
        tids = [h["ticket_id"] for h in b["tickets"]["hits"]]
        t_ok = bool(set(tids) & set(row["expected_ticket_ids"]))
        ticket_hit[s] += t_ok
        # Many near-identical tickets share one issue; a same-issue prior carries the same fix.
        issue_ok = any(h["issue_key"] == row["issue_key"] for h in b["tickets"]["hits"])
        issue_hit[s] += issue_ok
        if s == "no_prior_ticket":
            false_prior += any(h["issue_key"] == row["issue_key"] for h in b["tickets"]["hits"])
        m_ok = None
        if row["expected_manual_pages"]:
            manual_n[s] += 1
            m_ok = manual_gold_hit(b, row)
            manual_hit[s] += m_ok
        wiki_hits += sum(h["source"] == "wiki" for h in b["manuals"]["hits"])
        raw_hits += sum(h["source"] == "raw_pdf" for h in b["manuals"]["hits"])
        per_row.append({"eval_id": row["eval_id"], "stratum": s, "ticket_gold_at_2": t_ok,
                        "issue_match_at_2": issue_ok, "manual_gold": m_ok,
                        "tickets": tids, "manual_sources": [h["source"] for h in b["manuals"]["hits"]],
                        "notes": d["notes"]})

    report = {
        "search_mode": b["tickets"]["search_mode"],
        "wiki_available": wiki_up,
        "rows": len(rows),
        "ticket_gold_at_2": {s: f"{ticket_hit[s]}/{n[s]}" for s in sorted(n) if s != "no_prior_ticket"},
        "issue_match_at_2": {s: f"{issue_hit[s]}/{n[s]}" for s in sorted(n) if s != "no_prior_ticket"},
        "manual_gold": {s: f"{manual_hit[s]}/{manual_n[s]}" for s in sorted(manual_n)},
        "no_prior_false_claims": false_prior,
        "manual_hit_sources": {"wiki": wiki_hits, "raw_pdf": raw_hits},
        "per_row": per_row,
    }
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / f"answer_e2e_report_{report['search_mode']}.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "per_row"}, indent=2, sort_keys=True))
    assert not problems, problems
