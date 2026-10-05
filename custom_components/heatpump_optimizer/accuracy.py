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
from datetime import datetime, timedelta, timezone
from typing import Any, Deque, Iterable

import numpy as np

from homeassistant.util import dt as dt_util

from .const import HOUSE_HEAT_LOSS_SCALE_MAX, HOUSE_HEAT_LOSS_SCALE_MIN
from .drift import stored_instant
from .drift import utc_elapsed_seconds as utc_elapsed_seconds  # re-export: moved to drift so drift itself can use it
from .payload import Accuracy

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
    #: #1935: a boost overlay (channel or global mode) governed this
    #: interval. The prediction is suppressed on such intervals; the tag
    #: stays so a post-drift recommendation can exclude override rows from
    #: its evidence rather than guessing at windows.
    boost_space: bool = False

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
            "boost_space": self.boost_space,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AccuracySample | None":
        raw = data.get("t")
        if not raw:
            return None
        # The stored-instant rule (F3.1): a sample's stamp loads aware, or
        # the sample is dropped -- a naive one held live is a naive-vs-aware
        # TypeError waiting in whichever consumer next diffs it (P1-rca1).
        # The loader runs under the coordinator, which sees Home Assistant's
        # configured zone; a pure caller with no clock reads naive as UTC.
        when = stored_instant(str(raw), dt_util.DEFAULT_TIME_ZONE)
        if when is None:
            return None

        def num(key: str, lo: float = -np.inf) -> float | None:
            value = data.get(key)
            if value is None:
                return None
            try:
                value = float(value)
            except (TypeError, ValueError, OverflowError):
                return None
            return value if np.isfinite(value) and value >= lo else None

        return cls(
            when=when,
            predicted_power_kw=num("predicted_power_kw", 0.0),  # a plan draws no negative power
            actual_power_kw=num("actual_power_kw"),
            predicted_temp=num("predicted_temp"),
            actual_temp=num("actual_temp"),
            predicted_cost=num("predicted_cost"),
            actual_cost=num("actual_cost"),
            outdoor_temp=num("outdoor_temp"),
            humidity=num("humidity"),
            cop_residual=num("cop_residual"),
            boost_space=bool(data.get("boost_space", False)),
        )


def utc_shift(when: datetime, delta: timedelta) -> datetime:
    """``when + delta`` as real elapsed time, returned in ``when``'s zone.

    ``+`` on a zoned stamp adds wall clock: across the autumn fold a 2 h lead
    lands 3 h later. Adding in UTC and converting back keeps the label a real
    instant (the same walk ``_utc_step_starts`` makes); a naive stamp keeps
    the plain addition.
    """
    if when.tzinfo is None:
        return when + delta
    return (when.astimezone(timezone.utc) + delta).astimezone(when.tzinfo)


