"""Contracts for W20 v2 authoring, validation, freezing, and provenance."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from tests.retail_multi_profiles.lib.w20_authoring import (
    AUTHOR_PROMPT,
    BRIEFING_AUTHOR_PROMPT,
    BLINDING_SEED,
    COMPATIBILITY_PASS_SCORE,
    GLOBAL_ADVANTAGE_MARGIN,
    HUMAN_REVIEW_CONFIDENCE,
    approve_candidate,
    author_candidate,
    build_pdf_evidence_request,
    build_synthesis_request,
    freeze_candidate,
    parse_author_response,
    validate_candidate_suite,
)
from tests.retail_multi_profiles.lib.load_cos_insight_suite import load_cos_insight_suite


def _question(index: int, question_class: str) -> dict[str, object]:
    """Build one valid W20 v2 row for contract tests."""
    cross_brand = question_class == "global_cross_brand"
    sources = [
        {"file": "ge_GNE27JYMFS/user-guide.pdf", "location": "Controls"},
        {"file": "kitchenaid_KRFF507HPS/user-guide.pdf", "location": "Using the Controls"},
        {"file": "samsung_RF28K9070SG/user-guide.pdf", "location": "Feature panel"},
    ]
    if question_class == "boundary_local":
        sources = [{"file": "ge_GNE27JYMFS/user-guide.pdf", "location": "Controls"}]
    elif not cross_brand:
        sources = [
            {"file": "samsung_RF28K9070SG/user-guide.pdf", "location": f"Section {n}"}
            for n in range(1, 4)
        ]
    return {
        "id": f"W{index:02d}",
        "question_class": question_class,
        "audience": "training_lead",
        "question": f"What broad operating pattern should a lead teach for scenario {index}?",
        "answer": "A manual-grounded synthesis spanning the referenced sections.",
        "criteria": [
            {"text": "Identifies the main shared pattern", "critical": True},
            {"text": "Preserves meaningful brand differences", "critical": False},
            {"text": "Avoids unsupported operational advice", "critical": True},
        ],
        "authoring": {
            "human_verified": False,
            "sources": sources,
            "source_brands": ["GE", "KitchenAid"] if cross_brand else ["Samsung"],
        },
    }


def _suite() -> dict[str, object]:
    """Build the exact 12/4/4 candidate distribution."""
    classes = ["global_cross_brand"] * 12 + ["global_single_brand"] * 4 + ["boundary_local"] * 4
    return {
        "schema_version": "cos_insight_qa.v2",
        "eval_suite_id": "TYPE_W_W20",
        "status": "candidate",
        "questions": [_question(i + 1, value) for i, value in enumerate(classes)],
    }


def test_candidate_accepts_exact_construct_distribution() -> None:
    """A schema-valid 12/4/4 suite passes candidate validation."""
    validate_candidate_suite(_suite())


def test_briefing_construct_accepts_twenty_cross_manual_questions() -> None:
    """W20-D13 accepts 20 cross-brand briefings and rejects a local control row."""
    questions = [_question(index + 1, "global_cross_brand") for index in range(20)]
    suite = {
        "schema_version": "cos_insight_qa.v2",
        "eval_suite_id": "TYPE_W_W20",
        "construct": "briefing_v3",
        "status": "candidate",
        "questions": questions,
    }
    validate_candidate_suite(suite)
    questions[0]["question_class"] = "boundary_local"
    with pytest.raises(ValueError, match="unsupported question_class"):
        validate_candidate_suite(suite)


def test_briefing_synthesis_uses_pattern_prompt() -> None:
    """The briefing request asks for patterns and forbids local-fact question classes."""
    packets = [{"manual": {"file": f"manual-{index}.pdf"}, "sections": []} for index in range(4)]
    body = build_synthesis_request(packets, model="gpt-author-strong", construct="briefing_v3")
    text = body["input"][0]["content"][0]["text"]
    enum_values = body["text"]["format"]["schema"]["properties"]["questions"]["items"]["properties"][
        "question_class"
    ]["enum"]
    assert BRIEFING_AUTHOR_PROMPT in text
    assert enum_values == ["global_cross_brand"]


def test_candidate_rejects_wrong_construct_distribution() -> None:
    """Changing one global row into a boundary row violates the frozen distribution."""
    suite = _suite()
    questions = suite["questions"]
    assert isinstance(questions, list)
    questions[0]["question_class"] = "boundary_local"
    with pytest.raises(ValueError, match="12 global_cross_brand"):
        validate_candidate_suite(suite)


def test_candidate_rejects_global_row_without_three_sections() -> None:
    """A global question cannot be answerable from fewer than three references."""
    suite = _suite()
    questions = suite["questions"]
    assert isinstance(questions, list)
    questions[0]["authoring"]["sources"] = questions[0]["authoring"]["sources"][:2]
    with pytest.raises(ValueError, match="three source sections"):
        validate_candidate_suite(suite)


def test_candidate_rejects_cross_brand_row_without_two_brands() -> None:
    """A cross-brand question must identify at least two source brands."""
    suite = _suite()
    questions = suite["questions"]
    assert isinstance(questions, list)
    questions[0]["authoring"]["source_brands"] = ["GE"]
    with pytest.raises(ValueError, match="two source brands"):
        validate_candidate_suite(suite)


def test_candidate_rejects_missing_critical_metadata() -> None:
    """Every semantic criterion must explicitly declare whether it is critical."""
    suite = copy.deepcopy(_suite())
    questions = suite["questions"]
    assert isinstance(questions, list)
    del questions[0]["criteria"][0]["critical"]
    with pytest.raises(ValueError, match="critical"):
        validate_candidate_suite(suite)


def test_forbidden_terms_use_word_boundaries_not_storage_substrings() -> None:
    """The word storage is valid, while an explicit RAG benchmark reference is not."""
    suite = _suite()
    questions = suite["questions"]
    assert isinstance(questions, list)
    questions[0]["question"] = "What broad pattern links storage arrangement and installation guidance?"
    validate_candidate_suite(suite)
    questions[0]["question"] = "Would RAG answer this benchmark question?"
    with pytest.raises(ValueError, match="benchmark implementation"):
        validate_candidate_suite(suite)


def test_scoring_contract_is_frozen_before_authoring() -> None:
    """Threshold constants match the aligned experiment protocol."""
    assert COMPATIBILITY_PASS_SCORE == 70
    assert HUMAN_REVIEW_CONFIDENCE == 0.75
    assert GLOBAL_ADVANTAGE_MARGIN == 5
    assert BLINDING_SEED == "w20-v2-20261111"


def _pdfs(tmp_path: Path) -> list[Path]:
    """Create four tiny PDF-shaped files for transport contract tests."""
    paths = [
        tmp_path / "ge.pdf",
        tmp_path / "kitchenaid.pdf",
        tmp_path / "samsung-user.pdf",
        tmp_path / "samsung-repair.pdf",
    ]
    for index, path in enumerate(paths):
        path.write_bytes(b"%PDF-1.7\n" + str(index).encode("ascii"))
    return paths


def _response(suite: dict[str, object]) -> dict[str, object]:
    """Wrap one suite in the OpenAI Responses JSON shape used by the author."""
    return {
        "id": "resp-test",
        "model": "gpt-author-strong",
        "output": [{"content": [{"type": "output_text", "text": json.dumps(suite)}]}],
    }


def _evidence_response(filename: str) -> dict[str, object]:
    """Wrap one compact manual evidence packet in a provider response."""
    packet = {
        "manual": {"brand": "test", "model": "test", "file": filename},
        "sections": [
            {
                "location": "Controls",
                "topic": "temporary cooling",
                "facts": ["Temporary modes differ from permanent setpoints."],
            }
        ],
    }
    return {
        "id": f"evidence-{filename}",
        "model": "gpt-author-strong",
        "output": [{"content": [{"type": "output_text", "text": json.dumps(packet)}]}],
    }


def test_pdf_evidence_request_requires_explicit_model(tmp_path: Path) -> None:
    """Authoring cannot silently inherit the benchmark's mini answer model."""
    with pytest.raises(ValueError, match="explicit strong author model"):
        build_pdf_evidence_request(_pdfs(tmp_path)[0], model="")


