#!/usr/bin/env python3
"""D8 verifier-2 own harness — independent re-measure of D8-01, D8-02, D8-INST.

METRIC (three independent re-measures, own code and own family table):

  A. D8-01: foreign entities strictly inside each of the brief's seven named
     families' span in the English-display-name alphabetical order, over the
     entities the real ``async_setup_entry`` builds on one all-features
     install.  Family membership is MY OWN explicit translation-key table
     (no regex); the span code is written from positions, independently.
     Extras the finder did not print: the DISTINCT foreign-entity count (the
     finder's total double-counts an entity intruding in two families), the
     exact null expectation for a uniformly random family of the same size,
     a UI-section variant (a real HA device page sorts enabled primary and
     diagnostic entities in SEPARATE sections, so only same-section entities
     interleave), and a literal-prefix test per family.

  B. D8-02: icons.json coverage as a 2x2 table over (device_class declared,
     icons entry present) for every translation-keyed entity, device_class
     read the corrected way (property if the stub had one, else ``_attr_``).

  C. D8-INST (REDUCTION STATED: 1 cell of the finder's 75, 1 cycle of its 2,
     same real solve): the stub-gap instrument read.  For every entity, the
     property-only read (``getattr(ent, "device_class")`` etc.) versus the
     corrected ``_attr_`` read, and D8's four checks — enum state outside
     options, non-numeric MEASUREMENT, naive TIMESTAMP, unit on a
     non-numeric device class — computed under BOTH reads.  The vacuousness
     claim: all four read 0 under the property read regardless of the tree;
     the corrected read is live iff some check or the declared counts move.

COMMAND (from a tree root):

    PYTHONPATH=tests/hastub \
      /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D8/verify2_own.py [--perturb cost-prefix|drop-icon2]

EXPECTED (branch head 0855277; findings measured at 7dd68dd and re-run
identical there by the finder's own harness at this head, 8-core Apple M1,
counts only, contention-immune):
    own_entities=74
    A: own_name_intruders_total=159  own_distinct_foreign=110-ish (see run)
       tariff=60 dhw=7 learning=45 accuracy=29 ecl110=0 pv=0 card_headline=18
       --perturb cost-prefix: own_name_intruders_total falls, tariff=0
    B: own_entity_without_icon=4 (optimal_setpoint, outdoor_temperature_optimizer,
       measured_power, compressor_frequency_advisor)
       own_dc_with_icon=31  own_nodc_without_icon=0
       --perturb drop-icon2: own_entity_without_icon=5
    C: own_vacuous_dc_reads>0 own_vacuous_sc_reads>0 own_vacuous_cat_reads>0
       prop-read checks: all four 0; corrected read: timestamp_naive>=1
       own_declared_entity_category=20 (=1500 over the finder's 75 cells)
"""
from __future__ import annotations

import os

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import asyncio  # noqa: E402
import json  # noqa: E402
import random  # noqa: E402
import sys  # noqa: E402
from datetime import timedelta  # noqa: E402
from pathlib import Path  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.components.sensor import NON_NUMERIC_DEVICE_CLASSES  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

from golden import START, coordinator_scenarios  # noqa: E402

from heatpump_optimizer import binary_sensor, button, climate, sensor, switch  # noqa: E402
from heatpump_optimizer import datetime as datetime_platform  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

PERTURB = (
    sys.argv[sys.argv.index("--perturb") + 1]
    if "--perturb" in sys.argv and len(sys.argv) > sys.argv.index("--perturb") + 1
    else ""
)

ROOT = Path("custom_components/heatpump_optimizer")

PLATFORMS = {
    "sensor": sensor,
    "binary_sensor": binary_sensor,
    "button": button,
    "climate": climate,
    "switch": switch,
    "datetime": datetime_platform,
}

