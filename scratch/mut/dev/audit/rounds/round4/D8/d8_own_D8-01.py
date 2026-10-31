#!/usr/bin/env python3
"""D8-01, verifier 1's own harness (independent of naming_order.py).

METRIC (mine): build every entity of every platform through the real
``async_setup_entry`` on an all-features install; take each entity's English
display name from ``translations/en.json``; sort all names alphabetically;
for each of seven families whose membership I enumerate BY HAND as explicit
translation-key sets, count the entities OUTSIDE the family that sort
strictly between the family's alphabetically first and last member
("span intruders"), and sum over families.  Secondary aggregates: per-family
intruder counts, families with >=1 break, and whether the families with zero
intruders are exactly the families whose members all share the same first
word of their display name.

COMMAND (from a tree root):

    PYTHONPATH=tests/hastub \
      /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D8/d8_own_D8-01.py            # default arm
    ... d8_own_D8-01.py --perturb scatter               # my perturbation

EXPECTED (baseline 7dd68dd, and the branch head 0855277 whose only
custom_components/ drift is two version strings; 8-core Apple M1):
    entities=74
    span_intruders_total=159  (exact, integer count, contention-immune)
    zero_intruder_families=2  shared_first_word_families=2  (same two)
    default arm; ``--perturb scatter`` must RAISE the total above 159.
PERTURBATION (mine, opposite direction to the finder's): ``--perturb
scatter`` renames, in memory only, the members of the two zero-intruder
families (ecl110, pv) so they no longer share a literal prefix; the export
is never written to.  If the zeros were an artefact of family SIZE rather
than of the shared prefix, the total would not move.
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

PERTURB = (
    sys.argv[sys.argv.index("--perturb") + 1]
    if "--perturb" in sys.argv
    else ""
)

#: My own membership, written out by hand from the 74-entity list.  A
#: verifier who disagrees with a row disagrees with me, not with a regex.
MY_FAMILIES: dict[str, frozenset[str]] = {
    # hot-water family: every entity whose meaning is the DHW tank
    "dhw": frozenset(
        {
            "dhw_cost", "dhw_energy", "dhw_heating_cost", "dhw_heating_plan",
            "dhw_heating_schedule", "dhw_heavy_day_demand", "dhw_mixed_water",
            "dhw_setpoint_advisor", "dhw_temperature", "boost_dhw",
        }
    ),
    # the money family: what a billing-period comparison touches
    "tariff": frozenset(
        {
            "baseline_cost", "predicted_cost", "total_heating_cost",
            "current_electricity_price", "contract_comparison",
            "monthly_peak_power", "power_headroom",
        }
    ),
    # the learning family
    "learning": frozenset(
        {
            "comfort_weight", "run_system_identification",
            "reset_learned_comfort_weight", "estimated_cop", "observed_cop",
        }
    ),
    # how well is it predicting
    "accuracy": frozenset(
        {"prediction_accuracy", "diagnose_last_interval", "optimization_score"}
    ),
    # the ECL110 add-on
    "ecl110": frozenset({"ecl110_displace", "ecl110_effective_displace"}),
    # the solar family
    "pv": frozenset({"solar_irradiance", "solar_heat_gain", "solar_surplus_forecast"}),
    # the card's headline row: pinned by the card's HEADLINE_SUFFIXES +
    # statEntity("_monthly_savings") in www/heatpump-optimizer-card.js
    "card_headline": frozenset(
        {
            "predicted_savings", "savings_percentage", "optimization_score",
            "plan_narrative", "monthly_savings",
        }
    ),
}

#: Membership-sensitivity attack: the tariff family with the two
#: power-flavoured members removed (a narrower "money-only" reading).
TARIFF_MONEY_ONLY = frozenset(
    {
        "baseline_cost", "predicted_cost", "total_heating_cost",
        "current_electricity_price", "contract_comparison",
    }
)

#: --perturb scatter: strip the literal prefix off the two zero families.
SCATTER_RENAMES = {
    "ecl110_displace": "Flow Displacement (ECL110 Module)",
    "ecl110_effective_displace": "Flow Displacement Now In Effect",
    "solar_irradiance": "Irradiance Right Now",
    "solar_heat_gain": "Heat Gained Through Windows",
    "solar_surplus_forecast": "Surplus PV Forecast For Tomorrow",
}

PLATFORMS = {
    "sensor": sensor,
    "binary_sensor": binary_sensor,
    "button": button,
    "climate": climate,
    "switch": switch,
    "datetime": datetime_platform,
}

ROOT = Path("custom_components/heatpump_optimizer")


def build_all():
    """My own build: all-features topology, real async_setup_entry."""
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
    asyncio.run(coord._update_current_state())
    coord._forecast_arrays()
    coord.data = coord._build_data_dict()

    ents = {}
    for pname, module in PLATFORMS.items():
        added: list = []
        entry.runtime_data = coord
        asyncio.run(module.async_setup_entry(hass, entry, lambda e: added.extend(e)))
        for ent in added:
            ents[(pname, getattr(ent, "_attr_translation_key", None))] = ent
    return ents


def intruders_and_breaks(order, members):
    """(foreign entities inside the span, breaks) for one family, my way."""
    pos = sorted(i for i, nm in enumerate(order) if nm in members)
    if len(pos) < 2:
        return [], 0
    lo, hi = pos[0], pos[-1]
    foreign = [order[i] for i in range(lo, hi + 1) if order[i] not in members]
    breaks = sum(1 for a, b in zip(pos, pos[1:]) if b != a + 1)
    return foreign, breaks


def main() -> int:
    dt_util.freeze(START)
    try:
        ents = build_all()
    finally:
        dt_util.freeze(None)

    en = json.loads((ROOT / "translations" / "en.json").read_text())["entity"]
    strings = json.loads((ROOT / "strings.json").read_text())["entity"]

    rows = []
    for (pname, key), ent in ents.items():
        name = (
            en.get(pname, {}).get(key, {}).get("name")
            or strings.get(pname, {}).get(key, {}).get("name")
        )
        if name is None and pname == "climate":
            name = ""  # device-named entity: no name of its own
        rows.append(
            {
                "platform": pname,
                "key": key,
                "eid": getattr(ent, "entity_id", None) or "",
                "name": name,
            }
        )
    assert len(rows) == 74, f"expected 74 entities, built {len(rows)}"

    if PERTURB == "scatter":
        for r in rows:
            if r["key"] in SCATTER_RENAMES:
                r["name"] = SCATTER_RENAMES[r["key"]]

    # Sort by display name; a member's identity is its translation key.
    by_name = [r["key"] for r in sorted(rows, key=lambda r: r["name"] or "")]

    total = 0
    zero_families = []
    shared_word_families = []
    per_family = {}
    for fam, members in MY_FAMILIES.items():
        foreign, breaks = intruders_and_breaks(by_name, members)
        per_family[fam] = (len(foreign), breaks)
        total += len(foreign)
        if not foreign:
            zero_families.append(fam)
        names = [
            next(r["name"] for r in rows if r["key"] == k) for k in members
        ]
        first_words = {n.split(" ", 1)[0] for n in names if n}
        if len(first_words) == 1:
            shared_word_families.append(fam)
        print(
            f"# family {fam:<14} n={len(members):<3} "
            f"intruders={len(foreign):<3} breaks={breaks}"
        )

    # membership-sensitivity attack: the narrower money-only tariff reading
    mo_foreign, mo_breaks = intruders_and_breaks(by_name, TARIFF_MONEY_ONLY)

    # leave-one-out range over families (sum arithmetic, stated for the record)
    loo = {f: total - v[0] for f, v in per_family.items()}

    out = Path("tools/audit/round4/D8/d8_own_D8-01_detail.json")
    out.write_text(
        json.dumps(
            {
                "per_family": {f: {"intruders": v[0], "breaks": v[1]}
                               for f, v in per_family.items()},
                "zero_intruder_families": zero_families,
                "shared_first_word_families": shared_word_families,
                "tariff_money_only": {"intruders": len(mo_foreign),
                                      "breaks": mo_breaks},
                "leave_one_out": loo,
                "rows": rows,
            },
            indent=1,
            sort_keys=True,
            ensure_ascii=False,
        )
    )

    print(f"RESULT perturbation={PERTURB or 'none'} arm")
    print(f"RESULT entities={len(rows)} count")
    print(f"RESULT span_intruders_total={total} entities")
    print(f"RESULT split_families={sum(1 for v in per_family.values() if v[1] > 0)} families")
    print(f"RESULT zero_intruder_families={len(zero_families)} families")
    print(f"RESULT shared_first_word_families={len(shared_word_families)} families")
    print(f"RESULT zero_equals_shared_word={sorted(zero_families) == sorted(shared_word_families)} bool")
    print(f"RESULT tariff_money_only_intruders={len(mo_foreign)} entities")
    print(f"RESULT leave_one_out_min={min(loo.values())} entities")
    print(f"RESULT leave_one_out_max={max(loo.values())} entities")
    print(f"# detail written to {out}")
    import resource

    print("RESULT thread_factor=1.00 ratio")
    print("RESULT timing_results_reported=0 count")
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap} count")
    print(f"RESULT load1={os.getloadavg()[0]:.2f} load")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
