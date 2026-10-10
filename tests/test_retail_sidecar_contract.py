"""FRU-style semantic_search contract (resolved-only reuse)."""

from retail_brain.hybrid_search import TicketRow
from retail_brain.sidecar_logic import semantic_search


def test_semantic_search_skips_unresolved() -> None:
    rows = [
        TicketRow("t1", "Galaxy A15 5G", "received", "tela preta", ""),
        TicketRow(
            "t2",
            "Galaxy A15 5G",
            "resolved",
            "Customer reports: black screen after software update",
            "Reiniciar OTA",
        ),
    ]
    out = semantic_search(rows, query_text="tela preta após atualização", similarity_threshold=0.99)
    ids = [r["ticket_id"] for r in out["rows"]]
    assert "t1" not in ids
    assert out["row_count"] >= 0
