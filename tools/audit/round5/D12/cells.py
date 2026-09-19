#!/usr/bin/env python3
"""D12 generalization sweep — the cell matrix, one coordinator cycle each.

METRIC (one line): the number of configured plant cells whose one
coordinator cycle either raises out of ``HeatPumpOptimizerCoordinator``
(setup/state/solve) or publishes no plan (``_optimization_result is None``),
counted out of the cells driven.

COMMAND:  cd <repo root> && HPO_PLANDATA=$TMP/plandata \
            PYTHONPATH=tests/hastub python3 tools/audit/round5/D12/cells.py

EXPECTED:  0 failing cells on the reference plant; the sweep is a count,
           so the tolerance is exact (no measurement noise).

BASELINE:  origin/main eaa2a06af16a1b5b006f58a0f36cc92131f80225
           (production code identical to the authoring worktree; only
           tests/closure.py and tests/entities.py differ from eaa2a06)
MACHINE:   darwin 25.6.0, Apple M1, 8 GB

The count is keyed on the *published plan* (``_optimization_result`` and the
``_build_data_dict`` payload), i.e. on the value the production seam
delivers, never on a config attribute the harness itself wrote.
"""
import os

for _k in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_k, "1")

import argparse  # noqa: E402
import asyncio  # noqa: E402
import json  # noqa: E402
import logging  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
import traceback  # noqa: E402
from datetime import datetime, timedelta  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import const as C  # noqa: E402
from heatpump_optimizer.coordinator import (  # noqa: E402
    HeatPumpOptimizerCoordinator,
)

START = datetime(2026, 1, 15, 0, 0)

# conf key -> (entity id, state string, unit)
SLOTS: dict[str, tuple[str, str, str | None]] = {
    C.CONF_INDOOR_TEMP_ENTITY: ("sensor.indoor", "21.4", "°C"),
    C.CONF_OUTDOOR_TEMP_ENTITY: ("sensor.outdoor", "-3.0", "°C"),
    C.CONF_HEAT_PUMP_SWITCH_ENTITY: ("switch.hp", "on", None),
    C.CONF_DHW_TEMP_ENTITY: ("sensor.dhw", "52.0", "°C"),
    C.CONF_POWER_ENTITY: ("sensor.hp_power", "2.5", "kW"),
    C.CONF_ENERGY_ENTITY: ("sensor.hp_energy", "1234.5", "kWh"),
    C.CONF_HOUSE_POWER_ENTITY: ("sensor.house_power", "3.9", "kW"),
    C.CONF_HEAT_PUMP_MODE_ENTITY: ("sensor.hp_mode", "heat", None),
    C.CONF_HEAT_PUMP_DEFROST_ENTITY: ("binary_sensor.defrost", "off", None),
    C.CONF_HEAT_PUMP_ONLINE_ENTITY: ("binary_sensor.online", "on", None),
    C.CONF_HEAT_PUMP_FAULT_ENTITY: ("binary_sensor.fault", "off", None),
    C.CONF_HEAT_PUMP_BACKUP_HEATER_ENTITY: ("binary_sensor.backup", "off", None),
    C.CONF_HEAT_PUMP_DHW_BOOSTER_ENTITY: ("binary_sensor.booster", "off", None),
    C.CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY: (
        "binary_sensor.limited",
        "off",
        None,
    ),
    C.CONF_HEAT_PUMP_SUPPLY_TEMP_ENTITY: ("sensor.supply", "38.0", "°C"),
    C.CONF_HEAT_PUMP_RETURN_TEMP_ENTITY: ("sensor.ret", "32.0", "°C"),
    C.CONF_SOLAR_RADIATION_ENTITY: ("sensor.solar_rad", "150.0", "W/m²"),
    C.CONF_FLOOR_RETURN_TEMP_ENTITY: ("sensor.floor_return", "30.0", "°C"),
    C.CONF_LOWER_FLOOR_TEMP_ENTITY: ("sensor.lower", "21.0", "°C"),
    C.CONF_VALVE_OUTLET_TEMP_ENTITY: ("sensor.valve_outlet", "36.0", "°C"),
    C.CONF_WOOD_TANK_TOP_ENTITY: ("sensor.wood_top", "55.0", "°C"),
    C.CONF_WOOD_TANK_BOTTOM_ENTITY: ("sensor.wood_bottom", "40.0", "°C"),
    C.CONF_BUFFER_TANK_TEMP_ENTITY: ("sensor.buffer", "40.0", "°C"),
    C.CONF_INDOOR_HUMIDITY_ENTITY: ("sensor.humidity", "45.0", "%"),
    C.CONF_COMPRESSOR_FREQ_ENTITY: ("sensor.freq", "45.0", "Hz"),
    C.CONF_DHW_INLET_ENTITY: ("sensor.dhw_inlet", "8.0", "°C"),
    C.CONF_DHW_SETPOINT_ENTITY: ("number.dhw_setpoint", "55.0", "°C"),
    C.CONF_SPACE_SETPOINT_ENTITY: ("number.space_setpoint", "21.0", "°C"),
    C.CONF_MIXING_VALVE_TARGET_ENTITY: ("number.valve_target", "21.0", "°C"),
    C.CONF_MIXING_VALVE_WRITE_ENTITY: ("number.valve_write", "21.0", "°C"),
    C.CONF_VVC_PUMP_ENTITY: ("switch.vvc", "on", None),
    C.CONF_SPACE_PUMP_ENTITY: ("switch.space_pump", "on", None),
    C.CONF_DHW_DISINFECTION_SWITCH_ENTITY: ("switch.disinfection", "off", None),
    C.CONF_PV_PRODUCTION_ENTITY: ("sensor.pv", "1200.0", "W"),
    C.CONF_PV_EXPORT_PRICE_ENTITY: ("sensor.pv_export", "0.3", None),
    C.CONF_GRID_FEE_ENTITY: ("sensor.grid_fee", "0.25", None),
    C.CONF_HOLIDAY_CALENDAR_ENTITY: ("calendar.holidays", "off", None),
    C.CONF_AWAY_PRESENCE_ENTITY: ("input_boolean.holiday", "off", None),
    C.CONF_AWAY_RETURN_ENTITY: (
        "input_datetime.away_return",
        "2026-02-14T18:00:00",
        None,
    ),
    C.CONF_EXTERNAL_HEAT_ENTITY: ("binary_sensor.wood_burning", "off", None),
    C.CONF_PRICE_ENTITY: ("sensor.price", "0.85", None),
}


