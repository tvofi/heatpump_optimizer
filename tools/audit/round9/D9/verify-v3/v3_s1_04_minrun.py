"""D9 verify-v3 (round 9, lens V3) for D9-s1-04: DHW min-run repair steps
simulated PAST the step that already decided a refused slot's verdict.

Metric (one line): past_verdict_steps = sum over refused weak slots in
optimizer.HeatPumpOptimizer._apply_dhw_min_run of (steps the candidate check
simulated) - (index of its first ceiling breach + 1), counted from the arrays
ThermalModel.extend_dhw_temps actually returns; reported beside all
simulate_dhw_step calls of the solve, per stress.build_case cell.
Command:
  PYTHONPATH=tests/hastub /home/claude/venv/bin/python \
      tools/audit/round9/D9/verify-v3/v3_s1_04_minrun.py [--hours 48]
Instrumented symbols: HeatPumpOptimizer._apply_dhw_min_run (args captured),
ThermalModel.extend_dhw_temps and ThermalModel.simulate_dhw_step (counted).
Perturbation: --hours 48 -> past_verdict_steps UP (longer suffix per refusal).
Expected: past_verdict share of min-run steps 0.25-0.45 at 24 h; counts exact.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine printed.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _v3 as V  # noqa: E402
import argparse
import numpy as np
import stress
from heatpump_optimizer.optimizer import HeatPumpOptimizer
from heatpump_optimizer.thermal_model import ThermalModel

O_MR = HeatPumpOptimizer._apply_dhw_min_run
O_EXT = ThermalModel.extend_dhw_temps
O_STEP = ThermalModel.simulate_dhw_step
S = {}


def reset():
    S.update(inmr=0, ceiling=None, calls=[], steps_all=0, steps_mr=0)


def mr(self, plan, initial_temp, outdoor_temps, draw_rates, dt, p_dhw_max, min_run_power, max_temp, humidity=None):
    c = np.asarray(max_temp, float)
    S["ceiling"] = np.concatenate([c[:1], c]) + 0.5
    S["inmr"] += 1
    try:
        return O_MR(self, plan, initial_temp, outdoor_temps, draw_rates, dt, p_dhw_max, min_run_power, max_temp, humidity)
    finally:
        S["inmr"] -= 1


def ext(self, temps, from_step, *a, **k):
    if not S["inmr"]:
        return O_EXT(self, temps, from_step, *a, **k)
    pre = np.array(temps, float)
    out = O_EXT(self, temps, from_step, *a, **k)
    S["calls"].append((int(from_step), pre, np.array(out, float), S["ceiling"]))
    return out


def step(self, *a, **k):
    S["steps_all"] += 1
    if S["inmr"]:
        S["steps_mr"] += 1
    return O_STEP(self, *a, **k)


def analyse():
    """Walk the extend calls in order, applying production's own verdict rule
    (candidate[slot+1:] <= max(ceiling, base) + 1e-9) to each candidate; a
    refused candidate is followed by production's base refresh from the same
    slot, which is skipped (it is needed work, not verdict work)."""
    calls = S["calls"]; i = 0; refused = 0; accepted = 0; past = 0; cand = 0; refresh_ok = 0
    while i < len(calls):
        slot, pre, post, ceil = calls[i]
        simulated = post.size - 1 - slot
        cand += simulated
        limit = np.maximum(ceil[slot + 1: post.size], pre[slot + 1:])
        bad = np.where(post[slot + 1:] > limit + 1e-9)[0]
        if bad.size:
            refused += 1
            past += simulated - (int(bad[0]) + 1)
            if i + 1 < len(calls) and calls[i + 1][0] == slot:
                refresh_ok += 1
            i += 2
        else:
            accepted += 1; i += 1
    S["refresh_ok"] = refresh_ok
    return refused, accepted, past, cand


CELLS = {
    "single_zone_dhw_winter": dict(season="winter", two_zone=False, dhw=True),
    "single_zone_dhw_shoulder": dict(season="shoulder", two_zone=False, dhw=True),
    "single_zone_dhw_summer": dict(season="summer", two_zone=False, dhw=True),
    "two_zone_dhw_winter": dict(season="winter", two_zone=True, dhw=True),
    "single_zone_dhw_flat": dict(season="flat", two_zone=False, dhw=True),
}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--hours", type=int, default=24)
    a = ap.parse_args()
    HeatPumpOptimizer._apply_dhw_min_run = mr; ThermalModel.extend_dhw_temps = ext; ThermalModel.simulate_dhw_step = step
    o_sw = stress.SolverWork._dhw_step_wrapped; stress.SolverWork._dhw_step_wrapped = step  # SolverWork re-installs its counter over ours
    try:
        for cell, spec in CELLS.items():
            reset()
            stress.build_case(hours=a.hours, **spec)
            ref, acc, past, cand = analyse()
            t = f"{cell}_h{a.hours}"
            V.R(f"{t}.dhw_steps_solve", S["steps_all"], "count")
            V.R(f"{t}.dhw_steps_min_run", S["steps_mr"], "count")
            V.R(f"{t}.refused", ref, f"slots (refresh paired {S['refresh_ok']})"); V.R(f"{t}.accepted_loop", acc, "slots")
            V.R(f"{t}.past_verdict_steps", past, "steps (exact)")
            V.R(f"{t}.past_verdict_over_min_run", round(past / max(S['steps_mr'], 1), 4), "ratio")
    finally:
        HeatPumpOptimizer._apply_dhw_min_run = O_MR; ThermalModel.extend_dhw_temps = O_EXT; ThermalModel.simulate_dhw_step = O_STEP
        stress.SolverWork._dhw_step_wrapped = o_sw
    V.trailer()


if __name__ == "__main__":
    main()
