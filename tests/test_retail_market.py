"""RETAIL_MARKET drives seed copy and Postgres full-text config."""

import os

import pytest

from retail_brain.eval_gen import paraphrase_query
from retail_brain.market import market_code, market_profile, pg_ts_config
from retail_brain.seed import generate_tickets


def test_default_market_is_au(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("RETAIL_MARKET", raising=False)
    assert market_code() == "AU"
    assert pg_ts_config() == "english"
    assert market_profile()["bcp47"] == "en-AU"


def test_br_market_portuguese_ts(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RETAIL_MARKET", "BR")
    assert pg_ts_config() == "portuguese"
    row = generate_tickets(count=1, seed=1, market="BR")[0]
    assert row.customer_query_text.startswith("Cliente relata:")
    assert row.state in ("SP", "RJ", "BA")


def test_au_seed_english_copy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RETAIL_MARKET", "AU")
    row = generate_tickets(count=1, seed=1)[0]
    assert row.customer_query_text.startswith("Customer reports:")
    assert row.state in ("NSW", "VIC", "QLD")
    assert "São" not in row.city


def test_paraphrase_follows_market_template(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RETAIL_MARKET", "AU")
    text = "Customer reports: battery drains quickly on Galaxy A16 5G."
    q = paraphrase_query(text, "T-0042-000001")
    assert q.startswith("Need help:")
    assert "Customer reports:" not in q


def test_unknown_market_fails_fast(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RETAIL_MARKET", "XX")
    with pytest.raises(ValueError, match="RETAIL_MARKET"):
        market_code()
