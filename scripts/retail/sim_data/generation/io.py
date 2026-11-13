"""Write CSV, manifest, and eval JSONL for a profile directory."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from sim_data.generation.tickets import TicketRow, issue_index_for_ticket_id, sam_code


def read_manifest(path: Path) -> dict[str, dict[str, Any]]:
    """Load ticket_id → manifest record (issue_key, fault_code, etc.)."""
    out: dict[str, dict[str, Any]] = {}
    if not path.is_file():
        return out
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            out[str(obj["ticket_id"])] = obj
    return out


def read_csv(path: Path, *, manifest_path: Path | None = None) -> list[TicketRow]:
    """Load committed ``service_queries.csv`` into ``TicketRow`` (for eval-only regen)."""
    manifest = read_manifest(manifest_path) if manifest_path else {}
    rows: list[TicketRow] = []
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        has_customer = "customer_id" in fields
        for rec in reader:
            tid = rec["ticket_id"]
            meta = manifest.get(tid, {})
            issue_key = meta.get("issue_key") or rec.get("issue_key")
            fault_code = meta.get("fault_code") or rec.get("fault_code")
            if manifest and issue_key is None:
                raise ValueError(f"manifest missing issue_key for {tid}")
            if not manifest and not has_customer:
                idx = int(tid.rsplit("-", 1)[-1])
                with_code = idx % 2 == 0
                code = sam_code(idx // 2) if with_code else None
                issue_index = issue_index_for_ticket_id(tid)
            else:
                code = fault_code
                with_code = bool(code)
                issue_index = 0
            rows.append(
                TicketRow(
                    ticket_id=tid,
                    item_number=rec["item_number"],
                    store_id=rec["store_id"],
                    city=rec["city"],
                    state=rec["state"],
                    model=rec["model"],
                    status=rec["status"],
                    customer_query_text=rec["customer_query_text"],
                    resolution_text=rec["resolution_text"],
                    opened_at=rec["opened_at"],
                    updated_at=rec["updated_at"],
                    closed_at=rec.get("closed_at") or "",
                    has_sam_e=with_code,
                    sam_e=code,
                    issue_index=issue_index,
                    customer_id=rec.get("customer_id") if has_customer else None,
                    issue_key=str(issue_key) if issue_key else None,
                    fault_code=str(fault_code) if fault_code else None,
                )
            )
    return rows


def write_csv(path: Path, rows: list[TicketRow]) -> None:
    """Persist historical tickets as service_queries.csv."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "ticket_id",
        "customer_id",
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
                    "customer_id": r.customer_id or "",
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
    """Sidecar JSONL for provenance checks and eval-only regen."""
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
                        "issue_key": r.issue_key,
                        "fault_code": r.fault_code or r.sam_e,
                        "customer_id": r.customer_id,
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
