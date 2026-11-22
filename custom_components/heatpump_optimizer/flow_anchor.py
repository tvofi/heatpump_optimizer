"""The water a heating step's flow floor is anchored on, and its settle after a hot-water leg.

R11-OWNER-STEP-KICK (#3860; design ``design/R11-OWNER-STEP-KICK`` 09fecb1b,
option D). The arbiter's flow floor is the measured inlet plus a lift
(``thermal_model.modulation_floor_flow_c``), the inlet being the first fresh
rung of :data:`FLOW_INLET_KEYS`. Right after the pump swaps from hot water to
heating, the pump-loop return reads the tank coil's water. Inlet plus lift then
lands at or above the heating ceiling, and the step's first writes are the
ceiling, falling minute by minute with the probe. For the settle window after
such a swap the floor is anchored on the space loop's own water instead
(:func:`settled_inlet_c`), never above today's anchor.

A leaf: no Home Assistant import and no entity read; the arbiter reads the
rungs and hands the readings in.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .drift import utc_elapsed_seconds

from .const import (
    CONF_BUFFER_TANK_TEMP_ENTITY,
    CONF_FLOOR_RETURN_TEMP_ENTITY,
    CONF_HEAT_PUMP_RETURN_TEMP_ENTITY,
    CONF_VALVE_OUTLET_TEMP_ENTITY,
)

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
#: The rung a return target is not anchored on: the valve outlet is
#: house-side supply, and supply plus a lift written as a return target
#: over-commands by about the spread. A return target reads the other rungs
#: in the same precedence; none read leaves the no-inlet floor, the hold in
#: return terms.
RETURN_SKIPPED_RUNG = CONF_VALVE_OUTLET_TEMP_ENTITY


def inlet_rungs(return_target: bool, past_loop: bool = False) -> tuple[str, ...]:
    """The rungs read for the inlet, best first: without :data:`RETURN_SKIPPED_RUNG`
    for a return target, and without the pump-loop return when ``past_loop`` (the
    space-side water a settle falls back to, :func:`settled_inlet_c`)."""
    skip = {RETURN_SKIPPED_RUNG} if return_target else set()
    if past_loop:
        skip.add(CONF_HEAT_PUMP_RETURN_TEMP_ENTITY)
    return tuple(key for key in FLOW_INLET_KEYS if key not in skip)


@dataclass(frozen=True)
class Settle:
    """A pump's swap record as one pass reads it.

    ``swap_at``: when a pass last served heating with hot water served less
    than the settle span before (``None``: no swap seen since the start).
    ``space_inlet_c``: the inlet read on the last heating pass outside a
    settle with the compressor running, or ``None`` when there is none young
    enough to stand for the space loop's water.
    """

    swap_at: datetime | None
    space_inlet_c: float | None


def settled_inlet_c(live_c: float | None, settle: Settle, next_rung_c: float | None, now: datetime,
                    span_s: float) -> float | None:
    """The inlet a heating floor is anchored on at ``now``.

    Outside ``[swap_at, swap_at + span_s)`` it is ``live_c``, today's. Inside
    it is the space loop's water: the remembered space inlet, else
    ``next_rung_c`` (the first fresh rung past the pump-loop return), else
    ``None``, the rated hold. The caller keeps the lower of the floor this
    gives and today's (``pump_arbiter._map_inputs``), so a write is never
    above today's (invariant I1).
    """
    if not _within(now, settle.swap_at, span_s):
        return live_c
    return settle.space_inlet_c if settle.space_inlet_c is not None else next_rung_c


def _within(now: datetime, then: datetime | None, span_s: float) -> bool:
    """Whether ``then`` is under ``span_s`` before ``now``; a stamp ahead of now is not (its age is unknowable)."""
    return then is not None and 0.0 <= utc_elapsed_seconds(now, then) < span_s


@dataclass
class Swap:
    """One pump's swap record, the only one (design section 3, the orchestrator's option (a)).

    ``served``: the duty the last commanding pass served and when. ``swap_at``:
    the last pass serving heating (``space`` or ``both``) with hot water served
    under the settle span before, a served-duty change, so a gate transport
    that swaps with no mode write is seen too. ``space_inlet``: the inlet of
    the last heating pass outside a settle with the compressor running. Kept in
    memory only: a restart, like a gap longer than the span, sees no swap.
    """

    served: tuple[str | None, datetime] | None = None
    swap_at: datetime | None = None
    space_inlet: tuple[float, datetime] | None = None

    def note(self, served: str | None, now: datetime, inlet_c: float | None, running: bool, span_s: float) -> None:
        """A commanding pass serves ``served`` at ``now``."""
        heating = served in ("space", "both")
        if heating and self.served is not None and self.served[0] == "dhw" and _within(now, self.served[1], span_s):
            self.swap_at = now
        self.served = (served, now)
        if heating and running and inlet_c is not None and not _within(now, self.swap_at, span_s):
            self.space_inlet = (inlet_c, now)

    def settle(self, now: datetime, inlet_age_s: float) -> Settle:
        """The record as a pass reads it; the space inlet stands for the loop's water while younger than ``inlet_age_s``."""
        inlet = self.space_inlet
        return Settle(self.swap_at, inlet[0] if inlet is not None and _within(now, inlet[1], inlet_age_s) else None)
