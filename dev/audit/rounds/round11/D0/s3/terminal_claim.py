"""D0.M7 terminal credit: does removing it make the plan breach the comfort
floor at the tail, as `HeatPumpOptimizer._terminal_cost`'s docstring claims?
Round 11 D0-s3, baseline 92d38ecb, box B3 (4 cores shared by three seats).

Metric (one line): per cell, tail_breach_delta = degree-steps below the
per-step comfort floor (`OptimizationConfig.get_temp_bounds`) over the last 2 h
(8 steps) of the shipped plan's own room trajectory
(`OptimizationResult.room_temp_trajectory`) with `_terminal_cost` replaced by a
zero closure pair, minus the same with the credit in; counted cells are those
with delta > 1e-3 K-step. Beside it: tail energy (kWh, last 2 h) with/without,
the docstring's other half ("dumps the last couple of hours").
Key: the room trajectory the production result delivers, never an input.

The full-universe count is decomp_oracle.py's (every d0-grid line,
RESULT terminal_tail_breach_cells); this harness re-runs the claim on a fixed
committed list (terminal_cells.txt: 5 cells per price profile drawn from the
cells where dropping the credit lowers tail energy by > 0.1 kWh) so the
perturbation can be run cheaply.

Command (from the export root):
  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D0/s3/terminal_claim.py [--perturb weak_floor]
Expected (unperturbed): tail_breach_worse_cells=0/40, tail_dump_cells=40/40.
Perturbation: --perturb weak_floor sets the optimizer's config.comfort_weight
to 1 % of its value (a config change; both arms): the floor penalty no longer
holds the tail, so tail_breach_worse_cells must move up from 0 -- the floor is
held by the comfort penalty, not by the terminal credit.
Arm --perturb learned_min: config.comfort_weight = comfort_learning.COMFORT_WEIGHT_MIN
(1.0, the lowest weight the comfort learner can reach): is the claim live
anywhere in the shipped weight range?
Machine: box B3. Counts are contention-immune; CPU is provisional.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import json
import time
import argparse
from datetime import timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402

TAIL = 8


def one(cell, perturb):
    import d0s3_lib as L
    from unittest import mock
    from golden import START
    from heatpump_optimizer.optimizer import HeatPumpOptimizer
    orig_tc = HeatPumpOptimizer._terminal_cost

    def zero_tc(self, *a, **k):
        orig_tc(self, *a, **k)
        return (lambda *x, **y: 0.0), (lambda traj: np.zeros(traj["room"].shape[0]))

    def run(credit):
        b = L.build(cell)
        opt = b["optimizer"]
        if perturb == "weak_floor":
            opt.config.comfort_weight = opt.config.comfort_weight * 0.01
        elif perturb == "learned_min":
            from heatpump_optimizer.comfort_learning import COMFORT_WEIGHT_MIN
            opt.config.comfort_weight = COMFORT_WEIGHT_MIN
        if credit:
            r = opt.optimize(inputs=L.inputs_of(b))
        else:
            with mock.patch.object(HeatPumpOptimizer, "_terminal_cost", zero_tc):
                r = opt.optimize(inputs=L.inputs_of(b))
        n = len(r.power_schedule)
        fl = np.array([opt.config.get_temp_bounds(((START + timedelta(hours=0.25 * (i + 1))).hour
                                                   + (START + timedelta(hours=0.25 * (i + 1))).minute / 60.0))[0]
                       for i in range(n)])
        room = np.asarray(r.room_temp_trajectory, dtype=float)[1:n + 1]
        return (float(np.maximum(0, fl[-TAIL:] - room[-TAIL:]).sum()),
                float(np.sum(np.asarray(r.power_schedule, dtype=float)[-TAIL:]) * 0.25), float(room[-1]))

    bc, kc, ec = run(True)
    bn, kn, en = run(False)
    return {"cell": cell, "breach_credit": bc, "breach_nocredit": bn, "tail_kwh_credit": kc,
            "tail_kwh_nocredit": kn, "end_room_credit": ec, "end_room_nocredit": en}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", default="")
    ap.add_argument("--cells", default=os.path.join(HERE, "terminal_cells.txt"))
    a = ap.parse_args()
    cells = [l.strip() for l in open(a.cells) if l.strip()]
    t0 = time.process_time(); tt0 = time.thread_time()
    R = []
    for c in cells:
        r = one(c, a.perturb)
        R.append(r)
        print(f"{c} breach {r['breach_credit']:.4f}->{r['breach_nocredit']:.4f} "
              f"tail_kwh {r['tail_kwh_credit']:.3f}->{r['tail_kwh_nocredit']:.3f}", flush=True)
    worse = [r for r in R if r["breach_nocredit"] > r["breach_credit"] + 1e-3]
    dump = [r for r in R if r["tail_kwh_nocredit"] < r["tail_kwh_credit"] - 1e-3]
    import d0s3_lib as L
    print(f"RESULT perturb={a.perturb or 'none'}")
    print(f"RESULT tail_breach_worse_cells={len(worse)}/{len(R)}")
    print(f"RESULT tail_dump_cells={len(dump)}/{len(R)}")
    print(f"RESULT max_tail_breach_nocredit={max(r['breach_nocredit'] for r in R):.4f} K-steps")
    print(f"RESULT max_tail_breach_credit={max(r['breach_credit'] for r in R):.4f} K-steps")
    pc = time.process_time() - t0; tc = time.thread_time() - tt0
    print(f"RESULT cpu_s={pc:.1f} provisional")
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={L.load1():.2f}")
    print(f"RESULT swapins={L.swapins()}")


if __name__ == "__main__":
    main()
