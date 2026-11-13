"""Deterministic seed narrative expansion."""

from retail_brain.seed import generate_tickets
from retail_brain.seed_narrative import narrative_parts


def test_narrative_deterministic_for_seed_and_index() -> None:
    a = narrative_parts(seed=42, index=3, market="AU")
    b = narrative_parts(seed=42, index=3, market="AU")
    c = narrative_parts(seed=42, index=4, market="AU")
    assert a == b
    assert a != c


def test_generate_tickets_uses_ten_issue_pool() -> None:
    rows = generate_tickets(count=10, seed=99)
    bodies = [r.customer_query_text for r in rows]
    assert len(set(bodies)) == 10
