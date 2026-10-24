#!/usr/bin/env python3
"""R10-DEMAND-OVERBOOK (#2499): closed-loop replay of the real coordinator on synthetic installs.

Each arm runs the coordinator's own ``_update_current_state`` (every learner)
and the real optimizer every 30 min against a SYNTHETIC true house -- a
``ThermalModel`` whose parameters the arm sets -- with no heat sensor. The
pump may deliver less than commanded (``deliver``: a setpoint-driven or
capped pump), and draws ``idle`` kW of standby while off. Prices are flat
unless the arm says ``spread``: with no price to chase, any excess the plan
books is demand, not arbitrage (the flat-price null).

Per arm it prints one ``RESULT`` line:

  scale        the learned ``house_heat_loss_scale`` after the run; ``true``
               is the synthetic house's own.
  plan/deliv   the plan's 12-hour energy at 00:00 and 12:00, summed per day,
               over the electric energy the house actually received that
               day, days 2..end (day 1 is the learner's warm-up).
  samples      the house learner's accepted samples.

Arms whose name ends ``_oracle`` replace the slab seed with the TRUE house's
slab: the upper bound a perfect slab estimate reaches, and the control that
attributes the learner's bias to the slab seed rather than to the learner.

``--dp`` adds the DP reference: after the ``owner_i01`` arm it solves the
same 12-hour window by dynamic programming over a (room, slab) grid on the
coordinator's own learned model, and prints the optimizer's plan and the DP
optimum on one objective (energy cost plus a quadratic penalty below the
comfort floor).

    PYTHONPATH=tests/hastub:custom_components:tests \\
        python3 dev/audit/harnesses/r10_demand_overbook.py [--dp] [ARM ...]
"""
from __future__ import annotations

import asyncio
import copy
import json
import subprocess
import sys
from dataclasses import replace
from datetime import timedelta
from pathlib import Path

import numpy as np

DT_MIN = 30.0
MIN_TEMP = 20.0
PENALTY_PER_K2 = 50.0


def _deliver_owner(c):
    return min(3.0, 0.4 * c) if c > 0.05 else 0.0


OWNER = {"clamp": True, "pmin": 1.5, "pmax": 5.0, "true_scale": 0.6, "days": 10}
ARMS = {
    "null": {},
    "true0.5": {"true_scale": 0.5},
    "slab3x": {"true": {"slab_thermal_mass": 15.0}},
    "meter_half": {"deliver": "half"},
    "meter_half_oracle": {"deliver": "half", "slab_oracle": True},
    "meter_sat3": {"deliver": "sat3"},
    "nometer_half": {"meter": False, "deliver": "half"},
    "owner_ideal": {**OWNER},
    "owner_i01": {**OWNER, "idle": 0.1, "deliver": "owner"},
    "owner_i01_oracle": {**OWNER, "idle": 0.1, "deliver": "owner", "slab_oracle": True},
    "owner_i01_spread": {**OWNER, "idle": 0.1, "deliver": "owner", "spread": True},
    "owner_i03": {**OWNER, "idle": 0.3, "deliver": "owner"},
}
DELIVER = {
    None: lambda c: c,
    "half": lambda c: 0.5 * c,
    "sat3": lambda c: min(c, 3.0),
    "owner": _deliver_owner,
}


def _weather(day, h):
    return float(8.0 + 2.0 * np.sin(day * 0.9) + 4.0 * np.sin((h - 14.0) / 24.0 * 2 * np.pi))


def _day(day, spread):
    h = np.arange(48) * 0.5
    prices = 1.3 + 0.9 * np.sin(2 * np.pi * (h - 7.5) / 24.0) if spread else np.full(48, 1.3)
    return prices, np.array([_weather(day, x) for x in h])


