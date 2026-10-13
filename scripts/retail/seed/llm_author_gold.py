#!/usr/bin/env python3.12
"""Offline LLM pass: add acceptable_ticket_ids to eval JSONL (not runtime eval).

Run after generate_eval_from_manifest.py. Does not change expected_ticket_ids (strict source).
Requires GEMINI_API_KEY and RETAIL_GOLD_MODEL (default gemini-2.0-flash). Use --dry-run to preview.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "retail"))

from utils.retail_fru.env import load_repo_env  # noqa: E402

load_repo_env(ROOT)

from retail_brain.ticket_store import load_ticket_rows  # noqa: E402


def _gold_model() -> str:
    return (
        os.environ.get("RETAIL_GOLD_MODEL", "").strip()
        or os.environ.get("GEMINI_MODEL", "").strip()
        or "gemini-2.0-flash"
    )


def _api_key() -> str:
    key = (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or "").strip()
    if not key:
        raise RuntimeError("Set GEMINI_API_KEY for llm_author_gold (offline authoring only).")
    return key


def candidates_for_case(rows, *, model_filter: str, limit: int = 40) -> list[dict]:
    out = []
    for r in rows:
        if r.status != "resolved" or r.model != model_filter:
            continue
        out.append(
            {
                "ticket_id": r.ticket_id,
                "customer_query_text": r.customer_query_text,
                "resolution_text": r.resolution_text,
            }
        )
    return out[:limit]


def llm_pick_acceptable(
    *,
    query: str,
    source_ticket_id: str,
    candidates: list[dict],
) -> tuple[list[str], str]:
    """Return (ticket_ids, rationale) from Gemini generateContent."""
    model = _gold_model()
    key = _api_key()
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={key}"
    )
    prompt = {
        "role": "user",
        "parts": [
            {
                "text": (
                    "You are an exam author for retail service ticket retrieval.\n"
                    "Given an exam QUESTION and a CANDIDATE list (ticket_id, customer text, resolution), "
                    "return JSON only: {\"acceptable_ticket_ids\": [...], \"rationale\": \"...\"}.\n"
                    "Include ticket ids that are valid answers (same incident class and same acceptable fix). "
                    f"Always include {source_ticket_id}. Do not invent ids.\n\n"
                    f"QUESTION: {query}\n\n"
                    f"CANDIDATES: {json.dumps(candidates, ensure_ascii=False)}"
                )
            }
        ],
    }
    body = json.dumps({"contents": [prompt]}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Gemini gold author failed: {e.read().decode()[:500]}") from e
    text = data["candidates"][0]["content"]["parts"][0]["text"]
    start, end = text.find("{"), text.rfind("}") + 1
    parsed = json.loads(text[start:end])
    ids = sorted(set(parsed.get("acceptable_ticket_ids") or []))
    if source_ticket_id not in ids:
        ids.append(source_ticket_id)
        ids.sort()
    return ids, str(parsed.get("rationale") or "")


def main() -> None:
    p = argparse.ArgumentParser(description="Offline LLM gold: acceptable_ticket_ids on eval JSONL")
    p.add_argument(
        "--eval",
        type=Path,
        default=ROOT / "scripts" / "retail/eval/ticket_retrieval.jsonl",
    )
    p.add_argument(
        "--csv",
        type=Path,
        default=ROOT / "scripts/retail/seed/generated/service_queries.csv",
    )
    p.add_argument("--max-rows", type=int, default=0, help="0 = all rows")
    p.add_argument("--dry-run", action="store_true", help="Print plan only; no API calls")
    args = p.parse_args()
    rows = load_ticket_rows(args.csv)
    cases = []
    with args.eval.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                cases.append(json.loads(line))
    if args.max_rows:
        cases = cases[: args.max_rows]

    if args.dry_run:
        print(f"llm_author_gold: would author {len(cases)} rows from {args.csv}")
        print(f"model={_gold_model()} eval={args.eval}")
        return

    updated = []
    for case in cases:
        cands = candidates_for_case(rows, model_filter=case["model_filter"])
        ids, rationale = llm_pick_acceptable(
            query=case["query"],
            source_ticket_id=case["source_ticket_id"],
            candidates=cands,
        )
        case = dict(case)
        case["acceptable_ticket_ids"] = ids
        case["gold_rationale"] = rationale
        updated.append(case)
        print(f"  {case['eval_id']}: acceptable n={len(ids)}")

    with args.eval.open("w", encoding="utf-8") as f:
        for row in updated:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"llm_author_gold: wrote {len(updated)} rows to {args.eval}")


if __name__ == "__main__":
    main()
