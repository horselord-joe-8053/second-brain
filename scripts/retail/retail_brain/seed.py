"""Deterministic synthetic ticket and sales generation."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, List, TextIO

from retail_brain.market import cities_for_market, issues_for_market, market_profile
from retail_brain.models import MODELS, STATUSES, RESOLVED


@dataclass
class TicketRecord:
    ticket_id: str
    item_number: str
    store_id: str
    city: str
    state: str
    model: str
    status: str
    customer_query_text: str
    resolution_text: str
    opened_at: str
    updated_at: str
    closed_at: str


SERVICE_FIELDNAMES = [
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


def generate_tickets(*, count: int, seed: int = 42, market: str | None = None) -> List[TicketRecord]:
    profile = market_profile(market)
    prefix = profile["customer_query_prefix"]
    cities = cities_for_market(market)
    issues = issues_for_market(market)
    rows: List[TicketRecord] = []
    for i in range(count):
        city, state = cities[i % len(cities)]
        model = MODELS[i % len(MODELS)]
        issue, fix = issues[i % len(issues)]
        status = RESOLVED if i % 4 != 0 else STATUSES[i % len(STATUSES)]
        tid = f"T-{seed:04d}-{i:06d}"
        item_number = f"ITM-{i:08d}"
        rows.append(
            TicketRecord(
                ticket_id=tid,
                item_number=item_number,
                store_id=f"ST-{i % 120:04d}",
                city=city,
                state=state,
                model=model,
                status=status,
                customer_query_text=(
                    f"{prefix}{issue} on {model}. Case ref {item_number} / {tid}."
                ),
                resolution_text=fix if status == RESOLVED else "",
                opened_at="2025-01-01T10:00:00Z",
                updated_at="2025-01-02T10:00:00Z",
                closed_at="2025-01-03T10:00:00Z" if status == RESOLVED else "",
            )
        )
    return rows


def write_service_csv(path: Path, rows: List[TicketRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SERVICE_FIELDNAMES)
        w.writeheader()
        for r in rows:
            w.writerow({k: getattr(r, k) for k in SERVICE_FIELDNAMES})


def write_manifest(path: Path, rows: List[TicketRecord], *, seed: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            rec = {
                "ticket_id": r.ticket_id,
                "model": r.model,
                "status": r.status,
                "seed": seed,
                "customer_query_text": r.customer_query_text,
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def iter_manifest(path: Path) -> Iterator[dict]:
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)
