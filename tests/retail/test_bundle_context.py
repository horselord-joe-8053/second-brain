"""Unit tests for fixed-k bundled context assembly."""

from __future__ import annotations

from retail_brain.bundle_context import build_bundled_context


def test_bundled_context_tickets_before_manuals_and_includes_both_legs() -> None:
    """Concat helper must preserve leg order and text from fixture hits."""
    tickets = [
        {
            "ticket_id": "T-0042-100017",
            "customer_query_text": "panel dead",
            "resolution_text": "power-cycled display board",
        }
    ]
    manuals = [
        {
            "source_relpath": "fridge-docs/ge/manual.txt",
            "text": "Door alarm sounds after 2 minutes open.",
        }
    ]
    ctx = build_bundled_context(
        tickets,
        manuals,
        page_prefix_chars=8000,
        max_chars_per_chunk=2000,
    )
    assert "## Past resolved tickets" in ctx
    assert "## Manual excerpts" in ctx
    assert ctx.index("Past resolved tickets") < ctx.index("Manual excerpts")
    assert "T-0042-100017" in ctx
    assert "power-cycled display board" in ctx
    assert "Door alarm sounds" in ctx
    assert "fridge-docs/ge/manual.txt" in ctx
