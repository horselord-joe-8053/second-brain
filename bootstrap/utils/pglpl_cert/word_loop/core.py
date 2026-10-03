"""Word-loop core shared by ``expgtest`` (and, previously, the now-removed ``expgprod``
prod-seeding path — see war stories for why that mechanism turned out redundant).

Tracks per-scope pool item ids still needing a Door-C-verified paragraph, batches
Door C snapshots, and clears ``remain`` per paragraph when Door C passes. Door B uses
one generate call with all ``remain`` ids per scope; ``--n`` =
``targeted_words_per_paragraph`` splits paragraphs inside the API. expgtest
skips Door A and allows partial LPL progress at Door B (see refactor plan REMOVE_DOORA).

Catalog-23 scope list loads from ``config/seeds/catalog-23-pools.json`` (Layer A manifest).
The filename is a historical alias: the live catalog is the JSON scope count, not the number 23 in the name.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from utils.pglpl_cert.word_loop.door_c import (
    assign_paragraph_ids,
    load_door_c_settings,
    run_door_c_judges,
    scopes_payload_from_snapshots,
)

# Legacy fallback when manifest file is absent (export / first bootstrap only).
_LEGACY_NON_CONJ_CATALOG_23: tuple[str, ...] = (
    "places:continents",
    "places:countries",
    "places:states",
    "places:cities",
    "places:everyday",
    "places:gentilicos-continent",
    "places:gentilicos-country",
    "places:gentilicos-state",
    "places:gentilicos-city",
    "numbers:cardinals",
    "numbers:ordinals",
    "adjectives:endings",
    "determiners:demonstratives",
    "contractions:blending",
    "por-para:main",
    "inanimate:learn-by-heart",
    "inanimate:suffix-rule-binding",
    "inanimate:meaning-changers",
    "animated:fixed-article",
    "animated:same-form",
    "animated:two-forms",
    "animated:animals",
    "plural:plural",
    "comparison:unequal",
    "comparison:equal",
    "comparison:superlative",
    "comparison:irregulars",
)


def _load_non_conj_catalog_23() -> tuple[str, ...]:
    try:
        from app.catalog.catalog_23_manifest import catalog_23_scopes

        return catalog_23_scopes()
    except FileNotFoundError:
        return _LEGACY_NON_CONJ_CATALOG_23


# Deprecated alias — prefer ``app.catalog.catalog_23_manifest.catalog_23_scopes()``.
NON_CONJ_CATALOG_23: tuple[str, ...] = _load_non_conj_catalog_23()

EXPGTEST_22_SCOPES: tuple[str, ...] = tuple(
    s for s in NON_CONJ_CATALOG_23 if s != "numbers:cardinals"
)


@dataclass
class TaggedSnapshot:
    """One Door-B snapshot plus the pool word ids covered by its generate call.

    ``word_ids`` is the unshuffled slot guess used for packing. Remain credit
    uses blank ``content_id``s (``credit_ids_from_passed_tag``), not this field.
    """

    scope: str
    word_ids: list[int]
    rows: list[dict[str, Any]]
    door_c_id: str = ""


class BlankCreditError(ValueError):
    """Door C passed a paragraph that has no blank ``content_id``s to tick."""


def blank_content_ids_from_rows(
    rows: list[dict[str, Any]],
    *,
    scope: str | None = None,
) -> list[int]:
    """Ordered unique pool ids from snapshot ``blanks`` (Door C credit truth)."""
    from app.services.adjective_paragraph_pool import (
        adjective_blank_catalog_id,
        is_adjective_endings_scope,
    )

    adj_scope = is_adjective_endings_scope(scope or "")
    out: list[int] = []
    seen: set[int] = set()
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        blanks = row.get("blanks")
        if not isinstance(blanks, list):
            continue
        for blank in blanks:
            if not isinstance(blank, dict):
                continue
            raw = blank.get("content_id")
            if raw is None:
                continue
            try:
                cid = int(raw)
            except (TypeError, ValueError):
                continue
            if adj_scope:
                field = str(blank.get("field") or "").strip() or None
                cid = adjective_blank_catalog_id(cid, field)
            if cid in seen:
                continue
            seen.add(cid)
            out.append(cid)
    return out


def credit_ids_from_passed_tag(tag: TaggedSnapshot) -> list[int]:
    """Ids to drop from remain after a Door C pass — blanks, never ``word_ids``."""
    ids = blank_content_ids_from_rows(list(tag.rows or []), scope=tag.scope)
    if not ids:
        raise BlankCreditError(
            f"Door C pass scope={tag.scope!r} has no blank content_ids"
        )
    return ids


def remain_id_maps_equal(
    memory: dict[str, list[int]],
    ledger: dict[str, list[int]],
) -> bool:
    """True when per-scope leftover id *sets* match (order ignored)."""
    scopes = set(memory or ()) | set(ledger or ())
    for scope in scopes:
        left = {int(x) for x in (memory or {}).get(scope) or []}
        right = {int(x) for x in (ledger or {}).get(scope) or []}
        if left != right:
            return False
    return True


@dataclass
class RemainWordsState:
    """Mutable remain map: scope → pool ids still needing Door-C verification."""

    remain: dict[str, list[int]] = field(default_factory=dict)

    def is_empty(self) -> bool:
        return all(not ids for ids in self.remain.values())

    def remove_words(self, scope: str, word_ids: list[int]) -> None:
        if scope not in self.remain:
            return
        drop = set(int(x) for x in word_ids)
        self.remain[scope] = [i for i in self.remain[scope] if int(i) not in drop]

    def to_dict(self) -> dict[str, Any]:
        return {"remain": {k: list(v) for k, v in self.remain.items()}}

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> RemainWordsState:
        remain_raw = raw.get("remain") if isinstance(raw, dict) else {}
        remain: dict[str, list[int]] = {}
        if isinstance(remain_raw, dict):
            for scope, ids in remain_raw.items():
                if isinstance(ids, list):
                    remain[str(scope)] = [int(x) for x in ids]
        return cls(remain=remain)


def load_word_loop_settings(*, harness: str = "expgtest") -> dict[str, Any]:
    """Load outer-loop caps for ``expgtest`` CLI or ``admin`` word-loop bridge."""
    try:
        if harness == "admin":
            from app.services.main_config import get_admin_word_loop_settings

            return dict(get_admin_word_loop_settings())
        from app.services.main_config import get_expgtest_settings

        return {
            "max_overall_iterations": int(
                get_expgtest_settings().get("max_overall_iterations") or 4
            )
        }
    except Exception:
        if harness == "admin":
            return {"max_overall_iterations": 6, "door_c_chunk_size": 24}
        return {"max_overall_iterations": 4}


def door_b_api_n(requested_n: int, item_count: int, *, scope: str | None = None) -> int:
    """Chunk cap ``n`` for Door B generate POST (1–12, never above ``item_count``).

    Honors ``config/scope_paragraph.yaml`` fixed N when set for ``scope``.
    """
    from app.config.scope_paragraph_config import effective_paragraph_n

    count = max(0, int(item_count))
    eff = effective_paragraph_n(scope, int(requested_n))
    if count <= 0:
        return max(1, min(12, eff))
    return max(1, min(eff, count, 12))


def paragraph_word_id_chunks(
    item_ids: list[int],
    n: int,
    n_variety: int = 1,
    *,
    scope: str | None = None,
) -> list[list[int]]:
    """Map each generated paragraph slot to its pool word ids (scope chunk + variety)."""
    from app.pglpl.chunking import chunk_items_for_paragraph, expand_chunks_with_varieties

    ids = [int(x) for x in item_ids]
    scope_key = (scope or "").strip().lower()
    chunks = chunk_items_for_paragraph(scope_key, ids, max(1, int(n)))
    expanded = expand_chunks_with_varieties(chunks, max(1, int(n_variety)))
    return [[int(x) for x in chunk] for chunk in expanded]


def tagged_snapshots_from_door_b_rows(
    scope: str,
    remain_ids: list[int],
    rows: list[dict[str, Any]],
    *,
    n: int,
    n_variety: int = 1,
) -> list[TaggedSnapshot]:
    """Build one ``TaggedSnapshot`` per Door-B paragraph row (partial progress).

    ``slot_order`` is the row's position in the API's ``created[]`` list (see
    ``run_harness.run_scope`` ``allow_partial``) -- NOT necessarily a valid
    chunk index. ``created[]`` includes failed/retried attempts, so it can be
    longer than the planned chunk count; an LPL-OK row can land at a
    ``slot_order`` past the end of ``chunks`` even though it is a perfectly
    good paragraph. Prefer the row's own blank ``content_id``s (ground
    truth -- the same field remain-credit uses, see war story 141 and
    ``credit_ids_from_passed_tag``) and fall back to ``chunks[slot_order]``
    only when a row carries no ``blanks`` (keeps synthetic/legacy callers
    working). This way an out-of-range ``slot_order`` never silently drops a
    row that already passed LPL.
    """
    chunks = paragraph_word_id_chunks(remain_ids, n, n_variety, scope=scope)
    out: list[TaggedSnapshot] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        word_ids = blank_content_ids_from_rows([row], scope=scope)
        if not word_ids:
            slot = int(row.get("slot_order") if row.get("slot_order") is not None else 0)
            word_ids = list(chunks[slot]) if 0 <= slot < len(chunks) else []
        if not word_ids:
            continue
        out.append(TaggedSnapshot(scope=scope, word_ids=word_ids, rows=[row]))
    return out


def fetch_pool_ids(
    *,
    api_base_url: str,
    cookie: str,
    scope: str,
    origin: str,
    request_json: Callable[..., tuple[int, Any, str]],
) -> list[int]:
    """GET admin pool list and return ordered pool ids."""
    from pglpl_live.conj.conj_chain_scope import is_conj_harness_scope

    if is_conj_harness_scope(scope):
        from pglpl_live.conj.conj_run_harness import fetch_conj_vt_keys

        return fetch_conj_vt_keys(
            scope=scope,
            api_base_url=api_base_url,
            cookie=cookie,
            origin=origin,
            request_json=request_json,
            max_verbs=3,
        )

    from pglpl_live import resolve_target

    target = resolve_target(scope)
    status, pool, raw = request_json(
        api_base_url=api_base_url,
        method="GET",
        path=target.pool_path,
        cookie=cookie,
        origin=origin,
    )
    if status != 200 or not isinstance(pool, list):
        raise RuntimeError(f"pool {scope}: HTTP {status} {raw[:200]!r}")
    ids: list[int] = []
    for row in pool:
        if isinstance(row, dict) and row.get("id") is not None:
            ids.append(int(row["id"]))
    return ids


def pool_row_display_label(row: dict[str, Any]) -> str:
    """Human-readable pool row label for residual JSON (lemma only, no gloss)."""
    lemma = str(row.get("lemma") or row.get("label") or "").strip()
    if lemma:
        return lemma
    rid = row.get("id")
    return f"id:{rid}" if rid is not None else "unknown"


def fetch_pool_label_map(
    scope: str,
    *,
    api_base_url: str,
    cookie: str,
    origin: str,
    request_json: Callable[..., tuple[int, Any, str]],
) -> dict[int, str]:
    """Map pool content_id → display label for one scope."""
    from pglpl_live import resolve_target

    target = resolve_target(scope)
    status, pool, raw = request_json(
        api_base_url=api_base_url,
        method="GET",
        path=target.pool_path,
        cookie=cookie,
        origin=origin,
    )
    if status != 200 or not isinstance(pool, list):
        raise RuntimeError(f"pool labels {scope}: HTTP {status} {raw[:200]!r}")
    out: dict[int, str] = {}
    for row in pool:
        if isinstance(row, dict) and row.get("id") is not None:
            out[int(row["id"])] = pool_row_display_label(row)
    return out


def build_labeled_remain(
    remain_ids: dict[str, list[int]],
    label_maps: dict[str, dict[int, str]],
) -> dict[str, dict[str, str]]:
    """Build v2 residual ``remain`` block: scope → {id_str: label}."""
    out: dict[str, dict[str, str]] = {}
    for scope, ids in remain_ids.items():
        if not ids:
            continue
        scope_labels = label_maps.get(scope) or {}
        labeled: dict[str, str] = {}
        for word_id in sorted(int(x) for x in ids):
            labeled[str(word_id)] = scope_labels.get(word_id) or f"id:{word_id}"
        out[scope] = labeled
    return out


def parse_remain_block(raw_remain: Any) -> dict[str, list[int]]:
    """Parse v1 list-of-ids or v2 id→label map into scope → id lists."""
    if not isinstance(raw_remain, dict):
        raise ValueError("Missing or invalid 'remain' block")
    out: dict[str, list[int]] = {}
    for scope, value in raw_remain.items():
        if isinstance(value, list):
            out[str(scope)] = [int(x) for x in value]
        elif isinstance(value, dict):
            out[str(scope)] = [int(k) for k in value.keys()]
        else:
            raise ValueError(f"Invalid remain entry for scope {scope!r}")
    return out


def init_remain_state(
    scopes: list[str],
    *,
    api_base_url: str,
    cookie: str,
    origin: str,
    request_json: Callable[..., tuple[int, Any, str]],
) -> RemainWordsState:
    remain: dict[str, list[int]] = {}
    for scope in scopes:
        ids = fetch_pool_ids(
            api_base_url=api_base_url,
            cookie=cookie,
            scope=scope,
            origin=origin,
            request_json=request_json,
        )
        from app.domain.workbook_scope import is_conjugations_workbook_scope

        floor = 1 if is_conjugations_workbook_scope(scope) else 3
        if len(ids) < floor:
            raise RuntimeError(f"{scope}: need ≥{floor} pool items, got {len(ids)}")
        remain[scope] = ids
    return RemainWordsState(remain=remain)


def build_door_c_payload_from_tagged(
    tagged: list[TaggedSnapshot],
) -> tuple[list[dict[str, Any]], dict[str, TaggedSnapshot]]:
    """Group tagged snapshots by scope; return payload + map door_c_id → tag."""
    by_scope: dict[str, list[dict[str, Any]]] = {}
    # Track paragraph order per scope to map ids back to tags (one tag may yield multiple rows).
    scope_para_tags: dict[str, list[TaggedSnapshot]] = {}
    for tag in tagged:
        by_scope.setdefault(tag.scope, []).extend(tag.rows)
        scope_para_tags.setdefault(tag.scope, []).extend([tag] * len(tag.rows))
    snaps = [(scope, rows) for scope, rows in sorted(by_scope.items())]
    payload = scopes_payload_from_snapshots(snaps)
    assign_paragraph_ids(payload)
    id_map: dict[str, TaggedSnapshot] = {}
    for block in payload:
        scope = str(block.get("scope") or "")
        paras = block.get("paragraphs") or []
        tags_for_scope = scope_para_tags.get(scope) or []
        if len(paras) != len(tags_for_scope):
            continue
        for para, tag in zip(paras, tags_for_scope, strict=True):
            pid = str(para.get("id") or "")
            id_map[pid] = tag
    return payload, id_map


def tags_fully_passed_door_c(
    tagged: list[TaggedSnapshot],
    failed_ids: set[str],
    id_map: dict[str, TaggedSnapshot],
) -> list[TaggedSnapshot]:
    """Return tags whose **all** paragraph ids passed Door C (dual approve)."""
    if not id_map:
        return []
    tag_index = {id(t): i for i, t in enumerate(tagged)}
    pids_by_tag: dict[int, list[str]] = {i: [] for i in range(len(tagged))}
    for pid, tag in id_map.items():
        idx = tag_index.get(id(tag))
        if idx is not None:
            pids_by_tag[idx].append(pid)
    passed: list[TaggedSnapshot] = []
    for i, tag in enumerate(tagged):
        pids = pids_by_tag.get(i) or []
        if pids and all(pid not in failed_ids for pid in pids):
            passed.append(tag)
    return passed


def run_door_c_on_tagged(
    tagged: list[TaggedSnapshot],
    *,
    json_out_dir: Path,
    stamp: str,
    iter_label: str,
    door_c_cfg: dict[str, Any] | None = None,
    judge_fn: Callable[..., dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Run batched Door C on tagged snapshots; return judge result + passed tags."""
    if not tagged:
        return {"ok": True, "failed_ids": [], "passed": [], "artifact_path": None, "error": None}
    cfg = door_c_cfg or load_door_c_settings()
    payload, id_map = build_door_c_payload_from_tagged(tagged)
    judge_a = cfg.get("judge_a") or {"provider": "claude", "model": "claude-sonnet-4-5"}
    judge_b = cfg.get("judge_b") or {"provider": "openai", "model": "gpt-4.1"}
    artifact = json_out_dir / "tmp" / f"expgtest-door-c-{iter_label}-{stamp}.json"
    judge = judge_fn or run_door_c_judges
    result = judge(
        payload,
        judge_a={
            "provider": str(judge_a.get("provider") or "claude"),
            "model": str(judge_a.get("model") or "claude-sonnet-4-5"),
        },
        judge_b={
            "provider": str(judge_b.get("provider") or "openai"),
            "model": str(judge_b.get("model") or "gpt-4.1"),
        },
        consensus_fail_policy=str(cfg.get("consensus_fail_policy") or "dual_approve"),
        artifact_path=artifact,
    )
    failed = set(str(x) for x in (result.get("failed_ids") or []))
    passed = tags_fully_passed_door_c(tagged, failed, id_map)
    return {
        "ok": bool(result.get("ok")),
        "failed_ids": list(failed),
        "passed": passed,
        "artifact_path": result.get("artifact_path"),
        "error": result.get("error"),
    }


