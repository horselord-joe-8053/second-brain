"""Frozen spec for ten eval rows that demo the A/B/C/D (V1→V1.3) hybrid ladder on llm_gen."""

from __future__ import annotations

from typing import Any, TypedDict

DEMO_LIFT_MODES = frozenset(
    {
        "vector_only",
        "rrf_normal",
        "rrf_weighted",
        "rrf_weighted_boosted",
    }
)


class AbcdDemoEvalRow(TypedDict):
    """One eval JSONL row plus authoring metadata for the hybrid demo ladder."""

    eval_id: str
    query: str
    model_filter: str
    expected_ticket_ids: list[str]
    source_ticket_id: str
    stratum: str
    demo_lift: str


# Authoring intent: neighbor-bait wording + gold evidence (SAM-E / tokens). Tune with operator A/B/C/D.
ABCD_DEMO_EVAL_ROWS: list[AbcdDemoEvalRow] = [
    {
        "eval_id": "eval-0001",
        "query": (
            "Customer reports: 5G handover drops data on Galaxy A15 5G in Sydney, NSW. "
            "Worse when battery is below twenty percent. "
            "Samsung Members shows SAM-E100."
        ),
        "model_filter": "Galaxy A15 5G",
        "expected_ticket_ids": ["T-0042-000000"],
        "source_ticket_id": "T-0042-000000",
        "stratum": "hybrid_stress",
        "demo_lift": "rrf_weighted_boosted",
    },
    {
        "eval_id": "eval-0002",
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
        "eval_id": "eval-0003",
        "query": (
            "Galaxy A25 5G in Brisbane: after phone calls the display stays black until reboot. "
            "Error reference SAM-E110 in the support app."
        ),
        "model_filter": "Galaxy A25 5G",
        "expected_ticket_ids": ["T-0042-000020"],
        "source_ticket_id": "T-0042-000020",
        "stratum": "code_in_query",
        "demo_lift": "rrf_weighted_boosted",
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
            "Intake: Galaxy A15 5G owner in Sydney, NSW — ghost touches near edges. "
            "Worse when battery is below twenty percent. App lists SAM-E115."
        ),
        "model_filter": "Galaxy A15 5G",
        "expected_ticket_ids": ["T-0042-000030"],
        "source_ticket_id": "T-0042-000030",
        "stratum": "code_in_query",
        "demo_lift": "rrf_weighted_boosted",
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
            "Adelaide intake: Galaxy A16 5G fingerprint reader became slow after a road trip. "
            "Technician note mentions SAM-E105."
        ),
        "model_filter": "Galaxy A16 5G",
        "expected_ticket_ids": ["T-0042-000010"],
        "source_ticket_id": "T-0042-000010",
        "stratum": "code_in_query",
        "demo_lift": "rrf_weighted_boosted",
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
        "demo_lift": "rrf_normal",
    },
    {
        "eval_id": "eval-0009",
        "query": (
            "Customer reports: 5G handover drops data on Galaxy A25 5G in Brisbane, QLD. "
            "Worse when battery is below twenty percent. Diagnostic SAM-E101 in Samsung Members."
        ),
        "model_filter": "Galaxy A25 5G",
        "expected_ticket_ids": ["T-0042-000002"],
        "source_ticket_id": "T-0042-000002",
        "stratum": "hybrid_stress",
        "demo_lift": "rrf_normal",
    },
    {
        "eval_id": "eval-0010",
        "query": (
            "Adelaide Galaxy A16 5G: screen goes black after incoming calls. Diagnostic SAM-E120 on device."
        ),
        "model_filter": "Galaxy A16 5G",
        "expected_ticket_ids": ["T-0042-000040"],
        "source_ticket_id": "T-0042-000040",
        "stratum": "code_in_query",
        "demo_lift": "rrf_weighted_boosted",
    },
]


def row_to_jsonl_obj(row: AbcdDemoEvalRow) -> dict[str, Any]:
    """Export harness-facing fields plus optional demo_lift for operator docs."""
    return dict(row)
