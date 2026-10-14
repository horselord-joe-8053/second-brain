"""Frozen spec for ten eval rows that demo the A/B/C (V1→V1.2) hybrid ladder on llm_gen."""

from __future__ import annotations

from typing import Any, TypedDict

DEMO_LIFT_MODES = frozenset(
    {
        "vector_only",
        "rrf_normal",
        "rrf_term_boosted",
    }
)


class AbcdDemoEvalRow(TypedDict):
    """One eval JSONL row plus ``demo_lift`` (first mode expected to hit gold for authoring QA)."""

    eval_id: str
    query: str
    model_filter: str
    expected_ticket_ids: list[str]
    source_ticket_id: str
    stratum: str
    demo_lift: str


# Mix: 5 vector-easy, 3 hybrid_stress (B lift: open issue + closed/misroute bait), 2 SAM-E (C lift).
ABCD_DEMO_EVAL_ROWS: list[AbcdDemoEvalRow] = [
    {
        "eval_id": "eval-0001",
        "query": (
            "5G handover drops in Sydney on Galaxy A15 5G when battery low "
            "(customer repeating phrasing from an older closed ticket). "
            "Open problem: black screen after calls after weekend road trip."
        ),
        "model_filter": "Galaxy A15 5G",
        "expected_ticket_ids": ["T-0042-000000"],
        "source_ticket_id": "T-0042-000000",
        "stratum": "hybrid_stress",
        "demo_lift": "rrf_normal",
    },
    {
        "eval_id": "eval-0002",
        "query": (
            "Brisbane Galaxy A25 5G: mobile data drops during 5G handover when battery "
            "below twenty percent."
        ),
        "model_filter": "Galaxy A25 5G",
        "expected_ticket_ids": ["T-0042-000002"],
        "source_ticket_id": "T-0042-000002",
        "stratum": "paraphrase",
        "demo_lift": "vector_only",
    },
    {
        "eval_id": "eval-0003",
        "query": (
            "Customer reports: 5G handover drops data on Galaxy A25 5G in Brisbane, QLD. "
            "Worse when battery is below twenty percent. Samsung Members shows SAM-E110."
        ),
        "model_filter": "Galaxy A25 5G",
        "expected_ticket_ids": ["T-0042-000020"],
        "source_ticket_id": "T-0042-000020",
        "stratum": "code_in_query",
        "demo_lift": "rrf_term_boosted",
    },
    {
        "eval_id": "eval-0004",
        "query": (
            "Shopper in Perth with Galaxy A15 5G reports distorted speaker audio at medium volume."
        ),
        "model_filter": "Galaxy A15 5G",
        "expected_ticket_ids": ["T-0042-000015"],
        "source_ticket_id": "T-0042-000015",
        "stratum": "paraphrase",
        "demo_lift": "vector_only",
    },
    {
        "eval_id": "eval-0005",
        "query": (
            "Ghost touches near edges on Galaxy A15 5G in Sydney when battery low "
            "(customer repeating a closed-ticket script). "
            "Open problem: fingerprint reader slow since weekend road trip."
        ),
        "model_filter": "Galaxy A15 5G",
        "expected_ticket_ids": ["T-0042-000030"],
        "source_ticket_id": "T-0042-000030",
        "stratum": "hybrid_stress",
        "demo_lift": "rrf_normal",
    },
    {
        "eval_id": "eval-0006",
        "query": (
            "Melbourne customer: Galaxy A16 5G contactless wallet payments fail silently at checkout."
        ),
        "model_filter": "Galaxy A16 5G",
        "expected_ticket_ids": ["T-0042-000025"],
        "source_ticket_id": "T-0042-000025",
        "stratum": "paraphrase",
        "demo_lift": "vector_only",
    },
    {
        "eval_id": "eval-0007",
        "query": (
            "Melbourne customer reports NFC wallet fails at checkout on Galaxy A16 5G. "
            "Open problem on the Adelaide dual-SIM handset: fingerprint reader slow after weekend road trip."
        ),
        "model_filter": "Galaxy A16 5G",
        "expected_ticket_ids": ["T-0042-000010"],
        "source_ticket_id": "T-0042-000010",
        "stratum": "hybrid_stress",
        "demo_lift": "rrf_normal",
    },
    {
        "eval_id": "eval-0008",
        "query": (
            "Canberra Galaxy A25 5G: crackling speaker when volume above halfway, no water damage."
        ),
        "model_filter": "Galaxy A25 5G",
        "expected_ticket_ids": ["T-0042-000035"],
        "source_ticket_id": "T-0042-000035",
        "stratum": "paraphrase",
        "demo_lift": "vector_only",
    },
    {
        "eval_id": "eval-0009",
        "query": (
            "Customer in Canberra with Galaxy A25 5G: tap-to-pay at the terminal does nothing, "
            "no damage to the phone."
        ),
        "model_filter": "Galaxy A25 5G",
        "expected_ticket_ids": ["T-0042-000005"],
        "source_ticket_id": "T-0042-000005",
        "stratum": "paraphrase",
        "demo_lift": "vector_only",
    },
    {
        "eval_id": "eval-0010",
        "query": (
            "Canberra shopper: Galaxy A16 5G overheating during video calls. "
            "Diagnostic SAM-E120 on device."
        ),
        "model_filter": "Galaxy A16 5G",
        "expected_ticket_ids": ["T-0042-000040"],
        "source_ticket_id": "T-0042-000040",
        "stratum": "code_in_query",
        "demo_lift": "rrf_term_boosted",
    },
]


def row_to_jsonl_obj(row: AbcdDemoEvalRow) -> dict[str, Any]:
    """Export harness-facing fields plus optional demo_lift for operator docs."""
    return dict(row)
