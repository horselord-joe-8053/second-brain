"""Pick eval gold tickets that stay retrievable at scale (low corpus collision)."""

from __future__ import annotations

import random
from collections import Counter
from typing import Callable

from sim_data.generation.catalog import DETAIL_SLOTS, ISSUES
from sim_data.generation.tickets import TicketRow


def issue_label(row: TicketRow) -> str:
    """Canonical issue phrase for a historical row."""
    return ISSUES[row.issue_index][0]


def signature_mci(row: TicketRow) -> tuple[str, str, int]:
    """Model + city + issue index — coarse collision key."""
    return (row.model, row.city, row.issue_index)


def rich_signature(row: TicketRow) -> tuple[str, str, int, str]:
    """Model/city/issue plus the detail sentence in stored intake (usually unique)."""
    return signature_mci(row) + (detail_phrase_from_stored(row) or "",)


def build_signature_counts(resolved: list[TicketRow]) -> Counter[tuple[str, str, int]]:
    """How many resolved tickets share each model/city/issue triple."""
    return Counter(signature_mci(r) for r in resolved)


def build_rich_signature_counts(resolved: list[TicketRow]) -> Counter[tuple[str, str, int, str]]:
    """Collision counts including intake detail phrase."""
    return Counter(rich_signature(r) for r in resolved)


def detail_phrase_from_stored(row: TicketRow) -> str | None:
    """Return the detail slot sentence copied into ``customer_query_text``, if any."""
    text = row.customer_query_text
    for slot in DETAIL_SLOTS:
        if slot in text:
            return slot
    return None


def _sorted_pool(
    pool: list[TicketRow],
    sig_counts: Counter,
    rng: random.Random,
) -> list[TicketRow]:
    """Rare signatures first; shuffle within equal rarity for stable variety."""

    def key(r: TicketRow) -> tuple[int, float]:
        return (sig_counts[rich_signature(r)], rng.random())

    return sorted(pool, key=key)


def pick_gold_rows(
    resolved: list[TicketRow],
    count: int,
    rng: random.Random,
    *,
    used: set[str],
    predicate: Callable[[TicketRow], bool] | None = None,
    max_rich_count: int = 1,
) -> list[TicketRow]:
    """Choose ``count`` distinct tickets; prefer low rich-signature collision (detail phrase)."""
    sig_counts = build_rich_signature_counts(resolved)
    pool = [r for r in resolved if r.ticket_id not in used and (predicate is None or predicate(r))]
    pool = [r for r in pool if sig_counts[rich_signature(r)] <= max_rich_count]
    ordered = _sorted_pool(pool, sig_counts, rng)
    if len(ordered) < count:
        raise ValueError(f"need {count} gold tickets, only {len(ordered)} match filters")
    chosen = ordered[:count]
    used.update(r.ticket_id for r in chosen)
    return chosen
