"""V1.1 hybrid: RRF promotes lexical overlap."""

import os

from retail_brain.hybrid_search import TicketRow, search_ticket_ids
from retail_brain.rrf import reciprocal_rank_fusion


def test_rrf_promotes_shared_doc() -> None:
    fused = reciprocal_rank_fusion([["a", "c"], ["b", "a"]])
    scores = dict(fused)
    assert scores["b"] > scores["c"]
    assert fused[0][0] in ("b", "a")


def test_rrf_tie_prefers_lexical_rank_one() -> None:
    """Vector #1 wrong twin; lexical #1 gold — same RRF score, lexical wins."""
    v = ["wrong-twin", "gold"]
    lex = ["gold", "wrong-twin"]
    fused = reciprocal_rank_fusion([v, lex], lexical_rank_order=lex)
    assert fused[0][0] == "gold"


def test_rrf_weighted_favors_vector_leg() -> None:
    v = ["vec-first", "lex-first"]
    lex = ["lex-first", "vec-first"]
    equal = reciprocal_rank_fusion([v, lex], list_weights=[0.5, 0.5])
    weighted = reciprocal_rank_fusion([v, lex], list_weights=[0.7, 0.3])
    assert equal[0][0] != weighted[0][0] or equal[0][1] != weighted[0][1]
    assert weighted[0][0] == "vec-first"


def test_code_boost_can_flip_top1() -> None:
    from retail_brain.rrf import code_boost_scores

    v = ["twin", "gold"]
    lex = ["twin", "gold"]
    boost = code_boost_scores(
        "Error code SAM-E176",
        ["twin", "gold"],
        id_to_search_text={
            "twin": "Technician log: diagnostic code SAM-E193.",
            "gold": "Technician log: diagnostic code SAM-E176.",
        },
        lambda_boost=10.0,
    )
    fused = reciprocal_rank_fusion(
        [v, lex],
        list_weights=[0.7, 0.3],
        extra_score_by_id=boost,
    )
    assert fused[0][0] == "gold"


def test_lexical_leg_uses_fts_normalized_text() -> None:
    """Paraphrase query should overlap index text after prefix strip."""
    from retail_brain.text_normalize import fts_query_text, search_text_for_fts

    stored = (
        "Customer reports: battery drains quickly on Galaxy A16 5G in Melbourne, VIC. "
        "Started after the latest software update. Battery drops from full to half within two hours."
    )
    paraphrase = (
        "Need help: Alex in Melbourne with a Galaxy A16 5G — battery drains quickly. "
        "Battery drops from full to half within two hours."
    )
    q = fts_query_text(paraphrase, market="AU")
    doc = search_text_for_fts(stored, market="AU")
    assert "battery" in q and "battery" in doc
    rows = [
        TicketRow("t1", "Galaxy A16 5G", "resolved", stored, "fix"),
        TicketRow("t2", "Galaxy A16 5G", "resolved", "Customer reports: unrelated issue on device.", "x"),
    ]
    os.environ["RETAIL_TICKET_HYBRID_SEARCH"] = "1"
    ranked = search_ticket_ids(q, rows, model_filter="Galaxy A16 5G", limit=1)
    assert ranked[0] == "t1"


def test_hybrid_flag_changes_ranking() -> None:
    rows = [
        TicketRow("lex", "Galaxy A16 5G", "resolved", "SM-A156 chip não reconhece", "fix sim"),
        TicketRow(
            "vec",
            "Galaxy A16 5G",
            "resolved",
            "Customer reports: battery drains quickly on the device",
            "calibrar",
        ),
    ]
    os.environ["RETAIL_TICKET_HYBRID_SEARCH"] = "0"
    v_only = search_ticket_ids("SM-A156 chip", rows, model_filter="Galaxy A16 5G", limit=2)
    os.environ["RETAIL_TICKET_HYBRID_SEARCH"] = "1"
    hybrid = search_ticket_ids("SM-A156 chip", rows, model_filter="Galaxy A16 5G", limit=2)
    assert hybrid[0] == "lex"
    assert v_only  # vector leg still returns something
