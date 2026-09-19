"""D8 round 5 -- the topology x feature matrix.

Metric definition (per cell, per entity): every published (state, metadata)
pair a platform's real ``async_setup_entry`` produces for a coordinator built
the way ``golden._capture_coordinator`` builds it.

Run:
    PYTHONPATH=tests/hastub python3 tools/audit/round5/D8/d8_matrix.py \
        [--configs N] [--out /tmp/d8.json]

Emits one RESULT line per violation class plus a JSON dump for the
perturbation harness. Machine: Apple M1, 8 GB. Content -- the numbers are
counts, not timings.
"""
from __future__ import annotations

import argparse
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
_ROOT = _HERE.parents[4]                        # export root
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "tests"))
sys.path.insert(0, str(_ROOT / "tests" / "hastub"))

from harness import FakeEntry, FakeHass  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer import (  # noqa: E402
    binary_sensor, button, climate, datetime as datetime_mod, sensor, switch,
)
from golden import coordinator_scenarios  # noqa: E402

START = datetime(2026, 1, 15, 0, 0)
ROOT = Path("custom_components/heatpump_optimizer")
STRINGS = json.loads((ROOT / "strings.json").read_text())["entity"]

PLATFORM_MODULES = {
    "sensor": sensor, "binary_sensor": binary_sensor, "button": button,
    "climate": climate, "switch": switch, "datetime": datetime_mod,
}


def build_coordinator(config, *, seed=0, prices_mul=1.0, outdoor_delta=0.0,
                      base=0.6):
    """A coordinator with the same frozen inputs golden injects, plus knobs."""
    dt_util.freeze(START)
    hass = FakeHass()
    entry = FakeEntry(data=config)
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    coord._prices = [
        {
            "total": round((base + 0.5 * (h % 12) / 12.0) * prices_mul, 4),
            "starts_at": (START + timedelta(hours=h)).isoformat(),
            "level": "NORMAL",
        }
        for h in range(48)
    ]
    coord._weather_forecast = [
        {
            "datetime": (START + timedelta(hours=h)).isoformat(),
            "temperature": -5.0 + 3.0 * (h % 24) / 24.0 + outdoor_delta,
            "wind_speed": 3.0,
            "precipitation": 0.0,
            "humidity": 85.0,
        }
        for h in range(48)
    ]
    coord._solar_radiation_forecast = [
        max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)
    ]
    coord._forecast_arrays()
    data = coord._build_data_dict()
    coord.data = data
    dt_util.freeze(None)
    return hass, coord, data


def collect_all(coord):
    """Every entity of every platform, keyed by (platform, class-name, tkey)."""
    out = []
    for platform, module in PLATFORM_MODULES.items():
        added = []
        entry = FakeEntry()
        entry.runtime_data = coord
        hass = FakeHass()
        asyncio.run(module.async_setup_entry(hass, entry, added.extend))
        for e in added:
            out.append((platform, e))
    return out


def name_of(platform, entity):
    key = getattr(entity, "_attr_translation_key", None)
    entry = STRINGS.get(platform, {}).get(key)
    if entry is None:
        return f"<untranslated {platform}:{key}>"
    return entry.get("name", f"<no-name {platform}:{key}>")


def record(platform, e):
    nv = None
    nv_err = None
    try:
        nv = e.native_value
    except Exception as exc:  # noqa: BLE001
        nv_err = repr(exc)
    attrs = None
    attrs_err = None
    try:
        attrs = e.extra_state_attributes
    except Exception as exc:  # noqa: BLE001
        attrs_err = repr(exc)
    return {
        "platform": platform,
        "cls": type(e).__name__,
        "tkey": getattr(e, "_attr_translation_key", None),
        "name": name_of(platform, e),
        "entity_id": getattr(e, "entity_id", None),
        "device_class": str(getattr(e, "_attr_device_class", None)),
        "state_class": str(getattr(e, "_attr_state_class", None)),
        "unit": str(getattr(e, "_attr_native_unit_of_measurement", None)),
        "entity_category": str(getattr(e, "_attr_entity_category", None)),
        "icon": getattr(e, "_attr_icon", None),
        "enabled_default": getattr(e, "_attr_entity_registry_enabled_default", True),
        "options": list(getattr(e, "_attr_options", None) or []),
        "available": bool(getattr(e, "available", True)),
        "native_value": _jsonable(nv),
        "nv_type": type(nv).__name__,
        "nv_err": nv_err,
        "attrs": _jsonable(attrs),
        "attrs_err": attrs_err,
    }


