#!/usr/bin/env python3
"""Merge second-brain mcp_servers into ~/.hermes/config.yaml (idempotent marker block)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

MARKER = "# --- second-brain mcp_servers (scripts/brain/setup-hermes-mcp.sh) ---"
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MCP = ROOT.parent / "nu_llm_wiki" / "mcp-server" / "dist" / "src" / "index.js"


def main() -> int:
    config_path = Path(os.environ.get("HERMES_CONFIG", Path.home() / ".hermes" / "config.yaml"))
    mcp_js = Path(os.environ.get("NU_LLM_WIKI_MCP", DEFAULT_MCP))
    brain = ROOT / "brain"
    token_ref = "${LLM_WIKI_API_TOKEN}"

    if not config_path.is_file():
        print(f"merge-hermes-mcp-config: missing {config_path}", file=sys.stderr)
        return 1
    if not mcp_js.is_file():
        print(f"merge-hermes-mcp-config: missing MCP entry {mcp_js}", file=sys.stderr)
        return 1

    block = f"""
{MARKER}
mcp_servers:
  llm_wiki:
    command: node
    args:
      - {mcp_js}
    env:
      LLM_WIKI_API_TOKEN: "{token_ref}"
  second_brain_fs:
    command: npx
    args:
      - "-y"
      - "@modelcontextprotocol/server-filesystem"
      - {brain}
"""

    text = config_path.read_text(encoding="utf-8")
    if MARKER in text:
        text = text.split(MARKER, 1)[0].rstrip()
    config_path.write_text(text + block + "\n", encoding="utf-8")
    print(f"merge-hermes-mcp-config: updated {config_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
