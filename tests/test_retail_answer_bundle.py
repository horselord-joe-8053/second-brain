"""``retail_answer.v1`` bundle (P7/P13): schema, determinism, leg isolation, renderer, CLI."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.retail_answer_integration

from retail_brain.answer_bundle import SCHEMA, build_answer_bundle, bundle_to_json
from retail_brain.answer_manuals import FixtureWikiClient
from retail_brain.answer_render import render_markdown
from retail_brain.answer_tickets import InMemoryTicketSource
from retail_brain.hybrid_search import TicketRow
from retail_brain.txt_docs import TxtDocIndex, TxtDocRow

REPO = Path(__file__).resolve().parents[1]
GOLDEN = REPO / "tests" / "fixtures" / "retail_answer" / "golden_bundle.json"
SAM = "samsung_RF28K9070SG"
SAM_TXT = f"raw/sources/fridge-docs/{SAM}/user-guide.txt"

ROWS = [
    TicketRow("T-1", "RF28K9070SG", "resolved", "ice maker stopped producing cubes FRU-E101", "Reset ice maker."),
    TicketRow("T-2", "RF28K9070SG", "resolved", "door alarm keeps beeping", "Realigned door gasket."),
    TicketRow("T-3", "RF28K9070SG", "received", "ice maker stopped producing cubes", ""),
    TicketRow("T-4", "GNE27JYMFS", "resolved", "ice maker stopped producing cubes", "Lowered feeler arm."),
]
ISSUES = {"T-1": "ice_maker_no_ice", "T-2": "door_alarm", "T-4": "ice_maker_no_ice"}
QUERY = "Customer with RF28K9070SG: ice maker not making ice, code FRU-E101"
TOP_KEYS = {
    "schema",
    "profile",
    "corpus_profile",
    "query",
    "model",
    "model_sku",
    "fault_code",
    "tickets",
    "manuals",
    "diagnostics",
}


def _index() -> TxtDocIndex:
    """Samsung user guide with ice maker and door alarm passages."""
    return TxtDocIndex(
        [
            TxtDocRow(
                SAM_TXT,
                SAM,
                "user",
                "Ice maker not making ice check water supply line and shutoff valve. "
                "Door alarm beeping close the door firmly.",
            ),
        ]
    )


def _wiki() -> FixtureWikiClient:
    """One compiled Samsung page citing the user guide ``.txt``."""
    return FixtureWikiClient(
        {
            "wiki/sources/samsung-user-guide.md": (
                f'---\ntype: source\nsources: ["fridge-docs/{SAM}/user-guide.txt"]\n---\n# Samsung guide\n\n'
                "## Ice maker\nIf the ice maker is not making ice, check the water supply line and shutoff valve.\n"
            ),
        },
    )


def _bundle(**kw: object) -> dict:
    """Bundle for QUERY with in-memory tickets, fixture wiki, synthetic txt index."""
    args = dict(ticket_source=InMemoryTicketSource(ROWS, ISSUES), txt_index=_index(), wiki=_wiki())
    args.update(kw)
    return build_answer_bundle(QUERY, **args)


def test_schema_keys_and_model_detection() -> None:
    """Top-level keys fixed; model + manual folder + fault code inferred from the query text."""
    b = _bundle()
    assert set(b) == TOP_KEYS
    assert b["schema"] == SCHEMA == "retail_answer.v1"
    assert (b["profile"], b["model"], b["model_sku"], b["fault_code"]) == ("retail", "RF28K9070SG", SAM, "FRU-E101")
    assert set(b["diagnostics"]) == {"ticket_leg_ok", "manual_leg_ok", "wiki_available", "notes"}


def test_both_legs_always_present() -> None:
    """Top-2 resolved same-model tickets AND a manual hit with doc-level raw provenance."""
    b = _bundle()
    tids = [h["ticket_id"] for h in b["tickets"]["hits"]]
    assert tids[0] == "T-1" and len(tids) <= 2 and set(tids) <= {"T-1", "T-2"}
    m = b["manuals"]["hits"][0]
    assert m["source"] == "wiki"
    origin = m["raw_origin"]
    assert origin["doc_path"] == SAM_TXT
    assert origin["pages"] == []
    assert origin["archive_pdf_path"] == f"archive/fridge-docs/{SAM}/user-guide.pdf"


def test_ticket_leg_failure_is_isolated() -> None:
    """Broken ticket backend → empty ticket hits + note; manual leg still answers."""

    class Boom:
        """Ticket source whose database is down."""

        issue_keys: dict = {}

        def hits(self, query: str, *, model: object, limit: int) -> tuple:
            """Simulate a connection failure."""
            raise ConnectionError("pg down")

    b = _bundle(ticket_source=Boom())
    assert b["tickets"]["hits"] == [] and b["diagnostics"]["ticket_leg_ok"] is False
    assert any("pg down" in n for n in b["diagnostics"]["notes"])
    assert b["manuals"]["hits"] and b["diagnostics"]["manual_leg_ok"] is True


def test_bundle_json_is_byte_stable_and_matches_golden(monkeypatch: pytest.MonkeyPatch) -> None:
    """Two builds serialize identically; snapshot pinned (RETAIL_UPDATE_GOLDEN=1 rewrites it)."""
    monkeypatch.setenv("RETAIL_TICKET_SEARCH_MODE", "rrf_term_boosted")
    a, b = bundle_to_json(_bundle()), bundle_to_json(_bundle())
    assert a == b
    assert "timestamp" not in a and json.loads(a)["schema"] == SCHEMA
    if os.environ.get("RETAIL_UPDATE_GOLDEN") == "1":
        GOLDEN.parent.mkdir(parents=True, exist_ok=True)
        GOLDEN.write_text(a, encoding="utf-8")
    assert GOLDEN.read_text(encoding="utf-8") == a


def test_build_answer_bundle_skip_legs() -> None:
    """Each leg can be skipped independently (P17); default runs both."""
    full = _bundle()
    assert full["tickets"]["hits"]
    assert full["manuals"]["hits"]
    src = InMemoryTicketSource(ROWS, ISSUES)
    wiki = _wiki()
    idx = _index()
    ticket_only = build_answer_bundle(
        "ice maker stopped producing cubes",
        ticket_source=src,
        txt_index=idx,
        wiki=wiki,
        model="RF28K9070SG",
        skip_manual_leg=True,
    )
    assert ticket_only["tickets"]["hits"]
    assert ticket_only["manuals"]["hits"] == []
    assert "manual leg skipped" in ticket_only["diagnostics"]["notes"]
    manual_only = build_answer_bundle(
        "ice maker stopped producing cubes",
        ticket_source=src,
        txt_index=idx,
        wiki=wiki,
        model="RF28K9070SG",
        skip_ticket_leg=True,
    )
    assert manual_only["tickets"]["hits"] == []
    assert manual_only["tickets"]["search_mode"] == "skipped"
    assert manual_only["manuals"]["hits"]


def test_render_markdown_cites_doc_path_and_similarity() -> None:
    """Renderer keeps every reference: ticket ids with cosine, ``doc_path``."""
    b = _bundle()
    md = render_markdown(b)
    assert md == render_markdown(b)
    assert "T-1" in md and f"cosine {b['tickets']['hits'][0]['cosine_similarity']:.4f}" in md
    assert SAM_TXT in md
    assert "wiki/sources/samsung-user-guide.md" in md


def test_cli_offline_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """CLI ``main`` over CSV + ``.txt`` corpus, no wiki → ``raw_txt`` hit."""
    csv_path = tmp_path / "q.csv"
    csv_path.write_text(
        "ticket_id,model,status,customer_query_text,resolution_text\n"
        "T-1,RF28K9070SG,resolved,ice maker stopped producing cubes,Reset ice maker.\n",
        encoding="utf-8",
    )
    brain = tmp_path / "retail"
    txt = brain / "raw" / "sources" / "fridge-docs" / SAM / "user-guide.txt"
    txt.parent.mkdir(parents=True)
    txt.write_text("Ice maker not making ice check water supply line and shutoff valve.", encoding="utf-8")
    monkeypatch.setenv("RETAIL_TICKET_SEARCH_MODE", "vector_only")
    monkeypatch.setenv("RETAIL_FAULT_CODE_PREFIX", "FRU-E")
    spec = importlib.util.spec_from_file_location("answer_ticket_cli", REPO / "scripts/retail/answer/answer_ticket.py")
    cli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cli)
    rc = cli.main(
        [
            "--query",
            "ice maker not making ice",
            "--model",
            "RF28K9070SG",
            "--tickets-csv",
            str(csv_path),
            "--brain-root",
            str(brain),
            "--no-wiki",
            "--json",
        ]
    )
    assert rc == 0
    b = json.loads(capsys.readouterr().out)
    assert b["tickets"]["hits"][0]["ticket_id"] == "T-1"
    assert b["manuals"]["hits"][0]["source"] == "raw_txt"
    assert b["manuals"]["hits"][0]["raw_origin"]["doc_path"] == SAM_TXT
