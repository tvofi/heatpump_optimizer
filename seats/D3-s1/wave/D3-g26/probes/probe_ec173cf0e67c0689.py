#!/usr/bin/env python3
# Metric: channel solves optimize() runs (calls of _optimize_with_dhw/_optimize_space_only on the instance) for a
#   pinned horizon whose pins need NO safety release: the summer house of tests/manual_plan.py (summer_typical /
#   summer_warm, room 23 C, tank 54 C) with every space step forced off. Also the released count and the plan's
#   total space power (the plan itself must not move).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g26/probes/probe_ec173cf0e67c0689.py
# EXPECTED RESULT solves_baseline=1 count  (round 1 finds nothing to release and breaks)
# EXPECTED RESULT solves_mutant=4 count  (no break: all 3 repair rounds re-solve the identical pins)
# EXPECTED RESULT released_delta=0 count, power_delta_kw=0.0 (same plan, 3 wasted solves); tolerance exact
# EXPECTED RESULT null_solves_delta=0 count  (null: no pins at all -- the release loop is not entered)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g26 cloud (4 vCPU Intel Xeon @ 2.30GHz, 16 GB), venv-ci CPython; run while a GATE_JOBS=1 gate ran (counts exact, no timing reported).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer.optimize line 4518
#   `                if not rel_s and not rel_d:` (the early exit of the pin safety-repair loop).
# Perturbation: `if not rel_s and not rel_d:` -> `if False:` applied in memory. Direction: solves 1 -> 4 (x4 solve CPU
#   on every pinned replan that needs no release), the plan unchanged.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import g26_common as g  # noqa: E402  (thread pin first)
import numpy as np  # noqa: E402
from unittest import mock  # noqa: E402
mp = g.manual_plan_module()
from heatpump_optimizer import optimizer as O  # noqa: E402
H = O.HeatPumpOptimizer
MUT = g.mutant(H, "optimize", "if not rel_s and not rel_d:", "if False:")


def arm(bundle, mutated, **kw):
    with mock.patch.object(H, "optimize", MUT if mutated else H.optimize):
        c = g.SolveCounter(bundle[0])
        r = mp._solve(bundle, **kw)
        return c.n, len(r.manual_released_space), float(np.sum(r.power_schedule))


s = mp._build_optimizer("summer_typical", "summer_warm", room_temperature=23.0, dhw_temperature=54.0)
bn, br, bp = arm(s, False, space_pins=np.zeros(mp.N))
mn, mr, mpw = arm(s, True, space_pins=np.zeros(mp.N))
n0, _, _ = arm(s, False)
n1, _, _ = arm(s, True)
print(f"RESULT solves_baseline={bn} count")
print(f"RESULT solves_mutant={mn} count")
print(f"RESULT released_delta={abs(mr - br)} count")
print(f"RESULT power_delta_kw={abs(mpw - bp):.6f}")
print(f"RESULT null_solves_delta={abs(n1 - n0)} count")
g.trailer()
