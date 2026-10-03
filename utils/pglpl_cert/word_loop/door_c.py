"""pgbattest Door C — batched dual-model paragraph quality judges.

After Door A+B (pipeline ``shipped``), send all settled paragraphs in **one**
Pair-A call and **one** Pair-B call (parallel). Each pair is configured as
``{provider, model}`` under ``non_conj_paragraph.door_c.judge_a`` /
``judge_b`` (``gemini`` | ``openai`` | ``claude``). Env overrides:
``DOOR_C_JUDGE_A_PROVIDER`` / ``DOOR_C_JUDGE_A_MODEL`` (and B equivalents);
precedence is env > YAML > defaults. Pass only when **both** judges mark a
paragraph **OK** (dual approve); **any** ISSUE from either judge fails that
paragraph. Snapshot texts come from the harness before bulk-delete — not from
the live DB.

Same provider on both slots is allowed but weakens independence; prefer cross-vendor.
Gemini exchange code stays even when YAML comments Gemini out — set
``judge_a.provider: gemini`` to restore. Gemini→Claude auto-fallback runs only
when the selected slot's provider is ``gemini``.
"""

from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable

JudgeExchangeFn = Callable[[str, str, str], str]
# (provider, model, prompt) -> raw response text

_DOOR_C_PROVIDERS = frozenset({"gemini", "openai", "claude"})
_DEFAULT_JUDGE_A: dict[str, str] = {
    "provider": "claude",
    "model": "claude-sonnet-4-5",
}
_DEFAULT_JUDGE_B: dict[str, str] = {
    "provider": "openai",
    "model": "gpt-4.1",
}

# Bumped when global/scope pedagogy in ``build_judge_prompt`` changes materially.
DOOR_C_JUDGE_PROMPT_VERSION = "door_c_judge_v2"


def effective_door_c_prompt_version() -> str:
    """Module default with optional YAML ``non_conj_paragraph.door_c.prompt_version``."""
    try:
        from app.services.main_config import get_pgbattest_door_c_settings

        pv = str(get_pgbattest_door_c_settings().get("prompt_version") or "").strip()
        if pv:
            return pv
    except Exception:
        pass
    return DOOR_C_JUDGE_PROMPT_VERSION


from utils.pglpl_cert._paths import REPO_ROOT


def _repo_root() -> Path:
    return REPO_ROOT


def _normalize_judge_slot(
    raw: Any,
    *,
    default: dict[str, str],
    slot_name: str,
) -> dict[str, str]:
    """Normalize ``{provider, model}``; reject unknown providers."""
    base = {"provider": default["provider"], "model": default["model"]}
    if not isinstance(raw, dict):
        return base
    provider = str(raw.get("provider") or base["provider"]).strip().lower()
    if provider not in _DOOR_C_PROVIDERS:
        raise ValueError(f"door_c_unknown_provider:{slot_name}:{provider}")
    model = str(raw.get("model") or base["model"]).strip()
    if not model:
        raise ValueError(f"door_c_missing_model:{slot_name}")
    return {"provider": provider, "model": model}


def _apply_env_judge_overrides(cfg: dict[str, Any]) -> None:
    """Mutate cfg: env > YAML for Pair A/B provider and model."""
    ja = dict(cfg.get("judge_a") or _DEFAULT_JUDGE_A)
    jb = dict(cfg.get("judge_b") or _DEFAULT_JUDGE_B)

    env_ap = (os.getenv("DOOR_C_JUDGE_A_PROVIDER") or "").strip().lower()
    if env_ap in _DOOR_C_PROVIDERS:
        ja["provider"] = env_ap
    env_am = (os.getenv("DOOR_C_JUDGE_A_MODEL") or "").strip()
    if env_am:
        ja["model"] = env_am

    env_bp = (os.getenv("DOOR_C_JUDGE_B_PROVIDER") or "").strip().lower()
    if env_bp in _DOOR_C_PROVIDERS:
        jb["provider"] = env_bp
    env_bm = (os.getenv("DOOR_C_JUDGE_B_MODEL") or "").strip()
    if env_bm:
        jb["model"] = env_bm

    # Deprecated: DOOR_C_CLAUDE_MODEL → judge_a.model only when Pair A is Claude.
    env_cm = (os.getenv("DOOR_C_CLAUDE_MODEL") or "").strip()
    if env_cm and ja.get("provider") == "claude" and not env_am:
        ja["model"] = env_cm

    cfg["judge_a"] = _normalize_judge_slot(ja, default=_DEFAULT_JUDGE_A, slot_name="judge_a")
    cfg["judge_b"] = _normalize_judge_slot(jb, default=_DEFAULT_JUDGE_B, slot_name="judge_b")


