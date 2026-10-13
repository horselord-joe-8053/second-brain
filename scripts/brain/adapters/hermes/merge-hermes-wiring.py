#!/usr/bin/env python3.12
"""Merge Second Brain MCP + optional messaging platforms into ~/.hermes/config.yaml."""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

# Legacy single marker (mcp-only); new managed region uses START/END.
LEGACY_MCP_MARKER = "# --- second-brain mcp_servers (scripts/brain/setup-hermes-mcp.sh) ---"
WIRING_START = "# --- second-brain wiring (scripts/brain/adapters/hermes/merge-hermes-wiring.py) ---"
WIRING_END = "# --- end second-brain wiring ---"

ROOT = Path(__file__).resolve().parents[4]
SCRIPTS_BRAIN = ROOT / "scripts" / "brain"
if str(SCRIPTS_BRAIN) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_BRAIN))
from brain_stack import format_mcp_servers_block, load_brain_stack, load_mcp_servers_catalog

DEFAULT_MCP = ROOT.parent / "nu_llm_wiki" / "mcp-server" / "dist" / "src" / "index.js"


def _strip_managed_region(text: str) -> tuple[str, str]:
    """Return (before, preserved_tail). Removes legacy or START..END wiring blocks."""
    if WIRING_START in text:
        before = text.split(WIRING_START, 1)[0].rstrip()
        tail = text.split(WIRING_START, 1)[1]
        if WIRING_END in tail:
            preserved = tail.split(WIRING_END, 1)[1].lstrip("\n")
        else:
            preserved = ""
        return before, preserved

    if LEGACY_MCP_MARKER in text:
        before = text.split(LEGACY_MCP_MARKER, 1)[0].rstrip()
        # Legacy block ran to EOF; anything after mcp was already lost on prior merges.
        return before, ""

    return text.rstrip(), ""


def _extract_platforms_yaml(old_region: str) -> str | None:
    """If a previous wiring block had platforms:, return that subtree as text."""
    if not old_region.strip():
        return None
    m = re.search(r"(?ms)^platforms:\n(.*?)(?=^onboarding:|\Z)", old_region)
    if not m:
        return None
    return "platforms:\n" + m.group(1).rstrip() + "\n"


def _platforms_from_env() -> str | None:
    tg_token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    tg_users = os.environ.get("TELEGRAM_ALLOWED_USERS", "").strip()
    wa_on = os.environ.get("WHATSAPP_ENABLED", "").strip().lower() in ("1", "true", "yes")
    wa_users = os.environ.get("WHATSAPP_ALLOWED_USERS", "").strip()

    lines: list[str] = []
    if tg_token and tg_users:
        lines.append("platforms:")
        lines.append("  telegram:")
        lines.append("    enabled: true")
        home = os.environ.get("TELEGRAM_HOME_CHANNEL", "").strip()
        if home:
            lines.append("    home_channel:")
            lines.append("      platform: telegram")
            lines.append(f"      chat_id: '{home}'")
            lines.append(f"      user_id: '{home}'")
    elif tg_token or tg_users:
        print(
            "merge-hermes-wiring: TELEGRAM_BOT_TOKEN and TELEGRAM_ALLOWED_USERS both required for telegram.enabled",
            file=sys.stderr,
        )

    if wa_on and wa_users:
        if not lines:
            lines.append("platforms:")
        lines.append("  whatsapp:")
        lines.append("    enabled: true")
        home = os.environ.get("WHATSAPP_HOME_CHANNEL", "").strip()
        if home:
            lines.append("    home_channel:")
            lines.append("      platform: whatsapp")
            lines.append(f"      chat_id: {home}")
            wa_uid = os.environ.get("WHATSAPP_HOME_USER_ID", "").strip()
            if wa_uid:
                lines.append(f"      user_id: {wa_uid}")
    elif wa_on or wa_users:
        print(
            "merge-hermes-wiring: WHATSAPP_ENABLED=true and WHATSAPP_ALLOWED_USERS required for whatsapp.enabled",
            file=sys.stderr,
        )

    if not lines:
        return None
    return "\n".join(lines) + "\n"


def main() -> int:
    config_path = Path(os.environ.get("HERMES_CONFIG", Path.home() / ".hermes" / "config.yaml"))
    stack = load_brain_stack(ROOT)
    mcp_js = Path(os.environ.get("NU_LLM_WIKI_MCP", stack["hermes"]["mcp_server_js"]))
    if not config_path.is_file():
        print(f"merge-hermes-wiring: missing {config_path}", file=sys.stderr)
        return 1
    if not mcp_js.is_file():
        print(f"merge-hermes-wiring: missing MCP entry {mcp_js}", file=sys.stderr)
        return 1

    text = config_path.read_text(encoding="utf-8")
    old_region = ""
    if WIRING_START in text:
        old_region = text.split(WIRING_START, 1)[1]
        if WIRING_END in old_region:
            old_region = old_region.split(WIRING_END, 1)[0]
    elif LEGACY_MCP_MARKER in text:
        old_region = text.split(LEGACY_MCP_MARKER, 1)[1]

    before, preserved_tail = _strip_managed_region(text)

    catalog = load_mcp_servers_catalog(ROOT, stack)
    mcp_block = format_mcp_servers_block(catalog)

    platforms = _platforms_from_env()
    if not platforms:
        platforms = _extract_platforms_yaml(old_region)

    parts = [before, "", WIRING_START, mcp_block.rstrip()]
    if platforms:
        parts.append(platforms.rstrip())
    parts.append(WIRING_END)
    if preserved_tail.strip():
        parts.append("")
        parts.append(preserved_tail.rstrip())
    new_text = "\n".join(parts).rstrip() + "\n"

    config_path.write_text(new_text, encoding="utf-8")
    print(f"merge-hermes-wiring: updated {config_path}")
    if platforms:
        print("merge-hermes-wiring: platforms block present (env or preserved)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
