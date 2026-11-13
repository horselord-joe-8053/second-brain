"""Author and freeze W20 v2 without consulting A1/A3 benchmark outcomes.

The module owns the evaluation-data contract. Retrieval and answer behavior stay
outside this file so question authoring cannot silently tune either search arm.
"""

from __future__ import annotations

import base64
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.request
from typing import Any

from logging_utils.run_progress import write_jsonl_line
from utils.neat_logger.neat_logger_instance import NeatLogger, NeatLoggerFactory

EXPECTED_CLASSES = {
    "global_cross_brand": 12,
    "global_single_brand": 4,
    "boundary_local": 4,
}
BRIEFING_CLASSES = {"global_cross_brand": 20}
CONSTRUCT_CLASSES = {
    "mixed_v2": EXPECTED_CLASSES,
    "briefing_v3": BRIEFING_CLASSES,
}
EXPECTED_SOURCE_FILES = {
    "ge_GNE27JYMFS/user-guide.pdf",
    "kitchenaid_KRFF507HPS/user-guide.pdf",
    "samsung_RF28K9070SG/user-guide.pdf",
    "samsung_RF28K9070SG/repair-guide.pdf",
}
COMPATIBILITY_PASS_SCORE = 70
HUMAN_REVIEW_CONFIDENCE = 0.75
GLOBAL_ADVANTAGE_MARGIN = 5
BLINDING_SEED = "w20-v2-20261111"
FORBIDDEN_QUESTION_PATTERN = re.compile(
    r"\b(?:a1|a3|rag|retrieval|lane|lanes)\b|llm[\s-]+wiki",
    re.IGNORECASE,
)
AUTHOR_PROMPT = """You are authoring a frozen evaluation suite from the attached refrigerator manuals.

Produce exactly one JSON object matching the supplied schema. Use only facts supported by the attached PDFs.
Create exactly 20 questions:
- 12 global_cross_brand questions spanning at least two brands and at least three manual sections;
- 4 global_single_brand questions synthesizing at least three sections from one brand;
- 4 boundary_local control questions answerable from one local section.

Global questions must ask for a pattern, taxonomy, tradeoff, briefing framework, shared limitation, or meaningful
contrast. They must not be disguised two-passage fact lookups. A global question is invalid when one local passage
contains its full answer. Do not mention A1, A3, LLM Wiki, RAG, retrieval, lanes, benchmarks, or expected winners.

For every row:
- write a concise, manual-grounded gold answer;
- provide 3 to 5 semantic criteria;
- mark each criterion critical=true only when contradicting or omitting it would materially change correctness;
- keep useful nuance as critical=false so partial but sound answers can receive partial credit;
- list source file, section or page location, and source brands;
- set authoring.human_verified=false.

Do not add external product knowledge, invented rates, unsupported repairs, or score predictions. Return JSON only."""
BRIEFING_AUTHOR_PROMPT = """You are authoring a frozen evaluation suite from evidence extracted from four refrigerator manuals.

Produce exactly one JSON object matching the supplied schema. Use only facts supported by the evidence packets.
Create exactly 20 questions. Every question_class must be global_cross_brand, and every id must run from W20B_01 through W20B_20.

Each question is a cross-manual briefing for a trainer or support lead. Ask for a pattern, taxonomy, tradeoff, shared limitation, or briefing framework. Every question must need at least two brands and at least three manual sections. Reject a question when one passage, one diagnostic code, or one numeric specification contains its full answer.

Gold answers:
- Lead with the pattern, tradeoff, or taxonomy.
- Use brand differences only as short illustrations.
- Keep an exact interval, temperature, error code, page number, or parts-year out of the main point.
- An exact page fact may appear only as an optional illustration.

Criteria:
- Provide 3 to 5 semantic criteria.
- Set critical=true only for the pattern, tradeoff, taxonomy, or a material safety limitation.
- Omitting an exact number, code, or interval must not be critical.
- Set critical=false for useful brand-specific illustrations.
- Make at least one critical criterion acceptable without quoting a page.

For every row, list the source file, section or page location, and source brands, and set authoring.human_verified=false.
Do not mention A1, A3, LLM Wiki, RAG, retrieval, lanes, benchmarks, or expected winners.
Do not add external product knowledge, invented rates, unsupported repairs, or score predictions. Return JSON only."""
EVIDENCE_PROMPT = """Read the attached original refrigerator manual PDF and extract a compact, comprehensive
evidence packet for later cross-manual question authoring. Use only the PDF. Cover operating controls,
temporary modes, installation, water and ice behavior, maintenance, troubleshooting, warnings, diagnostics,
and service guidance that could support big-picture comparisons. Preserve exact numbers and limitations.
For each evidence group, give the PDF section/page location, a short topic, and concise factual claims.
Do not write evaluation questions. Return JSON only."""


