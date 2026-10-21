"""Synthetic seed and eval JSONL anti-leakage."""

from pathlib import Path

from retail_brain.eval_gen import build_eval_rows
from retail_brain.seed import generate_tickets, write_manifest


def test_eval_not_verbatim_manifest(tmp_path: Path) -> None:
    rows = generate_tickets(count=10, seed=1)
    manifest = tmp_path / "ticket_manifest.jsonl"
    write_manifest(manifest, rows, seed=1)
    eval_rows = build_eval_rows(manifest, max_rows=5)
    manifest_by_id = {r.ticket_id: r.customer_query_text for r in rows}
    for ev in eval_rows:
        src = ev["source_ticket_id"]
        assert ev["query"].strip() != manifest_by_id[src].strip()
        assert src in ev["expected_ticket_ids"]
        assert len(ev["expected_ticket_ids"]) >= 1


def test_each_ticket_has_unique_stored_text() -> None:
    rows = generate_tickets(count=30, seed=42)
    texts = [r.customer_query_text for r in rows]
    assert len(texts) == len(set(texts))


def test_customer_query_has_no_operational_ids() -> None:
    rows = generate_tickets(count=50, seed=42)
    forbidden = ("Case ref", "ITM-", "ST-", "T-0042")
    for r in rows:
        text = r.customer_query_text
        for token in forbidden:
            assert token not in text, f"{token} leaked into prose for {r.ticket_id}"


def test_eval_query_has_no_operational_ids(tmp_path: Path) -> None:
    rows = generate_tickets(count=20, seed=7)
    manifest = tmp_path / "ticket_manifest.jsonl"
    write_manifest(manifest, rows, seed=7)
    eval_rows = build_eval_rows(manifest, max_rows=10)
    forbidden = ("Case ref", "ITM-", "ST-", "(ref ", "T-0042", "Technician log:")
    for ev in eval_rows:
        for token in forbidden:
            assert token not in ev["query"], ev["eval_id"]


def test_strict_gold_single_expected_id(tmp_path: Path) -> None:
    rows = generate_tickets(count=12, seed=42)
    manifest = tmp_path / "ticket_manifest.jsonl"
    write_manifest(manifest, rows, seed=42)
    eval_rows = build_eval_rows(manifest, max_rows=20)
    for ev in eval_rows:
        assert ev["expected_ticket_ids"] == [ev["source_ticket_id"]]


def test_retail_seed_fixture_has_eval(retail_seed_dir: Path) -> None:
    assert (retail_seed_dir / "ticket_manifest.jsonl").is_file()
    assert (retail_seed_dir / "ticket_retrieval.jsonl").is_file()
    eval_rows = build_eval_rows(retail_seed_dir / "ticket_manifest.jsonl", max_rows=3)
    assert len(eval_rows) >= 1
