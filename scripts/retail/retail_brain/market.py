"""Retail market profile: locale, copy templates, and seed/eval wording (AU vs BR).

``pg_ts_config`` remains for historical seed/load paths; production keyword search uses
``lexical_search/`` backends, not Postgres FTS.
"""

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
        "eval_query_template": (
            "Need help: {caller} in {city} with a {model} — {issue}. {detail}"
        ),
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
            (
                "mobile data drops when switching to 5G",
                "Reset APN settings and verify carrier VoLTE profile.",
            ),
            (
                "camera app crashes on open",
                "Clear camera cache and apply latest security patch.",
            ),
            (
                "fingerprint sensor stopped working",
                "Re-register prints after wiping sensor area.",
            ),
            (
                "Bluetooth will not pair with car audio",
                "Forget device, reset network settings, pair again.",
            ),
            (
                "phone overheats during normal calls",
                "Check for rogue background sync and reduce brightness.",
            ),
            (
                "wireless charging pad not detected",
                "Test with another pad and inspect case thickness.",
            ),
            (
                "notifications delayed by several hours",
                "Disable battery optimization for messaging apps.",
            ),
        ],
    },
    "BR": {
        "label": "Brazil",
        "bcp47": "pt-BR",
        "pg_ts_config": "portuguese",
        "customer_query_prefix": "Cliente relata: ",
        "paraphrase_template": "Preciso de ajuda: usuário descreve {core} (ref {ref})",
        "eval_query_template": (
            "Preciso de ajuda: {caller} em {city} com {model} — {issue}. {detail}"
        ),
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
            (
                "dados móveis caem ao mudar para 5G",
                "Redefinir APN e validar perfil VoLTE.",
            ),
            (
                "app da câmera fecha ao abrir",
                "Limpar cache da câmera e aplicar patch.",
            ),
            (
                "leitor de digital parou de funcionar",
                "Recadastrar digitais após limpar sensor.",
            ),
            (
                "Bluetooth não emparelha no carro",
                "Esquecer dispositivo e parear de novo.",
            ),
            (
                "telefone esquenta durante ligações",
                "Verificar sync em segundo plano.",
            ),
            (
                "carregamento sem fio não detectado",
                "Testar outra base e remover capa grossa.",
            ),
            (
                "notificações atrasam horas",
                "Desativar otimização de bateria no app.",
            ),
        ],
    },
}


def market_code() -> MarketCode:
    """Active market from ``RETAIL_MARKET`` (default ``AU``)."""
    raw = (os.environ.get("RETAIL_MARKET") or "AU").strip().upper()
    if raw not in _PROFILES:
        allowed = ", ".join(sorted(_PROFILES))
        raise ValueError(f"Unknown RETAIL_MARKET={raw!r} — use one of: {allowed}")
    return raw


def market_profile(code: MarketCode | None = None) -> Dict[str, Any]:
    """Full profile dict (locale, templates, cities, issues) for a market code."""
    key = (code or market_code()).upper()
    if key not in _PROFILES:
        allowed = ", ".join(sorted(_PROFILES))
        raise ValueError(f"Unknown market {key!r} — use one of: {allowed}")
    return _PROFILES[key]


def pg_ts_config(code: MarketCode | None = None) -> str:
    """Postgres text search config name for legacy load paths (``english`` / ``portuguese``)."""
    return str(market_profile(code)["pg_ts_config"])


def cities_for_market(code: MarketCode | None = None) -> List[Tuple[str, str]]:
    """(city, state) pairs used in synthetic ticket narratives."""
    return list(market_profile(code)["cities"])


def issues_for_market(code: MarketCode | None = None) -> List[Tuple[str, str]]:
    """(customer issue, resolution) pairs for seed narrative rotation."""
    return list(market_profile(code)["issues"])