def test_pdf_evidence_request_embeds_one_original_pdf(tmp_path: Path) -> None:
    """Each extraction request contains one PDF so combined manuals cannot overflow context."""
    body = build_pdf_evidence_request(_pdfs(tmp_path)[0], model="gpt-author-strong")
    assert body["model"] == "gpt-author-strong"
    content = body["input"][0]["content"]
    files = [item for item in content if item["type"] == "input_file"]
    assert len(files) == 1
    assert all(str(item["file_data"]).startswith("data:application/pdf;base64,") for item in files)


def test_synthesis_request_contains_evidence_not_pdf_payloads() -> None:
    """Final authoring consumes bounded evidence packets rather than reopening four PDFs."""
    packets = [{"manual": {"file": f"manual-{index}.pdf"}, "sections": []} for index in range(4)]
    body = build_synthesis_request(
        packets,
        model="gpt-author-strong",
    )
    content = body["input"][0]["content"]
    assert all(item["type"] != "input_file" for item in content)
    assert AUTHOR_PROMPT in content[0]["text"]


def test_parse_author_response_rejects_non_json_text() -> None:
    """A prose or malformed provider response never becomes a candidate fixture."""
    raw = {"output": [{"content": [{"type": "output_text", "text": "not json"}]}]}
    with pytest.raises(ValueError, match="valid JSON"):
        parse_author_response(raw)


