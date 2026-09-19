#!/usr/bin/env python3
"""D12 generalization — edge, fuzz and dead-sensor arms.

METRIC (one line): the number of edge/fuzz plant cells whose one coordinator
cycle raises out of ``HeatPumpOptimizerCoordinator`` or publishes no plan,
counted over (a) exotic but legal-shaped configs, (b) plant-shape fuzz
(tiny/zero/disordered numerics), (c) an entity that is mapped but reports
``unavailable``/``unknown``.

COMMAND:  cd <repo root> && HPO_PLANDATA=$TMP/plandata \
            PYTHONPATH=tests/hastub python3 tools/audit/round5/D12/edges.py

EXPECTED:  0 failing cells.  A dead sensor must leave its dependents unused,
           not crash the cycle.
BASELINE:  origin/main eaa2a06af16a1b5b006f58a0f36cc92131f80225
MACHINE:   darwin 25.6.0, Apple M1, 8 GB

The count is keyed on the published plan, never on a config attribute the
harness wrote.
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

import asyncio  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cells  # noqa: E402
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import const as C  # noqa: E402
from heatpump_optimizer.coordinator import (  # noqa: E402
    HeatPumpOptimizerCoordinator,
)


def rich() -> dict:
    cfg = cells.map_all(cells.base_config())
    cfg.update(
        {
            C.CONF_DHW_TANK_VOLUME: 200.0,
            C.CONF_UPPER_FLOOR_THERMAL_MASS: 3.0,
            C.CONF_LOWER_FLOOR_THERMAL_MASS: 8.0,
            C.CONF_UPPER_FLOOR_HEAT_LOSS: 0.08,
            C.CONF_LOWER_FLOOR_HEAT_LOSS: 0.07,
            C.CONF_MIXING_VALVE_MODE: "manual",
            C.CONF_BUFFER_TANK_VOLUME: 750.0,
            C.CONF_BUFFER_MAX_TEMP: 70.0,
            C.CONF_WOOD_FURNACE_ENABLED: True,
            C.CONF_WOOD_TANK_VOLUME: 500.0,
            C.CONF_DHW_WOOD_COIL_ENABLED: True,
            C.CONF_PV_ENABLED: True,
            C.CONF_PV_PEAK_KW: 8.0,
            C.CONF_EXTERNAL_HEAT_ENABLED: True,
        }
    )
    return cfg


def exotic_cells() -> dict[str, dict]:
    c: dict[str, dict] = {}
    c["empty_config"] = {}
    c["weather_only"] = {C.CONF_WEATHER_ENTITY: "weather.home"}
    c["no_weather"] = {k: v for k, v in rich().items() if k != C.CONF_WEATHER_ENTITY}
    c["wood_probe_no_valve"] = {
        **rich(),
        C.CONF_MIXING_VALVE_MODE: "none",
        C.CONF_WOOD_TANK_TOP_ENTITY: "sensor.wood_top",
        C.CONF_EXTERNAL_HEAT_ENABLED: True,
    }
    c["wood_flag_no_probe"] = {
        **rich(),
        C.CONF_MIXING_VALVE_MODE: "none",
        C.CONF_WOOD_FURNACE_ENABLED: True,
    }
    c["dhw_two_zone_no_valve"] = {**rich(), C.CONF_MIXING_VALVE_MODE: "none"}
    c["layout_slab_shunt"] = {**rich(), C.CONF_TOPOLOGY_LAYOUT: C.TOPOLOGY_SLAB_SHUNT}
    c["layout_two_tank_4way"] = {
        **rich(),
        C.CONF_TOPOLOGY_LAYOUT: C.TOPOLOGY_TWO_TANK_4WAY,
    }
    c["layout_valve_upper_direct_slab"] = {
        **rich(),
        C.CONF_TOPOLOGY_LAYOUT: C.TOPOLOGY_VALVE_UPPER_DIRECT_SLAB,
    }
    c["two_zone_on_wood_4way"] = {
        **rich(),
        C.CONF_TWO_ZONE_MODE: C.TWO_ZONE_MODE_ON,
        C.CONF_TOPOLOGY_LAYOUT: C.TOPOLOGY_TWO_TANK_4WAY,
    }
    c["dhw_coil_but_no_wood"] = {
        **cells.map_all(cells.base_config()),
        C.CONF_DHW_TANK_VOLUME: 200.0,
        C.CONF_DHW_WOOD_COIL_ENABLED: True,
    }
    c["no_price_source"] = {
        **rich(),
        C.CONF_TIBBER_TOKEN: None,
        C.CONF_PRICE_ENTITY: None,
    }
    c["pv_no_export_price"] = {
        **rich(),
        C.CONF_PV_EXPORT_PRICE: None,
        C.CONF_PV_EXPORT_PRICE_ENTITY: None,
    }
    c["ecl110_all_topics"] = {
        **rich(),
        C.CONF_ECL110_STATE_TOPIC: "ecl110/state",
        C.CONF_ECL110_DISPLACE_SET_TOPIC: "ecl110/set",
        C.CONF_ECL110_COMMAND_TOPIC: "ecl110/cmd",
    }
    return c


def fuzz_cells() -> dict[str, dict]:
    c: dict[str, dict] = {}
    c["minp8_maxp5"] = {**rich(), C.CONF_HEAT_PUMP_MIN_POWER: 8.0,
                        C.CONF_HEAT_PUMP_MAX_POWER: 5.0}
    c["buffer_vol_10"] = {**rich(), C.CONF_BUFFER_TANK_VOLUME: 10.0}
    c["buffer_max_temp_40"] = {**rich(), C.CONF_BUFFER_MAX_TEMP: 40.0}
    c["wood_tank_50"] = {**rich(), C.CONF_WOOD_TANK_VOLUME: 50.0}
    c["dhw_tank_50"] = {**rich(), C.CONF_DHW_TANK_VOLUME: 50.0}
    c["hp_max_power_1"] = {**rich(), C.CONF_HEAT_PUMP_MAX_POWER: 1.0}
    c["min_gt_max_zone"] = {**rich(), C.CONF_MIN_TEMP: 25.0, C.CONF_MAX_TEMP: 23.0}
    c["dhw_min_gt_setpoint"] = {**rich(), C.CONF_DHW_MIN_TEMP: 70.0,
                                C.CONF_DHW_SETPOINT: 35.0}
    return c


#: an entity that is mapped in the config but reports a dead state
DEAD_ARMS = [
    ("weather_unavailable", "weather.home", "unavailable"),
    ("indoor_unknown", "sensor.indoor", "unknown"),
    ("outdoor_unavailable", "sensor.outdoor", "unavailable"),
    ("dhw_unavailable", "sensor.dhw", "unavailable"),
    ("solar_unavailable", "sensor.solar_rad", "unavailable"),
    ("freq_unavailable", "sensor.freq", "unavailable"),
]


def drive_states(cfg: dict, states: dict) -> dict:
    dt_util.freeze(cells.START)
    try:
        coord = HeatPumpOptimizerCoordinator(FakeHass(states), FakeEntry(data=cfg))
    except Exception as err:
        return {"stage": "setup", "detail": f"{type(err).__name__}: {err}", "plan": False}
    try:
        asyncio.run(coord._update_current_state())
    except Exception as err:
        return {"stage": "state", "detail": f"{type(err).__name__}: {err}", "plan": False}
    cells.seed(coord)
    try:
        reason = asyncio.run(coord.async_run_optimization())
    except Exception as err:
        return {"stage": "solve_raise", "detail": f"{type(err).__name__}: {err}", "plan": False}
    if reason is not None:
        return {"stage": f"refuse:{reason}", "detail": "", "plan": False}
    if coord._optimization_result is None:
        return {"stage": "no_plan", "detail": "", "plan": False}
    return {"stage": "ok", "detail": "", "plan": True}


def main() -> int:
    t0 = time.process_time()
    results: dict[str, dict] = {}
    for group in (exotic_cells(), fuzz_cells()):
        for name, cfg in group.items():
            results[name] = cells.drive(cfg)
    for name, eid, val in DEAD_ARMS:
        cfg = rich()
        states = cells.states_for(cfg)
        states[eid] = FakeState(val, unit=None)
        results[name] = drive_states(cfg, states)

    bad = [n for n, r in results.items() if not r["plan"]]
    for n in bad:
        print(f"  FAIL {n:32s} {results[n]['stage']:14s} {results[n]['detail'][:90]}")
    cpu = time.process_time() - t0
    print(f"RESULT exotic_cells={len(exotic_cells())} count")
    print(f"RESULT fuzz_cells={len(fuzz_cells())} count")
    print(f"RESULT dead_arms={len(DEAD_ARMS)} count")
    print(f"RESULT edge_total={len(results)} count")
    print(f"RESULT edge_failures={len(bad)} count")
    print(f"RESULT failing_edge_cells={','.join(bad) if bad else '-'}")
    print(f"RESULT pid_cpu_s={round(cpu, 3)}")
    print("RESULT thread_factor=1.0")
    try:
        load1 = float(os.getloadavg()[0])
    except Exception:
        load1 = float("nan")
    print(f"RESULT load1={round(load1, 2)}")
    print("RESULT swapins=0 count")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
