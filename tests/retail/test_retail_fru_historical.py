"""FRU historical generator diversity and IO round-trip."""

import os
from collections import Counter
from pathlib import Path

import pytest

from sim_data.generation.fru_tickets import generate_fru_historical, load_customers
from sim_data.generation.io import read_csv, write_csv, write_manifest


@pytest.fixture(autouse=True)
def _fru_prefix(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RETAIL_FAULT_CODE_PREFIX", "FRU-E")


def test_fru_historical_diversity() -> None:
    rows = generate_fru_historical(seed=20261015, count=1000)
    assert len(rows) == 1000
    keys = {r.issue_key for r in rows if r.issue_key}
    assert len(keys) >= 24
    issue_counts = Counter(r.issue_key for r in rows)
    max_share = max(issue_counts.values()) / len(rows)
    assert max_share <= 0.12
    models = Counter(r.model for r in rows)
    for share in (c / len(rows) for c in models.values()):
        assert 0.25 <= share <= 0.42
    customers = load_customers()
    expected_stores = {c["store_name"] for c in customers}
    ticket_stores = {r.store_id for r in rows}
    assert len(expected_stores) >= 10
    for name in expected_stores:
        slug = name.lower().replace(" ", "-").replace("'", "")
        assert f"store-{slug}" in ticket_stores
    texts = {r.customer_query_text.lower() for r in rows}
    assert len(texts) == len(rows)


def test_fru_csv_manifest_roundtrip(tmp_path: Path) -> None:
    rows = generate_fru_historical(seed=99, count=20)
    csv_path = tmp_path / "service_queries.csv"
    manifest = tmp_path / "ticket_manifest.jsonl"
    write_csv(csv_path, rows)
    write_manifest(manifest, rows, seed=99)
    back = read_csv(csv_path, manifest_path=manifest)
    for orig, got in zip(rows, back):
        assert got.customer_id == orig.customer_id
        assert got.issue_key == orig.issue_key
        assert got.fault_code == orig.fault_code
