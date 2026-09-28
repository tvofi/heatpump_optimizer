"""D9 round 4 / verifier 3 -- an independent instrument for D9-05.

The finder's h9 times ``_comfort_terms`` with ``time.perf_counter`` wall
hooks and divides by the solve's wall. This harness re-measures the same
phenomenon with TWO instruments of its own:

  1. CPU-clock hooks: ``time.process_time()`` accumulated inside a wrapper
     of ``HeatPumpOptimizer._comfort_terms`` / ``ThermalModel
     .simulate_trajectory_batch`` divided by the solve's process CPU.
     A different clock and a different denominator from the finder's
     wall/wall; contention moves wall, not CPU.
  2. cProfile cumtime: the whole solve under cProfile; the share of
     ``_comfort_terms`` cumtime in the solve wall, and -- the metric h9's
     header promises but never prints -- ``row_loop_share_pct`` =
     (cumtime of the two ``objective_batch`` closures minus cumtime of
     ``simulate_trajectory_batch``) / solve wall. cProfile adds ~1 us per
     Python call, and the row loop is 5+ Python calls x 97 rows x 305
     gradients of exactly that, so this share is biased HIGH against the
     finder's number; the bias is stated, not hidden.

Arms: the default two-zone DHW solve (the finding's scenario) and a
single-zone no-DHW solve (the leave-one-out arm: is the share a property
of the two-zone objective only?).

METRIC (one line): share of the default solve's CPU consumed by
``_comfort_terms`` as calls-per-gradient and CPU/CPU and (biased-high)
profiler shares, against ``simulate_trajectory_batch``.

COMMAND (from the repository root):

    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
      MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
      python3 tools/audit/round4/D9/verify3_h9_profile.py

EXPECTED (baseline 7dd68dd, 8-core Apple M1 / 8 GB, python 3.11):
  two_zone_dhw.comfort_calls_per_gradient 96 - 99 (+/- 1)
  two_zone_dhw.comfort_cpu_share_pct      25 - 40 (+/- 8 pp)
  single_zone.comfort_calls_per_gradient  96 - 99 (+/- 1)
  wall and profiler shares are PROVISIONAL; counts and CPU/CPU ratios
  are final (CPU ratios cancel load by the README's own rule).

PERTURBATION: none needed here -- the count's dependence on the batch
width is the finder's perturbation; this harness's job is the share by a
second instrument. The single-zone arm is the shape control.

Baseline SHA 7dd68dd327fe3dbfb09f3bd0fe38910c58877697; machine: the
audit box (8-core M1, 8 GB).
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

import cProfile  # noqa: E402
import pstats  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round4", "D9"))

import d9common as C  # noqa: E402

from heatpump_optimizer import optimizer as OPT  # noqa: E402
from heatpump_optimizer import thermal_model as TM  # noqa: E402

S = {}


def reset():
    S.clear()
    S.update({
        "ct_calls": 0, "ct_cpu": 0.0,
        "batch_calls": 0, "batch_rows": 0, "batch_cpu": 0.0,
        "njev": 0,
    })


def install():
    orig_ct = OPT.HeatPumpOptimizer._comfort_terms
    orig_batch = TM.ThermalModel.simulate_trajectory_batch
    orig_min = OPT._scoped_minimize

    def v3_ct(self, *a, **kw):
        t0 = time.process_time()
        try:
            return orig_ct(self, *a, **kw)
        finally:
            S["ct_cpu"] += time.process_time() - t0
            S["ct_calls"] += 1

    def v3_batch(self, initial_state, power_matrix, *a, **kw):
        import numpy as np

        m = np.asarray(power_matrix)
        S["batch_rows"] += int(m.shape[0]) if m.ndim == 2 else 1
        S["batch_calls"] += 1
        t0 = time.process_time()
        try:
            return orig_batch(self, initial_state, power_matrix, *a, **kw)
        finally:
            S["batch_cpu"] += time.process_time() - t0

    def v3_smin(*a, **kw):
        res = orig_min(*a, **kw)
        S["njev"] += int(getattr(res, "njev", 0) or 0)
        return res

    OPT.HeatPumpOptimizer._comfort_terms = v3_ct
    TM.ThermalModel.simulate_trajectory_batch = v3_batch
    OPT._scoped_minimize = v3_smin


def _stat(st, needle, lineno=None):
    """(ncalls, cumtime) summed over every profile entry whose function
    name ends in ``needle`` (optionally at ``lineno``) across files."""
    nc = 0
    ct = 0.0
    for (fn, ln, name), (cc, _nc, _tt, _cum, _cal) in st.stats.items():
        if name == needle and (lineno is None or ln == lineno):
            nc += cc
            ct += _cum
    return nc, ct


def arm(name, **kw):
    packed = C.make_solve(**kw)
    reset()
    prof = cProfile.Profile()
    p0, t0, w0 = time.process_time(), time.thread_time(), time.perf_counter()
    prof.enable()
    C.run_solve(packed)
    prof.disable()
    wall = time.perf_counter() - w0
    proc = time.process_time() - p0
    thr = time.thread_time() - t0
    st = pstats.Stats(prof)

    njev = S["njev"] or 1
    C.result(f"{name}.comfort_calls_per_solve", S["ct_calls"], "calls")
    C.result(f"{name}.comfort_calls_per_gradient",
             float(S["ct_calls"] / njev), "calls/grad")
    C.result(f"{name}.batch_rows_per_solve", S["batch_rows"], "rows")
    C.result(f"{name}.batch_rows_per_gradient",
             float(S["batch_rows"] / njev), "rows/grad")
    C.result(f"{name}.njev", S["njev"], "grads")
    # instrument 1: CPU-clock hooks, CPU/CPU
    C.result(f"{name}.comfort_cpu_share_pct",
             float(100.0 * S["ct_cpu"] / proc), "pct")
    C.result(f"{name}.simulate_batch_cpu_share_pct",
             float(100.0 * S["batch_cpu"] / proc), "pct")
    C.result(f"{name}.comfort_over_simulate_batch_cpu",
             float(S["ct_cpu"] / S["batch_cpu"]) if S["batch_cpu"]
             else float("nan"))
    # instrument 2: cProfile cumtime shares (biased high: ~1 us per Python
    # call, and the row loop is Python-call dense)
    ct_calls, ct_cum = _stat(st, "_comfort_terms")
    sb_calls, sb_cum = _stat(st, "simulate_trajectory_batch")
    ob_calls, ob_cum = _stat(st, "objective_batch")
    C.result(f"{name}.prof_comfort_calls", ct_calls, "calls")
    C.result(f"{name}.prof_comfort_share_pct_PROVISIONAL",
             float(100.0 * ct_cum / wall), "pct")
    C.result(f"{name}.prof_simbatch_share_pct_PROVISIONAL",
             float(100.0 * sb_cum / wall), "pct")
    row_loop = ob_cum - sb_cum
    C.result(f"{name}.prof_row_loop_share_pct_PROVISIONAL",
             float(100.0 * row_loop / wall) if row_loop > 0 else -1.0, "pct")
    C.result(f"{name}.prof_objective_batch_calls", ob_calls, "calls")
    C.result(f"{name}.solve_wall_s_PROVISIONAL", float(wall), "s")
    C.result(f"{name}.solve_cpu_s", float(proc), "s")
    C.result(f"{name}.thread_factor", float(proc / thr) if thr else float("nan"))
    return dict(wall=wall, proc=proc, thr=thr)


def main():
    print(f"# baseline=7dd68dd  verifier-3 independent instrument")
    print(f"# procs_at_start={C.concurrent_procs()} load1={C.load1():.2f}")
    install()
    reset()
    C.run_solve(C.make_solve(two_zone=True, dhw=True))  # warm, untimed
    a = arm("two_zone_dhw", two_zone=True, dhw=True,
            price_profile=C.SEASON_PRICES)
    b = arm("single_zone", two_zone=False, dhw=False,
            price_profile=C.SEASON_PRICES)
    C.telemetry(a["proc"] / a["thr"] if a["thr"] else float("nan"))


if __name__ == "__main__":
    main()
