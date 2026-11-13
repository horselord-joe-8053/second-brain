"""Checkpoint keys and JSONL progress for lane benchmark runs."""

from __future__ import annotations

import json
from pathlib import Path

from logging_utils.run_progress import (
    completed_row_keys,
    progress_row_key,
    read_jsonl,
    write_jsonl_line,
)


def test_progress_row_key_stable() -> None:
    """Resume identity is lane plus question_id."""
    assert progress_row_key("B", "samsung_RF28K9070SG-E01") == "B|samsung_RF28K9070SG-E01"


def test_completed_row_keys_from_results_jsonl(tmp_path: Path) -> None:
    """Parse finished rows for --resume skip set."""
    path = tmp_path / "results.jsonl"
    write_jsonl_line(
        path,
        {"type": "result", "row": {"lane": "A", "question_id": "q1", "pass": True}},
    )
    write_jsonl_line(
        path,
        {"type": "progress", "step": "judge_start", "lane": "A", "question_id": "q2"},
    )
    write_jsonl_line(
        path,
        {"type": "result", "row": {"lane": "A", "question_id": "q2", "pass": False}},
    )
    assert completed_row_keys(path) == {"A|q1", "A|q2"}


def test_last_progress_event_shows_active_ticket(tmp_path: Path) -> None:
    """When a run dies mid-row, the last progress line names lane + question + step."""
    path = tmp_path / "results.jsonl"
    write_jsonl_line(
        path,
        {"type": "progress", "step": "answer_done", "lane": "C", "question_id": "ge_GNE27JYMFS-H03", "index": 41},
    )
    write_jsonl_line(
        path,
        {"type": "progress", "step": "judge_start", "lane": "C", "question_id": "ge_GNE27JYMFS-H03", "index": 41},
    )
    lines = read_jsonl(path)
    last = lines[-1]
    assert last["step"] == "judge_start"
    assert last["question_id"] == "ge_GNE27JYMFS-H03"
