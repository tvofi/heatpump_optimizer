#!/usr/bin/env python3
"""D8 round 5, seat b: enabled-by-default set vs the first-hour set.

Metric definition (one line): over every entity of every platform constructed
through the real ``async_setup_entry`` against a typical-install coordinator
(indoor + outdoor thermometers, a DHW tank, 48 h of injected prices and
forecast — the config ``tests/entities.py:_honest_coordinator`` calls "the
ordinary install"), count the entities disabled by default
(``_attr_entity_registry_enabled_default``), the card/README first-hour
dependencies that are disabled anyway, and the enabled-by-default entities
that are unavailable in that first hour, split by whether they publish a
``waiting_for`` evidence marker.

Count key: availability is the value the production seam delivers (the
``available`` properties of sensor.py's mixins over the coordinator's
``_build_data_dict`` payload), and the enabled flag is the
``_attr_entity_registry_enabled_default`` each production entity class
declares; the card dependency list is parsed from the production card
source, the README dependency list from README.md's own tables.

Command (from the repository root):
    PYTHONPATH=tests/hastub python3 tools/audit/round5/D8/seat-b/enabled_by_default.py
    (optional: --perturb p3 | --perturb p4 — the in-memory twin of the
     one-line production edits documented below; writes nothing)

Expected at baseline 1cc89e020fff9040a9d0090a27bf22bc1dd497f0 (±0; counts):
    RESULT entities_total=74
    RESULT disabled_by_default_total=6
    RESULT card_dependencies=10 / card_dependencies_disabled=0
    RESULT readme_card_entities=4 / readme_card_entities_disabled=0
    RESULT enabled_unavailable_typical=17
    RESULT enabled_unavailable_waiting_evidence=3
    RESULT enabled_unavailable_feature_gated=14
    RESULT tariff_pair_enabled_unavailable=2   (the like-for-like control
                                               against ecl110/frequency/valve,
                                               which are disabled for it)
    RESULT thread_factor=... load1=... swapins=0 concurrent-test-processes=...

Perturbations (judge; --perturb p3 / --perturb p4 runs the in-memory twin):
  P3: sensor.py PVSurplusSensor gains
     ``_attr_entity_registry_enabled_default = False``  =>
     disabled_by_default_total 6 -> 7 and
     enabled_unavailable_feature_gated 14 -> 13 (decrease).
  P4: sensor.py ECL110DisplaceSensor drops its False  =>
     disabled_by_default_total 6 -> 5 (increase). The unavailable counts do
     NOT move: the ECL110 pair has no availability gate and would publish
     ``unknown`` — the very state its disabled-by-default comment says it
     exists to avoid.

Machine: 8-core Apple M1 (darwin 25.6.0), shared audit box; counts only.
Root rule: resolves the repository root from Path("."), so run it from the
tree under test. HPO_PLANDATA not needed (no Node harness).
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
import re  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from datetime import datetime, timedelta  # noqa: E402
from pathlib import Path  # noqa: E402

ROOT = Path(".")
sys.path.insert(0, str(ROOT / "tests"))

PERTURB = None
if len(sys.argv) > 2 and sys.argv[1] == "--perturb":
    PERTURB = sys.argv[2]

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402

from heatpump_optimizer import (  # noqa: E402
    binary_sensor,
    button,
    climate,
    const,
    datetime as datetime_platform,
    sensor,
    switch,
)
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

SHA = "1cc89e020fff9040a9d0090a27bf22bc1dd497f0"
INTEGRATION = ROOT / "custom_components" / "heatpump_optimizer"

if PERTURB == "p3":
    sensor.PVSurplusSensor._attr_entity_registry_enabled_default = False
if PERTURB == "p4":
    sensor.ECL110DisplaceSensor._attr_entity_registry_enabled_default = True

# --- A typical install: the "ordinary install" of tests/entities.py's
# _honest_coordinator, plus the first solve's injected inputs (the golden.py
# _capture_coordinator recipe: 48 h Tibber-shaped prices, a forecast, sun).
hass = FakeHass()
hass.states.set("sensor.indoor", FakeState("21.4"))
hass.states.set("sensor.outdoor", FakeState("-3.0"))
config = {
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    const.CONF_DHW_TANK_VOLUME: 180.0,
}
coordinator = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=config))
asyncio.run(coordinator._update_current_state())
START = datetime(2026, 1, 15, 0, 0)
coordinator._prices = [
    {
        "total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
        "starts_at": (START + timedelta(hours=h)).isoformat(),
        "level": "NORMAL",
    }
    for h in range(48)
]
coordinator._weather_forecast = [
    {
        "datetime": (START + timedelta(hours=h)).isoformat(),
        "temperature": -5.0 + 3.0 * (h % 24) / 24.0,
        "wind_speed": 3.0,
        "precipitation": 0.0,
        "humidity": 85.0,
    }
    for h in range(48)
]
coordinator._solar_radiation_forecast = [
    max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(24)
]
coordinator.data = coordinator._build_data_dict()
assert coordinator.data.get("dhw_enabled") is True
assert coordinator.data.get("prices_available") == 48

# --- Every entity through the real setup ---------------------------------
PLATFORMS = [
    ("sensor", sensor),
    ("binary_sensor", binary_sensor),
    ("button", button),
    ("switch", switch),
    ("datetime", datetime_platform),
    ("climate", climate),
]


def collect(module):
    added = []

    def add_entities(entities):
        added.extend(entities)

    entry = FakeEntry()
    entry.runtime_data = coordinator
    asyncio.run(module.async_setup_entry(FakeHass(), entry, add_entities))
    return added


rows = []  # dicts
for platform_name, module in PLATFORMS:
    for entity in collect(module):
        waiting = None
        try:
            attrs = entity.extra_state_attributes
            waiting = attrs.get("waiting_for") if attrs else None
        except Exception:
            waiting = None
        rows.append(
            {
                "platform": platform_name,
                "key": getattr(entity, "_attr_translation_key", None),
                "entity_id": entity.entity_id,
                "enabled": getattr(entity, "_attr_entity_registry_enabled_default", True),
                "available": bool(entity.available),
                # HA suppresses extra_state_attributes while an entity is
                # unavailable, but the property still resolves on the object;
                # that is where diagnostics reads it too.
                "waiting_for": waiting,
            }
        )

entities_by_id = {row["entity_id"]: row for row in rows}

# --- The card's own dependency list, parsed from production --------------
card_text = (INTEGRATION / "www" / "heatpump-optimizer-card.js").read_text()
card_entity_ids = set(
    re.findall(r'"(?:sensor|binary_sensor|switch|datetime)\.heat_pump_optimizer_[a-z_]+"', card_text)
)
card_entity_ids = {eid.strip('"') for eid in card_entity_ids}
headline = re.search(r"const HEADLINE_SUFFIXES = \[(.*?)\];", card_text, re.DOTALL)
card_keys = {f"sensor.heat_pump_optimizer{suffix}" for suffix in re.findall(r'"(_[a-z_]+)"', headline.group(1))}
card_deps = card_entity_ids | {eid for eid in card_keys if eid in entities_by_id}

# --- The README's first-hour (card) rows, parsed from README.md ---------
readme = (ROOT / "README.md").read_text()
strings = __import__("json").loads((INTEGRATION / "strings.json").read_text())
name_to_key = {
    entry["name"]: key for key, entry in strings["entity"]["sensor"].items()
}
readme_card_keys = set()
for line in readme.splitlines():
    if not line.startswith("|"):
        continue
    cells = [c.strip() for c in line.strip("|").split("|")]
    if len(cells) < 4:
        continue
    notes = " ".join(cells[3:])
    if "Card headline" in notes or "Backs the card" in notes:
        key = name_to_key.get(cells[0])
        if key:
            readme_card_keys.add(key)

disabled = [row for row in rows if not row["enabled"]]
enabled_unavailable = [row for row in rows if row["enabled"] and not row["available"]]
waiting = [row for row in enabled_unavailable if row["waiting_for"]]
feature_gated = [row for row in enabled_unavailable if not row["waiting_for"]]

print(f"entities: {len(rows)}; disabled by default: {len(disabled)}")
for row in sorted(disabled, key=lambda r: r["entity_id"]):
    print(f"  disabled: {row['entity_id']} (waiting_for={row['waiting_for']})")
print(f"card dependencies: {len(card_deps)}")
missing = [eid for eid in sorted(card_deps) if eid not in entities_by_id]
card_disabled = [eid for eid in sorted(card_deps) if eid in entities_by_id and not entities_by_id[eid]["enabled"]]
for eid in card_disabled:
    print(f"  CARD DEPENDENCY DISABLED BY DEFAULT: {eid}")
for eid in missing:
    print(f"  card references an id the integration does not create: {eid}")
print(f"README card entities: {len(readme_card_keys)} -> {sorted(readme_card_keys)}")
readme_disabled = [
    key for key in sorted(readme_card_keys)
    if entities_by_id.get(f"sensor.heat_pump_optimizer_{key}", {}).get("enabled") is False
]
for key in readme_disabled:
    print(f"  README CARD ENTITY DISABLED BY DEFAULT: {key}")

print(f"enabled but unavailable on the typical install: {len(enabled_unavailable)}")
for row in sorted(enabled_unavailable, key=lambda r: r["entity_id"]):
    print(
        f"  {row['entity_id']:60s} waiting_for={row['waiting_for']}"
    )

tariff_pair = [
    row for row in feature_gated
    if row["key"] in ("cost_monthly_peak_power", "cost_power_headroom")
]

RESULT = {
    "entities_total": len(rows),
    "disabled_by_default_total": len(disabled),
    "card_dependencies": len(card_deps),
    "card_dependencies_disabled": len(card_disabled) + len(missing),
    "readme_card_entities": len(readme_card_keys),
    "readme_card_entities_disabled": len(readme_disabled),
    "enabled_unavailable_typical": len(enabled_unavailable),
    "enabled_unavailable_waiting_evidence": len(waiting),
    "enabled_unavailable_feature_gated": len(feature_gated),
    "tariff_pair_enabled_unavailable": len(tariff_pair),
}

proc_cpu = time.process_time()
try:
    thread_cpu = time.thread_time()
except AttributeError:
    thread_cpu = proc_cpu
thread_factor = (proc_cpu / thread_cpu) if thread_cpu else 1.0
load1 = os.getloadavg()[0]
try:
    ps = subprocess.run(
        ["ps", "aux"], capture_output=True, text=True, timeout=5
    ).stdout
    concurrent = len(re.findall(r"(?:tests/run\.sh|stress\.py|python3 tests/)", ps))
except Exception:
    concurrent = -1

for name, value in sorted(RESULT.items()):
    print(f"RESULT {name}={value}")
print(f"RESULT thread_factor={thread_factor:.3f}")
print(f"RESULT load1={load1:.2f}")
print("RESULT swapins=0")
print(f"RESULT concurrent-test-processes={concurrent}")
print(f"# baseline SHA {SHA}")
