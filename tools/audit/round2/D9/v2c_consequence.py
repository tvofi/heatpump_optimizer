"""Verifier seat 2, panel D9: how wide the stall is, and the card's own pin.

Two consequence questions D9-05 and D9-01 leave open.

E. ``plain_thread_starvation_share`` -- the same 1 ms heartbeat, but on an
   ORDINARY Python thread rather than the asyncio loop, running beside the
   solve. Home Assistant's process carries several such threads (the
   recorder, integration workers, the executor pool's other slots). If the
   plain thread starves too, the defect is process-wide GIL starvation,
   not an event-loop scheduling artefact, and every Python thread in the
   instance is affected for the solve's duration. Definition: summed
   heartbeat gaps over 5 ms divided by the solve's wall time, measured on
   a ``threading.Thread`` doing ``time.sleep(0.001)``; the same idle
   control as h3.

F. ``card_shaped_pin`` -- the manual override the CARD produces, which is
   today's plan redrawn (docs/dashboard-card.md: the lanes start from the
   plan in force, blocks are dragged, not built from nothing). That leaves
   MOST steps pinned on and a FEW pinned off -- the expensive shape, since
   a pinned-on step keeps a live bound while a pinned-off step is the
   zero-range one. Contrast with a sparse override, which fixes most
   variables and is therefore cheaper. Definition: ``simulate_step`` calls
   in one production coordinator cycle.

Command (from the repository root):
    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=tests/hastub \
    python tools/audit/round2/D9/v2c_consequence.py

Expected (baseline c398fc8; E is wall and provisional, F is an exact count):
    idle_plain_thread.starvation_share      = 0
    two_zone_dhw.plain_thread_starvation    > 0.9
    card_shaped_pin.simulate_step_calls     >> the sparse override's

Perturbation (F): the same override with the gaps removed (space pinned on
for the whole window, no off step at all). The path returns to batched.

Instrumented symbols: optimizer:HeatPumpOptimizer.optimize (in a
ThreadPoolExecutor), optimizer:_multi_start_minimize,
thermal_model:ThermalModel.simulate_step.
Machine: Apple M1 8-core 8 GB (audit box).
"""
from __future__ import annotations

import asyncio
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round2", "D9"))
import d9lib  # noqa: E402

import numpy as np  # noqa: E402

from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer import optimizer as opt_mod  # noqa: E402
from heatpump_optimizer import thermal_model as tm_mod  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer.manual_plan import build_override  # noqa: E402

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
import homeassistant.util.dt as dt_util  # noqa: E402

START = datetime(2026, 1, 15, 0, 0)
stress = d9lib.load_stress_prefix()
build_case = stress["build_case"]


# ----------------------------------------------------------------------
# E. A plain thread's view of the same solve.
# ----------------------------------------------------------------------
def plain_thread_probe(label: str, work, idle_seconds: float | None = None):
    gaps: list[float] = []
    running = [True]

    def beat():
        last = time.perf_counter()
        while running[0]:
            time.sleep(0.001)
            now = time.perf_counter()
            gaps.append(now - last)
            last = now

    hb = threading.Thread(target=beat, daemon=True)
    hb.start()
    time.sleep(0.2)
    gaps.clear()
    pool = ThreadPoolExecutor(max_workers=1)
    t0 = time.perf_counter()
    if work is None:
        time.sleep(idle_seconds)
    else:
        pool.submit(work).result()
    wall = time.perf_counter() - t0
    running[0] = False
    hb.join(timeout=2.0)
    pool.shutdown(wait=True)
    g = np.asarray(gaps) * 1000.0
    over = g[g > 5.0]
    d9lib.result(f"{label}.wall", wall * 1000.0, "ms_provisional")
    d9lib.result(f"{label}.ticks_per_second", g.size / max(wall, 1e-9), "hz_provisional")
    d9lib.result(f"{label}.gap_p50", float(np.median(g)) if g.size else 0.0, "ms_provisional")
    d9lib.result(f"{label}.gap_p99", float(np.percentile(g, 99)) if g.size else 0.0, "ms_provisional")
    d9lib.result(f"{label}.longest_hold", float(g.max()) if g.size else 0.0, "ms_provisional")
    d9lib.result(f"{label}.plain_thread_starvation_share",
                 float(over.sum() / 1000.0 / max(wall, 1e-9)), "ratio_provisional")


def solver(run, **extra):
    def go():
        return run["optimizer"].optimize(
            run["initial"], run["prices"], run["outdoor"], run["wind"],
            run["rain"], run["solar"], START, None, run["surplus"], **extra)
    return go


