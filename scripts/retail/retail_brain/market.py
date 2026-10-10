"""Retail market profile: locale, copy, and Postgres full-text config (one knob for seed → PG → eval)."""

from __future__ import annotations

import os
from typing import Any, Dict, List, Tuple

MarketCode = str

_PROFILES: Dict[MarketCode, Dict[str, Any]] = {
    "AU": {
        "label": "Australia",
        "bcp47": "en-AU",
        "pg_ts_config": "english",
        "customer_query_prefix": "Customer reports: ",
        "paraphrase_template": "Need help: caller says {core} (ref {ref})",
        "cities": [
            ("Sydney", "NSW"),
            ("Melbourne", "VIC"),
            ("Brisbane", "QLD"),
        ],
        "issues": [
            (
                "black screen after software update",
                "Reboot to safe mode and reinstall the OTA patch.",
            ),
            (
                "battery drains quickly",
                "Calibrate battery and review background apps.",
            ),
            (
                "SM-A156 SIM not recognised",
                "Reseat SIM and validate operator 5G bands.",
            ),
        ],
    },
    "BR": {
        "label": "Brazil",
        "bcp47": "pt-BR",
        "pg_ts_config": "portuguese",
        "customer_query_prefix": "Cliente relata: ",
        "paraphrase_template": "Preciso de ajuda: usuário descreve {core} (ref {ref})",
        "cities": [
            ("São Paulo", "SP"),
            ("Rio de Janeiro", "RJ"),
            ("Salvador", "BA"),
        ],
        "issues": [
            (
                "tela preta após atualização",
                "Reiniciar em modo seguro e reinstalar patch OTA.",
            ),
            (
                "bateria descarrega rápido",
                "Calibrar bateria e verificar apps em segundo plano.",
            ),
            (
                "SM-A156 não reconhece chip",
                "Reassentar SIM e validar bandas 5G da operadora.",
            ),
        ],
    },
}


def market_code() -> MarketCode:
    raw = (os.environ.get("RETAIL_MARKET") or "AU").strip().upper()
    if raw not in _PROFILES:
        allowed = ", ".join(sorted(_PROFILES))
        raise ValueError(f"Unknown RETAIL_MARKET={raw!r} — use one of: {allowed}")
    return raw


def market_profile(code: MarketCode | None = None) -> Dict[str, Any]:
    key = (code or market_code()).upper()
    if key not in _PROFILES:
        allowed = ", ".join(sorted(_PROFILES))
        raise ValueError(f"Unknown market {key!r} — use one of: {allowed}")
    return _PROFILES[key]


def pg_ts_config(code: MarketCode | None = None) -> str:
    return str(market_profile(code)["pg_ts_config"])


def cities_for_market(code: MarketCode | None = None) -> List[Tuple[str, str]]:
    return list(market_profile(code)["cities"])


def issues_for_market(code: MarketCode | None = None) -> List[Tuple[str, str]]:
    return list(market_profile(code)["issues"])
