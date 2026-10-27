"""Load and validate the B20 bundled manual+ticket QA JSON."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator


@dataclass(frozen=True)
class BundledQuestion:
    """One B20 row: judged answer plus ticket retrieval label."""

    question_id: str
    difficulty: str
    model_id: str
    question: str
    gold_answer: str
    expected_ticket_ids: tuple[str, ...]
    manual_anchor_question_id: str


def load_bundled_suite(path: Path) -> dict[str, Any]:
    """Parse bundled_qa.v1 JSON."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != "bundled_qa.v1":
        raise ValueError(f"unsupported schema_version: {data.get('schema_version')!r}")
    qs = data.get("questions")
    if not isinstance(qs, list):
        raise ValueError("questions must be a list")
    return data


def iter_bundled_questions(data: dict[str, Any]) -> Iterator[BundledQuestion]:
    """Yield each bundled question in file order."""
    for q in data.get("questions") or []:
        ids = q.get("expected_ticket_ids") or []
        yield BundledQuestion(
            question_id=str(q["id"]),
            difficulty=str(q.get("difficulty") or ""),
            model_id=str(q.get("model") or ""),
            question=str(q.get("question") or ""),
            gold_answer=str(q.get("answer") or ""),
            expected_ticket_ids=tuple(str(x) for x in ids),
            manual_anchor_question_id=str(q.get("manual_anchor_question_id") or ""),
        )


def filter_bundled_ids(data: dict[str, Any], ids: set[str]) -> list[BundledQuestion]:
    """Return questions whose id is in ids, preserving file order."""
    want = set(ids)
    return [q for q in iter_bundled_questions(data) if q.question_id in want]
