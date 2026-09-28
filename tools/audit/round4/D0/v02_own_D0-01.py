"""VERIFIER-0-2 OWN HARNESS for D0-01 (independent of d0lib.py).

METRIC (one line): fraction of grid cells in which rewriting ONLY
L-BFGS-B's ``ftol`` to 1e-14 -- intercepted at ``optimizer.py``'s imported
``scipy.optimize.minimize`` symbol, one level closer to scipy than the
finder's ``_scoped_minimize`` hook -- makes ``HeatPumpOptimizer.optimize``
return a plan whose production ``objective_value`` is strictly lower, plus
the median / mean / max relative drop, the top-5-dropped mean (a stronger
robust aggregate than the finder's leave-one-out), a bitwise identity
control (rewriting ftol to its own value 1e-6 must reproduce the unpatched
plan bit for bit), a direction control (ftol 1e-4 must not improve), a
starts-vs-restart decomposition (tight only in the 4 main starts vs only
inside ``_lbfgsb_restart``), and an independently re-simulated comfort
check (the returned schedules re-run through
``ThermalModel.simulate_trajectory_with_dhw`` here, not through the result
object's trajectories).

COMMAND (from the repository root):

    PYTHONPATH=tests/hastub \
      /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D0/v02_own_D0-01.py

BASELINE SHA the finding was measured at: 7dd68dd (optimizer.py unchanged
between that and this tree, 3e91f85: only manifest.json and the card moved).
MACHINE: 8-core Apple M1, 8 GB, macOS 25.6.0, numpy 2.4.6 / scipy 1.17.1.

CONTENTION: every RESULT is an objective value, a ratio of two objective
values, a schedule element, or a temperature -- deterministic arithmetic,
no wall/CPU/RSS claims.
"""
from __future__ import annotations

import os
import sys

# BLAS thread pin FIRST (harness contract).
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import subprocess  # noqa: E402
import time  # noqa: E402
from datetime import datetime  # noqa: E402
from unittest import mock  # noqa: E402

sys.path.insert(0, os.path.join(os.getcwd(), "tests"))
sys.path.insert(0, os.path.join(os.getcwd(), "custom_components"))

import numpy as np  # noqa: E402

from profiles import DT, house, prices, weather  # noqa: E402
from heatpump_optimizer import optimizer as O  # noqa: E402
from heatpump_optimizer.optimizer import (  # noqa: E402
    HeatPumpOptimizer, OptimizationConfig)
from heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel, ThermalParameters, ThermalState)

_real_minimize = O.minimize          # scipy symbol bound in optimizer's namespace
_real_restart = O._lbfgsb_restart

PRICED = ("winter_typical", "winter_extreme", "shoulder", "summer_negative")
WEATHERS = ("winter_cold", "summer_cool")
FLAT = "flat"
MIN_T = 17.0

#: arm state: ftol applied to the 4 main starts (None = no rewrite), and
#: where the RESTART call's ftol comes from: "all" (same as starts),
#: "starts" (restart keeps production 1e-6), "restart" (only the restart
#: is tightened, starts keep production).
_MODE = {"start_ftol": None, "where": "all"}


def _patched_minimize(fun, x0, *a, **kw):
    ft = _MODE["start_ftol"]
    if ft is not None:
        opts = dict(kw.get("options") or {})
        opts["ftol"] = ft
        kw["options"] = opts
    return _real_minimize(fun, x0, *a, **kw)


def _restart_wrapper(best, objective, bounds, args, maxiter, batch_objective,
                     fd_eps):
    saved = _MODE["start_ftol"]
    try:
        if _MODE["where"] == "starts":
            _MODE["start_ftol"] = None      # restart keeps production ftol
        elif _MODE["where"] == "restart":
            _MODE["start_ftol"] = 1e-14     # ONLY the restart is tightened
        return _real_restart(best, objective, bounds, args, maxiter,
                             batch_objective, fd_eps)
    finally:
        _MODE["start_ftol"] = saved