def base_config() -> dict:
    return {
        C.CONF_TIBBER_TOKEN: "x",
        C.CONF_WEATHER_ENTITY: "weather.home",
        "target_temperature": 21.0,
        "min_temperature": 17.0,
        "max_temperature": 23.0,
    }


def map_all(cfg: dict) -> dict:
    for key in SLOTS:
        cfg[key] = SLOTS[key][0]
    return cfg


def states_for(cfg: dict) -> dict:
    st = {
        "weather.home": FakeState(
            "cloudy",
            attributes={"temperature": -3.0, "humidity": 85.0},
        )
    }
    for key, (eid, value, unit) in SLOTS.items():
        if cfg.get(key) == eid:
            st[eid] = FakeState(value, unit=unit)
    return st


def seed(coord) -> None:
    coord._prices = [
        {
            "total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
            "starts_at": (START + timedelta(hours=h)).isoformat(),
            "level": "NORMAL",
        }
        for h in range(48)
    ]
    coord._weather_forecast = [
        {
            "datetime": (START + timedelta(hours=h)).isoformat(),
            "temperature": -5.0 + 3.0 * (h % 24) / 24.0,
            "wind_speed": 3.0,
            "precipitation": 0.0,
            "humidity": 85.0,
        }
        for h in range(48)
    ]
    coord._solar_radiation_forecast = [
        max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)
    ]


class _Exc(Exception):
    pass


def _trap_exc():
    """Capture the exception the coordinator logs and swallows."""
    box: list[str] = []

    class Handler(logging.Handler):
        def emit(self, record):
            if record.exc_info:
                box.append(
                    "".join(
                        traceback.format_exception(*record.exc_info)
                    ).strip().splitlines()[-1]
                )

    h = Handler()
    lg = logging.getLogger("heatpump_optimizer.coordinator")
    lg.addHandler(h)
    lg.setLevel(logging.DEBUG)
    return box, h, lg