# MY OWN family table — membership by translation key, written by hand from
# the entity list, against the seven families D8.md names.  No regex.
FAMILIES: dict[str, frozenset[str]] = {
    "dhw": frozenset({
        "boost_dhw", "dhw_cost", "dhw_energy", "dhw_heating_cost",
        "dhw_heating_plan", "dhw_heating_schedule", "dhw_heavy_day_demand",
        "dhw_mixed_water", "dhw_setpoint_advisor", "dhw_temperature",
    }),
    "tariff": frozenset({
        "baseline_cost", "predicted_cost", "total_heating_cost",
        "current_electricity_price", "contract_comparison",
        "monthly_peak_power", "power_headroom",
    }),
    "learning": frozenset({
        "comfort_weight", "reset_learned_comfort_weight",
        "run_system_identification", "estimated_cop", "observed_cop",
    }),
    "accuracy": frozenset({
        "prediction_accuracy", "diagnose_last_interval", "optimization_score",
    }),
    "ecl110": frozenset({"ecl110_displace", "ecl110_effective_displace"}),
    "pv": frozenset({"solar_irradiance", "solar_heat_gain", "solar_surplus_forecast"}),
    "card_headline": frozenset({
        "predicted_savings", "savings_percentage", "optimization_score",
        "plan_narrative", "monthly_savings",
    }),
}

#: My own rename for the perturbation arm: the six PRIMARY tariff members.
#: (The seventh, contract_comparison, is diagnostic AND disabled by default,
#: so it never sorts against the others on a real device page.)
COST_RENAMES = {
    "baseline_cost": "Cost Baseline",
    "predicted_cost": "Cost Predicted",
    "total_heating_cost": "Cost Total Heating (lifetime)",
    "current_electricity_price": "Cost Electricity Price (now)",
    "monthly_peak_power": "Cost Monthly Peak Power",
    "power_headroom": "Cost Power Headroom",
}

#: Input states so a real solve has live readings (first slot of the
#: finder's two-slot table; this harness runs one cycle only).
STATES = {
    "sensor.indoor": ("21.4", "°C"), "sensor.outdoor": ("-3.0", "°C"),
    "sensor.dhw_temp": ("52.0", "°C"), "sensor.upper": ("21.1", "°C"),
    "sensor.lower": ("20.6", "°C"), "sensor.buffer": ("41.0", "°C"),
    "sensor.wood_top": ("78.0", "°C"), "sensor.wood_bottom": ("44.0", "°C"),
    "sensor.pv_now": ("2.6", "kW"), "sensor.pump_freq": ("48.0", "Hz"),
    "number.pump_freq": ("48.0", "Hz"), "number.valve_target": ("34.0", "°C"),
    "select.pump_mode": ("heat", None),
    "binary_sensor.pump_defrost": ("off", None),
    "binary_sensor.pump_online": ("on", None),
    "binary_sensor.pump_fault": ("off", None),
    "input_boolean.holiday": ("off", None),
    "sensor.pump_power": ("2.20", "kW"), "sensor.pump_energy": ("1234.5", "kWh"),
    "sensor.house_power": ("3.90", "kW"), "sensor.floor_return": ("31.5", "°C"),
    "sensor.solar_rad": ("180.0", "W/m²"), "sensor.humidity": ("41.0", "%"),
}


def corrected(ent, prop: str):
    """Property-first, ``_attr_`` fallback — the read D8-INST says is live."""
    via_prop = getattr(ent, prop, None)
    if via_prop is not None:
        return via_prop
    return getattr(ent, f"_attr_{prop}", None)