def solve_with(start_ftol, where, cell):
    """Run production optimize() with only ftol rewritten per arm."""
    _MODE["start_ftol"], _MODE["where"] = start_ftol, where
    try:
        with mock.patch.object(O, "minimize", _patched_minimize), \
                mock.patch.object(O, "_lbfgsb_restart", _restart_wrapper):
            return cell.opt.optimize(cell.st, cell.pr, cell.ot, cell.wi,
                                     cell.ra, cell.so, cell.start)
    finally:
        _MODE["start_ftol"], _MODE["where"] = None, "all"


class Cell:
    def __init__(self, price_p, weather_p, tz, start=datetime(2026, 1, 15)):
        cfg = house(two_zone=tz)
        p = ThermalParameters.from_config(cfg)
        p.dhw_enabled = True
        self.model = ThermalModel(p)
        self.opt = HeatPumpOptimizer(self.model, OptimizationConfig(
            horizon_hours=24, time_step_minutes=15,
            target_temp=21.0, min_temp=17.0, max_temp=23.0))
        self.pr = prices(price_p, start)
        self.ot, self.wi, self.ra, self.so = weather(weather_p, start)
        self.st = ThermalState(
            room_temperature=21.0, slab_temperature=22.0,
            outdoor_temperature=float(self.ot[0]),
            upper_floor_temperature=21.0, lower_floor_temperature=21.0,
            buffer_tank_temperature=40.0, dhw_temperature=50.0)
        self.start = start
        self.weather_p = weather_p
        self.tag = f"{price_p}/{weather_p}/tz{int(tz)}"

    def comfort_resim(self, result):
        """My OWN comfort check: re-simulate the returned schedules."""
        sp = np.asarray(result.power_schedule, dtype=float)
        dw = (np.asarray(result.dhw_power_schedule, dtype=float)
              if result.dhw_power_schedule is not None
              else np.zeros_like(sp))
        room, _, up, lo, _, _, _ = self.model.simulate_trajectory_with_dhw(
            initial_state=self.st, space_power_schedule=sp,
            dhw_power_schedule=dw,
            outdoor_temps=self.ot[:len(sp)], wind_speeds=self.wi[:len(sp)],
            precipitation=self.ra[:len(sp)],
            solar_radiation=self.so[:len(sp)],
            start_hour=self.start.hour + self.start.minute / 60.0,
            dt_hours=DT)
        worst = np.minimum(room, np.minimum(up, lo))[1:]
        return float(np.maximum(0.0, MIN_T - worst).sum()), float(worst.min())


def rel_gap(ja, jb):
    return (ja - jb) / abs(ja) * 100.0


def emit(name, value, unit=""):
    print(f"RESULT {name}={value} {unit}".rstrip())


