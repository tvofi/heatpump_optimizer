#!/usr/bin/env python
"""D2 harness -- the planning grid on the 23- and 25-hour DST days.

Metric: of the 96 planning steps the coordinator builds for a solve anchored at
local midnight, how many carry a price that is NOT the price in force at the real
instant t0 + i*15 min (steps_misaligned); the number of distinct real instants the
96 wall-clock step labels map to; the longest real gap between consecutive steps;
and the electrical energy the solved plan books in wall-clock steps that do not
exist (spring) or the power it holds across the 75-minute step (autumn).
Command:
  PYTHONPATH=tests/hastub python tools/audit/round2/D2/dst_grid.py
  PYTHONPATH=tests/hastub python tools/audit/round2/D2/dst_grid.py --perturb
(The harness sets HASTUB_TZ=Europe/Stockholm itself, before any import.)
Expected (c398fc84): plain day steps_misaligned = 0 (null control); six transition days
  (2025-2027) all 84;
  spring (2026-03-29) steps_misaligned = 84, distinct_instants = 92, span = 23 h;
  autumn (2026-10-25) steps_misaligned = 84, max_gap = 75 min, span = 25 h.
Perturbation (--perturb): HeatPumpOptimizerCoordinator._price_series builds step_starts
  by real (UTC) stepping instead of wall-clock timedelta: steps_misaligned -> 0 on
  both transition days (to_zero).
Instrumented: coordinator:HeatPumpOptimizerCoordinator._price_series (step_starts),
  coordinator:HeatPumpOptimizerCoordinator._forecast_arrays, optimizer:_Horizon.timestamps.
"""
import os
os.environ["HASTUB_TZ"] = "Europe/Stockholm"
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse
import resource
import sys
import time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np
_T_PROC0 = time.process_time()
_T_THR0 = time.thread_time()

from harness import FakeEntry, FakeHass
from homeassistant.util import dt as dt_util
from heatpump_optimizer import coordinator as coordmod
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
from heatpump_optimizer.coordinator import FORECAST_STEP_MINUTES
from heatpump_optimizer.price_model import extend_price_series
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
from profiles import house

ap = argparse.ArgumentParser()
ap.add_argument("--perturb", action="store_true")
args = ap.parse_args()

TZ = ZoneInfo("Europe/Stockholm")
UTC = timezone.utc
EPOCH = datetime(2026, 1, 1, tzinfo=UTC)


def price_for(instant: datetime) -> float:
    """A price that names the real hour: hours since 2026-01-01T00:00Z."""
    return float((instant.astimezone(UTC) - EPOCH).total_seconds() // 3600)


if args.perturb:
    def _price_series_utc(self, n_steps, midnight, step_offset):
        base = midnight.astimezone(UTC)
        step_starts = [
            (base + timedelta(minutes=FORECAST_STEP_MINUTES * (step_offset + i))).astimezone(midnight.tzinfo)
            for i in range(n_steps)
        ]
        known = self._known_prices_for(step_starts)
        prices, price_known, price_sigma = extend_price_series(known, n_steps, step_starts, self._price_prior())
        self._price_known_steps = int(np.sum(price_known))
        schedule = self._grid_fee_schedule()
        if schedule.active:
            prices = prices + self._fee_series(step_starts)
        return prices, price_known, price_sigma
    HeatPumpOptimizerCoordinator._price_series = _price_series_utc


def build_coord(day: datetime) -> HeatPumpOptimizerCoordinator:
    cfg = {"tibber_token": "x", "weather_entity": "weather.home", "target_temperature": 21.0,
           "min_temperature": 17.0, "max_temperature": 23.0}
    coord = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=cfg))
    start_utc = (day - timedelta(days=1)).astimezone(UTC)
    entries = []
    wx = []
    for h in range(72):
        t = (start_utc + timedelta(hours=h)).astimezone(TZ)  # real hourly walk, offset per entry like Tibber
        entries.append({"total": price_for(t), "starts_at": t.isoformat(), "level": "NORMAL"})
        wx.append({"datetime": t.isoformat(), "temperature": -3.0, "wind_speed": 3.0,
                   "precipitation": 0.0, "humidity": 80.0})
    coord._prices = entries
    coord._weather_forecast = wx
    coord._solar_radiation_forecast = [0.0] * 72
    return coord


def is_phantom(s: datetime) -> bool:
    """A wall-clock label that no real instant carries (the spring gap)."""
    back = s.astimezone(UTC).astimezone(TZ)
    return back.replace(tzinfo=None) != s.replace(tzinfo=None)


days = (("plain", datetime(2026, 8, 26, tzinfo=TZ)),
        ("spring", datetime(2026, 3, 29, tzinfo=TZ)),
        ("autumn", datetime(2026, 10, 25, tzinfo=TZ)),
        ("spring2025", datetime(2025, 3, 30, tzinfo=TZ)),
        ("autumn2025", datetime(2025, 10, 26, tzinfo=TZ)),
        ("spring2027", datetime(2027, 3, 28, tzinfo=TZ)),
        ("autumn2027", datetime(2027, 10, 31, tzinfo=TZ)))
