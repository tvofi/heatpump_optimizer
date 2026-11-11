"""D9-s1 H1: simulate-step-equivalents per gradient, and per DHW planning loop.

Metric (D9.md, fixed): per gradient evaluation inside _multi_start_minimize,
scalar ThermalModel.simulate_step calls + rows of
ThermalModel.simulate_trajectory_batch (both hooked). Also printed: batch
rows x steps ("kernel step equivalents") and the per-solve split of all
simulate work by phase (gradient / scalar objective / DHW planners / other).
A gradient is one call of optimizer._batch_fd_gradient (batched path) or of
scipy's approx_derivative (scalar FD path); both are hooked.
Count key: calls delivered to the production seams; nothing is derived from
the bounds shape.

Command:
  PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python \
      tools/audit/round9/D9/s1/grad_steps.py [--no-batch]
Perturbation: --no-batch swaps optimizer._bounds_supported_by_batch for a
function returning False (the pre-#97 scalar path); per-gradient scalar
steps must go UP (to ~(n+1)*n) and batch rows to 0.
Expected (baseline, counts exact): per-gradient batch rows = n+1 = 97 on a
24 h horizon, scalar steps per gradient 0.
Baseline SHA 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine printed.
"""
from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402  (pins threads before numpy)

import argparse
import collections
import contextlib

import numpy as np  # noqa: F401
import scipy.optimize._differentiable_functions as _df

import stress
from heatpump_optimizer import optimizer as opt_mod
from heatpump_optimizer.optimizer import HeatPumpOptimizer
from heatpump_optimizer.thermal_model import ThermalModel

PHASE_METHODS = [
    # DHW planning loops (optimizer.HeatPumpOptimizer)
    "_plan_dhw_min_cost", "_plan_dhw_cheapest_first", "_repair_dhw_floor",
    "_clamp_dhw_to_capacity", "_apply_dhw_min_run", "_build_dhw_requirements",
    "_dhw_window_floors", "_dhw_legionella_plan", "_dhw_coil_wood_forecast",
    # other named stages
    "_compute_baseline_power", "_baseline_dhw_economics", "_build_result",
    "_analyze_forecast_trajectory", "_deferred_energy_cost", "_replay_end_state",
    "_tighten_buffer_caps", "_derive_hold_schedule",
]


class Meter:
    def __init__(self):
        self.stack: list[str] = []
        self.in_grad = 0
        self.grad_calls = 0
        self.grad_kind = collections.Counter()
        self.per_grad_scalar: list[int] = []
        self.per_grad_rows: list[int] = []
        self.per_grad_rowsteps: list[int] = []
        self._g_scalar = self._g_rows = self._g_rowsteps = 0
        self.by_phase = collections.Counter()      # kernel step equivalents
        self.dhw_by_phase = collections.Counter()  # simulate_dhw_step calls
        self.phase_calls = collections.Counter()
        self.minimize_calls = 0

    def phase(self):
        if self.in_grad:
            return "gradient"
        return self.stack[-1] if self.stack else "other"


M = Meter()


def _wrap_method(name):
    orig = getattr(HeatPumpOptimizer, name)

    def w(self, *a, **k):
        M.stack.append(name)
        M.phase_calls[name] += 1
        try:
            return orig(self, *a, **k)
        finally:
            M.stack.pop()
    return orig, w


@contextlib.contextmanager
def instrument(no_batch: bool):
    saved = []
    for name in PHASE_METHODS:
        if hasattr(HeatPumpOptimizer, name):
            orig, w = _wrap_method(name)
            saved.append((HeatPumpOptimizer, name, orig))
            setattr(HeatPumpOptimizer, name, w)

    orig_msm = opt_mod._multi_start_minimize

    def msm(*a, **k):
        M.stack.append("_multi_start_minimize")
        M.phase_calls["_multi_start_minimize"] += 1
        try:
            return orig_msm(*a, **k)
        finally:
            M.stack.pop()
    saved.append((opt_mod, "_multi_start_minimize", orig_msm))
    opt_mod._multi_start_minimize = msm

    def grad_wrapper(orig, kind):
        def g(*a, **k):
            M.in_grad += 1
            M._g_scalar = M._g_rows = M._g_rowsteps = 0
            try:
                return orig(*a, **k)
            finally:
                M.in_grad -= 1
                M.grad_calls += 1
                M.grad_kind[kind] += 1
                M.per_grad_scalar.append(M._g_scalar)
                M.per_grad_rows.append(M._g_rows)
                M.per_grad_rowsteps.append(M._g_rowsteps)
        return g

    o_bfd = opt_mod._batch_fd_gradient
    saved.append((opt_mod, "_batch_fd_gradient", o_bfd))
    opt_mod._batch_fd_gradient = grad_wrapper(o_bfd, "batched")
    o_ad = _df.approx_derivative
    saved.append((_df, "approx_derivative", o_ad))
    _df.approx_derivative = grad_wrapper(o_ad, "scalar_fd")

    if no_batch:
        o_b = opt_mod._bounds_supported_by_batch
        saved.append((opt_mod, "_bounds_supported_by_batch", o_b))
        opt_mod._bounds_supported_by_batch = lambda bounds: False

    # Chain under stress.SolverWork, which build_case enters: it calls these
    # class attributes at call time, so wrapping them is inside its meter.
    o_step = stress.SolverWork._step_wrapped
    o_batch = stress.SolverWork._batch_wrapped
    o_dhw = stress.SolverWork._dhw_step_wrapped

    def step(*a, **k):
        if M.in_grad:
            M._g_scalar += 1
        M.by_phase[M.phase()] += 1
        return o_step(*a, **k)

    def batch(*a, **k):
        mat = a[2] if len(a) > 2 else k["power_matrix"]
        rows, steps = int(mat.shape[0]), int(mat.shape[1])
        if M.in_grad:
            M._g_rows += rows
            M._g_rowsteps += rows * steps
        M.by_phase[M.phase()] += rows * steps
        return o_batch(*a, **k)

    def dstep(*a, **k):
        M.dhw_by_phase[M.phase()] += 1
        return o_dhw(*a, **k)

    stress.SolverWork._step_wrapped = step
    stress.SolverWork._batch_wrapped = batch
    stress.SolverWork._dhw_step_wrapped = dstep
    saved += [(stress.SolverWork, "_step_wrapped", o_step),
              (stress.SolverWork, "_batch_wrapped", o_batch),
              (stress.SolverWork, "_dhw_step_wrapped", o_dhw)]
    try:
        yield
    finally:
        for obj, name, orig in reversed(saved):
            setattr(obj, name, orig)


