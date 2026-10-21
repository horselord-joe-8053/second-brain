"""ParadeDB client against a fake cursor. No Docker."""

from __future__ import annotations

from retail_brain.lexical_search.parade_db import ParadeDbLexicalIndex


class _Cur:
    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []

    def execute(self, sql: str, params=None) -> None:
        self.calls.append((sql, params))

    def fetchall(self):
        return [("T-1002",)]


def test_fake_cursor_returns_ids_and_sql() -> None:
    cur = _Cur()
    index = ParadeDbLexicalIndex(cursor=cur)
    ids = index.search_ids("battery drains", k=5, model_filter="Galaxy A16 5G")
    assert ids == ["T-1002"]
    sql, params = cur.calls[-1]
    assert "@@@" in sql
    assert "battery" in " ".join(str(p) for p in params)
    assert "Galaxy A16 5G" in params
