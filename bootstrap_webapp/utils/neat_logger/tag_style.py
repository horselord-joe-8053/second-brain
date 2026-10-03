"""Load ``config/logging.yaml`` tag colors and apply tag-only ANSI styling."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from .neat_logger import NC, _intrinsic_repo_root, _load_yaml_dict

# 16-color + 256-color names used in config/logging.yaml.
_COLOR_CODES: dict[str, str] = {
    "red": "\033[0;31m",
    "green": "\033[0;32m",
    "yellow": "\033[0;33m",
    "cyan": "\033[0;36m",
    "magenta": "\033[0;35m",
    "blue": "\033[0;34m",
    "purple": "\033[38;5;129m",
    "orange": "\033[38;5;208m",
}

_DEFAULT_EXACT: dict[str, str] = {
    "[LLM-REQUEST]": "red",
    "[LLM-RESPONSE]": "green",
    "[LLM-USAGE][RECEIVED]": "green",
    "[LLM-USAGE][ESTIMATED]": "green",
    "[LLM-VERIFY-LOCAL]": "yellow",
    "[LLM-VERIFY-FINAL]": "yellow",
    "[VERIFY-SELF-CONTRADICT]": "yellow",
    "[LLM-ERROR]": "red",
    "[LLM-PROMPT-SIZE]": "cyan",
    "[PARAGRAPH-SENSE-ANCHOR]": "magenta",
    "[PARAGRAPH-HOST-LEADING]": "cyan",
}
_DEFAULT_PREFIX: dict[str, str] = {
    "[EXPGTEST_": "purple",
    "[PWLAD_": "orange",
}

_CACHE: tuple[dict[str, str], dict[str, str]] | None = None


def _repo_root() -> Path:
    rr = os.getenv("REPO_ROOT", "").strip()
    if rr:
        return Path(rr).expanduser().resolve()
    return _intrinsic_repo_root()


def _fallback_yaml_path() -> Path:
    return Path(__file__).resolve().parent / "neat_logger_fallback_config.yaml"


def _resolve_project_log_config_path() -> Path | None:
    fallback = _load_yaml_dict(_fallback_yaml_path())
    rel = str(fallback.get("project_log_config", "")).strip()
    if not rel:
        return None
    p = Path(rel)
    return p.resolve() if p.is_absolute() else (_repo_root() / p).resolve()


def _color_code(name: str) -> str:
    key = str(name).strip().lower()
    return _COLOR_CODES.get(key, NC)


def _parse_styles(raw: dict[str, Any]) -> tuple[dict[str, str], dict[str, str]]:
    block = raw.get("tag_styles") if isinstance(raw.get("tag_styles"), dict) else {}
    exact_raw = block.get("exact") if isinstance(block.get("exact"), dict) else {}
    prefix_raw = block.get("prefix") if isinstance(block.get("prefix"), dict) else {}

    exact: dict[str, str] = {}
    for tag, color_name in {**_DEFAULT_EXACT, **exact_raw}.items():
        exact[str(tag)] = _color_code(str(color_name))

    prefix: dict[str, str] = {}
    for pref, color_name in {**_DEFAULT_PREFIX, **prefix_raw}.items():
        prefix[str(pref)] = _color_code(str(color_name))

    return exact, prefix


def reload_tag_styles() -> None:
    """Clear cached yaml styles (tests + ``reload_config``)."""
    global _CACHE
    _CACHE = None


def _load_styles() -> tuple[dict[str, str], dict[str, str]]:
    global _CACHE
    if _CACHE is not None:
        return _CACHE

    path = _resolve_project_log_config_path()
    raw: dict[str, Any] = _load_yaml_dict(path) if path and path.is_file() else {}
    _CACHE = _parse_styles(raw)
    return _CACHE


def styled_ansi_in_file() -> bool:
    """True when ANSI tag colors should be written to log files."""
    path = _resolve_project_log_config_path()
    raw: dict[str, Any] = _load_yaml_dict(path) if path and path.is_file() else {}
    for key in ("ansi_in_file_env", "legacy_ansi_in_file_env"):
        env_key = str(raw.get(key, "")).strip()
        if env_key and str(os.getenv(env_key, "")).strip().lower() in {"1", "true", "yes"}:
            return True
    if str(os.getenv("NEAT_LOGGER_STYLED_ANSI_IN_FILE", "")).strip().lower() in {
        "1",
        "true",
        "yes",
    }:
        return True
    return str(os.getenv("NEAT_LOGGER_LLM_ANSI_IN_FILE", "0")).strip().lower() in {
        "1",
        "true",
        "yes",
    }


def should_style_tty() -> bool:
    isatty = getattr(sys.stdout, "isatty", None)
    tty = bool(isatty()) if callable(isatty) else False
    return tty or bool(os.environ.get("PGLPL_FORCE_COLOR"))


def style_configured_tags(msg: str) -> str:
    """Wrap configured bracket tags in ANSI; body text stays plain."""
    if "[" not in msg:
        return msg

    exact, prefix = _load_styles()
    exact_tags = sorted(exact.keys(), key=len, reverse=True)
    prefix_items = sorted(prefix.items(), key=lambda item: len(item[0]), reverse=True)

    out: list[str] = []
    i = 0
    n = len(msg)
    while i < n:
        if msg[i] != "[":
            out.append(msg[i])
            i += 1
            continue

        matched = False
        for tag in exact_tags:
            if msg.startswith(tag, i):
                code = exact[tag]
                out.append(f"{code}{tag}{NC}")
                i += len(tag)
                matched = True
                break
        if matched:
            continue

        end = msg.find("]", i)
        if end < 0:
            out.append(msg[i:])
            break

        token = msg[i : end + 1]
        styled: str | None = None
        for pref, code in prefix_items:
            if token.startswith(pref):
                styled = f"{code}{token}{NC}"
                break
        out.append(styled if styled else token)
        i = end + 1

    return "".join(out)


def styled_tty_and_file(msg: str) -> tuple[str, str]:
    """Return ``(tty_msg, file_msg)`` mirroring pre-YAML semantics.

    Tag ANSI is computed independently of TTY: ``api.log`` can carry colors when
    ``NEAT_LOGGER_*_ANSI_IN_FILE`` is set even though uvicorn workers are non-TTY.
    """
    styled = style_configured_tags(msg)
    tty = styled if should_style_tty() else msg
    file_msg = styled if styled_ansi_in_file() else msg
    return tty, file_msg
