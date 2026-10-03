#!/usr/bin/env python3
"""Verify enforced feature specs have matching test_ac_* pytest functions."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPECS_DIR = ROOT / "docs" / "specs"
TEST_DIRS = [ROOT / "backend" / "tests", ROOT / "frontend" / "src"]

ENFORCE_MARKER = "<!-- ac-tests: enforced -->"
AC_PATTERN = re.compile(r"\*\*AC-([A-Z]+)(\d+):\*\*")
TEST_FUNC_PATTERN = re.compile(r"def (test_ac_[a-z0-9_]+)\(", re.IGNORECASE)


def ac_to_prefix(ac_letters: str, ac_num: str) -> str:
    return f"test_ac_{ac_letters.lower()}{ac_num}_"


def collect_test_names() -> set[str]:
    names: set[str] = set()
    for directory in TEST_DIRS:
        if not directory.is_dir():
            continue
        for path in directory.rglob("*.py"):
            if path.name.startswith("test_") or "/tests/" in str(path):
                names.update(TEST_FUNC_PATTERN.findall(path.read_text(encoding="utf-8")))
        for path in directory.rglob("*.test.tsx"):
            text = path.read_text(encoding="utf-8")
            for match in re.finditer(r"test_ac_[a-z0-9]+", text, re.IGNORECASE):
                names.add(match.group(0).lower())
    return {n.lower() for n in names}


def main() -> int:
    if not SPECS_DIR.is_dir():
        print("check-ac-tests: no docs/specs; skip")
        return 0

    test_names = collect_test_names()
    errors: list[str] = []

    for spec_path in sorted(SPECS_DIR.glob("*.md")):
        text = spec_path.read_text(encoding="utf-8")
        if ENFORCE_MARKER not in text:
            continue
        ac_ids = AC_PATTERN.findall(text)
        if not ac_ids:
            errors.append(f"{spec_path.name}: enforced but no **AC-*:** ids found")
            continue
        for letters, num in ac_ids:
            prefix = ac_to_prefix(letters, num)
            base = f"test_ac_{letters.lower()}{num}"
            if not any(
                name == base or name.startswith(prefix) for name in test_names
            ):
                errors.append(
                    f"{spec_path.name}: missing pytest matching {prefix}* "
                    f"(AC-{letters}{num})"
                )

    if errors:
        print("check-ac-tests: FAILED", file=sys.stderr)
        for line in errors:
            print(f"  - {line}", file=sys.stderr)
        return 1

    print("check-ac-tests: enforced specs OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
