#!/usr/bin/env python3
# Metric: _apply_pins_to_bounds(bounds, pins, min_on) over a grid of 4 bounds x pin vectors of length 0..6 (each
#   mixing 1.0 / 0.0 / NaN): the number of grid cells whose outcome (the bounds returned, or the exception type)
#   differs between baseline and mutant; plus REACH -- the distinct (len(bounds), len(pins)) pairs production hands
#   the function over 4 real coordinator refresh cycles, manual plan on and off (g26_common.coordinator_cycle_reach).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g26/probes/probe_c2896572788698c0.py
# EXPECTED RESULT cells_moved=4 count  (every pins-shorter-than-bounds cell, len 0..3 over 4 bounds: IndexError
#   in the mutant; equal and longer pins (len 4..6) iterate the same steps either way)
# EXPECTED RESULT reach_pairs=[(96, 96), (96, None)]  (pins are _normalise_pins'd to the horizon before they get here)
# EXPECTED RESULT reach_distinguishing_calls=0 count; null_cells_moved=0 count (the identity mutant); tolerance exact
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g26 cloud (4 vCPU Intel Xeon @ 2.30GHz, 16 GB), venv-ci CPython; run while a GATE_JOBS=1 gate ran (counts exact, no timing reported).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:_apply_pins_to_bounds line 2412
#   `    for i in range(min(len(out), len(pins))):`.
# Perturbation: -> `    for i in range((len(out))):` applied in memory (the function recompiled from its own source,
#   patched onto the module).
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import g26_common as g  # noqa: E402  (thread pin first)
import numpy as np  # noqa: E402
from heatpump_optimizer import optimizer as O  # noqa: E402
OLD = "for i in range(min(len(out), len(pins))):"
MUT = g.mutant(O, "_apply_pins_to_bounds", OLD, "for i in range((len(out))):")
IDENT = g.mutant(O, "_apply_pins_to_bounds", OLD, OLD)
BASE = O._apply_pins_to_bounds
BOUNDS = [(0.0, 3.0), (0.0, 2.0), (0.0, 0.0), (0.0, 3.0)]
CYCLE = [1.0, 0.0, float("nan"), 1.0, 0.0, float("nan")]


def outcome(fn, pins):
    try:
        return ("ok", tuple(fn(list(BOUNDS), pins, 0.8)))
    except Exception as err:  # noqa: BLE001 -- the exception type is the outcome
        return ("raise", type(err).__name__)


moved, null_moved, names = 0, 0, []
for n in range(0, 7):
    pins = np.array(CYCLE[:n], dtype=float)
    b, m, i = outcome(BASE, pins), outcome(MUT, pins), outcome(IDENT, pins)
    if repr(b) != repr(m):
        moved += 1
        names.append(f"len{n}:{m[1] if m[0] == 'raise' else 'bounds'}")
    null_moved += int(repr(b) != repr(i))
seen = []


def spy(b, p, m):
    seen.append((len(b), None if p is None else len(p)))
    return BASE(b, p, m)


solves = g.coordinator_cycle_reach([(O, "_apply_pins_to_bounds", spy)])
print(f"RESULT grid_cells=7 count")
print(f"RESULT cells_moved={moved} count  {names}")
print(f"RESULT null_cells_moved={null_moved} count")
print(f"RESULT reach_solves={solves} count")
print(f"RESULT reach_pairs={sorted(set(seen), key=str)}")
print(f"RESULT reach_distinguishing_calls={sum(1 for a, p in seen if p is not None and p < a)} count")
g.trailer()
