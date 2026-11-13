"""TYPE_C_C20 fixture and mock dual-arm runner."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.retail_multi_profiles.lib.cos_insight_runner import (
    CosInsightRunContext,
    run_cos_insight_benchmark,
    run_cos_insight_row,
    score_insight_graded,
    score_insight_judged,
)
from tests.retail_multi_profiles.lib.eval_models import EvalLlm, assert_independent_eval_providers
from tests.retail_multi_profiles.lib.eval_suites import (
    TYPE_C_C20,
    TYPE_C_C20_LONG,
    TYPE_W_W20,
    W20_SUITE_DEFAULT_PATH,
)
from tests.retail_multi_profiles.lib.load_cos_insight_suite import (
    CosInsightQuestion,
    InsightCriterion,
    iter_cos_insight_questions,
    load_cos_insight_suite,
)
from tests.retail_multi_profiles.run_cos_insight_qa import select_smoke_rows

REPO = Path(__file__).resolve().parents[2]
SUITE = REPO / "tests" / "retail_multi_profiles" / "data" / "retail-cos-insight-test-suite.json"
W20_SUITE = REPO / W20_SUITE_DEFAULT_PATH


def test_cos_insight_suite_shape() -> None:
    """Twenty rows with eval_suite_id TYPE_C_C20."""
    data = load_cos_insight_suite(SUITE)
    assert data.get("eval_suite_id") == TYPE_C_C20
    assert data.get("eval_suite_long_name") == TYPE_C_C20_LONG
    rows = list(iter_cos_insight_questions(data))
    assert len(rows) == 20
    easy = sum(1 for r in rows if r.difficulty == "easy")
    hard = sum(1 for r in rows if r.difficulty == "hard")
    assert easy == 10
    assert hard == 10


def test_w20_suite_loads() -> None:
    """TYPE_W_W20 has 20 synthesis rows and is accepted by the insight loader."""
    data = load_cos_insight_suite(W20_SUITE)
    assert data.get("eval_suite_id") == TYPE_W_W20
    rows = list(iter_cos_insight_questions(data))
    assert len(rows) == 20
    assert rows[0].question_id == "W01"
    assert rows[-1].question_id == "W20"


def test_w20_v2_smoke_falls_back_to_global_and_boundary_rows() -> None:
    """Stale legacy smoke ids select one global and one boundary v2 row."""
    suite = REPO / "tests" / "retail_multi_profiles" / "data" / "retail-w20-focused-synthesis-v2.json"
    rows = list(iter_cos_insight_questions(load_cos_insight_suite(suite, require_frozen=True)))
    selected = select_smoke_rows(rows, ["COS-C01", "COS-H01"])
    assert len(selected) == 2
    assert selected[0].question_class.startswith("global_")
    assert selected[1].question_class == "boundary_local"


def test_suite_gold_is_manual_orientation() -> None:
    """Adopted gold is prose from the manuals, with no fixture auto-pass token."""
    data = load_cos_insight_suite(SUITE)
    for q in iter_cos_insight_questions(data):
        assert "GOLD_MARK" not in q.gold_answer
        assert len(q.gold_answer) > 200
        assert len(q.rubric) == 4


def test_score_insight_reads_judge_json() -> None:
    """Judge pass follows the JSON the grader model returns."""

    def _fake(prompt: str, **_kwargs: object) -> str:
        return '{"pass": true, "rationale": "meets rubric"}'

    ok, why = score_insight_judged(
        "q",
        "gold text",
        "candidate text",
        ("r1",),
        provider="gemini",
        model="mock",
        llm_generate=_fake,
    )
    assert ok
    assert "rubric" in why


def _graded_payload(
    *,
    correctness: int = 4,
    completeness: int = 3,
    grounding: int = 4,
    unsupported: int = 0,
    confidence: float = 0.9,
    criterion_status: str = "met",
    contradiction: bool = False,
    citation_score: int = 0,
) -> str:
    """Build one deterministic graded-judge response."""
    import json

    return json.dumps(
        {
            "correctness": correctness,
            "completeness": completeness,
            "manual_grounding": grounding,
            "unsupported_claims": unsupported,
            "citation_score": citation_score,
            "correctness_confidence": confidence,
            "verdict": "mostly_correct",
            "criterion_scores": [
                {
                    "index": 0,
                    "status": criterion_status,
                    "contradiction": contradiction,
                    "reason": "test reason",
                }
            ],
            "rationale": "graded rationale",
        }
    )


def test_graded_judge_gives_partial_credit_for_noncritical_omission() -> None:
    """Missing a non-critical criterion lowers quality without forcing failure."""
    result = score_insight_graded(
        "Question",
        "Gold",
        "Candidate",
        (InsightCriterion("Optional nuance", critical=False),),
        question_id="W20-01",
        provider="gemini",
        model="judge",
        llm_generate=lambda _prompt, **_kwargs: _graded_payload(criterion_status="not_met"),
    )
    assert result["overall_score"] > 70
    assert result["judge_pass"] is True


def test_graded_judge_caps_missed_and_contradicted_critical_claims() -> None:
    """A missed critical claim caps at 69; directly contradicting it caps at 49."""
    criterion = (InsightCriterion("Required claim", critical=True),)
    missed = score_insight_graded(
        "Question",
        "Gold",
        "Candidate",
        criterion,
        question_id="W20-02",
        provider="gemini",
        model="judge",
        llm_generate=lambda _prompt, **_kwargs: _graded_payload(criterion_status="not_met"),
    )
    contradicted = score_insight_graded(
        "Question",
        "Gold",
        "Candidate",
        criterion,
        question_id="W20-02",
        provider="gemini",
        model="judge",
        llm_generate=lambda _prompt, **_kwargs: _graded_payload(
            criterion_status="not_met",
            contradiction=True,
        ),
    )
    assert missed["overall_score"] == 69
    assert contradicted["overall_score"] == 49
    assert missed["judge_pass"] is False
    assert contradicted["judge_pass"] is False


def test_graded_judge_keeps_citations_separate_and_prompt_blind() -> None:
    """Citation score does not change semantics, and arm labels never enter the judge prompt."""
    prompts: list[str] = []

    def _fake(prompt: str, **_kwargs: object) -> str:
        prompts.append(prompt)
        return _graded_payload(citation_score=0)

    result = score_insight_graded(
        "Question",
        "Gold",
        "Candidate answer",
        (InsightCriterion("Required", critical=True),),
        question_id="W20-03",
        provider="gemini",
        model="judge",
        llm_generate=_fake,
    )
    assert result["overall_score"] > 70
    assert result["citation_score"] == 0
    assert result["candidate_id"] == score_insight_graded(
        "Question",
        "Gold",
        "Candidate answer",
        (InsightCriterion("Required", critical=True),),
        question_id="W20-03",
        provider="gemini",
        model="judge",
        llm_generate=_fake,
    )["candidate_id"]
    assert "wiki" not in prompts[0].lower()
    assert "bundled" not in prompts[0].lower()
    assert '"arm"' not in prompts[0].lower()


def test_author_and_judge_providers_must_differ() -> None:
    """An author cannot grade its own suite through the same provider family."""
    with pytest.raises(ValueError, match="different providers"):
        assert_independent_eval_providers("openai", "openai")
    assert_independent_eval_providers("openai", "gemini")


def test_run_cos_insight_bundled_arm_mock() -> None:
    """A3 arm uses injected retrieval and does not emit a stub answer."""
    data = load_cos_insight_suite(SUITE)
    q = next(iter_cos_insight_questions(data))
    ctx = CosInsightRunContext(
        repo=REPO,
        run_id="test",
        out_dir=REPO / "tmp",
        results_path=REPO / "tmp" / "x.jsonl",
        cfg={"search_top_k": 5, "page_prefix_chars": 1000},
    )
    ans = EvalLlm("openai", "gpt-4o-mini", 0.0)
    judge = EvalLlm("gemini", "mock", 0.0)

    def _retrieve(_ctx: CosInsightRunContext, _question: str):
        return [{"path": "manual/ge.md", "source_relpath": "manual/ge.md", "text": "37 F"}], "37 F setpoint", 3

    def _fake(prompt: str, **_kwargs: object) -> str:
        if "strict grader" in prompt:
            return '{"pass": true, "rationale": "orientation matches"}'
        return "Brief staff to wait for stabilization before calling a part failed."

    row = run_cos_insight_row(
        ctx,
        q,
        arm="bundled",
        wiki=None,
        answer_llm=ans,
        judge_llm=judge,
        llm_generate=_fake,
        bundled_retrieve=_retrieve,
    )
    assert row["judge_pass"] is True
    assert row["arm"] == "bundled"
    assert "GOLD_MARK" not in row["candidate"]
    assert row["top_hit_paths"] == ["manual/ge.md"]


def test_benchmark_resume_skips_completed_question_arm_pair(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A resumed live run appends only tasks absent from its existing results."""
    from tests.retail_multi_profiles.lib import cos_insight_runner

    question = CosInsightQuestion(
        question_id="W20_TEST",
        difficulty="",
        audience="staff",
        question="Question",
        gold_answer="Gold",
        criteria=(InsightCriterion("Required", critical=True),),
        question_class="global_cross_brand",
    )
    answer = EvalLlm("openai", "answer", 0.0)
    judge = EvalLlm("gemini", "judge", 0.0)
    calls: list[tuple[str, str]] = []

    monkeypatch.setattr(cos_insight_runner, "load_merged_run_config", lambda _repo: {})
    monkeypatch.setattr(cos_insight_runner, "resolve_eval_llms", lambda _cfg: (answer, judge))

    def _row(_ctx: CosInsightRunContext, q: CosInsightQuestion, *, arm: str, **_kwargs: object) -> dict:
        calls.append((q.question_id, arm))
        return {"question_id": q.question_id, "arm": arm, "candidate_id": "opaque"}

    monkeypatch.setattr(cos_insight_runner, "run_cos_insight_row", _row)
    run_cos_insight_benchmark(tmp_path, [question], run_id="resume", arms=("bundled",))
    run_cos_insight_benchmark(tmp_path, [question], run_id="resume", arms=("bundled",), resume=True)

    results = (tmp_path / "ops" / "runs" / "retail-cos-insight" / "resume" / "results.jsonl").read_text()
    assert calls == [("W20_TEST", "bundled")]
    assert results.count('"question_id": "W20_TEST"') == 1
