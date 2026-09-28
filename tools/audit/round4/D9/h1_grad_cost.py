"""D9 round 4 / H1 -- simulate-step-equivalents per gradient, and where a
solve's simulation work actually goes.

METRIC (D9.md, verbatim): simulate-step-equivalents = scalar
``ThermalModel.simulate_step`` calls + rows of
``ThermalModel.simulate_trajectory_batch``, both hooked by monkeypatching
the production symbols; "per gradient" divides by the number of gradient
evaluations of ``_multi_start_minimize`` (sum of ``njev`` over every
``_scoped_minimize`` result inside it).

Phase attribution is EXCLUSIVE: a wrapped method is charged only the
equivalents consumed while no deeper wrapped method is on the stack.

COMMAND (from the repository root):

    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
      MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
      python3 tools/audit/round4/D9/h1_grad_cost.py

EXPECTED (baseline 7dd68dd, 8-core Apple M1 / 8 GB, macOS 25.6, numpy on
OpenBLAS, python 3.11):

    two_zone_dhw   equiv_per_grad   96 - 200   (+/- 5 %)
    two_zone_dhw   equiv_total      1.0e5 - 2.5e5 steps (+/- 10 %)
    zero_range     equiv_per_grad   within 2x of two_zone_dhw (D9-01 held)
    dhw_planning_share_pct          reported, tolerance +/- 3 pp

PERTURBATION: ``H1_PERTURB=maxiter`` halves ``_multi_start_minimize``'s
default ``maxiter`` 300 -> 150 by monkeypatching the production default;
every ``equiv_total`` must fall. ``H1_PERTURB=nobatch`` forces
``_bounds_supported_by_batch`` to return False; ``equiv_per_grad`` must
rise by roughly the variable count.

COUNTS ARE CONTENTION-IMMUNE and final. The CPU ratio against
``tests/stress.py:reference_solve`` is printed as well and is also a
ratio; the absolute wall/CPU seconds are provisional.
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

PERTURB = os.environ.get("H1_PERTURB", "")

# ---------------------------------------------------------------- counters
STATE = {
    "scalar": 0,
    "batch_rows": 0,
    "batch_calls": 0,
    "msm_entries": 0,
    "batchfd_calls": 0,
    "njev": 0,
    "nfev": 0,
    "nit": 0,
    "minimize_calls": 0,
}
PHASE = {}          # name -> exclusive equivalents
PHASE_CALLS = {}    # name -> call count
_stack = []


def _equiv():
    return STATE["scalar"] + STATE["batch_rows"]


def _charge():
    """Charge equivalents consumed since the last checkpoint to the top frame."""
    now = _equiv()
    if _stack:
        name, mark = _stack[-1]
        PHASE[name] = PHASE.get(name, 0) + (now - mark)
        _stack[-1] = (name, now)


def phase(name, fn):
    def wrapper(*a, **kw):
        _charge()
        _stack.append((name, _equiv()))
        PHASE_CALLS[name] = PHASE_CALLS.get(name, 0) + 1
        try:
            return fn(*a, **kw)
        finally:
            _charge()
            _stack.pop()
            if _stack:
                _stack[-1] = (_stack[-1][0], _equiv())

    wrapper.__name__ = getattr(fn, "__name__", name)
    return wrapper


def install():
    orig_step = TM.ThermalModel.simulate_step
    orig_batch = TM.ThermalModel.simulate_trajectory_batch

    def step(self, *a, **kw):
        STATE["scalar"] += 1
        return orig_step(self, *a, **kw)

    def batch(self, initial_state, power_matrix, *a, **kw):
        m = np.asarray(power_matrix)
        STATE["batch_rows"] += int(m.shape[0]) if m.ndim == 2 else 1
        STATE["batch_calls"] += 1
        return orig_batch(self, initial_state, power_matrix, *a, **kw)

    TM.ThermalModel.simulate_step = step
    TM.ThermalModel.simulate_trajectory_batch = batch

    orig_msm = OPT._multi_start_minimize

    def msm(*a, **kw):
        STATE["msm_entries"] += 1
        _charge()
        _stack.append(("_multi_start_minimize", _equiv()))
        PHASE_CALLS["_multi_start_minimize"] = (
            PHASE_CALLS.get("_multi_start_minimize", 0) + 1
        )
        try:
            return orig_msm(*a, **kw)
        finally:
            _charge()
            _stack.pop()
            if _stack:
                _stack[-1] = (_stack[-1][0], _equiv())

    OPT._multi_start_minimize = msm

    orig_bfd = OPT._batch_fd_gradient

    def bfd(*a, **kw):
        STATE["batchfd_calls"] += 1
        return orig_bfd(*a, **kw)

    OPT._batch_fd_gradient = bfd

    orig_min = OPT._scoped_minimize

    def smin(*a, **kw):
        res = orig_min(*a, **kw)
        STATE["minimize_calls"] += 1
        STATE["njev"] += int(getattr(res, "njev", 0) or 0)
        STATE["nfev"] += int(getattr(res, "nfev", 0) or 0)
        STATE["nit"] += int(getattr(res, "nit", 0) or 0)
        return res

    OPT._scoped_minimize = smin

    for name in (
        "_optimize_with_dhw",
        "_optimize_space_only",
        "_solve_space",
        "_build_dhw_requirements",
        "_plan_dhw_min_cost",
        "_plan_dhw_cheapest_first",
        "_repair_dhw_floor",
        "_clamp_dhw_to_capacity",
        "_apply_dhw_min_run",
        "_baseline_dhw_economics",
        "_compute_baseline_power",
        "_build_result",
        "_co_optimize",
        "_dhw_legionella_plan",
        "_replay_end_state",
        "_tighten_buffer_caps",
        "_repair_throttled_buffer_caps",
        "_derive_hold_schedule",
    ):
        fn = getattr(OPT.HeatPumpOptimizer, name, None)
        if fn is not None:
            setattr(OPT.HeatPumpOptimizer, name, phase(name, fn))

    if PERTURB == "maxiter":
        real_msm = OPT._multi_start_minimize

        def capped(objective, candidates, bounds, args=(), maxiter=300, **kw):
            return real_msm(objective, candidates, bounds, args, 150, **kw)

        OPT._multi_start_minimize = capped
    elif PERTURB == "nobatch":
        OPT._bounds_supported_by_batch = lambda bounds: False


def reset():
    for k in STATE:
        STATE[k] = 0
    PHASE.clear()
    PHASE_CALLS.clear()
    del _stack[:]


ARMS = [
    ("two_zone_dhw", dict(two_zone=True, dhw=True)),
    ("single_zone_dhw", dict(two_zone=False, dhw=True)),
    ("single_zone_nodhw", dict(two_zone=False, dhw=False)),
    ("zero_range_fuse_cap", dict(two_zone=True, dhw=True, power_cap_kw=3.5)),
    ("two_zone_dhw_FLAT_null", dict(two_zone=True, dhw=True,
                                    price_profile=C.FLAT_PRICES)),
]


def main():
    install()
    print(f"# baseline=7dd68dd  perturb={PERTURB or 'none'}")
    print(f"# procs_at_start={C.concurrent_procs()} load1={C.load1():.2f}")

    ref = C.reference_solve()
    ref_wall, ref_proc, ref_thread = ref
    tf_ref = ref_proc / ref_thread if ref_thread > 0 else float("nan")
    C.result("reference_solve_wall_s", float(ref_wall), "s")
    C.result("reference_solve_cpu_s", float(ref_proc), "s")
    C.result("reference_thread_factor", float(tf_ref))

    rows = []
    for name, kw in ARMS:
        packed = C.make_solve(**kw)
        reset()
        p0, t0, w0 = time.process_time(), time.thread_time(), time.perf_counter()
        res = C.run_solve(packed)
        wall = time.perf_counter() - w0
        proc = time.process_time() - p0
        thr = time.thread_time() - t0
        tf = proc / thr if thr > 0 else float("nan")
        equiv = _equiv()
        njev = STATE["njev"]
        per_grad = equiv / njev if njev else float("nan")
        dhw_phase = sum(
            v for k, v in PHASE.items() if k.startswith(("_plan_dhw", "_repair_dhw",
                                                         "_clamp_dhw", "_apply_dhw",
                                                         "_build_dhw", "_baseline_dhw",
                                                         "_dhw_"))
        )
        C.result(f"{name}.equiv_total", equiv, "steps")
        C.result(f"{name}.scalar_steps", STATE["scalar"], "steps")
        C.result(f"{name}.batch_rows", STATE["batch_rows"], "rows")
        C.result(f"{name}.batch_calls", STATE["batch_calls"], "calls")
        C.result(f"{name}.batchfd_calls", STATE["batchfd_calls"], "calls")
        C.result(f"{name}.msm_entries", STATE["msm_entries"], "entries")
        C.result(f"{name}.minimize_calls", STATE["minimize_calls"], "calls")
        C.result(f"{name}.njev", njev, "grads")
        C.result(f"{name}.nfev", STATE["nfev"], "fevals")
        C.result(f"{name}.nit", STATE["nit"], "iters")
        C.result(f"{name}.equiv_per_grad", float(per_grad), "steps/grad")
        C.result(f"{name}.dhw_planning_equiv", dhw_phase, "steps")
        C.result(
            f"{name}.dhw_planning_share_pct",
            float(100.0 * dhw_phase / equiv) if equiv else float("nan"),
            "pct",
        )
        C.result(f"{name}.cpu_ratio_vs_reference", float(proc / ref_proc))
        C.result(f"{name}.wall_s_PROVISIONAL", float(wall), "s")
        C.result(f"{name}.thread_factor", float(tf))
        top = sorted(PHASE.items(), key=lambda kv: -kv[1])[:8]
        for pname, pv in top:
            C.result(
                f"{name}.phase.{pname}",
                f"{pv} ({100.0 * pv / equiv:.1f}%) calls={PHASE_CALLS.get(pname, 0)}",
            )
        rows.append((name, equiv, per_grad, res))

    C.telemetry()


if __name__ == "__main__":
    main()
