"""Frost hold: below a threshold outdoors, an idle step keeps the pump on.

The plan switches the power switch off on idle steps whatever the weather.
Off for hours near 0 °C, an air-source unit can run no defrost and cannot
protect itself. So while the latch below is active, an OFF the integration
would write to the power switch becomes a **frost hold**: the switch stays
on, or is switched on where it reads off. In duty control the arbiter also
writes the hold row (``pump_arbiter.desired`` with ``frost``): the space
set-point at the pump's own floor (``pump_arbiter._hold_floor_c``); elsewhere
nothing else is written and the pump runs on its own thermostat and curve.

**The reading** (:func:`outdoor_reading`) is the outdoor sensor's ``InputHealth``
verdict, never ``state.outdoor_temperature``, which the coordinator
back-fills from the forecast, the prior value or a default. With no sensor
configured, the forecast's value for now is the reading.

**The latch** (:func:`_active`): no reading (stale, unavailable, missing,
no sensor and no forecast) sets it; a reading below the threshold sets it;
only a reading at or above the threshold plus :data:`CLEAR_K` clears it. In
memory only: a restart starts unset, and the first pass sets it from the
reading. It is updated in synchronous code with no ``await`` between its
read and its write, so it is atomic on the event loop.

**The one writer** of the hold's ``ArbiterState`` fields: ``frost_holding``,
which ``pump_arbiter`` reads, and the :class:`FrostRecord` only this module reads. The coordinator's supply gate calls :func:`gate` last, after
``supply_hold.hold_supply``, so the minimum run and pause never delay or
carry a hold, and a held write (``None``) is never reinterpreted. The early
cut-off asks :func:`take_off` before it cuts.

**The learners** (:func:`freeze_reason`): a held pump runs on its own curve,
which the plan did not command, so an interval in which a held pump ran, or
any held interval without a power meter, is frozen.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable

from homeassistant.util import dt as dt_util

from .const import CONF_OUTDOOR_TEMP_ENTITY, MODE_OFF
from .entry_config import EntryConfig
from .pump_arbiter import ArbiterInputs, ArbiterState, ran_kw, state_for, supply_switch
from .supply_hold import freeze_span

_LOGGER = logging.getLogger(__name__)

#: Kelvin above the threshold a reading must reach to clear the latch, so a
#: reading on the threshold does not switch the pump on and off each pass.
CLEAR_K = 1.0
#: The ``_learning_frozen`` reason for an interval a held pump may have run.
FREEZE_FROST = "frost_hold"
#: Why the hold is on: a reading below the threshold, or none to judge by.
CAUSE_COLD = "frost_hold"
CAUSE_NO_READING = "frost_hold_no_reading"


@dataclass
class FrostRecord:
    """The hold's own record on ``ArbiterState.frost``, in memory only."""

    #: The latch (:func:`_active`); ``None`` unset or opted out.
    latched: bool | None = None
    #: Until when (UTC) the learners freeze for a held run (:func:`_note_run`).
    ran_until: datetime | None = None


def _record(held: ArbiterState) -> FrostRecord:
    """``held``'s :class:`FrostRecord`, made on first use."""
    if held.frost is None:
        held.frost = FrostRecord()
    return held.frost


def outdoor_reading(health: Any, forecast_c: Callable[[], float | None], config: Any) -> float | None:
    """The outdoor temperature the latch judges, °C, or ``None`` for none.

    Where ``config`` names an outdoor sensor, its verdict in ``health``
    (``inputs.InputHealth``) is the reading, and a stale or missing one is
    ``None``, never the forecast standing in for it. With no sensor,
    ``forecast_c()`` is the forecast's value for now.
    """
    if not EntryConfig.from_mapping(config).outdoor_temp_entity:
        return forecast_c()
    got = None if health is None else health.readings.get(CONF_OUTDOOR_TEMP_ENTITY)
    return got.value if got is not None and got.ok else None


