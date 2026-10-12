#!/usr/bin/env python3
"""Idempotent Postgres reload for the active RETAIL_SIM_DATA_PROFILE corpus.

TRUNCATE service_queries → load profile CSV → embed (Gemini). Safe to re-run; only this
profile's tickets remain in PG after success.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "retail"))

from utils.retail_fru.env import load_repo_env  # noqa: E402

load_repo_env(ROOT)

from retail_brain.sim_data_profile import resolve_sim_data_profile  # noqa: E402


def _psql_truncate(dsn: str) -> None:
    import psycopg2  # type: ignore

    conn = psycopg2.connect(dsn)
    try:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE service_queries;")
        conn.commit()
    finally:
        conn.close()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--profile", help="Override RETAIL_SIM_DATA_PROFILE")
    p.add_argument(
        "--skip-truncate",
        action="store_true",
        help="Load without truncate (debug only; breaks profile isolation)",
    )
    args = p.parse_args()
    if args.profile:
        os.environ["RETAIL_SIM_DATA_PROFILE"] = args.profile

    dsn = os.environ.get("RETAIL_DATABASE_URL")
    if not dsn:
        raise SystemExit("RETAIL_DATABASE_URL required for reload_postgres_corpus.py")

    prof = resolve_sim_data_profile()
    prof.validate_files()
    prof.log_banner("Postgres reload (TRUNCATE → load → embed)")

    scripts = ROOT / "scripts" / "retail"
    if not args.skip_truncate:
        print(f"[sim_data_profile={prof.profile_id}] TRUNCATE service_queries", file=sys.stderr)
        _psql_truncate(dsn)

    print(f"[sim_data_profile={prof.profile_id}] load {prof.service_queries_csv}", file=sys.stderr)
    subprocess.run(
        [sys.executable, str(scripts / "load_service_queries.py"), str(prof.service_queries_csv)],
        check=True,
    )
    print(f"[sim_data_profile={prof.profile_id}] embed (Gemini)", file=sys.stderr)
    subprocess.run([sys.executable, str(scripts / "embed_service_queries.py")], check=True)
    print(f"[sim_data_profile={prof.profile_id}] reload complete", file=sys.stderr)


if __name__ == "__main__":
    main()