def main() -> int:
    cpu0, thr0 = time.process_time(), time.thread_time()
    rows = []
    cells = []
    for pp in PRICED + (FLAT,):
        for wp in WEATHERS:
            for tz in (False, True):
                cells.append(Cell(pp, wp, tz))
    # phase-shifted attack cells: same price shape, the day starts 08:00
    cells.append(Cell("winter_typical", "winter_cold", True,
                      start=datetime(2026, 1, 15, 8, 0)))
    cells.append(Cell("summer_negative", "summer_cool", False,
                      start=datetime(2026, 1, 15, 8, 0)))

    for c in cells:
        base = solve_with(None, "all", c)
        ident = solve_with(1e-6, "all", c)
        tight = solve_with(1e-14, "all", c)
        jb, jt = float(base.objective_value), float(tight.objective_value)
        bitwise = bool(np.array_equal(
            np.asarray(base.power_schedule, dtype=float),
            np.asarray(ident.power_schedule, dtype=float)))
        va, _ = c.comfort_resim(base)
        vt, _ = c.comfort_resim(tight)
        row = {
            "tag": c.tag, "J": jb, "gap_tight": rel_gap(jb, jt),
            "bitwise_identity": bitwise,
            "dJ_ident": rel_gap(jb, float(ident.objective_value)),
            "viol_a": va, "viol_t": vt, "worst_arm_viol": max(va, vt),
            "p0d": abs(float(base.power_schedule[0])
                       - float(tight.power_schedule[0])),
            "sched_l1": float(np.abs(
                np.asarray(base.power_schedule, dtype=float)
                - np.asarray(tight.power_schedule, dtype=float)).sum()),
        }
        if c.weather_p == "winter_cold":  # decomposition on the wintry half
            row["gap_starts_only"] = rel_gap(
                jb, float(solve_with(1e-14, "starts", c).objective_value))
            row["gap_restart_only"] = rel_gap(
                jb, float(solve_with(None, "restart", c).objective_value))
            row["gap_loose_1e-4"] = rel_gap(
                jb, float(solve_with(1e-4, "all", c).objective_value))
        rows.append(row)
        extra = " ".join(
            f"{k}={row[k]:+.4f}%" for k in
            ("gap_starts_only", "gap_restart_only", "gap_loose_1e-4") if k in row)
        print(f"CELL {c.tag:42s} J={jb:.5f} tight={row['gap_tight']:+.4f}% "
              f"ident_bitwise={bitwise} viol {va:.4f}->{vt:.4f} "
              f"p0d={row['p0d']:.4f}kW {extra}", flush=True)

    priced = [r for r in rows if not r["tag"].startswith("flat")]
    flat = [r for r in rows if r["tag"].startswith("flat")]
    gp = sorted(r["gap_tight"] for r in priced)
    gf = [r["gap_tight"] for r in flat]
    dec = [r for r in rows if "gap_starts_only" in r]

    emit("cells_total", len(rows))
    emit("cells_priced", len(priced))
    emit("cells_improved_strictly_priced", sum(1 for g in gp if g > 1e-9))
    emit("cells_tight_worse_priced", sum(1 for g in gp if g < -1e-9))
    emit("median_gap_priced_pct", round(float(np.median(gp)), 6), "%")
    emit("mean_gap_priced_pct", round(float(np.mean(gp)), 6), "%")
    emit("max_gap_priced_pct", round(gp[-1], 6), "%")
    s = gp[:-5] if len(gp) > 5 else []
    emit("mean_gap_priced_top5_dropped_pct",
         round(float(np.mean(s)), 6) if s else float("nan"), "%")
    emit("mean_gap_flat_null_pct", round(float(np.mean(gf)), 6), "%")
    emit("max_gap_flat_null_pct", round(max(gf), 6), "%")
    emit("identity_control_bitwise_equal_cells",
         f"{sum(1 for r in rows if r['bitwise_identity'])} of {len(rows)}")
    emit("max_abs_dJ_identity_pct",
         round(max(abs(r["dJ_ident"]) for r in rows), 9), "%")
    emit("decomp_cells", len(dec))
    emit("mean_gap_starts_only_pct",
         round(float(np.mean([r["gap_starts_only"] for r in dec])), 6), "%")
    emit("mean_gap_restart_only_pct",
         round(float(np.mean([r["gap_restart_only"] for r in dec])), 6), "%")
    emit("mean_gap_loose_1e-4_pct",
         round(float(np.mean([r["gap_loose_1e-4"] for r in dec])), 6), "%")
    emit("max_gap_loose_1e-4_pct",
         round(max(r["gap_loose_1e-4"] for r in dec), 6), "%")
    emit("cells_tight_worse_comfort_resim",
         sum(1 for r in rows if r["viol_t"] > r["viol_a"] + 1e-6))
    emit("max_comfort_violation_either_arm",
         round(max(r["worst_arm_viol"] for r in rows), 6), "degree-steps")
    emit("cells_step0_differs_gt_0p01kW",
         sum(1 for r in priced if r["p0d"] > 0.01))
    emit("max_step0_delta_kW", round(max(r["p0d"] for r in priced), 6), "kW")
    emit("max_schedule_l1_kW",
         round(max(r["sched_l1"] for r in priced), 6), "kW")
    cpu, thr = time.process_time() - cpu0, time.thread_time() - thr0
    emit("thread_factor", round(cpu / thr if thr > 0 else float("nan"), 4))
    emit("load1", round(os.getloadavg()[0], 2))
    try:
        out = subprocess.run(["vm_stat"], capture_output=True, text=True,
                             timeout=10).stdout
        emit("swapins", next(int(l.split(":")[1].strip().rstrip("."))
                             for l in out.splitlines()
                             if l.strip().startswith("Swapins")))
    except Exception:
        emit("swapins", -1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
