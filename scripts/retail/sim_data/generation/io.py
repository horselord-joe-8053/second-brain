"""Write CSV, manifest, and eval JSONL for a profile directory."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from sim_data.generation.tickets import TicketRow, issue_index_for_ticket_id, sam_code


def read_csv(path: Path) -> list[TicketRow]:
    """Load committed ``service_queries.csv`` into ``TicketRow`` (for eval-only regen)."""
    rows: list[TicketRow] = []
    with path.open(encoding="utf-8", newline="") as f:
        for rec in csv.DictReader(f):
            tid = rec["ticket_id"]
            idx = int(tid.rsplit("-", 1)[-1])
            with_code = idx % 2 == 0
            text = rec["customer_query_text"]
            code = sam_code(idx // 2) if with_code else None
            rows.append(
                TicketRow(
                    ticket_id=tid,
                    item_number=rec["item_number"],
                    store_id=rec["store_id"],
                    city=rec["city"],
                    state=rec["state"],
                    model=rec["model"],
                    status=rec["status"],
                    customer_query_text=text,
                    resolution_text=rec["resolution_text"],
                    opened_at=rec["opened_at"],
                    updated_at=rec["updated_at"],
                    closed_at=rec["closed_at"],
                    has_sam_e=bool(code),
                    sam_e=code,
                    issue_index=issue_index_for_ticket_id(tid),
                )
            )
    return rows


def write_csv(path: Path, rows: list[TicketRow]) -> None:
    """Persist historical tickets as service_queries.csv."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "ticket_id",
        "item_number",
        "store_id",
        "city",
        "state",
        "model",
        "status",
        "customer_query_text",
        "resolution_text",
        "opened_at",
        "updated_at",
        "closed_at",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(
                {
                    "ticket_id": r.ticket_id,
                    "item_number": r.item_number,
                    "store_id": r.store_id,
                    "city": r.city,
                    "state": r.state,
                    "model": r.model,
                    "status": r.status,
                    "customer_query_text": r.customer_query_text,
                    "resolution_text": r.resolution_text,
                    "opened_at": r.opened_at,
                    "updated_at": r.updated_at,
                    "closed_at": r.closed_at,
                }
            )


def write_manifest(path: Path, rows: list[TicketRow], seed: int) -> None:
    """Sidecar JSONL for provenance checks."""
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(
                json.dumps(
                    {
                        "ticket_id": r.ticket_id,
                        "model": r.model,
                        "status": r.status,
                        "seed": seed,
                        "customer_query_text": r.customer_query_text,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )


def write_eval(path: Path, eval_rows: list[dict[str, Any]]) -> None:
    """Write ticket_retrieval.jsonl eval rows."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in eval_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
