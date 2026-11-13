"""Load TYPE_A_M90 / M90-technical-singlefact manual QA benchmark JSON."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

from .eval_suites import TYPE_A_M90


@dataclass(frozen=True)
class SuiteQuestion:
    """One benchmark row with SKU context."""

    model_id: str
    question_id: str
    difficulty: str
    question: str
    gold_answer: str


def load_suite(path: Path) -> dict[str, Any]:
    """Parse suite JSON and validate top-level schema."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != "1.0":
        raise ValueError(f"unsupported schema_version: {data.get('schema_version')!r}")
    if not isinstance(data.get("models"), list):
        raise ValueError("models must be a list")
    suite_id = data.get("eval_suite_id")
    if suite_id is not None and suite_id != TYPE_A_M90:
        raise ValueError(f"eval_suite_id must be {TYPE_A_M90!r}, got {suite_id!r}")
    return data


def iter_questions(data: dict[str, Any]) -> Iterator[SuiteQuestion]:
    """Yield every question across all model leaves."""
    for model in data["models"]:
        model_id = str(model["model_id"])
        for q in model.get("questions") or []:
            yield SuiteQuestion(
                model_id=model_id,
                question_id=str(q["id"]),
                difficulty=str(q.get("difficulty") or ""),
                question=str(q["question"]),
                gold_answer=str(q.get("answer") or ""),
            )


def filter_question_ids(data: dict[str, Any], ids: set[str]) -> list[SuiteQuestion]:
    """Return questions whose id is in ids, preserving suite order."""
    want = set(ids)
    return [q for q in iter_questions(data) if q.question_id in want]
