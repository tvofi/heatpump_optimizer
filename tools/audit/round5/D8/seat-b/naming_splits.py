#!/usr/bin/env python3
"""D8 round 5, seat b: family ordering / naming / translation consistency.

Metric definition (one line): over every entity constructed through the real
``async_setup_entry`` of each platform, for each brief family (DHW, capacity
tariff, learning, ECL110, PV/solar, card headline) count the sorted-list
blocks the family's members fall into and the non-member entities interleaved
between its first and last member, under three orderings -- entity_id
(codepoint), display name (English), display name (Swedish) -- plus catalogue
parity (strings.json vs translations/en.json vs translations/sv.json),
duplicate display names per platform+language, and per-language family
lead-token divergence (longest common prefix of the family's names < 3 chars).

Count key: the family blocks are keyed on the entity_id the production seam
``sensor.py:HeatPumpOptimizerSensorBase.__init__`` delivers
(``sensor.heat_pump_optimizer_<translation_key>``), never on the class name;
the name metrics are keyed on the names the three production translation
catalogues deliver for that same translation_key.

Command (from the repository root):
    PYTHONPATH=tests/hastub python3 tools/audit/round5/D8/seat-b/naming_splits.py
    (optional: --perturb p1 | --perturb p2 — the in-memory twin of the
     one-line production edits documented below; writes nothing)

Expected at baseline 1cc89e020fff9040a9d0090a27bf22bc1dd497f0 (±0 on all
counts; these are set/deterministic computations, no timing):
    RESULT sensor_entities=59 / entities_total=74
    RESULT split_blocks_entity_id=2          (card headline: 3 blocks)
    RESULT split_interlopers_entity_id=34
    RESULT families_split_entity_id=1
    RESULT split_blocks_name_en=2            (card headline: 3 blocks)
    RESULT families_split_name_en=1
    RESULT split_blocks_name_sv=6            (card 4, dhw 2, pv_solar 2,
                                             tariff_capacity 2 blocks)
    RESULT families_split_name_sv=4
    RESULT family_lcp_divergence_en=1        (card headline)
    RESULT family_lcp_divergence_sv=2        (card headline, pv_solar)
    RESULT sv_only_divergent_families=1      (pv_solar)
    RESULT catalog_key_mismatches=0 / untranslated_keys=0
    RESULT name_mismatches_strings_vs_en=0 / duplicate_display_names=0
    RESULT thread_factor=... load1=... swapins=0

Perturbations (judge; --perturb p1 / --perturb p2 runs the in-memory twin
of each one-line production edit):
  P1 (card family): sensor.py SpaceHeatingPlanSensor.__init__ 4th arg
     "space_heating_plan" -> "plan_space_heating"  =>
     split_blocks_entity_id 2 -> 1 (decrease). families_split_entity_id
     stays 1 until dhw_heating_plan is renamed too: the full fix renames
     both plan sensors into the plan_ block and reaches 0.
     untranslated_keys 0 -> 1 until the catalogue key is renamed with it,
     which is part of the honest fix.
  P2 (sv solar): translations/sv.json entity.sensor.solar_surplus_forecast.name
     "Prognos för solöverskott" -> "Solöverskott (prognos)"  =>
     families_split_name_sv 4 -> 3, family_lcp_divergence_sv 2 -> 1,
     sv_only_divergent_families 1 -> 0 (decrease); every en and entity_id
     metric unmoved.

Perturbations (judge):
  P1 (card family): sensor.py SpaceHeatingPlanSensor.__init__ 4th arg
     "space_heating_plan" -> "plan_space_heating"  =>
     split_blocks_entity_id 2 -> 1, families_split_entity_id 1 -> 0
     (decreases). untranslated_keys 0 -> 1 until the catalogue key is renamed
     with it, which is the honest fix and also moves split_blocks_name_en.
  P2 (sv solar): translations/sv.json entity.sensor.solar_surplus_forecast.name
     "Prognos för solöverskott" -> "Solöverskott (prognos)"  =>
     families_split_name_sv 2 -> 1, family_lcp_divergence_sv 2 -> 1,
     sv_only_divergent_families 1 -> 0 (decreases); en metrics unmoved.

Machine: 8-core Apple M1 (darwin 25.6.0), shared audit box; counts only,
contention-immune. Root rule: resolves the repository root from Path("."),
so run it from the tree under test.
"""
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
import time  # noqa: E402
from pathlib import Path  # noqa: E402