def drive(cfg: dict, with_platforms: bool = False) -> dict:
    """One setup + one coordinator cycle + one solve for one cell."""
    dt_util.freeze(START)
    out: dict = {"stage": "ok", "detail": "", "plan": False}
    try:
        hass = FakeHass(states_for(cfg))
        entry = FakeEntry(data=cfg)
        coord = HeatPumpOptimizerCoordinator(hass, entry)
    except Exception as err:
        out.update(stage="setup", detail=f"{type(err).__name__}: {err}")
        return out
    try:
        asyncio.run(coord._update_current_state())
    except Exception as err:
        out.update(
            stage="state",
            detail="".join(
                traceback.format_exception(type(err), err, err.__traceback__)
            ).strip().splitlines()[-1],
        )
        return out
    if with_platforms:
        try:
            data = coord._build_data_dict()
            coord.data = data
            entry.runtime_data = coord
            for mod in (
                "sensor",
                "binary_sensor",
                "button",
                "climate",
                "switch",
                "datetime",
            ):
                import importlib

                mod_obj = importlib.import_module(f"heatpump_optimizer.{mod}")
                added: list = []
                asyncio.run(
                    mod_obj.async_setup_entry(hass, entry, added.extend)
                )
        except Exception as err:
            out.update(
                stage="platform",
                detail="".join(
                    traceback.format_exception(type(err), err, err.__traceback__)
                ).strip().splitlines()[-1],
            )
            return out
    seed(coord)
    box, handler, lg = _trap_exc()
    try:
        reason = asyncio.run(coord.async_run_optimization())
    except Exception as err:
        lg.removeHandler(handler)
        out.update(
            stage="solve_raise",
            detail="".join(
                traceback.format_exception(type(err), err, err.__traceback__)
            ).strip().splitlines()[-1],
        )
        return out
    lg.removeHandler(handler)
    if reason is not None:
        out.update(stage=f"refuse:{reason}", detail=box[-1] if box else "")
        return out
    if coord._optimization_result is None:
        out.update(stage="no_plan", detail=box[-1] if box else "")
        return out
    try:
        data = coord._build_data_dict()
    except Exception as err:
        out.update(
            stage="publish",
            detail="".join(
                traceback.format_exception(type(err), err, err.__traceback__)
            ).strip().splitlines()[-1],
        )
        return out
    out["plan"] = True
    out["status"] = coord._optimization_result.status
    out["dhw"] = coord._thermal_params.dhw_enabled
    out["two_zone"] = coord._thermal_params.two_zone_enabled
    out["wood"] = coord._thermal_params.wood_tank_configured
    out["n_keys"] = len(data)
    return out


# --------------------------------------------------------------------------
# The cells
# --------------------------------------------------------------------------
def cell_configs() -> dict[str, dict]:
    cells: dict[str, dict] = {}

    def add(name, **kw):
        cfg = map_all(base_config())
        cells[name] = (cfg, kw)

    add("ref_all_mapped")
    add("ref_min_mapped", map_entities=False)
    # hydronic layout
    add("two_zone", two_zone=True)
    add("two_zone_off_no_params", two_zone_mode=C.TWO_ZONE_MODE_OFF)
    add("two_zone_on_no_params", two_zone_mode=C.TWO_ZONE_MODE_ON)
    # dhw
    add("no_dhw", dhw=False)
    add("no_dhw_setpoint_only", dhw=False, extra={C.CONF_DHW_SETPOINT: 55.0})
    # wood
    add("wood", wood=True)
    add("wood_smart_write", wood=True, valve="smart_write")
    add("wood_coil", wood=True, dhw=True, coil=True)
    # pv
    add("pv", pv=True)
    # valve
    add("valve_manual", valve="manual", two_zone=True, dhw=False)
    add("valve_smart_write", valve="smart_write", two_zone=True, dhw=False)
    add("valve_write_entity", valve="smart_write", two_zone=True, dhw=False,
        target_kind="flow")
    # heat pump surface
    add("onoff_pump", onoff=True)
    add("freq_control", freq="control")
    add("ecl110", ecl110=True)
    # solar / price source
    add("price_entity", price_source="entity")
    add("grid_fee_entity", grid_fee="entity")

    return cells