def build_entities(with_solve: bool):
    cfg = dict(coordinator_scenarios()["coord_all_features"])
    cfg.update(
        {
            "indoor_temp_entity": "sensor.indoor",
            "outdoor_temp_entity": "sensor.outdoor",
            "dhw_tank_volume": 200.0,
            "mixing_valve_mode": "smart_write",
            "mixing_valve_write_entity": "number.valve_target",
            "ecl110_state_topic": "ecl110/flow_temp_control/displace",
            "wood_furnace_enabled": True,
            "compressor_freq_entity": "number.pump_freq",
            "contract_fixed_price": 1.2,
            "pv_enabled": True,
            "pv_peak_kw": 8.0,
            "pv_export_price": 0.3,
            "pv_production_entity": "sensor.pv_now",
            "peak_tariff_enabled": True,
            "peak_tariff_price_per_kw": 45.0,
            "grid_fee_mode": "rules",
            "grid_fee_rules": "Mon-Fri 06:00-22:00 = 0.25",
            "heat_pump_mode_entity": "select.pump_mode",
            "heat_pump_defrost_entity": "binary_sensor.pump_defrost",
            "heat_pump_online_entity": "binary_sensor.pump_online",
            "heat_pump_fault_entity": "binary_sensor.pump_fault",
            "compressor_freq_sensor": "sensor.pump_freq",
            "heat_pump_power_entity": "sensor.pump_power",
            "heat_pump_energy_entity": "sensor.pump_energy",
            "house_power_entity": "sensor.house_power",
            "floor_return_temp_entity": "sensor.floor_return",
            "solar_radiation_entity": "sensor.solar_rad",
            "indoor_humidity_entity": "sensor.humidity",
            "buffer_tank_temp_entity": "sensor.buffer",
            "dhw_temp_entity": "sensor.dhw_temp",
            "upper_floor_temp_entity": "sensor.upper",
            "lower_floor_temp_entity": "sensor.lower",
            "wood_tank_top_entity": "sensor.wood_top",
            "wood_tank_bottom_entity": "sensor.wood_bottom",
            "away_enabled": True,
            "away_presence_entity": "input_boolean.holiday",
            "away_temperature": 17.0,
        }
    )
    hass = FakeHass()
    for eid, (val, unit) in STATES.items():
        hass.states.set(eid, FakeState(val, unit=unit))
    entry = FakeEntry(data=cfg)
    coord = HeatPumpOptimizerCoordinator(hass, entry)

    def series():
        coord._prices = [
            {"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
             "starts_at": (START + timedelta(hours=h)).isoformat(),
             "level": "NORMAL"}
            for h in range(48)
        ]
        coord._weather_forecast = [
            {"datetime": (START + timedelta(hours=h)).isoformat(),
             "temperature": -5.0 + 3.0 * (h % 24) / 24.0, "wind_speed": 3.0,
             "precipitation": 0.0, "humidity": 85.0}
            for h in range(48)
        ]
        coord._solar_radiation_forecast = [
            max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)
        ]

    series()
    asyncio.run(coord._update_current_state())
    series()
    coord._forecast_arrays()
    if with_solve:
        asyncio.run(coord.async_run_optimization())
    coord.data = coord._build_data_dict()

    ents = []
    for pname, module in PLATFORMS.items():
        added: list = []
        entry.runtime_data = coord
        asyncio.run(module.async_setup_entry(hass, entry, lambda e: added.extend(e)))
        for e in added:
            ents.append((pname, e))
    return ents


def span_intruders_positions(order, members):
    """Own span code: positions, index arithmetic, no slices."""
    pos = [i for i, nm in enumerate(order) if nm in members]
    if len(pos) < 2:
        return 0, 0
    n_in = sum(1 for i in range(pos[0], pos[-1] + 1) if order[i] not in members)
    breaks = sum(1 for a, b in zip(pos, pos[1:]) if b != a + 1)
    return n_in, breaks