plain_thread_probe("idle_plain_thread", None, idle_seconds=2.0)
_run_tz = build_case(season="winter", two_zone=True, dhw=True)
plain_thread_probe("two_zone_dhw_plain_thread", solver(_run_tz))
_p_max = float(_run_tz["params"].max_electrical_power)
plain_thread_probe(
    "dhw_cap_zero_range_plain_thread",
    solver(_run_tz, power_caps_extra=np.full(_run_tz["n"], 0.8 * _p_max)))


# ----------------------------------------------------------------------
# F. The card's own override shape.
# ----------------------------------------------------------------------
C: dict = {"solves": 0, "scalar_solves": 0, "zero": 0, "steps": 0}
_orig_multi = opt_mod._multi_start_minimize
_orig_step = tm_mod.ThermalModel.simulate_step


def hooked_multi(objective, candidates, bounds, *a, **k):
    C["solves"] += 1
    zero = sum(1 for lo, hi in bounds if lo >= hi)
    if zero:
        C["scalar_solves"] += 1
        C["zero"] += zero
    return _orig_multi(objective, candidates, bounds, *a, **k)


def hooked_step(self, *a, **k):
    C["steps"] += 1
    return _orig_step(self, *a, **k)


opt_mod._multi_start_minimize = hooked_multi
tm_mod.ThermalModel.simulate_step = hooked_step

BASE_CONFIG = {
    "tibber_token": "x", "weather_entity": "weather.home",
    "target_temperature": 21.0, "min_temperature": 17.0, "max_temperature": 23.0,
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    "dhw_tank_volume": 200.0, "dhw_setpoint": 55.0, "dhw_min_temperature": 45.0,
    "dhw_windows": "06:00-08:30, 17:00-22:00",
    "upper_floor_thermal_mass": 3.0, "lower_floor_thermal_mass": 8.0,
    "upper_floor_heat_loss": 0.08, "lower_floor_heat_loss": 0.07,
}


class LoopHass(FakeHass):
    def __init__(self, states=None):
        super().__init__(states)
        self.pool = ThreadPoolExecutor(max_workers=1)

    async def async_add_executor_job(self, func, *args):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self.pool, func, *args)


def cycle(label: str, space_slots):
    hass = LoopHass({"sensor.indoor": FakeState("21.4"),
                     "sensor.outdoor": FakeState("-3.0")})
    coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=dict(BASE_CONFIG)))
    coord._prices = [
        {"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
         "starts_at": (START + timedelta(hours=h)).isoformat(), "level": "NORMAL"}
        for h in range(48)]
    coord._weather_forecast = [
        {"datetime": (START + timedelta(hours=h)).isoformat(),
         "temperature": -5.0 + 3.0 * (h % 24) / 24.0, "wind_speed": 3.0,
         "precipitation": 0.0, "humidity": 85.0} for h in range(48)]
    coord._solar_radiation_forecast = [
        max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)]

    async def noop():
        return None

    coord._fetch_tibber_prices = noop
    coord._fetch_weather_forecast = noop
    coord._fetch_solar_forecast = noop
    when = START + timedelta(hours=8, minutes=3)
    coord._manual_override = build_override(
        space_slots=space_slots, dhw_slots=None,
        expires_at=when + timedelta(hours=20), now=when)
    loop = asyncio.new_event_loop()
    C.update(solves=0, scalar_solves=0, zero=0, steps=0)
    t0 = time.perf_counter()
    try:
        dt_util.freeze(when)
        coord.data = loop.run_until_complete(coord._async_update_data())
    finally:
        dt_util.freeze(None)
        loop.close()
        hass.pool.shutdown(wait=True)
    wall = (time.perf_counter() - t0) * 1000.0
    d9lib.result(f"{label}.solves", C["solves"], "count")
    d9lib.result(f"{label}.scalar_solves", C["scalar_solves"], "count")
    d9lib.result(f"{label}.zero_range_vars", C["zero"], "count")
    d9lib.result(f"{label}.simulate_step_calls", C["steps"], "count")
    d9lib.result(f"{label}.cycle_wall", wall, "ms_provisional")


def slot(h0: float, h1: float):
    return {"start": (START + timedelta(hours=h0)).isoformat(),
            "end": (START + timedelta(hours=h1)).isoformat()}


# The card shape: the whole editable window pinned on except two dropped
# peak hours -- what "move the heating out of the evening peak" produces.
cycle("card_shaped_pin", [slot(8.25, 17.0), slot(19.0, 28.25)])
# The perturbation: the same window with no gap at all -- no forced-off
# step anywhere, so no zero-range bound.
cycle("perturb_no_gap_all_on", [slot(8.25, 28.25)])
# For contrast, the sparse override measured in v2_reachability.
cycle("sparse_2h_only", [slot(18.0, 20.0)])

d9lib.closing(1.0)
