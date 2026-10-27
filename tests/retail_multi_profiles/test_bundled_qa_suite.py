"""B20 bundled gold fixture contract tests."""

from __future__ import annotations

import csv
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
B20 = REPO / "tests" / "retail_multi_profiles" / "data" / "retail-bundled-qa-b20.json"


def test_bundled_b20_shape_and_ticket_ids_in_corpus() -> None:
    """Twenty rows, 10 easy / 10 hard; every expected ticket id exists in FRU CSV."""
    from tests.retail_multi_profiles.lib.load_bundled_suite import iter_bundled_questions, load_bundled_suite

    data = load_bundled_suite(B20)
    rows = list(iter_bundled_questions(data))
    assert len(rows) == 20
    easy = sum(1 for r in rows if r.difficulty == "easy")
    hard = sum(1 for r in rows if r.difficulty == "hard")
    assert easy == 10
    assert hard == 10

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

    for q in rows:
        assert q.model_id, q.question_id
        assert q.expected_ticket_ids, q.question_id
        for tid in q.expected_ticket_ids:
            assert tid in ticket_ids, f"{q.question_id} unknown ticket {tid}"


def test_rewritten_failure_questions_do_not_reveal_repairs() -> None:
    """Natural customer prompts must ask for service knowledge without embedding the gold repair."""
    from tests.retail_multi_profiles.lib.load_bundled_suite import iter_bundled_questions, load_bundled_suite

    questions = {q.question_id: q.question.lower() for q in iter_bundled_questions(load_bundled_suite(B20))}
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
