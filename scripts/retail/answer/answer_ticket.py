#!/usr/bin/env python3.12
"""Answer a new FRU service ticket with evidence: ``retail_answer.v1`` JSON (default) or Markdown.

Ticket leg: CSV corpus (``--tickets-csv``, default = active ``RETAIL_SIM_DATA_PROFILE``) or Postgres
(``--postgres``, needs ``RETAIL_DATABASE_URL``). Embeddings are always real Gemini calls.
Manual leg: LLM Wiki HTTP API on the retail profile (skip with ``--no-wiki``) + SKU-scoped ``.txt`` search
under ``raw/sources/fridge-docs/`` when wiki misses.

Examples:
  scripts/py scripts/retail/answer/answer_ticket.py --query "RF28K9070SG ice maker not making ice" --md
  scripts/py scripts/retail/answer/answer_ticket.py --query "…" --postgres --json
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import List, Optional

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "retail"))

from retail_brain.answer_bundle import build_answer_bundle, bundle_to_json  # noqa: E402
from retail_brain.answer_manuals import LlmWikiHttpClient  # noqa: E402
from retail_brain.answer_render import render_markdown  # noqa: E402
from retail_brain.answer_tickets import (  # noqa: E402
    EmptyTicketSource,
    InMemoryTicketSource,
    PgTicketSource,
    load_issue_keys,
)
from retail_brain.company_profile import cached_company_profile  # noqa: E402
from retail_brain.txt_docs import load_txt_docs  # noqa: E402
from retail_brain.sim_data_profile import resolve_sim_data_profile  # noqa: E402
from retail_brain.ticket_store import load_ticket_rows  # noqa: E402


def _parser() -> argparse.ArgumentParser:
    """CLI flags."""
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--query", required=True, help="New ticket text")
    p.add_argument("--model", default=None, help="Fridge SKU (e.g. RF28K9070SG); default: detected from query")
    src = p.add_mutually_exclusive_group()
    src.add_argument("--tickets-csv", type=Path, default=None, help="service_queries.csv corpus")
    src.add_argument("--postgres", action="store_true", help="Search Postgres via RETAIL_DATABASE_URL")
    p.add_argument("--manifest", type=Path, default=None, help="ticket_manifest.jsonl for issue_key")
    p.add_argument("--brain-root", type=Path, default=None, help="Retail brain root (default: brain/retail)")
    p.add_argument("--skip-tickets", action="store_true", help="Skip ticket leg (no CSV/PG search or ticket embeds)")
    p.add_argument("--skip-manual", action="store_true", help="Skip manual leg (no wiki or .txt search)")
    p.add_argument("--no-wiki", action="store_true", help="Skip LLM Wiki; manual leg uses raw .txt search only")
    p.add_argument("--wiki-project", default=None, help="LLM Wiki project id or path (default: $BRAIN_ROOT)")
    p.add_argument(
        "--k-manuals",
        type=int,
        default=5,
        help="Manual leg hit count (bundled default 5; legacy callers may pass 3)",
    )
    p.add_argument(
        "--k-tickets",
        type=int,
        default=2,
        help="Ticket leg hit count (matches build_answer_bundle default)",
    )
    fmt = p.add_mutually_exclusive_group()
    fmt.add_argument("--json", dest="fmt", action="store_const", const="json")
    fmt.add_argument("--md", dest="fmt", action="store_const", const="md")
    p.set_defaults(fmt="json")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    """Build one bundle and print it."""
    args = _parser().parse_args(argv)
    if args.skip_tickets and args.skip_manual:
        print("answer_ticket: at least one leg required (omit both --skip-tickets and --skip-manual)", file=sys.stderr)
        return 2
    if args.postgres or (not args.no_wiki and not args.skip_manual):
        from utils.retail_fru.env import load_repo_env  # live paths need .env (DSN, API token); never overrides

        load_repo_env(ROOT)
    # Term-boosted search reads the prefix from env (phone-era default SAM-E would never boost FRU codes).
    os.environ.setdefault("RETAIL_FAULT_CODE_PREFIX", cached_company_profile().fault_code_prefix)
    sim = resolve_sim_data_profile()
    manifest = args.manifest or sim.ticket_manifest_jsonl
    issue_keys = load_issue_keys(manifest) if manifest and Path(manifest).is_file() else {}
    if args.skip_tickets:
        source = EmptyTicketSource()
    elif args.postgres:
        dsn = os.environ.get("RETAIL_DATABASE_URL")
        if not dsn:
            print("answer_ticket: RETAIL_DATABASE_URL not set", file=sys.stderr)
            return 2
        source = PgTicketSource(dsn, issue_keys)
    else:
        source = InMemoryTicketSource(load_ticket_rows(args.tickets_csv or sim.service_queries_csv), issue_keys)
    wiki = None
    if not args.no_wiki and not args.skip_manual:
        project = args.wiki_project or os.environ.get("BRAIN_ROOT") or str(ROOT / "brain" / "retail")
        wiki = LlmWikiHttpClient(str(Path(project).resolve()) if os.path.isdir(project) else project)
    brain = args.brain_root or Path(os.environ.get("BRAIN_ROOT") or ROOT / "brain" / "retail")
    bundle = build_answer_bundle(
        args.query,
        ticket_source=source,
        txt_index=load_txt_docs(brain),
        wiki=wiki,
        model=args.model,
        k_tickets=args.k_tickets,
        k_manuals=args.k_manuals,
        corpus_profile=sim.profile_id,
        skip_ticket_leg=args.skip_tickets,
        skip_manual_leg=args.skip_manual,
    )
    sys.stdout.write(bundle_to_json(bundle) if args.fmt == "json" else render_markdown(bundle))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
