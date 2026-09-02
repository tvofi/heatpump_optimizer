"""Diagnostics for the Heat Pump Optimizer config entry (audit D10-12).

``Download diagnostics`` in Home Assistant produces this JSON. The rule the
Gold-scale item sets: no credential ever leaves the instance. The Tibber
token is redacted wholesale (not masked -- a masked token is still a
partial credential), and the entity ids in the configuration are kept
because a diagnostics file without them cannot say which sensors the
install was reading -- which is most of what debugging needs.
"""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_TIBBER_TOKEN, DOMAIN
from .coordinator import HeatPumpOptimizerCoordinator

#: Keys whose values are credentials and never leave the instance.
TO_REDACT = {CONF_TIBBER_TOKEN}


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
    return {
        "entry": {
            "version": entry.version,
            "options_keys": sorted(entry.options.keys()),
        },
        "config": {
            key: ("REDACTED" if key in TO_REDACT else value)
            for key, value in entry.data.items()
        },
        "coordinator": _coordinator_snapshot(coord) if coord else None,
        "domain": DOMAIN,
    }
