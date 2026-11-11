#!/usr/bin/env python3
"""D8-v1 independent harness attacking D8-s2-01. The finder's harness
(s2_ordering_finding.py) measures whether the Python *list literal* order
inside sensor.py's `async_setup_entry` matches alphabetical order of
`translation_key` -- a source-code construct with no runtime consequence:
`async_add_entities()` registration order does not control what a user sees
(Home Assistant's own UI sorts the entity/device list by name, not by
registration order; nothing in this repository's card or dashboard code
reads `async_setup_entry`'s list order either).

The D8 brief's actual requirement is: "grouping and naming such that
alphabetical sort clusters related entities" -- i.e. the *entity_id strings
themselves*, when sorted, should keep families (cost_, plan_, dhw_, ...)
together. This harness builds every sensor entity through the real
`async_setup_entry`, reads back the *actual* `entity_id` each one is given,
sorts THOSE (not the source list), and counts how many times a family
prefix is interrupted by a non-family member in that sorted order -- the
metric the brief actually specifies.

    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
      MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
      python3 tools/audit/round8/D8/v1_ordering_refute.py

Metric definition: `family_splits` = number of families (grouped by the
entity_id's first underscore-delimited token after the
"heat_pump_optimizer_" prefix) whose members are NOT contiguous when the
real, constructed `entity_id` values are sorted alphabetically. This is the
brief's own test ("alphabetical sort clusters related entities"), applied to
the string the brief names (`entity_id`), not to Python source order.

Instrumented symbol: heatpump_optimizer.sensor:async_setup_entry (via the
real entities it constructs, not via source-text parsing).

Perturbation (null control): shuffle the constructed entity list itself
(the equivalent of the finder's "wrong" construction order) and re-sort by
entity_id -- `family_splits` must be identical, because sorting by
entity_id is invariant to construction order. If it is not identical, the
finder's premise (construction order matters to the sorted view) would be
correct and this harness says so.

Baseline SHA: cdf82daabcfe3777d98b31489f36df5555ec9d82. Counts only, final.
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import random
import sys
from datetime import timedelta

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import harness  # noqa: E402
import golden  # noqa: E402
from harness import FakeEntry, FakeHass  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer import sensor  # noqa: E402

START = golden.START
CONFIG = golden.coordinator_scenarios()["coord_all_features"]

PREFIX = "sensor.heat_pump_optimizer_"


def build():
    hass = FakeHass()
    entry = FakeEntry(data=CONFIG)
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    coord._prices = [
        {"total": 0.7, "starts_at": (START + timedelta(hours=h)).isoformat(), "level": "NORMAL"}
        for h in range(48)
    ]
    coord._weather_forecast = [
        {"datetime": (START + timedelta(hours=h)).isoformat(), "temperature": 2.0,
         "wind_speed": 3.0, "precipitation": 0.0, "humidity": 80.0}
        for h in range(48)
    ]
    coord._solar_radiation_forecast = [0.0 for _ in range(48)]
    coord._forecast_arrays()
    data = coord._build_data_dict()
    coord.data = data
    return hass, entry, coord


def family_splits(entity_ids):
    families = []
    for eid in entity_ids:
        base = eid[len(PREFIX):] if eid.startswith(PREFIX) else eid
        family = base.split("_")[0]
        families.append(family)
    seen_closed = set()
    splits = 0
    last_family = None
    for fam in families:
        if fam != last_family:
            if fam in seen_closed:
                splits += 1
            seen_closed.add(fam)
            last_family = fam
    return splits


dt_util.freeze(START)
try:
    hass, entry, coord = build()
    entry.runtime_data = coord
    added = []
    asyncio.run(sensor.async_setup_entry(hass, entry, lambda es: added.extend(es)))
    entity_ids = [e.entity_id for e in added]
    print(f"RESULT total_entities={len(entity_ids)} count")

    ctor_order_splits = family_splits(entity_ids)
    print(f"RESULT family_splits_in_construction_order={ctor_order_splits} count")

    sorted_ids = sorted(entity_ids)
    sorted_splits = family_splits(sorted_ids)
    print(f"RESULT family_splits_when_actually_sorted={sorted_splits} count")

    # null control: shuffle construction order, re-derive the sorted view --
    # must be identical, since sorted() only depends on the string values.
    rng = random.Random(1234)
    shuffled = list(entity_ids)
    rng.shuffle(shuffled)
    shuffled_sorted = sorted(shuffled)
    invariant_ok = int(shuffled_sorted == sorted_ids)
    print(f"RESULT sort_invariant_to_construction_order={invariant_ok} bool")

finally:
    dt_util.freeze(None)

print(
    "RESULT brief_requirement_met="
    f"{int(sorted_splits == 0)} bool  "
    "(alphabetical sort of the real entity_id values clusters every family "
    "contiguously, independent of async_setup_entry's list literal order)"
)
