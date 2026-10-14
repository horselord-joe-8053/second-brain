"""FRU ABC eval rows driven by YAML paraphrase / hybrid / code templates."""

from __future__ import annotations

import random
from typing import Any

from retail_brain.company_profile import CompanyProfile, cached_company_profile

from sim_data.generation.eval_gold import detail_phrase_from_stored, pick_gold_rows
from sim_data.generation.tickets import TicketRow


def _resolved(rows: list[TicketRow]) -> list[TicketRow]:
    return [r for r in rows if r.status == "resolved"]


def _issue_symptom(row: TicketRow, profile: CompanyProfile) -> str:
    if row.issue_key:
        return profile.issue_by_key(row.issue_key).symptom
    return row.customer_query_text.split(".")[0]


def _paraphrase_query(gold: TicketRow, profile: CompanyProfile, rng: random.Random, variant: int) -> str:
    issue = profile.issue_by_key(gold.issue_key) if gold.issue_key else None
    issue_p = issue.paraphrase if issue else _issue_symptom(gold, profile)
    detail = detail_phrase_from_stored(gold)
    tail = f" {detail}" if detail else ""
    if variant % 3 == 0:
        return f"{gold.city} {gold.model}: {issue_p}.{tail}"
    if variant % 3 == 1:
        return f"Owner in {gold.city} with {gold.model} reports {issue_p}.{tail}"
    return f"{gold.city} customer: {gold.model} — {issue_p}.{tail}"


def _hybrid_query(
    gold: TicketRow,
    profile: CompanyProfile,
    pair_idx: int,
) -> str:
    pairs = profile.hybrid_bait_pairs
    pair = pairs[pair_idx % len(pairs)]
    bait = profile.issue_by_key(pair["bait_key"])
    open_issue = profile.issue_by_key(gold.issue_key) if gold.issue_key else None
    open_symptom = open_issue.symptom if open_issue else _issue_symptom(gold, profile)
    detail = detail_phrase_from_stored(gold)
    anchor = f" {detail}" if detail else ""
    style = pair.get("style", "closed_ticket_repeat")
    if style == "misroute_checkout":
        return (
            f"{bait.symptom} at a grocery checkout on {gold.model} in Dallas "
            f"(mis-pasted intake from another case). "
            f"Open problem on the {gold.city} unit: {open_symptom} after a long weekend.{anchor}"
        )
    return (
        f"{bait.symptom} on {gold.model} in {gold.city} "
        f"(customer repeating phrasing from an older closed ticket). "
        f"Open problem: {open_symptom} since the holiday weekend.{anchor}"
    )


def _code_query(gold: TicketRow, profile: CompanyProfile, variant: int) -> str:
    code = gold.fault_code or gold.sam_e or "FRU-E110"
    detail = detail_phrase_from_stored(gold)
    anchor = f" {detail}" if detail else ""
    bait_issue = profile.issues[(variant + 3) % len(profile.issues)]
    if gold.issue_key and bait_issue.key == gold.issue_key:
        bait_issue = profile.issues[(variant + 5) % len(profile.issues)]
    phrasing = profile.code_phrasings[variant % len(profile.code_phrasings)].format(code=code)
    return (
        f"Customer reports: {bait_issue.symptom} on {gold.model} in {gold.city}. "
        f"Door panel log shows {phrasing}.{anchor}"
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


def generate_fru_abc_eval(
    historical: list[TicketRow],
    *,
    seed: int,
    n_paraphrase: int,
    n_hybrid: int,
    n_code: int,
    profile: CompanyProfile | None = None,
) -> list[dict[str, Any]]:
    """Build tuned incoming eval rows for the FRU profile."""
    profile = profile or cached_company_profile()
    rng = random.Random(seed + 991)
    pool = _resolved(historical)
    used: set[str] = set()
    para_g = pick_gold_rows(pool, n_paraphrase, rng, used=used, max_rich_count=2)
    hybrid_g: list[TicketRow] = []
    for i in range(n_hybrid):
        hybrid_g.extend(
            pick_gold_rows(pool, 1, rng, used=used, max_rich_count=2)
        )
    code_g = pick_gold_rows(
        pool,
        n_code,
        rng,
        used=used,
        predicate=lambda r: bool(r.fault_code or r.sam_e),
        max_rich_count=2,
    )
    out: list[dict[str, Any]] = []
    n = 1
    for i, g in enumerate(para_g):
        out.append(
            _eval_row(
                n,
                query=_paraphrase_query(g, profile, rng, i),
                gold=g,
                stratum="paraphrase",
                demo_lift="rrf_normal",
            )
        )
        n += 1
    for i, g in enumerate(hybrid_g):
        out.append(
            _eval_row(
                n,
                query=_hybrid_query(g, profile, i),
                gold=g,
                stratum="hybrid_stress",
                demo_lift="rrf_normal",
            )
        )
        n += 1
    for i, g in enumerate(code_g):
        out.append(
            _eval_row(
                n,
                query=_code_query(g, profile, i),
                gold=g,
                stratum="code_in_query",
                demo_lift="rrf_term_boosted",
            )
        )
        n += 1
    return out
