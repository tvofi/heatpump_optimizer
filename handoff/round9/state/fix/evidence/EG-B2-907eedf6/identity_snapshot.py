"""Print platform<TAB>unique_id<TAB>entity_id<TAB>translation_key per entity, sorted.

Usage (from repo root): PYTHONPATH=tests/hastub:tests:. python identity_snapshot.py en|sv
Mirrors tests/entities.py ``collect``: real async_setup_entry per platform over a FakeCoordinator.
"""
import asyncio
import sys

from harness import FakeCoordinator, FakeEntry, FakeHass

import heatpump_optimizer as integration
from heatpump_optimizer import (
    binary_sensor, button, climate, const, datetime as datetime_mod, sensor, switch,
)

lang = sys.argv[1]
mods = {
    "sensor": sensor, "binary_sensor": binary_sensor, "button": button,
    "climate": climate, "switch": switch, "datetime": datetime_mod,
}
assert sorted(mods) == sorted(const.PLATFORMS), (sorted(mods), const.PLATFORMS)
assert sorted(str(p) for p in integration.PLATFORM_LIST) == sorted(mods)

entry = FakeEntry()  # entry_id is the fixed "test_entry"
rows = []
for platform, mod in mods.items():
    hass = FakeHass()
    hass.config.language = lang
    coord = FakeCoordinator({})
    coord.hass.config.language = lang
    coord._month_totals = {"dhw": (41.5, 62.25), "space": (120.0, 180.0)}
    entry.runtime_data = coord
    added = []

    def add(entities, hass=hass, added=added):
        for e in entities:
            e.hass = hass
        added.extend(entities)

    asyncio.run(mod.async_setup_entry(hass, entry, add))
    for e in added:
        rows.append("\t".join((
            platform,
            str(getattr(e, "_attr_unique_id", None)),
            str(getattr(e, "entity_id", None)),
            str(getattr(e, "_attr_translation_key", None)),
        )))
print("\n".join(sorted(rows)))
