"""D9 round 4 / H9 -- the batched objective vectorizes the SIMULATION but
not the COST: a Python loop over the batch rows.

``optimizer.py:objective_batch`` (both the space-only and the with-DHW
twin) calls ``ThermalModel.simulate_trajectory_batch`` once for all B
perturbed schedules -- that is #97's win -- and then runs
``for b in range(B)``, calling ``HeatPumpOptimizer._comfort_terms``,
``energy_cost_of``, ``cycling``, ``capacity`` and ``terminal_cost`` once
per row on 96-element slices. B is the variable count + the base row, so
the loop runs ~97 times per gradient evaluation.

METRICS (all hooking production symbols):
  comfort_terms_calls_per_solve      count, FINAL
  comfort_terms_calls_per_gradient   count / njev, FINAL
  batch_rows_per_solve               count, FINAL
  comfort_terms_cpu_share_pct        accumulated ``time.perf_counter``
                                     inside ``_comfort_terms`` / solve wall
  simulate_batch_cpu_share_pct       the same for
                                     ``simulate_trajectory_batch``
  row_loop_share_pct                 (objective_batch total minus the
                                     batched simulation) / solve wall
  cpu_ratio_vs_reference             solve CPU / stress.reference_solve CPU

Shares are wall fractions of the SAME solve, so they are ratios and
survive contention; the absolute seconds are PROVISIONAL. A null control
at the flat price profile is measured for every number -- the loop is a
property of the batch shape, not of the prices, so the shares must NOT
move at flat prices, which is what distinguishes a structural cost from a
price-driven one.

COMMAND (from the repository root):

    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
      MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
      python3 tools/audit/round4/D9/h9_batch_cost_loop.py

EXPECTED (baseline 7dd68dd, 8-core Apple M1 / 8 GB, python 3.11):
  comfort_terms_calls_per_gradient 96 - 99 (+/- 1)
  comfort_terms_cpu_share_pct      15 - 35 (+/- 5 pp)
  row_loop_share_pct               25 - 55 (+/- 8 pp)

PERTURBATION: ``H9_HORIZON=12`` halves the horizon, so the batch has ~49
rows instead of ~97; ``comfort_terms_calls_per_gradient`` must fall to
about half. That is the direction proving the count is the batch width
and not a constant.

COUNTS ARE FINAL; shares are ratios; seconds are PROVISIONAL.
"""
from __future__ import annotations

import os

for _t in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_t, "1")

import sys  # noqa: E402
import time  # noqa: E402

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round4", "D9"))

import d9common as C  # noqa: E402

import numpy as np  # noqa: E402
from heatpump_optimizer import optimizer as OPT  # noqa: E402
from heatpump_optimizer import thermal_model as TM  # noqa: E402

HORIZON = int(os.environ.get("H9_HORIZON", "24"))

S = {}


def reset():
    S.clear()
    S.update({
        "ct_calls": 0, "ct_time": 0.0,
        "batch_calls": 0, "batch_rows": 0, "batch_time": 0.0,
        "njev": 0,
    })


def install():
    orig_ct = OPT.HeatPumpOptimizer._comfort_terms
    orig_batch = TM.ThermalModel.simulate_trajectory_batch
    orig_min = OPT._scoped_minimize

    def ct(self, *a, **kw):
        t0 = time.perf_counter()
        try:
            return orig_ct(self, *a, **kw)
        finally:
            S["ct_time"] += time.perf_counter() - t0
            S["ct_calls"] += 1

    def batch(self, initial_state, power_matrix, *a, **kw):
        m = np.asarray(power_matrix)
        S["batch_rows"] += int(m.shape[0]) if m.ndim == 2 else 1
        S["batch_calls"] += 1
        t0 = time.perf_counter()
        try:
            return orig_batch(self, initial_state, power_matrix, *a, **kw)
        finally:
            S["batch_time"] += time.perf_counter() - t0

    def smin(*a, **kw):
        res = orig_min(*a, **kw)
        S["njev"] += int(getattr(res, "njev", 0) or 0)
        return res

    OPT.HeatPumpOptimizer._comfort_terms = ct
    TM.ThermalModel.simulate_trajectory_batch = batch
    OPT._scoped_minimize = smin


def arm(name, price_profile):
    packed = C.make_solve(two_zone=True, dhw=True,
                          price_profile=price_profile, horizon_hours=HORIZON)
    reset()
    p0, t0, w0 = time.process_time(), time.thread_time(), time.perf_counter()
    C.run_solve(packed)
    wall = time.perf_counter() - w0
    proc = time.process_time() - p0
    thr = time.thread_time() - t0
    njev = S["njev"] or 1
    C.result(f"{name}.comfort_terms_calls_per_solve", S["ct_calls"], "calls")
    C.result(f"{name}.comfort_terms_calls_per_gradient",
             float(S["ct_calls"] / njev), "calls/grad")
    C.result(f"{name}.batch_rows_per_solve", S["batch_rows"], "rows")
    C.result(f"{name}.batch_rows_per_gradient",
             float(S["batch_rows"] / njev), "rows/grad")
    C.result(f"{name}.njev", S["njev"], "grads")
    C.result(f"{name}.comfort_terms_cpu_share_pct",
             float(100.0 * S["ct_time"] / wall), "pct")
    C.result(f"{name}.simulate_batch_cpu_share_pct",
             float(100.0 * S["batch_time"] / wall), "pct")
    C.result(f"{name}.comfort_over_simulate_batch",
             float(S["ct_time"] / S["batch_time"]) if S["batch_time"]
             else float("nan"))
    C.result(f"{name}.solve_wall_s_PROVISIONAL", float(wall), "s")
    C.result(f"{name}.solve_cpu_s_PROVISIONAL", float(proc), "s")
    C.result(f"{name}.thread_factor", float(proc / thr) if thr else float("nan"))
    return dict(wall=wall, proc=proc, ct=S["ct_time"], batch=S["batch_time"],
                calls=S["ct_calls"], njev=S["njev"])


def main():
    print(f"# baseline=7dd68dd  horizon={HORIZON}h")
    print(f"# procs_at_start={C.concurrent_procs()} load1={C.load1():.2f}")
    install()
    reset()
    # warm the caches before any timed arm
    C.run_solve(C.make_solve(two_zone=True, dhw=True, horizon_hours=HORIZON))
    ref_wall, ref_proc, ref_thr = C.reference_solve()
    C.result("reference_solve_cpu_s", float(ref_proc), "s")
    C.result("reference_thread_factor",
             float(ref_proc / ref_thr) if ref_thr else float("nan"))
    a = arm("winter_typical", C.SEASON_PRICES)
    b = arm("flat_NULL", C.FLAT_PRICES)
    C.result("cpu_ratio_vs_reference", float(a["proc"] / ref_proc))
    C.result("null_control_comfort_share_delta_pp",
             float(100.0 * (b["ct"] / b["wall"] - a["ct"] / a["wall"])), "pp")
    C.result("null_control_calls_per_gradient_delta",
             float(b["calls"] / max(b["njev"], 1)
                   - a["calls"] / max(a["njev"], 1)), "calls/grad")
    C.telemetry()


if __name__ == "__main__":
    main()