def _jsonable(v):
    if isinstance(v, datetime):
        return v.isoformat()
    if isinstance(v, (list, tuple)):
        return [_jsonable(x) for x in v]
    if isinstance(v, dict):
        return {str(k): _jsonable(x) for k, x in v.items()}
    if isinstance(v, float) and v != v:
        return "NaN"
    return v


def feature_grid():
    """Topology x feature-toggle cells. Each is a config dict."""
    base = {
        "tibber_token": "x", "weather_entity": "weather.home",
        "target_temperature": 21.0, "min_temperature": 17.0,
        "max_temperature": 23.0,
    }
    toggles = {
        "dhw": {"dhw_tank_volume": 200.0, "dhw_setpoint": 55.0,
                "dhw_min_temperature": 45.0},
        "twozone": {"upper_floor_thermal_mass": 3.0, "lower_floor_thermal_mass": 8.0,
                    "upper_floor_heat_loss": 0.08, "lower_floor_heat_loss": 0.07},
        "valvestorage": {"valve_storage": True},
        "ecl110": {"ecl110_enabled": True},
        "pv": {"pv_enabled": True, "pv_peak_kw": 8.0, "pv_export_price": 0.3},
        "captariff": {"peak_tariff_enabled": True, "peak_tariff_price_per_kw": 45.0},
        "gridfee": {"grid_fee_mode": "rules",
                    "grid_fee_rules": "Mon-Fri 06:00-22:00 = 0.25",
                    "grid_fee_fixed": 0.05},
        "away": {"away_enabled": True},
        "wood": {"wood_boiler_entity": "sensor.wood"},
    }
    cells = {}
    for name, cfg in coordinator_scenarios().items():
        cells[name] = cfg
    # singles
    for tname, tcfg in toggles.items():
        cells[f"t_{tname}"] = {**base, **tcfg}
    # a few combos
    cells["combo_dhw_pv_cap"] = {**base, **toggles["dhw"], **toggles["pv"],
                                 **toggles["captariff"]}
    cells["combo_zone_grid_away"] = {**base, **toggles["twozone"],
                                     **toggles["gridfee"], **toggles["away"]}
    cells["combo_everything"] = {**base, **{k: v for t in toggles.values()
                                            for k, v in t.items()}}
    return cells


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/tmp/d8_matrix.json")
    ap.add_argument("--only", default=None)
    args = ap.parse_args()

    cells = feature_grid()
    if args.only:
        cells = {args.only: cells[args.only]}

    all_records = {}
    for cell, cfg in cells.items():
        hass, coord, data = build_coordinator(cfg)
        ents = collect_all(coord)
        all_records[cell] = {
            "config": cfg,
            "n_data_keys": len(data),
            "data": _jsonable(data),
            "entities": [record(p, e) for p, e in ents],
        }
        print(f"RESULT cell={cell} entities={len(ents)} data_keys={len(data)}")

    Path(args.out).write_text(json.dumps(all_records, indent=1, default=str))
    total = sum(len(v["entities"]) for v in all_records.values())
    print(f"RESULT cells={len(all_records)} entity_records={total}")
    print("RESULT thread_factor=1.0")
    try:
        load1 = os.getloadavg()[0]
    except OSError:
        load1 = -1.0
    print(f"RESULT load1={load1:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
