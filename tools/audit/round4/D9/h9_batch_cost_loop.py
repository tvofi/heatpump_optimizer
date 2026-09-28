"""D9 round 4 / H9 -- the batched objective's cost half: a Python row loop
at the 7dd68dd baseline, vectorized since (#948, PR #985, 2026-09-14).

HISTORY (#950, D9-INST re-record): this header used to promise a
``row_loop_share_pct`` RESULT (25 - 55 +/- 8 pp) that the script never
printed -- grep found the name only in these header lines, and a judge
re-running per header looked for a RESULT that could not exist. What the
band described was real at the baseline: ``objective_batch`` (both twins)
vectorized the simulation (#97) and then re-computed the cost terms in a
Python loop over the B batch rows, ``_comfort_terms`` entering 97.02 times
per gradient at 33.3 % of the solve's wall (verify-0-3 measured the loop
itself at 43.28 % by cProfile). PR #985 replaced the loop with
``_cost_terms_batch``, called once per batch; the metrics and bands below
are re-recorded against that reality at ad7bcdf.

METRICS (all hooking production symbols):
  comfort_terms_calls_per_solve      count, FINAL
  comfort_terms_calls_per_gradient   count / njev, FINAL
  batch_rows_per_solve               count, FINAL
  cost_terms_batch_calls_per_solve   count, FINAL -- the batched twin's
                                     entries; the residual per-row
                                     ``_comfort_terms`` entries are the
                                     scalar trajectory scipy evaluates at
                                     each iterate, not the removed loop
  comfort_terms_cpu_share_pct        accumulated ``time.perf_counter``
                                     inside ``_comfort_terms`` / solve wall
  cost_terms_family_share_pct        (``_comfort_terms`` + the batched
                                     ``_cost_terms_batch``) / solve wall --
                                     this IS the metric the never-printed
                                     ``row_loop_share_pct`` stood for, now
                                     printed under a name that says what it
                                     measures
  simulate_batch_cpu_share_pct       the same for
                                     ``simulate_trajectory_batch``
  cpu_ratio_vs_reference             solve CPU / stress.reference_solve CPU

Shares are wall fractions of the SAME solve, so they are ratios and
survive contention; the absolute seconds are PROVISIONAL. A null control
at the flat price profile is measured for every number -- the cost family
is a property of the batch shape, not of the prices, so the shares must
NOT move at flat prices, which is what distinguishes a structural cost
from a price-driven one.

COMMAND (from the repository root):

    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
      MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
      python3 tools/audit/round4/D9/h9_batch_cost_loop.py

EXPECTED (re-recorded at ad7bcdf 2026-09-14, post-#985; the 7dd68dd bands
-- 96 - 99 calls/grad, 15 - 35 % comfort share -- were the row loop the
fix removed and are history, not the expectation):
  comfort_terms_calls_per_gradient ~1.0 (+/- 0.1)
  cost_terms_batch_calls_per_gradient ~1.0 (+/- 0.1)
  comfort_terms_cpu_share_pct      <= 2
  cost_terms_family_share_pct      30 - 50 (+/- 5 pp)  -- the family is
                                     batched now, one call per gradient,
                                     but still the wall's largest Python
                                     item beside the simulation (~40 %
                                     measured; the row-loop wall share it
                                     replaced was 43.28 % by cProfile,
                                     against a solve wall 38 % longer)

live-header: this header is maintained against the tree; harness_headers.py executes it.

FINAL RESULT (exact; #1005 review follow-up -- the marker above puts
this harness in tests/harness_headers.py's executed set, which compares
these lines to the run. The arm-scoped names further down carry a dot
the checker's RESULT pattern cannot read, so main() also restates the
winter arm's structural per-gradient facts under plain names):
    RESULT cost_terms_batch_calls_per_gradient=1
    RESULT batch_rows_per_gradient=96
    RESULT null_control_batched_calls_per_gradient_delta=0
Per-gradient ratios, not absolute counts: every gradient evaluation is
exactly one batched-twin call (jac -> _batch_fd_gradient ->
objective_batch) of n_steps rows, so they hold on any backend where the
iteration count itself does not reproduce. The absolute per-solve
counts (njev 305 winter / 300 flat on the recording seat) stay unpinned
deliberately -- they are solver-path numbers.

PERTURBATION: ``H9_HORIZON=12`` halves the horizon, so the batch has ~49
rows instead of ~97; ``batch_rows_per_gradient`` must fall to ~48. That
is the direction proving the batch width drives the work and not a
constant.

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
        "ctb_calls": 0, "ctb_time": 0.0,
        "batch_calls": 0, "batch_rows": 0, "batch_time": 0.0,
        "njev": 0,
    })


def install():
    orig_ct = OPT.HeatPumpOptimizer._comfort_terms
    orig_ctb = OPT.HeatPumpOptimizer._cost_terms_batch
    orig_batch = TM.ThermalModel.simulate_trajectory_batch
    orig_min = OPT._scoped_minimize

    def ct(self, *a, **kw):
        t0 = time.perf_counter()
        try:
            return orig_ct(self, *a, **kw)
        finally:
            S["ct_time"] += time.perf_counter() - t0
            S["ct_calls"] += 1

    def ctb(self, *a, **kw):
        # The batched cost half (#985). Only the outer twin is timed:
        # ``_cost_terms_batch`` calls ``_comfort_terms_batch`` itself, so
        # hooking both would double-count the nested span.
        t0 = time.perf_counter()
        try:
            return orig_ctb(self, *a, **kw)
        finally:
            S["ctb_time"] += time.perf_counter() - t0
            S["ctb_calls"] += 1

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
    OPT.HeatPumpOptimizer._cost_terms_batch = ctb
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
    C.result(f"{name}.cost_terms_batch_calls_per_solve",
             S["ctb_calls"], "calls")
    C.result(f"{name}.cost_terms_batch_calls_per_gradient",
             float(S["ctb_calls"] / njev), "calls/grad")
    C.result(f"{name}.batch_rows_per_solve", S["batch_rows"], "rows")
    C.result(f"{name}.batch_rows_per_gradient",
             float(S["batch_rows"] / njev), "rows/grad")
    C.result(f"{name}.njev", S["njev"], "grads")
    C.result(f"{name}.comfort_terms_cpu_share_pct",
             float(100.0 * S["ct_time"] / wall), "pct")
    C.result(f"{name}.cost_terms_family_share_pct",
             float(100.0 * (S["ct_time"] + S["ctb_time"]) / wall), "pct")
    C.result(f"{name}.simulate_batch_cpu_share_pct",
             float(100.0 * S["batch_time"] / wall), "pct")
    C.result(f"{name}.comfort_over_simulate_batch",
             float(S["ct_time"] / S["batch_time"]) if S["batch_time"]
             else float("nan"))
    C.result(f"{name}.solve_wall_s_PROVISIONAL", float(wall), "s")
    C.result(f"{name}.solve_cpu_s_PROVISIONAL", float(proc), "s")
    C.result(f"{name}.thread_factor", float(proc / thr) if thr else float("nan"))
    return dict(wall=wall, proc=proc, ct=S["ct_time"], batch=S["batch_time"],
                ctb=S["ctb_time"], calls=S["ct_calls"], njev=S["njev"],
                ctb_calls=S["ctb_calls"], batch_rows=S["batch_rows"])


def main():
    t0 = C.span_start()
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
    # #1005 review follow-up: checker-readable FINAL summaries. The
    # arm-scoped names carry a dot, which tests/harness_headers.py's
    # RESULT pattern ([A-Za-z0-9_]+=) cannot read; these restate the
    # winter arm's structural per-gradient facts under plain names, with
    # the flat null's delta beside them. Ratios, not counts: one
    # batched-twin call per gradient evaluation, of n_steps rows each,
    # independent of how many iterations the solver took.
    C.result("cost_terms_batch_calls_per_gradient",
             float(a["ctb_calls"] / max(a["njev"], 1)), "calls/grad")
    C.result("batch_rows_per_gradient",
             float(a["batch_rows"] / max(a["njev"], 1)), "rows/grad")
    C.result("null_control_batched_calls_per_gradient_delta",
             float(b["ctb_calls"] / max(b["njev"], 1)
                   - a["ctb_calls"] / max(a["njev"], 1)), "calls/grad")
    C.result("cpu_ratio_vs_reference", float(a["proc"] / ref_proc))
    C.result("null_control_comfort_share_delta_pp",
             float(100.0 * (b["ct"] / b["wall"] - a["ct"] / a["wall"])), "pp")
    C.result("null_control_calls_per_gradient_delta",
             float(b["calls"] / max(b["njev"], 1)
                   - a["calls"] / max(a["njev"], 1)), "calls/grad")
    C.result("null_control_family_share_delta_pp",
             float(100.0 * ((b["ct"] + b["ctb"]) / b["wall"]
                            - (a["ct"] + a["ctb"]) / a["wall"])), "pp")
    # #950 D9-INST: the whole-span factor in the trailing block as well as
    # per arm -- the arms solve on the calling thread under the pinned
    # BLAS, so the plain ratio is the signal.
    C.telemetry(C.span_factor(t0))


if __name__ == "__main__":
    main()
