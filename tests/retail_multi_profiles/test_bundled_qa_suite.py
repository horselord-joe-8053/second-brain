"""TYPE_B_B20 / B20-technical-compound bundled gold fixture contract tests."""

from __future__ import annotations

import csv
from pathlib import Path

from tests.retail_multi_profiles.lib.eval_suites import TYPE_B_B20, TYPE_B_B20_LONG

REPO = Path(__file__).resolve().parents[2]
TYPE_B_B20_SUITE_JSON = REPO / "tests" / "retail_multi_profiles" / "data" / "retail-bundled-qa-b20.json"


def test_bundled_b20_shape_and_ticket_ids_in_corpus() -> None:
    """Twenty-six rows (prior 24 + H10N-alt rerank arms), 12 easy / 14 hard; expected tickets in FRU CSV."""
    from tests.retail_multi_profiles.lib.load_bundled_suite import iter_bundled_questions, load_bundled_suite

    data = load_bundled_suite(TYPE_B_B20_SUITE_JSON)
    assert data.get("eval_suite_id") == TYPE_B_B20
    assert data.get("eval_suite_long_name") == TYPE_B_B20_LONG
    rows = list(iter_bundled_questions(data))
    assert len(rows) == 26
    easy = sum(1 for r in rows if r.difficulty == "easy")
    hard = sum(1 for r in rows if r.difficulty == "hard")
    assert easy == 12
    assert hard == 14

    import sys

    retail_pkg = REPO / "scripts" / "retail"
    if str(retail_pkg) not in sys.path:
        sys.path.insert(0, str(retail_pkg))
    from retail_brain.sim_data_profile import resolve_sim_data_profile

    fru_csv = resolve_sim_data_profile().service_queries_csv
    assert fru_csv.is_file(), f"missing corpus {fru_csv}"
    ticket_ids: set[str] = set()
    with fru_csv.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            tid = row.get("ticket_id") or row.get("id")
            if tid:
                ticket_ids.add(str(tid))

    from tests.retail_multi_profiles.lib.bundled_gold_contract import (
        assert_expected_tickets_resolved,
        load_ticket_status_by_id,
    )

    status_by_id = load_ticket_status_by_id(fru_csv)

    for q in rows:
        assert q.model_id, q.question_id
        assert q.expected_ticket_ids, q.question_id
        for tid in q.expected_ticket_ids:
            assert tid in ticket_ids, f"{q.question_id} unknown ticket {tid}"
        assert_expected_tickets_resolved(
            q.expected_ticket_ids, status_by_id, question_id=q.question_id
        )


def test_rewritten_failure_questions_do_not_reveal_repairs() -> None:
    """Natural customer prompts must ask for service knowledge without embedding the gold repair."""
    from tests.retail_multi_profiles.lib.load_bundled_suite import iter_bundled_questions, load_bundled_suite

    questions = {
        q.question_id: q.question.lower()
        for q in iter_bundled_questions(load_bundled_suite(TYPE_B_B20_SUITE_JSON))
    }
    forbidden = {
        "BND-E03": ("bin auger seal", "adjusted freezer temperature"),
        "BND-E08": ("clogged inline filter", "flushed the water line"),
        "BND-H02": ("display board", "updated firmware"),
        "BND-H07": ("defrost drain tube", "heater-wire kit"),
        "BND-H08": ("inline filter", "flushed the water line"),
        "BND-H10": ("start relay", "condenser mounts"),
    }
    for question_id, leaked_phrases in forbidden.items():
        question = questions[question_id]
        for phrase in leaked_phrases:
            assert phrase not in question, f"{question_id} leaks gold phrase: {phrase}"
        for harness_phrase in ("past service", "similar case", "resolved case", "user guide says"):
            assert harness_phrase not in question, f"{question_id} exposes harness wording: {harness_phrase}"


def test_ambient_alt_tickets_share_parent_gold() -> None:
    """E08N-alt / H10N-alt are query-only variants; labels match BND-E08 / BND-H10."""
    from tests.retail_multi_profiles.lib.load_bundled_suite import load_bundled_suite

    data = load_bundled_suite(TYPE_B_B20_SUITE_JSON)
    assert data.get("eval_suite_id") == TYPE_B_B20
    assert data.get("eval_suite_long_name") == TYPE_B_B20_LONG
    by_id = {q["id"]: q for q in data["questions"]}
    pairs = (
        ("BND-E08N-alt", "BND-E08"),
        ("BND-H10N-alt", "BND-H10"),
        ("BND-H10N-site", "BND-H10"),
        ("BND-H10N-alt-rr-xenc", "BND-H10"),
        ("BND-H10N-alt-rr-llm", "BND-H10"),
    )
    for alt_id, parent_id in pairs:
        alt = by_id[alt_id]
        parent = by_id[parent_id]
        assert alt["expected_ticket_ids"] == parent["expected_ticket_ids"]
        assert alt["manual_anchor_question_id"] == parent["manual_anchor_question_id"]
        assert alt["answer"] == parent["answer"]
        assert alt["model"] == parent["model"]
        assert alt["question"] != parent["question"]


def test_h10n_rerank_arms_copy_alt_question() -> None:
    """Rerank probe rows keep the H10N-alt question and name their manual rerank arm."""
    from tests.retail_multi_profiles.lib.load_bundled_suite import load_bundled_suite

    data = load_bundled_suite(TYPE_B_B20_SUITE_JSON)
    assert data.get("eval_suite_id") == TYPE_B_B20
    assert data.get("eval_suite_long_name") == TYPE_B_B20_LONG
    by_id = {q["id"]: q for q in data["questions"]}
    base = by_id["BND-H10N-alt"]
    assert "manual_rerank" not in base
    expected = {
        "BND-H10N-alt-rr-xenc": "cross_encoder",
        "BND-H10N-alt-rr-llm": "llm_listwise",
    }
    for qid, backend in expected.items():
        row = by_id[qid]
        assert row["question"] == base["question"]
        assert row["manual_rerank"] == backend
        assert row["difficulty"] == "hard"
