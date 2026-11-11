"""CLI: TYPE_C_C20 insight QA — wiki vs bundled arms."""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RETAIL_PKG = REPO / "scripts" / "retail"
for p in (str(REPO), str(RETAIL_PKG)):
    if p not in sys.path:
        sys.path.insert(0, p)

from tests.retail_multi_profiles.lib.cos_insight_runner import run_cos_insight_benchmark  # noqa: E402
from tests.retail_multi_profiles.lib.eval_suites import INSIGHT_SUITE_DEFAULT_PATH  # noqa: E402
from tests.retail_multi_profiles.lib.load_cos_insight_suite import (  # noqa: E402
    CosInsightQuestion,
    iter_cos_insight_questions,
    load_cos_insight_suite,
)
from tests.retail_multi_profiles.lib.run_config import load_merged_run_config  # noqa: E402


def select_smoke_rows(
    rows: list[CosInsightQuestion],
    configured_ids: list[str],
) -> list[CosInsightQuestion]:
    """Select configured smoke ids or one global plus one boundary v2 fallback."""
    wanted = set(configured_ids)
    selected = [row for row in rows if row.question_id in wanted]
    if selected or not any(row.question_class for row in rows):
        return selected
    global_row = next((row for row in rows if row.question_class.startswith("global_")), None)
    boundary_row = next((row for row in rows if row.question_class == "boundary_local"), None)
    return [row for row in (global_row, boundary_row) if row is not None]


def main(argv: list[str] | None = None) -> int:
    """Parse flags and run smoke or full TYPE_C_C20 benchmark."""
    parser = argparse.ArgumentParser(description="COS insight Q&A (TYPE_C_C20)")
    parser.add_argument("--smoke", action="store_true", help="Run cos_insight_smoke_question_ids from run-config")
    parser.add_argument("--full", action="store_true", help="Run all 20 insight questions")
    parser.add_argument("--arm", default="both", help="wiki | bundled | both")
    parser.add_argument("--run-id", default="", help="Ops run id subdirectory")
    parser.add_argument("--suite", type=Path, default=None, help="Suite JSON (default TYPE_C_C20)")
    parser.add_argument("--resume", action="store_true", help="Keep completed question-arm rows and run only the rest")
    args = parser.parse_args(argv)
    if args.smoke == args.full:
        parser.error("Specify exactly one of --smoke or --full")
    suite_path = args.suite if args.suite is not None else REPO / INSIGHT_SUITE_DEFAULT_PATH
    # Legacy suites remain runnable for historical reproduction; v2 must pass the human freeze gate.
    data = load_cos_insight_suite(suite_path, require_frozen=True)
    author_provider = ""
    if data.get("schema_version") == "cos_insight_qa.v2":
        authoring_run = data.get("authoring_run")
        if not isinstance(authoring_run, dict) or not str(authoring_run.get("provider") or "").strip():
            parser.error("frozen W20 v2 suite is missing authoring_run.provider")
        author_provider = str(authoring_run["provider"])
    suite_sha256 = hashlib.sha256(suite_path.read_bytes()).hexdigest()
    rows = list(iter_cos_insight_questions(data))
    cfg = load_merged_run_config(REPO)
    if args.smoke:
        rows = select_smoke_rows(rows, list(cfg.get("cos_insight_smoke_question_ids") or []))
    if not rows:
        parser.error("no questions selected")
    arms: tuple[str, ...]
    if args.arm == "both":
        arms = ("wiki", "bundled")
    else:
        arms = (args.arm.strip().lower(),)
    run_id = args.run_id or ("c20-smoke" if args.smoke else "c20-full")
    out = run_cos_insight_benchmark(
        REPO,
        rows,
        run_id=run_id,
        arms=arms,
        author_provider=author_provider,
        suite_sha256=suite_sha256,
        resume=bool(args.resume),
    )
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
