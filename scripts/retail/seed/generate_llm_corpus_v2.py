#!/usr/bin/env python3.12
"""Shim: generate ``data_1000_100`` profile via ``sim_data.generation.cli``."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts" / "retail"))

from sim_data.generation.cli import generate_profile

if __name__ == "__main__":
    generate_profile("data_1000_100")
