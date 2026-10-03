#!/usr/bin/env python3
"""List learner-visible paragraph exercises (Door C pass + Finally OK, non-legacy scopes).

Uses the same filter as ``get_published_exercises`` / ``is_learner_practice_row`` in
``apps/api/app/services/gender_paragraph_legit.py``. Excludes clitics nine-chip legacy
scopes (``CLITICS_LEGACY_SCOPE_ALIASES``) that the UI no longer queries.

Run from repo root::

    cd apps/api && uv run python ../../.cursor/rules/project_specific/code/actpara_list_active.py
    cd apps/api && uv run python ../../.cursor/rules/project_specific/code/actpara_list_active.py --scope clitics:pronominal-verb
    cd apps/api && uv run python ../../.cursor/rules/project_specific/code/actpara_list_active.py --json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

# Resolve repo + apps/api for imports when invoked from any cwd.
_HERE = Path(__file__).resolve()
_REPO = _HERE.parents[4]
if not (_REPO / "config" / "main_config.yaml").exists():
    _REPO = _HERE.parents[3]
_APPS_API = _REPO / "apps" / "api"
for p in (str(_APPS_API), str(_REPO)):
    if p not in sys.path:
        sys.path.insert(0, p)

os.environ.setdefault("REPO_ROOT", str(_REPO))


def _load_dotenv() -> None:
    env_path = _REPO / ".env"
    if not env_path.is_file():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and (key not in os.environ or not str(os.environ.get(key, "")).strip()):
            os.environ[key] = value


@dataclass(frozen=True)
class ActiveParagraphRow:
    id: int
    scope: str
    n: int
    status: str
    gen_finally_ok: bool
    chars: int


def _list_active(*, scope: str | None = None) -> list[ActiveParagraphRow]:
    from app.db.connection import get_engine
    from app.db.models.learning_suite_schema import GenderParagraphExercise
    from app.services.area_paragraph_registry import CLITICS_LEGACY_SCOPE_ALIASES
    from app.services.gender_paragraph_legit import is_learner_practice_row

    legacy = frozenset(CLITICS_LEGACY_SCOPE_ALIASES.keys())
    want_scope = (scope or "").strip().lower() or None

    engine = get_engine()
    with Session(engine) as db:
        rows = list(db.scalars(select(GenderParagraphExercise)).all())

    out: list[ActiveParagraphRow] = []
    for row in rows:
        if row.scope in legacy:
            continue
        if not is_learner_practice_row(row):
            continue
        if want_scope and row.scope != want_scope:
            continue
        out.append(
            ActiveParagraphRow(
                id=int(row.id),
                scope=str(row.scope),
                n=int(row.n),
                status=str(row.status),
                gen_finally_ok=bool(row.gen_finally_ok),
                chars=len(str(row.paragraph_text or "")),
            )
        )
    out.sort(key=lambda r: (r.scope, r.id))
    return out


def _print_table(rows: list[ActiveParagraphRow]) -> None:
    by_scope = Counter(r.scope for r in rows)
    print(f"Active learner paragraphs: {len(rows)} rows across {len(by_scope)} scopes")
    print(f"{'scope':<42} {'count':>5}  ids (sample)")
    for scope, count in sorted(by_scope.items()):
        ids = [r.id for r in rows if r.scope == scope]
        sample = ", ".join(str(i) for i in ids[:8])
        if len(ids) > 8:
            sample += f", … (+{len(ids) - 8})"
        print(f"{scope:<42} {count:>5}  {sample}")


def main() -> int:
    _load_dotenv()

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scope",
        default="",
        help="Optional canonical scope filter (e.g. clitics:pronominal-verb).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON array instead of a summary table.",
    )
    args = parser.parse_args()

    try:
        rows = _list_active(scope=args.scope or None)
    except RuntimeError as exc:
        print(f"actpara: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps([asdict(r) for r in rows], indent=2))
    else:
        _print_table(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
