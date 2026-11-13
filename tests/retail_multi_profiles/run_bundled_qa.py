"""CLI entry: judged TYPE_B_B20 / B20-technical-compound bundled benchmark."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tests.retail_multi_profiles.lib.bundled_runner import (  # noqa: E402
    load_default_suite,
    run_bundled_benchmark,
)
from tests.retail_multi_profiles.lib.load_bundled_suite import (  # noqa: E402
    filter_bundled_ids,
    iter_bundled_questions,
)
from tests.retail_multi_profiles.lib.run_config import load_merged_run_config  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    """Parse flags and run smoke or full TYPE_B_B20 suite."""
    parser = argparse.ArgumentParser(description="Bundled manual+ticket Q&A (TYPE_B_B20)")
    parser.add_argument("--smoke", action="store_true", help="Run bundled_smoke_question_ids only")
    parser.add_argument("--full", action="store_true", help="Run all 20 bundled questions")
    parser.add_argument("--run-id", default="", help="Optional run id subdirectory")
    parser.add_argument("--resume", action="store_true", help="Skip rows already in results.jsonl")
    parser.add_argument(
        "--profile",
        default="MANUAL_B_RAW_PG_HYBRID",
        help="Manual leg run_profiles id (default: PG hybrid, rerank off)",
    )
    parser.add_argument(
        "--question-ids",
        default="",
        help="Comma-separated BND-* ids (overrides --smoke/--full selection)",
    )
    args = parser.parse_args(argv)

    if not args.smoke and not args.full and not (args.question_ids or "").strip():
        parser.error("pass --smoke, --full, or --question-ids")

    data = load_default_suite(REPO)
    cfg = load_merged_run_config(REPO)
    if (args.question_ids or "").strip():
        qids = {x.strip() for x in args.question_ids.split(",") if x.strip()}
        questions = filter_bundled_ids(data, qids)
    elif args.smoke:
        smoke_raw = cfg.get("bundled_smoke_question_ids") or ["BND-E01", "BND-H01"]
        if isinstance(smoke_raw, dict):
            smoke_ids = {str(v) for v in smoke_raw.values()}
        else:
            smoke_ids = {str(x) for x in smoke_raw}
        questions = filter_bundled_ids(data, smoke_ids)
    else:
        questions = list(iter_bundled_questions(data))

    if not questions:
        print("No questions selected", file=sys.stderr)
        return 2

    path = run_bundled_benchmark(
        REPO,
        questions=questions,
        run_id=args.run_id or None,
        resume=args.resume,
        manual_profile_id=args.profile,
    )
    print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
