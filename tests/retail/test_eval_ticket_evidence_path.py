"""P2.5 — evidence-path eval row shape (mock search, no live Postgres)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from retail_brain.ticket_evidence_eval import run_evidence_path_row, write_evidence_jsonl

REPO = Path(__file__).resolve().parents[2]


def _mock_search(
    _dsn: str,
    _query: str,
    *,
    model_filter: str | None = None,
    limit: int = 5,
) -> tuple[str, list[dict[str, Any]]]:
    return (
        "rrf_term_boosted",
        [
            {
                "ticket_id": "T-0042-000001",
                "model": model_filter or "",
                "customer_query_text": "black screen",
                "resolution_text": "fixed",
            },
        ],
    )


def test_evidence_path_retriever_emits_jsonl_fields(tmp_path) -> None:
    case = {
        "eval_id": "eval-0001",
        "query": "black screen update",
        "model_filter": "Galaxy A15 5G",
        "expected_ticket_ids": ["T-0042-000001"],
        "stratum": "paraphrase",
    }
    row = run_evidence_path_row(
        case,
        dsn="postgresql://mock",
        mode="retriever",
        repo_root=REPO,
        search_fn=_mock_search,
    )
    assert row["hit_strict"] is True
    assert row["evidence_path"] == "retriever"
    assert row["top_ticket_id"] == "T-0042-000001"
    out = tmp_path / "rows.jsonl"
    write_evidence_jsonl([row], out)
    assert "eval-0001" in out.read_text(encoding="utf-8")
