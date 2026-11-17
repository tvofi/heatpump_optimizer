"""D0-s2 cell builder (round 11): one d0-grid cell -> the exact SolveRecord production solves.

Not a harness on its own; imported by race.py / mpc.py / enum_cells.py in this directory.

A cell is `price/weather/topology/dhw/plant/<H>h` (tools/audit/enumerate.py d0-grid).
The record is built by the PRODUCTION coordinator (`HeatPumpOptimizerCoordinator._solve_record`)
over a FakeHass entry whose config is tests/profiles.py:house(...) plus the plant's keys, with
the clock frozen at tests/golden.py:START and the horizon arrays taken from tests/profiles.py
(tiled for 48 h, cut for 6 h). `record.optimizer()` is the production solver object.

Plant mapping (config keys only; every key is a production config key in const.py):
  plain                      no valve (house() defaults: 200 L buffer as a pass-through)
  valve-storage              mixing_valve_mode=smart_write (throttling, the buffer stores)
  manual-valve-buffer        mixing_valve_mode=manual (throttling, dumb valve, buffer)
  wood                       mixing_valve_mode=manual + wood furnace on with a top probe (two-tank), the wood
                             tank read at WOOD_TANK_C = 65 C at the solve (without a reading the solver runs
                             the plant as manual-valve-buffer: 59/59 identical plans before this was set)
  flow-setpoint-behind-valve mixing_valve_mode=smart_write, write kind flow, pump duty control,
                             space set-point unit flow, modulating compressor
Coordinator captures: tests/golden.py:coordinator_scenarios() configs, same horizon injection.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
from dataclasses import replace
from datetime import timedelta

ROOT = os.getcwd()
for _p in (os.path.join(ROOT, "tests"), os.path.join(ROOT, "custom_components")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np  # noqa: E402

WOOD_TANK_C = 65.0
PRICES = ("winter_typical", "winter_extreme", "winter_narrow", "winter_moderate")

PLANTS = {
    "plain": {},
    "valve-storage": {"mixing_valve_mode": "smart_write",
                      "mixing_valve_write_entity": "number.valve_target"},
    "manual-valve-buffer": {"mixing_valve_mode": "manual"},
    "wood": {"mixing_valve_mode": "manual", "wood_furnace_enabled": True,
             "wood_tank_top_entity": "sensor.wood_top", "wood_tank_volume": 1000.0},
    "flow-setpoint-behind-valve": {
        "mixing_valve_mode": "smart_write", "mixing_valve_write_entity": "number.valve_target",
        "mixing_valve_write_target_kind": "flow", "pump_duty_mode": "control",
        "space_setpoint_entity": "number.flow_sp", "space_setpoint_unit": "flow",
        "compressor_modulation": "modulating"},
}


def cell_config(topology, dhw, plant):
    import profiles
    cfg = profiles.house(two_zone=(topology == "two-zone"))
    cfg.update({"tibber_token": "x", "weather_entity": "weather.home",
                "dhw_enabled": dhw == "dhw"})
    if dhw != "dhw":
        for k in ("dhw_tank_volume", "dhw_setpoint", "dhw_min_temperature",
                  "dhw_daily_consumption", "dhw_windows"):
            cfg.pop(k, None)
    cfg.update(PLANTS[plant])
    return cfg


def coord_config(name):
    import golden
    return dict(golden.coordinator_scenarios()[name])


def _series(price, weather, start, hours, offset=0):
    import profiles
    n = int(hours * 4)
    days = max(1, int(np.ceil((offset + n) / 96.0)))
    pr = np.concatenate([profiles.prices(price, start + timedelta(days=d)) for d in range(days)])
    ws = [profiles.weather(weather, start + timedelta(days=d)) for d in range(days)]
    ot, wi, ra, so = (np.concatenate([w[i] for w in ws]) for i in range(4))
    sl = slice(offset, offset + n)
    return pr[sl], ot[sl], wi[sl], ra[sl], so[sl]


def build_record(config, price, weather, hours, state_over=None, offset=0, state=None):
    """(record, coord) for one cell, built by the production coordinator.

    ``offset`` (15-min steps) moves the solve anchor and the horizon window forward (the MPC loop);
    ``state`` replaces the coordinator's current state wholesale (a plant state in the loop)."""
    import golden
    from harness import FakeEntry, FakeHass
    from homeassistant.util import dt as dt_util
    from heatpump_optimizer.coordinator import (
        HeatPumpOptimizerCoordinator, ForecastArrays)
    saved = dt_util.DEFAULT_TIME_ZONE
    dt_util.DEFAULT_TIME_ZONE = golden.SCENARIO_ZONE
    start = golden.START + timedelta(minutes=15 * offset)
    dt_util.freeze(start)
    try:
        coord = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=config))
        coord._opt_config = replace(coord._opt_config, horizon_hours=float(hours))
        pr, ot, wi, ra, so = _series(price, weather, golden.START, hours, offset)
        n = pr.size
        hz = ForecastArrays(pr, ot, wi, ra, so, np.ones(n, bool), np.zeros(n),
                            np.zeros(n), np.full(n, np.nan), np.zeros(n))
        st = coord._current_state
        st.room_temperature = 21.0
        st.slab_temperature = 22.0
        st.outdoor_temperature = float(ot[0])
        st.upper_floor_temperature = 21.0
        st.lower_floor_temperature = 21.0
        st.buffer_tank_temperature = 40.0
        # DHW starts at ThermalState's own default (55 C); the coordinator reads no tank sensor here.
        if config.get("wood_furnace_enabled"):
            # The wood plant only exists for the solver with a tank reading (ThermalState.wood_tank_temperature
            # None = the two-tank model off): a charged tank after a firing, WOOD_TANK_C.
            st.wood_tank_temperature = WOOD_TANK_C
        if state is not None:
            import copy
            st = copy.deepcopy(state)
            st.outdoor_temperature = float(ot[0])
            coord._current_state = st
        for k, v in (state_over or {}).items():
            setattr(st, k, v)
        rec = coord._solve_record(start, hz)
    finally:
        dt_util.freeze(None)
        dt_util.DEFAULT_TIME_ZONE = saved
    return rec, coord


def parse_cell(line):
    price, weather, topo, dhw, plant, h = line.strip().split("/")
    return price, weather, topo, dhw, plant, int(h.rstrip("h"))


def cell_record(line, price_override=None):
    price, weather, topo, dhw, plant, h = parse_cell(line)
    return build_record(cell_config(topo, dhw, plant), price_override or price, weather, h)


def coord_record(line, price_override=None):
    _, name, price, weather = line.strip().split("/")
    return build_record(coord_config(name), price_override or price, weather, 24)


def any_record(line, price_override=None):
    return coord_record(line, price_override) if line.startswith("coord/") else cell_record(line, price_override)
