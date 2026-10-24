#!/usr/bin/env python3
"""Verifiers' own harness for D3-S1 (verifier seat 1 of panel D3-0, round 4).

FINDING: grid_fee.py:106 `if start <= end:` (parse_month_range) turned into
`if False:` — a NON-wrapping month range like Mar-Sep then falls through to
the wrapping branch and covers all 12 months (year-round fee), while the
suite's only month-range value assertion uses the WRAPPING case (Nov-Mar).

METRIC: (a) direct probe — sorted month sets returned by
custom_components.heatpump_optimizer.grid_fee.parse_month_range for
"Mar-Sep"/"Nov-Mar"/"Jul", base arm vs mutant arm; (b) kill rule — the first
of the named test scripts (tests/features.py, tests/entities.py,
tests/config_flow_steps.py — everything under tests/*.py that greps for the
symbol or its spec grammar, minus stress.py/run.sh/card lanes) whose exit
status or `N of M ... FAILED` count rises against a PASSING baseline arm run
by this harness on the same tree.

RUN (from this worktree's root; mutates ONLY ../audit-r4-verify-D3-1-scratch):
    PYTHONPATH=tests/hastub python3 tools/audit/round4/D3/d3_own_S1.py

EXPECTED: mutant arm of the probe returns 12 months for "Mar-Sep"
(base returns 7); killed_by=none (no named script notices the mutant).
BASELINE: measured against worktree HEAD 0855277 (branch head; finder used 7dd68dd)
MACHINE: 8-core Apple M1, macOS 25.6.0, python 3.11
"""
from __future__ import annotations

import sys

sys.path.insert(0, "tools/audit/round4/D3")
from d3_own_common import (arms, heavy_neighbours, load1, swapins,
                           thread_factor)

REL = "custom_components/heatpump_optimizer/grid_fee.py"
LINE, OLD, NEW = 106, "if start <= end:", "if False:"

PROBE = r"""
import json
from custom_components.heatpump_optimizer import grid_fee as gf
print(json.dumps({
    "Mar-Sep": sorted(gf.parse_month_range("Mar-Sep")),
    "Nov-Mar": sorted(gf.parse_month_range("Nov-Mar")),
    "Jul":     sorted(gf.parse_month_range("Jul")),
}))
"""


def main() -> int:
    print(f"D3-S1 own harness — mutant {REL}:{LINE} {OLD!r} -> {NEW!r}")
    print(f"heavy neighbours (stress.py/run.sh procs): {heavy_neighbours()}")
    out = arms(
        REL, LINE, OLD, NEW,
        scripts=["tests/features.py", "tests/entities.py",
                 "tests/config_flow_steps.py"],
        finding="S1",
        probes={"code": PROBE},
    )
    b = out["probes"]["base"]["value"]
    m = out["probes"]["mut"]["value"]
    n_mar_sep_base = len(b["Mar-Sep"])
    n_mar_sep_mut = len(m["Mar-Sep"])
    for script, rec in out["scripts"].items():
        base, mut = rec["base"], rec["mut"]
        if mut is None:
            print(f"RESULT S1_{script.replace('/', '_')}_verdict=void")
            continue
        print(f"RESULT S1_{script.replace('/', '_')}_rc={base['rc']}->{mut['rc']} delta_rc")
        print(f"RESULT S1_{script.replace('/', '_')}_failed={base['failed']}->{mut['failed']} count")
    print(f"RESULT S1_mar_sep_months_base={n_mar_sep_base} months")
    print(f"RESULT S1_mar_sep_months_mut={n_mar_sep_mut} months")
    print(f"RESULT S1_nov_mar_unchanged={b['Nov-Mar'] == m['Nov-Mar']} bool")
    print(f"RESULT S1_killed_by={out['killed_by'] or 'none'} script")
    print(f"RESULT thread_factor={thread_factor()}")
    print(f"RESULT load1={load1():.2f}")
    print(f"RESULT swapins={swapins()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
