"""Simulated ticket corpus profiles for Postgres load + A/B eval (isolated reload per profile).

Two corpora share one `service_queries` table: switching profile TRUNCATEs and reloads that
profile's CSV only. Runtime isolation is temporal (one active corpus in PG), not side-by-side.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Mapping

# Profile ids (env RETAIL_SIM_DATA_PROFILE)
RRF_DATA_PRAG_GEN = "rrf_data_prag_gen"
RRF_DATA_LLM_GEN = "rrf_data_llm_gen"

DEFAULT_PROFILE = RRF_DATA_LLM_GEN

VALID_PROFILES = (RRF_DATA_PRAG_GEN, RRF_DATA_LLM_GEN)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class SimDataProfile:
    """Paths and labels for one simulated-data corpus."""

    profile_id: str
    label: str
    service_queries_csv: Path
    eval_jsonl: Path
    reports_dir: Path
    ticket_manifest_jsonl: Path | None = None

    def validate_files(self) -> None:
        if not self.service_queries_csv.is_file():
            raise FileNotFoundError(
                f"[sim_data_profile={self.profile_id}] missing CSV: {self.service_queries_csv}"
            )
        if not self.eval_jsonl.is_file():
            raise FileNotFoundError(
                f"[sim_data_profile={self.profile_id}] missing eval JSONL: {self.eval_jsonl}"
            )

    def as_report_fields(self) -> Dict[str, str]:
        return {
            "sim_data_profile": self.profile_id,
            "sim_data_profile_label": self.label,
            "service_queries_csv": str(self.service_queries_csv),
            "eval_jsonl": str(self.eval_jsonl),
        }

    def log_banner(self, phase: str, *, stream=None) -> None:
        out = stream or sys.stderr
        print(
            f"\n=== RETAIL sim_data_profile={self.profile_id} ({self.label}) — {phase} ===\n"
            f"  CSV:     {self.service_queries_csv}\n"
            f"  Eval:    {self.eval_jsonl}\n"
            f"  Reports: {self.reports_dir}\n",
            file=out,
        )


def _profiles(root: Path) -> Mapping[str, SimDataProfile]:
    return {
        RRF_DATA_PRAG_GEN: SimDataProfile(
            profile_id=RRF_DATA_PRAG_GEN,
            label="Programmatic seed (generate_tickets.py / seed_narrative)",
            service_queries_csv=root / "scripts/retail/seed/generated/service_queries.csv",
            eval_jsonl=root / "scripts/retail/eval/ticket_retrieval.jsonl",
            reports_dir=root / "scripts/retail/eval/reports/prag_gen",
            ticket_manifest_jsonl=root / "scripts/retail/seed/generated/ticket_manifest.jsonl",
        ),
        RRF_DATA_LLM_GEN: SimDataProfile(
            profile_id=RRF_DATA_LLM_GEN,
            label="LLM-authored corpus (tmp/simulated_data)",
            service_queries_csv=root / "tmp/simulated_data/service_queries.csv",
            eval_jsonl=root / "tmp/simulated_data/ticket_retrieval.jsonl",
            reports_dir=root / "tmp/simulated_data/reports",
            ticket_manifest_jsonl=root / "tmp/simulated_data/ticket_manifest.jsonl",
        ),
    }


def resolve_sim_data_profile(name: str | None = None) -> SimDataProfile:
    """RETAIL_SIM_DATA_PROFILE env; default rrf_data_llm_gen."""
    raw = (name or os.environ.get("RETAIL_SIM_DATA_PROFILE") or DEFAULT_PROFILE).strip()
    if raw not in VALID_PROFILES:
        raise ValueError(
            f"Unknown RETAIL_SIM_DATA_PROFILE={raw!r}; use one of: {', '.join(VALID_PROFILES)}"
        )
    return _profiles(repo_root())[raw]


def shell_exports(root: Path | None = None) -> str:
    """Bash-evalable exports for prep scripts."""
    root = root or repo_root()
    prof = resolve_sim_data_profile()
    lines = [
        f'export RETAIL_SIM_DATA_PROFILE="{prof.profile_id}"',
        f'export RETAIL_SIM_CSV="{prof.service_queries_csv}"',
        f'export RETAIL_SIM_EVAL="{prof.eval_jsonl}"',
        f'export RETAIL_SIM_REPORTS_DIR="{prof.reports_dir}"',
        f'export RETAIL_SIM_PROFILE_LABEL="{prof.label}"',
    ]
    return "\n".join(lines) + "\n"


def _main() -> None:
    import argparse

    p = argparse.ArgumentParser(description="Resolve retail simulated-data profile paths.")
    p.add_argument("--profile", help="Override RETAIL_SIM_DATA_PROFILE for this invocation")
    p.add_argument("--shell", action="store_true", help="Print bash export statements")
    p.add_argument("--validate", action="store_true", help="Exit 1 if corpus files missing")
    args = p.parse_args()
    if args.profile:
        os.environ["RETAIL_SIM_DATA_PROFILE"] = args.profile
    prof = resolve_sim_data_profile()
    if args.validate:
        prof.validate_files()
    if args.shell:
        sys.stdout.write(shell_exports())
    else:
        print(prof.profile_id)
        print(prof.service_queries_csv)
        print(prof.eval_jsonl)
        print(prof.reports_dir)


if __name__ == "__main__":
    _main()
