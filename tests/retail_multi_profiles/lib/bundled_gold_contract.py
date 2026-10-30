"""B20 retrieval gold must match ticket leg (resolved-only search pool)."""

from __future__ import annotations

import csv
from pathlib import Path


def load_ticket_status_by_id(csv_path: Path) -> dict[str, str]:
    """Map ticket_id → status from sim service_queries.csv."""
    out: dict[str, str] = {}
    with csv_path.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            tid = (row.get("ticket_id") or row.get("id") or "").strip()
            if tid:
                out[tid] = (row.get("status") or "").strip().lower()
    return out


def assert_expected_tickets_resolved(
    expected_ticket_ids: tuple[str, ...] | list[str],
    status_by_id: dict[str, str],
    *,
    question_id: str = "",
) -> None:
    """Fail when a retrieval label is missing or not resolved (ticket_leg never returns open rows)."""
    for tid in expected_ticket_ids:
        st = status_by_id.get(tid)
        if st is None:
            raise AssertionError(f"{question_id} unknown ticket {tid} in corpus")
        if st != "resolved":
            raise AssertionError(
                f"{question_id} expected_ticket_ids {tid} has status {st!r}; "
                "retrieval gold must be resolved (see REFACTOR_B20_RESOLVED_GOLD_LABELS.md)"
            )
