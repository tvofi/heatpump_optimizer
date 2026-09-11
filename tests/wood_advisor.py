#!/usr/bin/env python3
"""#796: a default-on sensor must not render Unknown while it is available.

    PYTHONPATH=tests/hastub python3 tests/wood_advisor.py

Home Assistant paints ``available=True`` and ``native_value is None`` as
Unknown — the same string it uses for an integration that has thrown.
``_WaitsForEvidenceMixin`` exists so that case is Unavailable instead.
``WoodCheaperBinarySensor`` already gates the same ``wood_fuel.ready`` key
and answers "nothing to report right now" with ``False``, not with None.

The one-line ``available`` gate on ``ready`` is not the fix: it only
silences installs that lack the furnace. On a wood-ready payload with no
``night_advice`` (the normal ``action == "none"`` branch after #795) the
sensor is still available-and-None. The rule below uses that payload, so a
ready-gate without a published idle state still fails.
"""
from __future__ import annotations

import asyncio
import sys

from harness import FakeCoordinator, FakeEntry, FakeHass, Results

from heatpump_optimizer import sensor

R = Results("Wood-burn advisor availability (#796)")
ENTRY = FakeEntry()


def _collect(data: dict | None):
    added = []

    def add_entities(entities):
        added.extend(entities)

    coordinator = FakeCoordinator(data)
    ENTRY.runtime_data = coordinator
    asyncio.run(sensor.async_setup_entry(FakeHass(), ENTRY, add_entities))
    return added


def _enabled_default(entity) -> bool:
    return getattr(type(entity), "_attr_entity_registry_enabled_default", True)


def _mute_reporters(data: dict | None) -> list[str]:
    """Enabled-by-default sensors that are available while publishing None.

    Same question the D8-02 judge adopted: read-only, default-on, available,
    and the published state is None. Driven through ``async_setup_entry`` so
    a later default-on sensor is in the population without being named here.
    """
    names = []
    for entity in _collect(data):
        if not _enabled_default(entity):
            continue
        if entity.available and entity.native_value is None:
            names.append(type(entity).__name__)
    return sorted(names)


def _advisor(data: dict | None) -> sensor.WoodBurnAdvisorSensor:
    return sensor.WoodBurnAdvisorSensor(FakeCoordinator(data), ENTRY)


DEFAULT = {"mode": "auto"}
WOOD_IDLE = {"mode": "auto", "wood_fuel": {"ready": True, "cheaper": False}}
WOOD_LIGHT = {
    "mode": "auto",
    "wood_fuel": {
        "ready": True,
        "night_advice": {
            "action": "light",
            "text": "light Thu 23:00",
            "when": "2026-01-01T23:00:00",
            "reason": "cheap night and a low tank",
        },
    },
}

R.section("The instance")

_default = _advisor(DEFAULT)
R.check(
    "without a wood furnace the advisor is unavailable, not Unknown",
    (not _default.available) and _default.native_value is None,
    f"available={_default.available} value={_default.native_value!r}",
)

_idle = _advisor(WOOD_IDLE)
R.check(
    "wood-ready with no advice publishes an idle state, not Unknown",
    _idle.available and _idle.native_value == "none",
    f"available={_idle.available} value={_idle.native_value!r}",
)

_light = _advisor(WOOD_LIGHT)
R.check(
    "wood-ready with light advice still publishes the text",
    _light.available and _light.native_value == "light Thu 23:00",
    f"available={_light.available} value={_light.native_value!r}",
)

R.section("The rule, not a roster")

# Population is every default-on sensor async_setup_entry adds. The
# predicate is the pair of payloads that differ only by night_advice:
# a sensor whose None is caused by a missing power key (or any other
# absent field) is in both sets; a sensor whose None is caused by
# missing night_advice leaves the light set. Naming WoodBurnAdvisor
# here would be the fourteenth roster entry the finding refused.
_idle_mute = set(_mute_reporters(WOOD_IDLE))
_light_mute = set(_mute_reporters(WOOD_LIGHT))
_caused_by_missing_advice = sorted(_idle_mute - _light_mute)
R.check(
    "no default-on sensor is available-and-None only because night_advice is absent",
    _caused_by_missing_advice == [],
    f"idle-only mute={_caused_by_missing_advice}",
)
R.check(
    "the idle payload is the one-line gate's null control",
    _idle.available,
    "a ready-gate alone would pass the no-furnace check and fail the idle state",
)

sys.exit(R.close("wood-advisor checks"))
