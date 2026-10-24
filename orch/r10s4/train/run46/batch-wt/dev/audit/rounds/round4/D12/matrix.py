"""D12-H1 -- the generalization matrix.

METRIC (one line): the number of enumerated plant cells for which driving
setup + one real coordinator cycle + every platform's ``async_setup_entry``
raises, or publishes no plan without a named refusal.

RUN (from the repository root):

    PYTHONPATH=tests/hastub:tools/audit/round4/D12 \
      /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D12/matrix.py

EXPECTED at the baseline: cells_enumerated=108 (derived, see cells.py),
cells_failing=0, tolerance exact (every number is a count).  This harness is a
NON-FINDING: the crash / no-plan bar is clean at this baseline.  The D12
finding rests on units.py, whose bar this one does not measure.
BASELINE: 7dd68dd327fe3dbfb09f3bd0fe38910c58877697
MACHINE: MacBookAir10,1 (8-core Apple M1, 8 GB), macOS 25.6.0
INSTRUMENTED SYMBOL: heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator
  (._update_current_state, .async_run_optimization, ._build_data_dict) plus
  every platform's async_setup_entry.
PERTURBATION: --shrink drops one sensor / DHW / wood / PV / one zone from the
  fully mapped plant; cells_failing must move.
NULL CONTROL: the NULL_fully_mapped cell, printed separately.
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict

import d12lib
import cells as cellmod


def main(argv):
    dump = "--dump" in argv
    only = None
    for arg in argv:
        if arg.startswith("--group="):
            only = arg.split("=", 1)[1]

    matrix = cellmod.enumerate_cells()
    if only:
        matrix = [c for c in matrix if c[0] == only]

    results = []
    failing = []
    by_group = defaultdict(lambda: [0, 0])
    for group, name, cfg, states in matrix:
        r = d12lib.drive_cell(name, cfg, states)
        r["group"] = group
        results.append(r)
        by_group[group][0] += 1
        if not r["ok"]:
            by_group[group][1] += 1
            failing.append(r)

    print(f"RESULT cells_enumerated={len(matrix)} count")
    print(f"RESULT cells_failing={len(failing)} count")
    for group in sorted(by_group):
        total, bad = by_group[group]
        print(f"RESULT group_{group}_cells={total} count")
        print(f"RESULT group_{group}_failing={bad} count")
    steps = Counter(r["first_failing_step"] for r in failing)
    for step, n in sorted(steps.items()):
        print(f"RESULT first_failing_step_{step}={n} count")
    null = [r for r in results if r["group"] == "NULL"]
    if null:
        print(f"RESULT null_control_fully_mapped_ok={int(null[0]['ok'])} count")
        print(f"RESULT null_control_plan_steps={null[0]['plan_steps']} count")

    print()
    for r in failing:
        print(f"FAIL {r['group']:9s} {r['cell']}")
        print(f"     step={r['first_failing_step']}  {r['detail']}")
    if dump:
        print()
        for r in failing:
            print("=" * 70)
            print(r["cell"])
            print(r.get("traceback", ""))

    print()
    print(f"RESULT thread_factor=1.0")
    print(f"RESULT load1={d12lib.load1()}")
    print(f"RESULT swapins={d12lib.swapins()}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