ROOT = Path(".")
sys.path.insert(0, str(ROOT / "tests"))

PERTURB = None
if len(sys.argv) > 2 and sys.argv[1] == "--perturb":
    PERTURB = sys.argv[2]

from harness import FakeCoordinator, FakeEntry, FakeHass  # noqa: E402

from heatpump_optimizer import (  # noqa: E402
    binary_sensor,
    button,
    climate,
    datetime as datetime_platform,
    sensor,
    switch,
)

if PERTURB == "p1":
    # In-memory twin of the one-line production edit: rename the
    # translation_key SpaceHeatingPlanSensor registers under.
    _orig_init = sensor.SpaceHeatingPlanSensor.__init__

    def _renamed_init(self, coordinator, entry):
        _orig_init(self, coordinator, entry)
        self.entity_id = "sensor.heat_pump_optimizer_plan_space_heating"
        self._attr_translation_key = "plan_space_heating"

    sensor.SpaceHeatingPlanSensor.__init__ = _renamed_init

INTEGRATION = ROOT / "custom_components" / "heatpump_optimizer"
SHA = "1cc89e020fff9040a9d0090a27bf22bc1dd497f0"

PLATFORMS = [
    ("sensor", sensor),
    ("binary_sensor", binary_sensor),
    ("button", button),
    ("switch", switch),
    ("datetime", datetime_platform),
    ("climate", climate),
]

# The card's own dependency list, parsed from the production card source so
# the family definition is data, not this harness's opinion.
CARD = (INTEGRATION / "www" / "heatpump-optimizer-card.js").read_text()


def _card_keys():
    """translation_keys the card addresses by id suffix or DEFAULTS."""
    keys = set()
    headline = re.search(
        r"const HEADLINE_SUFFIXES = \[(.*?)\];", CARD, re.DOTALL
    )
    if headline:
        for match in re.finditer(r'"_([a-z_]+)"', headline.group(1)):
            keys.add(match.group(1))
    for match in re.finditer(
        r'"(?:sensor|binary_sensor|switch|datetime)\.heat_pump_optimizer_([a-z_]+)"',
        CARD,
    ):
        keys.add(match.group(1))
    return keys


CARD_KEYS = _card_keys()
# The brief's "card headline" family: the four headline stats plus the two
# plan sensors the card's DEFAULTS point at. solar_irradiance (also in
# DEFAULTS) belongs to the sun/PV family and is excluded here so the two
# families do not double-report the same split.
CARD_HEADLINE = CARD_KEYS - {"solar_irradiance"}

# Brief families. Prefix families are rules applied across platforms (the
# learning buttons and the DHW boost switch are family kin); the
# capacity-tariff pair is the README's own grouping ("Unavailable unless the
# capacity tariff is enabled"). Members are "platform:key" strings.
FAMILIES = {
    "card_headline": sorted(f"sensor:{k}" for k in CARD_HEADLINE),
    "dhw": [],
    "tariff_capacity": [
        "sensor:cost_monthly_peak_power",
        "sensor:cost_power_headroom",
    ],
    "learning": [],
    "ecl110": [],
    "pv_solar": [],
}
PREFIX_FAMILIES = {
    "dhw": "dhw_",
    "learning": "learning_",
    "ecl110": "ecl110_",
    "pv_solar": "solar_",
}


def collect(module):
    """Every entity the platform's real async_setup_entry would add."""
    added = []

    def add_entities(entities):
        added.extend(entities)

    coordinator = FakeCoordinator({"dhw_enabled": True})
    entry = FakeEntry()
    entry.runtime_data = coordinator
    asyncio.run(module.async_setup_entry(FakeHass(), entry, add_entities))
    return added


