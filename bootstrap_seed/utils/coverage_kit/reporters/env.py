"""Parse portable ``COV_*`` and project-specific coverage env vars."""

from __future__ import annotations

import os
from dataclasses import dataclass


def _truthy(name: str, default: str = "0") -> bool:
    raw = os.environ.get(name, default).strip().lower()
    return raw in ("1", "true", "yes", "on")


def _int_env(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


@dataclass(frozen=True)
class CoverageEnv:
    emit_html: bool
    log_report_max_lines: int
    e2e_instrument: bool
    dashboard_port: int
    dashboard_bind: str


def load_coverage_env() -> CoverageEnv:
    """Read env; ``RESALL_COV_*`` aliases portable ``COV_*`` names."""
    if "RESALL_COV_EMIT_HTML" in os.environ:
        emit = _truthy("RESALL_COV_EMIT_HTML", "1")
    elif "COV_EMIT_HTML" in os.environ:
        emit = _truthy("COV_EMIT_HTML", "1")
    else:
        emit = True

    if "RESALL_COV_LOG_REPORT_MAX_LINES" in os.environ:
        max_lines = _int_env("RESALL_COV_LOG_REPORT_MAX_LINES", 40)
    else:
        max_lines = _int_env("COV_LOG_REPORT_MAX_LINES", 40)

    if "RESALL_COV_E2E_INSTRUMENT" in os.environ:
        e2e = _truthy("RESALL_COV_E2E_INSTRUMENT", "0")
    else:
        e2e = _truthy("COV_E2E_INSTRUMENT", "0")

    if "RESALL_COV_DASHBOARD_PORT" in os.environ:
        port = _int_env("RESALL_COV_DASHBOARD_PORT", 5199)
    else:
        port = _int_env("COV_DASHBOARD_PORT", 5199)

    bind = os.environ.get("RESALL_COV_DASHBOARD_BIND", "").strip()
    if not bind:
        bind = os.environ.get("COV_DASHBOARD_BIND", "127.0.0.1").strip() or "127.0.0.1"

    return CoverageEnv(
        emit_html=emit,
        log_report_max_lines=max_lines,
        e2e_instrument=e2e,
        dashboard_port=port,
        dashboard_bind=bind,
    )


def is_e2e_cov_enabled(*, ritual_cov: bool) -> bool:
    return ritual_cov and load_coverage_env().e2e_instrument
