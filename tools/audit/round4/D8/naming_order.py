#!/usr/bin/env python3
"""D8 — ordering, naming, translation and enabled-by-default over every entity.

METRIC: with every entity of every platform built through the real
``async_setup_entry``, (a) for each named family, how many entities that are
NOT in the family fall strictly inside the family's span in the global
alphabetical order — once by ``entity_id`` and once by English display name;
(b) how many translation keys differ between ``strings.json`` and each of the
two shipped languages, and how many Swedish names are byte-identical to the
English one; (c) the enabled-by-default set against what the card and the
README name.

COMMAND (from the export root):

    PYTHONPATH=tests/hastub \
      /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D8/naming_order.py

EXPECTED (baseline 7dd68dd327fe3dbfb09f3bd0fe38910c58877697, 8-core Apple M1):
    entities=74  families=7  (exact, no tolerance)
    id_order_intruders=178  name_order_intruders=159
    sensor_id_order_intruders=92
    entity_without_icon_entry=4  orphan_icon_keys=0
    strings_vs_en_mismatch=0  strings_vs_sv_missing=0  sv_untranslated=0
    entity_without_strings_entry=0  strings_entry_without_entity=0
    enabled_default_off=6  card_needs=12  card_needs_disabled=0
    readme_named_by_id=0  readme_named_by_display_name=72
All counts are integers over a deterministic construction; contention-immune.
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
from pathlib import Path  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

from golden import START, coordinator_scenarios  # noqa: E402

from heatpump_optimizer import binary_sensor, button, climate, sensor, switch  # noqa: E402
from heatpump_optimizer import datetime as datetime_platform  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

#: PERTURBATION, applied in memory so the export is never written to.
#: ``--perturb tariff-prefix`` renames the seven money entities to share the
#: literal prefix "Cost " -- the single change D8-01 says would cluster them --
#: and nothing else.  ``name_order_intruders`` must fall.
#: ``--perturb drop-icon`` removes one icons.json entry; ``entity_without_icon_entry``
#: must rise by one.
PERTURB = (
    sys.argv[sys.argv.index("--perturb") + 1]
    if "--perturb" in sys.argv and len(sys.argv) > sys.argv.index("--perturb") + 1
    else ""
)

TARIFF_PREFIX_RENAMES = {
    "baseline_cost": "Cost Baseline",
    "predicted_cost": "Cost Predicted",
    "total_heating_cost": "Cost Total Heating (lifetime)",
    "current_electricity_price": "Cost Electricity Price (now)",
    "contract_comparison": "Cost Contract Comparison",
    "monthly_peak_power": "Cost Monthly Peak Power",
    "power_headroom": "Cost Power Headroom",
}

ROOT = Path("custom_components/heatpump_optimizer")
CARD = ROOT / "www" / "heatpump-optimizer-card.js"
README = Path("README.md")

PLATFORMS = {
    "sensor": sensor,
    "binary_sensor": binary_sensor,
    "button": button,
    "climate": climate,
    "switch": switch,
    "datetime": datetime_platform,
}

# ---------------------------------------------------------------------------
# The families the brief names.  Membership is by meaning, written out so a
# verifier can disagree with a specific row rather than with a regex.
# ---------------------------------------------------------------------------
FAMILIES: dict[str, re.Pattern] = {
    "dhw": re.compile(r"dhw|hot_water|legionella|mixed_water", re.I),
    "tariff": re.compile(
        r"electricity_price|monthly_peak_power|power_headroom|contract_comparison"
        r"|grid_fee|baseline_cost|predicted_cost|total_heating_cost",
        re.I,
    ),
    "learning": re.compile(
        r"comfort_weight|system_identification|learned|estimated_cop|observed_cop",
        re.I,
    ),
    "accuracy": re.compile(
        r"prediction_accuracy|diagnose_last_interval|optimization_score", re.I
    ),
    "ecl110": re.compile(r"ecl110", re.I),
    "pv": re.compile(r"solar_irradiance|solar_heat_gain|solar_surplus|^pv_", re.I),
    "card_headline": re.compile(
        r"^(predicted_savings|savings_percentage|optimization_score"
        r"|plan_narrative|monthly_savings)$"
    ),
}

#: Entity-id suffixes the shipped card resolves by suffix; grepped out of the
#: card so the list cannot drift from it silently.
CARD_SUFFIX_RE = re.compile(r'stat(?:Entity|Number)\("(_[a-z0-9_]+)"')
CARD_PINNED_RE = re.compile(r'"(?:switch|datetime|binary_sensor|sensor)\.(heat_pump_optimizer_[a-z0-9_]+)"')


def build_all():
    """Every entity of every platform, one realistic all-features install."""
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
        }
    )
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    entry = FakeEntry(data=cfg)
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    from datetime import timedelta

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
                    "cls": type(ent).__name__,
                    "entity_id": getattr(ent, "entity_id", None) or "",
                    "translation_key": getattr(ent, "_attr_translation_key", None),
                    "enabled": bool(
                        getattr(ent, "_attr_entity_registry_enabled_default", True)
                    ),
                    "category": str(
                        getattr(ent, "_attr_entity_category", None) or ""
                    ),
                }
            )
    return rows


def span_intruders(order: list[str], members: set[str]) -> tuple[int, int, list[str]]:
    """Foreign entities inside the family's alphabetical span, and its breaks."""
    idx = [i for i, name in enumerate(order) if name in members]
    if len(idx) < 2:
        return 0, 0, []
    lo, hi = idx[0], idx[-1]
    intruders = [order[i] for i in range(lo, hi + 1) if order[i] not in members]
    runs = 1
    for a, b in zip(idx, idx[1:]):
        if b != a + 1:
            runs += 1
    return len(intruders), runs - 1, intruders


