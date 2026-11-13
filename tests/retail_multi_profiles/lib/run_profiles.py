"""Resolve named run_profiles from harness run-config.yaml."""

from __future__ import annotations

from typing import Any

# HG-P1 (2026-10-25): operational default when CLI omits --profile on raw_rag runs.
# Eval comparison anchor stays raw vector (abcd-raw-full-openai-v1) — not this id.
DEFAULT_RUN_PROFILE_ID = "MANUAL_B_RAW_HYBRID_RERANK"


def effective_run_profile_id(
    cfg: dict[str, Any],
    *,
    cli_profile: str,
    retrieval_mode: str,
) -> str:
    """Return profile id to resolve: explicit --profile, else YAML default on raw_rag only."""
    pid = (cli_profile or "").strip()
    if pid:
        return pid
    if retrieval_mode != "raw_rag":
        return ""
    configured = str(cfg.get("default_run_profile") or DEFAULT_RUN_PROFILE_ID).strip()
    if not configured:
        return ""
    resolve_run_profile(cfg, configured)  # fail fast if misconfigured
    return configured


def resolve_run_profile(cfg: dict[str, Any], profile_id: str) -> dict[str, Any]:
    """Return CLI kwargs fragment for a profile id or raise KeyError."""
    profiles = cfg.get("run_profiles") or {}
    block = profiles.get(profile_id)
    if not block or not isinstance(block, dict):
        raise KeyError(f"unknown run profile: {profile_id}")
    return dict(block)
