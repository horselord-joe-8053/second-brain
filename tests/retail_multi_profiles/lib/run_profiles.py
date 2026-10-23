"""Resolve named run_profiles from harness run-config.yaml."""

from __future__ import annotations

from typing import Any


def resolve_run_profile(cfg: dict[str, Any], profile_id: str) -> dict[str, Any]:
    """Return CLI kwargs fragment for a profile id or raise KeyError."""
    profiles = cfg.get("run_profiles") or {}
    block = profiles.get(profile_id)
    if not block or not isinstance(block, dict):
        raise KeyError(f"unknown run profile: {profile_id}")
    return dict(block)
