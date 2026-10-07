"""bootstrap_seed purity gate (REFACTOR_BOOTSTRAP_SEED_THREE_ZONES phase 3)."""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_check_seed_kit_exits_zero() -> None:
    script = REPO / "bootstrap_seed" / "core" / "scripts" / "check-seed-kit.sh"
    assert script.is_file()
    subprocess.run(["bash", str(script)], check=True, cwd=REPO)
