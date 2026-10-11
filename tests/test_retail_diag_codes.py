"""Diagnostic code pairs: fair full embed, hybrid eval stratum."""

import re

from retail_brain.seed import generate_tickets
from retail_brain.seed_narrative import (
    format_eval_query_with_code,
    format_stored_customer_query,
    narrative_parts,
)
from retail_brain.text_normalize import fts_query_text, search_text_for_fts


def _body_without_code(stored: str) -> str:
    return re.sub(
        r"\s*Technician log: diagnostic code \S+\.\s*$",
        "",
        stored,
        flags=re.IGNORECASE,
    ).strip()


def test_pair_shares_symptom_prose_different_code() -> None:
    p0 = narrative_parts(seed=42, index=0)
    p1 = narrative_parts(seed=42, index=1)
    s0 = format_stored_customer_query(p0, index=0)
    s1 = format_stored_customer_query(p1, index=1)
    assert p0.issue == p1.issue and p0.detail_symptom == p1.detail_symptom
    assert _body_without_code(s0) != _body_without_code(s1)
    assert "Need help:" in s1
    assert p0.diagnostic_code != p1.diagnostic_code


def test_stored_text_keeps_code_for_fts_not_vector_index() -> None:
    from retail_brain.text_normalize import text_for_embedding

    parts = narrative_parts(seed=42, index=4)
    stored = format_stored_customer_query(parts, index=4)
    assert parts.diagnostic_code in stored
    assert parts.diagnostic_code in search_text_for_fts(stored)
    assert parts.diagnostic_code not in text_for_embedding(stored)


def test_error_code_eval_query_matches_screenshot_shape() -> None:
    parts = narrative_parts(seed=42, index=4)
    stored = format_stored_customer_query(parts, index=4)
    q = format_eval_query_with_code(parts)
    assert parts.model in q
    assert parts.issue in q
    assert parts.diagnostic_code in q
    fts_q = fts_query_text(q, market="AU")
    assert parts.diagnostic_code in fts_q or parts.diagnostic_code in search_text_for_fts(stored)


def test_no_duplicate_full_stored_text_at_90() -> None:
    rows = generate_tickets(count=90, seed=42)
    texts = [r.customer_query_text for r in rows]
    assert len(texts) == len(set(texts))