def run(name, dp=False):
    import homeassistant.util.dt as dt_mod
    from harness import FakeEntry, FakeHass, FakeState
    from profiles import solve_inputs

    import heatpump_optimizer.coordinator as C
    from heatpump_optimizer import boost
    from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
    from heatpump_optimizer.thermal_model import ThermalModel, ThermalState

    arm = ARMS[name]
    meter = arm.get("meter", True)
    deliver = DELIVER[arm.get("deliver")]
    cfg = {
        "tibber_token": "x", "weather_entity": "weather.home",
        "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
        "optimization_interval": DT_MIN,
        "heat_pump_min_power": arm.get("pmin", 1.0), "heat_pump_max_power": arm.get("pmax", 5.0),
    }
    if meter:
        cfg["heat_pump_power_entity"] = "sensor.hp_power"
    coord = C.HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=cfg))
    coord._snapshots_loaded = True
    getattr(coord, "_ctx", coord)._thermal_params.dhw_enabled = False
    true_params = copy.deepcopy(getattr(coord, "_ctx", coord)._thermal_params)
    true_params.house_heat_loss_scale = arm.get("true_scale", 1.0)
    for key, value in arm.get("true", {}).items():
        setattr(true_params, key, value)
    house = ThermalModel(true_params)
    held = {}
    if arm.get("slab_oracle"):
        plan_value = C._open_loop_plan_value
        C._open_loop_plan_value = lambda r, attr, now: (
            held["house"].slab_temperature if attr == "slab_temp_trajectory" else plan_value(r, attr, now))

        async def true_slab(*_args):
            return held["house"].slab_temperature
        C._propagated_slab = true_slab
    opt = HeatPumpOptimizer(coord._thermal_model, OptimizationConfig(
        horizon_hours=12.0, time_step_minutes=DT_MIN, target_temp=21.0, min_temp=MIN_TEMP,
        max_temp=23.0, clamp_planned_levels=arm.get("clamp", False)))
    hs = ThermalState(room_temperature=21.0, outdoor_temperature=8.0, slab_temperature=22.0)
    start = dt_mod.parse_datetime("2026-10-05T00:00:00+00:00")
    draw, day = 0.0, -1
    delivered, planned = {}, {}
    for i in range(int(arm.get("days", 6) * 48)):
        t = start + timedelta(minutes=i * DT_MIN)
        day += t.hour == 0 and t.minute == 0
        dt_mod.freeze(t)
        held["house"] = hs
        h = t.hour + t.minute / 60.0
        out = _weather(day, h)
        coord.hass.states.set("sensor.indoor", FakeState(f"{hs.room_temperature:.3f}", last_updated=t, unit="°C"))
        coord.hass.states.set("sensor.outdoor", FakeState(f"{out:.3f}", last_updated=t, unit="°C"))
        if meter:
            coord.hass.states.set("sensor.hp_power", FakeState(f"{draw:.3f}", last_updated=t, unit="kW"))
        asyncio.run(coord._update_current_state())
        state = getattr(coord, "_ctx", coord)._current_state
        p1, o1 = _day(day, arm.get("spread", False))
        p2, o2 = _day(day + 1, arm.get("spread", False))
        k = int(round(h * 2))
        window = (np.concatenate([p1, p2])[k:k + 24], np.concatenate([o1, o2])[k:k + 24])
        res = opt.optimize(inputs=solve_inputs(
            initial_state=state, prices=window[0], outdoor_temps=window[1], start_time=t))
        coord._optimization_result = res
        commanded = float(res.power_schedule[0])
        if t.minute == 0 and t.hour in (0, 12):
            planned[day] = planned.get(day, 0.0) + float(np.sum(res.power_schedule)) * DT_MIN / 60.0
        boost.adopt_plan(coord, {
            "power": commanded, "setpoint": 23.0, "mode": "auto", "power_normalized": commanded / 5.0,
            "heat_pump_on": commanded > 0.05, "displace_value": 0.0, "space_reason": "plan"})
        heat_e = deliver(commanded)
        draw = heat_e + (arm.get("idle", 0.0) if heat_e <= 0.05 else 0.0)
        delivered[day] = delivered.get(day, 0.0) + heat_e * DT_MIN / 60.0
        hs = house.simulate_step(hs, heat_e, out, dt_hours=DT_MIN / 60.0, hour_of_day=h)
        hs.outdoor_temperature = out
    days = sorted(delivered)[1:]
    row = {
        "arm": name,
        "scale": round(coord._house_heat_loss_scale, 3),
        "true": arm.get("true_scale", 1.0),
        "plan/deliv": round(sum(planned[d] for d in days) / max(sum(delivered[d] for d in days), 1e-9), 3),
        "plan_kwh": [round(planned[d], 1) for d in days],
        "deliv_kwh": [round(delivered[d], 1) for d in days],
        "samples": coord._house_heat_loss_samples,
        "room": round(hs.room_temperature, 2),
    }
    if dp:
        row["dp"] = _dp_reference(coord._thermal_model, state, window, res, t)
    return row


