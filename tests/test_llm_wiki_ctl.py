"""local LLM Wiki process control: wrapper script and Hermes skill contract."""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "brain" / "llm-wiki.sh"
SKILL = REPO / "harness" / "second-brain" / "skills" / "local-llm-wiki" / "SKILL.md"


def test_llm_wiki_script_help_lists_lifecycle_commands() -> None:
    """status/start/stop/restart are the only operator commands, and help forbids token minting."""
    assert SCRIPT.is_file()
    assert SCRIPT.stat().st_mode & 0o111
    proc = subprocess.run(
        ["bash", str(SCRIPT), "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    text = proc.stdout
    for command in ("status", "start", "stop", "restart"):
        assert command in text
    assert "Generate" not in text or "Do not generate" in text
    assert "new Hermes session" in text


def test_local_llm_wiki_skill_is_not_the_compiler_skill() -> None:
    """Hermes loads this name from external_dirs; it must not collide with disabled llm-wiki."""
    text = SKILL.read_text(encoding="utf-8")
    assert text.startswith("---\nname: local-llm-wiki\n")
    assert "llm-wiki.sh" in text
    assert "token refreshed" in text
    assert "Generate new token" in text
    assert "bundled" in text
    query = (REPO / "harness" / "second-brain" / "skills" / "query-brain" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    assert "local-llm-wiki" in query
