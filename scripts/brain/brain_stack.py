#!/usr/bin/env python3
"""Load config/brain-stack.yaml and apply env/path helpers (no PyYAML required)."""
from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

_ENV_REF = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    """Parse a small YAML subset: nested maps, string scalars, string lists."""
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]
    list_key: str | None = None
    list_indent = 0

    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        key_line = line.strip()

        while stack and indent <= stack[-1][0]:
            stack.pop()
            list_key = None

        parent = stack[-1][1]

        if key_line.startswith("- ") and list_key is not None and indent >= list_indent:
            item = key_line[2:].strip().strip('"').strip("'")
            assert isinstance(parent.get(list_key), list)
            parent[list_key].append(item)
            continue

        if ":" not in key_line:
            continue
        key, _, rest = key_line.partition(":")
        key = key.strip()
        val = rest.strip()

        if not val:
            if key.endswith("_keys") or key in ("sync_env_keys",):
                parent[key] = []
                list_key = key
                list_indent = indent + 2
            else:
                new_map: dict[str, Any] = {}
                parent[key] = new_map
                stack.append((indent, new_map))
                list_key = None
            continue

        if val in ("|", ">"):
            parent[key] = ""
            continue

        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            parent[key] = [x.strip().strip('"').strip("'") for x in inner.split(",") if x.strip()] if inner else []
            list_key = None
            continue

        parent[key] = val.strip('"').strip("'")
        list_key = None

    return root


