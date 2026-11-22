#!/usr/bin/env python3
# Metric: OptimizationConfig.baseline_load_array(n_steps) on each input of a grid (baseline_load_kw None, [], a
#   list and an ndarray of length n-1, n and n+1, n_steps 96 and 0): the number of grid cells whose outcome (the
#   returned values, or the exception type) differs between baseline and mutant; plus REACH -- the distinct
#   (len(baseline_load_kw), n_steps) pairs production hands the method over 4 real coordinator refresh cycles
#   (g26_common.coordinator_cycle_reach: house power entity absent/present x manual plan off/on).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g26/probes/probe_65b62179a34d3443.py
# EXPECTED RESULT cells_moved=1 count (empty list at n=96: zeros(96) -> IndexError from values[-1]; at n=0 both return an empty array); reach_distinguishing_calls=0 (production never stores an empty profile)
# EXPECTED RESULT reach_pairs=[(96, 96)]  (production always hands exactly n_steps values: coordinator._baseline_house_load(n_steps))
# EXPECTED RESULT null_cells_moved=0 count  (null: the identity mutant -- the same method recompiled unchanged); tolerance exact
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g26 cloud (4 vCPU Intel Xeon @ 2.30GHz, 16 GB), venv-ci CPython; run while a GATE_JOBS=1 gate ran (counts exact, no timing reported).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:OptimizationConfig.baseline_load_array line 2823 `if values.size == 0:`.
# Perturbation: `if values.size == 0:` -> `if False:` applied in memory (the method recompiled from its own source, patched onto the class).
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import g26_common as g  # noqa: E402  (thread pin first)
import numpy as np  # noqa: E402
from unittest import mock  # noqa: E402
from heatpump_optimizer import optimizer as O  # noqa: E402
C = O.OptimizationConfig
MUT = g.mutant(C, "baseline_load_array", "if values.size == 0:", "if False:")
IDENT = g.mutant(C, "baseline_load_array", "if values.size == 0:", "if values.size == 0:")
GRID = [("none", None, 96), ("empty", [], 96), ("empty_n0", [], 0)]
for n in (96, 0):
    for size in sorted({max(n - 1, 0), n, n + 1}):
        GRID.append((f"list{size}_n{n}", [0.5 + 0.01 * i for i in range(size)], n))
        GRID.append((f"arr{size}_n{n}", np.linspace(0.3, 1.2, size), n))


def outcome(fn, v, n):
    try:
        out = fn(C(baseline_load_kw=v), n)
        return ("ok", tuple(np.round(np.asarray(out, dtype=float), 12)), str(np.asarray(out).dtype))
    except Exception as err:  # noqa: BLE001 -- the exception type is the outcome
        return ("raise", type(err).__name__)


base_fn = C.baseline_load_array
moved, null_moved, moved_names = 0, 0, []
for name, v, n in GRID:
    b, m, i = outcome(base_fn, v, n), outcome(MUT, v, n), outcome(IDENT, v, n)
    if b != m:
        moved += 1
        moved_names.append(f"{name}:{b[0] if b[0] == 'raise' else 'values'}->{m[1] if m[0] == 'raise' else 'values'}")
    null_moved += int(b != i)
seen = []


def spy(self, n):
    v = self.baseline_load_kw
    seen.append((None if v is None else int(np.asarray(v).size), n))
    return base_fn(self, n)


solves = g.coordinator_cycle_reach([(C, "baseline_load_array", spy)])
print(f"RESULT grid_cells={len(GRID)} count")
print(f"RESULT cells_moved={moved} count  {moved_names}")
print(f"RESULT null_cells_moved={null_moved} count")
print(f"RESULT reach_solves={solves} count")
print(f"RESULT reach_pairs={sorted(set(seen), key=str)}")
print(f"RESULT reach_distinguishing_calls={sum(1 for s, n in seen if s is not None and s != n)} count")
g.trailer()
