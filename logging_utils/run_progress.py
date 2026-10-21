"""JSONL checkpoint + progress events for long retail lane benchmark runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator


def progress_row_key(lane_id: str, question_id: str) -> str:
    """Stable resume key for one (lane, question) pair."""
    return f"{lane_id}|{question_id}"


def write_jsonl_line(path: Path, record: dict[str, Any]) -> None:
    """Append one JSON object and flush (durable progress for operators)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        fh.flush()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load all JSONL records; empty file → []."""
    if not path.is_file():
        return []
    out: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        out.append(json.loads(line))
    return out


def completed_row_keys(jsonl_path: Path) -> set[str]:
    """Row keys already written as ``type: result`` records."""
    keys: set[str] = set()
    for rec in read_jsonl(jsonl_path):
        if rec.get("type") != "result":
            continue
        row = rec.get("row") or {}
        lane = str(row.get("lane") or "")
        qid = str(row.get("question_id") or "")
        if lane and qid:
            keys.add(progress_row_key(lane, qid))
    return keys


def last_progress_event(jsonl_path: Path) -> dict[str, Any] | None:
    """Most recent ``type: progress`` line (shows where a crash likely occurred)."""
    last: dict[str, Any] | None = None
    for rec in read_jsonl(jsonl_path):
        if rec.get("type") == "progress":
            last = rec
    return last


def iter_result_rows(jsonl_path: Path) -> Iterator[dict[str, Any]]:
    """Yield result dicts from checkpoint file in file order."""
    for rec in read_jsonl(jsonl_path):
        if rec.get("type") == "result" and isinstance(rec.get("row"), dict):
            yield rec["row"]
