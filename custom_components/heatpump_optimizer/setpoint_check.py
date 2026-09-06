"""Pump set-point consistency: configured disinfection/min vs live entity (#408).

Consistency only — not an optimality advisory. The scoping judge refused
Fix-to-argmin: the argmin moves 50→65 °C under a price roll and the cost
surface's deterministic non-convexities (4.2080 SEK/day) exceed the median
gain (2.72). Space set-point is never recommended.
"""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.helpers import issue_registry as ir

from .const import (
    CONF_DHW_SETPOINT_ENTITY,
    CONF_SPACE_SETPOINT_ENTITY,
    DOMAIN,
    MIXING_VALVE_WRITE_EPSILON,
)

_LOGGER = logging.getLogger(__name__)

ISSUE_DHW = "dhw_setpoint_below_disinfection"
ISSUE_SPACE = "space_setpoint_unreadable"
_INVALID = ("unknown", "unavailable", "none", "")


def evaluate(coord: Any) -> None:
    """Read optional set-point entities and raise or clear the two issues.

    Stateless and idempotent: no coordinator attribute. A second call with
    the same inputs leaves ``hass.issues`` at one entry per issue id.
    Never raises into the caller — a balky entity must not break a solve.
    """
    try:
        _evaluate(coord)
    except Exception as err:  # noqa: BLE001 - never break a solve
        _LOGGER.debug("Set-point consistency check skipped: %s", err)


def _evaluate(coord: Any) -> None:
    hass = coord.hass
    config = coord._config
    params = coord._thermal_params
    _dhw(hass, config, params)
    _space(hass, config)


def _dhw_floor(params: Any) -> float:
    floor = float(params.dhw_min_temp)
    if params.dhw_legionella_enabled:
        floor = max(floor, float(params.dhw_legionella_temp))
    return floor


def _dhw(hass: Any, config: dict[str, Any], params: Any) -> None:
    entity_id = config.get(CONF_DHW_SETPOINT_ENTITY)
    pump = _read_setpoint(hass, entity_id) if entity_id else None
    floor = _dhw_floor(params)
    active = (
        bool(entity_id)
        and pump is not None
        and pump < floor - MIXING_VALVE_WRITE_EPSILON
    )
    data = {"entity_id": entity_id, "target": floor} if active else None
    placeholders = {
        "pump": f"{pump:.1f}" if pump is not None else "",
        "target": f"{floor:.0f}",
        "entity": entity_id or "",
    }
    _set_issue(
        hass, ISSUE_DHW, active, fixable=True, placeholders=placeholders, data=data
    )


def _space(hass: Any, config: dict[str, Any]) -> None:
    entity_id = config.get(CONF_SPACE_SETPOINT_ENTITY)
    if not entity_id:
        _set_issue(hass, ISSUE_SPACE, False)
        return
    readable = _read_setpoint(hass, entity_id) is not None
    _set_issue(
        hass,
        ISSUE_SPACE,
        not readable,
        placeholders={"entity": entity_id},
    )


def _read_setpoint(hass: Any, entity_id: str | None) -> float | None:
    if not entity_id:
        return None
    state = hass.states.get(entity_id)
    if state is None:
        return None
    raw = getattr(state, "state", None)
    if raw is None or str(raw).lower() in _INVALID:
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        pass
    attrs = getattr(state, "attributes", None) or {}
    try:
        return float(attrs.get("temperature"))
    except (TypeError, ValueError):
        return None


def _set_issue(
    hass: Any,
    issue_id: str,
    raise_it: bool,
    *,
    fixable: bool = False,
    placeholders: dict[str, str] | None = None,
    data: dict[str, Any] | None = None,
) -> None:
    if not raise_it:
        try:
            ir.async_delete_issue(hass, DOMAIN, issue_id)
        except Exception as err:  # noqa: BLE001 - clearing is best-effort
            _LOGGER.debug("Could not clear %s: %s", issue_id, err)
        return
    kwargs: dict[str, Any] = {
        "is_fixable": fixable,
        "severity": ir.IssueSeverity.WARNING,
        "translation_key": issue_id,
        "translation_placeholders": placeholders or {},
    }
    if data is not None:
        kwargs["data"] = data
    ir.async_create_issue(hass, DOMAIN, issue_id, **kwargs)
