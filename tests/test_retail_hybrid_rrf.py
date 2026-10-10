"""V1.1 hybrid: RRF promotes lexical overlap."""

import os

from retail_brain.hybrid_search import TicketRow, search_ticket_ids
from retail_brain.rrf import reciprocal_rank_fusion


def test_rrf_promotes_shared_doc() -> None:
    fused = reciprocal_rank_fusion([["a", "c"], ["b", "a"]])
    scores = dict(fused)
    assert scores["b"] > scores["c"]
    assert fused[0][0] in ("b", "a")


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
