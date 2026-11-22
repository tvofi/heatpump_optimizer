"""Suspend actuation while the pump reports a latched fault (R11-OWNER-FAULT-HOLD).

A pump whose fault alarm stays on is not taking commands as the plan means
them, and writing modes, set-points, an OFF, a frequency or a heat-curve
offset into it only adds traffic a person then has to undo. A fault alarm that
clears in well under a minute is the pump's own self-clearing kind, so the
hold starts only once the alarm has been on for :data:`FAULT_HOLD_AFTER`.

**Reading.** The fault slot (``CONF_HEAT_PUMP_FAULT_ENTITY``) is read with no
age limit (``inputs.UNBOUNDED``): a fault a push-only source reported once and
never again still reads on. Unavailable, unknown, not a flag and no slot are
unusable: an unusable reading never starts a hold and never ends one. The
60-minute horizon keeps governing the learner freeze in ``pump_signals``.

**Latch**, in memory per config entry: ``since`` is the alarm state's
``last_changed`` (bounded to now) at the first legible on, kept through a code
change and through unusable readings; only a legible off resets it. Optimizer
Off clears it, so the first consult after On re-seeds it from the entity's
``last_changed`` and an old fault holds again at once; a reload does the same.

**The one writer of the latch and of the ``pump_fault_hold`` repair**; every
writer that suspends itself consults :func:`holding` or :func:`gate`. The
repair is one domain-wide id, as ``pump_write_ignored`` is: it is cleared only
when no entry holds. The solver keeps planning; only actuation stops.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any
from weakref import WeakKeyDictionary

from homeassistant.util import dt as dt_util

from . import issues
from .const import CONF_HEAT_PUMP_FAULT_ENTITY, MODE_OFF
from .entry_config import EntryConfig
from .inputs import UNBOUNDED, InputReader

_LOGGER = logging.getLogger(__name__)

#: How long the alarm reads on before actuation stops: past the owner's
#: longest self-clearing fault (a few minutes), well short of a latched one.
FAULT_HOLD_AFTER = timedelta(minutes=10)

ISSUE = "pump_fault_hold"


@dataclass
class FaultLatch:
    """One entry's latch: since when the alarm reads on, and whether it holds."""

    since: datetime | None = None
    holding: bool = False
    entity: str | None = None
    hass: Any = None


_STATES: WeakKeyDictionary[Any, FaultLatch] = WeakKeyDictionary()


def _latch(entry: Any) -> FaultLatch:
    return _STATES.setdefault(entry, FaultLatch())


def holding(entry: Any, hass: Any, config: Any, *, off: bool, released: bool = False,
            now: datetime | None = None) -> bool:
    """Read the alarm, move the latch, raise or clear the repair on an edge.

    ``off`` (the optimizer is Off) and the ``fault_hold`` option off clear the
    latch and answer False; ``released`` (the entry is unloaded) answers False
    and raises nothing.
    """
    latch = _latch(entry)
    if released:
        return False
    cfg = EntryConfig.from_mapping(config)
    if off or not cfg.fault_hold or not cfg.heat_pump_fault_entity:
        latch.since = None
        return _move(latch, hass, False)
    now = dt_util.as_utc(now or dt_util.now())
    reading = InputReader(hass, dict(config)).read_bool(CONF_HEAT_PUMP_FAULT_ENTITY, max_age_minutes=UNBOUNDED)
    if reading.flag is False and reading.ok:
        latch.since = None
    elif reading.flag and reading.ok and latch.since is None:
        changed = getattr(hass.states.get(reading.entity_id), "last_changed", None)
        latch.since = min(dt_util.as_utc(changed), now) if changed is not None else now
    latch.entity, latch.hass = reading.entity_id, hass
    return _move(latch, hass, latch.since is not None and now - latch.since >= FAULT_HOLD_AFTER)


def _move(latch: FaultLatch, hass: Any, on: bool) -> bool:
    """Set the hold; raise the repair on its rising edge, clear it on its falling one."""
    if on and not latch.holding:
        since = latch.since.isoformat() if latch.since is not None else ""
        _LOGGER.warning("%s has reported a fault since %s: the optimizer stops actuating the pump "
                        "until it clears", latch.entity, since)
        issues.set_issue(hass, ISSUE, True, placeholders={"entity": str(latch.entity), "since": since})
    elif latch.holding and not on:
        latch.holding = False
        _clear(hass)
    latch.holding = on
    return on


def _clear(hass: Any) -> None:
    """Clear the domain-wide repair once no entry holds."""
    if not any(other.holding and other.hass is hass for other in list(_STATES.values())):
        issues.clear_issue(hass, ISSUE)


def consult(entry: Any, inp: Any, now: datetime | None = None) -> bool:
    """:func:`holding` for one pass's ``ArbiterInputs``."""
    return holding(entry, inp.hass, inp.config, off=inp.mode == MODE_OFF, released=inp.entry_released, now=now)


def held(entry: Any) -> bool:
    """The latch as last moved, with no read."""
    latch = _STATES.get(entry)
    return latch is not None and latch.holding


def gate(entry: Any, held_state: Any, inp: Any, value: bool | None) -> bool | None:
    """``value``, with an OFF turned into "leave" while the fault holds.

    An ON passes. A left OFF marks ``held_state.supply_held`` (the arbiter's
    record), so the step tick retries it each minute and it lands after the
    clear, and the cycle's cooling message is not printed for it.
    """
    if value is not False or not consult(entry, inp):
        return value
    held_state.supply_held = True
    _LOGGER.debug("Not switching the pump off: its fault alarm holds actuation")
    return None


def release(hass: Any, entry: Any) -> bool:
    """Unload: whether the entry was holding; drop its latch and, if last, the repair."""
    latch = _STATES.pop(entry, None)
    was = latch is not None and latch.holding
    if was:
        _clear(hass)
    return was


def diagnostics_view(entry: Any) -> dict[str, Any]:
    """The latch, for the diagnostics."""
    latch = _STATES.get(entry) or FaultLatch()
    return {"holding": latch.holding, "since": latch.since.isoformat() if latch.since else None,
            "hold_after_minutes": FAULT_HOLD_AFTER.total_seconds() / 60.0}
