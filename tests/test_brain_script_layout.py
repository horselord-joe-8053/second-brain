"""Phase 14: Hermes entrypoints live under scripts/brain/adapters/hermes/, not root shims."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BRAIN = REPO / "scripts" / "brain"

FORBIDDEN_ROOT_NAMES = {
    "setup-hermes.sh",
    "setup-hermes-mcp.sh",
    "setup-hermes-messaging.sh",
    "setup-hermes-desktop.sh",
    "setup-hermes-skills.sh",
    "start-hermes.sh",
    "stop-hermes.sh",
    "merge-hermes-wiring.py",
    "merge-hermes-mcp-config.py",
    "merge-hermes-skills-config.py",
    "hermes-env.sh",
    "hermes-preflight.sh",
    "install-and-start-hermes-desktop.sh",
    "smoke-integrated.sh",
    "acceptance-automated.sh",
}


def test_no_hermes_shim_files_at_scripts_brain_root() -> None:
    present = sorted(n for n in FORBIDDEN_ROOT_NAMES if (BRAIN / n).exists())
    assert present == [], f"remove wrapper shims (use adapters/hermes/): {present}"


def test_hermes_adapter_setup_harness_exists() -> None:
    p = BRAIN / "adapters" / "hermes" / "setup-harness.sh"
    assert p.is_file()


def test_harness_runbooks_exist() -> None:
    assert (REPO / "docs_manual_gen" / "RUNBOOK_HARNESS_HERMES.md").is_file()
    assert (REPO / "docs_manual_gen" / "RUNBOOK_HARNESS_OPENCLAW.md").is_file()
