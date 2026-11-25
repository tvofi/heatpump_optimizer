#!/usr/bin/env python3
"""D8.M4 (round 11, seat D8-s3): enabled-by-default set vs the card's and README's first-hour list.

Metric: per coordinator scenario, count of entities the dashboard card addresses (every
"_suffix" literal and every <domain>.heat_pump_optimizer_<key> literal in the card source,
runtime-derived statEntity/ADVISOR/HEALTH suffixes included) that the real async_setup_entry
builds with registry default False; the same for README-named entity ids; and enabled entities
neither names. Key: the built entity's entity_id and its registry default (the value the
production seam delivers), never the card text alone.
Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D8/s3/m4_enabled_default.py [--perturb-disable KEY]
Expected at baseline 92d38ecb64: card_disabled_where_input_lit=0, readme_disabled_where_input_lit=0 (exact).
Perturbation: --perturb-disable optimization_score patches the class of the entity whose unique id ends _<KEY>'s registry
default False in memory -> card_disabled_where_input_lit 0 -> 1 (up), card_disabled_total 21 -> 27.
Machine: macOS arm64 local seat.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, re, sys, time
from pathlib import Path
sys.path[:0] = ["tests", "custom_components"]
_p0, _t0 = time.process_time(), time.thread_time()

from golden import START, coordinator_scenarios  # noqa: E402
from harness import FakeEntry, FakeHass  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer import sensor, binary_sensor, button, switch, climate  # noqa: E402
from heatpump_optimizer import datetime as dt_mod  # noqa: E402
from datetime import timedelta  # noqa: E402

PLATFORMS = (sensor, binary_sensor, button, switch, climate, dt_mod)
CARD = Path("custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js").read_text()
README = Path("README.md").read_text()
PREFIX = "heat_pump_optimizer"
DOMS = r"(?:sensor|binary_sensor|switch|button|climate|datetime)"


def registry_default(e):
    return bool(getattr(e, "entity_registry_enabled_default",
                        getattr(e, "_attr_entity_registry_enabled_default", True)))


def build(config):
    hass = FakeHass()
    entry = FakeEntry(data=config)
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    coord._prices = [{"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
                      "starts_at": (START + timedelta(hours=h)).isoformat(), "level": "NORMAL"}
                     for h in range(48)]
    coord._weather_forecast = [{"datetime": (START + timedelta(hours=h)).isoformat(),
                                "temperature": -5.0 + 3.0 * (h % 24) / 24.0, "wind_speed": 3.0,
                                "precipitation": 0.0, "humidity": 85.0} for h in range(48)]
    coord._solar_radiation_forecast = [max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)]
    coord.data = coord._build_data_dict()
    entry.runtime_data = coord
    out = []
    for mod in PLATFORMS:
        added = []

        def add(ents, _a=added):
            for e in ents:
                e.hass = hass
            _a.extend(ents)
        asyncio.run(mod.async_setup_entry(hass, entry, add))
        out.extend(added)
    return out


def object_id(i):
    return i.split(".", 1)[1]


def card_suffixes():
    sfx = set(re.findall(r'"(_[a-z][a-z0-9_]+)"', CARD))
    sfx |= {"_" + m for m in re.findall(r'"' + DOMS + r'\.' + PREFIX + r'_([a-z0-9_]+)"', CARD)}
    return sfx


STRINGS = __import__("json").loads(Path("custom_components/heatpump_optimizer/strings.json").read_text())["entity"]


def readme_names():
    """Display names in the first cell of every README table row that are entity names."""
    known = {v.get("name") for plat in STRINGS.values() for v in plat.values()}
    out = set()
    for line in README.splitlines():
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            cell = cells[0].strip("*")
            notes = " ".join(cells[3:])
            # First-hour rows only: the README's own "Card headline" / "Backs the card" tags.
            if cell in known and ("Card headline" in notes or "Backs the card" in notes):
                out.add(cell)
    return out


def dname(e):
    plat = e.entity_id.split(".", 1)[0]
    key = getattr(e, "_attr_translation_key", None)
    return STRINGS.get(plat, {}).get(key, {}).get("name")


def readme_ids():
    return set(re.findall(r"\b" + DOMS + r"\." + PREFIX + r"_[a-z0-9_]+", README))


def main():
    pkey = sys.argv[sys.argv.index("--perturb-disable") + 1] if "--perturb-disable" in sys.argv else None
    rnames = readme_names()
    lit_card_dis = lit_readme_dis = 0
    sfx = card_suffixes()
    rids = readme_ids()
    card_dis_total = readme_dis_total = 0
    unread_on = []
    seen_ids = set()
    cells = dict(coordinator_scenarios())
    # Gate-lit cell: every input that lights a card-addressed gated entity is configured,
    # so a card dependency still disabled here is disabled where its data exists.
    cells["coord_all_inputs_lit"] = {
        **cells["coord_all_features"],
        "dhw_temp_entity": "sensor.tank", "lower_floor_temp_entity": "sensor.lower",
        "floor_return_temp_entity": "sensor.ret", "buffer_tank_temp_entity": "sensor.buf",
        "mixing_valve_mode": "manual",
    }
    for name, cfg in cells.items():
        ents = build(cfg)
        ids = {e.entity_id: e for e in ents}
        for e in ents:
            if pkey is not None and str(getattr(e, "_attr_unique_id", "")).endswith("_" + pkey):
                type(e).entity_registry_enabled_default = property(lambda self: False)
        rids = readme_ids() | {i for i, e in ids.items() if dname(e) in rnames}
        seen_ids |= set(ids)
        card_hit = {i for i in ids if any(object_id(i) in (PREFIX + s,) for s in sfx)}
        card_dis = sorted(i for i in card_hit if not registry_default(ids[i]))
        rd_dis = sorted(i for i in rids if i in ids and not registry_default(ids[i]))
        on = {i for i, e in ids.items() if registry_default(e)}
        unread = sorted(on - card_hit - rids)
        card_dis_total += len(card_dis)
        readme_dis_total += len(rd_dis)
        print(f"CELL {name} entities={len(ids)} enabled={len(on)} card_hit={len(card_hit)} "
              f"card_disabled={card_dis} readme_disabled={rd_dis} enabled_unread={len(unread)}")
        if name.endswith("inputs_lit"):
            lit_card_dis, lit_readme_dis = len(card_dis), len(rd_dis)
        if name.endswith("all_features"):
            unread_on = unread
    seen_obj = {object_id(i) for i in seen_ids}
    print("CARD_SUFFIXES_UNBUILT", sorted(s for s in sfx if PREFIX + s not in seen_obj))
    print("README_IDS_UNBUILT", sorted(i for i in rids if i not in seen_ids))
    print("ENABLED_UNREAD_ALL_FEATURES", unread_on)
    print(f"RESULT card_suffixes={len(sfx)} count")
    print(f"RESULT readme_entity_names={len(rnames)} count")
    print(f"RESULT card_disabled_where_input_lit={lit_card_dis} count")
    print(f"RESULT readme_disabled_where_input_lit={lit_readme_dis} count")
    print(f"RESULT card_disabled_total={card_dis_total} count")
    print(f"RESULT readme_disabled_total={readme_dis_total} count")
    print(f"RESULT enabled_unread_all_features={len(unread_on)} count")
    tc = time.thread_time() - _t0
    print(f"RESULT thread_factor={(time.process_time() - _p0) / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


main()
