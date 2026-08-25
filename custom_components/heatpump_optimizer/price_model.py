"""A learned prior for the part of the price horizon that is not published yet.

Nord Pool and Tibber publish tomorrow's prices around 13:00 local time. Before
that, a large fraction of a 24-hour-plus horizon has no data, and the
coordinator used to fill it by repeating the last known value:

.. code-block:: python

    while len(prices) < n_steps:
        prices.append(prices[-1] if prices else 0.5)

A flat tail has no trough. The optimizer therefore cannot see a cheap period
ahead worth waiting for, and systematically under-defers load in the morning —
precisely when deferral is most valuable. It also interacts badly with the
terminal-cost term, which values stored heat against a price that is entirely
fictitious.

What replaces it is a normalised diurnal shape learned from the prices that
*have* been seen, scaled to the recent price level. Two design points matter:

**The prior must never displace real data.** If tomorrow's prices are known,
the learned shape is not consulted at all. It fills unknown steps only.

**Padded steps are marked.** Consumers get a per-step confidence flag so the
plan sensors and the dashboard card can show where the plan rests on a guess
rather than on published prices. A plan that looks identical whether or not it
is built on real prices is a plan nobody can audit.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime

import numpy as np

_LOGGER = logging.getLogger(__name__)

HOURS_PER_DAY = 24
QUARTERS_PER_HOUR = 4
QUARTERS_PER_DAY = HOURS_PER_DAY * QUARTERS_PER_HOUR
# Weekday and weekend price shapes differ enough to be worth separating: the
# morning peak is later and shallower at the weekend.
PROFILE_WEEKDAY = 0
PROFILE_WEEKEND = 1

# EWMA rate for the shape. Slow, because a single unusual day (a cold snap, a
# transmission outage) should not redefine what a normal day looks like.
SHAPE_ALPHA = 0.12
# Below this many observed days the shape is blended towards flat, so an early
# accidental pattern cannot drive the plan.
SHAPE_CONFIDENCE_DAYS = 5
# Guard rails on the normalised shape. Real spot curves do swing widely, but a
# factor outside this range is a data error rather than a market.
SHAPE_MIN = 0.2
SHAPE_MAX = 3.0

# The quarter-hour refinement (#19) rides its own confidence ramp: the hourly
# shape may be fully trusted while intra-hour structure is still unseen, and
# a factor of 1.0 at zero confidence makes the 96-bin model collapse exactly
# onto the 24-bin one — which is what keeps old stores and fresh installs
# byte-identical.
QUARTER_ALPHA = 0.12
QUARTER_CONFIDENCE_DAYS = 5
# Intra-hour ramps are real (the 06:45 quarter can be 50-100 öre from 06:00)
# but a quarter at several times its hour's mean is a data error.
QUARTER_FACTOR_MIN = 0.25
QUARTER_FACTOR_MAX = 4.0

# Dispersion of the prior's misses (#34), per (profile, hour), as an EWMA of
# squared normalised residuals. Slightly faster than the shape: how wrong the
# prior has been lately is more useful than a long memory of old regimes.
VAR_ALPHA = 0.15


def _profile_index(when: datetime) -> int:
    return PROFILE_WEEKEND if when.weekday() >= 5 else PROFILE_WEEKDAY


@dataclass
class PriceShapeModel:
    """Normalised mean price by hour of day, split weekday/weekend.

    The 24-bin hourly ``shapes`` are the model as it has always been. The
    quarter factors (#19) and residual variance (#34) are strictly additive
    refinements: absent from an old store they default to "no effect", and
    the loader never reshapes ``shapes`` itself — the silent-fallback loader
    would discard a reshaped payload, learned state and all.
    """

    #: ``shapes[profile][hour]``, each profile normalised to mean 1.0.
    shapes: list[list[float]] = field(
        default_factory=lambda: [[1.0] * HOURS_PER_DAY for _ in range(2)]
    )
    #: Number of complete days folded into each profile.
    days: list[int] = field(default_factory=lambda: [0, 0])
    #: ``quarter_factors[profile][hour*4+q]``: each quarter's price relative
    #: to its hour's mean, each hour's four factors normalised to mean 1.0.
    quarter_factors: list[list[float]] = field(
        default_factory=lambda: [[1.0] * QUARTERS_PER_DAY for _ in range(2)]
    )
    #: Complete quarter-resolution days folded into each profile.
    quarter_days: list[int] = field(default_factory=lambda: [0, 0])
    #: EWMA of squared normalised prior residuals per (profile, hour): how
    #: far the day's real normalised price landed from what the trusted
    #: shape would have predicted for that hour.
    residual_var: list[list[float]] = field(
        default_factory=lambda: [[0.0] * HOURS_PER_DAY for _ in range(2)]
    )

    # -- learning -----------------------------------------------------------

    def observe_day(self, when: datetime, hourly_prices: list[float]) -> bool:
        """Fold one complete day of hourly prices into the shape.

        Returns whether the observation was used. A partial day is rejected:
        the shape is about the *relative* cost of each hour, and a day missing
        its cheap night hours would bias every hour upward.
        """
        if len(hourly_prices) != HOURS_PER_DAY:
            return False
        values = np.asarray(hourly_prices, dtype=float)
        if not np.all(np.isfinite(values)):
            return False
        mean = float(np.mean(values))
        # A zero or negative daily mean makes the normalisation meaningless.
        # Negative spot hours are real and are kept in the shape; a whole day
        # averaging at or below zero is not something to generalise from.
        if mean <= 1e-6:
            return False

        normalised = np.clip(values / mean, SHAPE_MIN, SHAPE_MAX)
        idx = _profile_index(when)

        # The prior's miss, measured against what it would actually have
        # predicted — the trust-damped shape — *before* this day is folded
        # in. Folding first would let the day grade its own homework.
        predicted = np.asarray(self.shape_for(when), dtype=float)
        residuals = normalised - predicted
        var = np.asarray(self.residual_var[idx], dtype=float)
        if self.days[idx] == 0:
            var = residuals**2
        else:
            var = (1.0 - VAR_ALPHA) * var + VAR_ALPHA * residuals**2
        self.residual_var[idx] = [float(v) for v in var]

        current = np.asarray(self.shapes[idx], dtype=float)
        if self.days[idx] == 0:
            updated = normalised
        else:
            updated = (1.0 - SHAPE_ALPHA) * current + SHAPE_ALPHA * normalised
        # Re-normalise so the profile always has mean 1.0 and the scaling step
        # below is a pure level shift.
        updated = updated / max(float(np.mean(updated)), 1e-6)
        self.shapes[idx] = [float(v) for v in updated]
        self.days[idx] = self.days[idx] + 1
        return True

    def observe_day_quarters(
        self, when: datetime, quarter_prices: list[float]
    ) -> bool:
        """Fold one complete day of quarter prices into the quarter factors.

        Strictly additive beside ``observe_day``: the hourly shape carries
        the diurnal structure, and this carries only how each hour's price
        splits across its four quarters — the ramp structure the 15-minute
        MTU introduced, which an hourly prior smears flat.
        """
        if len(quarter_prices) != QUARTERS_PER_DAY:
            return False
        values = np.asarray(quarter_prices, dtype=float)
        if not np.all(np.isfinite(values)):
            return False
        if float(np.mean(values)) <= 1e-6:
            return False

        by_hour = values.reshape(HOURS_PER_DAY, QUARTERS_PER_HOUR)
        hour_means = by_hour.mean(axis=1)
        factors = np.ones_like(by_hour)
        usable = hour_means > 1e-6
        factors[usable] = np.clip(
            by_hour[usable] / hour_means[usable, None],
            QUARTER_FACTOR_MIN,
            QUARTER_FACTOR_MAX,
        )

        idx = _profile_index(when)
        current = np.asarray(self.quarter_factors[idx], dtype=float).reshape(
            HOURS_PER_DAY, QUARTERS_PER_HOUR
        )
        if self.quarter_days[idx] == 0:
            updated = factors
        else:
            updated = (1.0 - QUARTER_ALPHA) * current + QUARTER_ALPHA * factors
        # Each hour's four factors keep mean 1.0 so the refinement never
        # shifts the hourly level, only how it splits inside the hour.
        updated = updated / np.maximum(updated.mean(axis=1, keepdims=True), 1e-6)
        self.quarter_factors[idx] = [float(v) for v in updated.reshape(-1)]
        self.quarter_days[idx] = self.quarter_days[idx] + 1
        return True

    # -- use ----------------------------------------------------------------

    def confidence(self, when: datetime) -> float:
        """How much to trust the shape, between 0 and 1."""
        idx = _profile_index(when)
        return min(1.0, self.days[idx] / SHAPE_CONFIDENCE_DAYS)

    def quarter_confidence(self, when: datetime) -> float:
        """How much to trust the intra-hour factors, between 0 and 1."""
        idx = _profile_index(when)
        return min(1.0, self.quarter_days[idx] / QUARTER_CONFIDENCE_DAYS)

    def shape_for(self, when: datetime) -> np.ndarray:
        """Shape for this day, blended towards flat while still uncertain."""
        idx = _profile_index(when)
        shape = np.asarray(self.shapes[idx], dtype=float)
        trust = self.confidence(when)
        return 1.0 + (shape - 1.0) * trust

    def quarter_factor(self, when: datetime) -> float:
        """Intra-hour factor at ``when``, damped towards 1.0 while uncertain."""
        idx = _profile_index(when)
        trust = self.quarter_confidence(when)
        if trust <= 0.0:
            return 1.0
        q = (when.hour % HOURS_PER_DAY) * QUARTERS_PER_HOUR + (
            when.minute // 15
        ) % QUARTERS_PER_HOUR
        factor = float(self.quarter_factors[idx][q])
        return 1.0 + (factor - 1.0) * trust

    def predict(self, when: datetime, level: float) -> float:
        """Expected price at ``when`` given a recent average price ``level``."""
        shape = self.shape_for(when)
        return float(
            level * shape[when.hour % HOURS_PER_DAY] * self.quarter_factor(when)
        )

    def expected_daily_min(
        self, day_types: list[int], level: float
    ) -> float | None:
        """Expected cheapest hourly price over the given day types (#47).

        The elastic legionella gate asks: is today's known minimum already
        as cheap as a typical day gets, or is a better day likely before
        the deadline? The answer is the level scaled by the LOWEST hourly
        shape factor across the day types the remaining interval spans.

        None — the gate's "no opinion, defer to the deadline" answer —
        when any requested day type is not yet fully trusted. This is
        load-bearing, not politeness: a damped young shape has its minimum
        pulled toward 1.0, making the "expected minimum" the daily MEAN,
        and every horizon's cheapest hour beats its mean — so a young
        model would run the cycle at the minimum interval every time, the
        exact opposite of deferring. Shopping is for models that know the
        shape of a day.
        """
        if not day_types or not np.isfinite(level) or level <= 0.0:
            return None
        factors = []
        for idx in day_types:
            idx = int(idx) % len(self.shapes)
            if self.days[idx] < SHAPE_CONFIDENCE_DAYS:
                return None
            shape = np.asarray(self.shapes[idx], dtype=float)
            factors.append(float(np.min(shape)))
        return float(level * min(factors))

    def sigma(self, when: datetime, level: float) -> float:
        """One-sigma dispersion of the prior's guess at ``when``, in SEK/kWh.

        Damped by the shape's own confidence: a young model has both a vague
        mean and a vague variance, and a risk premium built on the latter
        alone would swing the plan on two days of evidence.
        """
        idx = _profile_index(when)
        var = float(self.residual_var[idx][when.hour % HOURS_PER_DAY])
        if var <= 0.0:
            return 0.0
        return float(level * np.sqrt(var) * self.confidence(when))

    # -- persistence --------------------------------------------------------

    def as_dict(self) -> dict:
        return {
            "shapes": self.shapes,
            "days": self.days,
            "quarter_factors": self.quarter_factors,
            "quarter_days": self.quarter_days,
            "residual_var": self.residual_var,
        }

    @classmethod
    def from_dict(cls, data: dict | None) -> "PriceShapeModel":
        model = cls()
        if not isinstance(data, dict):
            return model
        shapes = data.get("shapes")
        days = data.get("days")
        if (
            isinstance(shapes, list)
            and len(shapes) == 2
            and all(isinstance(s, list) and len(s) == HOURS_PER_DAY for s in shapes)
        ):
            model.shapes = [[float(v) for v in s] for s in shapes]
        if isinstance(days, list) and len(days) == 2:
            model.days = [int(v) for v in days]
        # Additive fields (#19, #34): absent from a pre-v4 store, and their
        # defaults mean "no effect", so an old payload loads into exactly the
        # behaviour it had.
        quarters = data.get("quarter_factors")
        if (
            isinstance(quarters, list)
            and len(quarters) == 2
            and all(
                isinstance(s, list) and len(s) == QUARTERS_PER_DAY
                for s in quarters
            )
        ):
            model.quarter_factors = [[float(v) for v in s] for s in quarters]
        qdays = data.get("quarter_days")
        if isinstance(qdays, list) and len(qdays) == 2:
            model.quarter_days = [int(v) for v in qdays]
        var = data.get("residual_var")
        if (
            isinstance(var, list)
            and len(var) == 2
            and all(isinstance(s, list) and len(s) == HOURS_PER_DAY for s in var)
        ):
            model.residual_var = [
                [max(0.0, float(v)) for v in s] for s in var
            ]
        return model

    def summary(self) -> dict:
        return {
            "weekday_days": self.days[PROFILE_WEEKDAY],
            "weekend_days": self.days[PROFILE_WEEKEND],
            "weekday_shape": [round(v, 3) for v in self.shapes[PROFILE_WEEKDAY]],
            "weekend_shape": [round(v, 3) for v in self.shapes[PROFILE_WEEKEND]],
            "weekday_quarter_days": self.quarter_days[PROFILE_WEEKDAY],
            "weekend_quarter_days": self.quarter_days[PROFILE_WEEKEND],
            "weekday_sigma": [
                round(float(np.sqrt(max(0.0, v))), 4)
                for v in self.residual_var[PROFILE_WEEKDAY]
            ],
            "weekend_sigma": [
                round(float(np.sqrt(max(0.0, v))), 4)
                for v in self.residual_var[PROFILE_WEEKEND]
            ],
        }


def extend_price_series(
    known: list[float],
    n_steps: int,
    step_start_times: list[datetime],
    model: PriceShapeModel | None,
    *,
    fallback: float = 0.5,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Extend a price series to ``n_steps``, marking which steps are guessed.

    Returns ``(prices, known_mask, sigma)``. ``known_mask[i]`` is True for
    steps backed by published prices. ``sigma`` (#34) is the prior's learned
    one-sigma dispersion per step, zero on every known step — published
    prices are facts — and zero everywhere while nothing has been learned,
    so a consumer adding ``λ·sigma`` prices exactly as before by default.
    """
    prices = list(known[:n_steps])
    known_count = len(prices)
    mask = np.zeros(n_steps, dtype=bool)
    mask[:known_count] = True
    sigma = np.zeros(n_steps, dtype=float)

    if known_count >= n_steps:
        return np.asarray(prices[:n_steps], dtype=float), mask, sigma

    if known_count == 0:
        return np.full(n_steps, fallback, dtype=float), mask, sigma

    # The level to scale the shape by comes from the known window — but the
    # shape is normalised to mean 1.0 over a whole *day*, and the known window
    # rarely is one. Known prices ending at the evening peak average ~1.4× the
    # daily level, and scaling by that raw mean overprices the entire guessed
    # tail by the same 40%. Dividing by the shape's own mean over the known
    # steps calibrates the level so shape × level reproduces the known window,
    # and reduces to the raw mean when the window covers whole days.
    level = float(np.mean(prices))
    last_known = float(prices[-1])
    if model is not None:
        shape_values = [
            float(
                model.shape_for(step_start_times[i])[
                    step_start_times[i].hour % HOURS_PER_DAY
                ]
            )
            for i in range(min(known_count, len(step_start_times)))
        ]
        shape_mean = float(np.mean(shape_values)) if shape_values else 1.0
        if shape_mean > 1e-6:
            level /= shape_mean

    for i in range(known_count, n_steps):
        when = (
            step_start_times[i]
            if i < len(step_start_times)
            else step_start_times[-1]
        )
        if model is None or model.confidence(when) <= 0.0:
            # No learned shape yet, so there is nothing better than the old
            # flat repeat. Being explicit about that is better than pretending.
            prices.append(last_known)
            continue
        prices.append(max(0.0, model.predict(when, level)))
        sigma[i] = model.sigma(when, level)

    return np.asarray(prices[:n_steps], dtype=float), mask, sigma


def _entries_by_day(entries: list[dict]) -> dict[str, dict[int, dict[int, float]]]:
    """Valid entries grouped as ``{day: {hour: {minute: value}}}``.

    Keyed by minute rather than kept as a list so quarter order never depends
    on the order the API happened to deliver entries in, and so a duplicated
    entry overwrites instead of double-counting.
    """
    by_day: dict[str, dict[int, dict[int, float]]] = {}
    for entry in entries or []:
        starts_at = entry.get("starts_at") or entry.get("startsAt")
        total = entry.get("total")
        if not starts_at or total is None:
            continue
        try:
            when = datetime.fromisoformat(str(starts_at))
            value = float(total)
        except (TypeError, ValueError):
            continue
        if not np.isfinite(value):
            continue
        day = by_day.setdefault(when.date().isoformat(), {})
        day.setdefault(when.hour, {})[when.minute] = value
    return by_day


def hourly_from_entries(entries: list[dict]) -> dict[str, list[float]]:
    """Group Tibber-style price entries into complete days by local date.

    Only days with all 24 hours present are returned, since a partial day would
    bias the learned shape. An hour delivered as several 15-minute entries is
    averaged — assigning the entries to one slot per hour, as this previously
    did, silently trained the hourly shape on whichever quarter arrived last,
    the :45 one.
    """
    complete: dict[str, list[float]] = {}
    for day, hours in _entries_by_day(entries).items():
        if len(hours) == HOURS_PER_DAY:
            complete[day] = [
                float(np.mean(list(hours[h].values())))
                for h in range(HOURS_PER_DAY)
            ]
    return complete


def quarters_from_entries(entries: list[dict]) -> dict[str, list[float]]:
    """Complete quarter-resolution days, ``{day: [96 values]}`` (#19).

    A day only qualifies when every hour delivered all four quarter marks —
    hourly data, or a day straddling the MTU switch, trains the hourly shape
    but says nothing about intra-hour structure.
    """
    quarter_marks = tuple(15 * q for q in range(QUARTERS_PER_HOUR))
    complete: dict[str, list[float]] = {}
    for day, hours in _entries_by_day(entries).items():
        if len(hours) == HOURS_PER_DAY and all(
            all(mark in hours[h] for mark in quarter_marks)
            for h in range(HOURS_PER_DAY)
        ):
            complete[day] = [
                hours[h][mark]
                for h in range(HOURS_PER_DAY)
                for mark in quarter_marks
            ]
    return complete
