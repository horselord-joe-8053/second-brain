"""CLI: retail lane A–D benchmark (smoke or full)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RETAIL_PKG = REPO / "scripts" / "retail"
for p in (str(REPO), str(RETAIL_PKG)):
    if p not in sys.path:
        sys.path.insert(0, p)

from tests.retail_multi_profiles.lib.report_html import write_scoreboard_html  # noqa: E402
from tests.retail_multi_profiles.lib.report_md import write_scoreboard_md  # noqa: E402
from tests.retail_multi_profiles.lib.run_config import load_merged_run_config  # noqa: E402
from tests.retail_multi_profiles.lib.runner import run_full, run_smoke  # noqa: E402
from tests.retail_multi_profiles.lib.sources_only_replay import run_sources_only_replay  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    """Parse CLI and run smoke or full benchmark across lanes."""
    parser = argparse.ArgumentParser(description="Retail ingest lane QA benchmark")
    parser.add_argument("--smoke", action="store_true", help="Run configured smoke question ids")
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run full 90-question suite on each lane (live LLM Wiki + Gemini)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="With --full: run only first N questions (0 = all 90)",
    )
    parser.add_argument("--lanes", default="A,B,C,D", help="Comma-separated lane ids")
    parser.add_argument("--run-id", default="", help="Optional run id subdirectory name")
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Skip rows already present in ops/.../results.jsonl",
    )
    parser.add_argument(
        "--sources-only-replay",
        action="store_true",
        help="Replay mixed-outcome tickets using only wiki/sources hits inside top 10",
    )
    parser.add_argument(
        "--ticket-file",
        default="",
        help="Mixed-outcome JSON for --sources-only-replay",
    )
    args = parser.parse_args(argv)

    if args.sources_only_replay:
        ticket = Path(args.ticket_file) if args.ticket_file else (
            REPO
            / "ops/runs/retail-lane-abcd/abcd-full-openai-v2/b-vs-d-mixed-outcomes.json"
        )
        lane_ids = [x.strip() for x in args.lanes.split(",") if x.strip()]
        if args.lanes == "A,B,C,D":
            lane_ids = ["B", "D"]
        out = run_sources_only_replay(
            REPO,
            ticket_file=ticket,
            lane_ids=lane_ids,
            top_k=10,
            run_id=args.run_id or "abcd-sources-only-topk10",
        )
        print(f"Wrote {out}")
        return 0

    if args.smoke == args.full:
        parser.error("Specify exactly one of --smoke or --full")

    lane_ids = [x.strip() for x in args.lanes.split(",") if x.strip()]
    run_id = args.run_id or None

    if args.smoke:
        cfg = load_merged_run_config(REPO)
        qids = list(cfg.get("smoke_question_ids") or [])
        out_dir = run_smoke(
            REPO, lane_ids=lane_ids, question_ids=qids, run_id=run_id, resume=args.resume
        )
    else:
        out_dir = run_full(
            REPO,
            lane_ids=lane_ids,
            limit=args.limit,
            run_id=run_id,
            resume=args.resume,
        )

    results = out_dir / "results.json"
    md = write_scoreboard_md(results)
    html = write_scoreboard_html(results)
    print(f"Wrote {results}")
    print(f"Wrote {md}")
    print(f"Wrote {html}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
