#!/usr/bin/env python3
"""D0 seat b (round 5) -- DHW<->space decomposition iteration count.

Metric: per grid cell, the production objective gap
(1 - obj_iter/obj_prod)*100 % between the shipped plan (production's
single `_co_optimize` pass) and the plan an instrumented `_co_optimize`
that re-plans DHW against the solved space profile up to MAX_ITERS=6
rounds (fixed point or exhaustion) ships, both scored as
float(objective(space, dhw)) on the objective closure captured from the
production `_solve_space` seam. Feasibility parity: comfort floor/
ceiling violations of the iterated plan must not exceed production's
(+1e-6). Count of extra rounds that changed the plan is reported.

Command (from the repository root):
  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  PYTHONPATH=tests/hastub python3 \
  tools/audit/round5/D0/seat-b/decompose_iter.py

Expected at baseline 1cc89e0 on the 8-core M1 audit box, Python 3.11
(load1 ~5.5, thread_factor 1.000):
  RESULT iter_gap_max=+0.0000 unit=percent   (tolerance ±0.0001)
  RESULT iter_cells_changed=1 unit=count     (summer_negative only,
                                              objective-identical)
  RESULT iter_rounds_total=1 unit=count
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

MAX_ITERS = 6
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


class Cap:
    def __init__(self):
        self.h = None
        self.objective = None
        self.ms_args = ()
        self.draw_rates = None


def make_recorder(cap):
    orig_swd = HeatPumpOptimizer._optimize_with_dhw
    orig_ss = HeatPumpOptimizer._solve_space
    orig_bdr = HeatPumpOptimizer._build_dhw_requirements
    orig_ms = optm._multi_start_minimize

    def swd(self, h):
        cap.h = h
        return orig_swd(self, h)

    def ss(self, dhw_plan, warm_start, h, *a, **kw):
        return orig_ss(self, dhw_plan, warm_start, h, *a, **kw)

    def bdr(*a, **kw):
        plan = orig_bdr(*a, **kw)
        cap.draw_rates = np.asarray(plan.draw_rates, dtype=float).copy()
        return plan

    def ms(objective, candidates, bounds, args=(), maxiter=300,
           batch_objective=None, fd_eps=1e-4):
        res = orig_ms(objective, candidates, bounds, args, maxiter,
                      batch_objective, fd_eps)
        cap.objective = objective
        cap.ms_args = args
        return res

    ps = [mock.patch.object(HeatPumpOptimizer, "_optimize_with_dhw", swd),
          mock.patch.object(HeatPumpOptimizer, "_solve_space", ss),
          mock.patch.object(HeatPumpOptimizer, "_build_dhw_requirements", bdr),
          mock.patch.object(optm, "_multi_start_minimize", ms)]
    return ps


def iterated_co_optimize(orig_co):
    def co(self, h, *, space_power, dhw_power, status, best_score,
           solve_space, p_max):
        last_scores = {}

        def ss(dhw_plan, warm_start):
            r = solve_space(dhw_plan, warm_start)
            last_scores["score"] = r[2]
            return r

        cur_space, cur_dhw, cur_status = space_power, dhw_power, status
        cur_score = best_score
        rounds = 0
        for _ in range(MAX_ITERS):
            new_space, new_dhw, new_status = orig_co(
                self, h, space_power=cur_space, dhw_power=cur_dhw,
                status=cur_status, best_score=cur_score,
                solve_space=ss, p_max=p_max)
            if (np.allclose(new_space, cur_space, atol=1e-9)
                    and np.allclose(new_dhw, cur_dhw, atol=1e-9)):
                break
            if "score" in last_scores:
                cur_score = last_scores["score"]
            cur_space, cur_dhw, cur_status = new_space, new_dhw, new_status
            rounds += 1
        co.last_rounds = rounds
        return cur_space, cur_dhw, cur_status
    return co


def viol_of(cap, m, space, dhw):
    h = cap.h
    n = h.n_steps
    traj = m.simulate_trajectory_with_dhw(
        initial_state=h.initial_state, space_power_schedule=space,
        dhw_power_schedule=dhw,
        outdoor_temps=h.outdoor_temps, wind_speeds=h.wind_speeds,
        precipitation=h.precipitation, solar_radiation=h.solar_radiation,
        start_hour=float(h.step_hours[0]), dt_hours=h.dt,
        dhw_draw_rates=cap.draw_rates, external_heat_kw=h.external_heat_kw,
        valve_targets=h.valve_targets, humidity=h.humidity)
    lo_b = np.asarray(h.temp_min_bounds[-n:], dtype=float)
    hi_b = np.asarray(h.temp_max_bounds[-n:], dtype=float)
    tot = 0.0
    for t in (traj[0], traj[2], traj[3]):
        t = np.asarray(t, dtype=float)[-n:]
        tot += float(np.maximum(0.0, lo_b - t).sum()
                     + np.maximum(0.0, t - hi_b).sum())
    return tot


def main():
    rows = []
    t0 = time.time()
    for pp in PRICE_PROFILES:
        opt, m, pr, ot, wi, ra, so, st = build_cell(pp)
        cap = Cap()
        ps = make_recorder(cap)
        for p in ps:
            p.start()
        try:
            res_prod = opt.optimize(st, pr, ot, wi, ra, so, START)
            prod_space = np.asarray(res_prod.power_schedule, dtype=float)
            prod_dhw = np.asarray(res_prod.dhw_power_schedule, dtype=float)
            prod_obj = float(cap.objective(prod_space, *cap.ms_args))
            prod_viol = viol_of(cap, m, prod_space, prod_dhw)

            orig_co = HeatPumpOptimizer._co_optimize
            co = iterated_co_optimize(orig_co)
            with mock.patch.object(HeatPumpOptimizer, "_co_optimize", co):
                res_it = opt.optimize(st, pr, ot, wi, ra, so, START)
            it_space = np.asarray(res_it.power_schedule, dtype=float)
            it_dhw = np.asarray(res_it.dhw_power_schedule, dtype=float)
            # score both plans on the SAME closure (the iterated run's).
            it_obj = float(cap.objective(it_space, *cap.ms_args))
            prod_obj_same = float(cap.objective(prod_space, *cap.ms_args))
            it_viol = viol_of(cap, m, it_space, it_dhw)
            rounds = co.last_rounds
        finally:
            for p in ps:
                p.stop()
        gap = (prod_obj_same - it_obj) / max(abs(prod_obj_same), 1e-12) * 100.0
        feas = it_viol <= prod_viol + 1e-6
        p0_diff = abs(it_space[0] - prod_space[0])
        rows.append(dict(price=pp, gap=gap, feas=feas, rounds=rounds,
                         prod_obj=prod_obj_same, it_obj=it_obj,
                         prod_viol=prod_viol, it_viol=it_viol,
                         p0_diff=p0_diff))
        print("%-18s prod %9.3f iter %9.3f gap %+.4f%% rounds_extra %d "
              "viol %.4f->%.4f %s p0diff %.2f" % (
                  pp, prod_obj_same, it_obj, gap, rounds, prod_viol,
                  it_viol, "OK" if feas else "!INFEAS", p0_diff),
              flush=True)

    gaps = [r["gap"] if r["feas"] else 0.0 for r in rows]
    print("RESULT cells=%d" % len(rows))
    print("RESULT iter_gap_mean=%+.4f unit=percent" % np.mean(gaps))
    print("RESULT iter_gap_max=%+.4f unit=percent" % np.max(gaps))
    print("RESULT iter_cells_changed=%d unit=count" % sum(
        1 for r in rows if r["rounds"] > 0))
    print("RESULT iter_rounds_total=%d unit=count" % sum(
        r["rounds"] for r in rows))
    best = int(np.argmax(gaps))
    loo = [g for i, g in enumerate(gaps) if i != best]
    print("RESULT iter_gap_mean_loo=%+.4f unit=percent" % np.mean(loo))
    print("RESULT elapsed_wall=%.1f unit=s" % (time.time() - t0))
    print("RESULT thread_factor=%.3f" % (
        time.process_time() / max(time.thread_time(), 1e-9)))
    print("RESULT load1=%.2f" % float(os.getloadavg()[0]))


if __name__ == "__main__":
    main()
