"""The compressor's running signal: one listener per pump, its edges, and who hears them.

Design: R10-START-COUNTER-EDGES, part D of Bankaifan's outside pull request
3420. The class of one reading is ``wear.compressor_running``'s and its
debounced edges ``wear.EdgeTracker``'s; this module is the Home Assistant glue
that owns them for one coordinator, in every duty mode, from the coordinator's
construction (:func:`attach`) to its release (:func:`detach`). It never
triggers a pass and writes nothing.

**Source** (:func:`source`): the actual-frequency sensor where one is
configured (never the number entity, a set-point register that echoes the last
write), else the meter against ``thermal_model.on_threshold_kw``. On the meter
a reading the coordinator's ``element`` callable calls the immersion element's
is no signal: a resistive draw is not the compressor (#11).

**Edges.** Each state event of the signal entity is one reading
(:func:`note`); the coordinator re-reads once per refresh too, since the
element's latch and the commanded draw change there without a meter event
(:func:`refresh`), and each subscriber's tick then hears whether the class
reads settled running: the start counter holds a meter's rise for them. A
change pending at a reading is confirmed by a timer at
``wear.EDGE_DEBOUNCE_S`` (:func:`confirm`), because a sensor whose state holds
fires no event that could confirm it. Each confirmed edge is handed to every
subscriber (:func:`subscribe`): the start counter always, the duty-switch
learner while the arbiter listens.

**Running now** (:func:`running_now`): ``True`` or ``False`` for a settled
class with no change pending; ``None`` before the first confirmed edge, with no
source configured, while the entity is unavailable or non-numeric, on the meter
while the element rule holds, and while a change is pending.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable
from weakref import WeakKeyDictionary

from homeassistant.core import callback
from homeassistant.helpers.event import async_call_later, async_track_state_change_event
from homeassistant.util import dt as dt_util

from . import wear
from .drift import utc_elapsed_seconds, utc_shift
from .entry_config import EntryConfig
from .freq_control import resolve_reading
from .inputs import state_power_kw
from .thermal_model import on_threshold_kw

#: ``() -> (frequency Hz, power kW, threshold kW, by frequency)``, the
#: arguments of ``wear.compressor_running``.
Reader = Callable[[], tuple[float | None, float | None, float | None, bool]]
#: A confirmed edge: (its first changed reading's time, the new class).
Edge = tuple[datetime, bool | None]


@dataclass
class Signal:
    """One pump's running signal: the tracker, the listener, the timer, the subscribers."""

    hass: Any = None
    tracker: wear.EdgeTracker = field(default_factory=wear.EdgeTracker)
    reader: Reader | None = None
    unsub: Callable[[], None] | None = None
    #: (the pending change the timer confirms, its cancel), while one is armed.
    timer: tuple[Any, Callable[[], None]] | None = None
    subscribers: list[Callable[[Edge], None]] = field(default_factory=list)
    #: Who hears each refresh's read: ``True`` for a settled running class.
    ticks: list[Callable[[bool], None]] = field(default_factory=list)


_SIGNALS: WeakKeyDictionary[Any, Signal] = WeakKeyDictionary()


def signal_for(coord: Any) -> Signal:
    """The pump's signal, made on first use; one config entry is one pump."""
    return _SIGNALS.get(coord) or _SIGNALS.setdefault(coord, Signal(coord.hass))


def source(
    hass: Any, cfg: EntryConfig, params: Callable[[], Any], element: Callable[[float], bool],
) -> tuple[str | None, Reader]:
    """The entity whose changes say the compressor started or stopped, and its reader.

    ``params`` returns the live thermal parameters the meter's threshold is
    read from; ``element`` says whether a meter reading, kW, is the immersion
    element's. The frequency source reads neither.
    """
    sensor, meter, states = cfg.compressor_freq_sensor, cfg.heat_pump_power_entity, hass.states

    def reader() -> tuple[float | None, float | None, float | None, bool]:
        if sensor:
            return resolve_reading(None, sensor, states.get, 0.0, 0.0)[0], None, None, True
        kw = state_power_kw(states.get(meter), "clamp")
        if kw is not None and element(kw):
            return None, None, None, False
        return None, kw, on_threshold_kw(params()), False

    return sensor or meter, reader


def attach(sig: Signal, entity: str | None, reader: Reader) -> None:
    """Listen on ``entity`` and read it once; idempotent, and a no-op without one."""
    if sig.unsub is not None or not entity:
        return
    sig.reader = reader

    @callback
    def _changed(_event: Any) -> None:
        note(sig, dt_util.now())

    sig.unsub = async_track_state_change_event(sig.hass, [entity], _changed)
    note(sig, dt_util.now())


def detach(sig: Signal) -> None:
    """Stop listening, cancel the timer and drop the subscribers and ticks; idempotent.

    The subscribers, the ticks and the reader close over the coordinator, and the
    table's value would otherwise keep its own weak key alive: a released
    coordinator is collected only once they are gone. The settled class is kept.
    """
    unsub, timer, sig.unsub, sig.timer, sig.reader = sig.unsub, sig.timer, None, None, None
    sig.subscribers.clear()
    sig.ticks.clear()
    if unsub is not None:
        unsub()
    if timer is not None:
        timer[1]()


def subscribe(sig: Signal, hear: Callable[[Edge], None], tick: Callable[[bool], None] | None = None) -> None:
    """Hand ``hear`` every confirmed edge from now on, and ``tick`` each refresh's read; idempotent."""
    if hear not in sig.subscribers:
        sig.subscribers.append(hear)
    if tick is not None and tick not in sig.ticks:
        sig.ticks.append(tick)


def unsubscribe(sig: Signal, hear: Callable[[Edge], None]) -> None:
    if hear in sig.subscribers:
        sig.subscribers.remove(hear)


def note(sig: Signal, when: datetime) -> None:
    """One reading of the signal; a no-op before the attach and after the detach."""
    if sig.reader is not None:
        _publish(sig, sig.tracker.note(when, wear.compressor_running(*sig.reader())))


def refresh(sig: Signal, when: datetime) -> None:
    """The coordinator's per-refresh re-read; then each tick hears whether the class reads settled running."""
    note(sig, when)
    read = running_now(sig) is True
    for tick in list(sig.ticks):
        tick(read)


def confirm(sig: Signal, when: datetime) -> None:
    """Settle a change that has held the debounce by ``when``."""
    _publish(sig, sig.tracker.confirm(when))


def running_now(sig: Signal) -> bool | None:
    """The settled class with no change pending, else ``None``."""
    return sig.tracker.settled if sig.tracker.pending is None else None


def _publish(sig: Signal, edge: Edge | None) -> None:
    if edge is not None:
        for hear in list(sig.subscribers):
            hear(edge)
    _arm_timer(sig)


def _arm_timer(sig: Signal) -> None:
    """Hold one timer for the pending change, none without one; a held one is kept."""
    pending = sig.tracker.pending if sig.unsub is not None else None
    if sig.timer is not None and sig.timer[0] == pending:
        return
    if sig.timer is not None:
        sig.timer[1]()
        sig.timer = None
    if pending is None:
        return
    due = utc_shift(pending[1], timedelta(seconds=wear.EDGE_DEBOUNCE_S))

    @callback
    def _due(_now: Any) -> None:
        sig.timer = None
        confirm(sig, due)

    delay = max(0.0, wear.EDGE_DEBOUNCE_S - utc_elapsed_seconds(dt_util.now(), pending[1]))
    sig.timer = (pending, async_call_later(sig.hass, delay, _due))
