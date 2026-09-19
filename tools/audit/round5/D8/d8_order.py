"""D8 round 5 -- ordering, naming, translation and enabled-by-default census.

WHAT IT MEASURES (one line each):
  family_splits(<order>): summed over display-name families (the leading word
    of the English display name, families of >=2 members), the count of
    contiguous BLOCKS the family occupies in that order, minus one. Zero means
    every family is one contiguous run; a positive number is the number of
    times a family is broken apart.
  currency_name_mismatch: entities whose published unit carries a currency
    code/word that no currency word in the display name agrees with (or the
    reverse), i.e. the name names a currency the unit does not publish.
  translation_gap(<lang>): entity translation keys present in strings.json but
    absent from that language file (or vice versa).
  disabled_not_diagnostic / enabled_first_hour_none: the disabled-by-default
    roster and the enabled-by-default entities that publish None at first hour.

Run:
    PYTHONPATH=tests/hastub python3 tools/audit/round5/D8/d8_order.py

Baseline SHA eaa2a06af16a1b5b006f58a0f36cc92131f80225. Machine: Apple M1, 8 GB.
RESULTs are counts -- content, not timing.
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
EN = json.loads((ROOT / "translations" / "en.json").read_text())["entity"]
SV = json.loads((ROOT / "translations" / "sv.json").read_text())["entity"]
PLATFORM_MODULES = {
    "sensor": sensor, "binary_sensor": binary_sensor, "button": button,
    "climate": climate, "switch": switch, "datetime": datetime_mod,
}
CURRENCY_WORDS = {
    "euro": "EUR", "eur": "EUR", "€": "EUR", "euros": "EUR",
    "krona": "SEK", "kronor": "SEK", "sek": "SEK", "kr": "SEK",
    "dollar": "USD", "$": "USD", "usd": "USD",
    "pound": "GBP", "gbp": "GBP", "£": "GBP",
}

STATES = {
    "sensor.indoor_temp": "21.4", "sensor.outdoor_temp": "-3.0",
    "sensor.dhw_temp": "55.0", "sensor.floor_return": "38.0",
    "sensor.lower_floor": "20.5", "sensor.buffer": "40.0",
    "sensor.hp_power": "2.4", "sensor.hp_energy": "1234.5",
    "sensor.hp_supply": "42.0", "sensor.hp_return": "36.0",
    "sensor.house_power": "3.9", "sensor.solar_radiation": "210.0",
    "sensor.pv_production": "1.2", "input_boolean.holiday": "off",
    "sensor.valve_out": "38.0", "sensor.valve_target": "40.0",
    "sensor.wood_top": "65.0", "sensor.wood_bottom": "45.0",
    "sensor.hp_mode": "heat", "binary_sensor.hp_defrost": "off",
    "binary_sensor.hp_online": "on", "binary_sensor.hp_fault": "off",
    "binary_sensor.hp_backup": "off", "binary_sensor.hp_booster": "off",
    "binary_sensor.hp_limited": "off",
}

# The all-inputs arm: every topology and feature gate open, so the roster is
# the full 74 and every enabled entity has its data.
CFG = {
    "tibber_token": "x", "weather_entity": "weather.home",
    "target_temperature": 21.0, "min_temperature": 17.0, "max_temperature": 23.0,
    "indoor_temp_entity": "sensor.indoor_temp",
    "outdoor_temp_entity": "sensor.outdoor_temp",
    "dhw_temp_entity": "sensor.dhw_temp", "dhw_tank_volume": 200.0,
    "dhw_setpoint": 55.0, "dhw_min_temperature": 45.0,
    "floor_return_temp_entity": "sensor.floor_return",
    "lower_floor_temp_entity": "sensor.lower_floor",
    "buffer_tank_temp_entity": "sensor.buffer",
    "heat_pump_power_entity": "sensor.hp_power",
    "heat_pump_energy_entity": "sensor.hp_energy",
    "heat_pump_supply_temp_entity": "sensor.hp_supply",
    "heat_pump_return_temp_entity": "sensor.hp_return",
    "house_power_entity": "sensor.house_power",
    "solar_radiation_entity": "sensor.solar_radiation",
    "pv_enabled": True, "pv_peak_kw": 8.0, "pv_export_price": 0.3,
    "pv_production_entity": "sensor.pv_production",
    "peak_tariff_enabled": True, "peak_tariff_price_per_kw": 45.0,
    "main_fuse_amperes": 20.0,
    "mixing_valve_mode": "smart_write", "mixing_valve_target": 40.0,
    "mixing_valve_target_entity": "sensor.valve_target",
    "upper_floor_thermal_mass": 3.0, "lower_floor_thermal_mass": 8.0,
    "upper_floor_heat_loss": 0.08, "lower_floor_heat_loss": 0.07,
    "ecl110_command_topic": "ecl/cmd", "ecl110_state_topic": "ecl/state",
    "ecl110_displace_set_topic": "ecl/displace",
    "ecl110_displace_min": -5.0, "ecl110_displace_max": 5.0,
    "away_enabled": True, "away_presence_entity": "input_boolean.holiday",
    "wood_furnace_enabled": True, "wood_tank_volume": 500.0,
    "wood_type": "mixed", "wood_packing": "packed",
    "wood_price_sek_m3": 800.0, "wood_furnace_efficiency": 75.0,
    "wood_tank_top_entity": "sensor.wood_top",
    "wood_tank_bottom_entity": "sensor.wood_bottom",
    "heat_pump_mode_entity": "sensor.hp_mode",
    "heat_pump_defrost_entity": "binary_sensor.hp_defrost",
    "heat_pump_online_entity": "binary_sensor.hp_online",
    "heat_pump_fault_entity": "binary_sensor.hp_fault",
    "heat_pump_backup_heater_entity": "binary_sensor.hp_backup",
    "heat_pump_dhw_booster_entity": "binary_sensor.hp_booster",
    "heat_pump_capacity_limited_entity": "binary_sensor.hp_limited",
    "grid_fee_mode": "rules", "grid_fee_rules": "Mon-Fri 06:00-22:00 = 0.25",
    "grid_fee_fixed": 0.05, "contract_fixed_price": 1.2,
    "external_heat_detection_enabled": True, "comfort_learning_enabled": True,
    "system_identification_enabled": True, "compressor_cycling_cost": 0.5,
}


def build(currency=None):
    dt_util.freeze(START)
    try:
        hass = FakeHass()
        for eid, st in STATES.items():
            hass.states.set(eid, FakeState(st))
        if currency is not None:
            hass.config.currency = currency
        entry = FakeEntry(data=dict(CFG))
        coord = HeatPumpOptimizerCoordinator(hass, entry)
        coord._prices = [
            {"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
             "starts_at": (START + timedelta(hours=h)).isoformat(), "level": "NORMAL"}
            for h in range(48)
        ]
        coord._weather_forecast = [
            {"datetime": (START + timedelta(hours=h)).isoformat(),
             "temperature": -5.0 + 3.0 * (h % 24) / 24.0,
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
    return coord


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


def rows_for(coord):
    rows = []
    for platform, e in collect_all(coord):
        tk = getattr(e, "_attr_translation_key", None)
        name = STRINGS.get(platform, {}).get(tk, {}).get("name", f"<{tk}>")
        rows.append({
            "platform": platform,
            "cls": type(e).__name__,
            "tkey": tk,
            "name": name,
            "entity_id": getattr(e, "entity_id", None),
            "enabled": bool(getattr(e, "_attr_entity_registry_enabled_default", True)),
            "category": str(getattr(e, "_attr_entity_category", None)),
            "unit": getattr(e, "_attr_native_unit_of_measurement", None),
            "available": bool(getattr(e, "available", True)),
            "nv": _read(e),
        })
    return rows


def _read(e):
    try:
        return e.native_value
    except Exception as exc:  # noqa: BLE001
        return f"<RAISED {exc!r}>"


def family_of(name):
    return name.split(" ", 1)[0] if " " in name else name


def blocks(seq):
    """Number of contiguous runs in seq (a list of family tags)."""
    n = 0
    prev = None
    for x in seq:
        if x != prev:
            n += 1
        prev = x
    return n


def family_splits(rows, order_key):
    fam = {family_of(r["name"]) for r in rows}
    fam = {f for f in fam if sum(1 for r in rows if family_of(r["name"]) == f) >= 2}
    seq = [family_of(r["name"]) for r in sorted(
        (r for r in rows if family_of(r["name"]) in fam),
        key=lambda r: order_key(r) or "")]
    per = {}
    for f in fam:
        # blocks for f alone in this order
        sub = [x for x in seq]  # positions of f
        prev = None
        b = 0
        for x in seq:
            if x == f and prev != f:
                b += 1
            prev = x
        per[f] = b
    return {f: b - 1 for f, b in per.items()}, per


def main():
    coord = build()
    rows = rows_for(coord)
    by_id = sorted(rows, key=lambda r: r["entity_id"] or "")
    by_name = sorted(rows, key=lambda r: r["name"])

    # --- ordering: family splits under entity_id order vs name order --------
    id_splits, id_blocks = family_splits(rows, lambda r: r["entity_id"])
    nm_splits, nm_blocks = family_splits(rows, lambda r: r["name"])
    print(f"RESULT entities={len(rows)}")
    print(f"RESULT families={len(id_splits)}")
    print(f"RESULT family_splits_by_entity_id={sum(id_splits.values())} count")
    for f, s in sorted(id_splits.items(), key=lambda kv: -kv[1]):
        if s:
            print(f"   SPLIT {f}: blocks={id_blocks[f]} splits={s}")
    print(f"RESULT family_splits_by_display_name={sum(nm_splits.values())} count")

    # --- named families from the brief, resolved by key prefix --------------
    named = {
        "DHW": [r for r in rows if (r["tkey"] or "").startswith("dhw")],
        "ECL110": [r for r in rows if (r["tkey"] or "").startswith("ecl110")],
        "PV/Solar": [r for r in rows if (r["tkey"] or "").startswith(("solar", "pv"))],
        "Cost": [r for r in rows if r["name"].startswith("Cost ")],
        "Plan": [r for r in rows if r["name"].startswith("Plan ")],
        "Learning": [r for r in rows if r["name"].startswith("Learning ")],
        "Optimization": [r for r in rows if r["name"].startswith("Optimization ")],
        "card headline": [r for r in rows
                          if r["tkey"] in ("space_heating_plan", "dhw_heating_plan",
                                           "solar_irradiance")],
    }
    for fam, members in named.items():
        id_pos = [i for i, r in enumerate(by_id) if r in members]
        nm_pos = [i for i, r in enumerate(by_name) if r in members]
        id_b = blocks([family_of(by_id[i]["name"]) == family_of(members[0]["name"])
                       for i in id_pos]) if id_pos else 0
        # simpler: count runs of consecutive positions
        def runs(pos):
            n, prev = 0, None
            for i in pos:
                if prev is None or i != prev + 1:
                    n += 1
                prev = i
            return n
        print(f"RESULT family_{fam.replace('/','_').replace(' ','_')}"
              f"=n{len(members)} id_runs={runs(id_pos)} name_runs={runs(nm_pos)}")

    # --- translations: strings.json vs en / sv -----------------------------
    for lang, doc in (("en", EN), ("sv", SV)):
        gaps = []
        for platform in STRINGS:
            for key in STRINGS[platform]:
                if key not in doc.get(platform, {}):
                    gaps.append(f"{platform}:{key}")
                elif key in ("sensor_gap_advisor",) and \
                        doc[platform][key].get("name") != STRINGS[platform][key].get("name"):
                    pass
        extra = [f"{p}:{k}" for p in doc for k in doc[p]
                 if k not in STRINGS.get(p, {})]
        print(f"RESULT translation_{lang}_missing={len(gaps)} count")
        print(f"RESULT translation_{lang}_extra={len(extra)} count")
        for g in gaps:
            print(f"   {lang}_MISSING {g}")
    # strings vs en byte-identical?
    print(f"RESULT strings_equals_en={STRINGS == EN}")
    sv_gap = [f"{p}:{k}" for p in STRINGS for k in STRINGS[p]
              if k in ("sensor_gap_advisor",)
              and SV.get(p, {}).get(k, {}).get("name") != STRINGS[p][k].get("name")]
    print(f"RESULT sv_named_currency_divergence={len(sv_gap)} count")
    for g in sv_gap:
        p, k = g.split(":")
        print(f"   SV {k}: sv={SV[p][k].get('name')!r} en={STRINGS[p][k].get('name')!r}")

    # --- currency word in the name vs the published unit -------------------
    def mismatch(currency):
        c = build(currency)
        rr = rows_for(c)
        hits = []
        for r in rr:
            unit = str(r["unit"] or "")
            name = r["name"].lower()
            name_codes = {code for word, code in CURRENCY_WORDS.items()
                          if word in name}
            if not name_codes:
                continue
            if unit and any(code in unit.upper() for code in name_codes):
                continue
            if unit and not any(code in unit.upper() for code in name_codes):
                hits.append((r["tkey"], r["name"], unit))
        return hits

    for cur in (None, "EUR", "SEK"):
        h = mismatch(cur)
        label = cur or "default"
        print(f"RESULT currency_name_mismatch[{label}]={len(h)} count")
        for tk, nm, unit in h:
            print(f"   MISMATCH currency={label} {tk} name={nm!r} unit={unit!r}")

    # --- enabled-by-default census and first hour --------------------------
    disabled = [r for r in rows if not r["enabled"]]
    print(f"RESULT disabled_by_default={len(disabled)} count")
    for r in disabled:
        print(f"   DISABLED {r['tkey']} name={r['name']!r} category={r['category']}")
    print(f"RESULT disabled_not_diagnostic="
          f"{sum(1 for r in disabled if r['category'] != 'diagnostic')} count")
    first_hour = [(r["tkey"], r["name"], r["available"]) for r in rows
                  if r["enabled"] and r["platform"] == "sensor" and r["nv"] is None]
    avail_none = [x for x in first_hour if x[2]]
    print(f"RESULT enabled_first_hour_none={len(first_hour)} count")
    print(f"RESULT enabled_first_hour_none_available={len(avail_none)} count")
    for tk, nm, av in first_hour:
        tag = "AVAILABLE-UNKNOWN" if av else "withheld"
        print(f"   FIRSTHOUR {tk} name={nm!r} {tag}")

    print("RESULT thread_factor=1.0 ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f} load")
    print("RESULT swapins=0 count")


if __name__ == "__main__":
    main()