def _class_counts(construct: str) -> dict[str, int]:
    """Return the required question-class counts for one authoring construct."""
    try:
        return CONSTRUCT_CLASSES[construct]
    except KeyError as exc:
        raise ValueError(f"unsupported W20 construct: {construct}") from exc


def _author_prompt(construct: str) -> str:
    """Return the synthesis prompt for the selected question construct."""
    _class_counts(construct)
    if construct == "briefing_v3":
        return BRIEFING_AUTHOR_PROMPT
    return AUTHOR_PROMPT


def _author_schema(construct: str = "mixed_v2") -> dict[str, Any]:
    """Return the strict provider schema for one W20 candidate construct."""
    source = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "file": {"type": "string"},
            "location": {"type": "string"},
        },
        "required": ["file", "location"],
    }
    criterion = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "text": {"type": "string"},
            "critical": {"type": "boolean"},
        },
        "required": ["text", "critical"],
    }
    question = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "id": {"type": "string"},
            "question_class": {"type": "string", "enum": list(_class_counts(construct))},
            "audience": {"type": "string"},
            "question": {"type": "string"},
            "answer": {"type": "string"},
            "criteria": {"type": "array", "minItems": 3, "maxItems": 5, "items": criterion},
            "authoring": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "human_verified": {"type": "boolean", "enum": [False]},
                    "sources": {"type": "array", "minItems": 1, "items": source},
                    "source_brands": {"type": "array", "minItems": 1, "items": {"type": "string"}},
                },
                "required": ["human_verified", "sources", "source_brands"],
            },
        },
        "required": [
            "id",
            "question_class",
            "audience",
            "question",
            "answer",
            "criteria",
            "authoring",
        ],
    }
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "schema_version": {"type": "string", "enum": ["cos_insight_qa.v2"]},
            "eval_suite_id": {"type": "string", "enum": ["TYPE_W_W20"]},
            "status": {"type": "string", "enum": ["candidate"]},
            "questions": {"type": "array", "minItems": 20, "maxItems": 20, "items": question},
        },
        "required": ["schema_version", "eval_suite_id", "status", "questions"],
    }


def _evidence_schema() -> dict[str, Any]:
    """Return the bounded schema for one manual evidence extraction call."""
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "manual": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "brand": {"type": "string"},
                    "model": {"type": "string"},
                    "file": {"type": "string"},
                },
                "required": ["brand", "model", "file"],
            },
            "sections": {
                "type": "array",
                "minItems": 1,
                "maxItems": 80,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "location": {"type": "string"},
                        "topic": {"type": "string"},
                        "facts": {
                            "type": "array",
                            "minItems": 1,
                            "maxItems": 10,
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["location", "topic", "facts"],
                },
            },
        },
        "required": ["manual", "sections"],
    }


def _sha256_bytes(value: bytes) -> str:
    """Return a stable lowercase SHA-256 digest."""
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    """Hash one source file without exposing its content in provenance."""
    return _sha256_bytes(path.read_bytes())


def build_pdf_evidence_request(pdf_path: Path, *, model: str) -> dict[str, Any]:
    """Build one bounded extraction request containing one original PDF."""
    selected_model = model.strip()
    if not selected_model:
        raise ValueError("an explicit strong author model is required")
    if not pdf_path.is_file():
        raise FileNotFoundError(f"manual PDF not found: {pdf_path}")
    if pdf_path.suffix.casefold() != ".pdf":
        raise ValueError(f"manual source must be PDF: {pdf_path}")
    encoded = base64.b64encode(pdf_path.read_bytes()).decode("ascii")
    content = [
        {
            "type": "input_file",
            "filename": pdf_path.name,
            "file_data": f"data:application/pdf;base64,{encoded}",
        },
        {"type": "input_text", "text": EVIDENCE_PROMPT},
    ]
    return {
        "model": selected_model,
        "input": [{"role": "user", "content": content}],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "manual_evidence",
                "strict": True,
                "schema": _evidence_schema(),
            }
        },
    }


