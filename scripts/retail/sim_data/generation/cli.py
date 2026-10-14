#!/usr/bin/env python3.12
"""CLI entry: generate historical + ABC eval for a sim_data profile."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts" / "retail"))

from sim_data.generation.eval_abc import generate_abc_eval, generate_legacy_ten_eval
from sim_data.generation.io import write_csv, write_eval, write_manifest
from sim_data.generation.profiles import PROFILE_SPECS
from sim_data.generation.tickets import generate_historical


def profile_dir(name: str) -> Path:
    return ROOT / "scripts" / "retail" / "sim_data" / "profiles" / name


def generate_profile(spec_name: str) -> Path:
    """Write CSV, manifest, and eval JSONL for ``spec_name``."""
    spec = PROFILE_SPECS[spec_name]
    out = profile_dir(spec.dir_name)
    if spec.skip_regen:
        print(f"skip_regen: {spec_name} (frozen snapshot under {out})")
        return out
    rows = generate_historical(seed=spec.seed, count=spec.historical_count)
    if spec.eval_paraphrase + spec.eval_hybrid + spec.eval_code == 10:
        eval_rows = generate_legacy_ten_eval(rows, spec.seed)
    else:
        eval_rows = generate_abc_eval(
            rows,
            seed=spec.seed,
            n_paraphrase=spec.eval_paraphrase,
            n_hybrid=spec.eval_hybrid,
            n_code=spec.eval_code,
        )
    write_csv(out / "service_queries.csv", rows)
    write_manifest(out / "ticket_manifest.jsonl", rows, spec.seed)
    write_eval(out / "ticket_retrieval.jsonl", eval_rows)
    sam = sum(1 for r in rows if r.has_sam_e)
    print(
        f"wrote profile={spec_name} tickets={len(rows)} eval={len(eval_rows)} "
        f"SAM-E={sam} -> {out}"
    )
    return out


def main() -> None:
    p = argparse.ArgumentParser(description="Generate sim_data profile corpus.")
    p.add_argument(
        "--profile",
        choices=sorted(PROFILE_SPECS.keys()),
        default="data_1000_100",
    )
    args = p.parse_args()
    generate_profile(args.profile)


if __name__ == "__main__":
    main()
