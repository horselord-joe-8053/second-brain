"""Generation parameters per committed profile directory."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProfileGenSpec:
    """Counts and seed for one profile under ``sim_data/profiles/``."""

    dir_name: str
    historical_count: int
    eval_paraphrase: int
    eval_hybrid: int
    eval_code: int
    seed: int
    skip_regen: bool = False


PROFILE_SPECS: dict[str, ProfileGenSpec] = {
    "data_60_10": ProfileGenSpec(
        dir_name="data_60_10",
        historical_count=60,
        eval_paraphrase=5,
        eval_hybrid=3,
        eval_code=2,
        seed=20261012,
        skip_regen=True,
    ),
    "data_1000_100": ProfileGenSpec(
        dir_name="data_1000_100",
        historical_count=1000,
        eval_paraphrase=50,
        eval_hybrid=30,
        eval_code=20,
        seed=20261014,
    ),
}
