"""Retail pytest defaults — isolate fault-code prefix from operator shell env."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _clear_retail_fault_prefix_for_tests(monkeypatch: pytest.MonkeyPatch) -> None:
    """``RETAIL_FAULT_CODE_PREFIX=FRU-E`` in the shell breaks SAM-E unit tests (see war_stories)."""
    monkeypatch.delenv("RETAIL_FAULT_CODE_PREFIX", raising=False)