def build_synthesis_request(
    evidence_packets: list[dict[str, Any]],
    *,
    model: str,
    construct: str = "mixed_v2",
) -> dict[str, Any]:
    """Build the final W20 request from compact packets extracted from original PDFs."""
    selected_model = model.strip()
    if not selected_model:
        raise ValueError("an explicit strong author model is required")
    if len(evidence_packets) != 4:
        raise ValueError("exactly four manual evidence packets are required")
    prompt = (
        f"{_author_prompt(construct)}\n\n"
        "The following evidence packets were extracted by the same model from the four original PDFs. "
        "Treat their file and location fields as the only allowed source references.\n\n"
        f"{json.dumps(evidence_packets, ensure_ascii=False)}"
    )
    return {
        "model": selected_model,
        "input": [
            {
                "role": "user",
                "content": [{"type": "input_text", "text": prompt}],
            }
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "w20_suite",
                "strict": True,
                "schema": _author_schema(construct),
            }
        },
    }


def _validate_evidence_packet(packet: dict[str, Any], pdf_path: Path) -> None:
    """Reject empty or structurally unsafe evidence before final synthesis."""
    manual = _mapping(packet.get("manual"), "manual evidence manual")
    for field in ("brand", "model", "file"):
        if not str(manual.get(field) or "").strip():
            raise ValueError(f"manual evidence {field} is required for {pdf_path}")
    sections = _sequence(packet.get("sections"), "manual evidence sections")
    if not sections:
        raise ValueError(f"manual evidence sections are required for {pdf_path}")
    for section in sections:
        item = _mapping(section, "manual evidence section")
        if not str(item.get("location") or "").strip() or not str(item.get("topic") or "").strip():
            raise ValueError(f"manual evidence section requires location and topic for {pdf_path}")
        facts = _sequence(item.get("facts"), "manual evidence facts")
        if not facts or any(not str(fact).strip() for fact in facts):
            raise ValueError(f"manual evidence facts are required for {pdf_path}")


def _source_id(path: Path) -> str:
    """Return the stable model-folder/file identifier used by gold references."""
    return f"{path.parent.name}/{path.name}"


