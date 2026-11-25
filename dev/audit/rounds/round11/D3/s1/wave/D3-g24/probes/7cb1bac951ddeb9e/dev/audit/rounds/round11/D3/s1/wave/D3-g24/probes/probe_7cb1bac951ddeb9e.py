#!/usr/bin/env python3
# Metric: number of (row_cost variant x end-temperature row) cases on which the batch terminal cost
#   HeatPumpOptimizer._terminal_cost_batch(row_cost, term_spec)(traj) returns a different value BIT FOR BIT
#   (struct-packed float64, so -0.0 vs +0.0 and NaN payloads count) under the mutant, plus the number of
#   cases where the batch twin's value differs bitwise from the scalar closure's max(0.0, cap - end) terms
#   (the parity the method's docstring promises). Count key: the closure's returned array.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g24/probes/probe_7cb1bac951ddeb9e.py
# Expected: see EXPECTED below (exact counts, tolerance 0).
# EXPECTED RESULT null_cases_moved=0 count
# EXPECTED RESULT null_parity_breaks=0 count
# EXPECTED RESULT null_cases_tried=81 count
# EXPECTED RESULT mutant_cases_moved=0 count
# EXPECTED RESULT mutant_parity_breaks=0 count
# EXPECTED RESULT mutant_cases_tried=81 count
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g24 (4 vCPU Intel Xeon @ 2.10GHz, Linux,
#   CPython 3.14 venv-ci).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._terminal_cost_batch
#   (inner cost_batch, optimizer.py:3772, CMP_BOUND), fed the production row_cost/term_spec built by
#   optimizer:_terminal_row_cost.
# Perturbation: mutant 7cb1bac951ddeb9e, optimizer.py:3772
#   '(d := cap - traj[name][:, -1]) > 0.0, d, 0.0' -> '(d := cap - traj[name][:, -1]) >= 0.0, d, 0.0',
#   applied in memory (the static method recompiled from its own source); direction: cases_moved 0 -> >0.
# Null control: the baseline method against itself (null_cases_moved must be 0).
# Inputs tried: end == cap (d = +0.0), cap = -0.0 with end = +0.0 (d = -0.0), end one ulp above/below cap,
#   end NaN, end +/-inf, end far below/above cap; coef positive, negative and zero (mass*survival);
#   row_cost with cop_buffer == cop_end, != cop_end, and with a refill derate.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _mutlib  # noqa: E402
import numpy as np  # noqa: E402
from custom_components.heatpump_optimizer import optimizer  # noqa: E402
from custom_components.heatpump_optimizer.optimizer import HeatPumpOptimizer, _terminal_row_cost  # noqa: E402

OLD = "(d := cap - traj[name][:, -1]) > 0.0, d, 0.0"
NEW = "(d := cap - traj[name][:, -1]) >= 0.0, d, 0.0"
bits = lambda x: struct.pack("<d", float(x))

ENDS = [("end==cap", 21.0, 21.0), ("cap=-0,end=+0", -0.0, 0.0), ("end=cap+ulp", 21.0, np.nextafter(21.0, 99)),
        ("end=cap-ulp", 21.0, np.nextafter(21.0, -99)), ("end=nan", 21.0, np.nan), ("end=+inf", 21.0, np.inf),
        ("end=-inf", 21.0, -np.inf), ("end_far_below", 21.0, 15.0), ("end_far_above", 21.0, 30.0)]
COEFS = [("mass+", 2.0, 1.0), ("mass-", -2.0, 1.0), ("surv0", 2.0, 0.0)]
ROWS = [("same_cop", 3.0, 3.0, None), ("split_cop", 3.0, 2.5, None), ("refill", 3.0, 2.5, lambda e: 1.1 * e)]


def run(fn, label):
    moved = parity = n = 0
    for rname, cop_end, cop_buf, refill in ROWS:
        for cname, mass, surv in COEFS:
            for ename, cap, end in ENDS:
                stores = ((mass, "room", cap, surv), (1.0, "buffer", 45.0, 1.0))
                row_cost, spec = _terminal_row_cost(0.3, cop_end, cop_buf, stores, refill)
                traj = {"room": np.array([[20.0, end]]), "buffer": np.array([[45.0, 44.0]])}
                vb = HeatPumpOptimizer._terminal_cost_batch(row_cost, spec)(traj)[0]
                vm = fn(row_cost, spec)(traj)[0]
                scalar = row_cost([c * max(0.0, cp - (end if nm == "room" else 44.0)) for c, nm, cp in spec])
                d = int(bits(vb) != bits(vm))
                p = int(bits(vm) != bits(scalar))
                moved += d
                parity += p
                n += 1
                if d or p:
                    print(f"CASE {rname}/{cname}/{ename}: baseline={vb!r} mutant={vm!r} scalar={scalar!r} moved={d} parity_break={p}")
    print(f"RESULT {label}_cases_moved={moved} count")
    print(f"RESULT {label}_parity_breaks={parity} count")
    print(f"RESULT {label}_cases_tried={n} count")


raw = HeatPumpOptimizer.__dict__["_terminal_cost_batch"]
run(raw.__func__ if isinstance(raw, staticmethod) else raw, "null")
mut = _mutlib.mutated(HeatPumpOptimizer, "_terminal_cost_batch", OLD, NEW, optimizer)
run(mut.__func__ if isinstance(mut, staticmethod) else mut, "mutant")
_mutlib.footer()
