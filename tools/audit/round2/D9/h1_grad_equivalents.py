"""D9 metric 1: simulate-step-equivalents per gradient evaluation.

Metric (binding, tools/audit/briefs/D9.md): scalar ``simulate_step`` calls +
rows of ``simulate_trajectory_batch``, both hooked by monkeypatching the
production symbols, per gradient evaluation (``OptimizeResult.njev`` summed
over the L-BFGS-B runs) of one ``_multi_start_minimize`` call.

Command (from the repository root):
    PYTHONPATH=tests/hastub python tools/audit/round2/D9/h1_grad_equivalents.py

Expected (baseline c398fc8, n = 96 steps, exact -- counts are deterministic):
    two_zone_dhw   equivalents_per_gradient = 288 (= 3n: n batch rows + 2n
                   scalar steps, the scalar objective being evaluated TWICE
                   per gradient -- once by scipy, once inside the batched jac
                   for its f0), on the batched path
    pin_zero_range equivalents_per_gradient = 9312 (= n(n+1): scipy's own
                   forward-difference gradient, scalar path); the same pin
                   in the two-zone DHW solve, and a fuse/capacity cap equal
                   to the DHW run power (0.8 p_max) at every step or at ONE
                   DHW step, put the WHOLE solve on that path: 0.9-1.5 M
                   simulate_step calls, 10-18 s of M1 CPU, 400-750x the
                   reference solve against 38x on the batched path
    perturbation horizon 24 h -> 48 h (n = 192): two_zone_dhw rises to 576
    perturbation one-entry memo on ThermalModel.simulate_trajectory (stands
                   in for reusing scipy's f(x) as the jac's f0): falls to 192
CPU shares are ratios of thread CPU inside one process and are final; the
solve-to-reference CPU ratio is against tests/stress.py:reference_solve.

Instrumented symbols: thermal_model:ThermalModel.simulate_step,
thermal_model:ThermalModel.simulate_trajectory_batch, optimizer:_scoped_minimize,
optimizer:_batch_fd_gradient, optimizer:_multi_start_minimize.
Machine: Apple M1 8-core 8 GB (audit box, shared during the fan-out).
"""
from __future__ import annotations

import os
import sys
import time

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round2", "D9"))
import d9lib  # noqa: E402  (thread pin before numpy)

import numpy as np  # noqa: E402

from heatpump_optimizer import optimizer as opt_mod  # noqa: E402
from heatpump_optimizer import thermal_model as tm_mod  # noqa: E402

C = {}


def reset():
    C.update(steps=0, rows=0, njev=0, nfev=0, nit=0, batch_grads=0,
             msm_calls=0, lbfgs_runs=0, scalar_traj=0,
             t_scalar=0.0, t_batch=0.0, t_dhw=0.0, t_lbfgs=0.0, t_msm=0.0)


reset()

# --- hooks ----------------------------------------------------------------
_orig_step = tm_mod.ThermalModel.simulate_step
_orig_batch = tm_mod.ThermalModel.simulate_trajectory_batch
_orig_traj = tm_mod.ThermalModel.simulate_trajectory
_orig_dhw_req = opt_mod.HeatPumpOptimizer._build_dhw_requirements
_orig_scoped = opt_mod._scoped_minimize
_orig_bfd = opt_mod._batch_fd_gradient
_orig_msm = opt_mod._multi_start_minimize


def hooked_step(self, *a, **k):
    C["steps"] += 1
    return _orig_step(self, *a, **k)


def hooked_batch(self, initial_state, power_matrix, *a, **k):
    C["rows"] += int(np.asarray(power_matrix).shape[0])
    t0 = time.thread_time()
    try:
        return _orig_batch(self, initial_state, power_matrix, *a, **k)
    finally:
        C["t_batch"] += time.thread_time() - t0


def hooked_traj(self, *a, **k):
    C["scalar_traj"] += 1
    t0 = time.thread_time()
    try:
        return _orig_traj(self, *a, **k)
    finally:
        C["t_scalar"] += time.thread_time() - t0


def hooked_dhw_req(self, *a, **k):
    t0 = time.thread_time()
    try:
        return _orig_dhw_req(self, *a, **k)
    finally:
        C["t_dhw"] += time.thread_time() - t0


