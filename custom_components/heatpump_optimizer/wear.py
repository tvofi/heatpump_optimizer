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

import numpy as np

from .const import START_HYSTERESIS_SAMPLES

#: Months of per-month counts kept, matching the ledger's horizon.
KEEP_MONTHS = 24


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

    def as_dict(self) -> dict:
        return {
            "lifetime": int(self.lifetime),
            "months": {k: int(v) for k, v in self.months.items()},
            "running": bool(self.running),
        }

    @classmethod
    def from_dict(cls, data: dict | None) -> "StartCounter":
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
                    counter.months[str(key)] = max(0, int(value))
                except (TypeError, ValueError, OverflowError):
                    continue
        counter.running = bool(data.get("running", False))
        return counter


def wear_price_per_start(replacement_cost: float, rated_starts: int) -> float:
    """SEK one compressor start consumes of its replacement budget."""
    if not np.isfinite(replacement_cost) or replacement_cost <= 0:
        return 0.0
    return float(replacement_cost) / max(1, int(rated_starts))
