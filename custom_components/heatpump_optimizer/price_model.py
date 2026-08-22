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


def _profile_index(when: datetime) -> int:
    return PROFILE_WEEKEND if when.weekday() >= 5 else PROFILE_WEEKDAY


@dataclass
class PriceShapeModel:
    """Normalised mean price by hour of day, split weekday/weekend."""

    #: ``shapes[profile][hour]``, each profile normalised to mean 1.0.
    shapes: list[list[float]] = field(
        default_factory=lambda: [[1.0] * HOURS_PER_DAY for _ in range(2)]
    )
    #: Number of complete days folded into each profile.
    days: list[int] = field(default_factory=lambda: [0, 0])

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

    # -- use ----------------------------------------------------------------

    def confidence(self, when: datetime) -> float:
        """How much to trust the shape, between 0 and 1."""
        idx = _profile_index(when)
        return min(1.0, self.days[idx] / SHAPE_CONFIDENCE_DAYS)

    def shape_for(self, when: datetime) -> np.ndarray:
        """Shape for this day, blended towards flat while still uncertain."""
        idx = _profile_index(when)
        shape = np.asarray(self.shapes[idx], dtype=float)
        trust = self.confidence(when)
        return 1.0 + (shape - 1.0) * trust

    def predict(self, when: datetime, level: float) -> float:
        """Expected price at ``when`` given a recent average price ``level``."""
        shape = self.shape_for(when)
        return float(level * shape[when.hour % HOURS_PER_DAY])

    # -- persistence --------------------------------------------------------

    def as_dict(self) -> dict:
        return {"shapes": self.shapes, "days": self.days}

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
        return model

    def summary(self) -> dict:
        return {
            "weekday_days": self.days[PROFILE_WEEKDAY],
            "weekend_days": self.days[PROFILE_WEEKEND],
            "weekday_shape": [round(v, 3) for v in self.shapes[PROFILE_WEEKDAY]],
            "weekend_shape": [round(v, 3) for v in self.shapes[PROFILE_WEEKEND]],
        }


def extend_price_series(
    known: list[float],
    n_steps: int,
    step_start_times: list[datetime],
    model: PriceShapeModel | None,
    *,
    fallback: float = 0.5,
) -> tuple[np.ndarray, np.ndarray]:
    """Extend a price series to ``n_steps``, marking which steps are guessed.

    Returns ``(prices, known_mask)`` where ``known_mask[i]`` is True for steps
    backed by published prices.
    """
    prices = list(known[:n_steps])
    known_count = len(prices)
    mask = np.zeros(n_steps, dtype=bool)
    mask[:known_count] = True

    if known_count >= n_steps:
        return np.asarray(prices[:n_steps], dtype=float), mask

    if known_count == 0:
        return np.full(n_steps, fallback, dtype=float), mask

    # The level to scale the shape by is the mean of the known window, which is
    # the best available estimate of "how expensive electricity is at the
    # moment" and is unaffected by where in the day the known window happens
    # to end.
    level = float(np.mean(prices))
    last_known = float(prices[-1])

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

    return np.asarray(prices[:n_steps], dtype=float), mask


def hourly_from_entries(entries: list[dict]) -> dict[str, list[float]]:
    """Group Tibber-style price entries into complete days by local date.

    Only days with all 24 hours present are returned, since a partial day would
    bias the learned shape.
    """
    by_day: dict[str, dict[int, float]] = {}
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
        by_day.setdefault(when.date().isoformat(), {})[when.hour] = value

    complete: dict[str, list[float]] = {}
    for day, hours in by_day.items():
        if len(hours) == HOURS_PER_DAY:
            complete[day] = [hours[h] for h in range(HOURS_PER_DAY)]
    return complete