def load_door_c_settings(
    *,
    enabled_override: bool | None = None,
    mode_override: str | None = None,
) -> dict[str, Any]:
    """Load Door C settings; prefer app main_config, fall back to nested defaults.

    Precedence for Pair A/B: env overrides > YAML > defaults.
    """
    try:
        from app.services.main_config import get_pgbattest_door_c_settings

        cfg = dict(get_pgbattest_door_c_settings())
    except Exception:
        cfg = {
            "enabled": True,
            "mode": "ALL_SHIPPED_SCOPES",
            "judge_a": dict(_DEFAULT_JUDGE_A),
            "judge_b": dict(_DEFAULT_JUDGE_B),
        }
    # Ensure nested shape even if an older loader returned flat keys.
    if "judge_a" not in cfg or not isinstance(cfg.get("judge_a"), dict):
        cfg["judge_a"] = dict(_DEFAULT_JUDGE_A)
    if "judge_b" not in cfg or not isinstance(cfg.get("judge_b"), dict):
        cfg["judge_b"] = dict(_DEFAULT_JUDGE_B)
    if enabled_override is not None:
        cfg["enabled"] = bool(enabled_override)
    if mode_override:
        mode = str(mode_override).strip().upper()
        if mode in {"ALL_SHIPPED_SCOPES", "PER_SHIPPED_SCOPE"}:
            cfg["mode"] = mode
    _apply_env_judge_overrides(cfg)
    return cfg


_BLANK_MARKER_RE = re.compile(r"⟦(\d+)⟧")


def _blank_is_spell_noun_chip(blank: dict[str, Any]) -> bool:
    """True when the blank drills a noun spelling (spell chips).

    Prefer ``blank_kind == "noun"`` (same-form / two-forms / animals). Leading
    chips (LBH / fixed-article / meaning-changers) use ``blank_kind == "leading"``.
    """
    kind = str(blank.get("blank_kind") or "").strip().lower()
    return kind == "noun"


def _judge_fill_surface_for_blank(blank: dict[str, Any]) -> str:
    """Surface pasted into ``⟦n⟧`` for Door C only (not learner-facing).

    Spell chips: natural leadings stay in the paragraph; inject stores the noun
    alone. Judges fill **noun only** so they see the same glue learners see.
    Place no-article ``—`` is the grade key only — visible fill is empty.
    """
    from app.pglpl.visible_fill import visible_fill_for_blank

    return visible_fill_for_blank(blank)


def _maybe_capitalize_fill(fill: str, *, text: str, start: int) -> str:
    """Capitalize fill when the marker starts a sentence."""
    if not fill:
        return fill
    if start == 0:
        return fill[:1].upper() + fill[1:]
    prev = text[:start].rstrip()
    if prev.endswith((".", "!", "?")):
        return fill[:1].upper() + fill[1:]
    return fill


