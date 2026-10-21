"""FRU company profile YAML loader."""

from pathlib import Path

from retail_brain.company_profile import load_company_profile


def test_fru_profile_loads_24_issues() -> None:
    prof = load_company_profile()
    assert prof.market == "US"
    assert prof.fault_code_prefix == "FRU-E"
    assert len(prof.issues) >= 24
    assert prof.detail_slots


def test_fru_customers_seed_count() -> None:
    path = Path(__file__).resolve().parents[2] / "scripts/retail/sim_data/seed/fru_customers.jsonl"
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 150
