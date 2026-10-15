"""Brain stack config loader and env sync (REFACTOR_BRAIN_STACK_CONFIG)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def test_brain_stack_example_yaml_exists() -> None:
    assert (REPO / "config" / "brain-stack.example.yaml").is_file()


def _import_brain_stack():
    """Import scripts/brain/brain_stack.py as a module."""
    import sys

    sys.path.insert(0, str(REPO / "scripts" / "brain"))
    import brain_stack

    return brain_stack


def _write_stack(repo: Path, local: str = "") -> None:
    """Create a minimal repo with example (+ optional local) brain-stack yaml."""
    cfg = repo / "config"
    cfg.mkdir(parents=True, exist_ok=True)
    (cfg / "brain-stack.example.yaml").write_text(
        'version: 1\npaths:\n  brains_dir: "brain"\nhermes:\n  mcp_server_js: "x.js"\n',
        encoding="utf-8",
    )
    if local:
        (cfg / "brain-stack.yaml").write_text(local, encoding="utf-8")


def test_load_brain_stack_example(monkeypatch: pytest.MonkeyPatch) -> None:
    """Default stack resolves the retail profile under brain/."""
    monkeypatch.delenv("BRAIN_PROFILE", raising=False)
    bs = _import_brain_stack()
    stack = bs.load_brain_stack(REPO)
    assert stack["paths"]["brain_root"] == str((REPO / "brain" / "retail").resolve())
    assert "OPENAI_API_KEY" in stack["hermes"]["sync_env_keys"]
    assert stack["llm_wiki"]["api_base_url"].startswith("http")
    assert stack.get("active_harness") == "hermes"


def test_profile_env_over_yaml_default_retail(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """BRAIN_PROFILE env beats yaml active_brain_profile; default is retail."""
    bs = _import_brain_stack()
    monkeypatch.delenv("BRAIN_PROFILE", raising=False)
    _write_stack(tmp_path)
    assert bs.resolve_brain_profile(bs.load_brain_stack(tmp_path)) == "retail"

    _write_stack(tmp_path, local="active_brain_profile: personal\n")
    stack = bs.load_brain_stack(tmp_path)
    assert stack["active_brain_profile"] == "personal"
    assert stack["paths"]["brain_root"] == str((tmp_path / "brain" / "personal").resolve())

    monkeypatch.setenv("BRAIN_PROFILE", "retail")
    stack = bs.load_brain_stack(tmp_path)
    assert stack["active_brain_profile"] == "retail"
    assert stack["paths"]["brain_root"] == str((tmp_path / "brain" / "retail").resolve())


def test_profile_paths_derive_wiki_and_obsidian(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """wiki_vault and obsidian.vault_path always follow the active profile (legacy brain/wiki ignored)."""
    bs = _import_brain_stack()
    monkeypatch.setenv("BRAIN_PROFILE", "personal")
    _write_stack(
        tmp_path,
        local='paths:\n  brain_root: "brain"\n  wiki_vault: "brain/wiki"\nobsidian:\n  vault_path: "brain/wiki"\n',
    )
    stack = bs.load_brain_stack(tmp_path)
    personal = (tmp_path / "brain" / "personal").resolve()
    assert stack["paths"]["brains_dir"] == str((tmp_path / "brain").resolve())
    assert stack["paths"]["brain_root"] == str(personal)
    assert stack["paths"]["wiki_vault"] == str(personal / "wiki")
    assert stack["obsidian"]["vault_path"] == str(personal / "wiki")


def test_unknown_profile_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Typos in BRAIN_PROFILE fail loudly with the valid list."""
    bs = _import_brain_stack()
    monkeypatch.setenv("BRAIN_PROFILE", "retial")
    _write_stack(tmp_path)
    with pytest.raises(ValueError, match="personal, retail"):
        bs.load_brain_stack(tmp_path)


def test_profile_env_cli_exports(monkeypatch: pytest.MonkeyPatch) -> None:
    """`brain_stack.py profile-env` prints exports without side effects."""
    import subprocess
    import sys

    env = {k: v for k, v in os.environ.items() if k != "BRAIN_PROFILE"}
    env["BRAIN_PROFILE"] = "personal"
    out = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "brain" / "brain_stack.py"), "profile-env"],
        capture_output=True,
        text=True,
        env=env,
        check=True,
    ).stdout
    personal = (REPO / "brain" / "personal").resolve()
    assert "export BRAIN_PROFILE=personal" in out
    assert f"export BRAIN_ROOT={personal}" in out
    assert f"export SECOND_BRAIN_WIKI_VAULT={personal / 'wiki'}" in out


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
