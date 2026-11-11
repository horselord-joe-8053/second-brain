"""D6 eval suite short ids (TYPE_*_*) and long human-readable names."""

from __future__ import annotations

# Type A — manual single-leg technical (90-Q judged harness).
TYPE_A_M90 = "TYPE_A_M90"
TYPE_A_M90_LONG = "M90-technical-singlefact"

# Type B — bundled manual + ticket compound technical (20-Q, minor M4).
TYPE_B_B20 = "TYPE_B_B20"
TYPE_B_B20_LONG = "B20-technical-compound"

# Type C — COS / insight orientation (20-Q, planned fixture).
TYPE_C_C20 = "TYPE_C_C20"
TYPE_C_C20_LONG = "C20-insight-orientation"

# Type W — cross-manual synthesis (20-Q). Same judge shape as Type C.
TYPE_W_W20 = "TYPE_W_W20"
TYPE_W_W20_LONG = "W20-focused-multi-section-synthesis"

SUITE_SHORT_TO_LONG: dict[str, str] = {
    TYPE_A_M90: TYPE_A_M90_LONG,
    TYPE_B_B20: TYPE_B_B20_LONG,
    TYPE_C_C20: TYPE_C_C20_LONG,
    TYPE_W_W20: TYPE_W_W20_LONG,
}

MANUAL_SUITE_DEFAULT_PATH = "tests/retail_multi_profiles/data/retail-manual-qa-test-suite.json"
BUNDLED_SUITE_DEFAULT_PATH = "tests/retail_multi_profiles/data/retail-bundled-qa-b20.json"
INSIGHT_SUITE_DEFAULT_PATH = "tests/retail_multi_profiles/data/retail-cos-insight-test-suite.json"
W20_SUITE_DEFAULT_PATH = "tests/retail_multi_profiles/data/retail-w20-focused-synthesis.json"
