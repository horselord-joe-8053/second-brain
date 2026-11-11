"""Load legacy and frozen-v2 insight QA suites without changing retrieval behavior."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

from .eval_suites import TYPE_C_C20, TYPE_W_W20

_INSIGHT_SUITE_IDS = {TYPE_C_C20, TYPE_W_W20}
_INSIGHT_SCHEMAS = {"cos_insight_qa.v1", "cos_insight_qa.v2"}


@dataclass(frozen=True)
class InsightCriterion:
    """One semantic judge criterion and whether missing it materially changes correctness."""

    text: str
    critical: bool


@dataclass(frozen=True)
class CosInsightQuestion:
    """One insight row with legacy-compatible rubric text and v2 metadata."""

    question_id: str
    difficulty: str
    audience: str
    question: str
    gold_answer: str
    criteria: tuple[InsightCriterion, ...]
    question_class: str = ""

    @property
    def rubric(self) -> tuple[str, ...]:
        """Expose criterion text for legacy callers until graded judging replaces them."""
        return tuple(item.text for item in self.criteria)


def load_cos_insight_suite(path: Path, *, require_frozen: bool = False) -> dict[str, Any]:
    """Parse a supported insight suite and optionally require frozen W20 v2 data."""
    data = json.loads(path.read_text(encoding="utf-8"))
    schema = data.get("schema_version")
    if schema not in _INSIGHT_SCHEMAS:
        raise ValueError(f"unsupported schema_version: {data.get('schema_version')!r}")
    suite_id = data.get("eval_suite_id")
    if suite_id is not None and suite_id not in _INSIGHT_SUITE_IDS:
        raise ValueError(f"eval_suite_id must be one of {sorted(_INSIGHT_SUITE_IDS)!r}, got {suite_id!r}")
    qs = data.get("questions")
    if not isinstance(qs, list):
        raise ValueError("questions must be a list")
    if schema == "cos_insight_qa.v2":
        from .w20_authoring import validate_candidate_suite

        validate_candidate_suite(data)
        if require_frozen and data.get("status") != "frozen":
            raise ValueError("W20 v2 suite must be frozen before a benchmark run")
    return data


def iter_cos_insight_questions(data: dict[str, Any]) -> Iterator[CosInsightQuestion]:
    """Yield each insight question in file order."""
    for q in data.get("questions") or []:
        raw_criteria = q.get("criteria") or q.get("rubric") or []
        criteria = []
        for item in raw_criteria:
            if isinstance(item, dict):
                criteria.append(
                    InsightCriterion(
                        text=str(item.get("text") or ""),
                        critical=bool(item.get("critical")),
                    )
                )
            else:
                criteria.append(InsightCriterion(text=str(item), critical=False))
        yield CosInsightQuestion(
            question_id=str(q["id"]),
            difficulty=str(q.get("difficulty") or ""),
            audience=str(q.get("audience") or ""),
            question=str(q.get("question") or ""),
            gold_answer=str(q.get("answer") or ""),
            criteria=tuple(criteria),
            question_class=str(q.get("question_class") or ""),
        )