mis = {}
for label, day in days:
    now = day.replace(hour=0, minute=7)
    dt_util.freeze(now)
    coord = build_coord(day)
    arrays = coord._forecast_arrays(now)
    prices = np.asarray(arrays[0], dtype=float)
    n = prices.size
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    # The labels _price_series stamps on the steps (wall-clock timedelta stepping).
    step_starts = [midnight + timedelta(minutes=FORECAST_STEP_MINUTES * i) for i in range(n)]
    instants = [s.astimezone(UTC) for s in step_starts]
    distinct = len(set(instants))
    gaps = [(instants[i + 1] - instants[i]).total_seconds() / 60.0 for i in range(n - 1)]
    span_h = ((instants[-1] - instants[0]).total_seconds() / 3600.0) + FORECAST_STEP_MINUTES / 60.0
    t0 = instants[0]
    real = [t0 + timedelta(minutes=FORECAST_STEP_MINUTES * i) for i in range(n)]
    expected_real = np.array([price_for(r) for r in real])
    expected_wall = np.array([price_for(s) for s in step_starts])
    mis_real = int(np.sum(prices != expected_real))
    mis_wall = int(np.sum(prices != expected_wall))
    phantom = [i for i, s in enumerate(step_starts) if is_phantom(s)]
    first_mis = int(np.argmax(prices != expected_real)) if mis_real else -1
    print(f"CELL {label}: n={n} distinct_instants={distinct} span_h={span_h:.2f} max_gap_min={max(gaps):.0f} "
          f"min_gap_min={min(gaps):.0f} misaligned_vs_real={mis_real} (first at step {first_mis}) "
          f"misaligned_vs_wall={mis_wall} phantom_steps={phantom}")
    print(f"RESULT dst_{label}_steps_misaligned={mis_real} count")
    print(f"RESULT dst_{label}_distinct_instants={distinct} count")
    print(f"RESULT dst_{label}_span_hours={span_h:.2f} h")
    print(f"RESULT dst_{label}_max_gap_min={max(gaps):.0f} min")
    print(f"RESULT dst_{label}_phantom_steps={len(phantom)} count")
    mis[label] = mis_real

    # The plan built on that grid: the production optimizer, anchored as the
    # coordinator anchors it (aware local datetime), on the coordinator's arrays.
    hcfg = house(two_zone=False, dhw=False)
    params = ThermalParameters.from_config(hcfg)
    params.dhw_enabled = False
    ocfg = OptimizationConfig(horizon_hours=24, time_step_minutes=15, target_temp=21.0, min_temp=17.0, max_temp=23.0)
    opt = HeatPumpOptimizer(ThermalModel(params), ocfg)
    state = ThermalState(room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=-3.0,
                         upper_floor_temperature=21.0, lower_floor_temperature=21.0,
                         dhw_temperature=50.0, buffer_tank_temperature=40.0)
    anchor = coord._solve_anchor(now)
    # A price shape with a night trough so the plan has a reason to heat at 02:00.
    hours = np.array([(s.hour + s.minute / 60.0) for s in step_starts])
    shaped = np.where((hours >= 0) & (hours < 5), 0.6, np.where((hours >= 16) & (hours < 20), 2.8, 1.1))
    res = opt.optimize(state, shaped, np.asarray(arrays[1]), np.asarray(arrays[2]),
                       np.asarray(arrays[3]), np.asarray(arrays[4]), anchor)
    ts = res.timestamps
    ph = [i for i, t in enumerate(ts) if is_phantom(t)]
    power = np.asarray(res.power_schedule)
    phantom_kwh = float(np.sum(power[ph]) * 0.25) if ph else 0.0
    total_kwh = float(np.sum(power) * 0.25)
    ts_utc = [t.astimezone(UTC) for t in ts]
    tgaps = [(ts_utc[i + 1] - ts_utc[i]).total_seconds() / 60.0 for i in range(len(ts) - 1)]
    gap_idx = int(np.argmax(tgaps))
    print(f"CELL {label} plan: phantom_steps={ph} phantom_kwh={phantom_kwh:.3f} total_kwh={total_kwh:.3f} "
          f"max_gap_min={max(tgaps):.0f} at step {gap_idx} power={power[gap_idx]:.3f} kW "
          f"timestamps_distinct={len(set(ts_utc))}")
    print(f"RESULT dst_{label}_plan_phantom_kwh={phantom_kwh:.3f} kWh")
    print(f"RESULT dst_{label}_plan_total_kwh={total_kwh:.3f} kWh")
    print(f"RESULT dst_{label}_plan_max_gap_min={max(tgaps):.0f} min")
    print(f"RESULT dst_{label}_plan_gap_step_power={power[gap_idx]:.3f} kW")
    dt_util.freeze(None)

trans = [v for k, v in mis.items() if k != "plain"]
print(f"RESULT dst_transition_cells={len(trans)} count")
print(f"RESULT dst_transition_steps_misaligned_min={min(trans)} count")
print(f"RESULT dst_transition_steps_misaligned_max={max(trans)} count")
print(f"RESULT dst_transition_steps_misaligned_drop_most_favourable={max(sorted(trans)[:-1]) if len(trans) > 1 else 0} count")
print(f"RESULT dst_null_control_plain={mis['plain']} count")

proc = time.process_time() - _T_PROC0
thr = time.thread_time() - _T_THR0
print(f"RESULT thread_factor={proc / max(thr, 1e-9):.3f} ratio")
print(f"RESULT load1={os.getloadavg()[0]:.2f} load")
print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap} count")
