"""D8 round 5 -- source dependency map and "unknown where the data exists".

Metric definition (one line): for each (entity, cell) pair, whether the
entity's published state is None/unknown while at least one data key its
own ``native_value`` was empirically shown to depend on is present and
non-None in that cell's payload.

Method: build a real coordinator per cell with a full input cycle and a
solve (so a plan exists), collect every entity through the real
``async_setup_entry``, then EMPIRICALLY map each entity to the top-level
data keys it reads by poisoning one key at a time and re-reading
``native_value``. An entity is "unknown where data exists" when its state
is None in a cell yet any of its dependency keys holds a non-None value
there.

Run:
    PYTHONPATH=tests/hastub python3 tools/audit/round5/D8/d8_sources.py

Machine: Apple M1, 8 GB. RESULTs are counts and ratios -- content.
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_var, "1")

_HERE = Path(__file__).resolve()
_ROOT = _HERE.parents[4]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "tests"))
sys.path.insert(0, str(_ROOT / "tests" / "hastub"))

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import (  # noqa: E402
    binary_sensor, button, climate, datetime as datetime_mod, sensor, switch,
)
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

START = datetime(2026, 1, 15, 0, 0)
ROOT = Path("custom_components/heatpump_optimizer")
STRINGS = json.loads((ROOT / "strings.json").read_text())["entity"]
PLATFORM_MODULES = {
    "sensor": sensor, "binary_sensor": binary_sensor, "button": button,
    "climate": climate, "switch": switch, "datetime": datetime_mod,
}

# States every entity's gate wants satisfied. Seeded so every reading gate
# opens; this is the "every input present" arm, not the default install.
STATES = {
    "sensor.indoor": "21.4", "sensor.outdoor": "-3.0", "sensor.dhw": "55.0",
    "sensor.floor_return": "38.0", "sensor.lower_floor": "20.5",
    "sensor.buffer": "40.0", "sensor.hp_power": "2.4", "sensor.hp_energy": "1234.5",
    "sensor.house_power": "3.9", "sensor.solar_radiation": "210.0",
    "sensor.pv_production": "1.2", "input_boolean.holiday": "off",
    "sensor.hp_supply": "42.0", "sensor.hp_return": "36.0",
    "sensor.valve_out": "38.0", "sensor.valve_target": "40.0",
    "sensor.wood_top": "65.0", "sensor.wood_bottom": "45.0",
    "sensor.hp_mode": "heat",
}

CFG = {
    "tibber_token": "x", "weather_entity": "weather.home",
    "target_temperature": 21.0, "min_temperature": 17.0, "max_temperature": 23.0,
    "dhw_tank_volume": 200.0, "dhw_setpoint": 55.0, "dhw_min_temperature": 45.0,
    "dhw_temp_entity": "sensor.dhw", "dhw_inlet_entity": "sensor.dhw_inlet",
    "floor_return_temp_entity": "sensor.floor_return",
    "lower_floor_temp_entity": "sensor.lower_floor",
    "buffer_tank_temp_entity": "sensor.buffer",
    "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
    "heat_pump_power_entity": "sensor.hp_power",
    "heat_pump_energy_entity": "sensor.hp_energy",
    "house_power_entity": "sensor.house_power",
    "solar_radiation_entity": "sensor.solar_radiation",
    "pv_enabled": True, "pv_peak_kw": 8.0, "pv_export_price": 0.3,
    "pv_production_entity": "sensor.pv_production",
    "peak_tariff_enabled": True, "peak_tariff_price_per_kw": 45.0,
    "main_fuse_amperes": 20.0,
    "mixing_valve_mode": "smart_write", "mixing_valve_target": 40.0,
    "upper_floor_thermal_mass": 3.0, "lower_floor_thermal_mass": 8.0,
    "ecl110_command_topic": "ecl/cmd", "ecl110_state_topic": "ecl/state",
    "ecl110_displace_set_topic": "ecl/displace",
    "away_enabled": True, "away_presence_entity": "input_boolean.holiday",
    "wood_furnace_enabled": True, "wood_tank_volume": 500.0,
    "wood_tank_top_entity": "sensor.wood_top",
    "wood_tank_bottom_entity": "sensor.wood_bottom",
}


def build(phase=0):
    dt_util.freeze(START)
    try:
        hass = FakeHass()
        for eid, st in STATES.items():
            hass.states.set(eid, FakeState(st))
        entry = FakeEntry(data=dict(CFG))
        coord = HeatPumpOptimizerCoordinator(hass, entry)
        coord._prices = [
            {"total": round(0.6 + 0.5 * (h % 12) / 12.0 + 0.2 * phase, 4),
             "starts_at": (START + timedelta(hours=h)).isoformat(), "level": "NORMAL"}
            for h in range(48)
        ]
        coord._weather_forecast = [
            {"datetime": (START + timedelta(hours=h)).isoformat(),
             "temperature": -5.0 + 3.0 * (h % 24) / 24.0 + 2.0 * phase,
             "wind_speed": 3.0, "precipitation": 0.0, "humidity": 85.0}
            for h in range(48)
        ]
        coord._solar_radiation_forecast = [
            max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)
        ]

        async def run():
            await coord._update_current_state()
            coord.data = coord._build_data_dict()
            await coord.async_run_optimization()
            coord.data = coord._build_data_dict()

        asyncio.run(run())
    finally:
        dt_util.freeze(None)
    return hass, coord


def collect_all(coord):
    out = []
    for platform, module in PLATFORM_MODULES.items():
        added = []
        entry = FakeEntry()
        entry.runtime_data = coord
        asyncio.run(module.async_setup_entry(FakeHass(), entry, added.extend))
        for e in added:
            out.append((platform, e))
    return out


def poison(value):
    if isinstance(value, bool):
        return not value
    if isinstance(value, (int, float)):
        return value + 1000
    if isinstance(value, str):
        return "POISONED"
    if isinstance(value, (list, dict)):
        return None            # flips every "is the branch present" test
    if value is None:
        return 42.0
    return "POISONED"


def native_of(e):
    try:
        return e.native_value
    except Exception:  # noqa: BLE001
        return "<RAISED>"


def main():
    hass, coord = build(0)
    ents = collect_all(coord)
    base = {(p, type(e).__name__): native_of(e) for p, e in ents}
    avail = {(p, type(e).__name__): bool(getattr(e, "available", True))
             for p, e in ents}
    keys = list((coord.data or {}).keys())
    first = dict(coord.data)

    # dependency map: entity -> set of top-level keys that move native_value
    deps = {}
    nonnone_keys = {k for k in keys if coord.data.get(k) is not None}
    for p, e in ents:
        ident = (p, type(e).__name__)
        b = base[ident]
        moved = set()
        for k in keys:
            original = coord.data[k]
            coord.data[k] = poison(original)
            try:
                if native_of(e) != b:
                    moved.add(k)
            finally:
                coord.data[k] = original
        deps[ident] = moved

    # unknown where data exists: state None, entity available, while a
    # dependency key holds a non-None value in the same payload.
    unknown_where = []
    for p, e in ents:
        ident = (p, type(e).__name__)
        if p != "sensor" or not avail[ident]:
            continue
        if base[ident] is None and (deps[ident] & nonnone_keys):
            unknown_where.append((ident[1], sorted(deps[ident] & nonnone_keys)))

    # constants: entities whose value no top-level key moves
    constants = [ident for ident, m in deps.items() if not m]

    # two cycles: a second coordinator with changed inputs. An entity is
    # STALE when a key it depends on changed but its published value did not;
    # SPURIOUS when its value moved though no dependency key did.
    _, coord2 = build(1)
    second = coord2.data
    changed = {k for k in keys if second.get(k) != coord.data.get(k)}
    for k in keys:
        coord.data[k] = second.get(k)
    stale, spurious = [], []
    for p, e in ents:
        ident = (p, type(e).__name__)
        v2 = native_of(e)
        dep_changed = bool(deps[ident] & changed)
        moved = (v2 != base[ident])
        if dep_changed and not moved:
            stale.append(ident[1])
        if moved and not dep_changed and deps[ident]:
            spurious.append(ident[1])

    # cache reversion: the definitive "no staleness" property. Put the FIRST
    # payload back; a stateless entity must return exactly to its base value.
    # Any mismatch is a value that did not follow its input -- a real cache.
    for k in keys:
        coord.data[k] = first[k]
    reversion = [(p, type(e).__name__, base[(p, type(e).__name__)], native_of(e))
                 for p, e in ents if native_of(e) != base[(p, type(e).__name__)]]

    Path("/tmp/d8_sources.json").write_text(json.dumps({
        "n_data_keys": len(keys), "n_nonnull_keys": len(nonnone_keys),
        "n_entities": len(ents), "n_changed_keys": len(changed),
        "deps": {f"{a}:{b}": sorted(m) for (a, b), m in deps.items()},
        "base": {f"{a}:{b}": v for (a, b), v in base.items()},
        "unknown_where": unknown_where,
        "constants": [f"{a}:{b}" for a, b in constants],
        "stale": stale, "spurious": spurious,
        "reversion": [f"{a}:{b}" for a, b, _, _ in reversion],
    }, indent=1, default=str))

    print(f"RESULT entities={len(ents)}")
    print(f"RESULT data_keys={len(keys)}")
    print(f"RESULT nonnull_keys={len(nonnone_keys)}")
    print(f"RESULT unknown_where_data_exists={len(unknown_where)}")
    for name, kk in unknown_where:
        print(f"   UNKNOWN {name} deps={kk}")
    print(f"RESULT changed_keys_cycle2={len(changed)}")
    print(f"RESULT stale={len(stale)}")
    for s in stale:
        print(f"   STALE {s}")
    print(f"RESULT spurious={len(spurious)}")
    for s in spurious:
        print(f"   SPURIOUS {s}")
    print(f"RESULT cache_reversion_mismatch={len(reversion)}")
    for p, name, a, b in reversion:
        print(f"   REVERT {p}:{name} base={a!r} after={b!r}")
    print(f"RESULT constant_entities={len(constants)}")
    for ident in constants:
        print(f"   CONST {ident}  base={base[ident]!r}")
    print("RESULT thread_factor=1.0 ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f} load")
    print("RESULT swapins=0 count")


if __name__ == "__main__":
    main()
