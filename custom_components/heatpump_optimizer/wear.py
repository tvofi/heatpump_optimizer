"""Compressor start counting and the wear price it implies (T6 #55).

Every heat pump datasheet rates the compressor in starts, yet nothing in the
integration counted them — the cycling penalty priced an *assumed* cost. A
start is a confirmed edge of the running class, ``compressor_running`` over
one reading debounced by :class:`EdgeTracker`, to running from a last known
class of stopped (R10-START-COUNTER-EDGES, part D of Bankaifan's outside
pull request 3420). The edges come from ``running_signal``, the one owner of
the signal, as each reading lands rather than once per refresh, so a stop
and restart between two refreshes is a start. The meter source reads no
signal while the immersion element runs (#11): a resistive spike is exactly
the shape a naive edge detector would call a compressor start.

The money side is deliberately simple: one start costs
``replacement_cost / rated_starts``. With the default replacement cost of 0
the counter is pure observation; pricing it is the user's call, and feeding
the price back into the optimizer's cycling penalty is a separate opt-in
(``wear_autotune_enabled``), because that is the one piece that changes plans.

Kept free of Home Assistant imports so it can be unit-tested directly.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import numpy as np

from .drift import utc_elapsed_seconds

#: Months of per-month counts kept, matching the ledger's horizon.
KEEP_MONTHS = 24
#: Reported compressor frequency, Hz, at or above which it runs. A stopped
#: inverter reports 0 and a running one its modulation floor, tens of Hz; 1 Hz
#: is the line ``freq_control.FrequencyMap.observe`` already refuses a sample
#: under. A constant, not a measured threshold.
RUNNING_FLOOR_HZ = 1.0
#: Seconds a changed running class must hold before it is an edge: longer
#: than a one-frame zero or a meter's dip, shorter than any stop worth
#: counting. A constant, not a measured threshold.
EDGE_DEBOUNCE_S = 30.0
#: Refreshes that must read the meter's signal settled running before a rise
#: on it is a start (S7, owner ruling D1): the first can fall inside an
#: averaging meter's partial report, the second is a refresh period later,
#: past any report period up to that interval.
HOLD_REFRESHES = 2


def compressor_running(
    frequency_hz: float | None, power_kw: float | None, threshold_kw: float | None,
    by_frequency: bool,
) -> bool | None:
    """Whether the compressor runs, by one reading; ``None`` is no signal.

    ``by_frequency`` names the install's source: the actual-frequency sensor
    where one is configured, at :data:`RUNNING_FLOOR_HZ`; else the meter at
    ``threshold_kw`` (``thermal_model.on_threshold_kw``). A reading that is
    absent or not finite is no signal, never "stopped", and the source is
    never mixed: a meter standing in for a silent frequency sensor would
    flip the class at every outage.
    """
    reading, floor = (frequency_hz, RUNNING_FLOOR_HZ) if by_frequency else (power_kw, threshold_kw)
    if reading is None or floor is None or not (np.isfinite(reading) and np.isfinite(floor)):
        return None
    return bool(float(reading) >= float(floor))


@dataclass
class EdgeTracker:
    """Debounced edges of the running class (``True``, ``False``, ``None``).

    An event of the settled class costs one compare and clears a pending
    change, so a one-frame zero is no edge. A changed class is pending from
    its first event and becomes the settled class once it held
    :data:`EDGE_DEBOUNCE_S`, confirmed by a later event of the same class
    (:meth:`note`) or by the caller's own clock (:meth:`confirm`): a final
    zero no event follows is still confirmed. The edge carries the first
    changed event's time. A time-spacing throttle would drop exactly that
    final event.
    """

    settled: bool | None = None
    #: (the changed class, when it was first seen), until confirmed or undone.
    pending: tuple[bool | None, datetime] | None = None

    def note(self, when: datetime, running: bool | None) -> tuple[datetime, bool | None] | None:
        """Fold one reading; the confirmed edge ``(since, class)`` or ``None``."""
        if running == self.settled:
            self.pending = None
            return None
        if self.pending is None or self.pending[0] != running:
            self.pending = (running, when)
        return self.confirm(when)

    def confirm(self, when: datetime) -> tuple[datetime, bool | None] | None:
        """Settle a pending change that has held the debounce by ``when``."""
        pending = self.pending
        if pending is None or utc_elapsed_seconds(when, pending[1]) < EDGE_DEBOUNCE_S:
            return None
        self.settled, self.pending = pending[0], None
        return pending[1], pending[0]


@dataclass
class RiseHold:
    """The meter source's rises, held until :data:`HOLD_REFRESHES` refreshes read them running.

    S7 (owner ruling D1): a meter reporting its window's average gives an
    element cut-in, compressor off, one partial report between the
    on-threshold and the over level. It holds one report period, at least
    :data:`EDGE_DEBOUNCE_S`, so it is a confirmed rise before over arrives,
    and over reads no class. A held rise is passed on at its own time once
    the refreshes read the class settled running; a no-class edge drops it. A
    stop passes it on with the stop when it rose from a stop (a short run),
    and drops it when it rose from no class: an element's falling average as
    it cuts out.
    """

    #: The class of the last edge heard.
    last: bool | None = None
    #: (the rise's time, whether it rose from a stop, the refreshes that read
    #: it running), while one is held.
    held: tuple[datetime, bool, int] | None = None

    def admit(self, since: datetime, running: bool | None) -> list[tuple[datetime, bool | None]]:
        """Hear one confirmed edge; the edges to fold now, in order."""
        held, rose_from, self.held, self.last = self.held, self.last, None, running
        if running is True:
            self.held = (since, rose_from is False, 0)
            return []
        if held is not None and held[1] and running is False:  # a short run
            return [(held[0], True), (since, running)]
        return [(since, running)]

    def refresh(self, running: bool) -> list[tuple[datetime, bool | None]]:
        """One refresh, ``running`` its read of the settled class; the held rise, once released."""
        if self.held is None or not running:
            return []
        since, from_stop, seen = self.held
        seen += 1
        if seen < HOLD_REFRESHES:
            self.held = (since, from_stop, seen)
            return []
        self.held = None
        return [(since, True)]


@dataclass
class StartCounter:
    """Compressor starts, folded from the running signal's confirmed edges.

    A counter built bare is **unrestored**: it folds no edge but queues it in
    order, because the listener is armed before the ledger store is read.
    :meth:`restore` reads the stored payload and replays the queue against
    the stored ``running``, so an edge before the read is neither lost nor
    counted twice.
    """

    #: The last known running class: a ``None`` edge (no signal) leaves it,
    #: so an outage, or the element on the meter, never books a start.
    running: bool = False
    lifetime: int = 0
    months: dict[str, int] = field(default_factory=dict)
    #: Edges seen before :meth:`restore`; ``None`` once restored.
    queued: list[tuple[datetime, bool | None]] | None = field(default_factory=list)
    #: The meter source's :class:`RiseHold`; ``None`` on the frequency source.
    hold: RiseHold | None = None

    def hear(self, since: datetime, running: bool | None) -> list[datetime]:
        """Fold one confirmed edge of the signal through the hold; the starts counted."""
        edges = [(since, running)] if self.hold is None else self.hold.admit(since, running)
        return [at for edge in edges for at in self.fold(*edge)]

    def refresh(self, running: bool) -> list[datetime]:
        """One refresh's read of the settled class; the start a held rise it releases counted."""
        edges = [] if self.hold is None else self.hold.refresh(running)
        return [at for edge in edges for at in self.fold(*edge)]

    def fold(self, since: datetime, running: bool | None) -> list[datetime]:
        """Fold one confirmed edge; the start it counted, at ``since``, or none."""
        if self.queued is not None:
            self.queued.append((since, running))
            return []
        if running is None:
            return []
        started, self.running = running and not self.running, running
        if not started:
            return []
        self.lifetime += 1
        key = since.strftime("%Y-%m")
        self.months[key] = int(self.months.get(key, 0)) + 1
        extra = sorted(self.months)[: max(0, len(self.months) - KEEP_MONTHS)]
        for old in extra:
            del self.months[old]
        return [since]

    def restore(self, data: dict[str, Any] | None) -> list[datetime]:
        """Read the stored counter, then replay the queue; the starts the replay counted."""
        stored = StartCounter.from_dict(data)
        queued, self.queued = self.queued or [], None
        self.running, self.lifetime, self.months = stored.running, stored.lifetime, stored.months
        return [at for edge in queued for at in self.fold(*edge)]

    def month_count(self, month: str) -> int:
        return int(self.months.get(month, 0))

    # -- persistence --------------------------------------------------------

    def as_dict(self) -> dict[str, Any]:
        return {
            "lifetime": int(self.lifetime),
            "months": {k: int(v) for k, v in self.months.items()},
            "running": bool(self.running),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "StartCounter":
        """A restored counter from the stored payload; absent or invalid fields read as zero."""
        counter = cls(queued=None)
        if not isinstance(data, dict):
            return counter
        try:
            counter.lifetime = max(0, int(data.get("lifetime", 0)))
        except (TypeError, ValueError, OverflowError):
            counter.lifetime = 0
        months = data.get("months")
        if isinstance(months, dict):
            for key, value in months.items():
                try:
                    if (starts := int(value)) >= 1:  # a month is written at its first start
                        counter.months[str(key)] = starts
                except (TypeError, ValueError, OverflowError):
                    continue
        counter.running = bool(data.get("running", False))
        return counter


def wear_price_per_start(replacement_cost: float, rated_starts: int) -> float:
    """SEK one compressor start consumes of its replacement budget."""
    if not np.isfinite(replacement_cost) or replacement_cost <= 0:
        return 0.0
    return float(replacement_cost) / max(1, int(rated_starts))
