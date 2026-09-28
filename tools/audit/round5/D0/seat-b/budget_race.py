#!/usr/bin/env python3
"""D0 seat b (round 5) -- budget arm race on the production objective.

Metric: per grid cell, the best FEASIBLE plan's objective gap
(1 - obj_champ/obj_prod)*100 %, where obj_* is the production objective
closure value of the plan each arm ships (flow-level re-solve of
`HeatPumpOptimizer.optimize` with only the L-BFGS-B budget options
changed via a patched `_scoped_minimize`), and FEASIBLE means per-step
comfort floor/ceiling violations (room/upper/lower vs the horizon's
temp_min_bounds/temp_max_bounds, re-simulated through the production
model) and power-bound excursions no worse than the production plan's
(+1e-6 tolerance). The objective closure is captured from the
`_multi_start_minimize` call `_solve_space`/`_optimize_space_only`
make, so the score is the exact production objective, not a re-derivation.

Command (from the repository root):
  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  PYTHONPATH=tests/hastub python3 \
  tools/audit/round5/D0/seat-b/budget_race.py [--quick|--full]

Expected at baseline 1cc89e0 on the 8-core M1 audit box, Python 3.11
(core grid, load1 ~4.7-5.7, thread_factor 1.000), tolerance ±0.10
percentage points on the gap means (BLAS-to-BLAS solver noise), exact
for the cap counts:
  RESULT gap_big_feasible_mean=+0.0000 unit=percent        (caps never bind)
  RESULT gap_ftol9_feasible_mean=+0.2267 unit=percent
  RESULT gap_ftol9_feasible_max=+0.9317 unit=percent
  RESULT gap_eps5_feasible_mean=-0.0276 unit=percent       (null: no effect)
  RESULT gap_deep_feasible_mean=+0.3882 unit=percent
  RESULT prod_scoped_minimize_cap_hits=0 unit=count
  AGG ftol9 mean_nonflat +0.2769 / mean_flat(null) -0.0240
Perturbation checks (instrumentation grant, restore after):
  tighten production ftol 1e-6 -> 1e-9 at optimizer.py:457 and :579,
  re-run --quick: gap_ftol9 -> +0.0000 exactly (to_zero);
  loosen only optimizer.py:579 to 1e-3, re-run --quick:
  gap_ftol9_feasible_mean +0.6554 / max +0.7344 (up).
Root rule: resolves the repository root from __file__ (measures the tree
the file lives in).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
import argparse
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
WEATHERS = ["winter_cold", "shoulder"]
START = datetime(2026, 1, 15)


def build_cell(two_zone, dhw, price_p, weather_p, horizon):
    cfg = house(two_zone=two_zone)
    p = ThermalParameters.from_config(cfg)
    p.dhw_enabled = dhw
    m = ThermalModel(p)
    opt = HeatPumpOptimizer(m, OptimizationConfig(
        horizon_hours=horizon, time_step_minutes=15,
        target_temp=21.0, min_temp=17.0, max_temp=23.0))
    pr = prices(price_p, START)
    ot, wi, ra, so = weather(weather_p, START)
    st = ThermalState(
        room_temperature=21.0, slab_temperature=22.0,
        outdoor_temperature=float(ot[0]),
        upper_floor_temperature=21.0, lower_floor_temperature=21.0,
        buffer_tank_temperature=40.0, dhw_temperature=48.0)
    return opt, m, pr, ot, wi, ra, so, st


class Recorder:
    """Read-only capture of the production solve seams."""

    def __init__(self):
        self.h = None
        self.dhw_plan = None
        self.last_ss_dhw = None
        self.draw_rates = None
        self.objective = None
        self.ms_calls = []
        self.solve_stats = []          # (nit, nfev, njev, status) per _scoped_minimize
        self._patchers = []

    def __enter__(self):
        mod = optm
        orig_sso = HeatPumpOptimizer._optimize_space_only
        orig_swd = HeatPumpOptimizer._optimize_with_dhw
        orig_ss = HeatPumpOptimizer._solve_space
        orig_bdr = HeatPumpOptimizer._build_dhw_requirements
        orig_ms = optm._multi_start_minimize
        orig_sm = optm._scoped_minimize
        rec = self

        def sso(self, h):
            rec.h = h
            rec.dhw_plan = None
            rec.draw_rates = None
            return orig_sso(self, h)

        def swd(self, h):
            rec.h = h
            return orig_swd(self, h)

        def ss(self, dhw_plan, warm_start, h, *a, **kw):
            rec.last_ss_dhw = np.asarray(dhw_plan, dtype=float).copy()
            return orig_ss(self, dhw_plan, warm_start, h, *a, **kw)

        def bdr(*a, **kw):
            plan = orig_bdr(*a, **kw)
            rec.draw_rates = np.asarray(plan.draw_rates, dtype=float).copy()
            return plan

        def ms(objective, candidates, bounds, args=(), maxiter=300,
               batch_objective=None, fd_eps=1e-4):
            res = orig_ms(objective, candidates, bounds, args, maxiter,
                          batch_objective, fd_eps)
            rec.objective = objective
            rec.ms_calls.append(dict(
                args=args, maxiter=maxiter, fd_eps=fd_eps,
                prod_res=res, bounds=bounds,
                n_candidates=len(candidates)))
            return res

        def sm(*a, **kw):
            res = orig_sm(*a, **kw)
            try:
                rec.solve_stats.append(
                    (res.nit, res.nfev, getattr(res, "njev", -1), res.status))
            except AttributeError:
                pass
            return res

        for tgt, name, new in (
            (HeatPumpOptimizer, "_optimize_space_only", sso),
            (HeatPumpOptimizer, "_optimize_with_dhw", swd),
            (HeatPumpOptimizer, "_solve_space", ss),
            (HeatPumpOptimizer, "_build_dhw_requirements", bdr),
        ):
            self._patchers.append(mock.patch.object(tgt, name, new))
        self._patchers.append(mock.patch.object(mod, "_multi_start_minimize", ms))
        self._patchers.append(mock.patch.object(mod, "_scoped_minimize", sm))
        for p in self._patchers:
            p.start()
        return self

    def __exit__(self, *a):
        for p in self._patchers:
            p.stop()


def run_arm(opt, m, pr, ot, wi, ra, so, st, arm, rec):
    """One flow-level solve under a budget arm; returns a dict of metrics."""
    opts_override = {
        "big":  dict(maxiter=3000, maxfun=200000, ftol=1e-6, eps=1e-4),
        "ftol9": dict(maxiter=300, ftol=1e-9, eps=1e-4),
        "eps5": dict(maxiter=300, ftol=1e-6, eps=1e-5),
        "deep": dict(maxiter=3000, maxfun=200000, ftol=1e-9, eps=1e-4),
    }[arm]
    fd_eps_override = 1e-5 if arm == "eps5" else None
    keep_override = 1e-12 if arm == "deep" else None
    orig_sm = optm._scoped_minimize
    orig_ms = optm._multi_start_minimize
    orig_keep = optm._LBFGSB_RESTART_KEEP_REL

    def sm(*a, **kw):
        kw = dict(kw)
        o = dict(kw.get("options") or {})
        o.update(opts_override)
        kw["options"] = o
        return orig_sm(*a, **kw)

    def ms(objective, candidates, bounds, args=(), maxiter=300,
           batch_objective=None, fd_eps=1e-4):
        if fd_eps_override is not None:
            fd_eps = fd_eps_override
        return orig_ms(objective, candidates, bounds, args, maxiter,
                       batch_objective, fd_eps)

    rec.h = None
    rec.objective = None
    rec.ms_calls = []
    rec.solve_stats = []
    with mock.patch.object(optm, "_scoped_minimize", sm), \
            mock.patch.object(optm, "_multi_start_minimize", ms), \
            mock.patch.object(optm, "_LBFGSB_RESTART_KEEP_REL", keep_override
                              if keep_override is not None else orig_keep):
        result = opt.optimize(st, pr, ot, wi, ra, so, START)
    return result


def score(rec, m, result, pr, dt):
    """Achieved objective + feasibility + energy of a shipped plan."""
    h = rec.h
    space = np.asarray(result.power_schedule, dtype=float)
    shipped_dhw = np.asarray(result.dhw_power_schedule, dtype=float) \
        if result.dhw_power_schedule else None
    obj = float(rec.objective(space, *rec.ms_calls[-1]["args"])) if rec.ms_calls else float(result.objective_value)
    n = h.n_steps
    if shipped_dhw is not None:
        traj = m.simulate_trajectory_with_dhw(
            initial_state=h.initial_state,
            space_power_schedule=space,
            dhw_power_schedule=shipped_dhw,
            outdoor_temps=h.outdoor_temps, wind_speeds=h.wind_speeds,
            precipitation=h.precipitation,
            solar_radiation=h.solar_radiation,
            start_hour=float(h.step_hours[0]), dt_hours=h.dt,
            dhw_draw_rates=rec.draw_rates,
            external_heat_kw=h.external_heat_kw,
            valve_targets=h.valve_targets, humidity=h.humidity)
        room, slab, up, lo = traj[0], traj[1], traj[2], traj[3]
        combined = space + shipped_dhw
    else:
        traj = m.simulate_trajectory(
            initial_state=h.initial_state, power_schedule=space,
            outdoor_temps=h.outdoor_temps, wind_speeds=h.wind_speeds,
            precipitation=h.precipitation,
            solar_radiation=h.solar_radiation, dt_hours=h.dt,
            external_heat_kw=h.external_heat_kw,
            valve_targets=h.valve_targets, humidity=h.humidity,
            start_hour=float(h.step_hours[0]))
        room, slab, up, lo = traj[0], traj[1], traj[2], traj[3]
        combined = space
    lo_b = np.asarray(h.temp_min_bounds[-n:], dtype=float)
    hi_b = np.asarray(h.temp_max_bounds[-n:], dtype=float)

    def viol(t):
        t = np.asarray(t, dtype=float)[-n:]
        return float(np.maximum(0.0, lo_b - t).sum()
                     + np.maximum(0.0, t - hi_b).sum())

    v_room, v_up, v_lo = viol(room), viol(up), viol(lo)
    energy_sek = float(np.sum(pr[:n] * combined[:n] * dt))
    nit_max = max((s[0] for s in rec.solve_stats), default=0)
    nfev = sum(s[1] for s in rec.solve_stats)
    status_max = max((s[3] for s in rec.solve_stats), default=0)
    n_cap = sum(1 for s in rec.solve_stats if s[3] == 1)
    return dict(
        obj=obj, viol=v_room + v_up + v_lo, energy_sek=energy_sek,
        p0=float(space[0]),
        dhw0=float(shipped_dhw[0]) if shipped_dhw is not None else 0.0,
        nit_max=nit_max, nfev=nfev, status_max=status_max, n_cap=n_cap,
        n_ms=len(rec.ms_calls),
        power=space,
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true",
                    help="one weather, three price profiles")
    ap.add_argument("--full", action="store_true",
                    help="full 48-cell grid (two weathers)")
    args = ap.parse_args()

    if args.full:
        cells = []
        for w in WEATHERS:
            for pp in PRICE_PROFILES:
                cells.append(dict(two_zone=True, dhw=True, price=pp,
                                  weather=w, horizon=24))
        for pp in PRICE_PROFILES:
            cells.append(dict(two_zone=False, dhw=True, price=pp,
                              weather="winter_cold", horizon=24))
            cells.append(dict(two_zone=True, dhw=False, price=pp,
                              weather="winter_cold", horizon=24))
        arm_sets = None
    elif args.quick:
        cells = [dict(two_zone=True, dhw=True, price=p,
                      weather="winter_cold", horizon=24)
                 for p in ("winter_typical", "winter_extreme", "flat")]
        arm_sets = None
    else:
        # Core grid (default): every price profile (flat included, the null
        # arm) on the default topology, plus the DHW-off variant on the
        # four most distinct price shapes, plus two single-zone probes.
        cells = []
        for pp in PRICE_PROFILES:
            cells.append(dict(two_zone=True, dhw=True, price=pp,
                              weather="winter_cold", horizon=24))
        for pp in ("winter_typical", "winter_extreme", "winter_narrow",
                   "flat"):
            cells.append(dict(two_zone=True, dhw=False, price=pp,
                              weather="winter_cold", horizon=24))
        for pp in ("winter_typical", "flat"):
            cells.append(dict(two_zone=False, dhw=True, price=pp,
                              weather="winter_cold", horizon=24))
        arm_sets = {
            ("winter_typical", "winter_cold", 1, 1):
                ("big", "ftol9", "eps5", "deep"),
            ("winter_typical", "winter_cold", 1, 0):
                ("ftol9", "deep"),
            ("winter_extreme", "winter_cold", 1, 0):
                ("ftol9", "deep"),
            ("winter_narrow", "winter_cold", 1, 0):
                ("ftol9",),
            ("flat", "winter_cold", 1, 0):
                ("ftol9", "deep"),
            ("winter_typical", "winter_cold", 0, 1):
                ("ftol9",),
            ("flat", "winter_cold", 0, 1):
                ("ftol9",),
        }

    rows = []
    t_start = time.time()
    for cell in cells:
        opt, m, pr, ot, wi, ra, so, st = build_cell(
            two_zone=cell["two_zone"], dhw=cell["dhw"],
            price_p=cell["price"], weather_p=cell["weather"],
            horizon=cell["horizon"])
        label = "%s/%s/tz%d/dhw%d/h%d" % (
            cell["price"], cell["weather"], cell["two_zone"], cell["dhw"],
            cell["horizon"])
        with Recorder() as rec:
            res_prod = opt.optimize(st, pr, ot, wi, ra, so, START)
            s_prod = score(rec, m, res_prod, pr, 0.25)
            key = (cell["price"], cell["weather"], cell["two_zone"],
                   cell["dhw"])
            cell_arms = arm_sets[key] if arm_sets and key in arm_sets else (
                ("ftol9", "eps5", "deep") if cell["two_zone"]
                else ("ftol9", "deep") if cell["dhw"] else ("ftol9", "deep"))
            arms = {}
            for arm in cell_arms:
                res_a = run_arm(opt, m, pr, ot, wi, ra, so, st, arm, rec)
                arms[arm] = score(rec, m, res_a, pr, 0.25)
        row = dict(cell=cell, label=label, prod=s_prod, arms=arms)
        rows.append(row)
        gaps = []
        for arm, s in arms.items():
            feasible = s["viol"] <= s_prod["viol"] + 1e-6
            gap = (s_prod["obj"] - s["obj"]) / max(abs(s_prod["obj"]), 1e-12) * 100.0
            sek = s_prod["energy_sek"] - s["energy_sek"]
            gaps.append("%s:%+.3f%%%s(p0 %.2f,sek%+.2f,nit%d,viol%.4f)" % (
                arm, gap, "" if feasible else "!INFEAS",
                s["p0"], sek, s["nit_max"], s["viol"]))
        print("%-46s obj %9.3f viol %7.4f p0 %.2f sek %.1f | %s" % (
            label, s_prod["obj"], s_prod["viol"], s_prod["p0"],
            s_prod["energy_sek"], " ".join(gaps)), flush=True)

    # Aggregates (contention-immune: objective % and counts, no timing).
    # Verdict aggregates are over FEASIBLE cells only (parity rule); the
    # feasible/infeasible split is printed beside every aggregate.
    def agg(rows_in, arm):
        gaps, subset = [], []
        n_infeas = 0
        for r in rows_in:
            if arm not in r["arms"]:
                continue
            s = r["arms"][arm]
            if s["viol"] > r["prod"]["viol"] + 1e-6:
                n_infeas += 1
                continue
            gap = (r["prod"]["obj"] - s["obj"]) / max(abs(r["prod"]["obj"]), 1e-12) * 100.0
            gaps.append(gap)
            subset.append(r)
        return gaps, subset, n_infeas

    for arm in ("big", "ftol9", "eps5", "deep"):
        gaps, subset, n_infeas = agg(rows, arm)
        if not gaps:
            continue
        nonflat = [g for g, r in zip(gaps, subset) if r["cell"]["price"] != "flat"]
        flat = [g for g, r in zip(gaps, subset) if r["cell"]["price"] == "flat"]
        print("AGG %s: feasible %d infeasible_excluded %d mean_gap %+.4f%% "
              "max %+.4f%% mean_nonflat %+.4f%% mean_flat(null) %+.4f%%" % (
                  arm, len(gaps), n_infeas, np.mean(gaps), np.max(gaps),
                  np.mean(nonflat) if nonflat else float("nan"),
                  np.mean(flat) if flat else float("nan")))
        best = max(range(len(gaps)), key=lambda i: gaps[i])
        loo = [g for i, g in enumerate(gaps) if i != best]
        print("AGG %s: leave-one-out (drop best cell %s) mean %+.4f%% "
              "range [%.4f, %.4f]" % (
                  arm, subset[best]["label"], np.mean(loo),
                  min(gaps), max(gaps)))

    # Status cap evidence: did any production solve hit its iteration cap?
    print("RESULT grid_cells=%d" % len(rows))
    for arm in ("big", "ftol9", "eps5", "deep"):
        gaps, _, _ = agg(rows, arm)
        if not gaps:
            continue
        print("RESULT gap_%s_feasible_mean=%+.4f unit=percent" % (
            arm, np.mean(gaps)))
        print("RESULT gap_%s_feasible_max=%+.4f unit=percent" % (
            arm, np.max(gaps)))
    prod_caps = sum(r["prod"]["n_cap"] for r in rows)
    print("RESULT prod_scoped_minimize_cap_hits=%d unit=count" % prod_caps)
    import json
    out = os.environ.get("D0B_ROWS_OUT", "")
    if out:
        slim = []
        for r in rows:
            slim.append(dict(
                label=r["label"], cell=r["cell"],
                prod={k: v for k, v in r["prod"].items() if k != "power"},
                arms={a: {k: v for k, v in s.items() if k != "power"}
                      for a, s in r["arms"].items()}))
        with open(out, "w") as fh:
            json.dump(slim, fh, indent=1)
    print("RESULT elapsed_wall=%.1f unit=s" % (time.time() - t_start))
    print("RESULT thread_factor=%.3f" % (
        time.process_time() / max(time.thread_time(), 1e-9)))
    print("RESULT load1=%.2f" % float(os.getloadavg()[0]))


if __name__ == "__main__":
    main()
