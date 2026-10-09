"""Brain stack config loader and env sync (REFACTOR_BRAIN_STACK_CONFIG)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def test_brain_stack_example_yaml_exists() -> None:
    assert (REPO / "config" / "brain-stack.example.yaml").is_file()


def test_load_brain_stack_example() -> None:
    import sys

    sys.path.insert(0, str(REPO / "scripts" / "brain"))
    from brain_stack import load_brain_stack

    stack = load_brain_stack(REPO)
    assert stack["paths"]["brain_root"].endswith("/brain") or stack["paths"]["brain_root"].endswith("brain")
    assert "OPENAI_API_KEY" in stack["hermes"]["sync_env_keys"]
    assert stack["llm_wiki"]["api_base_url"].startswith("http")
    assert stack.get("active_harness") == "hermes"


def test_active_harness_and_messaging_keys() -> None:
    import sys

    sys.path.insert(0, str(REPO / "scripts" / "brain"))
    from brain_stack import active_harness, load_brain_stack, messaging_sync_env_keys

    stack = load_brain_stack(REPO)
    assert active_harness(stack) == "hermes"
    msg = messaging_sync_env_keys(stack)
    assert "TELEGRAM_BOT_TOKEN" in msg
    assert "WHATSAPP_ENABLED" in msg


def test_expand_env_in_stack(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import sys

    sys.path.insert(0, str(REPO / "scripts" / "brain"))
    from brain_stack import expand_env_refs

    monkeypatch.setenv("MY_ROOT", str(tmp_path))
    out = expand_env_refs({"p": "${MY_ROOT}/brain"})
    assert out["p"] == f"{tmp_path}/brain"


def test_collect_secrets_prefers_yaml(tmp_path: Path) -> None:
    import sys

    sys.path.insert(0, str(REPO / "scripts" / "brain"))
    from brain_stack import collect_hermes_secrets

    stack = {
        "hermes": {"sync_env_keys": ["OPENAI_API_KEY", "GEMINI_API_KEY"]},
        "secrets": {"OPENAI_API_KEY": "from-yaml", "GEMINI_API_KEY": ""},
    }
    (tmp_path / ".env").write_text("GEMINI_API_KEY=from-env\n", encoding="utf-8")
    got = collect_hermes_secrets(stack, tmp_path)
    assert got["OPENAI_API_KEY"] == "from-yaml"
    assert got["GEMINI_API_KEY"] == "from-env"


def test_upsert_env_keys(tmp_path: Path) -> None:
    import sys

    sys.path.insert(0, str(REPO / "scripts" / "brain"))
    from brain_stack import upsert_env_file

    src = tmp_path / "src.env"
    dst = tmp_path / "dst.env"
    src.write_text("OPENAI_API_KEY=sk-test\nLLM_WIKI_API_TOKEN=abc\n", encoding="utf-8")
    dst.write_text("# hermes template\nOTHER=1\n", encoding="utf-8")
    upsert_env_file(
        dst,
        src,
        keys=["OPENAI_API_KEY", "LLM_WIKI_API_TOKEN", "MISSING_KEY"],
    )
    text = dst.read_text(encoding="utf-8")
    assert "OPENAI_API_KEY=sk-test" in text
    assert "LLM_WIKI_API_TOKEN=abc" in text
    assert "MISSING_KEY=" not in text
    assert "OTHER=1" in text
