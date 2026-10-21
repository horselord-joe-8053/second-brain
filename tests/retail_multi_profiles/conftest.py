"""Pytest hooks for retail multi-profile lane benchmark (CI tier)."""

from __future__ import annotations

import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Register lane-benchmark markers."""
    config.addinivalue_line(
        "markers",
        "retail_lane_live: live LLM Wiki + real LLM/judge (not run in verify.sh)",
    )
