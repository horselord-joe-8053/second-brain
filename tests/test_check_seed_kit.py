"""Fabrication skill purity gate (fabrication plan phase 5)."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FAB = REPO / ".cursor" / "skills" / "fabrication"
CHECK = FAB / "scripts" / "check-seed-kit.sh"


def test_check_seed_kit_exits_zero() -> None:
    assert CHECK.is_file()
    subprocess.run(["bash", str(CHECK)], check=True, cwd=REPO)


def test_check_seed_kit_fails_on_forbidden_string() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp) / "fabrication"
        shutil.copytree(FAB, dest)
        poison = dest / "references" / "poison.txt"
        poison.write_text("portuguese-learn", encoding="utf-8")
        script = dest / "scripts" / "check-seed-kit.sh"
        proc = subprocess.run(["bash", str(script)], cwd=dest, capture_output=True, text=True)
        assert proc.returncode != 0
