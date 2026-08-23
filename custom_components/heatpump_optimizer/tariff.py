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
        """Above what level a new hour would raise the bill, in kW.

        Once the month has ``peaks_averaged`` peaks recorded, this is the
        lowest of them: anything under it displaces nothing and is free.

        Before that there is no reference, and the honest answer is *not*
        zero. Treating every kW as a brand-new peak makes the capacity term
        dwarf the entire energy cost — measured at roughly nine times it for a
        normal 6 kW day — so a fresh install, or the first days of any month,
        would contort the plan to avoid a peak the house sets on any ordinary
        day regardless.

        So with too little history the threshold is the lowest peak actually
        seen, and with none at all the term is disabled entirely by returning
        infinity. The tariff starts biting once there is something real to
        compare against, which is also when its answer starts being right.
        """
        if not self.peaks:
            return float("inf")
        n = max(1, tariff.peaks_averaged)
        if len(self.peaks) < n:
            return float(self.peaks[-1])
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


def metering_windows(
    house_power_kw: np.ndarray,
    window_minutes: int,
    dt_hours: float,
    offset_steps: int = 0,
) -> np.ndarray:
    """Box-average a per-step series into the tariff's metering windows.

    A 15-minute burst inside an hourly-metered tariff only raises the hourly
    average by a quarter of its excess, so penalising the instantaneous step
    would give away real savings to avoid a peak that is never billed.

    ``offset_steps`` is how many steps remain until the DSO's next window
    boundary. The plan rarely starts on one — a solve at 12:15 folded windows
    [12:15, 13:15) while the meter bills [12:00, 13:00) — and on the shifted
    grid a burst that really sits inside one billed window is split across
    two, halving its priced excess. The leading partial window is averaged
    over the steps it has; its already-elapsed consumption is unknowable here
    and is what the peak tracker's threshold accounts for.
    """
    house = np.asarray(house_power_kw, dtype=float)
    if house.size == 0:
        return house
    per_window = max(1, int(round(window_minutes / max(dt_hours * 60.0, 1e-6))))
    if per_window <= 1:
        return house

    head_steps = int(offset_steps) % per_window
    head = house[:head_steps]
    rest = house[head_steps:]

    pieces: list[np.ndarray] = []
    if head.size:
        pieces.append(np.array([head.mean()]))
    full = rest.size // per_window
    if full:
        pieces.append(rest[: full * per_window].reshape(full, per_window).mean(axis=1))
    tail = rest[full * per_window :]
    if tail.size:
        pieces.append(np.array([tail.mean()]))
    if not pieces:
        return np.array([house.mean()])
    return np.concatenate(pieces)


def peak_penalty(
    total_power_kw: np.ndarray,
    baseline_load_kw: np.ndarray,
    threshold_kw: float,
    tariff: CapacityTariff,
    dt_hours: float,
) -> float:
    """Cost of the new monthly peak this plan would create."""
    return peak_cost(
        total_power_kw,
        baseline_load_kw,
        threshold_kw,
        tariff.marginal_price_per_kw,
        tariff.window_minutes,
        dt_hours,
        tariff.peaks_averaged,
    )


def peak_cost(
    total_power_kw: np.ndarray,
    baseline_load_kw: np.ndarray,
    threshold_kw: float,
    price_per_kw: float,
    window_minutes: int,
    dt_hours: float,
    peaks_averaged: int = 3,
    offset_steps: int = 0,
) -> float:
    """What this plan would add to the monthly capacity charge.

    The bill is ``full_price × mean(top-k window peaks)``. Rearranged, that is
    ``(full_price / k) × sum(top-k)`` — and ``full_price / k`` is exactly
    ``marginal_price_per_kw``. So the cost of a plan is the marginal price
    times the sum of its top-k excesses above what the month already commits
    to, which is what this computes.

    Two things fall out of getting the algebra right rather than approximating:

    * **It is exact.** Charging only the single largest excess, as this
      previously did, under-states a plan with several high hours — precisely
      the plan a capacity tariff exists to discourage.
    * **The solver can see it.** ``max`` has zero gradient everywhere except at
      one window, so a gradient-based optimizer got a signal at 1 step in 96
      and the term was effectively inert; the measured result was that enabling
      the tariff *raised* the peak. Summing the top k gives every one of those
      k windows a gradient.

    Only the excess above the threshold is charged: if the month already has a
    9 kW peak recorded, an 8 kW hour changes nothing and costs nothing.
    """
    if price_per_kw <= 0 or not np.isfinite(threshold_kw):
        return 0.0
    house = np.asarray(total_power_kw, dtype=float) + np.asarray(
        baseline_load_kw, dtype=float
    )
    if house.size == 0:
        return 0.0
    windows = metering_windows(house, window_minutes, dt_hours, offset_steps)
    excess = np.maximum(0.0, windows - threshold_kw)
    if not np.any(excess > 0):
        return 0.0
    k = max(1, min(int(peaks_averaged), excess.size))
    top_k = np.sort(excess)[-k:]
    return float(price_per_kw * np.sum(top_k))


def realised_peak(
    total_power_kw: np.ndarray,
    baseline_load_kw: np.ndarray,
    window_minutes: int,
    dt_hours: float,
    offset_steps: int = 0,
) -> float:
    """The peak a plan would actually be billed on, in kW.

    The true maximum, not the smoothed one: the smoothing exists to give the
    solver a gradient, and reporting it to the user would overstate the peak.
    """
    house = np.asarray(total_power_kw, dtype=float) + np.asarray(
        baseline_load_kw, dtype=float
    )
    if house.size == 0:
        return 0.0
    return float(np.max(metering_windows(house, window_minutes, dt_hours, offset_steps)))