def persist_door_c_pipeline_statuses(
    tagged: list[TaggedSnapshot],
    door_c_result: dict[str, Any],
) -> dict[str, int]:
    """Write Door C pass/fail onto persisted paragraph rows (DB ids from snapshots).

    Judges reference synthetic ``{scope}#p{n}`` ids; snapshots carry ``row_id``
    with the admin generate integer pk when ``keep_paragraphs`` left rows in DB.
    """
    if not tagged or not door_c_result:
        return {"door_c_pass": 0, "door_c_fail": 0}
    payload, _id_map = build_door_c_payload_from_tagged(tagged)
    failed = {str(x) for x in (door_c_result.get("failed_ids") or [])}
    pass_ids: list[int] = []
    fail_ids: list[int] = []
    for block in payload:
        for para in block.get("paragraphs") or []:
            if not isinstance(para, dict):
                continue
            door_c_id = str(para.get("id") or "")
            raw_db = para.get("row_id")
            if raw_db is None and door_c_id.isdigit():
                raw_db = door_c_id
            if raw_db is None:
                continue
            try:
                db_id = int(raw_db)
            except (TypeError, ValueError):
                continue
            if door_c_id in failed:
                fail_ids.append(db_id)
            else:
                pass_ids.append(db_id)
    if not pass_ids and not fail_ids:
        return {"door_c_pass": 0, "door_c_fail": 0}
    from app.db.session import _maker
    from app.services.gender_paragraph_generator import set_gender_paragraph_pipeline_status
    from app.services.gender_paragraph_status import GenderParagraphPipelineStatus

    door_c_prompt_version = str(door_c_result.get("prompt_version") or "").strip() or None

    session = _maker()()
    try:
        n_pass = 0
        n_fail = 0
        if pass_ids:
            n_pass = set_gender_paragraph_pipeline_status(
                session,
                ids=pass_ids,
                status=GenderParagraphPipelineStatus.DOOR_C_PASS.value,
                door_c_prompt_version=door_c_prompt_version,
            )
        if fail_ids:
            n_fail = set_gender_paragraph_pipeline_status(
                session,
                ids=fail_ids,
                status=GenderParagraphPipelineStatus.DOOR_C_FAIL.value,
                door_c_prompt_version=door_c_prompt_version,
            )
    finally:
        session.close()
    return {"door_c_pass": n_pass, "door_c_fail": n_fail}


