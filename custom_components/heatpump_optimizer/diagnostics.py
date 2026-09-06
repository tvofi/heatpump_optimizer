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
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant

from .const import CONF_TIBBER_TOKEN, DOMAIN
from .coordinator import HeatPumpOptimizerCoordinator

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
    derivable).
    """
    snap: dict[str, Any] = {
        "mode": getattr(coord, "_mode", None),
        "tibber_outage_cycles": getattr(coord, "_tibber_outage_cycles", None),
        "tibber_reauth_started": getattr(coord, "_tibber_reauth_started", None),
        "weather_stale_hours": coord.weather_stale_hours()
        if hasattr(coord, "weather_stale_hours")
        else None,
        "optimization_running": getattr(coord, "_optimization_running", None),
        "solve_failures": getattr(coord, "_solve_failures", None),
        "cop_scale": getattr(coord, "_cop_scale", None),
        "cop_samples": getattr(coord, "_cop_samples", None),
        "house_heat_loss_scale": getattr(coord, "_house_heat_loss_scale", None),
        "last_update_success": bool(
            getattr(coord, "last_update_success", False)
        ),
    }
    for name in (
        "_accuracy", "_comfort_learner", "_curve_learner", "_price_model",
    ):
        obj = getattr(coord, name, None)
        summary = getattr(obj, "summary", None)
        if callable(summary):
            try:
                snap[name.lstrip("_")] = summary()
            except Exception:  # noqa: BLE001 -- diagnostics never breaks
                snap[name.lstrip("_")] = "summary unavailable"
    return snap


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry[HeatPumpOptimizerCoordinator]
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coord = entry.runtime_data if hasattr(entry, "runtime_data") else None
    # Both passes run over the whole payload rather than over ``entry.data``
    # alone, so a coordinate or a credential that a future coordinator
    # summary starts carrying is covered without a second decision here.
    return async_redact_data(
        _coarsen(
            {
                "entry": {
                    "version": entry.version,
                    "options_keys": sorted(entry.options.keys()),
                },
                "config": dict(entry.data),
                "coordinator": _coordinator_snapshot(coord) if coord else None,
                "domain": DOMAIN,
            }
        ),
        TO_REDACT,
    )
