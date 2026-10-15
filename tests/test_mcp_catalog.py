"""Shared MCP catalog (config/second-brain.mcp-servers.yaml) via brain_stack."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_mcp_catalog_resolves_repo_paths_not_home(monkeypatch) -> None:
    """Filesystem MCP root is the active brain-profile dir (default retail), never a home path."""
    import sys

    monkeypatch.delenv("BRAIN_PROFILE", raising=False)
    sys.path.insert(0, str(REPO / "scripts" / "brain"))
    from brain_stack import load_mcp_servers_catalog

    catalog = load_mcp_servers_catalog(REPO)
    assert "llm_wiki" in catalog
    assert "second_brain_fs" in catalog
    assert "retail_pg" in catalog

    mcp_js = catalog["llm_wiki"]["args"][0]
    brain_root = catalog["second_brain_fs"]["args"][-1]

    assert Path(mcp_js).is_absolute()
    assert Path(brain_root).is_absolute()
    assert brain_root == str((REPO / "brain" / "retail").resolve())

    catalog_text = (REPO / "config" / "second-brain.mcp-servers.yaml").read_text(encoding="utf-8")
    assert "/Users/" not in catalog_text


def test_format_mcp_servers_block_includes_both_servers() -> None:
    import sys

    sys.path.insert(0, str(REPO / "scripts" / "brain"))
    from brain_stack import format_mcp_servers_block, load_mcp_servers_catalog

    block = format_mcp_servers_block(load_mcp_servers_catalog(REPO))
    assert block.startswith("mcp_servers:")
    assert "llm_wiki:" in block
    assert "second_brain_fs:" in block
    assert "LLM_WIKI_API_TOKEN" in block
