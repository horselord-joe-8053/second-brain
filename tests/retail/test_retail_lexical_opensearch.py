"""OpenSearch client against a fake HTTP transport. Nothing listens on port 9200."""

from __future__ import annotations

from retail_brain.lexical_search.open_search import OpenSearchLexicalIndex


def test_fake_transport_returns_ids() -> None:
    seen: list[tuple[str, str, dict]] = []

    def transport(method: str, path: str, body: dict | None):
        seen.append((method, path, body or {}))
        return {"hits": {"hits": [{"_source": {"ticket_id": "T-1001"}}]}}

    index = OpenSearchLexicalIndex(transport=transport)
    ids = index.search_ids("battery drains", k=5, model_filter="Galaxy A15 5G")
    assert ids == ["T-1001"]
    method, path, body = seen[-1]
    assert method == "POST"
    assert path.endswith("/_search")
    assert body["query"]["bool"]["filter"] == [{"term": {"model": "Galaxy A15 5G"}}]
