"""Reviewer's own equivalence check for PR #2026 (not the fixer's harness).

Compares the MERGE-BASE script's per-arm ``run`` (every arm from its own
freshly built coordinator, the pre-fix semantics) with the HEAD script's
``replay`` (shared prefix + deepcopy fork), on every assertion input that
``check_arm`` / ``check_record`` read: daily, daily_bias, folds_frozen,
folds_outside, folds_after, hh_final, alarmed, tagged/untagged samples
(as_dict, full lists).

Modes:
  stub   full 9-day schedule, real fork (254), with HeatPumpOptimizer.optimize
         replaced by a cheap state-dependent controller that reads the LIVE
         learned model (so any hidden-state loss in the deepcopy propagates).
         Also fingerprints every solve's inputs (time, state, learned params)
         per arm to locate the first cycle the arms diverge at the base.
  real   real production solves, short schedule with a 7-cycle prefix that
         includes a 03:00 heartbeat.
  stub-control  stub mode with the head forked one cycle late (255): must DIFFER.
"""
from __future__ import annotations

import hashlib
import importlib.util
import sys
from datetime import timedelta

import numpy as np

import boost_drift_replay as head
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationResult

spec = importlib.util.spec_from_file_location(
    "bdr_base", "/Users/timmalmstrom/hpo-seats/r9c-rev-2026-r2-ev/bdr_base.py")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

REAL_OPT = HeatPumpOptimizer.optimize
TRACE: list = []


def fp(obj) -> str:
    d = {k: v for k, v in sorted(vars(obj).items())}
    return hashlib.sha1(repr(d).encode()).hexdigest()[:12]


def stub_optimize(self, *, inputs):
    st = inputs.state
    f = inputs.forecast
    prices = np.asarray(f.prices, dtype=float)
    outs = np.asarray(f.outdoor_temps, dtype=float)
    sol = (np.zeros_like(prices) if f.solar_radiation is None
           else np.asarray(f.solar_radiation, dtype=float))
    n = len(prices)
    TRACE.append((inputs.start_time, fp(st), fp(self.model.params)))
    p = []
    temps = [st.room_temperature]
    s = st
    for k in range(n):
        err = 21.0 - s.room_temperature
        pk = float(np.clip(2.0 + 3.0 * err + 0.8 * (1.4 - prices[k]), 0.0, 6.0))
        p.append(pk)
        if k < 6:  # a short predicted trajectory through the LEARNED model
            s = self.model.simulate_step(
                s, pk, float(outs[k]), wind_speed=2.0, precipitation=0.0,
                solar_radiation=float(sol[k]), dt_hours=0.5)
            temps.append(s.room_temperature)
        else:
            temps.append(temps[-1])
    t0 = inputs.start_time
    return OptimizationResult(
        power_schedule=p, room_temp_trajectory=temps[1:],
        slab_temp_trajectory=temps[1:],
        timestamps=[t0 + timedelta(minutes=30 * k) for k in range(n)],
        prices=list(prices), predicted_cost=float(np.dot(p, prices) * 0.5),
        baseline_cost=1.0, predicted_savings=0.0, savings_percentage=0.0,
        optimal_setpoints=[21.0] * n, status="optimal",
        outdoor_temps=list(outs), heat_pump_on_schedule=[x > 0.05 for x in p],
        displace_schedule=[0.0] * n,
    )


def comparable(out: dict) -> dict:
    return {k: ([s.as_dict() for s in v] if k in ("tagged", "untagged") else v)
            for k, v in out.items()}


ARMS = {"null_no_boost": "none", "channel_boost": "channel", "mode_boost": "mode"}
TZ = {"two_zone_boost": "channel", "two_zone_null": "none"}


def run_base(arms, two_zone=False):
    outs, traces = {}, {}
    for a, s in arms.items():
        TRACE.clear()
        outs[a] = base.run(a, s, two_zone=two_zone)
        traces[a] = list(TRACE)
    return outs, traces


def diff_fields(x, y):
    cx, cy = comparable(x), comparable(y)
    return [k for k in sorted(set(cx) | set(cy)) if cx.get(k) != cy.get(k)]


def main() -> int:
    mode = sys.argv[1]
    if mode.startswith("stub"):
        HeatPumpOptimizer.optimize = stub_optimize
    else:
        for m in (head, base):
            m.DAYS = 12 * m.DT_MIN / (24 * 60)
            m.BOOST_DAYS = (0,)
            m.BOOST_STARTS = (3.5,)
    fork = head.fork_cycle() + (1 if mode == "stub-control" else 0)
    print(f"RESULT mode={mode} fork_cycle={head.fork_cycle()} fork_used={fork} "
          f"n_cycles={int(head.DAYS * 48)}")
    ok = True
    groups = [(ARMS, False)] + ([(TZ, True)] if mode.startswith("stub") else [])
    for arms, tz in groups:
        b_out, b_tr = run_base(arms, two_zone=tz)
        h_out = head.replay(arms, two_zone=tz, fork=fork)
        for a in arms:
            d = diff_fields(b_out[a], h_out[a])
            n_s = len(b_out[a]["tagged"]) + len(b_out[a]["untagged"])
            print(f"RESULT {mode} {a}: samples={n_s} tagged={len(b_out[a]['tagged'])} "
                  f"folds_outside={b_out[a]['folds_outside']} "
                  f"folds_frozen={b_out[a]['folds_frozen']} folds_after={b_out[a]['folds_after']} "
                  f"hh_final={b_out[a]['hh_final']} "
                  f"{'EQUAL' if not d else 'DIFFERENT ' + ','.join(d)}")
            ok = ok and not d
        if mode == "stub" and not tz:
            ref = b_tr["null_no_boost"]
            for a in ("channel_boost", "mode_boost"):
                tr = b_tr[a]
                first = next((i for i, (x, y) in enumerate(zip(ref, tr)) if x != y), None)
                print(f"RESULT base divergence {a} vs null_no_boost: solve inputs "
                      f"identical for cycles 0..{(first - 1) if first is not None else len(tr) - 1}"
                      f", first differing solve cycle={first} of {len(tr)}")
    print(f"RESULT {mode} {'ALL EQUAL' if ok else 'DIFFERS'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
