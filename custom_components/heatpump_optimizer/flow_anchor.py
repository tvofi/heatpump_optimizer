"""The space flow floor's inlet across a hot-water -> space swap (R11-OWNER-STEP-KICK).

A heating step's flow set-point slides from the ceiling down to a floor one
lift above the water the pump heats (``thermal_model.modulation_floor_flow_c``),
read from the first fresh rung of :data:`FLOW_INLET_KEYS`. Right after a
hot-water leg the first rung, the pump-loop return, reads the tank coil's
water, so the floor lands at or above the ceiling and the first space writes
ask for the pump's maximum lift for the minutes the return takes to cool
(tvofi, 2026-11-22: the step-start kick).

This module owns the one rule that stands that off: for a settle span after a
pass that serves space right after one that served hot water (a *swap*), the
floor is anchored on the space loop's own water -- the inlet remembered from
the last running space pass, else the first rung past the pump-loop return.
The arbiter keeps the lower of that floor and today's, so a write never rises.
A settle span of zero is today's behaviour.

The swap keys on the duty the arbiter SERVED, not a landed mode write: a gate
transport swaps duties with no mode write. The record is not persisted, so a
restart never fires a swap late; neither does any gap between the two serves
longer than the settle span (a fault hold, a switch-off, an idle pass).

Pure: no ``homeassistant`` import; the arbiter reads the entities and passes
values in.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from .const import (
    CONF_BUFFER_TANK_TEMP_ENTITY,
    CONF_FLOOR_RETURN_TEMP_ENTITY,
    CONF_HEAT_PUMP_RETURN_TEMP_ENTITY,
    CONF_VALVE_OUTLET_TEMP_ENTITY,
)
from .drift import utc_elapsed_seconds

#: The sensors that measure the water the pump heats, best first: the
#: set-point is a power command (tvofi, 2026-10-19), so its floor sits a
#: lift above that water. One precedence for every plant, because what a
#: slot measures follows the plant (tvofi asked for every combination):
#:
#: * pump-loop return -- the condenser's own inlet on any plant;
#: * buffer tank -- with a buffer, with or without a mixing valve, the
#:   pump heats the tank;
#: * floor return -- on a direct-to-radiator plant the pump's inlet; behind
#:   a buffer, the mixed circuit's return, below the tank, so the floor
#:   errs toward less power;
#: * valve outlet -- house-side supply, at or above the floor return and,
#:   on a wood topology, mixed with the wood tank, so the last rung.
#:
#: The pump's outgoing temperature is not a rung: it is the set-point's own
#: controlled variable, and a floor anchored on it would chase itself. No
#: rung read leaves the rated ``pump_arbiter.FLOW_HOLD_C``, today's default.
FLOW_INLET_KEYS = (
    CONF_HEAT_PUMP_RETURN_TEMP_ENTITY,
    CONF_BUFFER_TANK_TEMP_ENTITY,
    CONF_FLOOR_RETURN_TEMP_ENTITY,
    CONF_VALVE_OUTLET_TEMP_ENTITY,
)
#: The rungs past the pump-loop return: the space side's own water, which a
#: hot-water leg does not pass through, so the settle's fallback anchor.
SPACE_SIDE_KEYS = FLOW_INLET_KEYS[1:]
#: The rung a return target is not anchored on: the valve outlet is
#: house-side supply, and supply plus a lift written as a return target
#: over-commands by about the spread. A return target reads the other rungs
#: in the same precedence; none read leaves the no-inlet floor, the hold in
#: return terms.
RETURN_SKIPPED_RUNG = CONF_VALVE_OUTLET_TEMP_ENTITY

#: The served duties that heat the space loop.
SPACE_DUTIES = ("space", "both")


def _within(start: datetime | None, now: datetime, span: timedelta) -> bool:
    """``now`` lies in ``[start, start + span)``; a ``start`` ahead of ``now``
    is an unknowable age, never 0, so it is outside (#775)."""
    if start is None:
        return False
    age = utc_elapsed_seconds(now, start)
    return 0.0 <= age < span.total_seconds()


@dataclass(frozen=True)
class Served:
    """The arbiter's record of the duty it last served, and what a swap reads.

    ``duty``/``at``: the last pass that reached the command, and when.
    ``swap_at``: the last hot-water -> space swap. ``space_inlet``: the inlet
    (°C, when) of the last space pass with the compressor running outside a
    settle span, the space loop's own water.
    """

    duty: str | None
    at: datetime
    swap_at: datetime | None = None
    space_inlet: tuple[float, datetime] | None = None

    def anchor_c(
        self, live_c: float | None, side_c: float | None, now: datetime,
        settle: timedelta, max_age: timedelta,
    ) -> float | None:
        """The inlet this pass's floor is anchored on (:func:`settled_inlet_c`).

        The remembered space inlet counts while younger than ``max_age``;
        ``side_c`` is the first fresh rung of :data:`SPACE_SIDE_KEYS`.
        """
        space = self.space_inlet
        space_c = space[0] if space is not None and _within(space[1], now, max_age) else None
        return settled_inlet_c(live_c, space_c, side_c, self.swap_at, now, settle)


def note(
    prev: Served | None, duty: str | None, now: datetime, settle: timedelta,
    inlet_c: float | None, running: bool,
) -> Served:
    """The record after a pass that serves ``duty`` at ``now``.

    A swap is a pass serving space (:data:`SPACE_DUTIES`) whose previous pass
    served hot water less than ``settle`` before. A running space-only pass
    outside a settle span remembers ``inlet_c`` as the space loop's water.
    """
    swap_at = prev.swap_at if prev is not None else None
    if duty in SPACE_DUTIES and prev is not None and prev.duty == "dhw" and _within(prev.at, now, settle):
        swap_at = now
    space = prev.space_inlet if prev is not None else None
    if duty == "space" and running and inlet_c is not None and not _within(swap_at, now, settle):
        space = (float(inlet_c), now)
    return Served(duty, now, swap_at, space)


def settled_inlet_c(
    live_c: float | None, space_c: float | None, side_c: float | None,
    swap_at: datetime | None, now: datetime, settle: timedelta,
) -> float | None:
    """The inlet the modulation floor is anchored on, °C, or ``None``.

    ``live_c`` outside ``[swap_at, swap_at + settle)``, and wherever the live
    inlet is unread. Inside it, the space loop's own water: ``space_c``, else
    ``side_c``; with neither, ``None``, which the arbiter's floor reads as its
    rated hold. The arbiter's floor is the lower of this anchor's and the live
    inlet's (``pump_arbiter._map_inputs``): the floor is monotone in its inlet,
    so the lower floor is the one ``min(live_c, anchor)`` would give, and the
    hold the ``None`` anchor gives never raises a cool live inlet's.
    """
    if live_c is None or not _within(swap_at, now, settle):
        return live_c
    return space_c if space_c is not None else side_c
