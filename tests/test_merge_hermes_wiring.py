"""merge-hermes-wiring.py preserves platforms and writes MCP block."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_merge_wiring_platforms_from_env(tmp_path: Path, monkeypatch) -> None:
    cfg = tmp_path / "config.yaml"
    cfg.write_text("model:\n  provider: gemini\n", encoding="utf-8")
    mcp = tmp_path / "index.js"
    mcp.write_text("// stub\n", encoding="utf-8")

    monkeypatch.setenv("HERMES_CONFIG", str(cfg))
    monkeypatch.setenv("NU_LLM_WIKI_MCP", str(mcp))
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "1:token")
    monkeypatch.setenv("TELEGRAM_ALLOWED_USERS", "12345")
    monkeypatch.setenv("TELEGRAM_HOME_CHANNEL", "12345")

    env = {**os.environ, "PYTHONPATH": str(REPO / "scripts" / "brain")}
    subprocess.run(
        [sys.executable, str(REPO / "scripts" / "brain" / "merge-hermes-wiring.py")],
        check=True,
        env=env,
        cwd=REPO,
    )
    text = cfg.read_text(encoding="utf-8")
    assert "llm_wiki:" in text
    assert "second_brain_fs:" in text
    assert "platforms:" in text
    assert "telegram:" in text
    assert "enabled: true" in text
    assert "chat_id: '12345'" in text
    assert WIRING_END in text if (WIRING_END := "# --- end second-brain wiring ---") else True


def test_merge_wiring_preserves_platforms_without_env(tmp_path: Path, monkeypatch) -> None:
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        """model:
  provider: gemini
# --- second-brain wiring (scripts/brain/merge-hermes-wiring.py) ---
mcp_servers:
  llm_wiki:
    command: node
platforms:
  whatsapp:
    enabled: true
    home_channel:
      chat_id: keep-me@lid
# --- end second-brain wiring ---
""",
        encoding="utf-8",
    )
    mcp = tmp_path / "index.js"
    mcp.write_text("// stub\n", encoding="utf-8")
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("WHATSAPP_ENABLED", raising=False)
    monkeypatch.setenv("HERMES_CONFIG", str(cfg))
    monkeypatch.setenv("NU_LLM_WIKI_MCP", str(mcp))

    env = {**os.environ, "PYTHONPATH": str(REPO / "scripts" / "brain")}
    subprocess.run(
        [sys.executable, str(REPO / "scripts" / "brain" / "merge-hermes-wiring.py")],
        check=True,
        env=env,
        cwd=REPO,
    )
    text = cfg.read_text(encoding="utf-8")
    assert "keep-me@lid" in text
