"""Diagnostics for the Heat Pump Optimizer config entry (audit D10-12).

``Download diagnostics`` in Home Assistant produces this JSON, and the file
routinely ends up attached to a public issue or forum post.

The rule the Gold-scale item set was "no credential ever leaves the
instance". #509 found that rule narrower than the risk: ``entry.data`` was
emitted verbatim apart from the token, and ``CONF_SOLAR_LOCATION`` is seeded
by ``config_flow._default_location`` from ``hass.config.latitude`` -- so the
usual install, which accepts the pre-filled field, published its home to
building precision. The rule is now **no credential and no personal
location**, enforced with Home Assistant's own ``async_redact_data`` so it
holds at any depth rather than only over the top-level keys of ``entry.data``.

What is kept, and why, because over-redaction makes a diagnostics file
useless for the support it exists for: the entity ids, which say which
sensors the install was reading; the MQTT topics, which are the usual cause
of an ECL110 control fault; and the building and tariff parameters, which are
the thermal model a "my plan is wrong" report is about. None of those is
pre-filled from anything private. ``entry.options`` is still emitted as key
names only.

R9-UX-7 (#1795) adds what the published payload says about the last cycle:
the last diagnosis, the input states, a plan summary (counts and totals, no
per-step series) and the learning view. Two kinds of entity id are an
exception to "ids are kept": a ``person.*`` id names a member of the
household and a ``calendar.*`` id a family calendar, and the away and
holiday options hold them. They are redacted wherever they appear, inside a
message string too, because an input problem echoes the id it is about.
"""
from __future__ import annotations

import re
from collections.abc import Callable, Mapping
from typing import Any

from homeassistant.components.diagnostics import REDACTED, async_redact_data
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant

from . import debugger, draw_range, pump_arbiter
from .const import CONF_COP_SCALE, CONF_TIBBER_TOKEN, DOMAIN
from .thermal_model import probe_install
from .coordinator import (
    CoordinatorDiagnostics,
    HeatPumpOptimizerConfigEntry,
    HeatPumpOptimizerCoordinator,
)
from .payload import LearningView

#: Keys whose values never leave the instance, at any depth: the Tibber
#: credential, and the entry name, which is free text the user typed and
#: which nothing outside the config flow's entry title reads. Redacting
#: ``name`` at any depth is deliberate even though it is a common key --
#: blanking an internal label a future summary adds is a far cheaper failure
#: than publishing a household name, and a privacy control fails safe.
TO_REDACT = {CONF_TIBBER_TOKEN, CONF_NAME}

#: Coordinate keys, wherever they are nested. Coarsened, not redacted.
COORDINATE_KEYS = frozenset({"latitude", "longitude"})

#: Decimal places kept on a coordinate. One place is about 11 km of latitude
#: and 6 km of longitude at the 59 degrees N of a Swedish install -- far
#: coarser than the dwelling #509 was about, and at or below Open-Meteo's own
#: forecast grid, so it cannot change which cell a reader would look up. A
#: fully redacted coordinate would hide the two faults this field actually
#: produces: latitude and longitude swapped, and a location in the wrong
#: country.
COORDINATE_PLACES = 1


#: Entity ids that name a person or a household calendar, anywhere in a
#: string: the away presence and holiday calendar options hold them, and an
#: input problem's message repeats the id it is about.
PRIVATE_ENTITY_ID = re.compile(r"\b(?:person|calendar)\.[a-z0-9_]+")

#: The input watchdog's published keys (the coordinator's input health view).
INPUT_KEYS = (
    "input_health",
    "stale_inputs",
    "input_problems",
    "problem_inputs",
    "problem_messages",
    "input_ages_minutes",
    "learners_frozen",
    "learner_freeze_reason",
)


