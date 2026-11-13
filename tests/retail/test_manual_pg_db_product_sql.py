"""evo-18 T0 — manual_chunks SQL product filter on list and KNN."""

from __future__ import annotations

from unittest.mock import MagicMock

from retail_brain.manual_pg_db import knn_manual_chunks, list_manual_chunks


def test_list_manual_chunks_adds_brand_oem_predicates() -> None:
    """list_manual_chunks passes brand and oem_model into WHERE."""
    cur = MagicMock()
    cur.fetchall.return_value = []
    list_manual_chunks(
        cur,
        lane_id="B",
        limit=100,
        brand="GE",
        oem_model="GNE27JYMFS",
    )
    sql = cur.execute.call_args[0][0]
    assert "brand = %s" in sql
    assert "oem_model = %s" in sql
    assert cur.execute.call_args[0][1] == ("B", "GE", "GNE27JYMFS", 100)


def test_knn_manual_chunks_adds_brand_oem_predicates() -> None:
    """knn_manual_chunks scopes vector search by product columns."""
    cur = MagicMock()
    cur.fetchall.return_value = []
    knn_manual_chunks(
        cur,
        lane_id="B",
        query_vector=[0.1, 0.2],
        limit=5,
        brand="Samsung",
        oem_model="RF28K9070SG",
    )
    sql = cur.execute.call_args[0][0]
    assert "brand = %s" in sql
    assert "oem_model = %s" in sql
