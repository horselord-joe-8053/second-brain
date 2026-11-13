"""ABC teaching eval rows (paraphrase / hybrid_stress / code_in_query)."""

from __future__ import annotations

import random
from typing import Any

from sim_data.generation.catalog import HYBRID_GOLD_BY_BAIT_IDX, ISSUES, PARAPHRASE_BY_ISSUE
from sim_data.generation.eval_gold import (
    detail_phrase_from_stored,
    issue_label,
    pick_gold_rows,
)
from sim_data.generation.tickets import TicketRow


def _resolved(rows: list[TicketRow]) -> list[TicketRow]:
    return [r for r in rows if r.status == "resolved"]


def _paraphrase_query(gold: TicketRow, rng: random.Random, variant: int) -> str:
    """Shopper phrasing — paraphrase issue (not catalog wording) plus intake detail anchor."""
    issue = issue_label(gold)
    issue_p = PARAPHRASE_BY_ISSUE.get(issue, issue)
    detail = detail_phrase_from_stored(gold)
    tail = f" {detail}" if detail else ""
    if variant % 3 == 0:
        base = f"{gold.city} {gold.model}: {issue_p}"
        if detail and "twenty percent" in detail:
            return f"{base} when battery below twenty percent."
        return f"{base}.{tail}"
    if variant % 3 == 1:
        return f"Shopper in {gold.city} with {gold.model} reports {issue_p}.{tail}"
    return f"{gold.city} customer: {gold.model} {issue_p}.{tail}"


def _hybrid_query(gold: TicketRow, bait_idx: int, gold_idx: int) -> str:
    """Closed/mis-route bait + open issue (P4 product-story pattern)."""
    if gold.issue_index != gold_idx:
        raise ValueError(f"gold {gold.ticket_id} issue_index {gold.issue_index} != {gold_idx}")
    bait = ISSUES[bait_idx][0]
    open_issue = ISSUES[gold_idx][0]
    detail = detail_phrase_from_stored(gold)
    anchor = f" {detail}" if detail else ""
    if bait_idx == 5:
        return (
            f"NFC tap-to-pay silent fail at checkout on {gold.model} in Melbourne "
            f"(mis-pasted intake from another case). "
            f"Open problem on the {gold.city} handset: {open_issue} after weekend road trip.{anchor}"
        )
    if bait_idx == 2:
        return (
            f"{bait} in {gold.city} on {gold.model} when battery low "
            f"(customer repeating phrasing from an older closed ticket). "
            f"Open problem: {open_issue} after weekend road trip.{anchor}"
        )
    return (
        f"{bait} on {gold.model} in {gold.city} when battery low "
        f"(customer repeating a closed-ticket script). "
        f"Open problem: {open_issue} since weekend road trip.{anchor}"
    )


def _code_query(gold: TicketRow, variant: int) -> str:
    """Mismatched symptom bait + SAM-E from gold (C term boost lifts gold over B)."""
    code = gold.sam_e or "SAM-E110"
    detail = detail_phrase_from_stored(gold)
    anchor = f" {detail}" if detail else ""
    bait = ISSUES[2][0]
    if issue_label(gold) == bait:
        bait = ISSUES[5][0]
    return (
        f"Customer reports: {bait} on {gold.model} in {gold.city}. "
        f"Worse when battery is below twenty percent. Samsung Members shows {code}.{anchor}"
    )


def _eval_row(
    n: int,
    *,
    query: str,
    gold: TicketRow,
    stratum: str,
    demo_lift: str,
) -> dict[str, Any]:
    return {
        "eval_id": f"eval-{n:04d}",
        "query": query,
        "model_filter": gold.model,
        "expected_ticket_ids": [gold.ticket_id],
        "source_ticket_id": gold.ticket_id,
        "stratum": stratum,
        "demo_lift": demo_lift,
    }


def generate_abc_eval(
    historical: list[TicketRow],
    *,
    seed: int,
    n_paraphrase: int,
    n_hybrid: int,
    n_code: int,
) -> list[dict[str, Any]]:
    """Build eval JSONL with unique gold ids, rare signatures, and ABC stratum mix."""
    rng = random.Random(seed + 99)
    resolved = _resolved(historical)
    used: set[str] = set()

    para_g = pick_gold_rows(resolved, n_paraphrase, rng, used=used, max_rich_count=1)

    hybrid_g: list[tuple[TicketRow, int, int]] = []
    for i in range(n_hybrid):
        bait_idx, gold_idx = HYBRID_GOLD_BY_BAIT_IDX[i % len(HYBRID_GOLD_BY_BAIT_IDX)]

        def _hybrid_pred(r: TicketRow, gidx: int = gold_idx, tidx: int = i) -> bool:
            if r.issue_index != gidx:
                return False
            bait_i, _ = HYBRID_GOLD_BY_BAIT_IDX[tidx % len(HYBRID_GOLD_BY_BAIT_IDX)]
            if bait_i == 5 and r.city == "Melbourne":
                return False
            return True

        batch = pick_gold_rows(
            resolved,
            1,
            rng,
            used=used,
            predicate=_hybrid_pred,
            max_rich_count=1,
        )
        hybrid_g.append((batch[0], bait_idx, gold_idx))

    def _code_pred(r: TicketRow) -> bool:
        return bool(r.sam_e)

    code_g = pick_gold_rows(resolved, n_code, rng, used=used, predicate=_code_pred)

    out: list[dict[str, Any]] = []
    seq = 1

    for i, gold in enumerate(para_g):
        out.append(
            _eval_row(
                seq,
                query=_paraphrase_query(gold, rng, i),
                gold=gold,
                stratum="paraphrase",
                demo_lift="vector_only",
            )
        )
        seq += 1

    for i, (gold, bait_idx, gold_idx) in enumerate(hybrid_g):
        out.append(
            _eval_row(
                seq,
                query=_hybrid_query(gold, bait_idx, gold_idx),
                gold=gold,
                stratum="hybrid_stress",
                demo_lift="rrf_normal",
            )
        )
        seq += 1

    for i, gold in enumerate(code_g):
        out.append(
            _eval_row(
                seq,
                query=_code_query(gold, i),
                gold=gold,
                stratum="code_in_query",
                demo_lift="rrf_term_boosted",
            )
        )
        seq += 1

    return out


def generate_legacy_ten_eval(historical: list[TicketRow], seed: int) -> list[dict[str, Any]]:
    """Ten-row mix for the 60/10 profile generator."""
    return generate_abc_eval(historical, seed=seed, n_paraphrase=5, n_hybrid=3, n_code=2)
