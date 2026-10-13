"""Samsung retail service brain — seed, search, eval, and agent sidecar helpers.

Postgres (pgvector) is the system of record for tickets. Search splits into:
  - ``pg_search`` — production path: embed in PG, keyword ids from ``lexical_search/``, RRF in Python.
  - ``hybrid_search`` — in-memory CSV rows for unit tests and offline eval (no PG, simpler lexical leg).

Config knobs live in env (``RETAIL_TICKET_SEARCH_MODE``, ``RETAIL_LEXICAL_BACKEND``, market, sim profile).
"""