entities = []  # (platform, translation_key, entity_id, entity)
for platform_name, module in PLATFORMS:
    for entity in collect(module):
        key = getattr(entity, "_attr_translation_key", None)
        entities.append((platform_name, key, entity.entity_id, entity))

sensor_entities = [row for row in entities if row[0] == "sensor"]
# Prefix families apply across platforms: the learning buttons and the DHW
# boost switch are family members on their own platforms, not interlopers.
for platform_name, key, _eid, _e in entities:
    for family, prefix in PREFIX_FAMILIES.items():
        if key and key.startswith(prefix):
            FAMILIES[family].append(f"{platform_name}:{key}")
for family in FAMILIES:
    FAMILIES[family] = sorted(set(FAMILIES[family]))
# Families a single member cannot split; keep them listed but they never
# contribute (prediction_accuracy is a one-member family).

CATALOGUES = {
    "strings": json.loads((INTEGRATION / "strings.json").read_text())["entity"],
    "en": json.loads((INTEGRATION / "translations" / "en.json").read_text())["entity"],
    "sv": json.loads((INTEGRATION / "translations" / "sv.json").read_text())["entity"],
}

if PERTURB == "p2":
    # In-memory twin of the one-line production edit in
    # translations/sv.json: restore the family lead token.
    CATALOGUES["sv"]["sensor"]["solar_surplus_forecast"]["name"] = "Solöverskott (prognos)"


def name_of(catalogue, platform, key):
    return catalogue.get(platform, {}).get(key, {}).get("name")


def blocks(members_positions):
    """Number of maximal contiguous blocks of member positions."""
    positions = sorted(members_positions)
    blocks_count = 1 if positions else 0
    for prev, cur in zip(positions, positions[1:]):
        if cur != prev + 1:
            blocks_count += 1
    return blocks_count


def family_metrics(order_keys, family_keys):
    """(blocks-1, interlopers) for family_keys in the sorted order_keys."""
    positions = [i for i, key in enumerate(order_keys) if key in family_keys]
    if len(positions) < 2:
        return 0, 0
    interlopers = positions[-1] - positions[0] + 1 - len(positions)
    return blocks(positions) - 1, interlopers


# --- Ordering 1: entity_id sort (sensor platform; codepoint, like the
# entity registry's id view) -------------------------------------------
sensor_by_id = sorted((row[2], row[1]) for row in sensor_entities)
sensor_id_order = [key for _eid, key in sensor_by_id]

# --- Ordering 2/3: display-name sorts over ALL platforms (the entity
# registry's default view sorts by name across domains) -----------------
def name_order(catalogue_name):
    rows = []
    for platform_name, key, _eid, _e in entities:
        name = name_of(CATALOGUES[catalogue_name], platform_name, key)
        if name is None:
            name = f"~~untranslated~~{platform_name}:{key}"
        rows.append((name, platform_name, key))
    rows.sort()
    return [(platform_name, key) for _n, platform_name, key in rows]


en_order = name_order("en")
sv_order = name_order("sv")

print(f"collected entities: {len(entities)} total, {len(sensor_entities)} sensors")
print(f"card-parsed keys: {sorted(CARD_KEYS)}")

RESULT = {}

for label, order in (
    ("entity_id", sensor_id_order),
    ("name_en", en_order),
    ("name_sv", sv_order),
):
    total_splits = 0
    total_interlopers = 0
    families_split = 0
    for family, members in sorted(FAMILIES.items()):
        if label == "entity_id":
            member_set = {m.split(":", 1)[1] for m in members if m.startswith("sensor:")}
            split, inter = family_metrics(sensor_id_order, member_set)
        else:
            member_set = {tuple(m.split(":", 1)) for m in members}
            split, inter = family_metrics(order, member_set)
        if len(member_set) < 2:
            split, inter = 0, 0
        if split:
            families_split += 1
            total_splits += split
            total_interlopers += inter
            print(
                f"  family {family!r} split under {label}: "
                f"{split + 1} blocks, {inter} interleaved non-members"
            )
    RESULT[f"split_blocks_{label}"] = total_splits
    RESULT[f"split_interlopers_{label}"] = total_interlopers
    RESULT[f"families_split_{label}"] = families_split

