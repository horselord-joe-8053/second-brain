"""Product scripts must run on CPython 3.12, not Apple's python3.

The keyword library bm25x publishes wheels for 3.12 only. Shell and shebangs
under scripts/ and the retail prep tree call scripts/py, which execs python3.12.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCAN_ROOTS = (REPO / "scripts", REPO / "cursor_gen" / "retail_v11_prep")
# "python3" as a command, but not the 3.12 binary name.
BARE_PYTHON3 = re.compile(r"(?<![\w.])python3(?![\w.])")


def test_interpreter_is_312() -> None:
    assert sys.version_info[:2] >= (3, 12), sys.version


def test_product_scripts_do_not_call_bare_python3() -> None:
    offenders: list[str] = []
    wrapper = REPO / "scripts" / "py"
    for root in SCAN_ROOTS:
        for path in root.rglob("*"):
            if not path.is_file() or path.resolve() == wrapper.resolve():
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            if path.suffix == ".py":
                lines = text.splitlines()[:1]
            elif path.suffix == ".sh":
                lines = [
                    line
                    for line in text.splitlines()
                    if line.strip() and not line.lstrip().startswith("#")
                ]
            else:
                continue
            for line in lines:
                if BARE_PYTHON3.search(line):
                    offenders.append(f"{path.relative_to(REPO)}: {line.strip()}")
    assert offenders == [], "bare python3 still invoked:\n" + "\n".join(offenders)
