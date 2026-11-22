#!/usr/bin/env python3
# Metric: how many space steps optimize() reports released when the pin safety repair runs out of rounds and abandons
#   the channel, for the cold-winter house of tests/manual_plan.py with space pins = 1.0 on steps 0-7 and 0.0 on 8-95.
#   The out-of-rounds path is reached exactly as tests/manual_plan.py:test_release_always_resolves reaches it: its
#   never_satisfied stub (re-typed here verbatim) replaces _safety_release_steps so every round asks one more release.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g26/probes/probe_2693e4fc04518cbf.py
# EXPECTED RESULT released_baseline=88 count  (only the 88 forced-off steps are abandoned)
# EXPECTED RESULT released_mutant=96 count  (and -> or: a forced-ON pin (1.0) now also satisfies the release test)
# EXPECTED RESULT null_released_delta=0 count  (null: pins all 0.0 -- every pin is off, both arms release 96)
# EXPECTED RESULT reach_on_pins=1 count  (the integration emits forced-on pins of 1.0)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g26 cloud (4 vCPU Intel Xeon @ 2.30GHz, 16 GB), venv-ci CPython; run while a GATE_JOBS=1 gate ran (counts exact, no timing reported).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer.optimize line 4560
#   `                            if not _pin_is_free(value) and value < 0.5:` (the out-of-rounds wholesale release).
# Perturbation: -> `if not _pin_is_free(value) or value < 0.5:` applied in memory. Direction: released 88 -> 96.
# Inputs tried: on-pins 1.0 (moves); pins all 0 as in manual_plan.py test_release_always_resolves (96 -> 96, no move); free NaN steps (never released in either arm).
import math
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import g26_common as g  # noqa: E402  (thread pin first)
import numpy as np  # noqa: E402
from unittest import mock  # noqa: E402
mp = g.manual_plan_module()
from heatpump_optimizer import optimizer as O  # noqa: E402
from heatpump_optimizer import manual_plan as MP  # noqa: E402
H = O.HeatPumpOptimizer
MUT = g.mutant(H, "optimize", "if not _pin_is_free(value) and value < 0.5:", "if not _pin_is_free(value) or value < 0.5:")


def never_satisfied(self, result, temp_min_bounds, space_pins, dhw_pins):
    if space_pins is None:
        return [], []
    free = [i for i in range(len(space_pins))
            if not math.isnan(float(space_pins[i])) and float(space_pins[i]) < 0.5]
    return (free[:1], [])


def arm(bundle, pins, mutated):
    with mock.patch.object(H, "optimize", MUT if mutated else H.optimize), \
            mock.patch.object(H, "_safety_release_steps", never_satisfied):
        r = mp._solve(bundle, space_pins=pins.copy())
        return len(r.manual_released_space)


w = mp._build_optimizer("winter_typical", "winter_cold")
sp = np.zeros(mp.N); sp[0:8] = 1.0
b = arm(w, sp, False)
m = arm(w, sp, True)
nb = arm(w, np.zeros(mp.N), False)
nm = arm(w, np.zeros(mp.N), True)
# reach: every pin value the integration's own path emits, over slot layouts (none, one, two, whole window,
# half-hour-aligned and 7-minute-offset slots) -- channel_pins on a build_override, then _normalise_pins
from datetime import timedelta  # noqa: E402
vals = set()
step_starts = [mp.START + timedelta(minutes=15 * i) for i in range(mp.N)]
for slots in ([], [(2, 3)], [(0, 1), (5, 8.5)], [(0, 6)], [(0.1167, 2.3)]):
    ov = MP.build_override(
        dhw_slots=[mp._slot(a, b) for a, b in slots], space_slots=[mp._slot(a, b) for a, b in slots],
        expires_at=mp.START + timedelta(hours=6), now=mp.START)
    for ch in (MP.CHANNEL_SPACE, MP.CHANNEL_DHW):
        arr = H._normalise_pins(ov.channel_pins(ch, step_starts), mp.N)
        vals |= {float(v) for v in arr if not math.isnan(float(v))}
print(f"RESULT released_baseline={b} count")
print(f"RESULT released_mutant={m} count")
print(f"RESULT null_released_delta={abs(nm - nb)} count")
print(f"RESULT reach_on_pins={int(1.0 in vals)} count  (pin values channel_pins can emit: {sorted(vals)})")
g.trailer()
