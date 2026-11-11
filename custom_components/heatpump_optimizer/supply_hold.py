"""The supply switch's minimum run and minimum pause.

The plan switches the supply at its 15-minute step boundaries, but a
re-solve, a cycle, a restart or a late write can land inside a step, and the
supply switch bypasses the compressor's own interlocks. So the one gate the
cycle and the step tick write through (``coordinator._write_supply``) holds a
write back that would

* end a run under :data:`MIN_RUN`. A run counts from the later of this
  gate's own on write and this record's first gated write: a run found on at
  a restart or a reload is held as one that started then;
* end a pause under :data:`MIN_PAUSE`, counted from this gate's own off write;
  a stop the early cut-off wrote keeps ``early_cutoff.allow_on``'s rule;
* start a run the plan ends under :data:`MIN_RUN`: an on write inside a step
  whose next step is planned off.

A held write sets ``ArbiterState.supply_held``, and ``pump_arbiter.
supply_tick`` retries it every minute with the step's own command, so the
write lands once its minimum has passed. Both minimums sit below the plan's
step, so the plan's own boundaries never meet them, and a plan holds no run
or pause shorter than them. A non-plan mode and a live boost pass unchanged,
and so does every off write the cooling or blocked mode already skips.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from homeassistant.util import dt as dt_util

from .boost import CHANNEL_DHW, CHANNEL_SPACE
from .const import MODE_AUTO, MODE_ECONOMY
from .entry_config import EntryConfig
from .plan_step import PLAN_STEP_MINUTES, plan_step_start
from .pump_arbiter import ArbiterInputs, ArbiterState, step_supply

#: The early cut-off's own minimums too (``early_cutoff.MIN_ON``/``MIN_OFF``).
MIN_RUN = timedelta(minutes=10)
MIN_PAUSE = timedelta(minutes=10)


@dataclass
class _Hold:
    #: This record's first gated write, and the gate's last on and off writes.
    born: datetime | None = None
    on_at: datetime | None = None
    off_at: datetime | None = None


def hold_supply(held: ArbiterState, inp: ArbiterInputs, boosts: Any, value: bool | None,
                now: datetime | None = None) -> bool | None:
    """``value``, or ``None`` while this module's rules hold the write back."""
    now = dt_util.as_utc(now or dt_util.now())
    rec = held.hold = held.hold or _Hold()
    rec.born, held.supply_held = rec.born or now, False
    switch = inp.hass.states.get(EntryConfig.from_mapping(inp.config).heat_pump_switch_entity or "")
    reads = getattr(switch, "state", None)
    if (value is None or reads not in ("on", "off") or (reads == "on") is value
            or inp.mode not in (MODE_AUTO, MODE_ECONOMY)
            or any(boosts.active(c, now) for c in (CHANNEL_SPACE, CHANNEL_DHW))):
        return value
    held.supply_held = _start_held(rec, inp, boosts, now) if value else _stop_held(rec, held, now)
    return None if held.supply_held else value


def _start_held(rec: _Hold, inp: ArbiterInputs, boosts: Any, now: datetime) -> bool:
    """Inside the gate's own pause, or a run the plan ends under :data:`MIN_RUN`."""
    nxt = plan_step_start(now) + timedelta(minutes=PLAN_STEP_MINUTES)
    wait = (rec.off_at is not None and now - rec.off_at < MIN_PAUSE) or (
        nxt - now < MIN_RUN and step_supply(inp, boosts, nxt) is False)
    rec.on_at = rec.on_at if wait else now
    return wait


def _stop_held(rec: _Hold, held: ArbiterState, now: datetime) -> bool:
    """A run under :data:`MIN_RUN`; a stop let through starts the gate's pause."""
    starts = (rec.born, rec.on_at)
    short = now - max(s for s in starts if s and s <= now) < MIN_RUN
    rec.off_at = rec.off_at if short else now
    return short
