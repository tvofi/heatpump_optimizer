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
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from homeassistant.components.diagnostics import REDACTED, async_redact_data
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant

from . import accuracy, debugger, pump_arbiter
from .const import CONF_TIBBER_TOKEN, DOMAIN
from .coordinator import (
    CoordinatorDiagnostics,
    HeatPumpOptimizerConfigEntry,
    HeatPumpOptimizerCoordinator,
)

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
        "cop_scale": state.cop_scale if state else None,
        "cop_samples": state.cop_samples if state else None,
        "house_heat_loss_scale": state.house_heat_loss_scale if state else None,
        "last_update_success": bool(
            getattr(coord, "last_update_success", False)
        ),
    }
    if state:
        snap.update(state.learner_summaries)
    # One row per module view. ``cop_learner`` says why the observed-COP sensor
    # has nothing yet: it is unavailable then, and HA hides its attributes.
    for key, view in (
        ("pump_duty", pump_arbiter.diagnostics_view),
        ("cop_learner", lambda c: accuracy.diagnostics_view(c.measured_cop, c.thermal_params)),
    ):
        try:
            snap[key] = view(coord)
        except Exception:  # noqa: BLE001 -- diagnostics never breaks
            snap[key] = "unavailable"
    return snap


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
        _coarsen(
            {
                "entry": {
                    "version": entry.version,
                    "options_keys": sorted(entry.options.keys()),
                },
                "config": dict(entry.data),
                "coordinator": snapshot,
                "domain": DOMAIN,
                # #1940: capped, so a week too large to inline is its summary.
                "debug": debugger.capped(
                    await collector.async_bundle(coord, snapshot),
                    f"{DOMAIN}_{entry.entry_id}_debug",
                ) if collector else None,
            }
        ),
        TO_REDACT,
    )