def hooked_scoped(*a, **k):
    C["lbfgs_runs"] += 1
    t0 = time.thread_time()
    try:
        res = _orig_scoped(*a, **k)
    finally:
        C["t_lbfgs"] += time.thread_time() - t0
    C["njev"] += int(getattr(res, "njev", 0) or 0)
    C["nfev"] += int(getattr(res, "nfev", 0) or 0)
    C["nit"] += int(getattr(res, "nit", 0) or 0)
    return res


def hooked_bfd(*a, **k):
    C["batch_grads"] += 1
    return _orig_bfd(*a, **k)


def hooked_msm(*a, **k):
    C["msm_calls"] += 1
    t0 = time.thread_time()
    try:
        return _orig_msm(*a, **k)
    finally:
        C["t_msm"] += time.thread_time() - t0


tm_mod.ThermalModel.simulate_step = hooked_step
tm_mod.ThermalModel.simulate_trajectory_batch = hooked_batch
tm_mod.ThermalModel.simulate_trajectory = hooked_traj
opt_mod.HeatPumpOptimizer._build_dhw_requirements = hooked_dhw_req
opt_mod._scoped_minimize = hooked_scoped
opt_mod._batch_fd_gradient = hooked_bfd
opt_mod._multi_start_minimize = hooked_msm

# --- cases ----------------------------------------------------------------
stress = d9lib.load_stress_prefix()
build_case = stress["build_case"]
START = stress["START"]
unit_ms, ref_tf = d9lib.reference_unit_ms(stress, 5)
d9lib.result("reference_solve_cpu", unit_ms, "ms_provisional")


def report(label: str, clocks: d9lib.Clocks, n: int):
    steps, rows, njev = C["steps"], C["rows"], max(C["njev"], 1)
    equiv = steps + rows
    d9lib.result(f"{label}.n_steps", n, "count")
    d9lib.result(f"{label}.multi_start_calls", C["msm_calls"], "count")
    d9lib.result(f"{label}.lbfgs_runs", C["lbfgs_runs"], "count")
    d9lib.result(f"{label}.njev", C["njev"], "count")
    d9lib.result(f"{label}.nfev", C["nfev"], "count")
    d9lib.result(f"{label}.nit", C["nit"], "count")
    d9lib.result(f"{label}.batch_gradients", C["batch_grads"], "count")
    d9lib.result(f"{label}.path", "batched" if C["batch_grads"] else "scalar", "path")
    d9lib.result(f"{label}.simulate_step_calls", steps, "count")
    d9lib.result(f"{label}.batch_rows", rows, "count")
    d9lib.result(f"{label}.equivalents_total", equiv, "count")
    d9lib.result(f"{label}.equivalents_per_gradient", equiv / njev, "count")
    d9lib.result(f"{label}.scalar_steps_per_gradient", steps / njev, "count")
    d9lib.result(f"{label}.batch_rows_per_gradient", rows / njev, "count")
    d9lib.result(f"{label}.scalar_trajectories", C["scalar_traj"], "count")
    d9lib.result(f"{label}.solve_cpu", clocks.proc_ms, "ms_provisional")
    d9lib.result(f"{label}.solve_over_reference", clocks.proc_ms / unit_ms, "ratio")
    tot = max(clocks.thread_ms / 1000.0, 1e-9)
    d9lib.result(f"{label}.share_scalar_sim", C["t_scalar"] / tot, "ratio")
    d9lib.result(f"{label}.share_batch_sim", C["t_batch"] / tot, "ratio")
    d9lib.result(f"{label}.share_dhw_planning", C["t_dhw"] / tot, "ratio")
    d9lib.result(f"{label}.share_lbfgs_total", C["t_lbfgs"] / tot, "ratio")
    d9lib.result(f"{label}.share_multi_start_total", C["t_msm"] / tot, "ratio")


def measured_build(label, **kw):
    reset()
    with d9lib.Clocks() as c:
        run = build_case(**kw)
    report(label, c, run["n"])
    return run, c


