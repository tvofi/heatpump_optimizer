"""Pump set-point consistency: configured disinfection/min vs live entity (#408).

Consistency only — not an optimality advisory. The scoping judge refused
Fix-to-argmin: the argmin moves 50→65 °C under a price roll and the cost
surface's deterministic non-convexities (4.2080 SEK/day) exceed the median
gain (2.72). Space set-point is never recommended.
"""
from __future__ import annotations

import logging
from typing import Any, Callable

from .const import MIXING_VALVE_WRITE_EPSILON
from .entry_config import EntryConfig
from .issues import clear_issue, set_issue
from .inputs import (
    read_temperature_delta_k,
    quantise_setpoint_c,
    read_setpoint,
    setpoint_and_unit,
    setpoint_grid,
    temperature_from_c,
)
from .quiet_windows import silent_unenforceable
from .thermal_model import dhw_start_below_c, dhw_step_target_c

_LOGGER = logging.getLogger(__name__)

ISSUE_DHW = "dhw_setpoint_below_disinfection"
ISSUE_SPACE = "space_setpoint_unreadable"
#: #1910 (SW-1): silent rows configured with no control that can hold
#: them. A warning, not a fix -- the remedy is an assignment only the
#: setup diagram (or SW-4's Modbus schedule) can make.
ISSUE_QUIET = "quiet_silent_not_enforced"
ISSUE_DHW_START = "dhw_minimum_above_start"


class ConfigNotices:
    """The standing warnings about stored configuration, one rule for all of them.

    Each is a persistent WARNING whose translation key is its issue id: the
    configuration survives a restart unchanged, so the notice must too.

    * Raised once per offending value. Re-raising every cycle refreshes the
      issue's timestamp and buries when the bad value first appeared, so
      ``report`` creates only when the value it is told about changes.
    * Cleared UNCONDITIONALLY. Correcting the configuration writes options,
      which reloads the entry and builds a new instance whose memory starts
      empty -- a delete gated on that memory can never run, and a persistent
      notice saying "this clears when you fix it" would stay up forever (the
      fee audit had exactly that defect until v5.1.7). The memory only ever
      suppresses a repeated create; deleting an absent issue is a no-op.
    """

    def __init__(self) -> None:
        self._raised: dict[str, object] = {}

    def report(
        self,
        hass: Any,
        issue_id: str,
        offending: object | None,
        placeholders: dict[str, str] | None = None,
    ) -> None:
        """``offending`` is what is wrong now, or ``None`` when nothing is."""
        if offending is None:
            clear_issue(hass, issue_id)
            self._raised.pop(issue_id, None)
            return
        if self._raised.get(issue_id) == offending:
            return
        set_issue(hass, issue_id, True, persistent=True, placeholders=placeholders)
        self._raised[issue_id] = offending


def evaluate(coord: Any, gated: Callable[[float], bool] | None = None) -> None:
    """Read optional set-point entities and raise or clear the two issues.

    Stateless and idempotent: no coordinator attribute. A second call with
    the same inputs leaves ``hass.issues`` at one entry per issue id.
    Never raises into the caller — a balky entity must not break a solve.
    ``gated`` is whether a reading is the pump-duty arbiter's own hot-water
    write (wired by the coordinator, which owns both sides of the seam,
    #1739): that is a step decision, not a mis-set point.
    """
    try:
        _evaluate(coord, gated)
    except Exception as err:  # noqa: BLE001 - never break a solve
        _LOGGER.debug("Set-point consistency check skipped: %s", err)


def _evaluate(coord: Any, gated: Callable[[float], bool] | None) -> None:
    hass = coord.hass
    config = coord.effective_config
    params = coord.thermal_params
    _dhw(hass, config, params, gated)
    _dhw_start(hass, config, params)
    _space(hass, config)
    _quiet(hass, config)


