"""Verifier-3 harness for D9-01: independent metric, perturbation, fix scope.

Independent metric (NOT the finder's simulate-step count): the path is named
by scipy itself -- ``fev_per_jev = OptimizeResult.nfev / OptimizeResult.njev``
summed over the L-BFGS-B runs of one solve. On the batched-jac path scipy
calls fun and jac once each per iterate, so the ratio is 1.0; when the jac is
withheld scipy estimates it with n+1 function evaluations per gradient, so the
ratio is n+1 = 97 at n = 96. No thermal_model hook is needed: the number comes
out of scipy's own counters, which makes it independent of how the finder
counts trajectories.

Command (from the repository root):
    PYTHONPATH=tests/hastub python tools/audit/round2/D9/v3_d901_fixscope.py

Sections
  A  path metric + the finder's perturbation (add the pin / cap, remove it)
  B  other zero-range producers than pins and power_caps_extra
  C  the proposed fix (lo == hi is a fixed variable: zero step, 0.0 gradient
     entry, batch kept for the rest) -- does it clear the finding, and does
     the plan move
  D  golden fuse_guard capture with and without the fix: does the fixture drift
  E  what scipy's L-BFGS-B itself does with a fixed variable, on a 2-variable
     quadratic, under jac=None / jac with NaN / jac with 0.0

Instrumented symbols: optimizer:_scoped_minimize (counters),
optimizer:_bounds_supported_by_batch (path gate + bound census),
optimizer:_batch_fd_gradient (the fix), thermal_model:ThermalModel.simulate_step.
Baseline c398fc84eec25fc44b60d74aae05b9a2da205884; Apple M1 8-core 8 GB.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round2", "D9"))
import d9lib  # noqa: E402  (thread pin before numpy)

import numpy as np  # noqa: E402

from heatpump_optimizer import optimizer as opt_mod  # noqa: E402
from heatpump_optimizer import thermal_model as tm_mod  # noqa: E402

C = {}


def reset():
    C.update(njev=0, nfev=0, steps=0, runs=0, gate_calls=0, gate_false=0,
             zero_range_bounds=0, nonfinite_bounds=0, statuses=[])


reset()

_orig_scoped = opt_mod._scoped_minimize
_orig_gate = opt_mod._bounds_supported_by_batch
_orig_bfd = opt_mod._batch_fd_gradient
_orig_step = tm_mod.ThermalModel.simulate_step


def hooked_scoped(*a, **k):
    res = _orig_scoped(*a, **k)
    C["runs"] += 1
    C["njev"] += int(getattr(res, "njev", 0) or 0)
    C["nfev"] += int(getattr(res, "nfev", 0) or 0)
    C["statuses"].append(int(getattr(res, "status", -1)))
    return res


def hooked_gate(bounds):
    C["gate_calls"] += 1
    zero = sum(1 for lo, hi in bounds if np.isfinite(lo) and np.isfinite(hi) and lo >= hi)
    nonfin = sum(1 for lo, hi in bounds if not (np.isfinite(lo) and np.isfinite(hi)))
    C["zero_range_bounds"] += zero
    C["nonfinite_bounds"] += nonfin
    out = _orig_gate(bounds)
    if not out:
        C["gate_false"] += 1
    return out


def hooked_step(self, *a, **k):
    C["steps"] += 1
    return _orig_step(self, *a, **k)


opt_mod._scoped_minimize = hooked_scoped
opt_mod._bounds_supported_by_batch = hooked_gate
tm_mod.ThermalModel.simulate_step = hooked_step

stress = d9lib.load_stress_prefix()
build_case = stress["build_case"]
START = stress["START"]


def report(label: str):
    njev = max(C["njev"], 1)
    d9lib.result(f"{label}.lbfgs_runs", C["runs"], "count")
    d9lib.result(f"{label}.njev", C["njev"], "count")
    d9lib.result(f"{label}.nfev", C["nfev"], "count")
    d9lib.result(f"{label}.fev_per_jev", C["nfev"] / njev, "ratio")
    d9lib.result(f"{label}.path",
                 "scalar" if C["nfev"] / njev > 2.0 else "batched", "path")
    d9lib.result(f"{label}.simulate_step_calls", C["steps"], "count")
    d9lib.result(f"{label}.bounds_gate_calls", C["gate_calls"], "count")
    d9lib.result(f"{label}.bounds_gate_false", C["gate_false"], "count")
    d9lib.result(f"{label}.zero_range_bounds_seen", C["zero_range_bounds"], "count")
    d9lib.result(f"{label}.lbfgs_statuses", ",".join(str(s) for s in C["statuses"]), "codes")


def solve(label, run, **extra):
    reset()
    res = run["optimizer"].optimize(
        run["initial"], run["prices"], run["outdoor"], run["wind"],
        run["rain"], run["solar"], START, None, run["surplus"], **extra,
    )
    report(label)
    return res


# ---------------------------------------------------------------- A: path ---
run_tz = build_case(season="winter", two_zone=True, dhw=True)
n = run_tz["n"]
p_max = float(run_tz["params"].max_electrical_power)
d9lib.result("n_steps", n, "count")

base = solve("A_no_pin_two_zone_dhw", run_tz)

pins = np.full(n, np.nan)
pins[40] = 0.0
pinned = solve("A_pin_two_zone_dhw", run_tz, space_pins=pins)

cap = np.full(n, 0.8 * p_max)
capped = solve("A_cap_two_zone_dhw", run_tz, power_caps_extra=cap)

# The perturbation, executed in the removal direction on the SAME solve.
removed = solve("A_perturb_pin_removed", run_tz)
d9lib.result("A_perturb_pin_removed.matches_no_pin_plan",
             int(np.array_equal(np.asarray(removed.power_schedule),
                                np.asarray(base.power_schedule))), "bool")

# ------------------------------------------- B: other zero-range producers ---
# B1: the pump-mode gate. optimizer.py:2132 sets power_caps = zeros(n) when
# space heating is mode-blocked, so EVERY bound is (0.0, 0.0) -- no pin and no
# fuse guard involved.
solve("B1_space_blocked", run_tz, space_blocked=True)

# B2: single-zone no-DHW, mode-blocked (the other solve path, optimizer.py:2832).
run_sz = build_case(season="winter", two_zone=False, dhw=False)
solve("B2_space_blocked_nodhw", run_sz, space_blocked=True)

# B3: a forced-ON pin whose min-on power equals the headroom left by the cap.
#     _apply_pins_to_bounds emits (min(min_on, high), high); at high == min_on
#     that is lo == hi with no forced-off pin anywhere.
opt = run_tz["optimizer"]
min_on = float(opt._pin_on_power(p_max))
cap_eq = np.full(n, p_max)
cap_eq[30] = min_on
pins_on = np.full(n, np.nan)
pins_on[30] = 1.0
solve("B3_pin_on_at_min_on_cap", run_tz, power_caps_extra=cap_eq, space_pins=pins_on)

# B4: a zero entry in the external cap itself (a fuse guard whose headroom
#     went to zero for one step -- caps_extra is clipped at 0, not above it).
cap_zero = np.full(n, p_max)
cap_zero[30] = 0.0
solve("B4_cap_zero_one_step", run_tz, power_caps_extra=cap_zero)

# ------------------------------------------------------------- C: the fix ---
def fixed_bounds_gate(bounds):
    """The proposal: a fixed variable (lo == hi) no longer forfeits the batch."""
    C["gate_calls"] += 1
    zero = sum(1 for lo, hi in bounds if np.isfinite(lo) and np.isfinite(hi) and lo >= hi)
    C["zero_range_bounds"] += zero
    if not bounds:
        C["gate_false"] += 1
        return False
    for lo, hi in bounds:
        if not (np.isfinite(lo) and np.isfinite(hi)):
            C["gate_false"] += 1
            return False
        if lo > hi:  # genuinely inconsistent, still refused
            C["gate_false"] += 1
            return False
    return True


def fixed_bfd(batch_objective, args, x0, f0, eps, bounds):
    """The proposal: zero step at a fixed variable, explicit 0.0 entry."""
    g = _orig_bfd(batch_objective, args, x0, f0, eps, bounds)
    lb = np.array([b[0] for b in bounds], dtype=float)
    ub = np.array([b[1] for b in bounds], dtype=float)
    return np.where(lb >= ub, 0.0, g)


def with_fix(fn):
    opt_mod._bounds_supported_by_batch = fixed_bounds_gate
    opt_mod._batch_fd_gradient = fixed_bfd
    try:
        return fn()
    finally:
        opt_mod._bounds_supported_by_batch = hooked_gate
        opt_mod._batch_fd_gradient = _orig_bfd


fixed_pin = with_fix(lambda: solve("C_fix_pin_two_zone_dhw", run_tz, space_pins=pins))
fixed_cap = with_fix(lambda: solve("C_fix_cap_two_zone_dhw", run_tz, power_caps_extra=cap))
fixed_blocked = with_fix(lambda: solve("C_fix_space_blocked", run_tz, space_blocked=True))


def compare(label, a, b):
    pa = np.asarray(a.power_schedule, dtype=float)
    pb = np.asarray(b.power_schedule, dtype=float)
    da = np.asarray(a.dhw_power_schedule, dtype=float)
    db = np.asarray(b.dhw_power_schedule, dtype=float)
    d9lib.result(f"{label}.max_abs_power_delta", float(np.max(np.abs(pa - pb))), "kW")
    d9lib.result(f"{label}.max_abs_dhw_delta", float(np.max(np.abs(da - db))), "kW")
    d9lib.result(f"{label}.cost_delta",
                 float(a.predicted_cost) - float(b.predicted_cost), "SEK")
    d9lib.result(f"{label}.cost_rel_delta",
                 abs(float(a.predicted_cost) - float(b.predicted_cost))
                 / max(abs(float(b.predicted_cost)), 1e-12), "ratio")
    d9lib.result(f"{label}.identical", int(np.array_equal(pa, pb) and np.array_equal(da, db)), "bool")
    d9lib.result(f"{label}.pinned_step_power_fixed", float(pa[40]), "kW")
    d9lib.result(f"{label}.pinned_step_power_current", float(pb[40]), "kW")
    d9lib.result(f"{label}.any_nan_fixed", int(bool(np.any(~np.isfinite(pa)))), "bool")


compare("C_fix_vs_current_pin", fixed_pin, pinned)
compare("C_fix_vs_current_cap", fixed_cap, capped)

# ------------------------------------------------------- D: golden drift ---
sys.path.insert(0, os.path.join(os.getcwd(), "tests"))
import golden  # noqa: E402

reset()
cur = golden.capture("fuse_guard", golden.SCENARIOS["fuse_guard"])
report("D_fuse_guard_current")
reset()
fix = with_fix(lambda: golden.capture("fuse_guard", golden.SCENARIOS["fuse_guard"]))
report("D_fuse_guard_fixed")


def field_drift(name):
    a = np.asarray(cur.get(name), dtype=float).ravel()
    b = np.asarray(fix.get(name), dtype=float).ravel()
    if a.shape != b.shape:
        d9lib.result(f"D_fuse_guard.{name}_shape_changed", 1, "bool")
        return
    d9lib.result(f"D_fuse_guard.{name}_max_abs_delta",
                 float(np.max(np.abs(a - b))) if a.size else 0.0, "unit")


for _f in ("power_schedule", "dhw_power_schedule", "optimal_setpoints",
           "room_temp_trajectory", "predicted_cost", "predicted_savings"):
    field_drift(_f)
d9lib.result("D_fuse_guard.status_current", str(cur.get("status")), "label")
d9lib.result("D_fuse_guard.status_fixed", str(fix.get("status")), "label")
d9lib.result("D_fuse_guard.payload_identical", int(cur == fix), "bool")

# ------------------------------------- E: what L-BFGS-B does with lo == hi ---
from scipy.optimize import minimize  # noqa: E402

E_bounds = [(0.0, 0.0), (-5.0, 5.0)]


def q(x):
    return float((x[0] - 3.0) ** 2 + (x[1] - 1.0) ** 2)


def gnan(x):
    return np.array([np.nan, 2.0 * (x[1] - 1.0)])


def gzero(x):
    return np.array([0.0, 2.0 * (x[1] - 1.0)])


def gtrue(x):
    return np.array([2.0 * (x[0] - 3.0), 2.0 * (x[1] - 1.0)])


for _tag, _jac in (("estimated", None), ("nan_entry", gnan),
                   ("zero_entry", gzero), ("true_entry", gtrue)):
    r = minimize(q, np.array([0.0, 0.0]), jac=_jac, method="L-BFGS-B",
                 bounds=E_bounds, options={"maxiter": 200, "ftol": 1e-6, "eps": 1e-4})
    d9lib.result(f"E_{_tag}.x0", float(r.x[0]), "value")
    d9lib.result(f"E_{_tag}.x1", float(r.x[1]), "value")
    d9lib.result(f"E_{_tag}.fun", float(r.fun), "value")
    d9lib.result(f"E_{_tag}.status", int(r.status), "code")
    d9lib.result(f"E_{_tag}.nit", int(r.nit), "count")

d9lib.closing(1.0)
