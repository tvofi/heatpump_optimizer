#!/usr/bin/env python3
"""R10-LIVE-AWAY-HEATING: does away mode plan space heating at indoor 22 C?

WHY IT EXISTS. The owner (2026-10-30, a Friday): "Turning away mode on still
leaves plenty of heating slots in the plan, even though indoor temperature is
already 22 degrees and i also lowered the set point to 18."

Every arm builds the solve the way ``coordinator._solve_hubs`` does: the
configured ``OptimizationConfig.from_mapping``, then ``away.solve_bands``
(production) over it with an ``AwayState`` as ``away.resolve`` leaves it, the
bands replaced into a copy, and ``HeatPumpOptimizer.optimize``. The thermostat
set point is ``target_temp`` (``coordinator.async_set_target_temperature``
writes only that field). A 48 h horizon from Friday 12:00 crosses into Saturday.

Arms (one RESULT line each: space slots > 0.1 kW, kWh, first/last slot, DHW
slots and kWh, room min/max):

  away           away on, set point 18, indoor 22, two winter_typical days
  null_away_off  away off, set point 18, indoor 22 (null control 1)
  away_off_setpoint21  away off at set point 21: does the set point move the plan?
  null_flat      away on, flat price (null control 2)
  indoor18       away on, indoor 18 (stale-reading vs wrong-target split)
  weekend        away on, a configured weekend comfort schedule (21/19.5)
  weekend_flat   the same at a flat price
  holiday        away on, a holiday calendar covering Saturday with 21/19.5
  recovery       away with recovery_active (return inside the estimate)

    PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_live_away_heating.py
"""
from __future__ import annotations

import copy
from dataclasses import replace
from datetime import datetime, timedelta

import numpy as np

from profiles import house, prices, solve_inputs, weather
from heatpump_optimizer import away as away_mode
from heatpump_optimizer.entry_config import EntryConfig
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState

START = datetime(2026, 10, 30, 12, 0)  # Friday, the report's day
SLOT_KW = 0.1


def _two_days(fn, profile):
    a = fn(profile, START)
    b = fn(profile, START + timedelta(hours=24))
    if isinstance(a, tuple):
        return tuple(np.concatenate([x, y]) for x, y in zip(a, b))
    return np.concatenate([a, b])


def _config(setpoint: float, **over) -> tuple[OptimizationConfig, ThermalParameters]:
    cfg = house(two_zone=False, dhw=True, target_temperature=setpoint, **over)
    opt = OptimizationConfig.from_mapping(EntryConfig.from_mapping(cfg))
    opt = replace(opt, horizon_hours=48, time_step_minutes=15)
    return opt, ThermalParameters.from_config(cfg)


def _away(active: bool, recovery: bool = False) -> away_mode.AwayState:
    cfg = away_mode.config_from_mapping({})
    if not active:
        return away_mode.AwayState()
    return away_mode.AwayState(
        active=True, source="service", recovery_active=recovery,
        target_temperature=21.0 if recovery else cfg.away_temperature,
        dhw_min_temperature=cfg.away_dhw_min_temperature,
    )


def run(name: str, *, active=True, setpoint=18.0, indoor=22.0, flat=False,
        recovery=False, holiday=False, **over) -> dict:
    opt_cfg, params = _config(setpoint, **over)
    if holiday:
        opt_cfg = replace(opt_cfg, holiday_dates=frozenset({(START + timedelta(days=1)).date()}),
                          holiday_comfort_day=21.0, holiday_comfort_night=19.5)
    bands, dhw = away_mode.solve_bands(opt_cfg, params, _away(active, recovery))
    config = replace(copy.deepcopy(opt_cfg), **bands)
    params = replace(copy.deepcopy(params), **dhw)
    model = ThermalModel(params)
    o, w, r, s = _two_days(weather, "shoulder")
    o = o - 4.0  # late-October Swedish, about 2 C mean
    pr = np.full(o.size, 1.2) if flat else _two_days(prices, "winter_typical")
    st = ThermalState(
        room_temperature=indoor, slab_temperature=indoor + 0.5, outdoor_temperature=float(o[0]),
        upper_floor_temperature=indoor, lower_floor_temperature=indoor,
        dhw_temperature=50.0, dhw_hours_since_legionella=20.0, buffer_tank_temperature=35.0,
    )
    res = HeatPumpOptimizer(model, config).optimize(inputs=solve_inputs(
        initial_state=st, prices=pr, outdoor_temps=o, wind_speeds=w, precipitation=r,
        solar_radiation=s, start_time=START))
    sp = np.asarray(res.power_schedule, float)
    dh = np.asarray(res.dhw_power_schedule or [0.0] * sp.size, float)
    on = np.flatnonzero(sp > SLOT_KW)
    ts = res.timestamps
    room = np.asarray(res.room_temp_trajectory, float)
    out = {
        "arm": name, "space_slots": int(on.size), "space_kwh": round(float(sp.sum() * 0.25), 2),
        "first": ts[on[0]].strftime("%a %H:%M") if on.size else "-",
        "last": ts[on[-1]].strftime("%a %H:%M") if on.size else "-",
        "weekend_slots": int(sum(1 for i in on if ts[i].weekday() >= 5)),
        "peak_kw": round(float(sp.max()), 2),
        "dhw_slots": int((dh > SLOT_KW).sum()), "dhw_kwh": round(float(dh.sum() * 0.25), 2),
        "room_min": round(float(room.min()), 2), "room_max": round(float(room.max()), 2),
        "comfort_fri": config.get_comfort_temp(14.0, START),
        "comfort_sat": config.get_comfort_temp(14.0, START + timedelta(days=1)),
        "floor_sat": config.get_temp_bounds(14.0, START + timedelta(days=1))[0],
        "status": res.status,
    }
    print("RESULT " + " ".join(f"{k}={v}" for k, v in out.items()), flush=True)
    return out


WEEKEND = {"comfort_temp_day_weekend": 21.0, "comfort_temp_night_weekend": 19.5}


def main() -> int:
    away = run("away")
    off18 = run("null_away_off", active=False)
    off21 = run("away_off_setpoint21", active=False, setpoint=21.0)
    run("null_flat", flat=True)
    run("indoor18", indoor=18.0)
    wk = run("weekend", **WEEKEND)
    run("weekend_flat", flat=True, **WEEKEND)
    run("weekend_away_off", active=False, **WEEKEND)
    hol = run("holiday", holiday=True)
    run("recovery", recovery=True)
    inert = (off18["space_slots"], off18["space_kwh"]) == (off21["space_slots"], off21["space_kwh"])
    print(f"VERDICT setpoint {'does NOT move the space plan (18 == 21)' if inert else 'moves the space plan'}")
    print(f"VERDICT away {'removes all space heating' if away['space_slots'] == 0 else 'leaves space heating'}")
    target_leak = wk["comfort_sat"] != away["comfort_sat"] or hol["comfort_sat"] != away["comfort_sat"]
    slot_leak = wk["weekend_slots"] > away["weekend_slots"] or hol["space_slots"] > away["space_slots"]
    print(f"VERDICT weekend/holiday comfort {'REPLACES' if target_leak else 'keeps'} the away target "
          f"(Sat {wk['comfort_sat']} / {hol['comfort_sat']} vs {away['comfort_sat']}); "
          f"extra space slots in this house: {'yes' if slot_leak else 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
