"""FTS normalize: finite strip of ticket boilerplate."""

import pytest

from retail_brain.text_normalize import (
    extract_diag_code,
    fts_query_text,
    search_text_for_fts,
    strip_case_ref_suffix,
    text_for_embedding,
)


def test_strip_case_ref_suffix() -> None:
    raw = "battery drains quickly on Galaxy A16. Case ref ITM-00000001 / T-0042-000001."
    assert strip_case_ref_suffix(raw) == "battery drains quickly on Galaxy A16."


def test_search_text_drops_au_prefix_and_ref() -> None:
    raw = (
        "Customer reports: SM-A156 SIM not recognised on Galaxy A16 5G. "
        "Case ref ITM-00000001 / T-0042-000001."
    )
    assert "Customer reports" not in search_text_for_fts(raw, market="AU")
    assert "Case ref" not in search_text_for_fts(raw, market="AU")
    assert "SM-A156" in search_text_for_fts(raw, market="AU")


def test_fts_query_strips_paraphrase_ref_tail() -> None:
    q = "Need help: caller says battery drains quickly (ref 000001)"
    norm = fts_query_text(q, market="AU")
    assert "(ref" not in norm.lower()
    assert "battery" in norm.lower()


def test_fts_query_screenshot_keeps_symptoms_and_code() -> None:
    q = (
        "Need help: Galaxy A15 5G, mobile data drops when switching to 5G. "
        "Battery drops from full to half within two hours. Error code SAM-E176."
    )
    norm = fts_query_text(q, market="AU")
    assert "SAM-E176" in norm
    assert "mobile" in norm.lower()
    assert "battery" in norm.lower()
    assert len(norm) > len("Technician log: diagnostic code SAM-E176.")


def test_text_for_embedding_retains_sam_e() -> None:
    raw = (
        "Customer reports: NFC fails on Galaxy A25 5G in Sydney, NSW. "
        "Technician log: diagnostic code SAM-E109."
    )
    emb = text_for_embedding(raw)
    assert "SAM-E109" in emb
    assert "Technician log:" in emb


def test_fts_query_aligns_eval_template_to_index_shape() -> None:
    q = (
        "Need help: Riley in Melbourne with a Galaxy A16 5G — battery drains quickly. "
        "Bluetooth pairing fails in the car every time."
    )
    norm = fts_query_text(q, market="AU")
    assert norm.startswith("battery drains quickly on Galaxy A16 5G in Melbourne.")
    assert "Bluetooth pairing" in norm


def test_extract_fru_diag_code(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RETAIL_FAULT_CODE_PREFIX", "FRU-E")
    from retail_brain import text_normalize

    text_normalize._DIAG_CODE = text_normalize.diag_code_pattern()
    assert extract_diag_code("Panel showed FRU-E142 on the door.") == "FRU-E142"
