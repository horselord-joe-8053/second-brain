"""Domain enums and constants for synthetic retail tickets and eval strata.

Phone-era (Galaxy A15/A16/A25) — used by ``rrf_data_prag_gen`` / ``seed_narrative`` only.
Default FRU corpus uses ``config/fru_us_service.yaml`` instead.
"""

from __future__ import annotations

MODELS = ("Galaxy A15 5G", "Galaxy A16 5G", "Galaxy A25 5G")

STATUSES = ("received", "resolving", "resolved", "resolution_rejected")

RESOLVED = "resolved"

EVAL_STRATA = ("paraphrase", "literal_token", "sql_routed")
