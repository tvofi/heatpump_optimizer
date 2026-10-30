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

R.section("The COP guard, not a hole")

# A record with no outdoor temperature folds to COP 0.0 through wood_fuel's
# own _force_float, so this is reachable on a real payload, not a unit-test
# contrivance. `price / cop` raises on a zero COP and would silently flip the
# comparison on a negative one; cheaper_hour_count must SKIP such an hour.
# The positive control beside it shows the guard is not rejecting every hour.
from heatpump_optimizer.wood_fuel import cheaper_hour_count

try:
    _zero_cop = cheaper_hour_count(
        wood_sek=1.0, prices=[1.0], cops=[0.0],
        runs=[True],
    )
except ZeroDivisionError as _zero_cop_err:
    _zero_cop = _zero_cop_err
R.check(
    "an hour whose COP is zero is skipped, not divided by",
    _zero_cop == 0,
    f"cops=[0.0] -> {_zero_cop!r}",
)
R.check(
    "and a usable COP still counts the hour when wood is cheaper",
    cheaper_hour_count(
        wood_sek=1.0, prices=[10.0], cops=[3.0],
        runs=[True],
    )
    == 1,
    "a guard that skipped every hour would hide the real comparison",
)

R.section("Today's cheaper windows and the lighting window")

# Driven through the production view builder. A ready config at 1275 SEK/m3
# of mixed packed wood at 75 % burns at 1275 / (1700 * 0.75) = 1.0 SEK/kWh;
# with a flat COP of 3 the pump's heat costs price / 3, so wood is cheaper
# exactly on the steps priced above 3.0.
from datetime import datetime as _dt, timedelta as _td, timezone as _tz

from heatpump_optimizer import binary_sensor as _bs
from heatpump_optimizer.wood_fuel import build_wood_fuel_view

_WOOD_READY = {
    "wood_tank_top_entity": "sensor.wood_tank_top",
    "external_heat_enabled": True,
    "wood_type": "mixed",
    "wood_packing": "packed",
    "wood_price_sek_m3": 1275.0,
    "wood_furnace_efficiency": 75.0,
}
_DAY0 = _dt(2026, 1, 15, 0, 0, tzinfo=_tz.utc)
# 30 hourly steps: today and the first six hours of tomorrow.
_STAMPS = [_DAY0 + _td(hours=i) for i in range(30)]


def _view(cheap_steps, off_steps=(), config=None):
    n = len(_STAMPS)
    return build_wood_fuel_view(
        _WOOD_READY if config is None else config,
        prices=[4.0 if i in cheap_steps else 1.0 for i in range(n)],
        outdoor=[0.0] * n,
        runs=[i not in off_steps for i in range(n)],
        cop_at=lambda _t: 3.0,
        timestamps=_STAMPS,
        forecast_kw=[],
        suppressing=False,
        local_tz=_tz.utc,
    )


def _iso(hour, minute=0):
    return (_DAY0 + _td(hours=hour, minutes=minute)).isoformat()


def _lighting(view):
    return view.get("lighting_start"), view.get("lighting_end")


# Two cheaper runs today (06-08 and 17-20), a cheaper step at 12 while the
# pump is planned off, and a cheaper step tomorrow at 02.
_two = _view({6, 7, 12, 17, 18, 19, 26}, off_steps={12})
R.check(
    "a day with two cheaper runs gives two windows, each contiguous run once",
    _two.get("cheaper_windows")
    == [
        {"start": _iso(6), "end": _iso(8)},
        {"start": _iso(17), "end": _iso(20)},
    ],
    repr(_two.get("cheaper_windows")),
)
R.check(
    "the lighting window opens the default 60 min before the first window "
    "and closes at its start",
    _lighting(_two) == (_iso(5), _iso(6)),
    repr(_lighting(_two)),
)
_lead90 = _view({6, 7}, config={**_WOOD_READY, "wood_lighting_lead_minutes": 90})
R.check(
    "the lead time is the configured option",
    _lighting(_lead90) == (_iso(4, 30), _iso(6)),
    repr(_lighting(_lead90)),
)
_now_open = _view({0, 1})
R.check(
    "a window open at the plan's first step lights now, never in the past",
    _lighting(_now_open) == (_iso(0), _iso(0)),
    repr(_lighting(_now_open)),
)
_pump_off = _view({12}, off_steps={12})
R.check(
    "a cheaper step while the pump is planned off is not a window",
    _pump_off.get("cheaper_windows", []) == [] and _lighting(_pump_off) == (None, None),
    repr(_pump_off.get("cheaper_windows")),
)
_tomorrow = _view({26})
R.check(
    "a cheaper step tomorrow is counted but is not one of today's windows",
    _tomorrow.get("cheaper_windows", []) == []
    and _tomorrow.get("cheaper_hour_count") == 1,
    repr(_tomorrow.get("cheaper_windows")),
)
_never = _view(set())
R.check(
    "null control: a day wood never beats the pump gives no windows and no "
    "lighting window",
    _never.get("cheaper_windows", []) == []
    and _lighting(_never) == (None, None)
    and _never.get("cheaper_hour_count") == 0,
    repr(_never),
)
_attrs = _bs.WoodCheaperBinarySensor(
    FakeCoordinator({"wood_fuel": _two}), ENTRY
).extra_state_attributes
R.check(
    "the wood sensor publishes the windows and the lighting window as attributes",
    _attrs.get("cheaper_windows") == _two["cheaper_windows"]
    and (_attrs.get("lighting_start"), _attrs.get("lighting_end"))
    == (_iso(5), _iso(6)),
    repr(_attrs),
)
_null_attrs = _bs.WoodCheaperBinarySensor(
    FakeCoordinator({"wood_fuel": _never}), ENTRY
).extra_state_attributes
R.check(
    "and with no window it publishes an empty list and no lighting window",
    _null_attrs.get("cheaper_windows") == []
    and (_null_attrs.get("lighting_start"), _null_attrs.get("lighting_end"))
    == (None, None),
    repr(_null_attrs),
)

sys.exit(R.close("wood-advisor checks"))
