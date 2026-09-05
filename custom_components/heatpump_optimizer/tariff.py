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
from datetime import datetime, timedelta

import numpy as np

from .dhw_schedule import Window, hour_in_windows

_LOGGER = logging.getLogger(__name__)


def _window_slot(when: datetime, window_minutes: int) -> datetime:
    """The start of the metering window containing ``when``.

    Anchored at local midnight and stepped by ``timedelta``, matching the
    optimizer's ``_window_offset_steps`` phase arithmetic — the DSO's grid
    runs from midnight, not from each wall-clock hour. The previous
    ``minute``-modulo snap could only move the minute field, so for windows
    longer than an hour the hour never advanced and a 90/120-minute tariff
    silently degenerated to hourly metering: less burst dilution, inflated
    recorded peaks and thresholds, and factor masks sampled one window off.
    For any window that divides the hour (15/30/60 — every common DSO
    config) this is bit-identical to the old snap, isoformat key included,
    so persisted ``window_key`` accumulators survive the upgrade untouched.
    """
    window = max(1, int(window_minutes))
    midnight = when.replace(hour=0, minute=0, second=0, microsecond=0)
    minutes = ((when.hour * 60 + when.minute) // window) * window
    slot = midnight + timedelta(minutes=minutes)
    if window <= 60:
        # ``timedelta`` arithmetic resets ``fold``, and the window key is the
        # slot's isoformat: without the flag, both real passes of the autumn
        # transition's repeated hour render the same key, one accumulator
        # swallows two metered hours, and a burst peak is diluted by their
        # average — under-recording exactly the threshold the live guard
        # protects. Sub-hour slots share ``when``'s wall hour, so the flag
        # transfers exactly (and is inert outside the ambiguous hour).
        # Windows longer than an hour stay wall-anchored at fold 0: the
        # repeated hour extends that window's real duration, which matches
        # wall-clock billing, while splitting on the flag would fabricate a
        # one-hour "window" no DSO meters.
        slot = slot.replace(fold=when.fold)
    return slot


@dataclass
class CapacityTariff:
    """Configuration of a monthly capacity tariff.

    The masks (#13) are how most real Swedish effekttariffs deviate from the
    flat model: many count only weekday daytime peaks, bill night peaks at a
    reduced rate, or apply only November–March. Every mask's default means
    "no mask": empty month set, empty hour windows and ``weekdays_only``
    False with ``offpeak_factor`` 1.0 reproduce the flat model bit for bit.
    """

    enabled: bool = False
    #: Currency per kW per month.
    price_per_kw: float = 0.0
    #: How many of the month's highest peaks are averaged for the bill.
    peaks_averaged: int = 3
    #: Metering window in minutes. Most Swedish DSOs meter hourly; some newer
    #: tariffs use 15 minutes, which is much harder to hide a defrost in.
    window_minutes: int = 60
    #: Months the tariff applies in at all; empty = every month. Outside
    #: them a window contributes *nothing* — not a discounted peak.
    months: frozenset[int] = frozenset()
    #: Peak hours; empty = all hours are peak. Outside them (or on a
    #: weekend, with ``weekdays_only``) the off-peak factor applies.
    peak_hours: tuple[Window, ...] = ()
    #: Weekends are off-peak when set.
    weekdays_only: bool = False
    #: What an off-peak window's kW counts at, 0..1. 1.0 = no distinction
    #: (the flat model); 0.5 = the common half-rate night peak; 0.0 =
    #: off-peak hours are free.
    offpeak_factor: float = 1.0

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

    def sample_factor(self, when: datetime) -> float:
        """What a metered kW at ``when`` counts at towards the billed peak.

        1.0 in peak hours (or with no masks at all), the off-peak factor in
        off-peak hours, and 0.0 in months where the tariff does not apply.
        """
        if self.months and when.month not in self.months:
            return 0.0
        offpeak = False
        if self.weekdays_only and when.weekday() >= 5:
            offpeak = True
        elif self.peak_hours:
            hour = when.hour + when.minute / 60.0
            offpeak = not hour_in_windows(hour, list(self.peak_hours))
        if not offpeak:
            return 1.0
        return float(min(1.0, max(0.0, self.offpeak_factor)))


@dataclass
class PeakTracker:
    """The realised peaks so far this month.

    With the masks (#13) the peaks kept here are *billed-equivalent* kW:
    each closed window's average scaled by what its hour counts at. A window
    in a month the tariff skips is not recorded at all — recording a zero
    would poison ``threshold_kw``'s early-month "lowest peak seen" answer.
    With no masks configured the factor is always 1.0 and nothing changes.
    """

    month: str = ""
    #: Highest billed-equivalent window averages seen this month, descending.
    peaks: list[float] = field(default_factory=list)
    #: Accumulator for the window currently being metered.
    _window_key: str = ""
    _window_sum: float = 0.0
    _window_samples: int = 0
    #: What the open window's kW counts at, captured when it opens.
    _window_factor: float = 1.0
    #: Time-weighted accumulator (#7): kW·h and hours. Fed only when a
    #: caller supplies ``dt_hours`` — the live meter listener, which knows
    #: real spacing. The 30-minute tick path never does, and with both
    #: accumulators empty of weighted samples the unweighted average is used
    #: bit for bit, which is what keeps every pre-T2 install identical.
    _window_wsum: float = 0.0
    _window_weight: float = 0.0

    # -- accumulation -------------------------------------------------------

    def observe(
        self,
        when: datetime,
        house_power_kw: float,
        tariff: CapacityTariff,
        dt_hours: float | None = None,
    ) -> None:
        """Fold one power sample into the current metering window.

        With ``dt_hours`` the sample is weighted by the time it actually
        stood for; a window holding any weighted sample closes on the
        weighted average. Without it (every pre-T2 caller) the unweighted
        sample mean is used, unchanged.
        """
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
            self._window_factor = 1.0
            self._window_wsum = 0.0
            self._window_weight = 0.0

        window = max(1, int(tariff.window_minutes))
        slot = _window_slot(when, window)
        key = f"{slot.isoformat()}|{window}"

        if key != self._window_key:
            self._close_window(tariff)
            self._window_key = key
            self._window_sum = 0.0
            self._window_samples = 0
            self._window_wsum = 0.0
            self._window_weight = 0.0
            # The whole window bills at one rate, so the factor is the
            # window's, not each sample's: a window straddling the 19:00
            # peak-hour boundary is billed by where it starts, exactly as
            # the DSO's meter attributes it.
            self._window_factor = tariff.sample_factor(slot)

        self._window_sum += float(house_power_kw)
        self._window_samples += 1
        if dt_hours is not None and np.isfinite(dt_hours) and dt_hours > 0:
            self._window_wsum += float(house_power_kw) * float(dt_hours)
            self._window_weight += float(dt_hours)

    def _window_mean(self) -> float | None:
        """The open window's running average, weighted where possible."""
        if self._window_weight > 0:
            return self._window_wsum / self._window_weight
        if self._window_samples > 0:
            return self._window_sum / self._window_samples
        return None

    def window_snapshot(
        self, when: datetime, tariff: CapacityTariff
    ) -> tuple[str, float | None, float, float]:
        """(window key, running mean or None, elapsed minutes, billing
        factor) at ``when``.

        The guard's projection input (#7). Read-only: a snapshot for a
        window other than the open one reports no accumulated mean, which
        the projection treats as "assume the current draw throughout". The
        factor is what this window's kW counts at under the #13 masks —
        the guard must compare billed-equivalent kW against the
        billed-equivalent threshold, or it would defend hours the tariff
        does not bill.
        """
        window = max(1, int(tariff.window_minutes))
        slot = _window_slot(when, window)
        key = f"{slot.isoformat()}|{window}"
        elapsed = (when - slot).total_seconds() / 60.0
        mean = self._window_mean() if key == self._window_key else None
        return key, mean, elapsed, tariff.sample_factor(slot)

    def _close_window(self, tariff: CapacityTariff) -> None:
        average = self._window_mean()
        if average is None:
            return
        if self._window_factor <= 0.0:
            # The tariff does not bill this window at all (masked month, or
            # off-peak hours that are free). Contributing nothing is the
            # point; contributing zero would be a discount.
            return
        self.peaks.append(average * self._window_factor)
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

        That infinity is a *decision sentinel* for the solver, never a number
        to publish. It is what this returns on the 1st of every month, for
        every install with a capacity tariff, because the tracker starts each
        month with no peaks. Two consumers have to know that: the sensor
        platform maps non-finite to ``None`` at the publication boundary
        (``sensor._finite``), and ``_power_headroom`` reads it as "the bill is
        set from zero", not as "draw what you like".
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
            "window_factor": self._window_factor,
            "window_wsum": self._window_wsum,
            "window_weight": self._window_weight,
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
        except (TypeError, ValueError, OverflowError):
            tracker._window_sum = 0.0
            tracker._window_samples = 0
        try:
            # Absent from pre-v4 payloads; 1.0 is the unmasked behaviour.
            tracker._window_factor = float(data.get("window_factor", 1.0))
        except (TypeError, ValueError, OverflowError):
            tracker._window_factor = 1.0
        try:
            # A restart mid-window must not close that window on the
            # unweighted mean — that would readmit exactly the phantom
            # chatty-meter peak the weighted fold exists to prevent.
            tracker._window_wsum = float(data.get("window_wsum", 0.0))
            tracker._window_weight = float(data.get("window_weight", 0.0))
        except (TypeError, ValueError, OverflowError):
            tracker._window_wsum = 0.0
            tracker._window_weight = 0.0
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


def mask_active(tariff: CapacityTariff) -> bool:
    """Whether any #13 mask can change what a window counts at."""
    return bool(tariff.months) or (
        (bool(tariff.peak_hours) or tariff.weekdays_only)
        and tariff.offpeak_factor < 1.0
    )


def window_factors(
    tariff: CapacityTariff,
    start_time: datetime | None,
    n_windows: int,
    dt_hours: float,
) -> np.ndarray | None:
    """Billing factor per metering window over the horizon, or None.

    None when no mask is configured — the fast path, and the proof of
    inertness: ``peak_cost`` with ``None`` runs the exact pre-#13 arithmetic.
    Windows are keyed by their aligned start instant, matching how
    ``PeakTracker.observe`` attributes a live window, so the plan's cost term
    and the realised tracker can never disagree about which hour a window
    bills under.
    """
    if start_time is None or n_windows <= 0 or not mask_active(tariff):
        return None
    window = max(1, int(tariff.window_minutes))
    slot0 = _window_slot(start_time, window)
    return np.asarray(
        [
            tariff.sample_factor(slot0 + timedelta(minutes=window * i))
            for i in range(n_windows)
        ],
        dtype=float,
    )


# Soft top-k temperature as a fraction of the largest excess. Small enough
# that separated peaks still match the billed sum; large enough that tied
# windows all carry gradient (#232).
_PEAK_SMOOTH_TAU = 0.05


def _smooth_topk_sum(values: np.ndarray, k: int, tau: float) -> float:
    """Differentiable approximation to ``sum(sort(values)[-k:])``.

    A hard top-k has zero gradient on every tied window beyond the kth, which
    leaves gradient-based solvers blind on the peak plateau that capacity
    tariffs create. Here a logistic threshold is chosen so the soft weights
    sum to *k*; when many windows tie, each gets weight ``k/n`` and the
    approximate sum stays ``k × tie_level``.
    """
    x = np.asarray(values, dtype=float)
    if x.size == 0 or k <= 0:
        return 0.0
    k = max(1, min(int(k), x.size))
    if not np.any(x > 0):
        return 0.0
    peak = float(np.max(x))
    scale = max(tau * peak, 1e-9)
    lo, hi = float(np.min(x)) - 1.0, peak + 1.0
    mid = 0.5 * (lo + hi)
    for _ in range(64):
        w = 1.0 / (1.0 + np.exp(-(x - mid) / scale))
        count = float(np.sum(w))
        if abs(count - k) < 1e-6:
            break
        if count > k:
            lo = mid
        else:
            hi = mid
        mid = 0.5 * (lo + hi)
    w = 1.0 / (1.0 + np.exp(-(x - mid) / scale))
    return float(np.sum(w * x))


def peak_cost(
    total_power_kw: np.ndarray,
    baseline_load_kw: np.ndarray,
    threshold_kw: float,
    price_per_kw: float,
    window_minutes: int,
    dt_hours: float,
    peaks_averaged: int = 3,
    offset_steps: int = 0,
    window_factors: np.ndarray | None = None,
) -> float:
    """What this plan would add to the monthly capacity charge.

    The bill is ``full_price × mean(top-k window peaks)``. Rearranged, that is
    ``(full_price / k) × sum(top-k)`` — and ``full_price / k`` is exactly
    ``marginal_price_per_kw``. So the cost of a plan is the marginal price
    times the sum of its top-k excesses above what the month already commits
    to, which is what this computes.

    Two things fall out of that algebra:

    * **Several high hours all count.** Charging only the single largest
      excess, as this previously did, under-states a plan with several high
      hours — precisely the plan a capacity tariff exists to discourage.
    * **The solver can see it.** ``max`` has zero gradient everywhere except at
      one window, so a gradient-based optimizer got a signal at 1 step in 96
      and the term was effectively inert; the measured result was that enabling
      the tariff *raised* the peak. Summing the top k gives every one of those
      k windows a gradient; when more than k windows tie, a smooth top-k
      spreads that signal across all of them (#232).

    It is still an upper bound on the true marginal bill, not an exact figure:
    each of the plan's top-k windows is charged as if it displaced a billed
    peak, but only windows that end the *month* in the top k actually do.
    Early in a month that is usually true; late in a high-peak month it
    over-charges and the plan is more peak-shy than strictly necessary —
    the conservative side of the error.

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
    if window_factors is not None and window_factors.size:
        # Billed-equivalent kW (#13): each window's average counts at its
        # hour's factor, against a threshold the tracker keeps in the same
        # billed-equivalent terms. A masked-out window (factor 0) can never
        # exceed any threshold, which is "contributes nothing" exactly.
        factors = window_factors[: windows.size]
        if factors.size < windows.size:
            factors = np.concatenate(
                [factors, np.ones(windows.size - factors.size)]
            )
        windows = windows * factors
    excess = np.maximum(0.0, windows - threshold_kw)
    if not np.any(excess > 0):
        return 0.0
    k = max(1, min(int(peaks_averaged), excess.size))
    return float(price_per_kw * _smooth_topk_sum(excess, k, _PEAK_SMOOTH_TAU))


def realised_peak(
    total_power_kw: np.ndarray,
    baseline_load_kw: np.ndarray,
    window_minutes: int,
    dt_hours: float,
    offset_steps: int = 0,
) -> float:
    """The peak a plan would actually be billed on, in kW.

    The highest metering-window average over the horizon — the quantity the
    DSO meters — not the per-step maximum, which would overstate the peak by
    however much of a burst the window average dilutes.
    """
    house = np.asarray(total_power_kw, dtype=float) + np.asarray(
        baseline_load_kw, dtype=float
    )
    if house.size == 0:
        return 0.0
    return float(np.max(metering_windows(house, window_minutes, dt_hours, offset_steps)))
