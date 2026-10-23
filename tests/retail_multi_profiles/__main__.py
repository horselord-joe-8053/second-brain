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
from tests.retail_multi_profiles.lib.compare_wiki_raw import (  # noqa: E402
    compare_runs,
    write_compare_markdown,
)
from tests.retail_multi_profiles.lib.raw_index_runner import run_index_raw  # noqa: E402
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
        "--retrieval-mode",
        choices=("llm_wiki", "raw_rag"),
        default="llm_wiki",
        help="llm_wiki (default) or raw_rag on raw/sources Lance index",
    )
    parser.add_argument(
        "--raw-retrieval",
        choices=("vector", "hybrid_rrf", "hybrid_rrf_rerank"),
        default="",
        help="Raw arm D3 mode when --retrieval-mode raw_rag (default: run-config retrieval.default_mode)",
    )
    parser.add_argument(
        "--raw-agentic",
        action="store_true",
        help="Enable bounded agentic re-search + verifier on raw_rag rows",
    )
    parser.add_argument(
        "--profile",
        default="",
        help="Named run_profiles id from run-config.yaml (overrides mode/lanes when set)",
    )
    parser.add_argument(
        "--index-raw",
        action="store_true",
        help="Build raw-sources vector index for --lanes (no Q&A)",
    )
    parser.add_argument(
        "--force-reindex",
        action="store_true",
        help="With raw_rag: rebuild Lance index even if manifest matches",
    )
    parser.add_argument(
        "--skip-index-check",
        action="store_true",
        help="With raw_rag: skip auto index freshness (expert; may use stale index)",
    )
    parser.add_argument(
        "--compare-wiki-raw",
        action="store_true",
        help="Write compare_wiki_vs_raw.md from wiki + raw results.json paths",
    )
    parser.add_argument(
        "--wiki-results",
        default="ops/runs/retail-lane-abcd/abcd-full-openai-v2/results.json",
        help="Wiki baseline results.json for --compare-wiki-raw",
    )
    parser.add_argument(
        "--raw-results",
        default="",
        help="Raw RAG results.json for --compare-wiki-raw",
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

    if args.compare_wiki_raw:
        raw_path = Path(args.raw_results) if args.raw_results else None
        if raw_path is None or not raw_path.is_file():
            parser.error("--compare-wiki-raw requires --raw-results pointing to results.json")
        wiki_path = REPO / args.wiki_results
        payload = compare_runs(wiki_path, raw_path)
        out_dir = raw_path.parent
        md = write_compare_markdown(payload, out_dir / "compare_wiki_vs_raw.md")
        print(f"Wrote {md}")
        return 0

    if args.index_raw:
        lane_ids = [x.strip() for x in args.lanes.split(",") if x.strip()]
        if args.lanes == "A,B,C,D":
            lane_ids = ["B", "C", "D"]
        out = run_index_raw(
            REPO,
            lane_ids=lane_ids,
            run_id=args.run_id or None,
            force_reindex=args.force_reindex,
            skip_index_check=args.skip_index_check,
        )
        print(f"Wrote {out}")
        return 0

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

    cfg = load_merged_run_config(REPO)
    lane_ids = [x.strip() for x in args.lanes.split(",") if x.strip()]
    retrieval_mode = args.retrieval_mode
    raw_retrieval = args.raw_retrieval
    raw_agentic = args.raw_agentic
    if args.profile:
        from tests.retail_multi_profiles.lib.run_profiles import resolve_run_profile

        prof = resolve_run_profile(cfg, args.profile)
        retrieval_mode = str(prof.get("retrieval_mode") or retrieval_mode)
        raw_retrieval = str(prof.get("raw_retrieval") or raw_retrieval)
        if prof.get("lanes"):
            lane_ids = [x.strip() for x in str(prof["lanes"]).split(",") if x.strip()]
    if retrieval_mode == "raw_rag" and args.lanes == "A,B,C,D" and not args.profile:
        lane_ids = ["B", "C", "D"]
    run_id = args.run_id or None
    raw_kw = {
        "retrieval_mode": retrieval_mode,
        "raw_retrieval": raw_retrieval,
        "raw_agentic": raw_agentic,
        "force_reindex": args.force_reindex,
        "skip_index_check": args.skip_index_check,
    }

    if args.smoke:
        qids = list(cfg.get("smoke_question_ids") or [])
        out_dir = run_smoke(
            REPO,
            lane_ids=lane_ids,
            question_ids=qids,
            run_id=run_id,
            resume=args.resume,
            **raw_kw,
        )
    else:
        out_dir = run_full(
            REPO,
            lane_ids=lane_ids,
            limit=args.limit,
            run_id=run_id,
            resume=args.resume,
            **raw_kw,
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