SCENARIOS = {
    "two_zone_dhw_winter": dict(season="winter", two_zone=True, dhw=True),
    "single_zone_dhw_winter": dict(season="winter", two_zone=False, dhw=True),
    "single_zone_nodhw_winter": dict(season="winter", two_zone=False, dhw=False),
    "zero_range_pin_off": dict(season="winter", two_zone=False, dhw=True, pin_off_steps=(40,)),
    "zero_range_fuse_3p68": dict(season="winter", two_zone=False, dhw=True, power_cap_kw=3.68),
    "two_zone_dhw_shoulder": dict(season="shoulder", two_zone=True, dhw=True),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-batch", action="store_true")
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    ref = [stress.reference_solve()[1] for _ in range(4)][1:]
    ref_ms = sorted(ref)[1]
    worst_tf = 1.0
    for label, spec in SCENARIOS.items():
        if args.only and label != args.only:
            continue
        global M
        M = Meter()
        with instrument(args.no_batch), C.Clock() as clk:
            run = stress.build_case(**spec)
        worst_tf = max(worst_tf, clk.thread_factor)
        g = M.grad_calls
        tag = f"{label}{'_nobatch' if args.no_batch else ''}"
        C.result(f"{tag}.gradients", g, "count")
        C.result(f"{tag}.gradients_batched", M.grad_kind["batched"], "count")
        C.result(f"{tag}.gradients_scalar_fd", M.grad_kind["scalar_fd"], "count")
        if g:
            C.result(f"{tag}.per_grad_scalar_steps_mean", round(sum(M.per_grad_scalar) / g, 2), "steps/gradient")
            C.result(f"{tag}.per_grad_batch_rows_mean", round(sum(M.per_grad_rows) / g, 2), "rows/gradient")
            C.result(f"{tag}.per_grad_step_equiv_mean", round((sum(M.per_grad_scalar) + sum(M.per_grad_rows)) / g, 2), "scalar_steps+batch_rows/gradient")
            C.result(f"{tag}.per_grad_kernel_step_equiv_mean", round((sum(M.per_grad_scalar) + sum(M.per_grad_rowsteps)) / g, 2), "scalar_steps+rows*steps/gradient")
        tot = sum(M.by_phase.values())
        C.result(f"{tag}.space_kernel_step_equiv_total", tot, "steps")
        for ph, v in sorted(M.by_phase.items(), key=lambda kv: -kv[1]):
            C.result(f"{tag}.space_steps[{ph}]", v, f"steps ({v / max(tot,1):.3f})")
        dtot = sum(M.dhw_by_phase.values())
        C.result(f"{tag}.dhw_step_calls_total", dtot, "calls")
        for ph, v in sorted(M.dhw_by_phase.items(), key=lambda kv: -kv[1]):
            C.result(f"{tag}.dhw_steps[{ph}]", v, "calls")
        C.result(f"{tag}.multi_start_calls", M.phase_calls["_multi_start_minimize"], "count")
        C.result(f"{tag}.solver_evals", run["solver_evals"], "count")
        C.result(f"{tag}.solve_thread_ms", round(run["solve_thread_ms"], 1), "ms (provisional)")
        C.result(f"{tag}.solve_share_of_reference", round(run["solve_cpu_ms"] / ref_ms, 2), "x reference_solve (ratio)")
        C.result(f"{tag}.thread_factor", clk.thread_factor)
    C.result("reference_solve_cpu_ms", round(ref_ms, 1), "ms (provisional)")
    C.trailer(worst_tf)


if __name__ == "__main__":
    main()
