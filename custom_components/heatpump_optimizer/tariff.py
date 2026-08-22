"""Monthly capacity (peak power) tariff awareness.

Swedish and increasingly Nordic DSOs bill a monthly *effekttariff*: typically
the mean of the three highest hourly consumption peaks in the month, priced per
kW. Nothing in the optimizer modelled this, so it would happily stack hot water
and space heating into the same cheap hour. A single new monthly peak can
easily cost more than the energy that stacking saved — the tariff is often
30-90 SEK/kW, against an energy saving measured in öre.

Three design points:

**The peak is whole-house.** Metering happens at the connection point, so the
heat pump's own draw is not the quantity being billed. A baseline load entity
is therefore part of the configuration; without one the model still works but
only sees the heat pump, and will under-estimate the peak.

**The penalty is soft, not a cap.** A hard constraint would fight the comfort
band and could make the problem infeasible on a cold morning. What is wanted is
a price signal: exceeding the running peak costs the tariff rate, so the
optimizer trades it off against energy cost the same way it trades everything
else.

**Only exceeding the *running* peak costs anything.** If the month already has
a 9 kW peak, an 8 kW hour is free — the bill is already set. That asymmetry is
the whole point, and modelling it as "keep power low" instead would give away
savings for nothing.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime

import numpy as np

_LOGGER = logging.getLogger(__name__)


@dataclass
class CapacityTariff:
    """Configuration of a monthly capacity tariff."""

    enabled: bool = False
    #: Currency per kW per month.
    price_per_kw: float = 0.0
    #: How many of the month's highest peaks are averaged for the bill.
    peaks_averaged: int = 3
    #: Metering window in minutes. Most Swedish DSOs meter hourly; some newer
    #: tariffs use 15 minutes, which is much harder to hide a defrost in.
    window_minutes: int = 60

    @property
    def marginal_price_per_kw(self) -> float:
        """Cost of raising the billed peak by 1 kW.

        Raising *one* peak by 1 kW raises the average of ``peaks_averaged``
        peaks by ``1/peaks_averaged`` kW, so the marginal cost is the tariff
        divided by the number averaged. Charging the full tariff would
        over-price the constraint by a factor of three on a typical tariff and
        make the optimizer far too timid.
        """
        if not self.enabled or self.peaks_averaged <= 0:
            return 0.0
        return self.price_per_kw / float(self.peaks_averaged)


@dataclass
class PeakTracker:
    """The realised peaks so far this month."""

    month: str = ""
    #: Highest metered window averages seen this month, descending.
    peaks: list[float] = field(default_factory=list)
    #: Accumulator for the window currently being metered.
    _window_key: str = ""
    _window_sum: float = 0.0
    _window_samples: int = 0

    # -- accumulation -------------------------------------------------------

    def observe(
        self, when: datetime, house_power_kw: float, tariff: CapacityTariff
    ) -> None:
        """Fold one power sample into the current metering window."""
        if not np.isfinite(house_power_kw) or house_power_kw < 0:
            return
        month = when.strftime("%Y-%m")
        if month != self.month:
            # A new month starts with a clean slate; last month's peaks are
            # already billed and constrain nothing.
            self.month = month
            self.peaks = []
            self._window_key = ""
            self._window_sum = 0.0
            self._window_samples = 0

        window = max(1, int(tariff.window_minutes))
        slot = when.replace(second=0, microsecond=0)
        slot = slot.replace(minute=(slot.minute // window) * window % 60)
        key = f"{slot.isoformat()}|{window}"

        if key != self._window_key:
            self._close_window(tariff)
            self._window_key = key
            self._window_sum = 0.0
            self._window_samples = 0

        self._window_sum += float(house_power_kw)
        self._window_samples += 1

    def _close_window(self, tariff: CapacityTariff) -> None:
        if self._window_samples <= 0:
            return
        average = self._window_sum / self._window_samples
        self.peaks.append(average)
        self.peaks.sort(reverse=True)
        # Keep a little more than the billed count so that a later correction
        # (a retracted sample) does not lose the runner-up.
        keep = max(tariff.peaks_averaged * 2, 6)
        del self.peaks[keep:]

    # -- reporting ----------------------------------------------------------

    def billed_peak_kw(self, tariff: CapacityTariff) -> float:
        """The peak level the bill is currently based on, in kW."""
        if not self.peaks:
            return 0.0
        n = max(1, tariff.peaks_averaged)
        top = self.peaks[:n]
        return float(sum(top) / len(top))

    def threshold_kw(self, tariff: CapacityTariff) -> float:
        """Above what level a new hour would raise the bill.

        Until the month has ``peaks_averaged`` peaks recorded, *any* hour joins
        the billed set, so the threshold is zero and every kW is chargeable.
        That is correct: early in the month there is no free headroom.
        """
        n = max(1, tariff.peaks_averaged)
        if len(self.peaks) < n:
            return 0.0
        return float(self.peaks[n - 1])

    def as_dict(self) -> dict:
        return {
            "month": self.month,
            "peaks": [round(p, 3) for p in self.peaks],
            "window_key": self._window_key,
            "window_sum": self._window_sum,
            "window_samples": self._window_samples,
        }

    @classmethod
    def from_dict(cls, data: dict | None) -> "PeakTracker":
        tracker = cls()
        if not isinstance(data, dict):
            return tracker
        tracker.month = str(data.get("month", ""))
        peaks = data.get("peaks")
        if isinstance(peaks, list):
            tracker.peaks = [
                float(p) for p in peaks if isinstance(p, (int, float))
            ]
            tracker.peaks.sort(reverse=True)
        tracker._window_key = str(data.get("window_key", ""))
        try:
            tracker._window_sum = float(data.get("window_sum", 0.0))
            tracker._window_samples = int(data.get("window_samples", 0))
        except (TypeError, ValueError):
            tracker._window_sum = 0.0
            tracker._window_samples = 0
        return tracker


def peak_penalty(
    total_power_kw: np.ndarray,
    baseline_load_kw: np.ndarray,
    threshold_kw: float,
    tariff: CapacityTariff,
    dt_hours: float,
) -> float:
    """Cost of the peak this plan would create, above what is already billed.

    Averaged over the metering window rather than applied per optimizer step:
    a 15-minute burst inside an hourly-metered tariff only raises the hourly
    average by a quarter of its excess, and penalising the instantaneous step
    would give away real savings to avoid a peak that is never billed.
    """
    marginal = tariff.marginal_price_per_kw
    if marginal <= 0:
        return 0.0

    house = np.asarray(total_power_kw, dtype=float) + np.asarray(
        baseline_load_kw, dtype=float
    )
    steps_per_window = max(
        1, int(round(tariff.window_minutes / max(dt_hours * 60.0, 1e-6)))
    )
    if steps_per_window > 1:
        # Box-average into metering windows, keeping any short tail.
        n_full = len(house) // steps_per_window
        if n_full:
            head = house[: n_full * steps_per_window].reshape(
                n_full, steps_per_window
            )
            windows = head.mean(axis=1)
            tail = house[n_full * steps_per_window :]
            if tail.size:
                windows = np.append(windows, tail.mean())
        else:
            windows = np.array([house.mean()])
    else:
        windows = house

    excess = np.maximum(0.0, windows - threshold_kw)
    if not np.any(excess > 0):
        return 0.0
    # Only the single largest excess in the horizon actually sets a new peak;
    # summing them would charge the tariff once per hour, which is nonsense.
    return float(marginal * np.max(excess))
