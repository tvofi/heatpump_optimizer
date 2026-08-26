"""Learned heat-curve bias for the ECL110 displace (item 2, v4.0.0 T4b).

Most ECL110 installs run a heat curve set once, conservatively, by an
installer who was never coming back: a curve hot enough for the coldest
day the house will ever see, every day. The optimizer already commands a
displace on top of that curve, so the machinery to correct it exists —
what is missing is the standing correction: "this curve runs 2 K hotter
than this house needs".

Shaped like ``comfort_learning.py`` — evidence in, one slow adjustment
out, everything persisted — with one deliberate asymmetry copied from
every safety-critical trim in this program:

* **Down is slow.** The bias creeps toward more negative (cooler) by at
  most ``MAX_DOWN_PER_WEEK`` per week, and only on evidence: days where
  every zone held comfortably above its floor while the displace was
  already being driven down.
* **Up is instant and total.** Any comfort miss — a zone at or under its
  floor while the bias was applied — resets the bias to 0 on the spot.
  A learner that undershoots comfort and then negotiates about it has
  chosen the wrong failure mode.

The bias is clamped to [−4, 0] K: it may only ever *cool* a curve that
was set too hot, never paper over an undersized one by heating.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime

import numpy as np

_LOGGER = logging.getLogger(__name__)

#: The bias can only cool an over-hot curve, never heat. Kelvin.
BIAS_MIN = -4.0
BIAS_MAX = 0.0
#: Fastest allowed creep toward cooler, K per week.
MAX_DOWN_PER_WEEK = 0.5
#: A day counts as comfortable when every zone kept this margin above
#: its floor throughout, °C.
COMFORT_MARGIN_C = 0.3
#: Comfortable days needed per downward step.
DAYS_PER_STEP = 3
#: One downward step, K. 3 days x (0.5/7) rounds to ~0.2.
STEP_K = 0.2


@dataclass
class CurveLearner:
    """The standing displace bias and the evidence for it."""

    bias: float = 0.0
    comfortable_days: int = 0
    resets: int = 0
    _last_day: str = ""
    _last_step_at: str = ""

    def record_day(
        self, now: datetime, worst_margin_c: float | None
    ) -> None:
        """Fold one day's comfort outcome in. Once per calendar day.

        ``worst_margin_c`` is the day's minimum of (zone temperature −
        comfort floor) across zones — the caller computes it from the
        same bounds the optimizer enforced.
        """
        day = now.date().isoformat()
        if day == self._last_day:
            return
        self._last_day = day
        if worst_margin_c is None:
            return
        if worst_margin_c <= 0.0:
            self.record_miss(now, worst_margin_c)
            return
        if worst_margin_c < COMFORT_MARGIN_C:
            # Held, but with nothing to spare: no evidence either way.
            self.comfortable_days = 0
            return
        self.comfortable_days += 1
        if self.comfortable_days >= DAYS_PER_STEP:
            self._step_down(now)

    def record_miss(self, now: datetime, worst_margin_c: float) -> None:
        """A zone touched its floor: the bias surrenders immediately.

        Full reset rather than a step back up — the miss proves the
        current bias wrong, and the safe restart point is the installer's
        own curve.
        """
        self.comfortable_days = 0
        if self.bias >= BIAS_MAX:
            return
        _LOGGER.warning(
            "Comfort miss (margin %.2f °C) with curve bias %.1f K applied; "
            "bias reset to 0",
            worst_margin_c,
            self.bias,
        )
        self.bias = 0.0
        self.resets += 1

    def _step_down(self, now: datetime) -> None:
        # The weekly rate cap holds even if the caller's day counting is
        # generous: at most MAX_DOWN_PER_WEEK of movement per 7 days.
        if self._last_step_at:
            try:
                last = datetime.fromisoformat(self._last_step_at)
                days = (now - last).total_seconds() / 86400.0
                max_now = MAX_DOWN_PER_WEEK * max(days, 0.0) / 7.0
            except ValueError:
                max_now = STEP_K
        else:
            max_now = STEP_K
        step = min(STEP_K, max_now)
        if step <= 0.0:
            return
        self.bias = float(np.clip(self.bias - step, BIAS_MIN, BIAS_MAX))
        self.comfortable_days = 0
        self._last_step_at = now.isoformat()
        _LOGGER.info("Curve bias stepped to %.2f K", self.bias)

    def summary(self) -> dict:
        return {
            "bias_k": round(self.bias, 2),
            "comfortable_days": self.comfortable_days,
            "resets": self.resets,
        }

    def as_dict(self) -> dict:
        return {
            "bias": round(self.bias, 3),
            "comfortable_days": self.comfortable_days,
            "resets": self.resets,
            "last_day": self._last_day,
            "last_step_at": self._last_step_at,
        }

    @classmethod
    def from_dict(cls, data: dict | None) -> "CurveLearner":
        learner = cls()
        if not isinstance(data, dict):
            return learner
        try:
            learner.bias = float(np.clip(data.get("bias", 0.0), BIAS_MIN, BIAS_MAX))
        except (TypeError, ValueError):
            learner.bias = 0.0
        try:
            learner.comfortable_days = max(0, int(data.get("comfortable_days", 0)))
        except (TypeError, ValueError):
            learner.comfortable_days = 0
        try:
            learner.resets = max(0, int(data.get("resets", 0)))
        except (TypeError, ValueError):
            learner.resets = 0
        learner._last_day = str(data.get("last_day", ""))
        learner._last_step_at = str(data.get("last_step_at", ""))
        return learner