def residual_dir_for_harness(harness: str = "expgtest") -> str:
    """Default residual JSON directory (only ``expgtest`` remains; kept as a
    parameter for call-site compatibility rather than a hardcoded literal)."""
    return "ops/run-logs/expgtest-residuals"


def export_residual_json(
    stamp: str,
    remain: dict[str, list[int]] | RemainWordsState,
    api_base_url: str,
    *,
    exrun_seq: int = 1,
    completed_tl_itr: int = 0,
    residual_dir: Path | str | None = None,
    harness: str = "expgtest",
    cookie: str | None = None,
    origin: str | None = None,
    request_json: Callable[..., tuple[int, Any, str]] | None = None,
    run_layout_v2: bool = False,
    chain_id: str | None = None,
    task: str | None = None,
    chain_exrun_seq: int | None = None,
) -> Path | None:
    """Export standardized residual JSON after an ex-run completes or is interrupted.

    Writes v2 schema (id→label ``remain`` map) when ``cookie`` and ``request_json`` are
    provided; otherwise falls back to v1 list-of-ids for tests without API access.
    Only writes a file if ``remaining_total_words > 0``.
    """
    remain_map: dict[str, list[int]] = (
        remain.remain if isinstance(remain, RemainWordsState) else dict(remain)
    )
    filtered_remain = {k: sorted(list(v)) for k, v in remain_map.items() if v}
    remaining_total = sum(len(ids) for ids in filtered_remain.values())

    if remaining_total == 0:
        return None

    out_dir = Path(residual_dir or residual_dir_for_harness(harness))
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"expgtest-residual-exrun{exrun_seq}-itr{completed_tl_itr}-{stamp}.json"

    version = 1
    remain_export: dict[str, Any] = filtered_remain
    if cookie and request_json and origin is not None:
        label_maps: dict[str, dict[int, str]] = {}
        for scope in filtered_remain:
            try:
                label_maps[scope] = fetch_pool_label_map(
                    scope,
                    api_base_url=api_base_url,
                    cookie=cookie,
                    origin=origin,
                    request_json=request_json,
                )
            except Exception:
                label_maps[scope] = {}
        remain_export = build_labeled_remain(filtered_remain, label_maps)
        version = 2

    payload = {
        "version": version,
        "stamp": stamp,
        "exrun_seq": int(exrun_seq),
        "completed_tl_itr": int(completed_tl_itr),
        "api_base_url": api_base_url,
        "remain": remain_export,
        "remaining_total_words": remaining_total,
    }
    if chain_id:
        payload["chain_id"] = chain_id
    if task:
        payload["task"] = task
    write_json_artifact(out_path, payload)
    return out_path


