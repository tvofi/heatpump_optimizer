"""Closed-loop accuracy: comparing what was predicted with what happened.

Nothing verified the savings claims. ``PredictedSavingsSensor`` published a
prediction with no realised counterpart, and there was no way to detect model
drift beyond the learners' own guard thresholds — which are designed to reject
outliers, not to notice a slow bias.

This module records, per interval, what the plan said would happen and what the
sensors say did happen, and rolls that into published accuracy figures. Three
things fall out:

* **Drift becomes visible** instead of showing up months later as a comfort
  complaint.
* **The defrost derate has something to learn from** (item 14), since the
  delivered-versus-predicted thermal ratio is exactly its training signal.
* **The savings figure stops being a simulation result.** Together with the
  replay harness in the test suite, the claim becomes an observed one.

Everything degrades cleanly without a measured power entity: temperature
accuracy is still recorded, only the power and cost columns go missing.
"""
from __future__ import annotations

import logging
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Deque

import numpy as np

_LOGGER = logging.getLogger(__name__)

# How many intervals to keep. At the default 30-minute optimization interval
# this is a fortnight, which is long enough to see a seasonal bias emerge
# without keeping an unbounded amount of state in memory.
HISTORY_LENGTH = 672


@dataclass
class AccuracySample:
    """One interval of predicted-versus-realised evidence."""

    when: datetime
    predicted_power_kw: float | None = None
    actual_power_kw: float | None = None
    predicted_temp: float | None = None
    actual_temp: float | None = None
    predicted_cost: float | None = None
    actual_cost: float | None = None
    outdoor_temp: float | None = None
    humidity: float | None = None
    #: Observed minus modelled COP for the interval (v4.0.0 T4a, #42's
    #: snapshot tags and #12's health watch both read it). None whenever a
    #: power meter or the model's figure was missing.
    cop_residual: float | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "t": self.when.isoformat(),
            "predicted_power_kw": self.predicted_power_kw,
            "actual_power_kw": self.actual_power_kw,
            "predicted_temp": self.predicted_temp,
            "actual_temp": self.actual_temp,
            "predicted_cost": self.predicted_cost,
            "actual_cost": self.actual_cost,
            "outdoor_temp": self.outdoor_temp,
            "humidity": self.humidity,
            "cop_residual": self.cop_residual,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AccuracySample | None":
        raw = data.get("t")
        if not raw:
            return None
        try:
            when = datetime.fromisoformat(str(raw))
        except ValueError:
            return None

        def num(key: str) -> float | None:
            value = data.get(key)
            if value is None:
                return None
            try:
                value = float(value)
            except (TypeError, ValueError):
                return None
            return value if np.isfinite(value) else None

        return cls(
            when=when,
            predicted_power_kw=num("predicted_power_kw"),
            actual_power_kw=num("actual_power_kw"),
            predicted_temp=num("predicted_temp"),
            actual_temp=num("actual_temp"),
            predicted_cost=num("predicted_cost"),
            actual_cost=num("actual_cost"),
            outdoor_temp=num("outdoor_temp"),
            humidity=num("humidity"),
            cop_residual=num("cop_residual"),
        )


#: Lead-time buckets, hours (T5 #16). The margin a plan needs against its
#: own uncertainty grows with how far ahead the promise was made; these
#: are the distances at which that growth is measured.
LEAD_BUCKETS: tuple[float, ...] = (1.0, 3.0, 6.0, 12.0, 24.0)
#: EWMA rate per scored prediction — weeks-scale, like every other slow
#: statistic here.
LEAD_SIGMA_ALPHA = 0.05
#: A matured prediction is matched to a measurement within this window;
#: further away, the pair says nothing about the lead it was filed under.
LEAD_MATCH_TOLERANCE_H = 0.5


