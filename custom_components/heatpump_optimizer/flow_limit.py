"""The space water set-point's effective high limit, °C (R11-OWNER-FLOWCAP).

An entity's advertised maximum can sit above the highest value the pump
accepts. Two sources state the lower one: the controller's maximum set-point
sensor (``space_setpoint_high_limit_entity``) and the manual option
(``space_setpoint_high_limit_c``, tvofi 2026-11-22: "add an option to manually
configure the high-limit if there is no such sensor"). This module is the one
owner of how they combine; ``pump_arbiter`` reads the sources and caps every
space water write on the answer. Pure: no Home Assistant.
"""

from __future__ import annotations

from typing import NamedTuple

from .const import FLOW_HEAT_C_MAX, FLOW_LIMIT_C_MIN, finite_float


class HighLimit(NamedTuple):
    """The effective limit, °C or ``None``, and each source set aside
    (``sensor``, ``option``), which the caller logs."""

    limit_c: float | None
    dropped: tuple[str, ...]


def option_c(stored: object) -> float | None:
    """The manual option, °C, or ``None`` for one unset, not a number, or
    outside the :data:`FLOW_LIMIT_C_MIN` to :data:`FLOW_HEAT_C_MAX` the
    options flow offers."""
    value = finite_float(stored)
    return value if value is not None and FLOW_LIMIT_C_MIN <= value <= FLOW_HEAT_C_MAX else None


def high_limit(sensor_c: float | None, manual_c: float | None, lowest_c: float) -> HighLimit:
    """Combine the two sources into the one limit.

    Each source is judged alone first: one below ``lowest_c``, the lowest
    heating write (the gate plus its clearance, on the entity's step), leaves
    no heating value and is dropped; one equal to it is kept, the boundary
    ``_feedback_bounds`` always had. The gate is bounded up to the entity's
    minimum, so ``lowest_c`` sits above it, and a limit under the minimum is
    dropped here rather than written under it. ``sensor_c`` arrives with the
    crossed-pair rule already applied (``pump_arbiter._setpoint_limits_c``),
    so a dropped or unread sensor leaves the option in force. Of the kept
    sources the lower binds (orchestrator ruling, 2026-11-22): a sensor never
    lifts a limit the person typed.
    """
    kept: list[float] = []
    dropped: list[str] = []
    for name, value in (("sensor", sensor_c), ("option", manual_c)):
        if value is not None and value >= lowest_c:
            kept.append(value)
        elif value is not None:
            dropped.append(name)
    return HighLimit(min(kept) if kept else None, tuple(dropped))
