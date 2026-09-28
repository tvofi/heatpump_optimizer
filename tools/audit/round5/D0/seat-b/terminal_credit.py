#!/usr/bin/env python3
"""D0 seat b (round 5) -- terminal credit: does the plan move as documented?

Metric: per grid cell, comparing the shipped plan (production
`_terminal_cost`) with the plan from a neutralized terminal credit
(`_terminal_cost` patched to return identically-zero scalar and batch
closures -- a structure arm that removes only the end-of-horizon
valuation): (a) end-of-horizon room temperature drop room_end_prod -
room_end_zero (C); (b) mean planned space power over the last 8 steps
(kW); (c) comfort floor/ceiling violations over the last quarter of the
horizon (degree-steps); (d) reported savings share-of-bill delta (the
docstring claims neutral credit reports borrowed-heat savings). The
docstring at optimizer.py:_terminal_cost claims that WITHOUT the term
the optimizer "always dumps the last couple of hours" -- the harness
counts cells where the zero-credit plan dumps the tail (end room colder
by > 0.5 C) and cells where tail violations appear that production's
plan does not have.

Command (from the repository root):
  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  PYTHONPATH=tests/hastub python3 \
  tools/audit/round5/D0/seat-b/terminal_credit.py

Expected at baseline 1cc89e0 on the 8-core M1 audit box, Python 3.11
(load1 ~4.3, thread_factor 1.000), tolerance ±1 cell on the counts,
±0.3 C on the mean drop:
  RESULT term_cells_dumping_tail=7 unit=count   (of 8 cells)
  RESULT term_cells_new_tail_viol=6 unit=count
  RESULT term_cells_borrowed_savings=1 unit=count
  RESULT term_mean_end_room_drop=1.628 unit=C
Root rule: resolves the repository root from __file__.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(os.path.join(
    __file__, *[os.pardir] * 5)))
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.path.join(ROOT, "custom_components"))

import numpy as np
from unittest import mock

from profiles import prices, weather, house
from heatpump_optimizer.thermal_model import (
    ThermalModel, ThermalParameters, ThermalState)
from heatpump_optimizer import optimizer as optm
from heatpump_optimizer.optimizer import (
    HeatPumpOptimizer, OptimizationConfig)

PRICE_PROFILES = [
    "winter_typical", "winter_extreme", "winter_narrow", "winter_moderate",
    "shoulder", "summer_typical", "summer_negative", "flat",
]
START = datetime(2026, 1, 15)


def build_cell(price_p, weather_p="winter_cold"):
    cfg = house(two_zone=True)
    p = ThermalParameters.from_config(cfg)
    p.dhw_enabled = True
    m = ThermalModel(p)
    opt = HeatPumpOptimizer(m, OptimizationConfig(
        horizon_hours=24, time_step_minutes=15,
        target_temp=21.0, min_temp=17.0, max_temp=23.0))
    pr = prices(price_p, START)
    ot, wi, ra, so = weather(weather_p, START)
    st = ThermalState(
        room_temperature=21.0, slab_temperature=22.0,
        outdoor_temperature=float(ot[0]),
        upper_floor_temperature=21.0, lower_floor_temperature=21.0,
        buffer_tank_temperature=40.0, dhw_temperature=48.0)
    return opt, m, pr, ot, wi, ra, so, st


def zero_terminal_cost(self, prices, outdoor_temps, solar_gains=None):
    """Neutral replacement for `_terminal_cost`: identically zero."""
    def cost(*a, **k):
        return 0.0

    def cost_batch(rows):
        for v in rows.values():
            return np.zeros(np.asarray(v).shape[0])
        return np.zeros(0)

    return cost, cost_batch


class Cap:
    pass


def run(opt, m, st, pr, ot, wi, ra, so, cap, neutral):
    orig_swd = HeatPumpOptimizer._optimize_with_dhw
    orig_bdr = HeatPumpOptimizer._build_dhw_requirements

    def swd(self, h):
        cap.h = h
        return orig_swd(self, h)

    def bdr(*a, **kw):
        plan = orig_bdr(*a, **kw)
        cap.draw_rates = np.asarray(plan.draw_rates, dtype=float).copy()
        return plan

    patches = [mock.patch.object(HeatPumpOptimizer, "_optimize_with_dhw", swd),
               mock.patch.object(HeatPumpOptimizer, "_build_dhw_requirements", bdr)]
    if neutral:
        patches.append(mock.patch.object(
            HeatPumpOptimizer, "_terminal_cost", zero_terminal_cost))
    for p in patches:
        p.start()
    try:
        res = opt.optimize(st, pr, ot, wi, ra, so, START)
    finally:
        for p in patches:
            p.stop()
    return res


def tail_metrics(cap, m, res):
    h = cap.h
    n = h.n_steps
    space = np.asarray(res.power_schedule, dtype=float)
    dhw = np.asarray(res.dhw_power_schedule, dtype=float)
    traj = m.simulate_trajectory_with_dhw(
        initial_state=h.initial_state, space_power_schedule=space,
        dhw_power_schedule=dhw,
        outdoor_temps=h.outdoor_temps, wind_speeds=h.wind_speeds,
        precipitation=h.precipitation, solar_radiation=h.solar_radiation,
        start_hour=float(h.step_hours[0]), dt_hours=h.dt,
        dhw_draw_rates=cap.draw_rates, external_heat_kw=h.external_heat_kw,
        valve_targets=h.valve_targets, humidity=h.humidity)
    room, up, lo = traj[0], traj[2], traj[3]
    lo_b = np.asarray(h.temp_min_bounds[-n:], dtype=float)
    hi_b = np.asarray(h.temp_max_bounds[-n:], dtype=float)
    q = max(1, n // 4)
    viol_tail = 0.0
    for t in (room, up, lo):
        t = np.asarray(t, dtype=float)[-q:]
        lb, hb = lo_b[-q:], hi_b[-q:]
        viol_tail += float(np.maximum(0.0, lb - t).sum()
                           + np.maximum(0.0, t - hb).sum())
    return dict(
        room_end=float(room[-1]),
        tail_power=float(np.mean(space[-8:])),
        tail_viol=viol_tail,
        savings_share=float(res.predicted_savings)
        / max(abs(float(res.baseline_cost)), 1e-9),
    )


def main():
    rows = []
    t0 = time.time()
    for pp in PRICE_PROFILES:
        opt, m, pr, ot, wi, ra, so, st = build_cell(pp)
        cap = Cap()
        res_prod = run(opt, m, st, pr, ot, wi, ra, so, cap, neutral=False)
        t_prod = tail_metrics(cap, m, res_prod)
        res_zero = run(opt, m, st, pr, ot, wi, ra, so, cap, neutral=True)
        t_zero = tail_metrics(cap, m, res_zero)
        rows.append(dict(price=pp, prod=t_prod, zero=t_zero))
        print("%-18s room_end %6.2f -> %6.2f (%+.2f C)  tailP %5.2f -> %5.2f"
              "  tailviol %.3f -> %.3f  sav %% %.1f -> %.1f" % (
                  pp, t_prod["room_end"], t_zero["room_end"],
                  t_prod["room_end"] - t_zero["room_end"],
                  t_prod["tail_power"], t_zero["tail_power"],
                  t_prod["tail_viol"], t_zero["tail_viol"],
                  100 * t_prod["savings_share"],
                  100 * t_zero["savings_share"]), flush=True)

    dumps = [r for r in rows
             if r["prod"]["room_end"] - r["zero"]["room_end"] > 0.5]
    new_viol = [r for r in rows
                if r["zero"]["tail_viol"] > r["prod"]["tail_viol"] + 1e-6]
    sav_up = [r for r in rows
              if r["zero"]["savings_share"] > r["prod"]["savings_share"] + 1e-3]
    print("RESULT cells=%d" % len(rows))
    print("RESULT term_cells_dumping_tail=%d unit=count" % len(dumps))
    print("RESULT term_cells_new_tail_viol=%d unit=count" % len(new_viol))
    print("RESULT term_cells_borrowed_savings=%d unit=count" % len(sav_up))
    print("RESULT term_mean_end_room_drop=%.3f unit=C" % np.mean([
        r["prod"]["room_end"] - r["zero"]["room_end"] for r in rows]))
    print("RESULT elapsed_wall=%.1f unit=s" % (time.time() - t0))
    print("RESULT thread_factor=%.3f" % (
        time.process_time() / max(time.thread_time(), 1e-9)))
    print("RESULT load1=%.2f" % float(os.getloadavg()[0]))


if __name__ == "__main__":
    main()
