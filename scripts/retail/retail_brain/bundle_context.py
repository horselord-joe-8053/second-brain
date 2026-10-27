"""Build one LLM context string from ticket hits and manual raw chunks (fixed-k concat)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence


def format_ticket_hits_for_context(
    hits: Sequence[Mapping[str, Any]],
    *,
    max_chars_per_hit: int = 1200,
) -> str:
    """Render past-ticket section: id, customer text, resolution (truncated per hit)."""
    blocks: list[str] = []
    cap = max(0, int(max_chars_per_hit))
    for h in hits:
        tid = str(h.get("ticket_id") or "")
        cust = str(h.get("customer_query_text") or "")[:cap]
        res = str(h.get("resolution_text") or "")[:cap]
        blocks.append(
            f"Ticket {tid}\nCustomer: {cust}\nResolution: {res}".strip()
        )
    return "\n\n".join(blocks)


def format_manual_hits_for_context(
    hits: Sequence[Mapping[str, Any]],
    *,
    page_prefix_chars: int,
    max_chars_per_chunk: int = 0,
) -> str:
    """Render manual excerpts with source paths (same caps as M90 raw RAG)."""
    parts: list[str] = []
    used = 0
    per_cap = max(0, int(max_chars_per_chunk or 0))
    budget = max(0, int(page_prefix_chars))
    for h in hits:
        rel = str(h.get("source_relpath") or "")
        text = str(h.get("text") or "")
        if per_cap > 0:
            text = text[:per_cap]
        block = f"--- {rel} ---\n{text}"
        if used + len(block) > budget and parts:
            break
        parts.append(block)
        used += len(block) + 2
    return "\n\n".join(parts)


def build_bundled_context(
    ticket_hits: Sequence[Mapping[str, Any]],
    manual_hits: Sequence[Mapping[str, Any]],
    *,
    page_prefix_chars: int,
    max_chars_per_chunk: int = 0,
    max_chars_per_ticket: int = 1200,
) -> str:
    """Concatenate tickets first, then manuals — labeled sections for one answer LLM call."""
    ticket_block = format_ticket_hits_for_context(
        ticket_hits, max_chars_per_hit=max_chars_per_ticket
    )
    manual_block = format_manual_hits_for_context(
        manual_hits,
        page_prefix_chars=page_prefix_chars,
        max_chars_per_chunk=max_chars_per_chunk,
    )
    return (
        "## Past resolved tickets\n"
        f"{ticket_block or '(no ticket excerpts)'}\n\n"
        "## Manual excerpts\n"
        f"{manual_block or '(no manual excerpts)'}"
    )


def bundled_answer_prompt(
    question: str,
    context: str,
    *,
    insufficient_literal: str,
) -> str:
    """System-style prompt for B20: both ticket resolutions and manual facts may be required."""
    return (
        "Answer using ONLY the past tickets and manual excerpts below. "
        "Combine relevant ticket resolution steps with manual facts when both apply. "
        f"If the excerpts do not contain enough information, reply exactly: {insufficient_literal}\n\n"
        f"Question: {question}\n\n{context}"
    )
