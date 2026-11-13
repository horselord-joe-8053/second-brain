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

RRF_DATA_PRAG_GEN = "rrf_data_prag_gen"
RRF_DATA_LLM_GEN = "rrf_data_llm_gen"
RRF_DATA_LLM_GEN_60_10 = "rrf_data_llm_gen_60_10"
RRF_DATA_LLM_GEN_1K = "rrf_data_llm_gen_1k"
FRU_US_1K = "fru_us_1k"

DEFAULT_PROFILE = FRU_US_1K

VALID_PROFILES = (
    RRF_DATA_PRAG_GEN,
    RRF_DATA_LLM_GEN,
    RRF_DATA_LLM_GEN_60_10,
    RRF_DATA_LLM_GEN_1K,
    FRU_US_1K,
)


def repo_root() -> Path:
    """Absolute path to second_brain repo root (parent of ``scripts/``)."""
    return Path(__file__).resolve().parents[3]


def _sim_profiles_root(root: Path) -> Path:
    return root / "scripts" / "retail" / "sim_data" / "profiles"


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
        """Raise ``FileNotFoundError`` if CSV or eval JSONL for this profile is missing."""
        if not self.service_queries_csv.is_file():
            raise FileNotFoundError(
                f"[sim_data_profile={self.profile_id}] missing CSV: {self.service_queries_csv}"
            )
        if not self.eval_jsonl.is_file():
            raise FileNotFoundError(
                f"[sim_data_profile={self.profile_id}] missing eval JSONL: {self.eval_jsonl}"
            )

    def as_report_fields(self) -> Dict[str, str]:
        """Metadata dict embedded in eval JSON reports."""
        return {
            "sim_data_profile": self.profile_id,
            "sim_data_profile_label": self.label,
            "service_queries_csv": str(self.service_queries_csv),
            "eval_jsonl": str(self.eval_jsonl),
        }

    def log_banner(self, phase: str, *, stream=None) -> None:
        """Print profile paths to stderr (or ``stream``) at prep-script phase boundaries."""
        out = stream or sys.stderr
        print(
            f"\n=== RETAIL sim_data_profile={self.profile_id} ({self.label}) — {phase} ===\n"
            f"  CSV:     {self.service_queries_csv}\n"
            f"  Eval:    {self.eval_jsonl}\n"
            f"  Reports: {self.reports_dir}\n",
            file=out,
        )


def _profiles(root: Path) -> Mapping[str, SimDataProfile]:
    """Static registry of prag vs LLM corpus path bundles."""
    p60 = _sim_profiles_root(root) / "data_60_10"
    p1k = _sim_profiles_root(root) / "data_1000_100"
    pfru = _sim_profiles_root(root) / "fru_us_1000_100"
    mini = SimDataProfile(
        profile_id=RRF_DATA_LLM_GEN_60_10,
        label="LLM corpus 60 historical + 10 ABC eval (data_60_10)",
        service_queries_csv=p60 / "service_queries.csv",
        eval_jsonl=p60 / "ticket_retrieval.jsonl",
        reports_dir=p60 / "reports",
        ticket_manifest_jsonl=p60 / "ticket_manifest.jsonl",
    )
    large = SimDataProfile(
        profile_id=RRF_DATA_LLM_GEN_1K,
        label="LLM corpus 1000 historical + 100 ABC eval (data_1000_100)",
        service_queries_csv=p1k / "service_queries.csv",
        eval_jsonl=p1k / "ticket_retrieval.jsonl",
        reports_dir=p1k / "reports",
        ticket_manifest_jsonl=p1k / "ticket_manifest.jsonl",
    )
    fru = SimDataProfile(
        profile_id=FRU_US_1K,
        label="FRU US corpus 1000 historical + 100 ABC eval (fru_us_1000_100)",
        service_queries_csv=pfru / "service_queries.csv",
        eval_jsonl=pfru / "ticket_retrieval.jsonl",
        reports_dir=pfru / "reports",
        ticket_manifest_jsonl=pfru / "ticket_manifest.jsonl",
    )
    return {
        RRF_DATA_PRAG_GEN: SimDataProfile(
            profile_id=RRF_DATA_PRAG_GEN,
            label="Programmatic seed (generate_tickets.py / seed_narrative)",
            service_queries_csv=root / "scripts/retail/seed/generated/service_queries.csv",
            eval_jsonl=root / "scripts/retail/eval/ticket_retrieval.jsonl",
            reports_dir=root / "scripts/retail/eval/reports/prag_gen",
            ticket_manifest_jsonl=root / "scripts/retail/seed/generated/ticket_manifest.jsonl",
        ),
        RRF_DATA_LLM_GEN_60_10: mini,
        RRF_DATA_LLM_GEN: mini,
        RRF_DATA_LLM_GEN_1K: large,
        FRU_US_1K: fru,
    }


def resolve_sim_data_profile(name: str | None = None) -> SimDataProfile:
    """RETAIL_SIM_DATA_PROFILE env; default fru_us_1k."""
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
    """CLI: print paths, bash exports, or validate corpus files."""
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