#: Lead-time buckets, hours (T5 #16). The margin a plan needs against its
#: own uncertainty grows with how far ahead the promise was made; these
#: are the distances at which that growth is measured.
LEAD_BUCKETS: tuple[float, ...] = (1.0, 3.0, 6.0, 12.0, 24.0)
#: EWMA rate per scored prediction — weeks-scale, like every other slow
#: statistic here.
LEAD_SIGMA_ALPHA = 0.05
#: A matured prediction is matched to the first measurement no more than
#: this far AFTER its target (one-sided window); later than that, the
#: pair says nothing about the lead it was filed under. Callers whose
#: sampling cadence is coarser than this pass their own window, or every
#: bucket that is not a multiple of the cadence starves forever.
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
    #: R9-DIAG-2S (#1936): when the learned state last jumped by a restore.
    #: Every pair before it was predicted by the state the restore replaced,
    #: so a refit fitted across it would apply that state's error to the
    #: restored one -- and an accepted refit's own evidence would be applied
    #: a second time. Persisted, because the samples it fences are.
    evidence_since: datetime | None = None

    def record(self, sample: AccuracySample) -> None:
        self.samples.append(sample)

    def restart_evidence(self, now: datetime) -> None:
        self.evidence_since = now

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

    def score_lead_predictions(
        self,
        now: datetime,
        actual_temp: float,
        window_hours: float | None = None,
    ) -> None:
        """Settle every matured promise against the measured temperature.

        ``window_hours`` is how long after its target a promise still
        counts — at least the default tolerance, and callers scoring on a
        coarse cadence pass that cadence, or promises maturing between
        their ticks would be discarded systematically and the buckets
        whose leads are not multiples of the cadence would never fill.
        """
        if not np.isfinite(actual_temp):
            return
        window = max(
            LEAD_MATCH_TOLERANCE_H,
            float(window_hours) if window_hours is not None else 0.0,
        )
        keep: list[tuple[datetime, float, float]] = []
        for target_time, lead, predicted in self.lead_pending:
            if not np.isfinite(predicted):
                continue
            age_h = utc_elapsed_seconds(now, target_time) / 3600.0
            if age_h < 0.0:
                keep.append((target_time, lead, predicted))
                continue
            if age_h <= window:
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

    def has_lead_history(self) -> bool:
        """Whether any lead bucket has actually scored a pair.

        ``sigma`` answers 0.0 both for "no evidence" and for "the model has
        been perfect", which is the right answer for a safety margin — both
        mean *add nothing*. It is the wrong answer for a band that gets
        DRAWN: a zero-width envelope on a fresh install claims a precision
        nothing has earned. Callers that publish a band ask this first and
        publish nothing at all when it is False.
        """
        # Deliberately the same admission test ``sigma`` applies, so the
        # two can never disagree: a half-restored store carrying sigmas
        # with no counts (or counts with no sigmas) answers False here and
        # 0.0 there, and nothing is drawn.
        return any(
            self.lead_counts.get(lead, 0) > 0 for lead in self.lead_sigma
        )

    def sigma(self, lead_hours: float) -> float:
        """Expected |error| for a promise this far ahead, °C.

        Zero with no history — which is what makes #16 byte-inert on a
        fresh install: no evidence, no margin. Between buckets the nearer
        bucket with evidence answers; beyond the last, the last does.
        """
        best: tuple[float, float, float] | None = None
        for lead, value in self.lead_sigma.items():
            if self.lead_counts.get(lead, 0) <= 0:
                continue
            distance = abs(lead - float(lead_hours))
            # Exact ties resolve to the LONGER bucket: between two equally
            # near answers, the more conservative one.
            if (
                best is None
                or distance < best[0] - 1e-12
                or (abs(distance - best[0]) <= 1e-12 and lead > best[2])
            ):
                best = (distance, value, lead)
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

    def summary(self) -> Accuracy:
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
        since = (
            {"evidence_since": self.evidence_since.isoformat()}
            if self.evidence_since is not None
            else {}
        )
        return {
            **since,
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
        raw_samples = data.get("samples")
        if isinstance(raw_samples, list):
            for raw in raw_samples:
                if not isinstance(raw, dict):
                    continue
                sample = AccuracySample.from_dict(raw)
                if sample is not None:
                    tracker.samples.append(sample)
        elif raw_samples is not None:
            # The decode's corruption barrier, like the sibling loaders': a
            # scalar "samples" once raised out of the loader and the next
            # cycle saved defaults over every learned field (#923).
            _LOGGER.warning(
                "Accuracy store: ignoring non-list 'samples' field (%s); "
                "the other learned fields are unaffected",
                type(raw_samples).__name__,
            )
        raw_sigma = data.get("lead_sigma")
        if isinstance(raw_sigma, dict):
            for key, value in raw_sigma.items():
                try:
                    parsed = float(value)
                except (TypeError, ValueError, OverflowError):
                    continue
                # max(0, NaN) is NaN — a poisoned sigma would reach the
                # comfort bounds as a NaN margin.
                if not np.isfinite(parsed):
                    continue
                try:
                    tracker.lead_sigma[float(key)] = max(0.0, parsed)
                except (TypeError, ValueError, OverflowError):
                    continue
        raw_counts = data.get("lead_counts")
        if isinstance(raw_counts, dict):
            for key, value in raw_counts.items():
                try:
                    if (count := int(value)) >= 1:  # a scored lead has one sample or more
                        tracker.lead_counts[float(key)] = count
                except (TypeError, ValueError, OverflowError):
                    continue
        raw_pending = data.get("lead_pending")
        if isinstance(raw_pending, list):
            for entry in raw_pending[-512:]:
                try:
                    when = datetime.fromisoformat(str(entry[0]))
                    lead = float(entry[1])
                    predicted = float(entry[2])
                except (TypeError, ValueError, OverflowError, IndexError, KeyError):
                    continue
                # A tz-naive timestamp raises on the first aware
                # comparison and, because it raises BEFORE pruning, would
                # brick every subsequent update until the store is hand-
                # edited. This classmethod is the corruption barrier.
                if when.tzinfo is None:
                    continue
                if not np.isfinite(lead) or not np.isfinite(predicted):
                    continue
                tracker.lead_pending.append((when, lead, predicted))
        since = data.get("evidence_since")
        if since:
            tracker.evidence_since = stored_instant(
                str(since), dt_util.DEFAULT_TIME_ZONE
            )
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


#: R9-DIAG-2S (#1936): the settled evidence a heat-loss refit waits for. In
#: the R9-DIAG-1 pre-study a refit one day after the boost days was as wrong
#: as the learner it would replace (0.576 against a true 1.15: the plant
#: state the predictions came from had not re-equilibrated); three settled
#: days answered 1.138.
REFIT_SETTLED_DAYS = 3.0
#: Width of the refit's uncertainty, in percent, published on the advice.
#: The recommendation text states the band as ±7-10 %: the pre-study's null
#: control -- a correct model, no boost -- refit to 0.93, a -7 % floor set
#: by the open-loop slab lag every plan prediction carries, and the honest
#: width around a drifted refit was about ±10 %.
REFIT_BAND_PERCENT = 10


def _refit_start(
    rows: list[AccuracySample], settle: timedelta, since: datetime | None
) -> datetime | None:
    """Where settled evidence begins: after the last boost-tagged pair plus
    ``settle``, and after the last restore, whichever is later."""
    tagged = [s.when for s in rows if s.boost_space]
    bounds = [since] if since is not None else []
    if tagged:
        bounds.append(utc_shift(max(tagged), settle))
    return max(bounds) if bounds else None


def _refit_pair(
    s: AccuracySample, min_delta: float, max_residual: float
) -> tuple[float, float] | None:
    """``(residual, delta_t)`` for a pair the interval learner would admit."""
    pred, act, out = s.predicted_temp, s.actual_temp, s.outdoor_temp
    if s.boost_space or pred is None or act is None or out is None:
        return None
    residual = act - pred
    delta_t = (act + pred) / 2.0 - out
    if delta_t < min_delta or abs(residual) > max_residual:
        return None
    return residual, delta_t


def heat_loss_refit(
    samples: Iterable[AccuracySample],
    *,
    current_scale: float,
    base_u: float,
    capacity: float,
    dt_hours: float,
    min_delta: float,
    max_residual: float,
    settle: timedelta,
    since: datetime | None,
) -> dict[str, Any]:
    """Batch-refit ``house_heat_loss_scale`` from settled prediction pairs.

    The interval learner's Newton relation -- a residual ``e`` over ``dt``
    at an indoor/outdoor difference ``dT`` implies ``dUA = -e*C/(dT*dt)`` --
    pooled over every admitted pair as one step, ``sum(-e*C) / sum(dT*dt)``,
    instead of 2 % a sample for days. ``dT`` is taken about the pair's mean
    indoor temperature, and a pair the learner's own guards would refuse
    (``min_delta``, ``max_residual``) is refused here too.

    The step is taken about ``current_scale`` although each pair was
    predicted under the scale of its own interval, which the learner walks
    meanwhile; the pre-study measured that approximation inside
    ``REFIT_BAND_PERCENT``. ``scale`` stays None until the settled span
    reaches ``REFIT_SETTLED_DAYS`` and holds a day's worth of admitted
    pairs at the ``dt_hours`` cadence.
    """
    rows = list(samples)
    start = _refit_start(rows, settle, since)
    settled = [
        s for s in rows
        if start is None or utc_elapsed_seconds(s.when, start) > 0
    ]
    num = den = 0.0
    pairs = 0
    for s in settled:
        pair = _refit_pair(s, min_delta, max_residual)
        if pair is not None:
            num -= pair[0] * capacity
            den += pair[1] * dt_hours
            pairs += 1
    days = 0.0
    if settled:
        origin = start or utc_shift(
            min(s.when for s in settled), timedelta(hours=-dt_hours)
        )
        days = utc_elapsed_seconds(max(s.when for s in settled), origin) / 86400.0
    scale = None
    if (
        days >= REFIT_SETTLED_DAYS
        and pairs >= 24.0 / max(dt_hours, 1e-6)
        and den > 0.0
        and base_u > 1e-6
    ):
        raw = current_scale + (num / den) / base_u
        if np.isfinite(raw):
            scale = round(float(np.clip(
                raw, HOUSE_HEAT_LOSS_SCALE_MIN, HOUSE_HEAT_LOSS_SCALE_MAX
            )), 3)
    return {
        "scale": scale,
        "band_percent": REFIT_BAND_PERCENT,
        "pairs": pairs,
        "settled_days": round(max(0.0, days), 2),
        "required_days": REFIT_SETTLED_DAYS,
        "settled_since": start.isoformat() if start is not None else None,
    }
