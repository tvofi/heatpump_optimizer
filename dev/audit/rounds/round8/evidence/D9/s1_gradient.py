"""D9 round 8 seat s1 -- gradient cost, full solves per optimize() and the DHW planning loops.

Metric (brief, fixed): simulate-step-equivalents per gradient = scalar
ThermalModel.simulate_step calls + ROWS of ThermalModel.simulate_trajectory_batch,
both hooked by monkeypatching the production class attributes, counted inside
each gradient evaluation of optimizer._multi_start_minimize (a supplied jac is
wrapped at optimizer._scoped_minimize; scipy's own FD, when no jac is supplied,
is delimited at scipy.optimize._differentiable_functions.approx_derivative).
Also printed: batch rows x steps (the stress.py SolverWork step-equivalent),
and entries into _multi_start_minimize / _scoped_minimize per optimize().
DHW planning loops: ThermalModel.simulate_dhw_step calls per call of each
HeatPumpOptimizer DHW planner method (_plan_dhw_min_cost, _plan_dhw_cheapest_first,
_apply_dhw_min_run, _clamp_dhw_to_capacity, _repair_dhw_floor), exclusive of
nested planner calls, and their share of all simulate steps in the solve.

Count key: the counts are keyed on production calls delivered through the hooked
seams (the value the seam delivers), never on an input attribute.

Command (repo root):
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 tools/audit/round8/D9/s1_gradient.py [--scalar] [--hours H]
  --scalar : perturbation -- optimizer._bounds_supported_by_batch forced False (restored in finally);
             sse_per_grad must go UP from ~96 to ~(n+1)*n.
  --hours  : horizon (default 24 -> n=96); 48 must move sse_per_grad up to ~192.
Expected (baseline cdf82da, 24 h): sse_per_grad = 96 (+-1 per memo miss) on every shape; exact counts.
Machine: 4-vCPU cloud container (audit-r8), counts are contention-immune.
"""
from __future__ import annotations

import os
for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_k, "1")

import argparse
import sys
import time
from collections import defaultdict

sys.path.insert(0, "tests")

import numpy as np  # noqa: E402
import scipy.optimize._differentiable_functions as _sdf  # noqa: E402

import stress  # noqa: E402  (has a __main__ guard)
# stress.py imports the package as ``heatpump_optimizer``; hook exactly those objects.
OPTS = [stress.optimizer_module]
TMS = [stress.ThermalModel]
HPOS = [stress.HeatPumpOptimizer]
assert stress.optimizer_module.HeatPumpOptimizer is stress.HeatPumpOptimizer

PLANNERS = ("_plan_dhw_min_cost", "_plan_dhw_cheapest_first", "_apply_dhw_min_run",
            "_clamp_dhw_to_capacity", "_repair_dhw_floor", "_build_dhw_requirements")


class Meter:
    def __init__(self):
        self.step = 0
        self.rows = 0
        self.rowsteps = 0
        self.dhw_step = 0
        self.msm = 0
        self.scoped = 0
        self.grads = []            # per-gradient (sse, rowsteps+steps, path)
        self.planner_stack = []
        self.planner = defaultdict(lambda: [0, 0, 0.0])  # name -> [calls, exclusive dhw steps, inclusive thread-CPU s]
        self.grad_cpu = 0.0
        self.saved = []

    def _set(self, obj, name, new):
        self.saved.append((obj, name, obj.__dict__[name]))
        setattr(obj, name, new)

    def __enter__(self):
        m = self
        for TM in TMS:
            s0, b0, d0 = TM.simulate_step, TM.simulate_trajectory_batch, TM.simulate_dhw_step

            def st(*a, _f=s0, **k):
                m.step += 1
                return _f(*a, **k)

            def bt(*a, _f=b0, **k):
                mat = a[2] if len(a) > 2 else k["power_matrix"]
                m.rows += int(mat.shape[0])
                m.rowsteps += int(mat.shape[0] * mat.shape[1])
                return _f(*a, **k)

            def dt(*a, _f=d0, **k):
                m.dhw_step += 1
                if m.planner_stack:
                    m.planner[m.planner_stack[-1]][1] += 1
                return _f(*a, **k)
            self._set(TM, "simulate_step", st)
            self._set(TM, "simulate_trajectory_batch", bt)
            self._set(TM, "simulate_dhw_step", dt)
            # build_case wraps the ORIGINAL kernels through stress.SolverWork's
            # class attributes; point those at ours so its meter sits over ours.
            self._set(stress.SolverWork, "_step_wrapped", st)
            self._set(stress.SolverWork, "_batch_wrapped", bt)
            self._set(stress.SolverWork, "_dhw_step_wrapped", dt)
        for H in HPOS:
            for name in PLANNERS:
                f0 = H.__dict__[name]

                def pw(*a, _f=f0, _n=name, **k):
                    m.planner[_n][0] += 1
                    m.planner_stack.append(_n)
                    t0 = time.thread_time()
                    try:
                        return _f(*a, **k)
                    finally:
                        m.planner_stack.pop()
                        if not m.planner_stack or _n == "_build_dhw_requirements":
                            pass
                        m.planner[_n][2] += time.thread_time() - t0
                self._set(H, name, pw)
        for O in OPTS:
            msm0, sc0 = O._multi_start_minimize, O._scoped_minimize

            def msm(*a, _f=msm0, **k):
                m.msm += 1
                return _f(*a, **k)

            def sc(*a, _f=sc0, **k):
                m.scoped += 1
                jac = k.get("jac")
                if jac is not None:
                    def wj(x, *aa, _j=jac):
                        b = (m.step, m.rows, m.rowsteps)
                        t0 = time.thread_time()
                        g = _j(x, *aa)
                        m.grad_cpu += time.thread_time() - t0
                        m.grads.append((m.step - b[0] + m.rows - b[1],
                                        m.step - b[0] + m.rowsteps - b[2], "batch"))
                        return g
                    k["jac"] = wj
                return _f(*a, **k)
            self._set(O, "_multi_start_minimize", msm)
            self._set(O, "_scoped_minimize", sc)
            self._set(stress.SolverWork, "_wrapped", sc)
        ad0 = _sdf.approx_derivative

        def ad(*a, _f=ad0, **k):
            b = (m.step, m.rows, m.rowsteps)
            t0 = time.thread_time()
            g = _f(*a, **k)
            m.grad_cpu += time.thread_time() - t0
            m.grads.append((m.step - b[0] + m.rows - b[1],
                            m.step - b[0] + m.rowsteps - b[2], "scipy-fd"))
            return g
        self._set(_sdf, "approx_derivative", ad)
        return self

    def __exit__(self, *exc):
        for obj, name, val in reversed(self.saved):
            setattr(obj, name, val)
        return False


