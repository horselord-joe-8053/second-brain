#!/usr/bin/env python3
"""Thin wrapper — logic lives in ``tests.utils.log_based``."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
if not (_REPO / "config" / "main_config.yaml").exists():
    _REPO = Path(__file__).resolve().parents[3]


def main() -> int:
    argv = ["-m", "tests.utils.log_based", "trabat-flow", *sys.argv[1:]]
    proc = subprocess.run(
        [sys.executable, *argv],
        cwd=_REPO,
        env={**os.environ, "PYTHONPATH": f"{_REPO / 'apps' / 'api'}{os.pathsep}{_REPO}"},
    )
    return int(proc.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