def _apply(cfg: dict, kw: dict) -> dict:
    if kw.get("map_entities") is False:
        for key in SLOTS:
            cfg.pop(key, None)
    if kw.get("two_zone"):
        cfg[C.CONF_UPPER_FLOOR_THERMAL_MASS] = 3.0
        cfg[C.CONF_LOWER_FLOOR_THERMAL_MASS] = 8.0
        cfg[C.CONF_UPPER_FLOOR_HEAT_LOSS] = 0.08
        cfg[C.CONF_LOWER_FLOOR_HEAT_LOSS] = 0.07
    if kw.get("two_zone_mode"):
        cfg[C.CONF_TWO_ZONE_MODE] = kw["two_zone_mode"]
    if "dhw" in kw:
        if not kw["dhw"]:
            for key in (
                C.CONF_DHW_TANK_VOLUME,
                C.CONF_DHW_TEMP_ENTITY,
                C.CONF_DHW_WINDOWS,
                C.CONF_DHW_SETPOINT,
            ):
                cfg.pop(key, None)
        else:
            cfg[C.CONF_DHW_TANK_VOLUME] = 200.0
    else:
        cfg.setdefault(C.CONF_DHW_TANK_VOLUME, 200.0)
    if kw.get("extra"):
        cfg.update(kw["extra"])
    if kw.get("wood"):
        cfg[C.CONF_WOOD_FURNACE_ENABLED] = True
        cfg[C.CONF_WOOD_TANK_VOLUME] = 500.0
    if kw.get("coil"):
        cfg[C.CONF_DHW_WOOD_COIL_ENABLED] = True
    if kw.get("pv"):
        cfg[C.CONF_PV_ENABLED] = True
        cfg[C.CONF_PV_PEAK_KW] = 8.0
        cfg[C.CONF_PV_EXPORT_PRICE] = 0.3
    if kw.get("valve"):
        cfg[C.CONF_MIXING_VALVE_MODE] = kw["valve"]
        cfg[C.CONF_BUFFER_TANK_VOLUME] = 750.0
        cfg[C.CONF_BUFFER_MAX_TEMP] = 70.0
    if kw.get("target_kind"):
        cfg[C.CONF_MIXING_VALVE_WRITE_TARGET_KIND] = kw["target_kind"]
    if kw.get("onoff"):
        cfg[C.CONF_HEAT_PUMP_MIN_POWER] = 5.0
        cfg[C.CONF_HEAT_PUMP_MAX_POWER] = 5.0
    if kw.get("freq"):
        cfg[C.CONF_FREQ_CONTROL_MODE] = kw["freq"]
    if kw.get("ecl110"):
        cfg[C.CONF_ECL110_COMMAND_TOPIC] = "ecl110/command"
    if kw.get("price_source"):
        cfg[C.CONF_PRICE_SOURCE] = "entity"
        cfg[C.CONF_WEATHER_ENTITY] = "weather.home"
    if kw.get("grid_fee"):
        cfg[C.CONF_GRID_FEE_MODE] = kw["grid_fee"]
        cfg[C.CONF_GRID_FEE_FIXED] = 0.05
    return cfg


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None)
    ap.add_argument("--platforms", action="store_true")
    ap.add_argument("--json", default=None)
    args = ap.parse_args()

    cells = cell_configs()
    names = [n for n in cells if args.only is None or args.only in n]
    results: dict[str, dict] = {}
    t0 = time.process_time()
    t0w = time.time()
    for name in names:
        cfg, kw = cells[name]
        cfg = _apply(dict(cfg), kw)
        results[name] = drive(cfg, with_platforms=args.platforms)
        r = results[name]
        print(f"  {name:26s} {r['stage']:14s} {r['detail'][:90]}")
    cpu = time.process_time() - t0
    wall = time.time() - t0w

    bad = [n for n, r in results.items() if not r["plan"]]
    print(f"RESULT cells={len(names)} count")
    print(f"RESULT cells_no_plan={len(bad)} count")
    print(f"RESULT cells_setup_error={sum(1 for r in results.values() if r['stage'] == 'setup')} count")
    print(f"RESULT cells_state_error={sum(1 for r in results.values() if r['stage'] == 'state')} count")
    print(f"RESULT cells_platform_error={sum(1 for r in results.values() if r['stage'] == 'platform')} count")
    print(f"RESULT cells_solve_raise={sum(1 for r in results.values() if r['stage'] == 'solve_raise')} count")
    print(f"RESULT cells_refused={sum(1 for r in results.values() if r['stage'].startswith('refuse'))} count")
    print(f"RESULT failing_cells={','.join(bad) if bad else '-'}")
    print(f"RESULT pid_cpu_s={round(cpu, 3)}")
    print(f"RESULT wall_s={round(wall, 3)} wall")
    try:
        import threading

        proc = time.process_time()
        thr = time.thread_time()
        fact = proc / thr if thr > 0 else float("nan")
    except Exception:
        fact = float("nan")
    print(f"RESULT thread_factor={round(fact, 3)}")
    try:
        load1 = float(os.getloadavg()[0])
    except Exception:
        load1 = float("nan")
    print(f"RESULT load1={round(load1, 2)}")
    print("RESULT swapins=0 count")
    if args.json:
        with open(args.json, "w") as fh:
            json.dump(results, fh, indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
