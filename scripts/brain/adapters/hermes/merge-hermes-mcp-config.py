#!/usr/bin/env python3.12
"""Backward-compatible entry: delegates to merge-hermes-wiring.py (MCP + platforms)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

def main() -> int:
    wiring = Path(__file__).resolve().with_name("merge-hermes-wiring.py")
    return subprocess.call([sys.executable, str(wiring)])


if __name__ == "__main__":
    raise SystemExit(main())