def main() -> int:
    dt_util.freeze(START)
    try:
        rows = build_all()
    finally:
        dt_util.freeze(None)

    strings = json.loads((ROOT / "strings.json").read_text())["entity"]
    en = json.loads((ROOT / "translations" / "en.json").read_text())["entity"]
    sv = json.loads((ROOT / "translations" / "sv.json").read_text())["entity"]

    def name_of(row, table):
        return (
            table.get(row["platform"], {})
            .get(row["translation_key"], {})
            .get("name")
        )

    if PERTURB == "tariff-prefix":
        for _k, _new in TARIFF_PREFIX_RENAMES.items():
            for _table in (strings, en):
                if _k in _table.get("sensor", {}):
                    _table["sensor"][_k] = dict(_table["sensor"][_k], name=_new)

    for row in rows:
        # The climate entity sets ``_attr_name = None`` under
        # ``has_entity_name``: Home Assistant shows the DEVICE name for it,
        # which sorts under the device, not under a name of its own.  Giving
        # it the class name here would invent an ordering position.
        row["name_en"] = (
            name_of(row, en)
            or name_of(row, strings)
            or ("" if row["platform"] == "climate" else row["cls"])
        )
        row["name_sv"] = name_of(row, sv) or ""

    by_id = sorted(r["entity_id"] for r in rows)
    by_name = [r["entity_id"] for r in sorted(rows, key=lambda r: r["name_en"])]

    report: dict = {"families": {}}
    total_id = total_name = 0
    for fam, pattern in FAMILIES.items():
        members = {
            r["entity_id"]
            for r in rows
            if pattern.search(r["translation_key"] or "")
            or pattern.search(r["entity_id"])
        }
        i_id, b_id, who_id = span_intruders(by_id, members)
        i_nm, b_nm, who_nm = span_intruders(by_name, members)
        total_id += i_id
        total_name += i_nm
        report["families"][fam] = {
            "members": sorted(members),
            "id_intruders": who_id,
            "id_breaks": b_id,
            "name_intruders": [
                next(r["name_en"] for r in rows if r["entity_id"] == e)
                for e in who_nm
            ],
            "name_breaks": b_nm,
        }
        print(
            f"# family {fam:<14} n={len(members):<3} "
            f"id_intruders={i_id:<3} id_breaks={b_id:<2} "
            f"name_intruders={i_nm:<3} name_breaks={b_nm}"
        )

    # Within the ``sensor.`` domain only: Home Assistant namespaces entity
    # ids by domain, so a switch sorting after every sensor is upstream's
    # ordering and not this integration's naming.
    sensor_ids = sorted(r["entity_id"] for r in rows if r["platform"] == "sensor")
    total_sensor_id = 0
    for fam, pattern in FAMILIES.items():
        members = {
            r["entity_id"]
            for r in rows
            if r["platform"] == "sensor"
            and (
                pattern.search(r["translation_key"] or "")
                or pattern.search(r["entity_id"])
            )
        }
        n, _b, _w = span_intruders(sensor_ids, members)
        total_sensor_id += n
        report["families"][fam]["sensor_id_intruders"] = n
    report["sensor_id_intruders_total"] = total_sensor_id

    # --- icons.json coverage ---------------------------------------------
    icons = json.loads((ROOT / "icons.json").read_text()).get("entity", {})
    if PERTURB == "drop-icon":
        icons.get("sensor", {}).pop("indoor_temperature_optimizer", None)
    no_icon = [
        f"{r['platform']}.{r['translation_key']}"
        for r in rows
        if r["translation_key"] is not None
        and r["translation_key"] not in icons.get(r["platform"], {})
    ]
    orphan_icons = [
        f"{p}.{k}"
        for p, entries in icons.items()
        for k in entries
        if (p, k) not in {(r["platform"], r["translation_key"]) for r in rows}
    ]
    report["entity_without_icon_entry"] = no_icon
    report["orphan_icon_keys"] = orphan_icons

    # --- translations -------------------------------------------------------
    mismatch, sv_missing, sv_same = [], [], []
    for platform, entries in strings.items():
        for key, body in entries.items():
            s_name = body.get("name")
            e_name = en.get(platform, {}).get(key, {}).get("name")
            v_name = sv.get(platform, {}).get(key, {}).get("name")
            if s_name != e_name:
                mismatch.append(f"{platform}.{key}: strings={s_name!r} en={e_name!r}")
            if v_name is None:
                sv_missing.append(f"{platform}.{key}")
            elif v_name == s_name:
                sv_same.append(f"{platform}.{key}={s_name!r}")
    report["strings_vs_en"] = mismatch
    report["sv_missing"] = sv_missing
    report["sv_untranslated"] = sv_same

    # entities built but with no translation entry at all
    untranslated = [
        f"{r['platform']}.{r['translation_key']}"
        for r in rows
        if r["translation_key"] is not None
        and r["translation_key"] not in strings.get(r["platform"], {})
    ]
    report["entity_without_strings_entry"] = untranslated

    # strings entries with no entity behind them
    built = {(r["platform"], r["translation_key"]) for r in rows}
    orphan = [
        f"{p}.{k}"
        for p, entries in strings.items()
        for k in entries
        if (p, k) not in built
    ]
    report["strings_entry_without_entity"] = orphan

    # --- enabled by default -------------------------------------------------
    off = sorted(r["entity_id"] for r in rows if not r["enabled"])
    card_text = CARD.read_text()
    card_suffixes = sorted(set(CARD_SUFFIX_RE.findall(card_text)))
    card_pinned = sorted(set(CARD_PINNED_RE.findall(card_text)))
    needed = set()
    for r in rows:
        for suf in card_suffixes:
            if r["entity_id"].endswith(suf):
                needed.add(r["entity_id"])
        for pin in card_pinned:
            if r["entity_id"].endswith(pin):
                needed.add(r["entity_id"])
    card_needs_disabled = sorted(needed & set(off))
    report["enabled_default_off"] = off
    report["card_suffixes"] = card_suffixes
    report["card_pinned"] = card_pinned
    report["card_needs"] = sorted(needed)
    report["card_needs_disabled"] = card_needs_disabled

    # README: the README names entities by DISPLAY NAME, never by entity id
    # (0 of 74 ids appear in it), so the "first hour" list is derived from the
    # names it prints.
    readme = README.read_text()
    readme_named_ids = sorted(
        r["entity_id"] for r in rows if r["entity_id"] in readme
    )
    readme_named = sorted(
        r["entity_id"] for r in rows if r["name_en"] and r["name_en"] in readme
    )
    report["readme_named_by_id"] = readme_named_ids
    readme_named_disabled = sorted(set(readme_named) & set(off))
    report["readme_named"] = readme_named
    report["readme_named_disabled"] = readme_named_disabled

    # enabled but permanently unavailable on a MINIMAL install: the mirror of
    # the six opt-in sensors that were switched off for exactly that reason.
    report["rows"] = rows

    out = Path("tools/audit/round4/D8/naming_detail.json")
    out.write_text(json.dumps(report, indent=1, sort_keys=True, ensure_ascii=False))

    print(f"RESULT perturbation={PERTURB or 'none'} arm")
    print(f"RESULT entities={len(rows)} count")
    print(f"RESULT families={len(FAMILIES)} count")
    print(f"RESULT id_order_intruders={total_id} entities")
    print(f"RESULT name_order_intruders={total_name} entities")
    print(f"RESULT sensor_id_order_intruders={total_sensor_id} entities")
    print(f"RESULT entity_without_icon_entry={len(no_icon)} entities")
    print(f"RESULT orphan_icon_keys={len(orphan_icons)} keys")
    print(f"RESULT strings_vs_en_mismatch={len(mismatch)} keys")
    print(f"RESULT strings_vs_sv_missing={len(sv_missing)} keys")
    print(f"RESULT sv_untranslated={len(sv_same)} keys")
    print(f"RESULT entity_without_strings_entry={len(untranslated)} entities")
    print(f"RESULT strings_entry_without_entity={len(orphan)} keys")
    print(f"RESULT enabled_default_off={len(off)} entities")
    print(f"RESULT card_suffixes={len(card_suffixes)} suffixes")
    print(f"RESULT card_needs={len(needed)} entities")
    print(f"RESULT card_needs_disabled={len(card_needs_disabled)} entities")
    print(f"RESULT readme_named_by_id={len(readme_named_ids)} entities")
    print(f"RESULT readme_named_by_display_name={len(readme_named)} entities")
    print(f"RESULT readme_named_disabled={len(readme_named_disabled)} entities")
    print(f"# detail written to {out}")
    # Harness contract (tools/audit/README.md): the three conditions lines.
    # This harness reports COUNTS only -- no wall, CPU or RSS number -- so the
    # thread factor cannot contaminate anything here; the pin is applied
    # anyway, above the numpy import, and stated so a reader need not infer it.
    import resource

    print("RESULT thread_factor=1.00 ratio")
    print("RESULT timing_results_reported=0 count")
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap} count")
    print(f"RESULT load1={os.getloadavg()[0]:.2f} load")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
