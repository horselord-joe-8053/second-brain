"""Offline wiki claim audit: compiled pages vs lane raw sources (Phase 3 P3.1)."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterator, Sequence

from retail_brain.answer_manuals import parse_frontmatter_sources
from retail_brain.sim_data_profile import repo_root

from .wiki_claim_verifier import WikiClaimVerdict, verify_wiki_claim

_CLAIM_SPLIT = re.compile(r"(?<=[.!?])\s+")
_DEFAULT_BRAIN_REL = Path("brain/retail-md")
_REGISTRY_DIR = ".wiki-claim-audit"
_CLAIMS_FILE = "claims.jsonl"
_PROGRESS_FILE = "audit_progress.jsonl"

ClaimExtractor = Callable[[str, str], list[str]]


@dataclass
class AuditPage:
    """One compiled wiki markdown file under ``wiki/``."""

    relpath: str
    text: str


def default_claim_extractor(body: str, _page_relpath: str) -> list[str]:
    """Stub extractor for CI: non-heading sentences from page body (no live LLM)."""
    lines = [ln.strip() for ln in (body or "").splitlines() if ln.strip()]
    paras: list[str] = []
    buf: list[str] = []
    for ln in lines:
        if ln.startswith("#"):
            if buf:
                paras.append(" ".join(buf))
                buf = []
            continue
        buf.append(ln)
    if buf:
        paras.append(" ".join(buf))
    claims: list[str] = []
    for para in paras:
        for sent in _CLAIM_SPLIT.split(para):
            s = sent.strip()
            if len(s) >= 24:
                claims.append(s)
    return claims[:12]


def _body(page_text: str) -> str:
    m = re.match(r"\A---\s*\n.*?\n---\s*\n", page_text or "", re.DOTALL)
    return page_text[m.end() :] if m else (page_text or "")


def resolve_source_files(brain_root: Path, source_entries: Sequence[str]) -> dict[str, Path]:
    """Map frontmatter source strings to readable files under ``raw/sources/``."""
    raw_root = brain_root / "raw" / "sources"
    out: dict[str, Path] = {}
    for entry in source_entries:
        entry = entry.strip().strip('"').strip("'")
        if not entry:
            continue
        if entry.startswith("fridge-docs/"):
            rel = Path("fridge-docs") / Path(entry).relative_to("fridge-docs")
            candidates = [raw_root / rel]
        elif entry.startswith("fridge-docs_md/"):
            sub = entry.split("/", 1)[1] if "/" in entry else entry
            parts = Path(sub).parts
            sku = parts[0] if parts else ""
            candidates = []
            if sku:
                candidates.append(raw_root / "fridge-docs_md" / sku / "user-guide.md")
            rel_path = raw_root / "fridge-docs_md" / sub
            if rel_path.suffix.lower() == ".png":
                candidates.append(rel_path.with_suffix(".md"))
            candidates.append(rel_path)
        else:
            candidates = [raw_root / entry, brain_root / entry]

        for cand in candidates:
            if cand.is_file() and cand.suffix.lower() in {".md", ".txt"}:
                key = entry
                out[key] = cand
                break
    return out


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_sources(paths: dict[str, Path]) -> dict[str, str]:
    texts: dict[str, str] = {}
    for key, path in paths.items():
        try:
            texts[key] = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
    return texts


def iter_wiki_pages(brain_root: Path, *, wiki_glob: str = "**/*.md") -> Iterator[AuditPage]:
    """Yield markdown pages under the lane brain ``wiki/`` tree."""
    wiki_root = brain_root / "wiki"
    if not wiki_root.is_dir():
        return
    for path in sorted(wiki_root.glob(wiki_glob)):
        if not path.is_file():
            continue
        rel = path.relative_to(brain_root).as_posix()
        texts = path.read_text(encoding="utf-8", errors="replace")
        yield AuditPage(relpath=rel, text=texts)


def audit_page(
    page: AuditPage,
    *,
    brain_root: Path,
    claim_extractor: ClaimExtractor = default_claim_extractor,
) -> list[dict[str, Any]]:
    """Audit one wiki page; return registry rows (not yet written)."""
    sources = parse_frontmatter_sources(page.text)
    src_paths = resolve_source_files(brain_root, sources)
    src_texts = _read_sources(src_paths)
    src_hashes = {k: _file_hash(p) for k, p in src_paths.items()}
    body = _body(page.text)
    claims = claim_extractor(body, page.relpath)
    rows: list[dict[str, Any]] = []
    for claim in claims:
        verdict: WikiClaimVerdict = verify_wiki_claim(claim, src_texts)
        src_key = verdict.source_relpath
        rows.append(
            {
                "page_relpath": page.relpath,
                "claim": claim,
                "status": verdict.status,
                "source_relpath": src_key,
                "source_hash": src_hashes.get(src_key or "", "") if src_key else "",
                "reasons": verdict.reasons,
                "audited_at": datetime.now(timezone.utc).isoformat(),
            }
        )
    return rows


def run_wiki_audit(
    *,
    brain_root: Path,
    registry_dir: Path | None = None,
    wiki_glob: str = "**/*.md",
    claim_extractor: ClaimExtractor = default_claim_extractor,
    progress_writer: Callable[[dict[str, Any]], None] | None = None,
    logger: Any = None,
    max_pages: int = 0,
) -> Path:
    """Scan wiki pages and write ``claims.jsonl`` under ``.wiki-claim-audit/``."""
    reg_dir = registry_dir or (brain_root / _REGISTRY_DIR)
    reg_dir.mkdir(parents=True, exist_ok=True)
    out_path = reg_dir / _CLAIMS_FILE
    rows_written = 0
    pages_scanned = 0
    if logger:
        logger.phase_start("wiki claim audit")
        logger.info(f"brain_root={brain_root} registry={out_path}")
    with out_path.open("w", encoding="utf-8") as out:
        for page in iter_wiki_pages(brain_root, wiki_glob=wiki_glob):
            if max_pages and pages_scanned >= max_pages:
                break
            pages_scanned += 1
            page_rows = audit_page(page, brain_root=brain_root, claim_extractor=claim_extractor)
            for row in page_rows:
                out.write(json.dumps(row, ensure_ascii=False) + "\n")
                rows_written += 1
            if progress_writer:
                progress_writer(
                    {
                        "ts": datetime.now(timezone.utc).isoformat(),
                        "page_relpath": page.relpath,
                        "claims": len(page_rows),
                    }
                )
            if logger:
                logger.step(f"{page.relpath}: {len(page_rows)} claims")
    if logger:
        logger.success(f"pages={pages_scanned} claims={rows_written} -> {out_path}")
        logger.phase_end("wiki claim audit")
    return out_path


def _default_logger():
    from utils.neat_logger.neat_logger_instance import NeatLoggerFactory

    return NeatLoggerFactory.create(
        "OPS",
        "WIKI_CLAIM_AUDIT",
        log_file_name="wiki-claim-audit.log",
        log_output="both",
    )


def summarize_claims_registry(claims_path: Path) -> dict[str, Any]:
    """Aggregate claim rows by status, SKU, and wiki/sources vs other paths."""
    counts: dict[str, int] = {}
    by_sku: dict[str, int] = {}
    sources_pages = 0
    other_pages: set[str] = set()
    pages: set[str] = set()
    if not claims_path.is_file():
        return {
            "claims_path": str(claims_path),
            "rows": 0,
            "by_status": {},
            "by_sku": {},
            "source_only_pages": 0,
            "other_page_count": 0,
        }
    with claims_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            status = str(row.get("status") or "unknown")
            counts[status] = counts.get(status, 0) + 1
            sku = str(row.get("sku") or row.get("model_id") or "_none")
            by_sku[sku] = by_sku.get(sku, 0) + 1
            page = str(row.get("page_relpath") or "")
            if page:
                pages.add(page)
                norm = page.replace("\\", "/")
                if "/wiki/sources/" in f"/{norm}" or norm.startswith("wiki/sources/"):
                    sources_pages += 1
                else:
                    other_pages.add(page)
    return {
        "claims_path": str(claims_path),
        "rows": sum(counts.values()),
        "by_status": counts,
        "by_sku": by_sku,
        "distinct_pages": len(pages),
        "source_page_claim_rows": sources_pages,
        "non_source_distinct_pages": len(other_pages),
    }


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry: ``python -m retail_brain.evidence.wiki_audit``."""
    parser = argparse.ArgumentParser(description="Audit compiled wiki claims vs lane raw sources.")
    parser.add_argument(
        "--brain-root",
        type=Path,
        default=None,
        help="Lane brain root (default: repo brain/retail-md)",
    )
    parser.add_argument("--wiki-glob", default="**/*.md", help="Glob under brain_root/wiki")
    parser.add_argument("--max-pages", type=int, default=0, help="Stop after N pages (0 = all)")
    parser.add_argument(
        "--summarize",
        action="store_true",
        help="Print JSON summary of existing claims.jsonl (no rescan)",
    )
    parser.add_argument(
        "--summary-out",
        type=Path,
        default=None,
        help="With --summarize: write summary JSON to this path",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)
    root = repo_root()
    brain = (args.brain_root or (root / _DEFAULT_BRAIN_REL)).resolve()
    if not brain.is_dir():
        print(f"brain root missing: {brain}", file=sys.stderr)
        return 2
    claims_path = brain / _REGISTRY_DIR / _CLAIMS_FILE
    if args.summarize:
        summary = summarize_claims_registry(claims_path)
        text = json.dumps(summary, indent=2)
        if args.summary_out:
            args.summary_out.parent.mkdir(parents=True, exist_ok=True)
            args.summary_out.write_text(text + "\n", encoding="utf-8")
        print(text)
        return 0
    log = _default_logger()
    progress_path = brain / _REGISTRY_DIR / _PROGRESS_FILE

    def _progress(row: dict[str, Any]) -> None:
        progress_path.parent.mkdir(parents=True, exist_ok=True)
        with progress_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    run_wiki_audit(
        brain_root=brain,
        wiki_glob=args.wiki_glob,
        progress_writer=_progress,
        logger=log,
        max_pages=max(0, int(args.max_pages or 0)),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