def fill_blank_markers_for_judge(text: str, blanks: list[Any] | None) -> str:
    """Replace ``⟦n⟧`` with judge-readable surfaces for Door C review only.

    Spell-chip blanks get the noun only (natural leadings already in the text).
    Glossary / leading blanks stay single-token fills.
    """
    by_slot: dict[int, str] = {}
    known_slots: set[int] = set()
    for b in blanks or []:
        if not isinstance(b, dict):
            continue
        try:
            slot = int(b.get("slot"))
        except (TypeError, ValueError):
            continue
        known_slots.add(slot)
        by_slot[slot] = _judge_fill_surface_for_blank(b)

    def _repl(m: re.Match[str]) -> str:
        try:
            slot = int(m.group(1))
        except (TypeError, ValueError):
            return m.group(0)
        if slot not in known_slots:
            return m.group(0)
        fill = by_slot.get(slot, "")
        return _maybe_capitalize_fill(fill, text=text or "", start=m.start())

    filled = _BLANK_MARKER_RE.sub(_repl, text or "")
    return re.sub(r"[ \t]{2,}", " ", filled).strip()


def build_judge_prompt(scopes_payload: list[dict[str, Any]]) -> str:
    """Build one batched review prompt covering all paragraphs in the payload.

    Design contract:
    - Enforces native-level correctness for Portuguese learner paragraphs.
    - Requires exact drill tokens listed under Fixed pedagogy blanks to be accepted as written
      (exempting spelling preference disputes like tricentésimo vs trecentésimo).
    - Expects full Portuguese grammar and agreement correctness across all tokens.
    """
    parts: list[str] = [
        "You are a Brazilian Portuguese language reviewer (native-level).",
        "Review learner paragraphs for CORRECTNESS only.",
        "",
        "Pedagogy (NOT errors unless clearly broken PT):",
        "- Epicene animals: fixed spelling + macho/fêmea; article/adjective gender",
        "  follows the NOUN, not biological sex. OK: \"o rinoceronte fêmea\",",
        "  \"a baleia macho\", \"um jacaré fêmea\". WRONG: \"uma jacaré\", \"a tubarão\".",
        "- Texts may still contain intentional cloze markers ⟦n⟧; do NOT mark ISSUE",
        "  solely because a token is \"missing\" at a marker (blanks are expected).",
        "- Fixed pedagogy blanks (exact drill tokens):",
        "  If a paragraph lists Fixed blanks, those exact tokens must be accepted as written.",
        "  Do NOT mark ISSUE solely to prefer an alternate spelling of a listed Fixed blank",
        "  (e.g. tricentésimo vs trecentésimo; nongentésimo vs noningentésimo; libido vs líbido when libido is listed).",
        "  However, real Portuguese language errors outside the listed Fixed blanks MUST still be flagged.",
        "- Do NOT ISSUE solely for missing sentence-initial capital after a period,",
        "  adjective placement preference, predicate-style word-choice nits",
        "  (e.g. 'estava pouca' vs 'havia pouca'), or other mild style preferences.",
        "- After cardinal 'zero', both singular and plural nouns are OK",
        "  ('zero aluno' / 'zero alunos') — do NOT ISSUE solely to flip noun number",
        "  after zero.",
        "- Do NOT fail for awkward scenes when the Portuguese is otherwise grammatical.",
        "",
        "Check REAL errors: clearly broken PT, wrong invented noun forms,",
        "self-contradictory quantity claims, and article/gender/verb agreement",
        "errors that are NOT excused by Fixed blanks above.",
        "",
        "Return ONLY valid JSON (no markdown fences) with this shape:",
        '{"paragraphs":[{"id":"<para_id>","verdict":"OK"|"ISSUE","issues":["..."]}]}',
        "Use the exact paragraph id strings given below. issues may be [] when OK.",
        "",
    ]
    for block in scopes_payload:
        scope = str(block.get("scope") or "")
        parts.append(f"## Scope: {scope}")
        try:
            from app.pglpl.pedagogy_notes import door_c_scope_pedagogy_note

            scope_note = door_c_scope_pedagogy_note(scope)
        except Exception:
            scope_note = ""
        if scope_note.strip():
            parts.append(scope_note.strip())
            parts.append("")
        for p in block.get("paragraphs") or []:
            pid = str(p.get("id") or "")
            text = str(p.get("text") or "")
            parts.append(f"### id={pid}")
            fixed = p.get("fixed_surfaces") or []
            if fixed:
                listed = ", ".join(repr(x) for x in fixed)
                parts.append(f"Fixed pedagogy blanks (exact tokens): {listed}")
            parts.append(text)
            parts.append("")
    return "\n".join(parts)


