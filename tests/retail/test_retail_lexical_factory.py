"""Switch for the keyword leg: default Tantivy, unknown values fail, no Postgres full-text SQL."""

from __future__ import annotations

import pytest

from retail_brain.lexical_search import lexical_backend_name
from retail_brain.pg_search import lexical_ids


def test_default_is_tantivy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("RETAIL_LEXICAL_BACKEND", raising=False)
    assert lexical_backend_name() == "tantivy"


def test_unknown_backend_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RETAIL_LEXICAL_BACKEND", "pg_fts")
    with pytest.raises(ValueError, match="tantivy"):
        lexical_backend_name()


def test_lexical_ids_does_not_use_tsquery(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Cur:
        def __init__(self) -> None:
            self.sql: list[str] = []

        def execute(self, sql: str, params=None) -> None:
            self.sql.append(sql)

        def fetchall(self):
            return []

    class _Index:
        def search_ids(self, query: str, *, k: int, model_filter: str | None = None) -> list[str]:
            assert k == 5
            return ["T-9"]

    monkeypatch.setattr(
        "retail_brain.lexical_search.open_lexical_index",
        lambda: _Index(),
    )
    cur = _Cur()
    assert lexical_ids(cur, "battery drains", model_filter=None, limit=5) == ["T-9"]
    assert cur.sql == []
