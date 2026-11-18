#!/usr/bin/env python3
"""Verifiers' own harness for D3-S4 (verifier seat 1 of panel D3-0, round 4).

FINDING (judged equivalent by the finder): optimizer.py:1549
`end = min(i + lookahead, n_steps)` in
HeatPumpOptimizer._anticipatory_weights, CLAMP_DROPped to
`end = (i + lookahead)`. Claim: Python/numpy slicing clamps the upper bound
itself, so `solar_gains[i:end]` / `heat_loss_factors[i:end]` are elementwise
identical and no value moves.

METRIC: (a) equivalence probe — max |weights_base - weights_mutant| over a
grid of shapes (n_steps in {1,2,3,5,24,96}, dt in {0.25,0.5,1.0,4.0,8.0,16.0},
seeded random solar/loss arrays; lookahead = int(8/dt) ranges 32..0, so
i+lookahead runs past n_steps in most cells), both arms importing the real
production class from the scratch tree; (b) kill rule — tests/features.py
(exercises the solve path that calls _anticipatory_weights at optimizer.py
:3357/:5397) against a passing baseline arm.

RUN (from this worktree's root; mutates ONLY ../audit-r4-verify-D3-1-scratch):
    PYTHONPATH=tests/hastub python3 tools/audit/round4/D3/d3_own_S4.py

EXPECTED: max abs diff 0.0; killed_by=none.
BASELINE: measured against worktree HEAD 0855277 (finder used 7dd68dd)
MACHINE: 8-core Apple M1, macOS 25.6.0, python 3.11
"""
from __future__ import annotations

import sys

sys.path.insert(0, "tools/audit/round4/D3")
from d3_own_common import (arms, heavy_neighbours, load1, swapins,
                           thread_factor)

REL = "custom_components/heatpump_optimizer/optimizer.py"
LINE, OLD, NEW = 1549, "end = min(i + lookahead, n_steps)", "end = (i + lookahead)"

PROBE = r"""
import json
import numpy as np
from custom_components.heatpump_optimizer.optimizer import HeatPumpOptimizer

rng = np.random.default_rng(20260912)
rows = []
for n_steps in (1, 2, 3, 5, 24, 96):
    for dt in (0.25, 0.5, 1.0, 4.0, 8.0, 16.0):
        solar = rng.random(n_steps) * 2.0
        loss = 1.0 + rng.random(n_steps)
        w = HeatPumpOptimizer._anticipatory_weights(
            None, n_steps, dt, solar, loss
        )
        rows.append([int(n_steps), float(dt), [float(x) for x in w]])
print(json.dumps({"rows": rows}))
"""


def _max_abs_diff(a, b) -> float:
    worst = 0.0
    for ra, rb in zip(a["rows"], b["rows"]):
        assert ra[0] == rb[0] and ra[1] == rb[1]
        for xa, xb in zip(ra[2], rb[2]):
            worst = max(worst, abs(xa - xb))
    return worst


def main() -> int:
    print(f"D3-S4 own harness — mutant {REL}:{LINE} {OLD!r} -> {NEW!r}")
    print(f"heavy neighbours (stress.py/run.sh procs): {heavy_neighbours()}")
    out = arms(
        REL, LINE, OLD, NEW,
        scripts=["tests/features.py"],
        finding="S4",
        probes={"code": PROBE},
    )
    diff = _max_abs_diff(out["probes"]["base"]["value"],
                         out["probes"]["mut"]["value"])
    for script, rec in out["scripts"].items():
        base, mut = rec["base"], rec["mut"]
        if mut is None:
            print(f"RESULT S4_{script.replace('/', '_')}_verdict=void")
            continue
        print(f"RESULT S4_{script.replace('/', '_')}_rc={base['rc']}->{mut['rc']} delta_rc")
        print(f"RESULT S4_{script.replace('/', '_')}_failed={base['failed']}->{mut['failed']} count")
    print(f"RESULT S4_weights_max_absdiff={diff:.6g} weight")
    print(f"RESULT S4_equivalent={diff == 0.0} bool")
    print(f"RESULT S4_killed_by={out['killed_by'] or 'none'} script")
    print(f"RESULT thread_factor={thread_factor()}")
    print(f"RESULT load1={load1():.2f}")
    print(f"RESULT swapins={swapins()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