def _strip_json_fence(raw: str) -> str:
    text = (raw or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _balance_json_closers(text: str) -> str:
    """Append missing ``]`` / ``}`` when a judge truncates the final braces."""
    in_str = False
    escape = False
    stack: list[str] = []
    for ch in text:
        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch in "{[":
            stack.append("}" if ch == "{" else "]")
        elif ch in "}]":
            if stack and stack[-1] == ch:
                stack.pop()
    if in_str:
        text += '"'
        # recompute quickly after closing the string
        return _balance_json_closers(text)
    if not stack:
        return text
    return text + "".join(reversed(stack))


def _loads_judge_json(raw: str) -> Any:
    """Parse judge JSON; tolerate markdown fences and trailing-brace truncation."""
    text = _strip_json_fence(raw)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        repaired = _balance_json_closers(text)
        return json.loads(repaired)


def parse_judge_response(raw: str) -> dict[str, dict[str, Any]]:
    """Map paragraph id -> {verdict, issues}. Raises ValueError on bad shape."""
    obj = _loads_judge_json(raw)
    rows = obj.get("paragraphs") if isinstance(obj, dict) else None
    if not isinstance(rows, list):
        raise ValueError("judge_json_missing_paragraphs")
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        pid = str(row.get("id") or "").strip()
        if not pid:
            continue
        verdict = str(row.get("verdict") or "").strip().upper()
        if verdict not in {"OK", "ISSUE"}:
            raise ValueError(f"judge_bad_verdict:{pid}:{verdict}")
        issues = row.get("issues") or []
        if not isinstance(issues, list):
            issues = [str(issues)]
        out[pid] = {"verdict": verdict, "issues": [str(x) for x in issues]}
    if not out:
        raise ValueError("judge_json_empty_paragraphs")
    return out


def _paragraph_index(pid: str) -> str:
    """Stable paragraph slot key (``#p3``) for aligning judge ids with typos."""
    if "#" in pid:
        return pid.rsplit("#", 1)[-1]
    return pid


def align_judge_response_ids(
    judge_map: dict[str, dict[str, Any]],
    expected_ids: list[str],
) -> dict[str, dict[str, Any]]:
    """Remap judge paragraph ids onto expected ids (exact match, then unique ``#pN``)."""
    if not judge_map or not expected_ids:
        return dict(judge_map)
    aligned: dict[str, dict[str, Any]] = {}
    used: set[str] = set()
    for eid in expected_ids:
        if eid in judge_map:
            aligned[eid] = judge_map[eid]
            used.add(eid)
    pending_expected = [eid for eid in expected_ids if eid not in aligned]
    pending_parsed = {k: v for k, v in judge_map.items() if k not in used}
    for eid in pending_expected:
        idx = _paragraph_index(eid)
        candidates = [pk for pk in pending_parsed if _paragraph_index(pk) == idx]
        if len(candidates) == 1:
            pk = candidates[0]
            aligned[eid] = pending_parsed[pk]
            del pending_parsed[pk]
    return aligned


def _missing_judge_slot(
    *,
    slot_name: str,
    judge_map: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Fail closed when the judge replied but no row aligned to this expected id."""
    tag = f"missing_from_{slot_name}"
    if judge_map:
        return {"verdict": "ISSUE", "issues": [tag]}
    return {"verdict": "OK", "issues": [tag]}


def consensus_quality_result(
    *,
    judge_a: dict[str, dict[str, Any]],
    judge_b: dict[str, dict[str, Any]],
    expected_ids: list[str],
    fail_policy: str = "dual_approve",
) -> dict[str, Any]:
    """Consensus over two judges.

    ``dual_approve`` (default): any ISSUE → fail. ``both_must_issue``: fail only when both judges ISSUE
    (split verdict with one OK → pass; warnings still recorded).
    """
    map_a = align_judge_response_ids(judge_a, expected_ids)
    map_b = align_judge_response_ids(judge_b, expected_ids)
    failed_ids: list[str] = []
    warnings: list[dict[str, Any]] = []
    per_para: list[dict[str, Any]] = []
    for pid in expected_ids:
        a = map_a.get(pid) or _missing_judge_slot(slot_name="judge_a", judge_map=judge_a)
        b = map_b.get(pid) or _missing_judge_slot(slot_name="judge_b", judge_map=judge_b)
        a_issue = a.get("verdict") == "ISSUE"
        b_issue = b.get("verdict") == "ISSUE"
        both = a_issue and b_issue
        if fail_policy == "both_must_issue":
            if both:
                failed_ids.append(pid)
        elif a_issue or b_issue:
            failed_ids.append(pid)
        if a_issue != b_issue:
            warnings.append(
                {
                    "id": pid,
                    "judge_a": a,
                    "judge_b": b,
                    # Legacy aliases (Pair A/B used to be fixed Gemini/OpenAI).
                    "gemini": a,
                    "openai": b,
                    "split_verdict": True,
                }
            )
        per_para.append(
            {
                "id": pid,
                "judge_a": a,
                "judge_b": b,
                "gemini": a,
                "openai": b,
                "both_issue": both,
            }
        )
    ok = not failed_ids
    return {
        "ok": ok,
        "failed_ids": failed_ids,
        "warnings": warnings,
        "paragraphs": per_para,
    }


def _http_json(
    method: str,
    url: str,
    *,
    headers: dict[str, str],
    body: dict[str, Any],
    timeout: float = 180.0,
) -> dict[str, Any]:
    """JSON HTTP via httpx (cert bundle) with urllib fallback."""
    try:
        import httpx

        with httpx.Client(timeout=timeout) as client:
            resp = client.request(method, url, headers=headers, json=body)
            if resp.status_code >= 400:
                raise urllib.error.HTTPError(
                    url, resp.status_code, resp.text[:300], hdrs=None, fp=None
                )
            return resp.json()
    except ImportError:
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers=headers,
            method=method,
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        return json.loads(raw)


def _exchange_openai(model: str, prompt: str, *, api_key: str) -> str:
    data = _http_json(
        "POST",
        "https://api.openai.com/v1/responses",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        body={
            "model": model,
            "input": prompt,
            "temperature": 0,
            # Large ALL_SHIPPED_SCOPES batches need headroom; truncate → broken JSON.
            "max_output_tokens": 8192,
        },
    )
    text = str(data.get("output_text") or "").strip()
    if text:
        return text
    chunks: list[str] = []
    for item in data.get("output") or []:
        if not isinstance(item, dict):
            continue
        for c in item.get("content") or []:
            if isinstance(c, dict) and c.get("type") in {"output_text", "text"}:
                chunks.append(str(c.get("text") or ""))
    return "\n".join(chunks).strip()


def _exchange_gemini(model: str, prompt: str, *, api_key: str) -> str:
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )
    data = _http_json(
        "POST",
        url,
        headers={"Content-Type": "application/json"},
        body={
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0,
                "responseMimeType": "application/json",
                "maxOutputTokens": 8192,
            },
        },
    )
    parts = (
        ((data.get("candidates") or [{}])[0].get("content") or {}).get("parts") or []
    )
    texts = [str(p.get("text") or "") for p in parts if isinstance(p, dict)]
    return "\n".join(texts).strip()


# Prefer configured Pro; on quota/429/404 fall back so Door C can still complete.
_GEMINI_FALLBACKS = (
    "gemini-2.5-pro",
    "gemini-3.6-flash",
)


def _exchange_gemini_with_fallback(model: str, prompt: str, *, api_key: str) -> str:
    tried: list[str] = []
    models = [model] + [m for m in _GEMINI_FALLBACKS if m != model]
    last_err: Exception | None = None
    for i, m in enumerate(models):
        tried.append(m)
        try:
            return _exchange_gemini(m, prompt, api_key=api_key)
        except urllib.error.HTTPError as ex:
            last_err = ex
            # 429/404/400: try next model; back off longer on rate limits.
            if ex.code in {429, 404, 400}:
                time.sleep(2.0 if ex.code == 429 else 0.8)
                continue
            raise
        except Exception as ex:  # noqa: BLE001
            last_err = ex
            time.sleep(0.5 + 0.3 * i)
            continue
    raise RuntimeError(f"gemini_all_failed:{tried}:{last_err}") from last_err


def _exchange_claude(model: str, prompt: str, *, api_key: str) -> str:
    """Anthropic Messages API (any Pair slot with provider=claude)."""
    data = _http_json(
        "POST",
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
        body={
            "model": model,
            # Match OpenAI/Gemini Door C headroom for ALL_SHIPPED_SCOPES batches.
            "max_tokens": 8192,
            "temperature": 0,
            "messages": [{"role": "user", "content": prompt}],
        },
    )
    chunks: list[str] = []
    for block in data.get("content") or []:
        if isinstance(block, dict) and block.get("type") == "text":
            chunks.append(str(block.get("text") or ""))
    return "\n".join(chunks).strip()


# Preferred id first; then common Anthropic ids (404 → next).
_CLAUDE_FALLBACK_MODELS = (
    "claude-sonnet-4-5",
    "claude-sonnet-4-5-20250929",
    "claude-3-5-sonnet-latest",
    "claude-3-5-sonnet-20241022",
)


def _claude_model_candidates(preferred: str) -> list[str]:
    pref = (preferred or "").strip()
    out: list[str] = []
    if pref:
        out.append(pref)
    for m in _CLAUDE_FALLBACK_MODELS:
        if m not in out:
            out.append(m)
    return out


def _exchange_claude_slot(model: str, prompt: str, *, api_key: str) -> str:
    """Claude slot: try configured model then fallbacks (404/transient)."""
    if not api_key:
        raise RuntimeError("missing_CLAUDE_API_KEY")
    last: Exception | None = None
    for cm in _claude_model_candidates(model):
        try:
            return _exchange_claude(cm, prompt, api_key=api_key)
        except Exception as ex:  # noqa: BLE001
            last = ex
            continue
    raise RuntimeError(f"claude_all_failed:{last}") from last


def _exchange_gemini_slot(model: str, prompt: str, *, gemini_key: str, claude_key: str) -> str:
    """Gemini slot; on total Gemini failure use Claude if ``CLAUDE_API_KEY`` is set.

    Emergency Claude fallback is **only** for ``provider=gemini`` slots — not when
    the slot is already Claude.
    """
    if gemini_key:
        try:
            return _exchange_gemini_with_fallback(model, prompt, api_key=gemini_key)
        except RuntimeError:
            if not claude_key:
                raise
    elif not claude_key:
        raise RuntimeError("missing_GEMINI_API_KEY")
    preferred = (os.getenv("DOOR_C_CLAUDE_MODEL") or "").strip()
    return _exchange_claude_slot(preferred or "claude-sonnet-4-5", prompt, api_key=claude_key)


def _exchange_for_provider(
    provider: str,
    model: str,
    prompt: str,
    *,
    gemini_key: str,
    openai_key: str,
    claude_key: str,
) -> str:
    """Dispatch Pair A/B exchange by provider string."""
    p = (provider or "").strip().lower()
    if p not in _DOOR_C_PROVIDERS:
        raise ValueError(f"door_c_unknown_provider:{p}")
    if p == "openai":
        if not openai_key:
            raise RuntimeError("missing_OPENAI_API_KEY")
        return _exchange_openai(model, prompt, api_key=openai_key)
    if p == "claude":
        return _exchange_claude_slot(model, prompt, api_key=claude_key)
    # gemini
    return _exchange_gemini_slot(
        model, prompt, gemini_key=gemini_key, claude_key=claude_key
    )


def _call_with_retry(
    *,
    label: str,
    fn: Callable[[], str],
) -> str:
    """One retry then fail-closed (raise). Billing/outage: no retry — raise typed error."""
    from app.pglpl.exrun_errors import classify_provider_message

    last: Exception | None = None
    for attempt in range(2):
        try:
            return fn()
        except Exception as ex:  # noqa: BLE001 — surface as judge transport error
            last = ex
            msg = str(ex)
            hit = classify_provider_message(text=msg, provider=label)
            if hit is not None:
                raise hit from ex
            delay = 3.0 if ("429" in msg or "Too Many Requests" in msg) else 0.6
            if attempt == 0:
                time.sleep(delay)
    raise RuntimeError(f"door_c_{label}_failed:{last}") from last


def assign_paragraph_ids(scopes_payload: list[dict[str, Any]]) -> list[str]:
    """Ensure each paragraph has a stable id ``{scope}#p{n}``; return all ids."""
    ids: list[str] = []
    for block in scopes_payload:
        scope = str(block.get("scope") or "scope")
        paras = block.get("paragraphs") or []
        for i, p in enumerate(paras, start=1):
            if not isinstance(p, dict):
                continue
            if not str(p.get("id") or "").strip():
                p["id"] = f"{scope}#p{i}"
            ids.append(str(p["id"]))
    return ids


def run_door_c_judges(
    scopes_payload: list[dict[str, Any]],
    *,
    judge_a: dict[str, str] | None = None,
    judge_b: dict[str, str] | None = None,
    consensus_fail_policy: str = "dual_approve",
    gemini_api_key: str | None = None,
    openai_api_key: str | None = None,
    claude_api_key: str | None = None,
    exchange_judge_a: JudgeExchangeFn | None = None,
    exchange_judge_b: JudgeExchangeFn | None = None,
    artifact_path: Path | None = None,
) -> dict[str, Any]:
    """Run dual judges in parallel over the batched payload; return consensus dict.

    ``judge_a`` / ``judge_b`` are ``{provider, model}``; omitted slots load from
    ``load_door_c_settings()``. Mock hooks receive ``(provider, model, prompt)``.
    """
    expected_ids = assign_paragraph_ids(scopes_payload)
    if not expected_ids:
        return {
            "ok": False,
            "error": "door_c_empty_payload",
            "failed_ids": [],
            "warnings": [],
            "paragraphs": [],
        }

    settings = load_door_c_settings()
    slot_a = _normalize_judge_slot(
        judge_a if judge_a is not None else settings.get("judge_a"),
        default=_DEFAULT_JUDGE_A,
        slot_name="judge_a",
    )
    slot_b = _normalize_judge_slot(
        judge_b if judge_b is not None else settings.get("judge_b"),
        default=_DEFAULT_JUDGE_B,
        slot_name="judge_b",
    )

    prompt = build_judge_prompt(scopes_payload)
    g_key = (gemini_api_key if gemini_api_key is not None else os.getenv("GEMINI_API_KEY", "")).strip()
    o_key = (openai_api_key if openai_api_key is not None else os.getenv("OPENAI_API_KEY", "")).strip()
    c_key = (claude_api_key if claude_api_key is not None else os.getenv("CLAUDE_API_KEY", "")).strip()

    def _run_slot(
        slot: dict[str, str],
        *,
        exchange: JudgeExchangeFn | None,
    ) -> str:
        provider = slot["provider"]
        model = slot["model"]
        if exchange is not None:
            return exchange(provider, model, prompt)
        return _exchange_for_provider(
            provider,
            model,
            prompt,
            gemini_key=g_key,
            openai_key=o_key,
            claude_key=c_key,
        )

    raw_a = ""
    raw_b = ""
    err: str | None = None
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            fut_a = pool.submit(
                _call_with_retry,
                label=f"judge_a_{slot_a['provider']}",
                fn=lambda: _run_slot(slot_a, exchange=exchange_judge_a),
            )
            fut_b = pool.submit(
                _call_with_retry,
                label=f"judge_b_{slot_b['provider']}",
                fn=lambda: _run_slot(slot_b, exchange=exchange_judge_b),
            )
            for fut in as_completed([fut_a, fut_b]):
                if fut is fut_a:
                    raw_a = fut.result()
                else:
                    raw_b = fut.result()
        map_a = parse_judge_response(raw_a)
        map_b = parse_judge_response(raw_b)
        result = consensus_quality_result(
            judge_a=map_a,
            judge_b=map_b,
            expected_ids=expected_ids,
            fail_policy=str(consensus_fail_policy or "dual_approve"),
        )
    except (RuntimeError, ValueError, json.JSONDecodeError, urllib.error.URLError) as ex:
        err = str(ex)
        result = {
            "ok": False,
            "error": err,
            "failed_ids": list(expected_ids),
            "warnings": [],
            "paragraphs": [],
        }

    prompt_version = effective_door_c_prompt_version()

    # Artifact: Pair A/B fields are canonical; raw_gemini/raw_openai kept one release.
    artifact = {
        "prompt_version": prompt_version,
        "scopes": scopes_payload,
        "judge_a_provider": slot_a["provider"],
        "judge_a_model": slot_a["model"],
        "judge_b_provider": slot_b["provider"],
        "judge_b_model": slot_b["model"],
        "raw_judge_a": raw_a,
        "raw_judge_b": raw_b,
        # Legacy aliases (historically Pair A=Gemini, Pair B=OpenAI).
        "gemini_model": slot_a["model"] if slot_a["provider"] == "gemini" else slot_a["model"],
        "openai_model": slot_b["model"] if slot_b["provider"] == "openai" else slot_b["model"],
        "raw_gemini": raw_a,
        "raw_openai": raw_b,
        "result": result,
        "error": err,
    }
    if artifact_path is not None:
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False), encoding="utf-8")
    result = dict(result)
    result["prompt_version"] = prompt_version
    result["artifact_path"] = str(artifact_path) if artifact_path else None
    result["error"] = err
    result["judge_a_provider"] = slot_a["provider"]
    result["judge_a_model"] = slot_a["model"]
    result["judge_b_provider"] = slot_b["provider"]
    result["judge_b_model"] = slot_b["model"]
    return result


def scopes_payload_from_snapshots(
    snapshots: list[tuple[str, list[dict[str, Any]]]],
) -> list[dict[str, Any]]:
    """Build Door C payload from ``(scope, paragraph_rows)`` snapshots."""
    out: list[dict[str, Any]] = []
    for scope, rows in snapshots:
        paras = []
        for i, row in enumerate(rows or [], start=1):
            text = str(row.get("text") or "").strip()
            if not text:
                continue
            fixed = row.get("fixed_surfaces") or []
            if not isinstance(fixed, list):
                fixed = []
            fixed = [str(x).strip() for x in fixed if str(x).strip()]
            paras.append(
                {
                    "id": f"{scope}#p{i}",
                    "text": text,
                    "row_id": row.get("id"),
                    "fixed_surfaces": fixed,
                }
            )
        if paras:
            out.append({"scope": scope, "paragraphs": paras})
    return out
