#!/usr/bin/env python3
"""Verifier-3 own harness for D8-01 / D8-02 / D8-INST (round 4, seat verify-0-3).

METRIC (mine, differing from the finder's where noted):

D8-01  For each of the seven families the D8 BRIEF names (dhw, tariff,
       learning, accuracy, ecl110, pv, card headline), with membership by my
       own regexes (written from the brief's words, not copied from the
       finder; the card-headline family is derived from the card's own
       HEADLINE_SUFFIXES array), the number of non-member entities falling
       strictly inside the family's span — computed under TWO sort keys:
       (a) codepoint order (Python sorted, the finder's key) and
       (b) casefold order (closer to how the HA frontend collates names).
       Plus: distinct intruding entities (vs the summed slots), leave-one-
       family-out re-aggregation, a minimal-install re-aggregation, the
       shared-display-name-prefix test, and cross-family member overlap.

D8-02  A 2x2 cross-tab over translation-keyed entities: (declares a
       device class) x (has an icons.json entry), plus the reverse
       perturbation (give the four missing entities an icon in memory and
       the count must fall to 0) and a structure check that every icons
       entry carries a "default" mdi value.

D8-INST Over the same built entities: for each of device_class /
       state_class / entity_category, how many entities have the ``_attr_*``
       value set while the public property read (getattr with default)
       returns None — the vacuity the stub gap creates — plus whether the
       stub's SensorEntity has the property at all.

COMMAND (from the repo root):

    PYTHONPATH=tests/hastub \
      /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D8/verify3_own.py

EXPECTED (finder's numbers under the finder's definitions, for comparison):
    name_order_intruders (codepoint, all-features) = 159
    entity_without_icon_entry = 4;  control cross-tab 31 / 0
    entity_category_declared per all-features build = 20
All counts; no timing; contention-immune.  Baseline the finder measured:
7dd68dd; this run is at the branch head, which differs from baseline in the
finding-relevant files by a card version bump only.
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
import re  # noqa: E402
import sys  # noqa: E402
from datetime import timedelta  # noqa: E402
from pathlib import Path  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

from golden import START, coordinator_scenarios  # noqa: E402

from heatpump_optimizer import binary_sensor, button, climate, sensor, switch  # noqa: E402
from heatpump_optimizer import datetime as datetime_platform  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

ROOT = Path("custom_components/heatpump_optimizer")
PLATFORMS = {
    "sensor": sensor,
    "binary_sensor": binary_sensor,
    "button": button,
    "climate": climate,
    "switch": switch,
    "datetime": datetime_platform,
}

# --- MY family membership, from the brief's words (D8.md section 3) ----------
# dhw: domestic hot water; tariff: the money/price family; learning: what the
# learner/system-id writes; accuracy: how good the predictions are; ecl110; pv;
# card headline: parsed out of the card below.
MY_FAMILIES: dict[str, re.Pattern] = {
    "dhw": re.compile(r"dhw|hot_water|legionella|mixed_water", re.I),
    "tariff": re.compile(
        r"electricity_price|peak_power|headroom|contract|grid_fee"
        r"|baseline_cost|predicted_cost|total_heating_cost",
        re.I,
    ),
    "learning": re.compile(
        r"comfort_weight|system_identification|learned|estimated_cop|observed_cop",
        re.I,
    ),
    "accuracy": re.compile(r"prediction_accuracy|diagnose_last_interval|optimization_score", re.I),
    "ecl110": re.compile(r"ecl110", re.I),
    "pv": re.compile(r"solar|^pv_", re.I),
}

CARD_TEXT = (ROOT / "www" / "heatpump-optimizer-card.js").read_text()
_headline = re.search(r"HEADLINE_SUFFIXES = \[(.*?)\]", CARD_TEXT, re.S)
CARD_HEADLINE_SUFFIXES = re.findall(r'"(_[a-z0-9_]+)"', _headline.group(1)) if _headline else []


def build_entities(cfg: dict) -> list[dict]:
    """Every entity of every platform through the real async_setup_entry."""
    hass = FakeHass()
    for eid, val in (
        ("sensor.indoor", "21.4"),
        ("sensor.outdoor", "-3.0"),
        ("sensor.dhw_temp", "52.0"),
        ("sensor.upper", "21.1"),
        ("sensor.lower", "20.6"),
        ("sensor.buffer", "41.0"),
        ("sensor.wood_top", "78.0"),
        ("sensor.wood_bottom", "44.0"),
        ("sensor.pv_now", "2.6"),
        ("sensor.pump_freq", "48.0"),
        ("number.pump_freq", "48.0"),
        ("number.valve_target", "34.0"),
        ("select.pump_mode", "heat"),
        ("binary_sensor.pump_defrost", "off"),
        ("binary_sensor.pump_online", "on"),
        ("binary_sensor.pump_fault", "off"),
        ("input_boolean.holiday", "off"),
        ("sensor.pump_power", "2.20"),
        ("sensor.pump_energy", "1234.5"),
        ("sensor.house_power", "3.90"),
        ("sensor.floor_return", "31.5"),
        ("sensor.solar_rad", "180.0"),
        ("sensor.humidity", "41.0"),
    ):
        hass.states.set(eid, FakeState(val))
    cfg = {
        "indoor_temp_entity": "sensor.indoor",
        "outdoor_temp_entity": "sensor.outdoor",
        **cfg,
    }
    entry = FakeEntry(data=cfg)
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    coord._prices = [
        {
            "total": round(0.45 + 0.9 * ((h * 7) % 12) / 12.0, 4),
            "starts_at": (START + timedelta(hours=h)).isoformat(),
            "level": "NORMAL",
        }
        for h in range(48)
    ]
    coord._weather_forecast = [
        {
            "datetime": (START + timedelta(hours=h)).isoformat(),
            "temperature": -7.0 + 5.0 * ((h * 5) % 24) / 24.0,
            "wind_speed": 4.0,
            "precipitation": 0.0,
            "humidity": 80.0,
        }
        for h in range(48)
    ]
    coord._solar_radiation_forecast = [
        max(0.0, 160.0 * (1 - abs(11 - (h % 24)) / 11.0)) for h in range(48)
    ]
    dt_util.freeze(START)
    try:
        asyncio.run(coord._update_current_state())
        coord._forecast_arrays()
        coord.data = coord._build_data_dict()
        rows = []
        for pname, module in PLATFORMS.items():
            added: list = []
            entry.runtime_data = coord
            asyncio.run(module.async_setup_entry(hass, entry, lambda e: added.extend(e)))
            for ent in added:
                rows.append(
                    {
                        "platform": pname,
                        "entity_id": getattr(ent, "entity_id", None) or "",
                        "translation_key": getattr(ent, "_attr_translation_key", None),
                        # MY reads: _attr_* directly (see D8-INST for why the
                        # public property reads are vacuous under the stub).
                        # (first version of this wrapped the ternary in str()
                        # and turned a missing class into the truthy string
                        # "None"; caught by the inst probe disagreeing)
                        "device_class": _dc_str(getattr(ent, "_attr_device_class", None)),
                        "category": _dc_str(getattr(ent, "_attr_entity_category", None)),
                    }
                )
    finally:
        dt_util.freeze(None)
    return rows


ALL_FEATURES_OVERLAY: dict = {
    "dhw_enabled": True,
    "dhw_tank_volume": 200.0,
    "dhw_setpoint": 55.0,
    "dhw_min_temperature": 45.0,
    "dhw_windows": "06:00-08:30, 17:00-22:00",
    "dhw_temp_entity": "sensor.dhw_temp",
    "upper_floor_thermal_mass": 3.0,
    "lower_floor_thermal_mass": 8.0,
    "upper_floor_heat_loss": 0.08,
    "lower_floor_heat_loss": 0.07,
    "upper_floor_temp_entity": "sensor.upper",
    "lower_floor_temp_entity": "sensor.lower",
    "mixing_valve_mode": "smart_write",
    "mixing_valve_write_entity": "number.valve_target",
    "buffer_tank_volume": 500.0,
    "buffer_tank_temp_entity": "sensor.buffer",
    "wood_tank_top_entity": "sensor.wood_top",
    "wood_tank_bottom_entity": "sensor.wood_bottom",
    "wood_tank_volume": 750.0,
    "wood_furnace_enabled": True,
    "wood_type": "birch",
    "wood_price_sek_m3": 1200.0,
    "wood_furnace_efficiency": 0.75,
    "ecl110_state_topic": "ecl110/flow_temp_control/displace",
    "ecl110_displace_set_topic": "ecl110/flow_temp_control/displace/set",
    "ecl110_command_topic": "ecl110/command",
    "ecl110_displace_min": -20.0,
    "ecl110_displace_max": 20.0,
    "pv_enabled": True,
    "pv_peak_kw": 8.0,
    "pv_export_price": 0.3,
    "pv_production_entity": "sensor.pv_now",
    "peak_tariff_enabled": True,
    "peak_tariff_price_per_kw": 45.0,
    "peak_tariff_peaks_averaged": 3,
    "peak_tariff_window_minutes": 60,
    "grid_fee_mode": "rules",
    "grid_fee_rules": "Mon-Fri 06:00-22:00 = 0.25",
    "grid_fee_fixed": 0.05,
    "heat_pump_mode_entity": "select.pump_mode",
    "heat_pump_defrost_entity": "binary_sensor.pump_defrost",
    "heat_pump_online_entity": "binary_sensor.pump_online",
    "heat_pump_fault_entity": "binary_sensor.pump_fault",
    "compressor_freq_entity": "number.pump_freq",
    "compressor_freq_sensor": "sensor.pump_freq",
    "heat_pump_power_entity": "sensor.pump_power",
    "heat_pump_energy_entity": "sensor.pump_energy",
    "house_power_entity": "sensor.house_power",
    "floor_return_temp_entity": "sensor.floor_return",
    "solar_radiation_entity": "sensor.solar_rad",
    "indoor_humidity_entity": "sensor.humidity",
    "away_enabled": True,
    "away_presence_entity": "input_boolean.holiday",
    "away_temperature": 17.0,
    "away_dhw_min_temperature": 40.0,
    "contract_fixed_price": 1.2,
}


def _dc_str(v):
    """str-ify a (possibly enum) _attr_* value; None stays None."""
    if v is None:
        return None
    return str(getattr(v, "value", v))


def span(order: list[str], members: set[str]) -> tuple[int, int, list[str]]:
    idx = [i for i, x in enumerate(order) if x in members]
    if len(idx) < 2:
        return 0, 0, []
    lo, hi = idx[0], idx[-1]
    intr = [order[i] for i in range(lo, hi + 1) if order[i] not in members]
    breaks = sum(1 for a, b in zip(idx, idx[1:]) if b != a + 1)
    return len(intr), breaks, intr


def lcp(names: list[str]) -> str:
    if not names:
        return ""
    p = names[0]
    for n in names[1:]:
        while not n.startswith(p):
            p = p[:-1]
    return p


def d801(rows: list[dict], tag: str, out: dict) -> None:
    strings = json.loads((ROOT / "strings.json").read_text())["entity"]
    en = json.loads((ROOT / "translations" / "en.json").read_text())["entity"]

    def name_of(r):
        return (
            en.get(r["platform"], {}).get(r["translation_key"], {}).get("name")
            or strings.get(r["platform"], {}).get(r["translation_key"], {}).get("name")
        )

    for r in rows:
        r["name_en"] = name_of(r) or ("<device-named:climate>" if r["platform"] == "climate" else r["translation_key"] or r["entity_id"])

    fams = dict(MY_FAMILIES)
    # card headline family: grounded in the card's own suffix list
    fams["card_headline"] = re.compile(
        "^(" + "|".join(s.strip("_") for s in CARD_HEADLINE_SUFFIXES) + "|monthly_savings)$"
    )

    members: dict[str, set[str]] = {}
    for fam, pat in fams.items():
        members[fam] = {
            r["entity_id"]
            for r in rows
            if pat.search(r["translation_key"] or "") or pat.search(r["entity_id"])
        }

    # overlap: entities claimed by more than one audited family
    claims: dict[str, int] = {}
    for fam, mem in members.items():
        for e in mem:
            claims[e] = claims.get(e, 0) + 1
    overlap = sorted(e for e, c in claims.items() if c > 1)

    eids = [r["entity_id"] for r in rows]
    order_cp = [r["entity_id"] for r in sorted(rows, key=lambda r: r["name_en"])]
    order_cf = [r["entity_id"] for r in sorted(rows, key=lambda r: (r["name_en"].casefold(), r["name_en"]))]

    per_fam = {}
    tot_cp = tot_cf = 0
    all_intruders: set[str] = set()
    member_intruder_slots = 0
    member_ids = set().union(*members.values())
    for fam in fams:
        i_cp, b_cp, _ = span(order_cp, members[fam])
        i_cf, b_cf, intr_cf = span(order_cf, members[fam])
        tot_cp += i_cp
        tot_cf += i_cf
        all_intruders |= set(intr_cf)
        member_intruder_slots += sum(1 for e in intr_cf if e in member_ids)
        names = sorted(name_of(r) for r in rows if r["entity_id"] in members[fam] and name_of(r))
        pref = lcp(names)
        shared = len(pref) >= 3 and " " not in pref[:2]
        per_fam[fam] = {
            "n": len(members[fam]),
            "intruders_codepoint": i_cp,
            "breaks_codepoint": b_cp,
            "intruders_casefold": i_cf,
            "breaks_casefold": b_cf,
            "name_prefix": pref if shared else "",
        }
        print(
            f"# [{tag}] family {fam:<14} n={len(members[fam]):<3} "
            f"cp={i_cp:<3}/{b_cp}  cf={i_cf:<3}/{b_cf}  "
            f"prefix={per_fam[fam]['name_prefix'] or '-'}"
        )

    loo = {f: tot_cf - per_fam[f]["intruders_casefold"] for f in fams}
    zero_cf = [f for f in fams if per_fam[f]["intruders_casefold"] == 0]
    prefix_fams = [f for f in fams if per_fam[f]["name_prefix"]]
    out[f"d801_{tag}"] = {
        "per_family": per_fam,
        "total_codepoint": tot_cp,
        "total_casefold": tot_cf,
        "distinct_intruding_entities": len(all_intruders),
        "intruder_slots_held_by_other_family_members": member_intruder_slots,
        "cross_family_member_overlap": overlap,
        "leave_one_family_out_casefold": loo,
        "zero_intruder_families": zero_cf,
        "shared_prefix_families": prefix_fams,
    }
    print(
        f"# [{tag}] total cp={tot_cp} cf={tot_cf} distinct={len(all_intruders)} "
        f"zero_cf={zero_cf} prefix_fams={prefix_fams} overlap={overlap}"
    )


def d802(rows: list[dict], out: dict) -> None:
    icons = json.loads((ROOT / "icons.json").read_text()).get("entity", {})
    tab = {"dc_icon": 0, "dc_noicon": 0, "nodc_icon": 0, "nodc_noicon": 0}
    missing, malformed = [], []
    for r in rows:
        if r["translation_key"] is None:
            continue
        has_icon = r["translation_key"] in icons.get(r["platform"], {})
        has_dc = r["device_class"] is not None
        tab[
            ("dc_" if has_dc else "nodc_") + ("icon" if has_icon else "noicon")
        ] += 1
        if not has_icon:
            missing.append(f"{r['platform']}.{r['translation_key']}")
    for plat, entries in icons.items():
        for k, v in entries.items():
            if not (isinstance(v, dict) and isinstance(v.get("default"), str) and v["default"].startswith("mdi:")):
                malformed.append(f"{plat}.{k}")
    # reverse perturbation: give the four missing keys an icon in memory
    for m in list(missing):
        plat, key = m.split(".", 1)
        icons.setdefault(plat, {})[key] = {"default": "mdi:check-bold"}
    still_missing = [
        f"{r['platform']}.{r['translation_key']}"
        for r in rows
        if r["translation_key"] is not None
        and r["translation_key"] not in icons.get(r["platform"], {})
    ]
    out["d802"] = {
        "cross_tab": tab,
        "missing": missing,
        "malformed_icon_entries": malformed,
        "after_add_icons": still_missing,
    }
    print(f"# [icons] cross_tab={tab} missing={missing} after_add={still_missing}")


def d8inst(rows_builder_rows: list[dict], out: dict) -> None:
    """Vacuity probes: rebuild entities to probe the live objects."""
    hass = FakeHass()
    for eid, val in (("sensor.indoor", "21.4"), ("sensor.outdoor", "-3.0")):
        hass.states.set(eid, FakeState(val))
    cfg = {
        "indoor_temp_entity": "sensor.indoor",
        "outdoor_temp_entity": "sensor.outdoor",
        **dict(coordinator_scenarios()["coord_all_features"]),
        **ALL_FEATURES_OVERLAY,
    }
    entry = FakeEntry(data=cfg)
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    dt_util.freeze(START)
    try:
        asyncio.run(coord._update_current_state())
        coord.data = coord._build_data_dict()
        res = {}
        ents = []
        for module in PLATFORMS.values():
            added: list = []
            entry.runtime_data = coord
            asyncio.run(module.async_setup_entry(hass, entry, lambda e: added.extend(e)))
            ents.extend(added)
        from homeassistant.components.sensor import SensorEntity  # the stub

        stub_has = {
            p: (p in dir(SensorEntity) and isinstance(getattr(SensorEntity, p, None), property))
            for p in ("device_class", "state_class", "entity_category")
        }
        for prop in ("device_class", "state_class", "entity_category"):
            attr_set = public_none = vacuous = 0
            for e in ents:
                a = getattr(e, "_attr_" + prop, None)
                p = getattr(e, prop, None)
                if a is not None:
                    attr_set += 1
                    if p is None:
                        vacuous += 1
                if p is None:
                    public_none += 1
            res[prop] = {
                "attr_set": attr_set,
                "public_read_none": public_none,
                "vacuous_attr_set_public_none": vacuous,
            }
        res["stub_has_property"] = stub_has
        res["entity_category_declared"] = res["entity_category"]["attr_set"]
        res["entities_built"] = len(ents)
        out["d8inst"] = res
        print(f"# [inst] stub_has={stub_has} per-prop={res}")
    finally:
        dt_util.freeze(None)


def main() -> int:
    out: dict = {}
    scenarios = coordinator_scenarios()

    rows_all = build_entities({**scenarios["coord_all_features"], **ALL_FEATURES_OVERLAY})
    rows_min = build_entities(dict(scenarios["coord_minimal"]))
    print(f"# built all-features={len(rows_all)} minimal={len(rows_min)}")

    d801(rows_all, "all", out)
    d801(rows_min, "minimal", out)
    d802(rows_all, out)
    d8inst(rows_all, out)

    Path("tools/audit/round4/D8/verify3_own_detail.json").write_text(
        json.dumps(out, indent=1, sort_keys=True, ensure_ascii=False)
    )

    a = out["d801_all"]
    m = out["d801_minimal"]
    t = out["d802"]
    i = out["d8inst"]
    print(f"RESULT entities_all_features={len(rows_all)} count")
    print(f"RESULT entities_minimal={len(rows_min)} count")
    print(f"RESULT card_headline_suffixes={CARD_HEADLINE_SUFFIXES} list")
    print(f"RESULT v3_name_intruders_codepoint_all={a['total_codepoint']} slots")
    print(f"RESULT v3_name_intruders_casefold_all={a['total_casefold']} slots")
    print(f"RESULT v3_name_intruders_casefold_minimal={m['total_casefold']} slots")
    print(f"RESULT v3_distinct_intruders_casefold_all={a['distinct_intruding_entities']} entities")
    print(f"RESULT v3_intruder_slots_other_family_members={a['intruder_slots_held_by_other_family_members']} slots")
    print(f"RESULT v3_zero_intruder_families_casefold={a['zero_intruder_families']} list")
    print(f"RESULT v3_shared_prefix_families={a['shared_prefix_families']} list")
    print(f"RESULT v3_cross_family_member_overlap={a['cross_family_member_overlap']} list")
    print(f"RESULT v3_leave_one_family_out_casefold={a['leave_one_family_out_casefold']} map")
    print(f"RESULT v3_icons_dc_with_icon={t['cross_tab']['dc_icon']} entities")
    print(f"RESULT v3_icons_dc_without_icon={t['cross_tab']['dc_noicon']} entities")
    print(f"RESULT v3_icons_nodc_with_icon={t['cross_tab']['nodc_icon']} entities")
    print(f"RESULT v3_icons_nodc_without_icon={t['cross_tab']['nodc_noicon']} entities")
    print(f"RESULT v3_entity_without_icon_entry={len(t['missing'])} entities")
    print(f"RESULT v3_missing_icons={t['missing']} list")
    print(f"RESULT v3_malformed_icon_entries={len(t['malformed_icon_entries'])} entries")
    print(f"RESULT v3_after_add_icons={len(t['after_add_icons'])} entities")
    print(f"RESULT v3_stub_sensor_has_property={i['stub_has_property']} map")
    print(f"RESULT v3_device_class_vacuous={i['device_class']['vacuous_attr_set_public_none']} entities")
    print(f"RESULT v3_state_class_vacuous={i['state_class']['vacuous_attr_set_public_none']} entities")
    print(f"RESULT v3_entity_category_vacuous={i['entity_category']['vacuous_attr_set_public_none']} entities")
    print(f"RESULT v3_entity_category_declared={i['entity_category_declared']} entities")
    print(f"RESULT v3_entities_probed={i['entities_built']} entities")
    # harness contract conditions lines; counts only, nothing timing-derived
    import resource

    print("RESULT thread_factor=1.00 ratio")
    print("RESULT timing_results_reported=0 count")
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap} count")
    print(f"RESULT load1={os.getloadavg()[0]:.2f} load")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
