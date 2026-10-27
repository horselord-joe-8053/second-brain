"""Merge run_profiles YAML, env, and CLI into one ResolvedRunProfile (D3 + D5)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from .config_coerce import coerce_bool, coerce_int
from .run_profiles import resolve_run_profile

# D3 retrieval engines for raw_rag (D5 is separate — see RUN_PROFILES.md).
_D3_ALIASES = {"hybrid_rrf_rerank": "hybrid_rrf"}


@dataclass(frozen=True)
class ResolvedRunProfile:
    """Effective harness dimensions after profile + env + CLI merge."""

    profile_id: str
    retrieval_mode: str
    d3_engine: str
    lane_ids: list[str]
    d5_rerank_enabled: bool = False
    d5_rerank_backend: str = "llm_listwise"
    d5_verifier_enabled: bool = False
    d5_agentic_enabled: bool = False
    d5_agentic_max_loops: int = 1
    manual_d3_backend: str = "pg"

    def dimension_tuple(self) -> str:
        """Informal profile_id string for analysis docs (D1.M manual raw)."""
        d5 = "0"
        parts: list[str] = []
        if self.d5_rerank_enabled:
            parts.append("R")
        if self.d5_verifier_enabled:
            parts.append("V")
        if self.d5_agentic_enabled:
            parts.append("A")
        if parts:
            d5 = "+".join(parts)
        lanes = ",".join(self.lane_ids)
        return f"MANUAL|M|D2.{lanes}|D3.{self._d3_label()}|LC|{d5}|M90|{lanes}"

    def _d3_label(self) -> str:
        if self.d3_engine == "vector":
            return "R-V"
        if self.d3_engine == "hybrid_rrf":
            return "R-H"
        return self.d3_engine

    def to_dict(self) -> dict[str, Any]:
        """JSON-serializable snapshot for results.json config_snapshot."""
        return {
            "profile_id": self.profile_id,
            "dimension_tuple": self.dimension_tuple(),
            "retrieval_mode": self.retrieval_mode,
            "d3_engine": self.d3_engine,
            "lane_ids": list(self.lane_ids),
            "d5": {
                "rerank": {
                    "enabled": self.d5_rerank_enabled,
                    "backend": self.d5_rerank_backend if self.d5_rerank_enabled else None,
                },
                "verifier": {"enabled": self.d5_verifier_enabled},
                "agentic": {
                    "enabled": self.d5_agentic_enabled,
                    "max_loops": self.d5_agentic_max_loops,
                },
            },
            "manual_d3_backend": self.manual_d3_backend,
        }


def _d5_block(prof: dict[str, Any], raw_rag: dict[str, Any]) -> dict[str, Any]:
    """Profile d5 block with fallback to legacy retail_raw_rag.agentic only for global defaults."""
    d5 = prof.get("d5")
    if isinstance(d5, dict):
        return d5
    return {}


def _parse_d5(
    prof: dict[str, Any],
    raw_rag: dict[str, Any],
    *,
    cli_raw_agentic: bool,
    env: dict[str, str] | None = None,
) -> tuple[bool, str, bool, bool, int]:
    """Return (rerank_on, backend, verifier_on, agentic_on, max_loops)."""
    env = env if env is not None else os.environ
    d5 = _d5_block(prof, raw_rag)
    rerank = d5.get("rerank") if isinstance(d5.get("rerank"), dict) else {}
    verifier = d5.get("verifier") if isinstance(d5.get("verifier"), dict) else {}
    agentic = d5.get("agentic") if isinstance(d5.get("agentic"), dict) else {}

    global_agentic = (raw_rag.get("agentic") or {}) if isinstance(raw_rag.get("agentic"), dict) else {}

    rerank_on = coerce_bool(rerank.get("enabled"), default=False)
    if "RETAIL_D5_RERANK_ENABLED" in env:
        rerank_on = coerce_bool(env["RETAIL_D5_RERANK_ENABLED"], default=rerank_on)

    backend = str(rerank.get("backend") or "llm_listwise").strip().lower()
    if env.get("RETAIL_D5_RERANK_BACKEND"):
        backend = env["RETAIL_D5_RERANK_BACKEND"].strip().lower()
    if rerank_on and not backend:
        backend = "llm_listwise"

    verifier_on = coerce_bool(verifier.get("enabled"), default=False)
    agentic_on = coerce_bool(
        agentic.get("enabled"),
        default=coerce_bool(global_agentic.get("enabled"), default=False),
    )
    if cli_raw_agentic:
        agentic_on = True
    if "RETAIL_D5_AGENTIC_ENABLED" in env:
        agentic_on = coerce_bool(env["RETAIL_D5_AGENTIC_ENABLED"], default=agentic_on)

    max_loops = coerce_int(agentic.get("max_loops"), default=coerce_int(global_agentic.get("max_loops"), default=1))

    # Legacy profile id: raw_retrieval hybrid_rrf_rerank implied D5.R+V+A when d5 block absent.
    raw_ret = str(prof.get("raw_retrieval") or "")
    if raw_ret == "hybrid_rrf_rerank" and not isinstance(prof.get("d5"), dict):
        rerank_on = True
        verifier_on = True
        agentic_on = True

    return rerank_on, backend, verifier_on, agentic_on, max_loops


def resolve_effective_profile(
    cfg: dict[str, Any],
    *,
    profile_id: str,
    lane_ids: list[str],
    retrieval_mode: str = "",
    raw_retrieval: str = "",
    raw_agentic: bool = False,
    env: dict[str, str] | None = None,
) -> ResolvedRunProfile:
    """Apply precedence CLI → env → run_profiles block → defaults (R18)."""
    prof = resolve_run_profile(cfg, profile_id)
    raw_rag = cfg.get("retail_raw_rag") or {}

    rm = str(prof.get("retrieval_mode") or retrieval_mode or "llm_wiki")
    d3 = str(prof.get("raw_retrieval") or raw_retrieval or "vector").strip()
    d3 = _D3_ALIASES.get(d3, d3)

    lanes = lane_ids
    if prof.get("lanes"):
        lanes = [x.strip() for x in str(prof["lanes"]).split(",") if x.strip()]

    rerank_on, backend, verifier_on, agentic_on, max_loops = _parse_d5(
        prof, raw_rag, cli_raw_agentic=raw_agentic, env=env
    )

    manual_backend = str(prof.get("manual_d3_backend") or "pg").strip().lower()
    if manual_backend != "pg":
        raise ValueError(
            f"manual_d3_backend={manual_backend!r} is removed; use Postgres (evo-16 branch kept Lance)"
        )

    return ResolvedRunProfile(
        profile_id=profile_id,
        retrieval_mode=rm,
        d3_engine=d3,
        lane_ids=list(lanes),
        d5_rerank_enabled=rerank_on,
        d5_rerank_backend=backend if rerank_on else "llm_listwise",
        d5_verifier_enabled=verifier_on,
        d5_agentic_enabled=agentic_on,
        d5_agentic_max_loops=max_loops,
        manual_d3_backend=manual_backend,
    )


def assert_rerank_preflight(resolved: ResolvedRunProfile, rank_fn: Any) -> None:
    """P1.2d — refuse full runs when D5.R is on but rank_fn is missing."""
    if not resolved.d5_rerank_enabled:
        return
    if resolved.d5_rerank_backend == "cross_encoder":
        raise RuntimeError("d5.rerank.backend cross_encoder is not implemented in Phase 1")
    if rank_fn is None:
        raise RuntimeError(
            f"profile {resolved.profile_id!r} has d5.rerank.enabled but no rank_fn (llm_listwise)"
        )
