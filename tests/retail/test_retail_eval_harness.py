"""Eval harness baseline (vector mode)."""

import os
from pathlib import Path

from retail_brain.eval_harness import run_eval, write_report


def test_eval_harness_vector_mode(retail_seed_dir: Path, tmp_path: Path) -> None:
    """Harness report mode follows RETAIL_TICKET_SEARCH_MODE when unset legacy hybrid flag."""
    os.environ.pop("RETAIL_TICKET_SEARCH_MODE", None)
    os.environ["RETAIL_TICKET_HYBRID_SEARCH"] = "0"
    report = run_eval(
        tickets_csv=retail_seed_dir / "service_queries.csv",
        eval_jsonl=retail_seed_dir / "ticket_retrieval.jsonl",
    )
    assert report["mode"] == "vector_only"
    assert report["total"] >= 1
    out = tmp_path / "baseline.json"
    write_report(out, report)
    assert out.is_file()
