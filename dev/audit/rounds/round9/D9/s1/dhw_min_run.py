"""D9-s1 H11: the DHW min-run repair's work -- optimizer.HeatPumpOptimizer.
_apply_dhw_min_run -- per weak slot, split by accepted / refused slots, and
what an early exit at the first breach saves with the plan unchanged.

Metric: ThermalModel.simulate_dhw_step calls made under _apply_dhw_min_run
(hooked, count) and its thread-CPU share of optimize(), per cell; weak slots,
accepted and refused (counted from the production decisions: plan[slot] after
the call); and the same with the early-exit arm, plus the shipped DHW plan's
sha in both arms.
Count key: calls delivered to ThermalModel.simulate_dhw_step and the
dhw_power_schedule the solve RETURNS.

Command:
  PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python \
      tools/audit/round9/D9/s1/dhw_min_run.py [--early-exit] [--hours 48]
Perturbations: --early-exit replaces the refused-slot check with a chunked
extension that stops at the first breach (same step function, same order):
calls must go DOWN, the plan sha must not change. --hours 48: calls UP
superlinearly (a suffix re-simulation per weak slot).
Baseline SHA 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine printed.
"""
from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

import argparse
import hashlib
import time

import numpy as np

import stress
from heatpump_optimizer.optimizer import HeatPumpOptimizer

PROD = HeatPumpOptimizer._apply_dhw_min_run
CHUNK = 8


def early_exit(self, plan, initial_temp, outdoor_temps, draw_rates, dt, p_dhw_max,
               min_run_power, max_temp, humidity=None):
    """Production _apply_dhw_min_run with ONE change: the per-slot candidate
    is extended CHUNK steps at a time and the slot is refused at the first
    chunk that breaches, instead of after the whole suffix."""
    plan = np.array(plan, dtype=float)
    weak = np.where((plan > 1e-6) & (plan < min_run_power))[0]
    if weak.size == 0:
        return np.clip(plan, 0.0, p_dhw_max)
    ceiling = np.asarray(max_temp, dtype=float)
    ceiling = np.concatenate([ceiling[:1], ceiling]) + 0.5

    def trajectory(schedule):
        return np.asarray(self.model.simulate_dhw_only(
            initial_temp=initial_temp, dhw_power_schedule=schedule,
            outdoor_temps=outdoor_temps, draw_rates=draw_rates, dt_hours=dt,
            humidity=humidity))
    run_power = min(min_run_power, p_dhw_max)
    base = trajectory(plan)
    joint = plan.copy()
    joint[weak] = run_power
    joint_temps = trajectory(joint)
    joint_limit = np.maximum(ceiling[: joint_temps.size], base[: joint_temps.size])
    if bool(np.all(joint_temps <= joint_limit + 1e-9)):
        return np.clip(joint, 0.0, p_dhw_max)
    n = plan.size
    for i in weak:
        slot = int(i)
        plan[slot] = run_power
        candidate = base.copy()
        ok = True
        pos = slot
        while pos < n:
            end = min(pos + CHUNK, n)
            self.model.extend_dhw_temps(candidate, pos, plan[:end], outdoor_temps,
                                        draw_rates, dt_hours=dt, humidity=humidity)
            lim = np.maximum(ceiling[pos + 1: end + 1], base[pos + 1: end + 1])
            if not bool(np.all(candidate[pos + 1: end + 1] <= lim + 1e-9)):
                ok = False
                break
            pos = end
        if ok:
            base = candidate
        else:
            plan[slot] = 0.0
            self.model.extend_dhw_temps(base, slot, plan, outdoor_temps, draw_rates,
                                        dt_hours=dt, humidity=humidity)
    return np.clip(plan, 0.0, p_dhw_max)


CELLS = {
    "single_zone_dhw_winter": dict(season="winter", dhw=True),
    "single_zone_dhw_winter_extreme": dict(season="winter_extreme", dhw=True),
    "single_zone_dhw_shoulder": dict(season="shoulder", dhw=True),
    "single_zone_dhw_summer": dict(season="summer", dhw=True),
    "two_zone_dhw_winter": dict(season="winter", two_zone=True, dhw=True),
    "single_zone_dhw_flat": dict(season="flat", dhw=True),  # null control
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--early-exit", action="store_true")
    ap.add_argument("--hours", type=int, default=24)
    args = ap.parse_args()
    impl = early_exit if args.early_exit else PROD
    st = {"in": 0, "calls": 0, "cpu": 0.0, "weak": 0, "acc": 0, "ref": 0}
    o_dhw = stress.SolverWork._dhw_step_wrapped

    def dstep(*a, **k):
        if st["in"]:
            st["calls"] += 1
        return o_dhw(*a, **k)

    def wrapped(self, plan, *a, **k):
        min_run = a[5] if len(a) > 5 else k["min_run_power"]
        p = np.asarray(plan, dtype=float)
        weak = np.where((p > 1e-6) & (p < min_run))[0]
        st["in"] += 1
        t0 = time.thread_time()
        try:
            out = impl(self, plan, *a, **k)
        finally:
            st["cpu"] += time.thread_time() - t0
            st["in"] -= 1
        st["weak"] += int(weak.size)
        st["acc"] += int(np.count_nonzero(out[weak] > 1e-6))
        st["ref"] += int(np.count_nonzero(out[weak] <= 1e-6))
        return out
    stress.SolverWork._dhw_step_wrapped = dstep
    HeatPumpOptimizer._apply_dhw_min_run = wrapped
    tf = 1.0
    shares = {}
    try:
        for cell, spec in CELLS.items():
            for key in st:
                st[key] = 0 if key != "cpu" else 0.0
            with C.Clock() as clk:
                run = stress.build_case(hours=args.hours, **spec)
            tf = max(tf, clk.thread_factor)
            solve = run["solve_thread_ms"] / 1000
            r = run["result"]
            dplan = np.asarray(getattr(r, "dhw_power_schedule", None) or [], dtype=float)
            splan = np.asarray(r.power_schedule, dtype=float)
            tag = f"{cell}_h{args.hours}" + ("_early" if args.early_exit else "")
            shares[cell] = st["cpu"] / solve
            C.result(f"{tag}.min_run_dhw_step_calls", st["calls"], "calls")
            C.result(f"{tag}.weak_slots", st["weak"], "count")
            C.result(f"{tag}.weak_accepted", st["acc"], "count")
            C.result(f"{tag}.weak_refused", st["ref"], "count")
            C.result(f"{tag}.min_run_share_of_solve", round(st["cpu"] / solve, 4), "ratio")
            C.result(f"{tag}.plan_sha", hashlib.sha1(dplan.tobytes() + splan.tobytes()).hexdigest()[:16])
    finally:
        stress.SolverWork._dhw_step_wrapped = o_dhw
        HeatPumpOptimizer._apply_dhw_min_run = PROD
    grid = sorted(v for k, v in shares.items() if k != "single_zone_dhw_flat")
    C.result("loo.cells", len(grid))
    C.result("loo.min", round(grid[0], 4))
    C.result("loo.max", round(grid[-1], 4))
    C.result("loo.mean", round(sum(grid) / len(grid), 4))
    C.result("loo.mean_drop_max", round(sum(grid[:-1]) / (len(grid) - 1), 4))
    C.trailer(tf)


if __name__ == "__main__":
    main()