def expand_env_refs(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: expand_env_refs(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [expand_env_refs(v) for v in obj]
    if isinstance(obj, str):

        def repl(m: re.Match[str]) -> str:
            return os.environ.get(m.group(1), "")

        return _ENV_REF.sub(repl, obj)
    return obj


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for k, v in overlay.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def _local_stack_path(repo: Path) -> Path | None:
    for name in (
        "brain-stack.yaml",
        "brain_stack.yaml",
        "brain-stack.yml",
        "brain-stack.local.yaml",
    ):
        p = repo / "config" / name
        if p.is_file():
            return p
    return None


def load_brain_stack(repo: Path | None = None) -> dict[str, Any]:
    repo = repo or Path(__file__).resolve().parents[2]
    example = repo / "config" / "brain-stack.example.yaml"
    if not example.is_file():
        raise FileNotFoundError("missing config/brain-stack.example.yaml")
    data = _parse_simple_yaml(example.read_text(encoding="utf-8"))
    local = _local_stack_path(repo)
    if local:
        data = _deep_merge(data, _parse_simple_yaml(local.read_text(encoding="utf-8")))
    paths = data.setdefault("paths", {})
    repo_s = str(repo.resolve())
    paths.setdefault("repo_root", repo_s)
    if "brain_root" in paths and not Path(paths["brain_root"]).is_absolute():
        paths["brain_root"] = str((repo / paths["brain_root"]).resolve())
    if "wiki_vault" in paths and not Path(paths["wiki_vault"]).is_absolute():
        paths["wiki_vault"] = str((repo / paths["wiki_vault"]).resolve())
    hermes = data.setdefault("hermes", {})
    mcp_js = hermes.get("mcp_server_js", "../nu_llm_wiki/mcp-server/dist/src/index.js")
    if not Path(mcp_js).is_absolute():
        hermes["mcp_server_js"] = str((repo / mcp_js).resolve())
    obs = data.setdefault("obsidian", {})
    vault = obs.get("vault_path") or paths.get("wiki_vault")
    if vault and not Path(vault).is_absolute():
        obs["vault_path"] = str((repo / vault).resolve())
    elif vault:
        obs["vault_path"] = str(Path(vault).resolve())
    return expand_env_refs(data)


def _read_env_map(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.is_file():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, _, v = s.partition("=")
        out[k.strip()] = v.strip()
    return out


def upsert_env_file(dst: Path, src: Path, keys: list[str]) -> None:
    """Copy listed keys from src into dst; preserve other dst lines."""
    src_map = _read_env_map(src)
    if not dst.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text("", encoding="utf-8")
    lines = dst.read_text(encoding="utf-8").splitlines()
    present = set()
    new_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            k = stripped.split("=", 1)[0].strip()
            if k in keys and k in src_map:
                new_lines.append(f"{k}={src_map[k]}")
                present.add(k)
                continue
        new_lines.append(line)
    for k in keys:
        if k in src_map and k not in present:
            new_lines.append(f"{k}={src_map[k]}")
    dst.write_text("\n".join(new_lines).rstrip() + "\n", encoding="utf-8")


def collect_hermes_secrets(stack: dict[str, Any], repo: Path) -> dict[str, str]:
    """Secrets for Hermes: brain-stack.yaml `secrets:` first, then repo `.env` fallback."""
    keys = list(stack.get("hermes", {}).get("sync_env_keys") or [])
    raw = stack.get("secrets") or {}
    out: dict[str, str] = {}
    if isinstance(raw, dict):
        for k in keys:
            v = raw.get(k)
            if isinstance(v, str) and v.strip():
                out[k] = v.strip()
    env_fallback = _read_env_map(repo / ".env")
    for k in keys:
        if k not in out and env_fallback.get(k):
            out[k] = env_fallback[k]
    return out


def upsert_stack_secret(repo: Path, key: str, value: str) -> None:
    """Update gitignored config/brain-stack.yaml secrets map (create from example if needed)."""
    local = _local_stack_path(repo) or (repo / "config" / "brain-stack.yaml")
    if not local.is_file():
        example = repo / "config" / "brain-stack.example.yaml"
        local.write_text(
            example.read_text(encoding="utf-8") + "\nsecrets:\n",
            encoding="utf-8",
        )
    text = local.read_text(encoding="utf-8")
    needle = f"{key}:"
    lines = text.splitlines()
    if any(line.strip().startswith(needle) for line in lines):
        new_lines = []
        for line in lines:
            if line.strip().startswith(needle):
                indent = line[: len(line) - len(line.lstrip())]
                new_lines.append(f"{indent}{key}: \"{value}\"")
            else:
                new_lines.append(line)
        local.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        return
    if "secrets:" not in text:
        text = text.rstrip() + "\n\nsecrets:\n"
    text = text.rstrip() + f'\n  {key}: "{value}"\n'
    local.write_text(text, encoding="utf-8")


def apply_hermes_model_config(stack: dict[str, Any]) -> None:
    """Write model.provider / model.default from brain-stack hermes.chat_* (if hermes CLI present)."""
    hermes = stack.get("hermes") or {}
    provider = (hermes.get("chat_provider") or "").strip()
    model = (hermes.get("chat_model") or "").strip()
    if not provider and not model:
        return
    if not shutil.which("hermes"):
        return
    if provider:
        subprocess.run(
            ["hermes", "config", "set", "model.provider", provider],
            check=False,
            capture_output=True,
        )
    if model:
        subprocess.run(
            ["hermes", "config", "set", "model.default", model],
            check=False,
            capture_output=True,
        )


def verify_stack_config(repo: Path) -> list[str]:
    """Return list of issues (empty if OK). Does not print secret values."""
    issues: list[str] = []
    try:
        stack = load_brain_stack(repo)
    except FileNotFoundError as e:
        return [str(e)]
    if not _local_stack_path(repo):
        issues.append("missing config/brain-stack.yaml — copy from config/brain-stack.example.yaml")
    hermes = stack.get("hermes") or {}
    if not hermes:
        issues.append("brain-stack missing hermes section")
        return issues
    keys = list(hermes.get("sync_env_keys") or [])
    optional_keys = frozenset(
        hermes.get("sync_env_keys_optional") or ["OPENROUTER_API_KEY", "GOOGLE_API_KEY"]
    )
    env_map = _read_env_map(repo / ".env")
    secrets = collect_hermes_secrets(stack, repo)
    if not (repo / ".env").is_file():
        issues.append("missing repo .env — copy from .env.example")
    for k in keys:
        if k in optional_keys:
            continue
        if k not in secrets:
            issues.append(f".env missing or empty: {k}")
    provider = (hermes.get("chat_provider") or "").strip().lower()
    if provider == "gemini" and not any(secrets.get(x) for x in ("GEMINI_API_KEY", "GOOGLE_API_KEY")):
        issues.append("gemini provider requires GEMINI_API_KEY or GOOGLE_API_KEY in .env")
    if not hermes.get("chat_provider"):
        issues.append("brain-stack hermes.chat_provider unset (e.g. gemini)")
    if not hermes.get("chat_model"):
        issues.append("brain-stack hermes.chat_model unset (e.g. gemini-3.0-flash)")
    mcp_js = Path(str(hermes.get("mcp_server_js", "")))
    if not mcp_js.is_file():
        issues.append(f"MCP server not built: {mcp_js}")
    # GEMINI_MODEL in .env is not used by Hermes — informational
    if env_map.get("GEMINI_MODEL") and not hermes.get("chat_model"):
        issues.append("GEMINI_MODEL in .env is ignored — set hermes.chat_model in brain-stack.yaml")
    return issues


def apply_hermes_env(stack: dict[str, Any], repo: Path) -> int:
    hermes_env = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes")) / ".env"
    secrets = collect_hermes_secrets(stack, repo)
    if not secrets:
        return 0
    tmp = repo / ".brain-stack-secrets.tmp.env"
    try:
        tmp.write_text("".join(f"{k}={v}\n" for k, v in secrets.items()), encoding="utf-8")
        upsert_env_file(hermes_env, tmp, list(secrets.keys()))
    finally:
        if tmp.is_file():
            tmp.unlink()
    return len(secrets)


def main() -> int:
    repo = Path(__file__).resolve().parents[2]
    stack = load_brain_stack(repo)
    n = apply_hermes_env(stack, repo)
    if n:
        print(f"brain_stack: applied {n} secret(s) from stack → {Path.home() / '.hermes' / '.env'} (not printed)")
    mcp = stack["hermes"]["mcp_server_js"]
    print(f"export NU_LLM_WIKI_MCP={mcp}")
    print(f"export SECOND_BRAIN_WIKI_VAULT={stack.get('obsidian', {}).get('vault_path', '')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
