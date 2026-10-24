"""Load merged benchmark config: brain-stack retail evidence + harness eval overrides."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[3]
BRAIN_SCRIPTS = REPO / "scripts" / "brain"
if str(BRAIN_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(BRAIN_SCRIPTS))

from brain_stack import _parse_simple_yaml, load_brain_stack  # noqa: E402

from .config_coerce import coerce_bool, coerce_int  # noqa: E402

_DEFAULT_EVIDENCE: dict[str, Any] = {
    "search_top_k": 5,
    "query_template": "{model_id} {question}",
    "page_prefix_chars": 8000,
    "insufficient_literal": "Insufficient_Information_Based_On_Given_PDF",
}

_DEFAULT_RAW_RAG: dict[str, Any] = {
    "embedding": {
        "provider": "openai",
        "model": "text-embedding-3-small",
        "batch_size": 32,
        "timeout_sec": 120,
    },
    "retrieval": {"default_mode": "vector", "rrf_k": 60},
    "agentic": {"enabled": False, "max_loops": 1},
}

_DEFAULT_EVAL: dict[str, Any] = {
    "answer": {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "temperature": 0,
    },
    "judge": {
        "provider": "gemini",
        "model": "gemini-3.1-flash-lite",
        "temperature": 0,
    },
}


def _smoke_question_ids(run_raw: dict[str, Any]) -> list[str]:
    """Normalize smoke ids (brain_stack parser may yield dict for block lists)."""
    raw = run_raw.get("smoke_question_ids")
    if isinstance(raw, list):
        return [str(x) for x in raw]
    if isinstance(raw, dict):
        return [str(v) for v in raw.values() if v]
    return []


def _coerce_raw_rag_scalars(raw_rag: dict[str, Any]) -> dict[str, Any]:
    """Normalize retail_raw_rag booleans/ints after simple YAML parse."""
    out = dict(raw_rag)
    agentic = dict(out.get("agentic") or {})
    agentic["enabled"] = coerce_bool(agentic.get("enabled"), default=False)
    agentic["max_loops"] = coerce_int(agentic.get("max_loops"), default=1)
    out["agentic"] = agentic
    retr = dict(out.get("retrieval") or {})
    if "rrf_k" in retr:
        retr["rrf_k"] = coerce_int(retr.get("rrf_k"), default=60)
    out["retrieval"] = retr
    emb = dict(out.get("embedding") or {})
    if "batch_size" in emb:
        emb["batch_size"] = coerce_int(emb.get("batch_size"), default=32)
    if "timeout_sec" in emb:
        emb["timeout_sec"] = coerce_int(emb.get("timeout_sec"), default=120)
    out["embedding"] = emb
    return out


def _coerce_evidence_scalars(evidence: dict[str, Any]) -> dict[str, Any]:
    """Normalize brain-stack string scalars (simple yaml parser) to int where needed."""
    out = dict(evidence)
    if "search_top_k" in out:
        out["search_top_k"] = int(out["search_top_k"])
    if "page_prefix_chars" in out:
        out["page_prefix_chars"] = int(out["page_prefix_chars"])
    return out


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    """Recursive dict merge (overlay wins on scalars)."""
    out = dict(base)
    for k, v in overlay.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_merged_run_config(
    repo_root: Path,
    *,
    run_config_path: Path | None = None,
) -> dict[str, Any]:
    """Evidence from ``second_brain.retail_evidence``; eval LLM steps from run-config ``retail_eval``."""
    cfg_path = run_config_path or (
        repo_root / "tests" / "retail_multi_profiles" / "data" / "run-config.yaml"
    )
    run_raw = _parse_simple_yaml(cfg_path.read_text(encoding="utf-8")) or {}

    evidence = dict(_DEFAULT_EVIDENCE)
    try:
        stack = load_brain_stack(repo_root)
        sb = stack.get("second_brain") or {}
        if isinstance(sb, dict):
            ev = sb.get("retail_evidence") or {}
            if isinstance(ev, dict):
                evidence = _deep_merge(evidence, ev)
    except FileNotFoundError:
        pass

    # Legacy harness file: top-level retrieval keys override brain-stack until removed.
    for key in ("search_top_k", "query_template", "page_prefix_chars", "insufficient_literal"):
        if key in run_raw:
            evidence[key] = run_raw[key]

    eval_block = run_raw.get("retail_eval") or {}
    if not eval_block and (run_raw.get("answer") or run_raw.get("judge")):
        eval_block = {"answer": run_raw.get("answer"), "judge": run_raw.get("judge")}

    eval_cfg = _deep_merge(_DEFAULT_EVAL, {k: v for k, v in eval_block.items() if v is not None})

    raw_rag_cfg = _deep_merge(_DEFAULT_RAW_RAG, run_raw.get("retail_raw_rag") or {})
    raw_rag_cfg = _coerce_raw_rag_scalars(raw_rag_cfg)

    evidence = _coerce_evidence_scalars(evidence)
    try:
        eval_rel = str(cfg_path.relative_to(repo_root))
    except ValueError:
        eval_rel = str(cfg_path)

    run_profiles = run_raw.get("run_profiles") or {}

    merged: dict[str, Any] = {
        "schema_version": str(run_raw.get("schema_version") or "1.0"),
        **evidence,
        "answer": eval_cfg["answer"],
        "judge": eval_cfg["judge"],
        "smoke_question_ids": _smoke_question_ids(run_raw),
        "retail_raw_rag": raw_rag_cfg,
        "run_profiles": run_profiles,
        "config_sources": {
            "retail_evidence": "config/brain-stack.example.yaml → second_brain.retail_evidence",
            "retail_eval": eval_rel,
            "retail_raw_rag": eval_rel,
        },
    }
    return merged