def openai_author_request(body: dict[str, Any]) -> dict[str, Any]:
    """Post one PDF authoring request to the OpenAI Responses endpoint."""
    api_key = (os.environ.get("OPENAI_API_KEY") or "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=900) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:1000]
        raise RuntimeError(f"OpenAI Responses HTTP {exc.code}: {detail}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("OpenAI Responses returned a non-object payload")
    return payload


def parse_author_response(raw: dict[str, Any]) -> dict[str, Any]:
    """Extract and parse the JSON suite from an OpenAI Responses payload."""
    text = raw.get("output_text")
    if not isinstance(text, str):
        for output in _sequence(raw.get("output"), "provider output"):
            item = _mapping(output, "provider output item")
            for content in _sequence(item.get("content"), "provider output content"):
                part = _mapping(content, "provider content item")
                if part.get("type") == "output_text" and isinstance(part.get("text"), str):
                    text = part["text"]
                    break
            if isinstance(text, str):
                break
    if not isinstance(text, str) or not text.strip():
        raise ValueError("provider response contains no output_text")
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`").removeprefix("json").strip()
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError("provider output_text is not valid JSON") from exc
    if not isinstance(parsed, dict):
        raise ValueError("provider output JSON must be an object")
    return parsed


def _author_logger(run_name: str) -> NeatLogger:
    """Create the standard operator logger for one author run."""
    safe = run_name.replace("/", "_")
    return NeatLoggerFactory.create(
        "OPS",
        "W20_AUTHOR",
        log_file_name=f"w20-author-{safe}.log",
        log_output="both",
    )


def author_candidate(
    pdf_paths: list[Path],
    *,
    output_dir: Path,
    model: str,
    transport: Any = openai_author_request,
    force: bool = False,
    resume: bool = False,
    construct: str = "mixed_v2",
    logger: NeatLogger | None = None,
) -> Path:
    """Extract four bounded evidence packets, then persist one auditable W20 suite."""
    candidate_path = output_dir / "candidate.json"
    if candidate_path.exists() and not force:
        raise FileExistsError(f"{candidate_path} exists; pass --force to replace it")
    if len(pdf_paths) != 4:
        raise ValueError("exactly four original PDF files are required")
    prompt = _author_prompt(construct)
    output_dir.mkdir(parents=True, exist_ok=True)
    progress_path = output_dir / "progress.jsonl"
    log = logger or _author_logger(output_dir.name)
    write_jsonl_line(progress_path, {"type": "progress", "step": "author_start"})
    log.step(f"author start model={model} sources={len(pdf_paths)}")
    log.debug(
        f"prompt_sha256={_sha256_bytes((EVIDENCE_PROMPT + prompt).encode('utf-8'))} "
        f"source_bytes={sum(path.stat().st_size for path in pdf_paths)}"
    )
    evidence_path = output_dir / "evidence_packets.json"
    raw_path = output_dir / "raw_response.json"
    evidence_packets: list[dict[str, Any]]
    evidence_responses: list[dict[str, Any]] = []
    if resume:
        if not evidence_path.is_file():
            raise FileNotFoundError(f"resume evidence not found: {evidence_path}")
        loaded_packets = json.loads(evidence_path.read_text(encoding="utf-8"))
        evidence_packets = [
            _mapping(packet, "manual evidence packet")
            for packet in _sequence(loaded_packets, "manual evidence packets")
        ]
        if len(evidence_packets) != len(pdf_paths):
            raise ValueError("resume evidence count does not match source PDFs")
        if raw_path.is_file():
            prior_raw = json.loads(raw_path.read_text(encoding="utf-8"))
            if isinstance(prior_raw, dict):
                evidence_responses = [
                    _mapping(item, "evidence response")
                    for item in _sequence(prior_raw.get("evidence_responses") or [], "evidence responses")
                ]
        log.info(f"resuming from {len(evidence_packets)} saved evidence packets")
    else:
        evidence_packets = []
        for index, path in enumerate(pdf_paths, start=1):
            write_jsonl_line(
                progress_path,
                {
                    "type": "progress",
                    "step": "source_extract_start",
                    "source_index": index,
                    "source": path.name,
                },
            )
            body = build_pdf_evidence_request(path, model=model)
            with log.heartbeat(f"extract PDF evidence {index}/{len(pdf_paths)} {path.name}"):
                evidence_raw = transport(body)
            packet = parse_author_response(evidence_raw)
            _validate_evidence_packet(packet, path)
            evidence_packets.append(packet)
            evidence_responses.append(evidence_raw)
            write_jsonl_line(
                progress_path,
                {
                    "type": "progress",
                    "step": "source_extract_done",
                    "source_index": index,
                    "source": path.name,
                    "section_count": len(_sequence(packet.get("sections"), "sections")),
                },
            )
    for packet, path in zip(evidence_packets, pdf_paths):
        _mapping(packet.get("manual"), "manual evidence manual")["file"] = _source_id(path)
    evidence_path.write_text(
        json.dumps(evidence_packets, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_jsonl_line(progress_path, {"type": "progress", "step": "request_start"})
    synthesis_body = build_synthesis_request(evidence_packets, model=model, construct=construct)
    with log.heartbeat("OpenAI W20 synthesis request"):
        raw = transport(synthesis_body)
    raw_path.write_text(
        json.dumps(
            {
                "evidence_responses": evidence_responses,
                "synthesis_response": raw,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    write_jsonl_line(progress_path, {"type": "progress", "step": "response_saved"})
    suite = parse_author_response(raw)
    suite["construct"] = construct
    validate_candidate_suite(suite)
    for row in _sequence(suite.get("questions"), "questions"):
        authoring = _mapping(_mapping(row, "question").get("authoring"), "authoring")
        authoring["human_verified"] = False
    prompt_hash = _sha256_bytes((EVIDENCE_PROMPT + prompt).encode("utf-8"))
    provenance = {
        "provider": "openai",
        "model": model,
        "authoring_strategy": "four_pdf_evidence_calls_then_synthesis",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "prompt_sha256": prompt_hash,
        "response_id": str(raw.get("id") or ""),
        "response_model": str(raw.get("model") or ""),
        "evidence_response_ids": [str(item.get("id") or "") for item in evidence_responses],
        "sources": [
            {
                "path": str(path),
                "filename": path.name,
                "sha256": _sha256_file(path),
                "bytes": path.stat().st_size,
            }
            for path in pdf_paths
        ],
    }
    (output_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
    (output_dir / "evidence_prompt.txt").write_text(EVIDENCE_PROMPT, encoding="utf-8")
    (output_dir / "provenance.json").write_text(
        json.dumps(provenance, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    candidate_path.write_text(
        json.dumps(suite, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_jsonl_line(progress_path, {"type": "progress", "step": "candidate_validated"})
    log.info(f"candidate validated path={candidate_path}")
    return candidate_path


def approve_candidate(
    candidate_path: Path,
    *,
    reviewer: str,
    approve_all: bool = False,
    logger: NeatLogger | None = None,
) -> Path:
    """Record one explicit human approve-all decision without changing authored content."""
    reviewer_name = reviewer.strip()
    if not reviewer_name:
        raise ValueError("reviewer is required")
    if not approve_all:
        raise ValueError("approve_all must be explicit")
    original = candidate_path.read_bytes()
    try:
        candidate = json.loads(original)
    except json.JSONDecodeError as exc:
        raise ValueError(f"candidate is not valid JSON: {candidate_path}") from exc
    if not isinstance(candidate, dict):
        raise ValueError("candidate JSON must be an object")
    validate_candidate_suite(candidate)
    if candidate.get("status") != "candidate":
        raise ValueError("only status=candidate can be approved")
    questions = _sequence(candidate.get("questions"), "questions")
    question_ids: list[str] = []
    for row in questions:
        question = _mapping(row, "question")
        question_ids.append(str(question.get("id") or ""))
        _mapping(question.get("authoring"), "authoring")["human_verified"] = True
    reviewed_at = datetime.now(timezone.utc).isoformat()
    review = {
        "reviewer": reviewer_name,
        "reviewed_at": reviewed_at,
        "approval": "approve_all",
        "approved_question_ids": question_ids,
        "pre_review_sha256": _sha256_bytes(original),
    }
    candidate["review"] = review
    provenance_path = candidate_path.with_name("provenance.json")
    if provenance_path.is_file():
        provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
        if isinstance(provenance, dict):
            candidate["authoring_run"] = {
                "provider": str(provenance.get("provider") or ""),
                "model": str(provenance.get("model") or ""),
                "prompt_sha256": str(provenance.get("prompt_sha256") or ""),
            }
    candidate_path.write_text(
        json.dumps(candidate, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    review_path = candidate_path.with_name("review.json")
    review_path.write_text(
        json.dumps(review, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_jsonl_line(
        candidate_path.parent / "progress.jsonl",
        {"type": "progress", "step": "review_done", "reviewer": reviewer_name},
    )
    log = logger or _author_logger(candidate_path.parent.name)
    log.info(f"review approved rows={len(question_ids)} reviewer={reviewer_name}")
    return candidate_path


def freeze_candidate(
    candidate_path: Path,
    *,
    output_path: Path,
    reviewer: str,
    force: bool = False,
    logger: NeatLogger | None = None,
) -> Path:
    """Freeze a fully human-reviewed candidate and write an immutable hash manifest."""
    reviewer_name = reviewer.strip()
    if not reviewer_name:
        raise ValueError("reviewer is required")
    if output_path.exists() and not force:
        raise FileExistsError(f"{output_path} exists; pass --force to replace it")
    candidate_bytes = candidate_path.read_bytes()
    try:
        candidate = json.loads(candidate_bytes)
    except json.JSONDecodeError as exc:
        raise ValueError(f"candidate is not valid JSON: {candidate_path}") from exc
    if not isinstance(candidate, dict):
        raise ValueError("candidate JSON must be an object")
    validate_candidate_suite(candidate)
    if candidate.get("status") != "candidate":
        raise ValueError("only status=candidate can be frozen")
    questions = _sequence(candidate.get("questions"), "questions")
    unverified = [
        str(_mapping(row, "question").get("id") or "")
        for row in questions
        if _mapping(_mapping(row, "question").get("authoring"), "authoring").get("human_verified")
        is not True
    ]
    if unverified:
        raise ValueError(f"human_verified must be true for all rows; pending={unverified}")

    # JSON round-trip isolates the frozen payload from any caller-held mutable object.
    frozen = json.loads(json.dumps(candidate))
    reviewed_at = datetime.now(timezone.utc).isoformat()
    candidate_hash = _sha256_bytes(candidate_bytes)
    frozen["status"] = "frozen"
    frozen["freeze"] = {
        "reviewer": reviewer_name,
        "reviewed_at": reviewed_at,
        "candidate_sha256": candidate_hash,
        "blinding_seed": BLINDING_SEED,
    }
    validate_candidate_suite(frozen)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    serialized = (json.dumps(frozen, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    output_path.write_bytes(serialized)
    frozen_hash = _sha256_bytes(serialized)
    manifest = {
        "reviewer": reviewer_name,
        "reviewed_at": reviewed_at,
        "candidate_path": str(candidate_path),
        "candidate_sha256": candidate_hash,
        "frozen_path": str(output_path),
        "frozen_sha256": frozen_hash,
    }
    manifest_path = output_path.with_suffix(".manifest.json")
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_jsonl_line(
        output_path.parent / "progress.jsonl",
        {
            "type": "progress",
            "step": "freeze_done",
            "frozen_sha256": frozen_hash,
        },
    )
    log = logger or _author_logger(output_path.parent.name)
    log.info(f"freeze done path={output_path} sha256={frozen_hash}")
    return output_path


def _mapping(value: object, label: str) -> dict[str, Any]:
    """Return a mapping or raise a validation error naming its field."""
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return value


def _sequence(value: object, label: str) -> list[Any]:
    """Return a list or raise a validation error naming its field."""
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list")
    return value


def _validate_criterion(value: object, row_id: str) -> None:
    """Require criterion text plus an explicit critical/non-critical decision."""
    criterion = _mapping(value, f"{row_id} criterion")
    if not str(criterion.get("text") or "").strip():
        raise ValueError(f"{row_id} criterion text is required")
    if not isinstance(criterion.get("critical"), bool):
        raise ValueError(f"{row_id} criterion critical must be true or false")


def _validate_question(value: object, allowed_classes: dict[str, int]) -> str:
    """Validate one W20 question and return its construct class."""
    row = _mapping(value, "question")
    row_id = str(row.get("id") or "").strip()
    if not row_id:
        raise ValueError("question id is required")
    question = str(row.get("question") or "").strip()
    answer = str(row.get("answer") or "").strip()
    if not question or not answer:
        raise ValueError(f"{row_id} question and answer are required")
    if FORBIDDEN_QUESTION_PATTERN.search(question):
        raise ValueError(f"{row_id} question refers to benchmark implementation")

    question_class = str(row.get("question_class") or "").strip()
    if question_class not in allowed_classes:
        raise ValueError(f"{row_id} has unsupported question_class {question_class!r}")
    criteria = _sequence(row.get("criteria"), f"{row_id} criteria")
    if not 3 <= len(criteria) <= 5:
        raise ValueError(f"{row_id} must have three to five semantic criteria")
    for criterion in criteria:
        _validate_criterion(criterion, row_id)

    authoring = _mapping(row.get("authoring"), f"{row_id} authoring")
    sources = _sequence(authoring.get("sources"), f"{row_id} authoring.sources")
    brands = {
        str(brand).strip().casefold()
        for brand in _sequence(authoring.get("source_brands"), f"{row_id} authoring.source_brands")
        if str(brand).strip()
    }
    for source in sources:
        item = _mapping(source, f"{row_id} source")
        source_file = str(item.get("file") or "").strip()
        if not source_file or not str(item.get("location") or "").strip():
            raise ValueError(f"{row_id} source requires file and location")
        if source_file not in EXPECTED_SOURCE_FILES:
            raise ValueError(f"{row_id} source file is not one of the four original PDFs: {source_file}")
    if question_class.startswith("global_") and len(sources) < 3:
        raise ValueError(f"{row_id} global question requires at least three source sections")
    if question_class == "global_cross_brand" and len(brands) < 2:
        raise ValueError(f"{row_id} cross-brand question requires at least two source brands")
    return question_class


def validate_candidate_suite(data: dict[str, Any]) -> None:
    """Validate the frozen W20 v2 construct before any benchmark can use it."""
    if data.get("schema_version") != "cos_insight_qa.v2":
        raise ValueError("schema_version must be cos_insight_qa.v2")
    if data.get("eval_suite_id") != "TYPE_W_W20":
        raise ValueError("eval_suite_id must be TYPE_W_W20")
    if data.get("status") not in {"candidate", "frozen"}:
        raise ValueError("status must be candidate or frozen")
    construct = str(data.get("construct") or "mixed_v2")
    expected_classes = _class_counts(construct)
    questions = _sequence(data.get("questions"), "questions")
    if len(questions) != 20:
        raise ValueError("W20 v2 must contain exactly 20 questions")
    ids = [str(_mapping(row, "question").get("id") or "") for row in questions]
    if len(set(ids)) != len(ids):
        raise ValueError("question ids must be unique")
    counts = Counter(_validate_question(row, expected_classes) for row in questions)
    for question_class, expected in expected_classes.items():
        if counts[question_class] != expected:
            detail = ", ".join(f"{count} {name}" for name, count in expected_classes.items())
            raise ValueError(f"W20 {construct} requires {detail}")
