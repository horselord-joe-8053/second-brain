"""OpenSearch keyword client. Fusion stays in Python. Tests inject a fake HTTP transport."""

from __future__ import annotations

import json
import os
import urllib.request
from typing import Any, Callable, Optional, Sequence

from retail_brain.text_normalize import fts_query_text, search_text_for_fts

TicketRow = tuple[str, str, Optional[str]]
Transport = Callable[[str, str, dict | None], dict]
INDEX = "retail_tickets"


class OpenSearchLexicalIndex:
    """HTTP client for index ``retail_tickets``; tests pass ``transport`` to avoid a live cluster."""

    def __init__(self, transport: Transport | None = None, base_url: str | None = None) -> None:
        """Inject ``transport`` for tests; else use ``RETAIL_OPENSEARCH_URL``."""
        self._transport = transport
        self._base_url = (base_url if base_url is not None else os.environ.get("RETAIL_OPENSEARCH_URL", "")).rstrip("/")

    def rebuild(self, rows: Sequence[TicketRow]) -> None:
        """Create index mapping then bulk NDJSON ingest (OpenSearch bulk API shape)."""
        try:
            self._call("DELETE", f"/{INDEX}", None)
        except Exception:
            pass  # index may not exist on first rebuild
        self._call(
            "PUT",
            f"/{INDEX}",
            {
                "mappings": {
                    "properties": {
                        "search_text": {"type": "text"},
                        "model": {"type": "keyword"},
                        "ticket_id": {"type": "keyword"},
                    }
                }
            },
        )
        lines: list[str] = []
        for ticket_id, text, model in rows:
            lines.append(json.dumps({"index": {"_index": INDEX, "_id": ticket_id}}))
            lines.append(
                json.dumps(
                    {
                        "ticket_id": ticket_id,
                        "search_text": search_text_for_fts(text or ""),
                        "model": model or "",
                    }
                )
            )
        if lines:
            # Real urllib path would send raw NDJSON; fake transport receives structured body in tests.
            self._call("POST", f"/{INDEX}/_bulk", {"ndjson": "\n".join(lines) + "\n"})

    def search_ids(self, query: str, *, k: int, model_filter: str | None = None) -> list[str]:
        """Bool query on ``search_text`` with optional ``model`` term filter."""
        q = fts_query_text(query) or query
        filt = [{"term": {"model": model_filter}}] if model_filter else []
        body = {
            "size": k,
            "query": {
                "bool": {
                    "must": {"match": {"search_text": q}},
                    "filter": filt,
                }
            },
        }
        payload = self._call("POST", f"/{INDEX}/_search", body)
        hits = ((payload.get("hits") or {}).get("hits")) or []
        out: list[str] = []
        for hit in hits:
            source = hit.get("_source") or {}
            tid = source.get("ticket_id") or hit.get("_id")
            if tid:
                out.append(str(tid))
        return out

    def _call(self, method: str, path: str, body: dict | None) -> dict:
        """HTTP JSON call via injected transport or urllib against ``base_url``."""
        if self._transport is not None:
            return self._transport(method, path, body)
        if not self._base_url:
            raise RuntimeError(
                "RETAIL_OPENSEARCH_URL is not set. OpenSearch is a separate service; "
                "default verify does not start it."
            )
        content_type = "application/json"
        if body is not None and "ndjson" in body:
            data = body["ndjson"].encode("utf-8")
            content_type = "application/x-ndjson"
        elif body is None:
            data = None
        else:
            data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            self._base_url + path,
            data=data,
            method=method,
            headers={"Content-Type": content_type},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else {}
