"""Deterministic Markdown view of a ``retail_answer.v1`` bundle (no LLM; every reference kept)."""

from __future__ import annotations

from typing import Any, Dict, List


def _pages(pages: List[int]) -> str:
    """``p.2`` / ``p.2, p.3``; empty → page not located."""
    return ", ".join(f"p.{p}" for p in pages) if pages else "(page not located)"


def _quote(text: str) -> str:
    """Single-line Markdown blockquote."""
    return "> " + " ".join((text or "").split())


def render_markdown(bundle: Dict[str, Any]) -> str:
    """Tickets with cosine/fused scores, then manual excerpts cited as ``pdf_path p.N``, then notes."""
    out: List[str] = [f"# Answer evidence — {bundle['query']}", ""]
    meta = [f"model {bundle.get('model') or 'unknown'}"]
    if bundle.get("model_sku"):
        meta.append(f"manual folder {bundle['model_sku']}")
    if bundle.get("fault_code"):
        meta.append(f"fault code {bundle['fault_code']}")
    meta.append(f"search mode {bundle['tickets']['search_mode']}")
    out += [" · ".join(meta), "", "## Similar past tickets", ""]

    hits = bundle["tickets"]["hits"]
    if not hits:
        out.append("_No similar resolved ticket found._")
    for h in hits:
        score = f"cosine {h['cosine_similarity']:.4f}"
        if h.get("fused_score") is not None:
            score += f" · fused {h['fused_score']:.6f}"
        issue = f" · issue {h['issue_key']}" if h.get("issue_key") else ""
        out += [f"{h['rank']}. **{h['ticket_id']}** — {score}{issue}",
                f"   - Customer: {' '.join(h['customer_query_text'].split())}",
                f"   - Resolution: {' '.join(h['resolution_text'].split())}"]

    out += ["", "## Manual references", ""]
    mhits = bundle["manuals"]["hits"]
    if not mhits:
        out.append("_No manual passage found._")
    for m in mhits:
        origin = m["raw_origin"]
        via = f" (via wiki `{m['wiki_path']}`)" if m.get("wiki_path") else " (raw PDF)"
        out += [f"{m['rank']}. {origin['pdf_path']} {_pages(origin['pages'])}{via}", "   " + _quote(m["excerpt"])]

    notes = bundle["diagnostics"]["notes"]
    if notes:
        out += ["", "## Notes", ""] + [f"- {n}" for n in notes]
    return "\n".join(out) + "\n"
