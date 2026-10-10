"""Deterministic customer-facing ticket prose (no operational IDs in text)."""

from __future__ import annotations

import random
import re
from dataclasses import dataclass
from typing import List, Tuple

from retail_brain.market import cities_for_market, issues_for_market, market_profile

_TICKET_INDEX = re.compile(r"-(\d+)$")

# Pools keyed by RNG draw — keeps CI stable for fixed (seed, i).
_WHEN_STARTED: Tuple[str, ...] = (
    "Started after the latest software update.",
    "Began a few days ago without any drop damage.",
    "Only happens since they installed a new banking app.",
    "First noticed it last weekend during travel.",
    "Issue comes and goes but is getting worse.",
    "Started right after the phone got warm in a car.",
    "They rebooted twice but it keeps coming back.",
    "Happens every morning when they unplug the charger.",
)

_SYMPTOM_EXTRA: Tuple[str, ...] = (
    "Screen stays black but the phone vibrates for calls.",
    "Battery drops from full to half within two hours.",
    "No SIM detected even after reseating the tray.",
    "Safe mode does not fix the display.",
    "Mobile data drops when switching to 5G.",
    "Camera app crashes whenever they open it.",
    "Fingerprint reader fails after the patch.",
    "Bluetooth pairing fails in the car every time.",
)

_FIRST_NAMES: Tuple[str, ...] = (
    "Alex",
    "Jordan",
    "Sam",
    "Casey",
    "Riley",
    "Morgan",
    "Taylor",
    "Jamie",
)


@dataclass(frozen=True)
class NarrativeParts:
    issue: str
    fix: str
    model: str
    city: str
    state: str
    detail_when: str
    detail_symptom: str
    caller_name: str


def _rng(seed: int, index: int) -> random.Random:
    return random.Random(f"{seed}:{index}")


def narrative_parts(
    *,
    seed: int,
    index: int,
    market: str | None = None,
) -> NarrativeParts:
    cities = cities_for_market(market)
    issues = issues_for_market(market)
    city, state = cities[index % len(cities)]
    from retail_brain.models import MODELS

    model = MODELS[index % len(MODELS)]
    issue, fix = issues[index % len(issues)]
    r = _rng(seed, index)
    return NarrativeParts(
        issue=issue,
        fix=fix,
        model=model,
        city=city,
        state=state,
        detail_when=r.choice(_WHEN_STARTED),
        detail_symptom=r.choice(_SYMPTOM_EXTRA),
        caller_name=r.choice(_FIRST_NAMES),
    )


def format_stored_customer_query(parts: NarrativeParts, *, market: str | None = None) -> str:
    prefix = market_profile(market)["customer_query_prefix"]
    return (
        f"{prefix}{parts.issue} on {parts.model} in {parts.city}, {parts.state}. "
        f"{parts.detail_when} {parts.detail_symptom}"
    )


def format_eval_query(parts: NarrativeParts, *, market: str | None = None) -> str:
    tpl = market_profile(market)["eval_query_template"]
    return tpl.format(
        caller=parts.caller_name,
        city=parts.city,
        model=parts.model,
        issue=parts.issue,
        detail=parts.detail_symptom,
    )


def ticket_index_from_id(ticket_id: str) -> int:
    m = _TICKET_INDEX.search(ticket_id.strip())
    if not m:
        raise ValueError(f"cannot parse ticket index from {ticket_id!r}")
    return int(m.group(1))


def parts_for_ticket_id(ticket_id: str, *, seed: int, market: str | None = None) -> NarrativeParts:
    return narrative_parts(seed=seed, index=ticket_index_from_id(ticket_id), market=market)