def main() -> int:
    dt_util.freeze(START)
    try:
        ents = build_entities(with_solve=True)
    finally:
        dt_util.freeze(None)

    en = json.loads((ROOT / "translations" / "en.json").read_text())["entity"]

    rows = []
    for platform, ent in ents:
        tk = getattr(ent, "_attr_translation_key", None)
        name = (
            en.get(platform, {}).get(tk, {}).get("name")
            if tk is not None
            else None
        )
        if name is None and platform != "climate":
            name = type(ent).__name__  # unseen in practice; keeps the sort total
        rows.append(
            {
                "platform": platform,
                "tk": tk,
                "name": name if tk is not None else ("",),
                "name_s": name or "",
                "eid": getattr(ent, "entity_id", None) or "",
                "enabled": bool(getattr(ent, "_attr_entity_registry_enabled_default", True)),
                "category": str(corrected(ent, "entity_category") or ""),
                "ent": ent,
            }
        )

    if PERTURB == "cost-prefix":
        for r in rows:
            if r["tk"] in COST_RENAMES:
                r["name_s"] = COST_RENAMES[r["tk"]]

    print(f"RESULT own_entities={len(rows)} count")

    # ---- A. D8-01 ---------------------------------------------------------
    order = sorted(range(len(rows)), key=lambda i: rows[i]["name_s"])
    names = [rows[i]["name_s"] for i in order]
    total = 0
    distinct = set()
    n_named = len(rows)
    null_total = 0.0
    rng = random.Random(20260912)
    report_fam = {}
    for fam, keys in FAMILIES.items():
        member_ids = {rows[i]["eid"] for i, r in enumerate(rows) if r["tk"] in keys}
        n, breaks = span_intruders_positions(
            [rows[i]["eid"] for i in order], member_ids
        )
        total += n
        who = {
            rows[i]["eid"]
            for i in range(len(order))
            if rows[i]["eid"] not in member_ids
            and any(
                rows[j]["eid"] in member_ids for j in range(len(order))
            )
        }
        # recompute 'who' honestly: inside the span
        idx = [i for i in range(len(order)) if rows[i]["eid"] in member_ids]
        who = {
            rows[i]["eid"]
            for i in range(idx[0], idx[-1] + 1)
            if rows[i]["eid"] not in member_ids
        } if len(idx) >= 2 else set()
        distinct |= who
        k = len(member_ids)
        expect = (n_named - k) * (k - 1) / (k + 1)
        null_total += expect
        # UI-section variant: same category AND enabled only
        sec_n = 0
        for cat in ("", "diagnostic"):
            sec_rows = [
                rows[i]
                for i in order
                if rows[i]["category"] == cat and rows[i]["enabled"]
            ]
            sec_members = {r["eid"] for r in sec_rows if r["tk"] in keys}
            s, _b = span_intruders_positions(
                [r["eid"] for r in sec_rows], sec_members
            )
            sec_n += s
        # literal prefix over the family's names
        fam_names = sorted(r["name_s"] for r in rows if r["tk"] in keys)
        pref = os.path.commonprefix(fam_names) if fam_names else ""
        report_fam[fam] = {
            "n": k, "intruders": n, "breaks": breaks,
            "null_expect": round(expect, 1), "ui_section_intruders": sec_n,
            "common_prefix": pref,
        }
        print(
            f"# fam {fam:<14} n={k:<3} intruders={n:<3} breaks={breaks} "
            f"null={expect:.1f} ui_section={sec_n} prefix={pref!r}"
        )

    # simulate the null once, to check the closed form
    sim_total = 0
    ids = [rows[i]["eid"] for i in order]
    for fam, keys in FAMILIES.items():
        k = sum(1 for r in rows if r["tk"] in keys)
        acc = 0
        for _ in range(2000):
            sample = set(rng.sample(ids, k))
            s, _ = span_intruders_positions(ids, sample)
            acc += s
        sim_total += acc / 2000

    print(f"RESULT own_name_intruders_total={total} entities")
    print(f"RESULT own_distinct_foreign_intruders={len(distinct)} entities")
    print(f"RESULT own_null_expected_total={null_total:.1f} entities")
    print(f"RESULT own_null_simulated_total={sim_total:.1f} entities")

    # ---- B. D8-02 ---------------------------------------------------------
    icons = json.loads((ROOT / "icons.json").read_text()).get("entity", {})
    if PERTURB == "drop-icon2":
        icons.get("sensor", {}).pop("dhw_temperature", None)
    dc_icon = dc_noicon = nodc_icon = nodc_noicon = 0
    noicon_list = []
    for r in rows:
        if r["tk"] is None:
            continue
        has_icon = r["tk"] in icons.get(r["platform"], {})
        dc = corrected(r["ent"], "device_class")
        if dc is not None and has_icon:
            dc_icon += 1
        elif dc is not None and not has_icon:
            dc_noicon += 1
            noicon_list.append(f"{r['platform']}.{r['tk']}")
        elif dc is None and has_icon:
            nodc_icon += 1
        else:
            nodc_noicon += 1
    print(f"RESULT own_entity_without_icon={dc_noicon + nodc_noicon} entities")
    print(f"RESULT own_without_icon_list={sorted(noicon_list)} entities")
    print(f"RESULT own_dc_with_icon={dc_icon} entities")
    print(f"RESULT own_dc_without_icon={dc_noicon} entities")
    print(f"RESULT own_nodc_with_icon={nodc_icon} entities")
    print(f"RESULT own_nodc_without_icon={nodc_noicon} entities")

    # ---- C. D8-INST -------------------------------------------------------
    vac_dc = vac_sc = vac_cat = 0
    dec_dc = dec_sc = dec_cat = 0
    for _p, ent in ents:
        p_dc, a_dc = getattr(ent, "device_class", None), getattr(ent, "_attr_device_class", None)
        p_sc, a_sc = getattr(ent, "state_class", None), getattr(ent, "_attr_state_class", None)
        p_ct, a_ct = getattr(ent, "entity_category", None), getattr(ent, "_attr_entity_category", None)
        if a_dc is not None and p_dc is None:
            vac_dc += 1
        if a_sc is not None and p_sc is None:
            vac_sc += 1
        if a_ct is not None and p_ct is None:
            vac_cat += 1
        dec_dc += a_dc is not None
        dec_sc += a_sc is not None
        dec_cat += a_ct is not None
    print(f"RESULT own_vacuous_device_class_reads={vac_dc} entities")
    print(f"RESULT own_vacuous_state_class_reads={vac_sc} entities")
    print(f"RESULT own_vacuous_entity_category_reads={vac_cat} entities")
    print(f"RESULT own_declared_device_class={dec_dc} entities")
    print(f"RESULT own_declared_state_class={dec_sc} entities")
    print(f"RESULT own_declared_entity_category={dec_cat} entities")

    # the four checks under both reads, over the solved payload
    def four_checks(prop_read: bool):
        counts = {"enum": 0, "nonnumeric": 0, "naive": 0, "unit": 0}
        for _p, ent in ents:
            if type(ent).__module__ is None or not hasattr(ent, "native_value"):
                continue
            get = (lambda e, a: getattr(e, a, None)) if prop_read else corrected
            dc = get(ent, "device_class")
            sc = get(ent, "state_class")
            try:
                val = ent.native_value
            except Exception:
                continue
            if val is None:
                continue
            opts = getattr(ent, "_attr_options", None)
            if str(dc) == "enum" and opts and val not in opts:
                counts["enum"] += 1
            if str(sc) == "measurement" and not isinstance(val, (int, float)):
                counts["nonnumeric"] += 1
            import datetime as _d
            if str(dc) == "timestamp" and isinstance(val, _d.datetime) and val.tzinfo is None:
                counts["naive"] += 1
            unit = getattr(ent, "_attr_native_unit_of_measurement", None)
            if dc in NON_NUMERIC_DEVICE_CLASSES and unit:
                counts["unit"] += 1
        return counts

    prop = four_checks(True)
    corr = four_checks(False)
    print(f"RESULT own_checks_property_read={prop} counts")
    print(f"RESULT own_checks_corrected_read={corr} counts")
    print(f"RESULT own_entity_category_x75={dec_cat * 75} entity_cells")

    out = Path("tools/audit/round4/D8/verify2_own_detail.json")
    out.write_text(
        json.dumps(
            {"families": report_fam, "icons": noicon_list},
            indent=1, sort_keys=True, ensure_ascii=False,
        )
    )
    print(f"# detail written to {out}")
    import resource

    print("RESULT thread_factor=1.00 ratio")
    print("RESULT timing_results_reported=0 count")
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap} count")
    print(f"RESULT load1={os.getloadavg()[0]:.2f} load")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