def load_residual_json(path: Path | str) -> dict[str, Any]:
    """Load and validate standardized v1/v2 residual JSON file."""
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Residual file not found: {p}")
    data = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Invalid residual JSON payload in {p}")
    remain_raw = data.get("remain")
    remain_ids = parse_remain_block(remain_raw)
    remain_labels: dict[str, dict[str, str]] | None = None
    if isinstance(remain_raw, dict):
        for scope, value in remain_raw.items():
            if isinstance(value, dict) and value and all(isinstance(v, str) for v in value.values()):
                if remain_labels is None:
                    remain_labels = {}
                remain_labels[str(scope)] = {str(k): str(v) for k, v in value.items()}
    return {
        "version": data.get("version", 1),
        "stamp": str(data.get("stamp") or ""),
        "exrun_seq": int(data.get("exrun_seq") or 1),
        "completed_tl_itr": int(
            data.get("completed_tl_itr")
            if data.get("completed_tl_itr") is not None
            else (data.get("iterations_run") or data.get("iteration") or 0)
        ),
        "api_base_url": str(data.get("api_base_url") or ""),
        "remain": remain_ids,
        "remain_labels": remain_labels,
        "remaining_total_words": int(data.get("remaining_total_words") or 0),
    }


def campaign_stamp() -> str:
    """Campaign stamp in local timezone: ``YYMMDD-HHMMSS`` (matches ``chain_id`` TZ)."""
    return datetime.now().astimezone().strftime("%y%m%d-%H%M%S")


def write_json_artifact(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