def test_author_candidate_writes_reproducible_artifacts(tmp_path: Path) -> None:
    """A mocked author call persists candidate, raw response, prompt, provenance, and progress."""
    output_dir = tmp_path / "run"
    suite = _suite()
    request_file_counts: list[int] = []

    def _transport(body: dict[str, object]) -> dict[str, object]:
        content = body["input"][0]["content"]
        files = [item for item in content if item["type"] == "input_file"]
        request_file_counts.append(len(files))
        if files:
            return _evidence_response(str(files[0]["filename"]))
        return _response(suite)

    candidate = author_candidate(
        _pdfs(tmp_path),
        output_dir=output_dir,
        model="gpt-author-strong",
        transport=_transport,
    )

    assert candidate == output_dir / "candidate.json"
    persisted = json.loads(candidate.read_text(encoding="utf-8"))
    assert persisted["status"] == "candidate"
    assert all(not q["authoring"]["human_verified"] for q in persisted["questions"])
    provenance = json.loads((output_dir / "provenance.json").read_text(encoding="utf-8"))
    assert provenance["provider"] == "openai"
    assert provenance["model"] == "gpt-author-strong"
    assert len(provenance["sources"]) == 4
    assert len(provenance["prompt_sha256"]) == 64
    assert request_file_counts == [1, 1, 1, 1, 0]
    assert (output_dir / "raw_response.json").exists()
    assert (output_dir / "prompt.txt").read_text(encoding="utf-8") == AUTHOR_PROMPT
    steps = [json.loads(line)["step"] for line in (output_dir / "progress.jsonl").read_text().splitlines()]
    assert steps.count("source_extract_start") == 4
    assert steps.count("source_extract_done") == 4
    assert steps[-3:] == ["request_start", "response_saved", "candidate_validated"]


def test_author_candidate_refuses_existing_output_without_force(tmp_path: Path) -> None:
    """Repeated author runs cannot overwrite an existing candidate accidentally."""
    output_dir = tmp_path / "run"
    output_dir.mkdir()
    (output_dir / "candidate.json").write_text("{}", encoding="utf-8")

    with pytest.raises(FileExistsError, match="--force"):
        author_candidate(
            _pdfs(tmp_path),
            output_dir=output_dir,
            model="gpt-author-strong",
            transport=lambda _body: _response(_suite()),
        )


def test_loader_accepts_candidate_for_review_but_not_full_run(tmp_path: Path) -> None:
    """Candidate data can be inspected, while benchmark selection requires frozen status."""
    path = tmp_path / "candidate.json"
    path.write_text(json.dumps(_suite()), encoding="utf-8")
    assert load_cos_insight_suite(path)["status"] == "candidate"
    with pytest.raises(ValueError, match="must be frozen"):
        load_cos_insight_suite(path, require_frozen=True)


def test_freeze_rejects_any_unverified_question(tmp_path: Path) -> None:
    """No candidate can freeze while even one gold row lacks human verification."""
    candidate = tmp_path / "candidate.json"
    candidate.write_text(json.dumps(_suite()), encoding="utf-8")
    with pytest.raises(ValueError, match="human_verified"):
        freeze_candidate(
            candidate,
            output_path=tmp_path / "frozen.json",
            reviewer="test-reviewer",
        )


def test_approve_all_records_reviewer_and_marks_every_row(tmp_path: Path) -> None:
    """Explicit approve-all records the human decision before freeze."""
    candidate = tmp_path / "candidate.json"
    candidate.write_text(json.dumps(_suite(), indent=2) + "\n", encoding="utf-8")

    approve_candidate(candidate, reviewer="test-reviewer", approve_all=True)

    reviewed = json.loads(candidate.read_text(encoding="utf-8"))
    assert all(q["authoring"]["human_verified"] is True for q in reviewed["questions"])
    decision = json.loads((tmp_path / "review.json").read_text(encoding="utf-8"))
    assert decision["reviewer"] == "test-reviewer"
    assert len(decision["approved_question_ids"]) == 20
    assert len(decision["pre_review_sha256"]) == 64


def test_freeze_writes_suite_and_hash_manifest(tmp_path: Path) -> None:
    """A fully reviewed candidate freezes without changing questions or gold answers."""
    suite = _suite()
    questions = suite["questions"]
    assert isinstance(questions, list)
    for row in questions:
        row["authoring"]["human_verified"] = True
    candidate = tmp_path / "candidate.json"
    candidate.write_text(json.dumps(suite, indent=2) + "\n", encoding="utf-8")

    frozen = freeze_candidate(
        candidate,
        output_path=tmp_path / "frozen.json",
        reviewer="test-reviewer",
    )

    payload = json.loads(frozen.read_text(encoding="utf-8"))
    assert payload["status"] == "frozen"
    assert payload["freeze"]["reviewer"] == "test-reviewer"
    assert payload["questions"] == suite["questions"]
    manifest = json.loads((tmp_path / "frozen.manifest.json").read_text(encoding="utf-8"))
    assert len(manifest["candidate_sha256"]) == 64
    assert len(manifest["frozen_sha256"]) == 64
    assert manifest["reviewer"] == "test-reviewer"
