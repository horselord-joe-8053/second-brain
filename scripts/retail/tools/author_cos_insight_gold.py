"""Author, validate, and freeze W20 evaluation data from original manual PDFs."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tests.retail_multi_profiles.lib.eval_suites import INSIGHT_SUITE_DEFAULT_PATH  # noqa: E402
from tests.retail_multi_profiles.lib.load_cos_insight_suite import (  # noqa: E402
    iter_cos_insight_questions,
    load_cos_insight_suite,
)
from tests.retail_multi_profiles.lib.w20_authoring import (  # noqa: E402
    approve_candidate,
    author_candidate,
    freeze_candidate,
    validate_candidate_suite,
)
from utils.neat_logger.neat_logger_instance import NeatLoggerFactory  # noqa: E402


def _default_pdfs() -> list[Path]:
    """Return the four original refrigerator manual PDFs in stable order."""
    root = REPO / "brain" / "retail" / "archive" / "pdf" / "fridge-docs"
    return [
        root / "ge_GNE27JYMFS" / "user-guide.pdf",
        root / "kitchenaid_KRFF507HPS" / "user-guide.pdf",
        root / "samsung_RF28K9070SG" / "user-guide.pdf",
        root / "samsung_RF28K9070SG" / "repair-guide.pdf",
    ]


def _logger():
    """Create the operator logger for validation-only CLI paths."""
    return NeatLoggerFactory.create(
        "OPS",
        "W20_AUTHOR",
        log_file_name="w20-author-cli.log",
        log_output="both",
    )


def _build_parser() -> argparse.ArgumentParser:
    """Build the authoring CLI without reading environment variables."""
    parser = argparse.ArgumentParser(description="Author and validate W20 v2 evaluation data")
    commands = parser.add_subparsers(dest="command", required=True)

    author = commands.add_parser("author", help="Generate a candidate suite from four original PDFs")
    author.add_argument("--pdf", type=Path, action="append", dest="pdfs", help="PDF path; repeat four times")
    author.add_argument("--model", default="", help="Strong OpenAI author model (or RETAIL_W20_AUTHOR_MODEL)")
    author.add_argument("--output-dir", type=Path, default=None, help="Run artifact directory")
    author.add_argument("--force", action="store_true", help="Replace an existing candidate in output-dir")
    author.add_argument("--resume", action="store_true", help="Reuse saved PDF evidence and rerun synthesis only")
    author.add_argument(
        "--construct",
        default="mixed_v2",
        choices=["mixed_v2", "briefing_v3"],
        help="mixed_v2 keeps 12/4/4; briefing_v3 authors 20 cross-manual briefings",
    )

    validate = commands.add_parser("validate", help="Validate an existing insight suite")
    validate.add_argument("--suite", type=Path, default=REPO / INSIGHT_SUITE_DEFAULT_PATH)
    approve = commands.add_parser("approve", help="Record explicit human approval of all candidate rows")
    approve.add_argument("--candidate", type=Path, required=True, help="Candidate JSON reviewed by the human")
    approve.add_argument("--reviewer", required=True, help="Human reviewer name or stable identifier")
    approve.add_argument("--all", action="store_true", dest="approve_all", help="Approve all 20 rows")
    freeze = commands.add_parser("freeze", help="Freeze a candidate after all 20 rows are human-verified")
    freeze.add_argument("--candidate", type=Path, required=True, help="Reviewed candidate JSON")
    freeze.add_argument("--output", type=Path, required=True, help="Frozen suite JSON path")
    freeze.add_argument("--reviewer", required=True, help="Human reviewer name or stable identifier")
    freeze.add_argument("--force", action="store_true", help="Replace an existing frozen output")
    return parser


def _validate(path: Path) -> int:
    """Validate either a legacy insight fixture or a W20 v2 candidate."""
    data = load_cos_insight_suite(path)
    if data.get("schema_version") == "cos_insight_qa.v2":
        validate_candidate_suite(data)
    rows = list(iter_cos_insight_questions(data))
    _logger().info(f"{path}: {len(rows)} questions, eval_suite_id={data.get('eval_suite_id')}")
    return 0 if len(rows) == 20 else 1


def main(argv: list[str] | None = None) -> int:
    """Dispatch author and validation commands."""
    args = _build_parser().parse_args(argv)
    if args.command == "validate":
        return _validate(args.suite)
    if args.command == "approve":
        approve_candidate(
            args.candidate,
            reviewer=args.reviewer,
            approve_all=bool(args.approve_all),
        )
        return 0
    if args.command == "freeze":
        freeze_candidate(
            args.candidate,
            output_path=args.output,
            reviewer=args.reviewer,
            force=bool(args.force),
        )
        return 0
    model = str(args.model or os.environ.get("RETAIL_W20_AUTHOR_MODEL") or "").strip()
    pdfs = list(args.pdfs or _default_pdfs())
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_dir = args.output_dir or REPO / "ops" / "runs" / "retail-w20-author" / run_id
    author_candidate(
        pdfs,
        output_dir=output_dir,
        model=model,
        force=bool(args.force),
        resume=bool(args.resume),
        construct=str(args.construct),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
