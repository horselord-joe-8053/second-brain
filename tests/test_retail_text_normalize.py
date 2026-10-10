"""FTS normalize: finite strip of ticket boilerplate."""

from retail_brain.text_normalize import (
    fts_query_text,
    search_text_for_fts,
    strip_case_ref_suffix,
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


def test_fts_query_aligns_eval_template_to_index_shape() -> None:
    q = (
        "Need help: Riley in Melbourne with a Galaxy A16 5G — battery drains quickly. "
        "Bluetooth pairing fails in the car every time."
    )
    norm = fts_query_text(q, market="AU")
    assert norm.startswith("battery drains quickly on Galaxy A16 5G in Melbourne.")
    assert "Bluetooth pairing" in norm