def _dp_reference(model, state, window, res, t):
    """The optimizer's plan against a DP optimum, both on ``model`` and one objective."""
    from scipy.interpolate import RegularGridInterpolator

    prices, outdoor = window
    n, dt_h = len(prices), DT_MIN / 60.0
    hours = [(t.hour + t.minute / 60.0 + i * dt_h) % 24.0 for i in range(n)]
    levels = [0.0, *np.arange(1.5, 5.01, 0.25)]
    rooms, slabs = np.arange(17.0, 25.01, 0.1), np.arange(17.0, 35.01, 0.25)

    def step(room, slab, p, i):
        s = model.simulate_step(replace(state, room_temperature=room, slab_temperature=slab),
                                p, outdoor[i], dt_hours=dt_h, hour_of_day=hours[i])
        return s.room_temperature, s.slab_temperature

    def stage(room, p, i):
        return prices[i] * p * dt_h + PENALTY_PER_K2 * max(0.0, MIN_TEMP - room) ** 2

    grid = [(room, slab) for room in rooms for slab in slabs]
    value = np.zeros((len(rooms), len(slabs)))
    for i in reversed(range(n)):
        nxt = RegularGridInterpolator((rooms, slabs), value, bounds_error=False, fill_value=None)
        best = np.full(len(grid), np.inf)
        for p in levels:
            after = np.array([step(room, slab, p, i) for room, slab in grid])
            shortfall = np.maximum(0.0, MIN_TEMP - after[:, 0])
            cost = prices[i] * p * dt_h + PENALTY_PER_K2 * shortfall ** 2 + nxt(after)
            best = np.minimum(best, cost)
        value = best.reshape(value.shape)
    dp_cost = float(RegularGridInterpolator((rooms, slabs), value)([[state.room_temperature, state.slab_temperature]])[0])

    def rollout(schedule):
        room, slab, cost, energy = state.room_temperature, state.slab_temperature, 0.0, 0.0
        for i, p in enumerate(schedule):
            room, slab = step(room, slab, float(p), i)
            cost += stage(room, float(p), i)
            energy += float(p) * dt_h
        return round(cost, 3), round(energy, 2)

    plan_cost, plan_kwh = rollout(res.power_schedule)
    return {"dp_cost": round(dp_cost, 3), "plan_cost": plan_cost, "plan_kwh": plan_kwh,
            "gap": round((plan_cost - dp_cost) / max(dp_cost, 1e-9), 4)}


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--one":
        print(json.dumps(run(args[1], dp=len(args) > 2)), flush=True)
        sys.exit(0)
    dp = "--dp" in args
    names = [a for a in args if a != "--dp"] or list(ARMS)
    procs = [
        (name, subprocess.Popen(
            [sys.executable, str(Path(__file__).resolve()), "--one", name, *(["dp"] if dp and name == "owner_i01" else [])],
            stdout=subprocess.PIPE, text=True))
        for name in names
    ]
    for name, proc in procs:
        out, _ = proc.communicate()
        print("RESULT", out.strip() if proc.returncode == 0 else json.dumps({"arm": name, "rc": proc.returncode}))
