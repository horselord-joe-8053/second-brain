"""FRU US historical ticket generation (YAML + customer seed)."""

from __future__ import annotations

import json
import random
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

from retail_brain.company_profile import CompanyProfile, FruIssue, cached_company_profile

from sim_data.generation.tickets import TicketRow

_SEED_CUSTOMERS = Path(__file__).resolve().parents[1] / "seed" / "fru_customers.jsonl"
_BANNED = ("Galaxy", "SAM-E", "Melbourne", "Sydney", "Brisbane", "CUST")


def load_customers(path: Path | None = None) -> list[dict[str, str]]:
    """Load committed customer pool JSONL."""
    p = path or _SEED_CUSTOMERS
    rows: list[dict[str, str]] = []
    with p.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def fru_code(n: int, prefix: str = "FRU-E") -> str:
    """Deterministic FRU-E### label from sequential index."""
    return f"{prefix}{100 + n:03d}"


def _store_id(store_name: str) -> str:
    slug = store_name.lower().replace(" ", "-").replace("'", "")
    return f"store-{slug}"


def _weighted_customer_pick(
    rng: random.Random,
    customers: list[dict[str, str]],
    visit_count: Counter[str],
) -> dict[str, str]:
    """Prefer customers with fewer tickets so repeats spread without JSONL order bias."""
    weights = [1.0 / (1 + visit_count[c["customer_id"]]) for c in customers]
    return rng.choices(customers, weights=weights, k=1)[0]


def _pick_issue(rng: random.Random, profile: CompanyProfile, sku: str) -> FruIssue:
    allowed = profile.issues_for_model(sku)
    weights = [i.weight for i in allowed]
    return rng.choices(allowed, weights=weights, k=1)[0]


def _timestamps(rng: random.Random, sales_date: str, index: int) -> tuple[str, str, str]:
    base = datetime.strptime(sales_date, "%Y-%m-%d")
    offset_days = rng.randint(7, 540)
    opened = base + timedelta(days=offset_days)
    updated = opened + timedelta(hours=rng.randint(2, 72))
    closed = updated + timedelta(hours=rng.randint(1, 48))
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    return opened.strftime(fmt), updated.strftime(fmt), closed.strftime(fmt)


def build_fru_stored_text(
    rng: random.Random,
    *,
    profile: CompanyProfile,
    index: int,
    customer: dict[str, str],
    issue: FruIssue,
    with_code: bool,
    code: str | None,
) -> str:
    """Customer-facing ticket body for a FRU service row."""
    model = customer["fridge_model"]
    city = customer["city"]
    state = customer["state"]
    store = customer["store_name"]
    opening_tpl = rng.choice(profile.intake_openings)
    opening = opening_tpl.format(
        symptom=issue.symptom,
        model=model,
        city=city,
        state=state,
        store=store,
    )
    detail = profile.detail_slots[(index + rng.randint(0, 3)) % len(profile.detail_slots)]
    extra = f" Ticket context #{index}: {rng.choice(('no power blinks', 'original install', 'extended warranty', 'second visit'))}."
    body = f"{opening} {detail}{extra}"
    if with_code and code:
        style = rng.choice(profile.code_phrasings).format(code=code)
        body = f"{body} {style}"
    return body.strip()


def generate_fru_historical(
    *,
    seed: int,
    count: int,
    profile: CompanyProfile | None = None,
    customers: list[dict[str, str]] | None = None,
) -> list[TicketRow]:
    """Build ``count`` FRU historical tickets tied to the customer pool."""
    profile = profile or cached_company_profile()
    customers = customers or load_customers()
    rng = random.Random(seed)
    code_seq = 0
    rows: list[TicketRow] = []
    seen_customers: set[str] = set()
    visit_count: Counter[str] = Counter()
    shuffled = list(customers)
    rng.shuffle(shuffled)

    for i in range(count):
        if i < len(shuffled):
            cust = shuffled[i]
        else:
            cust = _weighted_customer_pick(rng, shuffled, visit_count)
        seen_customers.add(cust["customer_id"])
        visit_count[cust["customer_id"]] += 1
        issue = _pick_issue(rng, profile, cust["fridge_model"])
        issue_index = next(i for i, x in enumerate(profile.issues) if x.key == issue.key)
        with_code = rng.random() < 0.5
        code: str | None = None
        if with_code:
            code = fru_code(code_seq, profile.fault_code_prefix)
            code_seq += 1
        text = build_fru_stored_text(
            rng,
            profile=profile,
            index=i,
            customer=cust,
            issue=issue,
            with_code=with_code,
            code=code,
        )
        for bad in _BANNED:
            if bad in text:
                raise ValueError(f"banned token {bad!r} in generated text")
        opened, updated, closed = _timestamps(rng, cust["sales_date"], i)
        status = "open" if rng.random() < 0.06 else "resolved"
        closed_at = "" if status == "open" else closed
        ticket_id = f"T-0042-{100000 + i:06d}"
        item_number = f"ITM-{100000 + i:06d}"
        rows.append(
            TicketRow(
                ticket_id=ticket_id,
                item_number=item_number,
                store_id=_store_id(cust["store_name"]),
                city=cust["city"],
                state=cust["state"],
                model=cust["fridge_model"],
                status=status,
                customer_query_text=text,
                resolution_text=issue.resolution,
                opened_at=opened,
                updated_at=updated,
                closed_at=closed_at,
                has_sam_e=bool(code),
                sam_e=code,
                issue_index=issue_index,
                customer_id=cust["customer_id"],
                issue_key=issue.key,
                fault_code=code,
            )
        )
    if count >= len(customers) and len(seen_customers) < len(customers):
        raise ValueError("not every customer received at least one ticket")
    if count >= len(customers):
        expected_stores = {_store_id(c["store_name"]) for c in customers}
        ticket_stores = {r.store_id for r in rows}
        if not expected_stores.issubset(ticket_stores):
            missing = expected_stores - ticket_stores
            raise ValueError(f"stores missing from tickets: {sorted(missing)[:5]}")
    return rows
