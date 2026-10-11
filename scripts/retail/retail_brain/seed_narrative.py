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

_DIAG_CODES: Tuple[str, ...] = tuple(f"SAM-E{i:03d}" for i in range(200))

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
    diagnostic_code: str


def _rng(seed: int, index: int) -> random.Random:
    return random.Random(f"{seed}:{index}")


def narrative_parts(
    *,
    seed: int,
    index: int,
    market: str | None = None,
) -> NarrativeParts:
    """Pair indices (0,1), (2,3), … share identical symptom prose; codes differ (eval distractors)."""
    cities = cities_for_market(market)
    issues = issues_for_market(market)
    pair_id = index // 2
    city, state = cities[pair_id % len(cities)]
    from retail_brain.models import MODELS

    model = MODELS[pair_id % len(MODELS)]
    issue, fix = issues[pair_id % len(issues)]
    code = _DIAG_CODES[(seed * 997 + index * 17) % len(_DIAG_CODES)]
    return NarrativeParts(
        issue=issue,
        fix=fix,
        model=model,
        city=city,
        state=state,
        detail_when=_WHEN_STARTED[(seed + pair_id * 7) % len(_WHEN_STARTED)],
        detail_symptom=_SYMPTOM_EXTRA[(seed + pair_id * 13) % len(_SYMPTOM_EXTRA)],
        caller_name=_FIRST_NAMES[index % len(_FIRST_NAMES)],
        diagnostic_code=code,
    )


def format_stored_customer_query(
    parts: NarrativeParts,
    *,
    market: str | None = None,
    index: int | None = None,
) -> str:
    """Even pair index: CRM-style stored prose. Odd index: intake-shaped twin (same symptoms, other code)."""
    tech = f"Technician log: diagnostic code {parts.diagnostic_code}."
    twin_mirror = index is not None and index % 2 == 1
    if twin_mirror:
        body = (
            f"Need help: {parts.model}, {parts.issue}. "
            f"{parts.detail_when} {parts.detail_symptom} "
        )
    else:
        prefix = market_profile(market)["customer_query_prefix"]
        body = (
            f"{prefix}{parts.issue} on {parts.model} in {parts.city}, {parts.state}. "
            f"{parts.detail_when} {parts.detail_symptom} "
        )
    return f"{body}{tech}"


def format_eval_query(parts: NarrativeParts, *, market: str | None = None) -> str:
    tpl = market_profile(market)["eval_query_template"]
    return tpl.format(
        caller=parts.caller_name,
        city=parts.city,
        model=parts.model,
        issue=parts.issue,
        detail=parts.detail_symptom,
    )


def format_eval_query_with_code(parts: NarrativeParts, *, market: str | None = None) -> str:
    """Intake mirrors screenshot: model + symptoms + explicit error code (fair to vector + lexical)."""
    return (
        f"Need help: {parts.model}, {parts.issue}. {parts.detail_symptom} "
        f"Error code {parts.diagnostic_code}."
    )


def ticket_index_from_id(ticket_id: str) -> int:
    m = _TICKET_INDEX.search(ticket_id.strip())
    if not m:
        raise ValueError(f"cannot parse ticket index from {ticket_id!r}")
    return int(m.group(1))


def parts_for_ticket_id(ticket_id: str, *, seed: int, market: str | None = None) -> NarrativeParts:
    return narrative_parts(seed=seed, index=ticket_index_from_id(ticket_id), market=market)
