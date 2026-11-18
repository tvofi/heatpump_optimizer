#!/usr/bin/env python3
"""Run the duty-switch section of ``tests/features.py`` alone, in seconds.

WHY IT EXISTS. ``tests/features.py`` has no section filter, and a mutation
proof over the duty-switch learner (R10-DUTY-SWITCH-RESTART-LEARNING) runs
it once per mutant. This cuts the section out of the script at its two
markers, gives it the names the script had bound by then, and runs it, so
one mutant costs the section and not the suite. It executes the tree's own
text: a check edited in ``tests/features.py`` is the check run here.

It refuses (exit 2) when a marker is missing or the section holds no check,
so a moved marker cannot read as a pass.

    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_duty_switch_section.py
"""
from __future__ import annotations

import sys
from pathlib import Path

def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
START = "from heatpump_optimizer import duty_switch as _ds_mod"
END = "# --- R10-CEILING-PROBE (#2498, #2808)"
PRELUDE = """
import json, asyncio as _asyncio
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from harness import FakeHass, FakeState, Results, UTC
from homeassistant.util import dt as _sa_dt
from heatpump_optimizer import boost as _sa_boost
from heatpump_optimizer import pump_arbiter as _sa_pa
from heatpump_optimizer import store as _sa_store
R = Results("duty-switch section of tests/features.py")
"""


def main() -> int:
    text = (ROOT / "tests" / "features.py").read_text()
    if text.count(START) != 1 or text.count(END) != 1:
        print("REFUSED: a section marker is missing or repeated in tests/features.py")
        return 2
    section = text[text.index(START):text.index(END)]
    sys.path[:0] = [str(ROOT / "tests"), str(ROOT / "custom_components")]
    scope: dict = {"__name__": "duty_switch_section"}
    exec(compile(PRELUDE + section, "tests/features.py[duty-switch]", "exec"), scope)
    results = scope["R"]
    if not results.checks:
        print("REFUSED: the section ran no check")
        return 2
    return results.close("DUTY-SWITCH SECTION CHECKS")


if __name__ == "__main__":
    import os
    os.chdir(ROOT)
    sys.exit(main())
