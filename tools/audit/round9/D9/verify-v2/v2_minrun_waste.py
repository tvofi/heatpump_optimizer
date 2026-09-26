"""V2 (independent) check of D9-s1-04: work past the verdict in
optimizer.HeatPumpOptimizer._apply_dhw_min_run.

Metric (own definition): of the DHW steps that ThermalModel.extend_dhw_temps
simulates while the PRODUCTION _apply_dhw_min_run runs, the fraction simulated
AFTER the step at which a refused slot's candidate first breaches its limit
(max(ceiling + 0.5, base)) -- i.e. steps whose outcome cannot change the
production decision. Computed from the production call itself: each
extend_dhw_temps call is recorded (start, array before, array after); the
candidate extension of a slot is the call on a copy of base; a slot is
refused when production leaves plan[slot] == 0; the first breach is read off
the recorded candidate against the recorded base. Nothing is re-implemented.
Also: steps per weak slot vs horizon (--hours 48), and the share of the
solve's simulate_dhw_step calls that fall inside _apply_dhw_min_run.
Count key: steps delivered by extend_dhw_temps (schedule.size - from_step)
and calls delivered to ThermalModel.simulate_dhw_step.

Command (repo root):
  PYTHONPATH=tests/hastub /home/claude/venv/bin/python \
      tools/audit/round9/D9/verify-v2/v2_minrun_waste.py [--hours 48]
Perturbation: --hours 48 (post-verdict steps UP more than 2x); null cell:
single_zone_dhw_flat (flat prices).
Expected (1936d5ca): a post-verdict fraction well above 0 on single-zone
winter cells (exact counts).
Machine: x86_64 4-core Linux container, CPython 3.14.0rc2, OpenBLAS pinned 1.
"""
from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _v2 as V  # noqa: E402

import argparse
import inspect

import numpy as np

import stress
from heatpump_optimizer.optimizer import HeatPumpOptimizer
from heatpump_optimizer.thermal_model import ThermalModel

PROD = HeatPumpOptimizer._apply_dhw_min_run
ORIG_EXT = ThermalModel.extend_dhw_temps
ORIG_STEP = stress.SolverWork._dhw_step_wrapped
S = {"in": 0, "rec": None, "calls_in": 0, "calls_all": 0}


ORIG_ONLY = ThermalModel.simulate_dhw_only


def only(self, *a, **k):
    S["nested"] = S.get("nested", 0) + 1
    try:
        return ORIG_ONLY(self, *a, **k)
    finally:
        S["nested"] -= 1


def ext(self, temps, from_step, sched, *a, **k):
    if S.get("nested"):
        return ORIG_EXT(self, temps, from_step, sched, *a, **k)
    before = np.array(temps, dtype=float)
    out = ORIG_EXT(self, temps, from_step, sched, *a, **k)
    if S["in"] and S["rec"] is not None:
        S["rec"].append((int(from_step), int(np.asarray(sched).size), before, np.array(temps, float)))
    return out


def dstep(*a, **k):
    S["calls_all"] += 1
    if S["in"]:
        S["calls_in"] += 1
    return ORIG_STEP(*a, **k)


TOT = {"steps": 0, "post": 0, "refused": 0, "weak": 0, "min_run_calls": 0}


SIG = inspect.signature(PROD)


def wrapped(self, *a, **k):
    b = SIG.bind(self, *a, **k)
    b.apply_defaults()
    plan, min_run, max_temp = b.arguments["plan"], b.arguments["min_run_power"], b.arguments["max_temp"]
    p = np.asarray(plan, float)
    weak = [int(i) for i in np.where((p > 1e-6) & (p < min_run))[0]]
    S["rec"] = []
    S["in"] += 1
    try:
        out = PROD(self, *a, **k)
    finally:
        S["in"] -= 1
    recs, S["rec"] = S["rec"], None
    ceiling = np.asarray(max_temp, float)
    ceiling = np.concatenate([ceiling[:1], ceiling]) + 0.5
    TOT["weak"] += len(weak)
    # production order: per weak slot, one candidate extension, then (if
    # refused) one base re-extension from the same slot.
    it = iter(recs)
    if not recs:  # the joint raise was accepted: no per-slot loop ran
        weak = []
    for slot in weak:
        start, size, base, cand = next(it)
        assert start == slot
        steps = size - start
        TOT["steps"] += steps
        if out[slot] <= 1e-6:  # refused by production
            TOT["refused"] += 1
            lim = np.maximum(ceiling[slot + 1: cand.size], base[slot + 1: cand.size])
            bad = np.nonzero(cand[slot + 1:] > lim + 1e-9)[0]
            first = int(bad[0]) + 1 if bad.size else steps  # steps needed to see the breach
            TOT["post"] += steps - first
            s2, size2, _b, _c = next(it)  # the base refresh
            TOT["steps"] += size2 - s2
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hours", type=int, default=24)
    args = ap.parse_args()
    cells = {
        "single_zone_dhw_winter": dict(season="winter", dhw=True),
        "single_zone_dhw_summer": dict(season="summer", dhw=True),
        "single_zone_dhw_shoulder": dict(season="shoulder", dhw=True),
        "two_zone_dhw_winter": dict(season="winter", two_zone=True, dhw=True),
        "single_zone_dhw_flat": dict(season="flat", dhw=True),  # null: flat prices
    }
    ThermalModel.extend_dhw_temps = ext
    ThermalModel.simulate_dhw_only = only
    stress.SolverWork._dhw_step_wrapped = dstep
    HeatPumpOptimizer._apply_dhw_min_run = wrapped
    try:
        for cell, spec in cells.items():
            for k in TOT:
                TOT[k] = 0
            S["calls_in"] = S["calls_all"] = 0
            stress.build_case(hours=args.hours, **spec)
            tag = f"{cell}_h{args.hours}"
            V.result(f"{tag}.weak_slots", TOT["weak"], "count")
            V.result(f"{tag}.refused", TOT["refused"], "count")
            V.result(f"{tag}.extend_steps_in_min_run", TOT["steps"], "steps")
            V.result(f"{tag}.post_verdict_steps", TOT["post"], "steps")
            V.result(f"{tag}.post_verdict_fraction", round(TOT["post"] / max(TOT["steps"], 1), 4), "ratio (exact)")
            V.result(f"{tag}.min_run_dhw_step_calls", S["calls_in"], "count")
            V.result(f"{tag}.min_run_share_of_solve_dhw_step_calls",
                     round(S["calls_in"] / max(S["calls_all"], 1), 4), "ratio (exact)")
    finally:
        ThermalModel.extend_dhw_temps = ORIG_EXT
        ThermalModel.simulate_dhw_only = ORIG_ONLY
        stress.SolverWork._dhw_step_wrapped = ORIG_STEP
        HeatPumpOptimizer._apply_dhw_min_run = PROD
    V.trailer()


if __name__ == "__main__":
    main()
