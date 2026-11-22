#!/usr/bin/env python3
# Metric: how many space steps optimize() reports in manual_released_space, and how many channel solves it runs,
#   for a cold-winter house (tests/manual_plan.py _build_optimizer winter_typical/winter_cold) whose space pins force
#   two blocks off: steps 0-23 (not breaching) and 80-83 (breaching); every other step free (NaN).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g26/probes/probe_f56e3474baa75dc5.py
# EXPECTED RESULT released_space_baseline=4 count  (only the breaching block 80-83 is released, in round 1)
# EXPECTED RESULT released_space_mutant=28 count  (the per-round release never clears a pin, the 3 repair rounds run out,
#   and the out-of-rounds branch abandons EVERY forced-off space pin, the non-breaching 0-23 block included)
# EXPECTED RESULT solves_baseline=2 count, solves_mutant=5 count; tolerance exact
# EXPECTED RESULT null_released_delta=0 count  (null: no space pins forced off at a breach -- the summer house, zeros: nothing released in either arm)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g26 cloud (4 vCPU Intel Xeon @ 2.30GHz, 16 GB), venv-ci CPython; run while a GATE_JOBS=1 gate ran (counts exact, no timing reported).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer.optimize line 4528
#   `                if space_pins is not None:` (the per-round write that frees each released space step).
# Perturbation: `if space_pins is not None:` -> `if False:` applied in memory (optimize recompiled from its own source,
#   patched onto the class for the mutant arm only). Direction: released 4 -> 28, solves 2 -> 5.
# Inputs tried: S1 two off-blocks (moves); null summer_typical/summer_warm room 23 C, space pins all 0.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import g26_common as g  # noqa: E402  (thread pin first)
import numpy as np  # noqa: E402
from unittest import mock  # noqa: E402
mp = g.manual_plan_module()
from heatpump_optimizer import optimizer as O  # noqa: E402
H = O.HeatPumpOptimizer
MUT = g.mutant(H, "optimize", "if space_pins is not None:", "if False:")


def arm(bundle, pins, mutated):
    with mock.patch.object(H, "optimize", MUT if mutated else H.optimize):
        c = g.SolveCounter(bundle[0])
        r = mp._solve(bundle, space_pins=pins.copy())
        return len(r.manual_released_space), c.n


w = mp._build_optimizer("winter_typical", "winter_cold")
sp = np.full(mp.N, np.nan); sp[0:24] = 0.0; sp[80:84] = 0.0
b, bn = arm(w, sp, False)
m, mn = arm(w, sp, True)
s = mp._build_optimizer("summer_typical", "summer_warm", room_temperature=23.0, dhw_temperature=54.0)
nb, _ = arm(s, np.zeros(mp.N), False)
nm, _ = arm(s, np.zeros(mp.N), True)
print(f"RESULT released_space_baseline={b} count")
print(f"RESULT released_space_mutant={m} count")
print(f"RESULT solves_baseline={bn} count")
print(f"RESULT solves_mutant={mn} count")
print(f"RESULT null_released_delta={abs(nm - nb)} count")
g.trailer()
