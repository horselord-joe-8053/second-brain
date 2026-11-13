"""Load ``TicketRow`` lists from generated CSV for offline ``hybrid_search`` / ``eval_harness``."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import List

from retail_brain.hybrid_search import TicketRow
from retail_brain.seed import SERVICE_FIELDNAMES


def load_ticket_rows(csv_path: Path) -> List[TicketRow]:
    """Parse service CSV into ``TicketRow`` objects (columns from ``SERVICE_FIELDNAMES``)."""
    rows: List[TicketRow] = []
    with csv_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for rec in reader:
            rows.append(
                TicketRow(
                    ticket_id=rec["ticket_id"],
                    model=rec["model"],
                    status=rec["status"],
                    customer_query_text=rec["customer_query_text"],
                    resolution_text=rec.get("resolution_text") or "",
                )
            )
    return rows