def measured_optimize(label, run, **extra):
    reset()
    with d9lib.Clocks() as c:
        run["optimizer"].optimize(
            run["initial"], run["prices"], run["outdoor"], run["wind"],
            run["rain"], run["solar"], START, None, run["surplus"], **extra,
        )
    report(label, c, run["n"])
    return c


tfs = []
run_tz, c = measured_build("two_zone_dhw", season="winter", two_zone=True, dhw=True)
tfs.append(c.thread_factor)
_, c = measured_build("single_zone_dhw", season="winter", two_zone=False, dhw=True)
tfs.append(c.thread_factor)
run_sz, c = measured_build("single_zone_nodhw", season="winter", two_zone=False, dhw=False)
tfs.append(c.thread_factor)

# Zero-range bounds, class 1: a manual pin forcing one step off -> (0, 0).
pins = np.full(run_sz["n"], np.nan)
pins[40] = 0.0
c = measured_optimize("pin_zero_range", run_sz, space_pins=pins)
tfs.append(c.thread_factor)

# The same pin in the default two-zone DHW solve: the whole solve (all of
# its gradients) leaves the batched path, not just the pinned variable.
pins_tz = np.full(run_tz["n"], np.nan)
pins_tz[40] = 0.0
c = measured_optimize("pin_zero_range_two_zone_dhw", run_tz, space_pins=pins_tz)
tfs.append(c.thread_factor)

# Zero-range bounds, class 2: an external per-step cap equal to the DHW run
# power (0.8 * p_max, optimizer.py:3195), so a DHW block consumes the whole
# cap and space heating inside it gets (0, 0).
p_max = float(run_tz["params"].max_electrical_power)
cap = np.full(run_tz["n"], 0.8 * p_max)
c = measured_optimize("dhw_cap_zero_range", run_tz, power_caps_extra=cap)
tfs.append(c.thread_factor)

# Class 2 at ONE step only: the cap is p_max everywhere except the first
# step the default plan runs hot water in, where it equals the DHW run
# power. _bounds_supported_by_batch rejects the whole solve on one such
# bound (optimizer.py, "if lo >= hi: return False").
dhw_sched = np.asarray(run_tz["result"].dhw_power_schedule, dtype=float)
first_dhw = int(np.argmax(dhw_sched > 1e-6))
cap_one = np.full(run_tz["n"], p_max)
cap_one[first_dhw] = 0.8 * p_max
d9lib.result("dhw_cap_one_step.step", first_dhw, "index")
c = measured_optimize("dhw_cap_one_step_zero_range", run_tz, power_caps_extra=cap_one)
tfs.append(c.thread_factor)

# Perturbation 1: horizon 24 h -> 48 h (n 96 -> 192); per-gradient must rise.
_, c = measured_build("perturb_h48_two_zone_dhw", season="winter", two_zone=True,
                      dhw=True, hours=48)
tfs.append(c.thread_factor)

# Perturbation 2: a one-entry memo on the scalar trajectory. scipy evaluates
# f(x) at every trial point and the batched jac then re-evaluates f(x) at the
# SAME x for its f0; reusing the first makes the second free. Expected: the
# scalar steps per gradient halve (2n -> n), the batch rows do not move.
_memo = {}


def memo_traj(self, initial_state, power_schedule, *a, **k):
    key = (id(self), id(initial_state), np.asarray(power_schedule).tobytes())
    hit = _memo.get(key)
    if hit is not None:
        # Restore the recorded side channels exactly as the real call would.
        self.last_buffer_trajectory, self.last_buffer_refused, self.last_wood_trajectory, out = hit
        return out
    out = hooked_traj(self, initial_state, power_schedule, *a, **k)
    _memo.clear()
    _memo[key] = (self.last_buffer_trajectory, self.last_buffer_refused,
                  self.last_wood_trajectory, out)
    return out


tm_mod.ThermalModel.simulate_trajectory = memo_traj
try:
    _, c = measured_build("perturb_memo_two_zone_dhw", season="winter",
                          two_zone=True, dhw=True)
    tfs.append(c.thread_factor)
finally:
    tm_mod.ThermalModel.simulate_trajectory = hooked_traj

d9lib.closing(float(np.median(tfs)))
