#!/usr/bin/env python3
# Metric: how many DHW steps optimize() reports in manual_released_dhw, and how many channel solves it runs, for a
#   cold-winter house with a low tank (tests/manual_plan.py _build_optimizer winter_typical/winter_cold, dhw 40 C)
#   whose DHW pins force two blocks off: steps 0-47 (breaching: the tank minimum) and 88-95 (not breaching); rest free.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g26/probes/probe_1721e50b7537a426.py
# EXPECTED RESULT released_dhw_baseline=48 count  (only the breaching block 0-47, released in round 1)
# EXPECTED RESULT released_dhw_mutant=56 count  (no per-round DHW write: the repair rounds run out and the out-of-rounds
#   branch abandons every forced-off DHW pin, the non-breaching 88-95 block included)
# EXPECTED RESULT solves_baseline=2 count, solves_mutant=5 count; tolerance exact
# EXPECTED RESULT null_released_delta=0 count  (null: summer house, tank 54 C, DHW pins off at 88-95 only: nothing breaches)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g26 cloud (4 vCPU Intel Xeon @ 2.30GHz, 16 GB), venv-ci CPython; run while a GATE_JOBS=1 gate ran (counts exact, no timing reported).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer.optimize line 4532
#   `                if dhw_pins is not None:` (the per-round write that frees each released DHW step).
# Perturbation: `if dhw_pins is not None:` -> `if False:` applied in memory (optimize recompiled from its own source,
#   patched onto the class for the mutant arm only). Direction: released 48 -> 56, solves 2 -> 5.
# Inputs tried: DHW pins all 0 (released 88 -> 96, solves 2 -> 5); the two-block plan above (48 -> 56); the null.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import g26_common as g  # noqa: E402  (thread pin first)
import numpy as np  # noqa: E402
from unittest import mock  # noqa: E402
mp = g.manual_plan_module()
from heatpump_optimizer import optimizer as O  # noqa: E402
H = O.HeatPumpOptimizer
MUT = g.mutant(H, "optimize", "if dhw_pins is not None:", "if False:")


def arm(bundle, pins, mutated):
    with mock.patch.object(H, "optimize", MUT if mutated else H.optimize):
        c = g.SolveCounter(bundle[0])
        r = mp._solve(bundle, dhw_pins=pins.copy())
        return len(r.manual_released_dhw), c.n


lt = mp._build_optimizer("winter_typical", "winter_cold", dhw_temperature=40.0)
dp = np.full(mp.N, np.nan); dp[0:48] = 0.0; dp[88:96] = 0.0
b, bn = arm(lt, dp, False)
m, mn = arm(lt, dp, True)
z0, _ = arm(lt, np.zeros(mp.N), False)
z1, _ = arm(lt, np.zeros(mp.N), True)
s = mp._build_optimizer("summer_typical", "summer_warm", dhw_temperature=54.0)
nd = np.full(mp.N, np.nan); nd[88:96] = 0.0
nb, _ = arm(s, nd, False)
nm, _ = arm(s, nd, True)
print(f"RESULT released_dhw_baseline={b} count")
print(f"RESULT released_dhw_mutant={m} count")
print(f"RESULT solves_baseline={bn} count")
print(f"RESULT solves_mutant={mn} count")
print(f"RESULT allzero_released_baseline={z0} count")
print(f"RESULT allzero_released_mutant={z1} count")
print(f"RESULT null_released_delta={abs(nm - nb)} count")
g.trailer()
