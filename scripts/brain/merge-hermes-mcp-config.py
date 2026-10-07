#!/usr/bin/env python3
"""Backward-compatible entry: delegates to merge-hermes-wiring.py (MCP + platforms)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    wiring = ROOT / "scripts" / "brain" / "merge-hermes-wiring.py"
    return subprocess.call([sys.executable, str(wiring)])


if __name__ == "__main__":
    raise SystemExit(main())
