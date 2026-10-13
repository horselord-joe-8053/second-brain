#!/usr/bin/env python3.12
"""OpenClaw wiring stub: load shared MCP catalog; channel merge blocked until schema is known."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SCRIPTS_BRAIN = ROOT / "scripts" / "brain"
if str(SCRIPTS_BRAIN) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_BRAIN))

from brain_stack import load_brain_stack, load_mcp_servers_catalog  # noqa: E402


def main() -> int:
    stack = load_brain_stack(ROOT)
    catalog = load_mcp_servers_catalog(ROOT, stack)
    names = ", ".join(sorted(catalog.keys()))
    print(f"merge-openclaw-wiring: catalog OK ({names}); channel merge not implemented")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
