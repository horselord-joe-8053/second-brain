"""Per-manual English-only trim for pypdf ``.txt`` extracts (retail fridge-docs).

We do **not** auto-detect language. Each multilingual PDF uses a different layout
(Samsung: English block then ``Español N``; GE: full English manual then French/Spanish
reprints). Operators add a ``ManualTrimRule`` when onboarding a new SKU.

When a rule fires, the builder writes the **full** extract to
``archive/fridge-docs/<sku>/<stem>.mul.txt`` and the **trimmed** body to
``raw/sources/fridge-docs/<sku>/<stem>.txt``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class ManualTrimRule:
    """How to cut one ``(sku_folder, guide_stem)`` extract to English-only raw text."""

    sku_folder: str
    guide_stem: str
    # Human note for maintainers (PDF layout / pub number).
    layout_note: str
    # Return cut index in ``body``, or None to keep full text.
    find_cut: Callable[[str], int | None]


def _samsung_user_guide_cut(body: str) -> int | None:
    """Samsung RF-style: English first; second language starts with ``Español <page>``."""
    min_english = 20_000
    pat = re.compile(
        r"\n(Español|Français|Deutsch|Italiano|Português|Nederlands|Polski|한국어|中文|日本語)\s+\d+\s",
        re.IGNORECASE,
    )
    m = pat.search(body)
    if not m or m.start() < min_english:
        return None
    return m.start()


def _ge_user_guide_cut(body: str) -> int | None:
    """GE Pub 49-1000472: English through ~page 104; French TOC starts ``CONSIGNES DE SÉCURITÉ``."""
    min_english = 50_000
    # French reprint table-of-contents block (not present in English operating section).
    pat = re.compile(r"\nCONSIGNES DE SÉCURITÉ\s+\.{2,}\s*\d+", re.IGNORECASE)
    m = pat.search(body)
    if not m or m.start() < min_english:
        return None
    return m.start()


# --- Register rules here (explicit markers per manual) ---
MANUAL_TRIM_RULES: tuple[ManualTrimRule, ...] = (
    ManualTrimRule(
        sku_folder="samsung_RF28K9070SG",
        guide_stem="user-guide",
        layout_note="Samsung multi-language user guide; English through ~page 154, then Español 2 …",
        find_cut=_samsung_user_guide_cut,
    ),
    ManualTrimRule(
        sku_folder="ge_GNE27JYMFS",
        guide_stem="user-guide",
        layout_note="GE 49-1000472 EN/FR/ES in one PDF; English ends before French CONSIGNES DE SÉCURITÉ TOC.",
        find_cut=_ge_user_guide_cut,
    ),
)

_RULE_INDEX: dict[tuple[str, str], ManualTrimRule] = {
    (r.sku_folder, r.guide_stem): r for r in MANUAL_TRIM_RULES
}


def apply_multilingual_trim(body: str, sku_folder: str, guide_stem: str) -> tuple[str, int | None]:
    """Return ``(text_for_raw_txt, cut_index)``; ``cut_index`` is None when unchanged."""
    rule = _RULE_INDEX.get((sku_folder, guide_stem))
    if rule is None:
        return body, None
    cut = rule.find_cut(body)
    if cut is None:
        return body, None
    return body[:cut].rstrip() + "\n", cut


def rule_for(sku_folder: str, guide_stem: str) -> ManualTrimRule | None:
    """Lookup registered trim rule, if any."""
    return _RULE_INDEX.get((sku_folder, guide_stem))