def _active(held: ArbiterState, inp: ArbiterInputs) -> bool:
    """Update the latch from this pass's reading; whether a hold applies.

    Opted out, it is never active, whatever the reading.
    """
    cfg, rec = EntryConfig.from_mapping(inp.config), _record(held)
    if not cfg.frost_hold:
        rec.latched = None
        return False
    out = inp.outdoor_c
    if out is None or out < cfg.frost_hold_below_c:
        rec.latched = True
    elif out >= cfg.frost_hold_below_c + CLEAR_K:
        rec.latched = False
    return bool(rec.latched)


def gate(held: ArbiterState, inputs: Callable[[], ArbiterInputs], value: bool | None,
         now: datetime | None = None) -> bool | None:
    """``value``, or the hold's write in place of an OFF while the latch is active.

    ``True`` ends a hold and passes; ``None`` (nothing to write, or a write
    ``supply_hold`` held back) passes unchanged. ``False`` under an active
    latch is held: ``None`` leaves a running switch alone, logged as the
    hold, and ``True`` switches one that reads off back on. ``inputs`` is
    the coordinator's ``arbiter_inputs`` builder, called only for an OFF.
    """
    if value is None:
        return None
    if value:
        held.frost_holding = False
        return True
    inp = inputs()
    held.frost_holding = _active(held, inp)
    if not held.frost_holding:
        return False
    _note_run(held, inp, now)
    switch = supply_switch(inp)
    if getattr(switch, "state", None) == "off":
        return True
    if switch is not None:
        _LOGGER.debug("Not switching %s off: frost hold", EntryConfig.from_mapping(inp.config).heat_pump_switch_entity)
    return None


def take_off(held: ArbiterState, inp: ArbiterInputs, now: datetime | None = None) -> bool:
    """Whether the early cut-off must not switch the pump off: a hold applies.

    On ``True`` the hold takes over from the cut: the arbiter's next pass
    writes the hold row and the switch stays on.
    """
    if not _active(held, inp):
        return False
    held.frost_holding = True
    _note_run(held, inp, now)
    return True


def holding(held: ArbiterState, inp: ArbiterInputs) -> bool:
    """Whether a hold is in force for this pass; never while the optimizer is Off."""
    return held.frost_holding and inp.mode != MODE_OFF


def _note_run(held: ArbiterState, inp: ArbiterInputs, now: datetime | None) -> None:
    """Freeze the learners for two intervals where the held pump ran, or may have.

    A run is the meter's (``pump_arbiter.ran_kw``); with no reading the pump
    may have run, which is the fail-closed side.
    """
    if not holding(held, inp):
        return
    power = inp.measured_power_kw
    if power is None or float(power) >= ran_kw(inp):
        _record(held).ran_until = dt_util.as_utc(now or dt_util.now()) + freeze_span(inp.config)


def freeze_reason(coord: Any, now: datetime | None = None) -> str | None:
    """:data:`FREEZE_FROST` while a learner's interval may hold a held run, else ``None``."""
    return _freeze(state_for(coord), lambda: coord.arbiter_inputs(), now)


def _freeze(held: ArbiterState, inputs: Callable[[], ArbiterInputs], now: datetime | None) -> str | None:
    """:func:`freeze_reason` on the record; ``inputs`` is built only while a hold is
    on, to note a run seen now."""
    now = dt_util.as_utc(now or dt_util.now())
    if held.frost_holding:
        _note_run(held, inputs(), now)
    until = _record(held).ran_until
    return FREEZE_FROST if until is not None and now < until else None


def diagnostics_view(held: ArbiterState, inp: ArbiterInputs) -> dict[str, Any]:
    """The latch, the hold, its cause, the threshold and the reading."""
    cfg, rec = EntryConfig.from_mapping(inp.config), _record(held)
    on = holding(held, inp)
    cause = (CAUSE_NO_READING if inp.outdoor_c is None else CAUSE_COLD) if on else None
    return {
        "enabled": cfg.frost_hold,
        "below_c": cfg.frost_hold_below_c,
        "reading_c": inp.outdoor_c,
        "latched": rec.latched,
        "holding": on,
        "cause": cause,
        "learners_frozen_until": None if rec.ran_until is None else rec.ran_until.isoformat(),
    }