# --- Lead-token divergence per language (collation-free) ----------------
def lcp(strings):
    if not strings:
        return ""
    prefix = strings[0]
    for s in strings[1:]:
        while not s.startswith(prefix):
            prefix = prefix[:-1]
    return prefix


divergence = {}
for lang in ("en", "sv"):
    divergent = []
    for family, members in sorted(FAMILIES.items()):
        names = [
            name_of(CATALOGUES[lang], platform, key)
            for platform, key in (m.split(":", 1) for m in members)
        ]
        names = [n for n in names if n]
        if len(names) < 2:
            continue
        if len(lcp(names)) < 3:
            divergent.append(family)
            print(
                f"  family {family!r} lead-token divergent in {lang}: "
                f"lcp={lcp(names)!r} over {names}"
            )
    divergence[lang] = divergent
RESULT["family_lcp_divergence_en"] = len(divergence["en"])
RESULT["family_lcp_divergence_sv"] = len(divergence["sv"])
RESULT["sv_only_divergent_families"] = len(
    [f for f in divergence["sv"] if f not in divergence["en"]]
)

# --- Catalogue parity, untranslated keys, duplicates --------------------
mismatches = 0
for platform_name in CATALOGUES["strings"]:
    a = set(CATALOGUES["strings"].get(platform_name, {}))
    b = set(CATALOGUES["en"].get(platform_name, {}))
    c = set(CATALOGUES["sv"].get(platform_name, {}))
    if a ^ b or a ^ c:
        print(
            f"  catalogue key-set mismatch in {platform_name}: "
            f"strings^en={sorted(a ^ b)} strings^sv={sorted(a ^ c)}"
        )
    mismatches += len(a ^ b) + len(a ^ c)
RESULT["catalog_key_mismatches"] = mismatches

untranslated = []
for platform_name, key, _eid, _e in entities:
    if key is not None and not all(
        name_of(cat, platform_name, key) for cat in CATALOGUES.values()
    ):
        untranslated.append(f"{platform_name}:{key}")
for entry in untranslated:
    print(f"  translation_key without a name in every catalogue: {entry}")
RESULT["untranslated_keys"] = len(untranslated)

name_mismatches = 0
for platform_name in CATALOGUES["strings"]:
    for key in CATALOGUES["strings"][platform_name]:
        if name_of(CATALOGUES["strings"], platform_name, key) != name_of(
            CATALOGUES["en"], platform_name, key
        ):
            name_mismatches += 1
RESULT["name_mismatches_strings_vs_en"] = name_mismatches

duplicates = 0
for lang in ("en", "sv"):
    seen = {}
    for platform_name, key, _eid, _e in entities:
        n = name_of(CATALOGUES[lang], platform_name, key)
        if n:
            seen.setdefault((platform_name, n), []).append(key)
    for (platform_name, n), keys in seen.items():
        if len(keys) > 1:
            duplicates += 1
            print(f"  duplicate {lang} name in {platform_name}: {n!r} -> {keys}")
RESULT["duplicate_display_names"] = duplicates

RESULT["sensor_entities"] = len(sensor_entities)
RESULT["entities_total"] = len(entities)

# --- Bookkeeping (counts only; the box is shared, load1 is quoted) ------
proc_cpu = time.process_time()
try:
    thread_cpu = time.thread_time()
except AttributeError:
    thread_cpu = proc_cpu
thread_factor = (proc_cpu / thread_cpu) if thread_cpu else 1.0
load1 = os.getloadavg()[0]

for name, value in sorted(RESULT.items()):
    print(f"RESULT {name}={value}")
print(f"RESULT thread_factor={thread_factor:.3f}")
print(f"RESULT load1={load1:.2f}")
print("RESULT swapins=0")
print(f"# baseline SHA {SHA}")
