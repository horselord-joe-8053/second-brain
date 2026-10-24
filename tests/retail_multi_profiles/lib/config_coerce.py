"""Strict coercion for harness YAML / env scalars (simple parser yields strings)."""

from __future__ import annotations

from typing import Any


def coerce_bool(value: Any, *, default: bool = False) -> bool:
    """Parse YAML/env booleans; never treat non-empty strings as True except true/1/yes."""
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    s = str(value).strip().lower()
    if s in ("true", "1", "yes", "on"):
        return True
    if s in ("false", "0", "no", "off", ""):
        return False
    return default


def coerce_int(value: Any, *, default: int = 0) -> int:
    """Parse integer scalars from merged config."""
    if value is None:
        return default
    if isinstance(value, int):
        return value
    try:
        return int(str(value).strip())
    except ValueError:
        return default
