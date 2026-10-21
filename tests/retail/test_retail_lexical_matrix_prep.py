"""Prep scripts for Phase 8 lexical × A/B/C matrix (layout contract)."""

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PREP = REPO / "cursor_gen" / "retail_v11_prep"
LEX = PREP / "lexical_docker"


def test_lexical_matrix_orchestrator_exists() -> None:
    """06_run_abcd_lexical_matrix.sh is the operator entry for four backends × three search modes."""
    script = PREP / "06_run_abcd_lexical_matrix.sh"
    assert script.is_file()
    text = script.read_text(encoding="utf-8")
    assert "tantivy" in text and "open_search" in text
    assert "rrf_data_llm_gen" in text


def test_lexical_docker_sidecar_scripts_exist() -> None:
    """One-at-a-time ParadeDB / OpenSearch helpers live under lexical_docker/."""
    for name in ("stop_sidecars.sh", "parade_up.sh", "opensearch_up.sh"):
        path = LEX / name
        assert path.is_file(), name
    stop = (LEX / "stop_sidecars.sh").read_text(encoding="utf-8")
    assert "retail_lexical_parade" in stop
    assert "retail_lexical_opensearch" in stop


def test_rebuild_lexical_index_script_exists() -> None:
    """Rebuild-only entrypoint avoids re-embed when switching RETAIL_LEXICAL_BACKEND."""
    path = REPO / "scripts" / "retail" / "rebuild_lexical_index.py"
    assert path.is_file()
    assert "rebuild_active" in path.read_text(encoding="utf-8")


def test_parade_schema_sql_exists() -> None:
    """Parade sidecar table + bm25 index DDL is versioned under scripts/retail/schema/."""
    sql = REPO / "scripts" / "retail" / "schema" / "003_lexical_parade_tickets.sql"
    assert sql.is_file()
    body = sql.read_text(encoding="utf-8")
    assert "lexical_tickets" in body
    assert "bm25" in body.lower()
