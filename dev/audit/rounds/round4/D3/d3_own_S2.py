#!/usr/bin/env python3
"""Verifiers' own harness for D3-S2 (verifier seat 1 of panel D3-0, round 4).

FINDING: legionella.py:521 `if not params.dhw_legionella_enabled:` (the head
of LegionellaGuard.due_in_hours) turned into `if False:` — with the feature
DISABLED the method then returns a countdown number instead of None, and that
number is what coordinator.py:6426 publishes as dhw_legionella_due_in_hours.
The suite's legionella assertions (features.py :20197/:20250, the _lg_coord
fixtures) all run with the feature ENABLED; the one disabled fixture
(_lg_off, features.py:20233) only checks check_mode_block, which has its own
enabled guard.

METRIC: (a) direct probe — LegionellaGuard.due_in_hours on a minimal
SimpleNamespace self (feature disabled, last cycle 20 d ago, interval 7 d),
base arm vs mutant arm; (b) kill rule — first of tests/features.py and
tests/entities.py (the scripts that grep for due_in_hours /
dhw_legionella_due_in_hours) whose exit status or FAILED count rises against
a passing baseline arm on the same tree.

RUN (from this worktree's root; mutates ONLY ../audit-r4-verify-D3-1-scratch):
    PYTHONPATH=tests/hastub python3 tools/audit/round4/D3/d3_own_S2.py

EXPECTED: base probe None, mutant probe about -312.0 h; killed_by=none.
BASELINE: measured against worktree HEAD 0855277 (finder used 7dd68dd)
MACHINE: 8-core Apple M1, macOS 25.6.0, python 3.11
"""
from __future__ import annotations

import sys

sys.path.insert(0, "tools/audit/round4/D3")
from d3_own_common import (arms, heavy_neighbours, load1, swapins,
                           thread_factor)

REL = "custom_components/heatpump_optimizer/legionella.py"
LINE, OLD, NEW = 521, "if not params.dhw_legionella_enabled:", "if False:"

PROBE = r"""
import json
from datetime import timedelta
from homeassistant.util import dt as dt_util
from custom_components.heatpump_optimizer.legionella import LegionellaGuard

# A real instance's methods without running __init__ (no hass/store needed):
# the mutant arm must survive past the guard into hours_since().
obj = LegionellaGuard.__new__(LegionellaGuard)
obj._params = type("P", (), {
    "dhw_legionella_enabled": False,
    "dhw_legionella_interval_days": 7.0,
})()
obj.last_cycle = dt_util.now() - timedelta(days=20.0)
obj.attempt = None
val = obj.due_in_hours()
print(json.dumps({"disabled_due_in_hours": None if val is None else float(val)}))
"""


def main() -> int:
    print(f"D3-S2 own harness — mutant {REL}:{LINE} {OLD!r} -> {NEW!r}")
    print(f"heavy neighbours (stress.py/run.sh procs): {heavy_neighbours()}")
    out = arms(
        REL, LINE, OLD, NEW,
        scripts=["tests/features.py", "tests/entities.py"],
        finding="S2",
        probes={"code": PROBE},
    )
    b = out["probes"]["base"]["value"] or {"disabled_due_in_hours": "PROBE_FAILED"}
    m = out["probes"]["mut"]["value"] or {"disabled_due_in_hours": "PROBE_FAILED"}
    for script, rec in out["scripts"].items():
        base, mut = rec["base"], rec["mut"]
        if mut is None:
            print(f"RESULT S2_{script.replace('/', '_')}_verdict=void")
            continue
        print(f"RESULT S2_{script.replace('/', '_')}_rc={base['rc']}->{mut['rc']} delta_rc")
        print(f"RESULT S2_{script.replace('/', '_')}_failed={base['failed']}->{mut['failed']} count")
    print(f"RESULT S2_disabled_due_base={b['disabled_due_in_hours']} hours_or_null")
    print(f"RESULT S2_disabled_due_mut={m['disabled_due_in_hours']} hours_or_null")
    print(f"RESULT S2_behaviour_changed={b['disabled_due_in_hours'] != m['disabled_due_in_hours']} bool")
    print(f"RESULT S2_killed_by={out['killed_by'] or 'none'} script")
    print(f"RESULT thread_factor={thread_factor()}")
    print(f"RESULT load1={load1():.2f}")
    print(f"RESULT swapins={swapins()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
