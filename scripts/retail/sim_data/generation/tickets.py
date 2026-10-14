"""Historical ticket row generation (deterministic, natural phrasing)."""

from __future__ import annotations

import random
from dataclasses import dataclass

from sim_data.generation.catalog import CITIES, DETAIL_SLOTS, ISSUES, MODELS


@dataclass
class TicketRow:
    """One historical service_queries row plus SAM-E metadata."""

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
    has_sam_e: bool
    sam_e: str | None
    issue_index: int


def sam_code(n: int) -> str:
    """Deterministic SAM-E### label from row index."""
    return f"SAM-E{100 + n:03d}"


def issue_index_for_ticket_id(ticket_id: str) -> int:
    """Map T-0042-NNNNNN to issue theme index (same rule as ``generate_historical``)."""
    i = int(ticket_id.rsplit("-", 1)[-1])
    return (i * 3 + i // 11) % len(ISSUES)


def build_stored_text(
    rng: random.Random,
    *,
    index: int,
    model: str,
    city: str,
    state: str,
    issue: str,
    with_code: bool,
    code: str | None,
) -> str:
    """Customer-facing ticket body with varied intake openings."""
    opening = rng.choice(
        (
            f"Customer reports: {issue} on {model} in {city}, {state}.",
            f"Shop note: shopper describes {issue} on their {model} ({city}).",
            f"Intake: {model} owner in {city}, {state} — {issue}.",
            f"Need help with {model}: {issue} (visited {city} store).",
        )
    )
    detail = DETAIL_SLOTS[(index + rng.randint(0, 3)) % len(DETAIL_SLOTS)]
    extra = f" Ticket context #{index}: {rng.choice(('no case', 'no drops', 'original charger', 'dual SIM'))}."
    body = f"{opening} {detail}{extra}"
    if with_code and code:
        style = rng.choice(
            (
                f" Phone displayed {code} on the service menu.",
                f" Diagnostic {code} appeared in Samsung Members.",
                f" Technician later confirmed {code} in the log.",
            )
        )
        body = f"{body} {style}"
    return body.strip()


def generate_historical(*, seed: int, count: int) -> list[TicketRow]:
    """Build ``count`` historical tickets with rotated model/city/issue themes."""
    rng = random.Random(seed)
    rows: list[TicketRow] = []
    for i in range(count):
        model = MODELS[(i // 7) % len(MODELS)]
        city, state = CITIES[i % len(CITIES)]
        issue_idx = (i * 3 + i // 11) % len(ISSUES)
        issue, fix = ISSUES[issue_idx]
        with_code = i % 2 == 0
        code = sam_code(i // 2) if with_code else None
        status = "received" if i % 17 == 16 else "resolved"
        text = build_stored_text(
            rng,
            index=i,
            model=model,
            city=city,
            state=state,
            issue=issue,
            with_code=with_code,
            code=code,
        )
        closed = "2025-01-03T10:00:00Z" if status == "resolved" else ""
        res = fix if status == "resolved" else ""
        rows.append(
            TicketRow(
                ticket_id=f"T-0042-{i:06d}",
                item_number=f"ITM-{i:08d}",
                store_id=f"ST-{i:04d}",
                city=city,
                state=state,
                model=model,
                status=status,
                customer_query_text=text,
                resolution_text=res,
                opened_at="2025-01-01T10:00:00Z",
                updated_at="2025-01-02T10:00:00Z",
                closed_at=closed,
                has_sam_e=with_code,
                sam_e=code,
                issue_index=issue_idx,
            )
        )
    return rows
