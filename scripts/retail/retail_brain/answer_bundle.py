"""Assemble the ``retail_answer.v1`` bundle: top-2 similar tickets + manual evidence with raw provenance.

Both legs always run (decision E3); each leg's failure is isolated into ``diagnostics`` so the caller
always gets a well-formed bundle. Output is deterministic (E6): no timestamps, rounded scores, and
``bundle_to_json`` sorts keys — the same inputs give byte-identical JSON.

Consumers: ``answer_render.render_markdown`` (deterministic), a JSON parser, or an LLM summarizer that
must keep ``ticket_id`` and ``raw_origin`` references.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional

from retail_brain.answer_manuals import WikiSearchClient, manual_leg
from retail_brain.answer_tickets import TicketSource, ticket_leg
from retail_brain.company_profile import CompanyProfile, cached_company_profile
from retail_brain.txt_docs import TxtDocIndex
from retail_brain.search_mode import resolve_ticket_search_mode
from retail_brain.text_normalize import diag_code_pattern

SCHEMA = "retail_answer.v1"


def detect_model(query: str, profile: CompanyProfile) -> Optional[str]:
    """First profile SKU (or manual folder name) mentioned in the query, as the ticket ``model`` code."""
    for m in profile.models:
        sku = m.get("sku", "")
        if sku and re.search(rf"\b{re.escape(sku)}\b", query, re.IGNORECASE):
            return sku
        folder = m.get("docs_folder", "")
        if folder and folder.lower() in query.lower():
            return sku
    return None


def fault_code(query: str, profile: CompanyProfile) -> Optional[str]:
    """Diagnostic code using the company profile's prefix (not the env default, which is phone-era SAM-E)."""
    m = diag_code_pattern(profile.fault_code_prefix.rstrip("-")).search(query or "")
    return m.group(0).upper() if m else None


def manual_query(query: str, profile: CompanyProfile) -> str:
    """Ticket text minus sentences that carry a fault code (manuals never mention FRU codes).

    Falls back to the full text when every sentence has a code.
    """
    pattern = diag_code_pattern(profile.fault_code_prefix.rstrip("-"))
    sentences = re.split(r"(?<=[.!?])\s+", query.strip())
    kept = [s for s in sentences if not pattern.search(s)]
    return " ".join(kept) if kept else query


def build_answer_bundle(
    query: str,
    *,
    ticket_source: TicketSource,
    txt_index: TxtDocIndex,
    wiki: Optional[WikiSearchClient],
    model: Optional[str] = None,
    k_tickets: int = 2,
    k_manuals: int = 3,
    corpus_profile: str = "fru_us_1k",
    company: Optional[CompanyProfile] = None,
    skip_ticket_leg: bool = False,
    skip_manual_leg: bool = False,
) -> Dict[str, Any]:
    """Run ticket and/or manual legs for one new ticket and return the bundle dict."""
    company = company or cached_company_profile()
    model = model or detect_model(query, company)
    model_sku = company.docs_folder_for_model(model) if model else None
    notes: list[str] = []

    if skip_ticket_leg:
        tickets = {"search_mode": "skipped", "hits": []}
        ticket_ok = True
        notes.append("ticket leg skipped")
    else:
        try:
            tickets = ticket_leg(query, ticket_source, model=model, k=k_tickets)
            ticket_ok = True
        except Exception as e:  # noqa: BLE001 — leg isolation: any backend failure becomes a note
            tickets = {"search_mode": resolve_ticket_search_mode(), "hits": []}
            ticket_ok = False
            notes.append(f"ticket leg failed: {type(e).__name__}: {e}")
        if model is None:
            notes.append("no fridge model found in query; tickets not model-scoped")

    if skip_manual_leg:
        manuals = {
            "hits": [],
            "diagnostics": {
                "manual_leg_ok": True,
                "wiki_available": False,
                "notes": ["manual leg skipped"],
            },
        }
        mdiag = manuals["diagnostics"]
    else:
        try:
            manuals = manual_leg(
                manual_query(query, company), sku=model_sku, wiki=wiki, txt_index=txt_index, k=k_manuals
            )
        except Exception as e:  # noqa: BLE001
            manuals = {
                "hits": [],
                "diagnostics": {
                    "manual_leg_ok": False,
                    "wiki_available": False,
                    "notes": [f"manual leg failed: {type(e).__name__}: {e}"],
                },
            }
        mdiag = manuals["diagnostics"]

    return {
        "schema": SCHEMA,
        "profile": "retail",
        "corpus_profile": corpus_profile,
        "query": query,
        "model": model,
        "model_sku": model_sku,
        "fault_code": fault_code(query, company),
        "tickets": tickets,
        "manuals": {"hits": manuals["hits"]},
        "diagnostics": {
            "ticket_leg_ok": ticket_ok,
            "manual_leg_ok": bool(mdiag["manual_leg_ok"]),
            "wiki_available": bool(mdiag["wiki_available"]),
            "notes": notes + list(mdiag["notes"]),
        },
    }


def bundle_to_json(bundle: Dict[str, Any]) -> str:
    """Canonical serialization: sorted keys, 2-space indent, UTF-8 text, trailing newline."""
    return json.dumps(bundle, sort_keys=True, ensure_ascii=False, indent=2) + "\n"