def _dhw_start(hass: Any, config: dict[str, Any], params: Any) -> None:
    """One warning when this pump cannot hold the hot-water minimum.

    A pump with a start hysteresis (``dhw_hysteresis_entity``) starts a charge
    only below its target less that (``thermal_model.dhw_start_below_c``, on
    the everyday target as written, ``thermal_model.dhw_step_target_c`` on the
    set-point entity's grid), and the plan places no charge it will not start.
    A minimum above that start temperature is therefore one the tank must fall
    through before any charge can begin: the plan shows the tank under it,
    and this says why. Cleared with no hysteresis read, and with hot water
    disabled (``dhw_enabled``): no charge is planned then and no minimum held.
    """
    cfg = EntryConfig.from_mapping(config)
    hysteresis = read_temperature_delta_k(hass, cfg.dhw_hysteresis_entity)
    target = dhw_step_target_c(params, False, setpoint_grid(hass, cfg.dhw_setpoint_entity))
    start = dhw_start_below_c(target, hysteresis)
    floor = float(params.dhw_min_temp)
    set_issue(
        hass,
        ISSUE_DHW_START,
        bool(params.dhw_enabled) and start is not None and floor > start,
        placeholders={
            "floor": f"{floor:.1f}",
            "start": "" if start is None else f"{start:.1f}",
            "target": f"{target:.1f}",
            "hysteresis": "" if hysteresis is None else f"{hysteresis:.1f}",
        },
    )


def _quiet(hass: Any, config: dict[str, Any]) -> None:
    """#1910: one warning when silent rows cannot be enforced.

    tvofi's chosen fallback (2026-09-30): normal operation with a warning.
    The plan is not capped for silent rows the optimizer cannot hold --
    planning for silence the pump will not deliver would buy the wrong
    hours. A switch is decided from the entity ID's domain alone, so one
    that has not reported yet (state ``unknown``) does not raise it:
    unknown is not off. A GCHV night-mode schedule that is only partly
    holdable (two windows, or days that differ) raises it too (#1913).
    """
    entity_id = EntryConfig.from_mapping(config).heat_pump_capacity_limited_entity
    set_issue(
        hass,
        ISSUE_QUIET,
        silent_unenforceable(config, hass.states.get),
        placeholders={"entity": entity_id or ""},
    )


def _dhw_floor(params: Any) -> float:
    disinfection = params.dhw_disinfection_temp
    floor = float(params.dhw_min_temp)
    return floor if disinfection is None else max(floor, float(disinfection))


def _dhw(hass: Any, config: dict[str, Any], params: Any, gated: Any = None) -> None:
    # "" for an unconfigured entity, which every reader below treats as unset.
    entity_id = EntryConfig.from_mapping(config).dhw_setpoint_entity or ""
    pump, unit = setpoint_and_unit(hass, entity_id) or (None, None)
    floor = _dhw_floor(params)
    # The floor on the entity's step, in its own unit (#1513): rounded UP
    # (#2805), as a floor written below itself is snapped down by the entity
    # and re-raises this notice, and never above the tank's hard maximum
    # (``dhw_hard_max_temp``, rounded down), the ceiling the arbiter bounds
    # its own write by: a Fix above it would be written back below the floor
    # at the arbiter's next step and the notice stand for good.
    on_step_c = quantise_setpoint_c(hass, entity_id, floor, rounding="up", hi_c=params.dhw_hard_max_temp)
    # A reading that is the pump-duty arbiter's own write is a step decision,
    # not a set-point below the disinfection floor: the arbiter writes the
    # cycle's temperature itself on a cycle step (``pump_arbiter.dhw_gated``).
    active = (
        bool(entity_id)
        and pump is not None
        and pump < on_step_c - MIXING_VALVE_WRITE_EPSILON
        and not (gated and gated(pump))
    )
    # ``target`` is degC for the notice's text; ``value`` is what Fix writes:
    # the floor on the step. An on-step floor at or below the ceiling is unchanged.
    data = None
    if active:
        value = round(temperature_from_c(on_step_c, unit), 6)
        data = {"entity_id": entity_id, "target": floor, "value": value}
    placeholders = {
        "pump": f"{pump:.1f}" if pump is not None else "",
        "target": f"{floor:.0f}",
        "entity": entity_id,
    }
    set_issue(
        hass, ISSUE_DHW, active, fixable=True, placeholders=placeholders, data=data
    )


def _space(hass: Any, config: dict[str, Any]) -> None:
    entity_id = EntryConfig.from_mapping(config).space_setpoint_entity
    if not entity_id:
        set_issue(hass, ISSUE_SPACE, False)
        return
    readable = read_setpoint(hass, entity_id) is not None
    set_issue(
        hass,
        ISSUE_SPACE,
        not readable,
        placeholders={"entity": entity_id},
    )
