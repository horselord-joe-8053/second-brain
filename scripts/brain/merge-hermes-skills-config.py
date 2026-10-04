#!/usr/bin/env python3
"""Patch ~/.hermes/config.yaml skills.disabled + external_dirs for Second Brain."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HARNESS_SKILLS = ROOT / "harness" / "second-brain" / "skills"
DISABLE = "llm-wiki"


def main() -> int:
    config_path = Path(os.environ.get("HERMES_CONFIG", Path.home() / ".hermes" / "config.yaml"))
    if not config_path.is_file():
        print(f"merge-hermes-skills-config: missing {config_path}", file=sys.stderr)
        return 1

    text = config_path.read_text(encoding="utf-8")
    if f"    - {DISABLE}" in text and str(HARNESS_SKILLS) in text:
        print("merge-hermes-skills-config: already patched")
        return 0

    needle = "  creation_nudge_interval:"
    insert = (
        f"  disabled:\n"
        f"    - {DISABLE}\n"
        f"  external_dirs:\n"
        f"    - {HARNESS_SKILLS}\n"
        f"{needle}"
    )
    if needle not in text:
        print("merge-hermes-skills-config: skills.creation_nudge_interval not found", file=sys.stderr)
        return 1
    if "  disabled:" in text.split("agent:", 1)[0]:
        print("merge-hermes-skills-config: skills.disabled already present; add llm-wiki manually if needed")
        return 0

    config_path.write_text(text.replace(needle, insert, 1), encoding="utf-8")
    print(f"merge-hermes-skills-config: disabled={DISABLE}, external_dirs={HARNESS_SKILLS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
