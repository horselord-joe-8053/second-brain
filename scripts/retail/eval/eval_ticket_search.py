#!/usr/bin/env python3
"""Run ticket retrieval eval; set RETAIL_TICKET_HYBRID_SEARCH for V1 vs V1.1."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "retail"))

import os

from utils.retail_fru.env import load_repo_env  # noqa: E402

load_repo_env(ROOT)

from retail_brain.eval_harness import load_eval_cases, run_eval, write_report  # noqa: E402
from retail_brain.pg_search import run_eval_pg  # noqa: E402
from retail_brain.sim_data_profile import resolve_sim_data_profile  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--postgres",
        action="store_true",
        help="Run eval against RETAIL_DATABASE_URL instead of CSV",
    )
    p.add_argument(
        "--tickets",
        type=Path,
        default=None,
        help="CSV corpus (default: active RETAIL_SIM_DATA_PROFILE)",
    )
    p.add_argument(
        "--eval",
        type=Path,
        default=None,
        help="Eval JSONL (default: active RETAIL_SIM_DATA_PROFILE)",
    )
    p.add_argument(
        "--report",
        type=Path,
        default=Path(__file__).resolve().parent / "reports" / "latest.json",
    )
    p.add_argument(
        "--sim-data-profile",
        help="Override RETAIL_SIM_DATA_PROFILE for default CSV/eval paths",
    )
    args = p.parse_args()
    if args.sim_data_profile:
        os.environ["RETAIL_SIM_DATA_PROFILE"] = args.sim_data_profile
    prof = resolve_sim_data_profile()
    tickets_csv = args.tickets or prof.service_queries_csv
    eval_jsonl = args.eval or prof.eval_jsonl
    if args.postgres:
        dsn = os.environ.get("RETAIL_DATABASE_URL")
        if not dsn:
            raise SystemExit("RETAIL_DATABASE_URL required with --postgres")
        cases = load_eval_cases(eval_jsonl)
        report = run_eval_pg(dsn, cases)
    else:
        report = run_eval(tickets_csv=tickets_csv, eval_jsonl=eval_jsonl)
    report.update(prof.as_report_fields())
    write_report(args.report, report)
    extra = ""
    if "acceptable_recall_at_1" in report:
        extra = f" acceptable_recall@1={report['acceptable_recall_at_1']:.3f}"
    lex = ""
    if report.get("lexical_leg_nonempty") is not None:
        lex = f" lexical_nonempty={report['lexical_leg_nonempty']}/{report['total']}"
    print(
        f"sim_data_profile={report['sim_data_profile']} mode={report['mode']} "
        f"recall@1={report['recall_at_1']:.3f}{extra}{lex} -> {args.report}"
    )


if __name__ == "__main__":
    main()
