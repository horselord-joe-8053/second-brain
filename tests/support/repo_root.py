"""Repo root path for tests nested under ``tests/`` subpackages."""

from __future__ import annotations

from pathlib import Path

# ``tests/support/repo_root.py`` → parents[2] is the repository root.
REPO_ROOT = Path(__file__).resolve().parents[2]