@dataclass
class AccuracyTracker:
    """Rolling record of prediction quality."""

    samples: Deque[AccuracySample] = field(
        default_factory=lambda: deque(maxlen=HISTORY_LENGTH)
    )
    #: T5 #16 — per-lead-bucket EWMA of |realised − predicted| room
    #: temperature, °C, and how many pairs each has scored.
    lead_sigma: dict[float, float] = field(default_factory=dict)
    lead_counts: dict[float, int] = field(default_factory=dict)
    #: Predictions waiting for their moment of truth:
    #: (target_time, lead_hours, predicted_temp). Bounded by construction —
    #: each solve files one entry per bucket and entries expire when scored
    #: or overdue.
    lead_pending: list[tuple[datetime, float, float]] = field(
        default_factory=list
    )

    def record(self, sample: AccuracySample) -> None:
        self.samples.append(sample)

    # -- lead-time error (T5 #16) --------------------------------------------

    def note_lead_prediction(
        self, target_time: datetime, lead_hours: float, predicted_temp: float
    ) -> None:
        """File one plan promise: 'at target_time the room will be X'."""
        if not np.isfinite(predicted_temp):
            return
        self.lead_pending.append(
            (target_time, float(lead_hours), float(predicted_temp))
        )
        # A hard cap far above normal fill (5 buckets × 48 half-hour
        # solves), purely so corrupt state cannot grow without bound.
        del self.lead_pending[:-512]

    def score_lead_predictions(self, now: datetime, actual_temp: float) -> None:
        """Settle every matured promise against the measured temperature."""
        if not np.isfinite(actual_temp):
            return
        keep: list[tuple[datetime, float, float]] = []
        for target_time, lead, predicted in self.lead_pending:
            age_h = (now - target_time).total_seconds() / 3600.0
            if age_h < 0.0:
                keep.append((target_time, lead, predicted))
                continue
            if age_h <= LEAD_MATCH_TOLERANCE_H:
                err = abs(float(actual_temp) - predicted)
                prev = self.lead_sigma.get(lead)
                self.lead_sigma[lead] = (
                    err
                    if prev is None
                    else (1.0 - LEAD_SIGMA_ALPHA) * prev
                    + LEAD_SIGMA_ALPHA * err
                )
                self.lead_counts[lead] = self.lead_counts.get(lead, 0) + 1
            # Matured entries never survive, scored or stale: a promise
            # that missed its measurement window is unverifiable.
        self.lead_pending = keep

    def sigma(self, lead_hours: float) -> float:
        """Expected |error| for a promise this far ahead, °C.

        Zero with no history — which is what makes #16 byte-inert on a
        fresh install: no evidence, no margin. Between buckets the nearer
        bucket with evidence answers; beyond the last, the last does.
        """
        best: tuple[float, float] | None = None
        for lead, value in self.lead_sigma.items():
            if self.lead_counts.get(lead, 0) <= 0:
                continue
            distance = abs(lead - float(lead_hours))
            if best is None or distance < best[0]:
                best = (distance, value)
        return float(best[1]) if best is not None else 0.0

    # -- metrics ------------------------------------------------------------

    def _paired(self, predicted: str, actual: str) -> tuple[np.ndarray, np.ndarray]:
        pred = []
        act = []
        for sample in self.samples:
            p = getattr(sample, predicted)
            a = getattr(sample, actual)
            if p is None or a is None:
                continue
            pred.append(p)
            act.append(a)
        return np.asarray(pred, dtype=float), np.asarray(act, dtype=float)

    def temperature_mae(self) -> float | None:
        """Mean absolute error of the predicted indoor temperature, °C."""
        pred, act = self._paired("predicted_temp", "actual_temp")
        if pred.size == 0:
            return None
        return round(float(np.mean(np.abs(pred - act))), 3)

    def temperature_bias(self) -> float | None:
        """Signed mean error. The sign is what identifies drift.

        A mean absolute error alone cannot distinguish random noise from a
        model that is consistently half a degree optimistic, and it is the
        second that matters.
        """
        pred, act = self._paired("predicted_temp", "actual_temp")
        if pred.size == 0:
            return None
        return round(float(np.mean(pred - act)), 3)

    def power_ratio(self) -> float | None:
        """Realised electrical draw over predicted, averaged."""
        pred, act = self._paired("predicted_power_kw", "actual_power_kw")
        usable = pred > 0.05
        if not np.any(usable):
            return None
        return round(float(np.mean(act[usable] / pred[usable])), 3)

    def cost_accuracy(self) -> float | None:
        """Percentage error of predicted cost against realised, signed."""
        pred, act = self._paired("predicted_cost", "actual_cost")
        if pred.size == 0:
            return None
        total_pred = float(np.sum(pred))
        total_act = float(np.sum(act))
        if abs(total_act) < 1e-6:
            return None
        return round((total_pred - total_act) / total_act * 100.0, 2)

    def realised_cost(self) -> float:
        return round(
            float(sum(s.actual_cost or 0.0 for s in self.samples)), 2
        )

    def predicted_cost(self) -> float:
        return round(
            float(sum(s.predicted_cost or 0.0 for s in self.samples)), 2
        )

    def trust(self) -> float:
        """A 0-1 signal for how far the model is currently to be believed.

        Used to damp the learners: when the model is badly wrong, its own
        residual-based corrections are the least reliable. Derived from the
        temperature error, which is the one signal every install has.
        """
        mae = self.temperature_mae()
        if mae is None:
            return 0.5
        # A quarter-degree average error is excellent; two degrees is useless.
        return float(np.clip(1.0 - (mae - 0.25) / 1.75, 0.0, 1.0))

    def summary(self) -> dict[str, Any]:
        return {
            "samples": len(self.samples),
            "temperature_mae": self.temperature_mae(),
            "temperature_bias": self.temperature_bias(),
            "power_ratio": self.power_ratio(),
            "cost_error_percent": self.cost_accuracy(),
            "realised_cost": self.realised_cost(),
            "predicted_cost": self.predicted_cost(),
            "trust": round(self.trust(), 2),
            # T5 #16, additive: the expected |error| per promise distance.
            "lead_sigma": {
                f"{lead:g}h": round(value, 3)
                for lead, value in sorted(self.lead_sigma.items())
                if self.lead_counts.get(lead, 0) > 0
            },
        }

    # -- persistence --------------------------------------------------------

    def as_dict(self) -> dict[str, Any]:
        # Only the most recent slice is persisted; the whole history is not
        # worth the storage write on every interval.
        recent = list(self.samples)[-192:]
        return {
            "samples": [s.as_dict() for s in recent],
            # T5 #16, additive keys. The pending promises persist too, or
            # every restart would silently discard up to a day of filed
            # predictions and the long buckets would starve.
            "lead_sigma": {
                str(lead): round(value, 4)
                for lead, value in self.lead_sigma.items()
            },
            "lead_counts": {
                str(lead): int(count)
                for lead, count in self.lead_counts.items()
            },
            "lead_pending": [
                [t.isoformat(), lead, round(pred, 3)]
                for t, lead, pred in self.lead_pending[-512:]
            ],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "AccuracyTracker":
        tracker = cls()
        if not isinstance(data, dict):
            return tracker
        for raw in data.get("samples", []) or []:
            if not isinstance(raw, dict):
                continue
            sample = AccuracySample.from_dict(raw)
            if sample is not None:
                tracker.samples.append(sample)
        raw_sigma = data.get("lead_sigma")
        if isinstance(raw_sigma, dict):
            for key, value in raw_sigma.items():
                try:
                    tracker.lead_sigma[float(key)] = max(0.0, float(value))
                except (TypeError, ValueError):
                    continue
        raw_counts = data.get("lead_counts")
        if isinstance(raw_counts, dict):
            for key, value in raw_counts.items():
                try:
                    tracker.lead_counts[float(key)] = max(0, int(value))
                except (TypeError, ValueError):
                    continue
        raw_pending = data.get("lead_pending")
        if isinstance(raw_pending, list):
            for entry in raw_pending[-512:]:
                try:
                    when = datetime.fromisoformat(str(entry[0]))
                    tracker.lead_pending.append(
                        (when, float(entry[1]), float(entry[2]))
                    )
                except (TypeError, ValueError, IndexError):
                    continue
        return tracker


def delivered_ratio(sample: AccuracySample) -> float | None:
    """Thermal output actually delivered, relative to what was predicted.

    Inverted from the power ratio on purpose: drawing *more* electricity than
    predicted for the same temperature outcome means the unit delivered *less*
    heat per kWh, which is what the defrost derate models.
    """
    if sample.predicted_power_kw is None or sample.actual_power_kw is None:
        return None
    if sample.predicted_power_kw <= 0.05 or sample.actual_power_kw <= 0.05:
        return None
    return float(sample.predicted_power_kw / sample.actual_power_kw)