def _without_private_ids(value: Any) -> Any:
    """``value`` with every person and calendar entity id redacted, at any depth."""
    if isinstance(value, str):
        return PRIVATE_ENTITY_ID.sub(REDACTED, value)
    if isinstance(value, Mapping):
        return {key: _without_private_ids(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_without_private_ids(item) for item in value]
    return value


def _plan_summary(data: Mapping[str, Any]) -> dict[str, Any]:
    """What the current plan is, in counts and totals: no per-step series."""

    def channel(plan: Any) -> dict[str, Any]:
        plan = plan if isinstance(plan, Mapping) else {}
        return {
            "steps": len(plan.get("forecast") or []),
            "slots": len(plan.get("slots") or []),
            "total_energy_kwh": plan.get("total_energy_kwh"),
            "total_cost": plan.get("total_cost"),
            "active_now": plan.get("active_now"),
        }

    return {
        **{
            key: data.get(key)
            for key in (
                "mode",
                "optimization_status",
                "last_optimization",
                "next_optimization",
                "plan_age_minutes",
                "plan_stale",
                "current_action",
            )
        },
        "space": channel(data.get("space_plan")),
        "dhw": channel(data.get("dhw_plan")),
    }


def _published_sections(coord: Any) -> dict[str, Any]:
    """The last cycle as the entities saw it: diagnosis, inputs, plan, learning."""
    data = getattr(coord, "data", None)
    data = data if isinstance(data, Mapping) else {}
    insight = data.get("insight")
    return {
        "last_diagnosis": (
            insight.get("last_diagnosis") if isinstance(insight, Mapping) else None
        ),
        "inputs": {key: data[key] for key in INPUT_KEYS if key in data},
        "plan": _plan_summary(data),
        "learning": {key: data[key] for key in LearningView.__annotations__ if key in data},
    }


def _coordinate(value: Any) -> Any:
    """One coordinate, coarsened -- or redacted if it is not a number.

    Free text under a coordinate key can be an address, so only something
    that converts to a float is published.
    """
    try:
        return round(float(value), COORDINATE_PLACES)
    except (TypeError, ValueError):
        return REDACTED


def _coarsen(value: Any) -> Any:
    """``value`` with every coordinate coarsened, at any depth."""
    if isinstance(value, Mapping):
        return {
            key: _coordinate(item) if key in COORDINATE_KEYS else _coarsen(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_coarsen(item) for item in value]
    return value


def _coordinator_snapshot(coord: HeatPumpOptimizerCoordinator) -> dict[str, Any]:
    """The runtime state a bug report actually needs.

    Deliberately small and plain: the learners' own summary() dictionaries,
    the outage latches and the staleness flags -- the things that explain
    WHY a plan looks wrong -- without the 200-key published payload
    (reproducible from the entities) or any trajectory array (large, and
    derivable). The counters and learner summaries arrive through the
    coordinator's published ``diagnostics_state`` view (#1739); a
    coordinator that cannot produce one (a duck-typed harness) reports the
    fields as ``None``, exactly as the per-field ``getattr`` fallbacks did.
    """
    try:
        state: CoordinatorDiagnostics | None = coord.diagnostics_state()
    except Exception:  # noqa: BLE001 -- diagnostics never breaks
        state = None
    snap: dict[str, Any] = {
        "mode": getattr(coord, "mode", None),
        "tibber_outage_cycles": state.tibber_outage_cycles if state else None,
        "tibber_reauth_started": state.tibber_reauth_started if state else None,
        "weather_stale_hours": coord.weather_stale_hours()
        if hasattr(coord, "weather_stale_hours")
        else None,
        "optimization_running": getattr(coord, "optimization_running", None),
        "solve_failures": state.solve_failures if state else None,
        CONF_COP_SCALE: state.cop_scale if state else None,
        "cop_samples": state.cop_samples if state else None,
        "house_heat_loss_scale": state.house_heat_loss_scale if state else None,
        "last_update_success": bool(
            getattr(coord, "last_update_success", False)
        ),
    }
    if state:
        snap.update(state.learner_summaries)
    snap.update({key: _never_breaks(view, coord) for key, view in _VIEWS})
    return snap


def _never_breaks(view: Callable[[Any], Any], coord: Any) -> Any:
    """One module's view, or ``"unavailable"``: diagnostics never breaks."""
    try:
        return view(coord)
    except Exception:  # noqa: BLE001 -- diagnostics never breaks
        return "unavailable"


#: Each module's own ``diagnostics_view``, one ``(key, view)`` row per module.
#: A row reads the coordinator's public views and hands its module values.
_VIEWS: tuple[tuple[str, Callable[[Any], Any]], ...] = (
    ("pump_duty", pump_arbiter.diagnostics_view),
    ("draw_range", lambda c: draw_range.diagnostics_view(
        c.accuracy.draw, c.thermal_params,
        probe_install(c.arbiter_inputs().config))),
)


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: HeatPumpOptimizerConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coord = entry.runtime_data if hasattr(entry, "runtime_data") else None
    snapshot = _coordinator_snapshot(coord) if coord else None
    collector = debugger.collector_for(coord) if coord else None
    # Both passes run over the whole payload rather than over ``entry.data``
    # alone, so a coordinate or a credential that a future coordinator
    # summary starts carrying is covered without a second decision here --
    # the debug bundle's payload snapshots and store documents included.
    return async_redact_data(
        _without_private_ids(
            _coarsen(
                {
                    "entry": {
                        "version": entry.version,
                        "options_keys": sorted(entry.options.keys()),
                    },
                    "config": dict(entry.data),
                    "coordinator": snapshot,
                    **_published_sections(coord),
                    "domain": DOMAIN,
                    # #1940: capped, so a week too large to inline is its summary.
                    "debug": debugger.capped(
                        await collector.async_bundle(coord, snapshot),
                        f"{DOMAIN}_{entry.entry_id}_debug",
                    ) if collector else None,
                }
            )
        ),
        TO_REDACT,
    )
