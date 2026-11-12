"""Compressor start counting and the wear price it implies (T6 #55).

Every heat pump datasheet rates the compressor in starts, yet nothing in the
integration counted them — the cycling penalty priced an *assumed* cost. This
module builds the first realised counter: edge detection on the measured
power, debounced with a two-sample hysteresis so a single noisy meter reading
never books a start, and blind to the immersion element on purpose — #11's
classifier already knows when the draw is resistive, and a resistive spike is
exactly the shape a naive edge detector would call a compressor start.

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

from .const import START_HYSTERESIS_SAMPLES
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
class StartCounter:
    """Debounced compressor-start counter over measured power samples."""

    #: Confirmed running state (after hysteresis), not the raw sample.
    running: bool = False
    #: Consecutive samples on the far side of the threshold.
    _streak: int = 0
    lifetime: int = 0
    months: dict[str, int] = field(default_factory=dict)

    def observe(
        self,
        when: datetime,
        measured_kw: float | None,
        threshold_kw: float,
        immersion_active: bool,
    ) -> bool:
        """Fold one power sample; True when a start was just confirmed.

        ``immersion_active`` freezes the state machine entirely rather than
        clamping the sample: while the element runs, the meter reads
        compressor-plus-resistive and neither edge direction can be trusted.
        The streak resets too — half an edge observed before the element cut
        in must not combine with half an edge observed after it drops out.
        """
        if measured_kw is None or not np.isfinite(measured_kw):
            # A meter outage resets the streak for the same reason the
            # element does: "two CONSECUTIVE samples" is the promise, and
            # two noise spikes separated by hours of missing readings are
            # not consecutive.
            self._streak = 0
            return False
        if immersion_active:
            self._streak = 0
            return False
        above = float(measured_kw) >= float(threshold_kw)
        if above == self.running:
            self._streak = 0
            return False
        self._streak += 1
        if self._streak < START_HYSTERESIS_SAMPLES:
            return False
        self._streak = 0
        self.running = above
        if not above:
            return False
        self.lifetime += 1
        key = when.strftime("%Y-%m")
        self.months[key] = int(self.months.get(key, 0)) + 1
        extra = sorted(self.months)[: max(0, len(self.months) - KEEP_MONTHS)]
        for old in extra:
            del self.months[old]
        return True

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
        counter = cls()
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
