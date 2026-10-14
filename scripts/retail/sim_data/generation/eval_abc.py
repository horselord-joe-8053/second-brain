"""ABC teaching eval rows (paraphrase / hybrid_stress / code_in_query)."""

from __future__ import annotations

import random
from typing import Any

from sim_data.generation.catalog import ISSUES, PARAPHRASE_BY_ISSUE
from sim_data.generation.tickets import TicketRow


def _resolved(rows: list[TicketRow]) -> list[TicketRow]:
    return [r for r in rows if r.status == "resolved"]


def _pick_unique(resolved: list[TicketRow], count: int, rng: random.Random) -> list[TicketRow]:
    """Sample ``count`` distinct resolved tickets (deterministic shuffle)."""
    pool = list(resolved)
    rng.shuffle(pool)
    if len(pool) < count:
        raise ValueError(f"need {count} unique resolved tickets, have {len(pool)}")
    return pool[:count]


def _paraphrase_query(gold: TicketRow, rng: random.Random) -> str:
    issue = ISSUES[gold.issue_index][0]
    issue_p = PARAPHRASE_BY_ISSUE.get(issue, issue)
    caller = rng.choice(("Jordan", "Sam", "Casey", "Riley", "Morgan", "Taylor"))
    return f"{gold.city} {gold.model}: {issue_p} — reported by {caller}."


def _hybrid_query(gold: TicketRow, template: int) -> str:
    """Closed/mis-route bait + open issue (P4 product-story pattern)."""
    open_issue = ISSUES[gold.issue_index][0]
    if template == 0:
        bait = ISSUES[2][0]
        return (
            f"{bait} on {gold.model} in {gold.city} when battery low "
            f"(customer repeating phrasing from an older closed ticket). "
            f"Open problem: {open_issue} after weekend road trip."
        )
    if template == 1:
        bait = ISSUES[12][0]
        return (
            f"{bait} on {gold.model} in {gold.city} when battery low "
            f"(customer repeating a closed-ticket script). "
            f"Open problem: {open_issue} since weekend road trip."
        )
    return (
        f"NFC tap-to-pay silent fail at checkout on {gold.model} in Melbourne "
        f"(mis-pasted intake from another case). "
        f"Open problem on the {gold.city} handset: {open_issue} after weekend road trip."
    )


def _code_query(gold: TicketRow) -> str:
    """Symptom bait plus SAM-E from gold (C-lift row)."""
    code = gold.sam_e or "SAM-E110"
    bait = ISSUES[2][0]
    return (
        f"Customer reports: {bait} on {gold.model} in {gold.city}. "
        f"Worse when battery is below twenty percent. Samsung Members shows {code}."
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
    """Build eval JSONL with unique gold ids and ABC stratum mix."""
    rng = random.Random(seed + 99)
    resolved = _resolved(historical)
    para_g = _pick_unique(resolved, n_paraphrase, rng)
    used = {g.ticket_id for g in para_g}
    rest = [r for r in resolved if r.ticket_id not in used]
    hybrid_g = _pick_unique(rest, n_hybrid, rng)
    used |= {g.ticket_id for g in hybrid_g}
    rest = [r for r in resolved if r.ticket_id not in used]
    code_candidates = [r for r in rest if r.sam_e] or rest
    code_g = _pick_unique(code_candidates, n_code, rng)

    out: list[dict[str, Any]] = []
    seq = 1

    for gold in para_g:
        out.append(
            _eval_row(
                seq,
                query=_paraphrase_query(gold, rng),
                gold=gold,
                stratum="paraphrase",
                demo_lift="vector_only",
            )
        )
        seq += 1

    for i, gold in enumerate(hybrid_g):
        out.append(
            _eval_row(
                seq,
                query=_hybrid_query(gold, i % 3),
                gold=gold,
                stratum="hybrid_stress",
                demo_lift="rrf_normal",
            )
        )
        seq += 1

    for gold in code_g:
        out.append(
            _eval_row(
                seq,
                query=_code_query(gold),
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
