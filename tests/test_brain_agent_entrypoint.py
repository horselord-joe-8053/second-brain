"""Contract tests for scripts/brain/agent.sh harness dispatch."""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
AGENT = REPO / "scripts" / "brain" / "agent.sh"
HERMES_START = REPO / "scripts" / "brain" / "adapters" / "hermes" / "start.sh"
HERMES_STOP = REPO / "scripts" / "brain" / "adapters" / "hermes" / "stop.sh"
OPENCLAW_START = REPO / "scripts" / "brain" / "adapters" / "openclaw" / "start.sh"


def test_agent_sh_exists_and_help_lists_subcommands() -> None:
    assert AGENT.is_file()
    proc = subprocess.run(
        ["bash", str(AGENT), "help"],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    out = proc.stdout.lower()
    for word in ("setup", "start", "stop", "restart", "status"):
        assert word in out, proc.stdout


def test_agent_status_exits_zero() -> None:
    proc = subprocess.run(
        ["bash", str(AGENT), "status"],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr + proc.stdout


def test_hermes_delegate_scripts_wrap_legacy_entrypoints() -> None:
    assert HERMES_START.is_file()
    assert HERMES_STOP.is_file()
    start_text = HERMES_START.read_text(encoding="utf-8")
    stop_text = HERMES_STOP.read_text(encoding="utf-8")
    assert "start-hermes.sh" in start_text
    assert "stop-hermes.sh" in stop_text


def test_openclaw_start_stub_exits_nonzero() -> None:
    assert OPENCLAW_START.is_file()
    proc = subprocess.run(
        ["bash", str(OPENCLAW_START)],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 2
    assert "openclaw" in (proc.stdout + proc.stderr).lower()
