"""P3.1 — wiki claim audit CLI writes claims.jsonl with expected statuses."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RETAIL_PKG = REPO / "scripts" / "retail"
for p in (str(REPO), str(RETAIL_PKG)):
    if p not in sys.path:
        sys.path.insert(0, p)

from retail_brain.evidence.wiki_audit import (  # noqa: E402
    AuditPage,
    audit_page,
    default_claim_extractor,
    run_wiki_audit,
    summarize_claims_registry,
)
from retail_brain.evidence.wiki_claim_verifier import verify_wiki_claim  # noqa: E402


FIXTURE_BRAIN = Path(__file__).resolve().parent / "fixtures" / "wiki_audit_mini"


def test_verify_wiki_claim_supported_on_substring() -> None:
    """Claim text present in source → supported."""
    verdict = verify_wiki_claim(
        "Freezer range is 5°F to -8°F",
        {"fridge-docs_md/demo_MODEL/manual.md": "Freezer range is 5°F to -8°F when using the panel."},
    )
    assert verdict.status == "supported"


def test_verify_wiki_claim_unverified_without_sources() -> None:
    """No resolved sources → unverified."""
    verdict = verify_wiki_claim("Any claim here.", {})
    assert verdict.status == "unverified"


def test_audit_page_fixture_rows(tmp_path: Path) -> None:
    """Fixture wiki page yields at least one supported claim row."""
    brain = FIXTURE_BRAIN
    page_path = brain / "wiki" / "concepts" / "demo-page.md"
    text = page_path.read_text(encoding="utf-8")
    rows = audit_page(
        AuditPage(relpath="wiki/concepts/demo-page.md", text=text),
        brain_root=brain,
        claim_extractor=default_claim_extractor,
    )
    assert rows
    statuses = {r["status"] for r in rows}
    assert "supported" in statuses


def test_run_wiki_audit_writes_registry(tmp_path: Path) -> None:
    """CLI core writes claims.jsonl under .wiki-claim-audit/."""
    brain = tmp_path / "brain"
    src = FIXTURE_BRAIN
    (brain / "wiki").mkdir(parents=True)
    (brain / "raw").mkdir(parents=True)
    import shutil

    shutil.copytree(src / "wiki", brain / "wiki", dirs_exist_ok=True)
    shutil.copytree(src / "raw", brain / "raw", dirs_exist_ok=True)

    out = run_wiki_audit(brain_root=brain, logger=None)
    assert out.name == "claims.jsonl"
    assert out.is_file()
    lines = [json.loads(ln) for ln in out.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert lines
    assert all("status" in row and "claim" in row for row in lines)


def test_summarize_counts(tmp_path: Path) -> None:
    """Summarize groups registry rows by status."""
    reg = tmp_path / "claims.jsonl"
    reg.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "status": "supported",
                        "sku": "ge_x",
                        "page_relpath": "wiki/sources/a.md",
                        "claim": "c1",
                    }
                ),
                json.dumps(
                    {
                        "status": "contradicted",
                        "sku": "ge_x",
                        "page_relpath": "wiki/concepts/b.md",
                        "claim": "c2",
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    summary = summarize_claims_registry(reg)
    assert summary["rows"] == 2
    assert summary["by_status"]["supported"] == 1
    assert summary["by_status"]["contradicted"] == 1