SHAPES = [
    ("two_zone_dhw_default", dict(season="winter", two_zone=True, dhw=True)),
    ("single_zone_space", dict(season="winter", two_zone=False, dhw=False)),
    ("single_zone_dhw", dict(season="winter", two_zone=False, dhw=True)),
    ("zero_range_fuse_cap_3.68kW", dict(season="winter", two_zone=True, dhw=True, power_cap_kw=3.68)),
    ("zero_range_manual_pin", dict(season="winter", two_zone=True, dhw=True, pin_off_steps=(10,))),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scalar", action="store_true")
    ap.add_argument("--hours", type=int, default=24)
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    saved_gate = [(O, O._bounds_supported_by_batch) for O in OPTS]
    if args.scalar:
        for O in OPTS:
            O._bounds_supported_by_batch = lambda b: False
    cpu0, th0 = time.process_time(), time.thread_time()
    try:
        for label, spec in SHAPES:
            if args.only and args.only not in label:
                continue
            with Meter() as m:
                case = stress.build_case(hours=args.hours, **spec)
            n = case["n"]
            g = m.grads
            sse = [x[0] for x in g]
            full = [x[1] for x in g]
            paths = sorted({x[2] for x in g})
            total = m.step + m.rowsteps + m.dhw_step
            print(f"RESULT {label}.n_steps={n} count")
            print(f"RESULT {label}.multi_start_minimize_entries={m.msm} count")
            print(f"RESULT {label}.scoped_minimize_calls={m.scoped} count")
            print(f"RESULT {label}.gradients={len(g)} count")
            print(f"RESULT {label}.grad_paths={'+'.join(paths)}")
            if g:
                print(f"RESULT {label}.sse_per_grad_median={float(np.median(sse)):.1f} sse")
                print(f"RESULT {label}.sse_per_grad_max={max(sse)} sse")
                print(f"RESULT {label}.stepeq_per_grad_median={float(np.median(full)):.1f} step-equivalents")
            gsum = sum(full)
            print(f"RESULT {label}.gradient_share_of_sim_steps={gsum / max(total, 1):.4f} ratio")
            print(f"RESULT {label}.sim_step_equivalents_total={total} count")
            print(f"RESULT {label}.dhw_steps_total={m.dhw_step} count")
            solve_ms = case["solve_thread_ms"]
            print(f"RESULT {label}.solve_thread_cpu_ms={solve_ms:.0f} ms-cpu (provisional)")
            print(f"RESULT {label}.gradient_cpu_share={m.grad_cpu * 1000 / max(solve_ms, 1e-9):.4f} ratio (provisional)")
            for name in PLANNERS:
                c, s, cpu = m.planner.get(name, [0, 0, 0.0])
                if c:
                    print(f"RESULT {label}.{name}.calls={c} count")
                    print(f"RESULT {label}.{name}.dhw_steps_exclusive={s} count")
                    print(f"RESULT {label}.{name}.cpu_share_inclusive={cpu * 1000 / max(solve_ms, 1e-9):.4f} ratio (provisional)")
            print(f"RESULT {label}.dhw_planning_share_of_sim_steps={m.dhw_step / max(total, 1):.4f} ratio")
    finally:
        for O, f in saved_gate:
            O._bounds_supported_by_batch = f
    cpu, th = time.process_time() - cpu0, time.thread_time() - th0
    print(f"RESULT thread_factor={cpu / max(th, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        with open("/proc/vmstat") as fh:
            sw = [ln.split()[1] for ln in fh if ln.startswith("pswpin")]
        print(f"RESULT swapins={sw[0] if sw else 0}")
    except OSError:
        print("RESULT swapins=0")


if __name__ == "__main__":
    main()
