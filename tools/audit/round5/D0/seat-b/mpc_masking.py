#!/usr/bin/env python3
"""D0 seat b (round 5) -- MPC masking: is an open-loop budget gap realised?

Metric: closed-loop 24 h race, tests/rolling.py:run_rolling shape (replan
every 2 h = 8 steps, plant == the optimizer's own model so the question
is purely whether re-planning absorbs the open-loop gap): realized
energy cost sum((space+dhw)*DT*price) in SEK/day and comfort violation
sum(max(0, floor - room))*DT in degree-hours, for the production policy
vs a challenger policy (L-BFGS-B options patched per `_scoped_minimize`,
e.g. ftol 1e-9 with the restart-adoption gate dropped). Also counts
replan instants where the two policies' step-0 actions differ by more
than 0.05 kW. If the challenger's open-loop objective gap does not
survive re-planning (realized cost and violation statistically equal),
the gap is MPC-masked and not a user-visible price defect.

Command (from the repository root):
  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  PYTHONPATH=tests/hastub python3 \
  tools/audit/round5/D0/seat-b/mpc_masking.py winter_typical winter_extreme

Expected at baseline 1cc89e0 on the 8-core M1 audit box, Python 3.11
(load1 ~4.0-7.1, thread_factor 1.000), tolerance ±0.15 SEK/day on the
deltas (re-planning path noise):
  CELL shoulder/winter_cold: delta -0.752 SEK/day (+1.281% of the
    58.71 SEK/day prod bill), viol delta 0.0000 dH, step0-differs 6/12
  RESULT mpc_cost_delta_winter_moderate=+2.943 (challenger WORSE
    closed-loop; the open-loop gain inverts under re-planning)
Root rule: resolves the repository root from __file__.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.abspath(os.path.join(
    __file__, *[os.pardir] * 5)))
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.path.join(ROOT, "custom_components"))

import numpy as np
from unittest import mock

from profiles import prices, weather, house, DT, N
from heatpump_optimizer.thermal_model import (
    ThermalModel, ThermalParameters, ThermalState)
from heatpump_optimizer import optimizer as optm
from heatpump_optimizer.optimizer import (
    HeatPumpOptimizer, OptimizationConfig)

START = datetime(2026, 1, 15, 0, 0)
REPLAN_STEPS = 8          # 2 h, as tests/rolling.py
HORIZON_STEPS = 96
DAY_STEPS = 96


def tile(series, steps):
    series = np.asarray(series, dtype=float)
    if len(series) >= steps:
        return series[:steps]
    return np.tile(series, int(np.ceil(steps / len(series))))[:steps]


def build(price_p, weather_p):
    cfg = house(two_zone=True)
    p = ThermalParameters.from_config(cfg)
    p.dhw_enabled = True
    m = ThermalModel(p)
    opt = HeatPumpOptimizer(m, OptimizationConfig(
        horizon_hours=24, time_step_minutes=15,
        target_temp=21.0, min_temp=17.0, max_temp=23.0))
    span = DAY_STEPS + HORIZON_STEPS + 4
    pr = tile(prices(price_p, START), span)
    w = weather(weather_p, START)
    ot, wi, ra, so = (tile(w[i], span) for i in range(4))
    state0 = ThermalState(
        room_temperature=21.0, slab_temperature=22.0,
        outdoor_temperature=float(ot[0]),
        upper_floor_temperature=21.0, lower_floor_temperature=21.0,
        dhw_temperature=52.0, dhw_hours_since_legionella=20.0,
        buffer_tank_temperature=40.0)
    return opt, m, pr, ot, wi, ra, so, state0


def solve(opt, st, pr, ot, wi, ra, so, now, arm):
    if arm is None:
        return opt.optimize(st, pr, ot, wi, ra, so, now)
    orig_sm = optm._scoped_minimize
    orig_keep = optm._LBFGSB_RESTART_KEEP_REL
    override = dict(maxiter=3000, maxfun=200000, ftol=1e-9, eps=1e-4)

    def sm(*a, **kw):
        kw = dict(kw)
        o = dict(kw.get("options") or {})
        o.update(override)
        kw["options"] = o
        return orig_sm(*a, **kw)

    with mock.patch.object(optm, "_scoped_minimize", sm), \
            mock.patch.object(optm, "_LBFGSB_RESTART_KEEP_REL", 1e-12):
        return opt.optimize(st, pr, ot, wi, ra, so, now)


def run_policy(opt, m, pr, ot, wi, ra, so, state0, arm):
    state = state0
    cost = 0.0
    viol_dh = 0.0
    p0s = []
    plan = None
    for step in range(DAY_STEPS):
        now = START + timedelta(hours=step * DT)
        if step % REPLAN_STEPS == 0:
            plan = solve(opt, state,
                         pr[step:step + HORIZON_STEPS],
                         ot[step:step + HORIZON_STEPS],
                         wi[step:step + HORIZON_STEPS],
                         ra[step:step + HORIZON_STEPS],
                         so[step:step + HORIZON_STEPS], now, arm)
            p0s.append(float(plan.power_schedule[0]))
        off = step % REPLAN_STEPS
        sp = float(plan.power_schedule[off])
        dp = float(plan.dhw_power_schedule[off]) \
            if plan.dhw_power_schedule else 0.0
        room, slab, upper, lower, tank, _, _ = m.simulate_trajectory_with_dhw(
            initial_state=state,
            space_power_schedule=np.array([sp]),
            dhw_power_schedule=np.array([dp]),
            outdoor_temps=ot[step:step + 1],
            wind_speeds=wi[step:step + 1],
            precipitation=ra[step:step + 1],
            solar_radiation=so[step:step + 1],
            start_hour=now.hour + now.minute / 60.0, dt_hours=DT)
        state = ThermalState(
            room_temperature=float(room[-1]),
            slab_temperature=float(slab[-1]),
            outdoor_temperature=float(ot[step]),
            upper_floor_temperature=float(upper[-1]),
            lower_floor_temperature=float(lower[-1]),
            dhw_temperature=float(tank[-1]),
            buffer_tank_temperature=state.buffer_tank_temperature,
            wood_tank_temperature=state.wood_tank_temperature,
            dhw_hours_since_legionella=(
                0.0 if float(tank[-1]) >= m.params.dhw_legionella_temp - 1.0
                else (state.dhw_hours_since_legionella or 0.0) + DT))
        cost += (sp + dp) * DT * float(pr[step])
        floor = 17.0
        room_now = min(float(upper[-1]), float(lower[-1]))
        viol_dh += max(0.0, floor - room_now) * DT
    return dict(cost=cost, viol=viol_dh, p0s=p0s,
                room_end=float(room[-1]))


def main():
    cells = sys.argv[1:] or ["winter_typical"]
    t0 = time.time()
    for cell in cells:
        price_p, weather_p = (cell.split(":") + ["winter_cold"])[:2]
        opt, m, pr, ot, wi, ra, so, state0 = build(price_p, weather_p)
        a = run_policy(opt, m, pr, ot, wi, ra, so, state0, None)
        b = run_policy(opt, m, pr, ot, wi, ra, so, state0, "deep")
        p0_diff = sum(1 for x, y in zip(a["p0s"], b["p0s"])
                      if abs(x - y) > 0.05)
        print("CELL %s/%s: prod cost %.2f SEK viol %.3f dH | deep cost %.2f "
              "SEK viol %.3f dH | cost delta %+.2f SEK/day "
              "(%+.3f%%) step0-differs %d/%d" % (
                  price_p, weather_p, a["cost"], a["viol"], b["cost"],
                  b["viol"], b["cost"] - a["cost"],
                  100 * (a["cost"] - b["cost"]) / max(a["cost"], 1e-9),
                  p0_diff, len(a["p0s"])), flush=True)
        print("RESULT mpc_cost_delta_%s=%+.3f unit=SEK_per_day" % (
            price_p, b["cost"] - a["cost"]))
        print("RESULT mpc_viol_delta_%s=%+.4f unit=degree_hours" % (
            price_p, b["viol"] - a["viol"]))
        print("RESULT mpc_step0_differs_%s=%d unit=count_of_%d" % (
            price_p, p0_diff, len(a["p0s"])))
    print("RESULT elapsed_wall=%.1f unit=s" % (time.time() - t0))
    print("RESULT thread_factor=%.3f" % (
        time.process_time() / max(time.thread_time(), 1e-9)))
    print("RESULT load1=%.2f" % float(os.getloadavg()[0]))


if __name__ == "__main__":
    main()
