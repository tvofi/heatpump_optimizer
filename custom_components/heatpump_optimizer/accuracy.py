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
import math
import random
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Deque, Iterable, Sequence

import numpy as np

from homeassistant.util import dt as dt_util

from .const import (
    COP_SCALE_MAX,
    COP_SCALE_MIN,
    COP_TRACKING_ERROR_GATE,
    HOUSE_HEAT_LOSS_SCALE_MAX,
    HOUSE_HEAT_LOSS_SCALE_MIN,
    finite_float,
)
from .thermal_model import is_sunlit_interval
from .draw_range import (
    ASK_FOLLOWS,
    ASK_IGNORED,
    ASK_PENDING,
    ASK_UNOBTAINABLE,
    FOLLOW_ASK_SPAN,
    FOLLOW_SLOPE_MIN,
    MIN_SAMPLES,
    WINDOW,
    DrawRange,
    ask_evidence,
    follows_ask,
    power_floor_kw,
)
from .drift import stored_instant, utc_shift
from .drift import utc_elapsed_seconds as utc_elapsed_seconds  # re-export: moved to drift so drift itself can use it
from .payload import Accuracy

_LOGGER = logging.getLogger(__name__)

# How many intervals to keep. At the default 30-minute optimization interval
# this is a fortnight, which is long enough to see a seasonal bias emerge
# without keeping an unbounded amount of state in memory.
HISTORY_LENGTH = 672

#: R9-UX-6 (decision U2): the day-ahead replay keeps the plan's promise for a
#: day, taken from the first plan solved in this local hour -- "the promise is
#: the plan snapshot taken at 00:00" -- and covering this many hours of it.
PROMISE_HOUR = 0
PROMISE_SPAN_H = 24.0
#: Promises kept: today's, and yesterday's, which the replay compares.
PROMISE_DAYS = 2


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
    #: #2223: the interval's measured irradiance, W/m², as the state carried
    #: it when the prediction was made. The drift refit admits night pairs
    #: only -- a sunlit residual carries the solar term's error, and folding
    #: it into the heat-loss scale settles a bias that looks converged. A
    #: sample written before this field existed reads as no sun, the tree's
    #: rule for an unknown irradiance (``None`` is never a measurement).
    solar_radiation: float | None = None
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
            "solar_radiation": self.solar_radiation,
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
            value = finite_float(data.get(key))
            return value if value is not None and value >= lo else None

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
            solar_radiation=num("solar_radiation"),
            cop_residual=num("cop_residual"),
            boost_space=bool(data.get("boost_space", False)),
        )


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
    #: R9-UX-6: the plan's day-ahead promise per local date
    #: (``plan_promise``'s shape), bounded at PROMISE_DAYS.
    promises: dict[str, dict[str, Any]] = field(default_factory=dict)
    #: The metered running draw beside the level the plan asked for: the
    #: same predicted-versus-realised power pair, kept over running intervals
    #: only, and the range it clamps the plan to (``draw_range``).
    draw: DrawRange = field(default_factory=DrawRange)

    def record(self, sample: AccuracySample) -> None:
        self.samples.append(sample)

    def restart_evidence(self, now: datetime) -> None:
        self.evidence_since = now

    # -- the day-ahead replay (R9-UX-6) ---------------------------------------

    def note_promise(
        self,
        solve_time: datetime,
        dt_h: float,
        room: Sequence[float],
        space: Sequence[float],
        dhw: Sequence[float],
        prices: Sequence[float],
    ) -> None:
        """Keep the day's promise from the first plan solved in PROMISE_HOUR.

        A plan solved later in the day is not that day's promise: after a
        restart at noon there is none, rather than one that starts at noon
        and reads as the night's.
        """
        local = dt_util.as_local(solve_time)
        day = local.date().isoformat()
        if local.hour != PROMISE_HOUR or day in self.promises:
            return
        promise = plan_promise(solve_time, dt_h, room, space, dhw, prices)
        if promise is None:
            return
        self.promises[day] = promise
        for old in sorted(self.promises)[:-PROMISE_DAYS]:
            del self.promises[old]

    def replay(self, now: datetime) -> dict[str, Any] | None:
        """Yesterday's promise beside what the samples measured over it."""
        day = (dt_util.as_local(now).date() - timedelta(days=1)).isoformat()
        promise = self.promises.get(day)
        if promise is None:
            return None
        return {"day": day, **promise, "measured": measured_since(
            self.samples, datetime.fromisoformat(promise["start"]))}

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

    def void_pending(self) -> None:
        """Drop every unmatured prediction: the plan that made them stopped
        being what runs, so scoring them would charge the model with errors
        it never made."""
        self.lead_pending.clear()

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
        draw = {"draw": self.draw.as_dict()} if self.draw.samples or self.draw.idle or self.draw.ceiling else {}
        return {
            **since,
            **draw,
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
            "promises": dict(self.promises),
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
        tracker.promises = _stored_promises(data.get("promises"))
        tracker.draw = DrawRange.from_dict(data.get("draw"))
        since = data.get("evidence_since")
        if since:
            tracker.evidence_since = stored_instant(
                str(since), dt_util.DEFAULT_TIME_ZONE
            )
        return tracker


def plan_promise(
    start: datetime,
    dt_h: float,
    room: Sequence[float],
    space: Sequence[float],
    dhw: Sequence[float],
    prices: Sequence[float],
) -> dict[str, Any] | None:
    """The plan's day-ahead promise: room and cumulative cost at each step.

    ``room[i]`` is the trajectory at ``start + i*dt_h`` (index 0 is the solve
    instant, the lead convention ``note_lead_prediction`` files by), and
    ``cost[i]`` is what the plan expected to have spent by then -- each
    step's electrical kW, space plus hot water (``dhw`` empty without a
    tank), times its price times the step, summed. None when the plan cannot
    cover a single step or carries a value that is not a finite number.
    """
    if not (np.isfinite(dt_h) and dt_h > 0):
        return None
    steps = min(int(round(PROMISE_SPAN_H / dt_h)), len(room) - 1, len(space), len(prices))
    if steps < 1 or (dhw and len(dhw) < steps):
        return None
    try:
        kw = np.asarray(space[:steps], dtype=float)
        if dhw:
            kw = kw + np.asarray(dhw[:steps], dtype=float)
        cost = np.concatenate(([0.0], np.cumsum(kw * np.asarray(prices[:steps], dtype=float) * dt_h)))
        temps = np.asarray(room[: steps + 1], dtype=float)
    except (TypeError, ValueError):  # a None step: the plan priced nothing there
        return None
    if not (np.all(np.isfinite(cost)) and np.all(np.isfinite(temps))):
        return None
    return {
        "start": start.isoformat(),
        "step_minutes": round(dt_h * 60.0, 3),
        "room": [round(float(v), 2) for v in temps],
        "cost": [round(float(v), 3) for v in cost],
    }


def measured_since(samples: Iterable[AccuracySample], start: datetime) -> dict[str, Any]:
    """What the samples measured over PROMISE_SPAN_H from ``start``.

    ``t`` is hours since ``start``; ``room`` the measured indoor temperature;
    ``cost`` the cumulative measured cost, or None without a power meter
    (no sample carries one). A sample settles the interval ending at its
    ``when``, so it belongs to the span when ``start < when <= end``. An
    interval the accuracy record skipped (an open window, external heat) is
    missing from both lines.
    """
    end = utc_shift(start, timedelta(hours=PROMISE_SPAN_H))
    span = [s for s in samples if start < s.when <= end]
    hours = [round(utc_elapsed_seconds(s.when, start) / 3600.0, 3) for s in span]
    costs = [s.actual_cost for s in span]
    spent = None
    if any(c is not None for c in costs):
        spent = [round(float(v), 3) for v in np.cumsum([c or 0.0 for c in costs])]
    return {
        "t": hours,
        "room": [None if s.actual_temp is None else round(s.actual_temp, 2) for s in span],
        "cost": spent,
    }


def _stored_promises(raw: Any) -> dict[str, dict[str, Any]]:
    """The persisted promises that parse, newest PROMISE_DAYS of them."""
    if not isinstance(raw, dict):
        return {}
    kept = {str(day): clean for day, value in raw.items()
            if (clean := _stored_promise(value)) is not None}
    return {day: kept[day] for day in sorted(kept)[-PROMISE_DAYS:]}


def _stored_promise(value: Any) -> dict[str, Any] | None:
    """One persisted promise in ``plan_promise``'s shape, or None to drop it."""
    if not isinstance(value, dict):
        return None
    try:
        start = datetime.fromisoformat(str(value["start"]))
        step = float(value["step_minutes"])
        room = [float(v) for v in value["room"]]
        cost = [float(v) for v in value["cost"]]
    except (TypeError, ValueError, KeyError, OverflowError):
        return None
    if (start.tzinfo is None or not (np.isfinite(step) and step > 0)
            or len(room) != len(cost) or len(room) < 2
            or not np.all(np.isfinite(room + cost))):
        return None
    return {"start": start.isoformat(), "step_minutes": step, "room": room, "cost": cost}


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
    """``(residual, delta_t)`` for a pair the interval learner would admit.

    #2223: a sunlit pair is refused, the same dark gate the interval
    learner takes (:func:`thermal_model.is_sunlit_interval`). The refit pools
    the interval learner's own relation, so it inherits the confound the
    gate removes: a residual on a sunny interval carries the aperture's
    error, and the pooled step settles it into the heat-loss scale. A
    sample with no recorded irradiance reads as no sun, which is how the
    tree reads an unknown one everywhere else.
    """
    pred, act, out = s.predicted_temp, s.actual_temp, s.outdoor_temp
    if s.boost_space or pred is None or act is None or out is None:
        return None
    if is_sunlit_interval(s.solar_radiation):
        return None
    residual = act - pred
    delta_t = (act + pred) / 2.0 - out
    if delta_t < min_delta or abs(residual) > max_residual:
        return None
    return residual, delta_t


def _clipped_refit_scale(
    current_scale: float,
    num: float,
    den: float,
    pairs: int,
    days: float,
    base_u: float,
    dt_hours: float,
) -> float | None:
    """The pooled Newton step, or None until the window is evidence.

    Three settled days, and a day's worth of pairs the learner would
    admit, at the interval cadence. Below either, the plant state the
    predictions came from has not re-equilibrated.
    """
    if (
        days < REFIT_SETTLED_DAYS
        or pairs < 24.0 / max(dt_hours, 1e-6)
        or den <= 0.0
        or base_u <= 1e-6
    ):
        return None
    raw = current_scale + (num / den) / base_u
    if not np.isfinite(raw):
        return None
    return round(float(np.clip(
        raw, HOUSE_HEAT_LOSS_SCALE_MIN, HOUSE_HEAT_LOSS_SCALE_MAX
    )), 3)


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
    (``min_delta``, ``max_residual``) is refused here too. So is a pair
    whose interval carried sun (#2223): the interval learner folds dark
    intervals only, and this refit pools that learner's relation.

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
    scale = _clipped_refit_scale(
        current_scale, num, den, pairs, days, base_u, dt_hours
    )
    return {
        "scale": scale,
        "band_percent": REFIT_BAND_PERCENT,
        "pairs": pairs,
        "settled_days": round(max(0.0, days), 2),
        "required_days": REFIT_SETTLED_DAYS,
        "settled_since": start.isoformat() if start is not None else None,
    }


def pairs_interval(elapsed_h: float) -> bool:
    """A pending prediction this many hours old still describes the interval
    that just closed: not a re-run minutes later, not across a restart or gap."""
    return 0.05 <= elapsed_h <= 2.0


# -- the COP learner's last word -------------------------------------------

#: Why the COP learner turned an interval away: one code per guard of
#: ``coordinator._fold_measured_cop``, in its order. Later guards extend the
#: list here rather than spelling a code at their call site.
COP_REFUSED_NO_POWER = "no_measured_power"
COP_REFUSED_FROZEN = "learners_frozen"
COP_REFUSED_DUTY_FLOOR = "duty_floor"
COP_REFUSED_NO_EVIDENCE = "awaiting_draw_evidence"
COP_REFUSED_FROST_BAND = "frost_band"
COP_REFUSED_DISTORTED = "draw_distorted"
COP_REFUSED_TRACKING = "tracking_gate"
COP_REFUSED_OFF_ASK = "draw_off_ask"
COP_REFUSED_BLENDED = "blended_duty"
COP_REFUSED_MODELLED = "modelled_cop"
COP_REFUSED_OBSERVED = "observed_cop"
#: A heat counter (#2261): the COP folds at its span close on the two
#: counters' deltas, so a cycle inside the span folds nothing, and a span
#: whose electric counter was not read at both of its instants has no
#: electrical figure to divide by. A span's own refusals are
#: ``heat_energy``'s ``SPAN_REFUSED_*`` codes.
COP_REFUSED_SPAN_OPEN = "span_open"
COP_REFUSED_UNALIGNED = "unaligned_meters"
#: A thermal power entity is configured and read no heat this interval
#: (unavailable, or negative): the plan's inference does not stand in for it.
COP_REFUSED_NO_HEAT = "no_heat_reading"

#: How far the metered draw may depart from the plan's ask, as a share of the
#: ask, before the interval is judged on ``draw_range.follows_ask``'s evidence
#: (``MeasuredCop.judge_ratio``).
COP_ASK_TOLERANCE = 0.15
#: How long such a departure waits in ``MeasuredCop.held`` for that evidence
#: before it is judged without it: the span of ``draw_range.WINDOW``, a week of
#: the default cycle. A window that has not filled in that time is not filling
#: (a hot-water-only season adds no running sample), so the wait ends.
COP_HOLD_HORIZON_S = 7 * 86400.0
#: How many standard errors of the mean pair contrast ``ScaleDither.verdict``
#: keeps between that mean and ``draw_range.FOLLOW_SLOPE_MIN`` before it
#: decides. It looks after every pair, so the bound prices repeated looks: a
#: draw swinging on its own across the pairs reads either way only by a
#: three-sigma run of the coin.
FOLLOW_BOUND_Z = 3.0
#: The seed of ``ScaleDither.coin``: any fixed one. The coin has to be
#: independent of the draw, not secret, and a fixed seed re-measures alike.
DITHER_SEED = 3662
#: How many probes in a row :meth:`ScaleProbe.reset` may end with no pair
#: read before the next one parks on its first row (``ScaleProbe.voided``):
#: a plan that re-prices its ask against the dithered scale spans the window
#: by the dither's own step, the evidence turns obtainable and resets the
#: probe, and the asks go flat again, without end (carry 6 of
#: R11-OUTSIDE-SELF-SETTING-PUMP; BLOCKED.md departure B1).
PROBE_VOID_CAP = 3

#: Whether this install can measure its COP at all (#2262,
#: R10-HOTFIX-COP-UNMEASURED; ``cop_observability``): only a heat reading over
#: an electrical one, neither of them a vendor's model, measures it. Without a
#: heat reading the ratio of draw to ask still trains the COP scale, but it is
#: the model's own COP scaled by plan tracking, never a measurement.
COP_HEAT_METERED = "heat_metered"
COP_ESTIMATED = "estimated_inputs"
COP_NOT_MEASURABLE = "not_measurable"
COP_NO_ELECTRIC = "no_electric_meter"


def cop_observability(*, electric: bool, measured_heat: bool, estimated: bool) -> str:
    """This install's COP observability: one of the ``COP_*`` states above.

    ``electric``: an electrical figure the COP divides by (the power entity,
    or the electric counter a heat counter's span reads); ``measured_heat``:
    ``probe_install(...).measured_heat``, the heat counter or the thermal power
    entity; ``estimated``: either side is a vendor's estimate.
    """
    if not electric:
        return COP_NO_ELECTRIC
    if not measured_heat:
        return COP_NOT_MEASURABLE
    return COP_ESTIMATED if estimated else COP_HEAT_METERED


@dataclass(frozen=True)
class CopInterval:
    """One interval as the COP fold's tail reads it, and what it was read against.

    What ``MeasuredCop.judge_ratio`` judges, and what it holds when the
    judgement must wait: the plan's ask and the metered draw, the reference
    ``coordinator._cop_reference_curve`` returned, the COP scale the ask was
    priced at, and when. A held interval folds later against ``cop_scale``,
    never the scale of the day it is released: its draw was a reading of the
    plan that scale priced.
    """

    asked_kw: float
    drawn_kw: float
    reference: tuple[float | None, bool, float | None]
    cop_scale: float
    at: datetime

    @property
    def ratio(self) -> float:
        """Metered over asked."""
        return float(self.drawn_kw) / max(self.asked_kw, 1e-6)

    @property
    def heat_ask_kw(self) -> float:
        """The heat the plan asked for: the ask at the scale that priced it."""
        return float(self.asked_kw) * float(self.cop_scale)


@dataclass
class ScaleDither:
    """A randomized two-level experiment on the COP scale: does the draw answer it?

    Under flat asks the heat ask (``CopInterval.heat_ask_kw``) moves only as
    the scale does, and a scale folded from the draw is the draw's own past,
    so no statistic on such rows tells a draw that follows from one that
    swings on its own (fix review 1 of #3662). Here the learner moves the
    scale itself: rows come in pairs, one at each of :meth:`levels`, in an
    order ``coin`` draws per pair. A pair's contrast is the change of log
    drawn between its rows over ``log FOLLOW_ASK_SPAN``, signed by the coin:
    1 for a draw that follows the heat ask, 0 on average for one that does
    not, whatever its own period, because the coin did not see it.

    A slot is one row of a pair: (pair number, coin, second of its pair).
    :meth:`step` hands out the slot each next interval runs under and
    :meth:`take` takes the row that interval produced, one cycle later. The
    step cannot wait for that row, so it hands out the slot after the one
    running; where the running slot's row turns out not to have been read, the
    step hands the missed slot out again and holds it until a row is read
    under it (``holding``): a read cycle that admits no row stretches the pair
    instead of voiding it (BLOCKED.md departure A, approved by the
    orchestrator's ruling on handoff-wip/r11-outside-self-setting-pump-p2).
    """

    coin: random.Random = field(default_factory=lambda: random.Random(DITHER_SEED))
    #: One per completed pair, oldest first.
    contrasts: list[float] = field(default_factory=list)
    #: Rows read since the last :meth:`clear`, in a pair or not.
    rows: int = 0
    #: The pair in flight, (number, coin); None: none, the scale waits at the
    #: base until a row is read.
    pair: tuple[int, int] | None = None
    #: The pair's first row, awaiting its second.
    first: CopInterval | None = None
    #: When the pair in flight was first handed out.
    since: datetime | None = None
    #: The coin of the pair after it, drawn once that pair's first slot is handed out ahead.
    after: int | None = None
    #: The slot of the interval the next row reads, and of the one running after it.
    reading: tuple[int, int, bool] | None = None
    ahead: tuple[int, int, bool] | None = None
    #: ``ahead`` re-runs a slot whose row was not read: hand it out until one is.
    holding: bool = False
    #: A row was read since the last :meth:`step`.
    admitted: bool = False

    def clear(self) -> None:
        """Forget every row and pair; the coin keeps its place."""
        self.contrasts, self.rows = [], 0
        self._void()

    def _void(self) -> None:
        """End the pair in flight: the scale waits at the base until a row is read."""
        self.pair = self.first = self.since = self.after = self.reading = self.ahead = None
        self.holding = self.admitted = False

    @staticmethod
    def levels(base: float) -> tuple[float, float]:
        """The two scales a pair runs at, low then high: ``FOLLOW_ASK_SPAN``
        apart, centred on ``base`` (+-7.2 %), or ``base`` and one full step
        to the open side where the centred pair would pass a clamp."""
        half = math.sqrt(FOLLOW_ASK_SPAN)
        if base / half < COP_SCALE_MIN:
            return base, base * FOLLOW_ASK_SPAN
        if base * half > COP_SCALE_MAX:
            return base / FOLLOW_ASK_SPAN, base
        return base / half, base * half

    def _want(self) -> tuple[int, int, bool] | None:
        """The slot the pair in flight still needs a row for."""
        return None if self.pair is None else (*self.pair, self.first is not None)

    def _next(self, slot: tuple[int, int, bool]) -> tuple[int, int, bool]:
        """The slot after ``slot``: its pair's second, or the next pair's first."""
        number, coin, second = slot
        if not second:
            return number, coin, True
        if self.after is None:
            self.after = self.coin.choice((-1, 1))
        return number + 1, self.after, False

    def step(self, base: float, read: bool, now: datetime) -> float:
        """The scale the next interval runs under.

        ``read``: no frozen or unread cycle came since the last step;
        otherwise the pair in flight is void and the scale waits at ``base``
        until a row is read again. So it is once the pair has run past
        ``COP_HOLD_HORIZON_S`` from its first row (from when it was handed
        out, before one is read, or an unknowable age). Else the slot after
        the one running, unless the running one is a slot handed out again
        because its first run read no row: that one is held.
        """
        admitted, self.admitted = self.admitted, False
        started = self.since if self.first is None else self.first.at
        if not read or (started is not None and not 0.0 <= utc_elapsed_seconds(now, started) <= COP_HOLD_HORIZON_S):
            self._void()
            return base
        if self.pair is None:
            if not admitted:
                return base
            self.pair, self.since = (0, self.coin.choice((-1, 1))), now
        want, running = self._want(), self.ahead
        self.reading = running
        if running == want:
            self.ahead = want if self.holding else self._next(want)
        else:
            self.holding = running is not None and running == self._next(want)
            self.ahead = want
        coin, second = self.ahead[1:]
        if self.since is None:
            self.since = now
        return self.levels(base)[(coin > 0) != second]

    def take(self, row: CopInterval) -> None:
        """Take the row of the interval :meth:`step` set up a cycle ago.

        Only a row read under the slot the pair still needs counts towards
        it; any other (a slot handed out ahead of a row that was not read, or
        a held slot's second run) is a row and nothing more. A pair's second
        row adds its contrast, unless the heat asks of the two rows moved by
        less than ``FOLLOW_SLOPE_MIN`` of the step in the coin's direction: a
        plan that re-priced its ask against the dithered scale kept the heat
        ask flat, and there even a draw that follows would read under the
        threshold. Such a pair is void.
        """
        self.rows, self.admitted = self.rows + 1, True
        if self.reading is None or self.reading != self._want():
            return
        number, coin, second = self.reading
        if not second:
            self.first = row
            return
        first = self.first
        self.pair, self.first, self.since = (number + 1, self.after if self.after is not None else self.coin.choice((-1, 1))), None, None
        self.after = None
        step = math.log(FOLLOW_ASK_SPAN)
        if coin * math.log(first.heat_ask_kw / row.heat_ask_kw) >= FOLLOW_SLOPE_MIN * step:
            self.contrasts.append(coin * math.log(first.drawn_kw / row.drawn_kw) / step)

    def verdict(self) -> str:
        """``ASK_FOLLOWS`` or ``ASK_IGNORED`` once ``MIN_SAMPLES`` rows stand
        in pairs and the mean contrast is ``FOLLOW_BOUND_Z`` standard errors
        clear of ``FOLLOW_SLOPE_MIN`` on that side; ``ASK_PENDING`` until then."""
        if 2 * len(self.contrasts) < MIN_SAMPLES:
            return ASK_PENDING
        mean = float(np.mean(self.contrasts))
        bound = FOLLOW_BOUND_Z * float(np.std(self.contrasts, ddof=1)) / math.sqrt(len(self.contrasts))
        if mean - bound >= FOLLOW_SLOPE_MIN:
            return ASK_FOLLOWS
        return ASK_IGNORED if mean + bound <= FOLLOW_SLOPE_MIN else ASK_PENDING


@dataclass
class ScaleProbe:
    """Whether the draw follows the HEAT ask, ``asked_kw x cop_scale``, and
    the scale owed while that is being found out.

    A heat-led pump's draw answers the scale; a pump that sets its own power
    does not, and its ratio of draw to ask would walk the scale to a clamp
    (owner ruling D4). ``dither`` is the experiment that tells them apart,
    around ``base``, the scale the first admitted row was priced at. While
    ``response`` is pending no admitted row folds (``MeasuredCop.judge_ratio``),
    so the scale moves only as the probe moves it: :meth:`owed_scale` is the
    scale it owes each cycle -- a dither level; ``base`` once it reads follows,
    after ``draw_range.WINDOW`` undecided rows (``parked_at``: no dither until
    ``COP_HOLD_HORIZON_S`` has passed) and on a :meth:`reset`; the configured
    scale once it reads ignored (``restore_due``). ``response`` persists, and
    ``base`` beside it while pending.
    """

    #: ``ASK_PENDING``, then ``ASK_FOLLOWS`` or ``ASK_IGNORED`` once ``dither``
    #: judges it (:meth:`admit`); only :meth:`reset` clears it.
    response: str = ASK_PENDING
    dither: ScaleDither = field(default_factory=ScaleDither)
    #: The scale the probe dithers around and returns to; None: no probe runs.
    base: float | None = None
    #: The scale is owed the configured one: the draw ignores the heat ask, so
    #: every fold since configuration read a draw the scale did not move; or
    #: the probe's first row was read at a clamp, where the scale cannot span.
    restore_due: bool = False
    #: The probe re-seeded at a clamp since its last reset: once, so a
    #: configured scale at a clamp is probed from there instead of re-seeding forever.
    reseeded: bool = False
    #: The scale is owed this one, once: the base of a probe that read
    #: follows, or that a reset ended.
    owed: float | None = None
    #: When the probe stopped undecided; None while it runs.
    parked_at: datetime | None = None
    #: Probes a reset ended with no pair read, in a row (:meth:`reset`): at
    #: ``PROBE_VOID_CAP`` the next one parks on its first row. Not persisted.
    voided: int = 0
    #: The scale :meth:`owed_scale` last returned (None: none it still holds),
    #: and whether it returned one this cycle.
    level: float | None = None
    moved: bool = False

    @property
    def unsettled(self) -> bool:
        """This cycle's interval ran under another scale than the one in
        force: the probe moved the scale this cycle, or still owes its base."""
        return self.moved or self.owed is not None

    def admit(self, row: CopInterval) -> str:
        """Admit ``row``; the verdict after it.

        A latched verdict, or a restore not yet applied, keeps no row. The
        first row read at a clamp (``COP_SCALE_MIN``/``COP_SCALE_MAX``) is
        kept by none: the restore falls due and the probe starts from the
        configured scale, once per reset. Otherwise the first row's scale
        is the probe's ``base`` and ``dither`` reads every row. Its verdict
        ends the probe: follows owes ``base`` back, ignored makes the restore
        due. ``WINDOW`` rows with neither park it (``parked_at``), and a
        parked probe reads nothing.
        """
        if self.response != ASK_PENDING or self.restore_due:
            return self.response
        if self.base is None:
            if not self.reseeded and not COP_SCALE_MIN < row.cop_scale < COP_SCALE_MAX:
                self.reseeded = self.restore_due = True
                return ASK_PENDING
            self.base = float(row.cop_scale)
            if self.voided >= PROBE_VOID_CAP:
                self.parked_at = row.at
        if self.parked_at is not None:
            return ASK_PENDING
        self.dither.take(row)
        self.response = self.dither.verdict()
        if self.response == ASK_PENDING:
            if self.dither.rows < WINDOW:
                return ASK_PENDING
            self.parked_at = row.at
        elif self.response == ASK_FOLLOWS:
            self.owed, self.base = self.base, None
        else:
            self.restore_due, self.base = True, None
        self.dither.clear()
        return self.response

    def owed_scale(self, configured: Callable[[], float], now: datetime, read: bool = True) -> float | None:
        """The COP scale the probe owes this cycle, or None: the scale stands.

        Called once on every cycle a scale may move (past the freeze gate),
        ahead of the cycle's own judgement. ``configured`` reads the configured
        scale, called only where a restore is due; a restore that re-seeds a pending
        probe makes it the probe's ``base``. Then, in order: a scale owed
        once (``owed``); nothing where no probe runs; ``base`` while the
        probe is parked, which re-arms once ``COP_HOLD_HORIZON_S`` has passed
        (or the wait is unknowable, ``parked_at`` ahead of ``now``); else the
        next dither level (``ScaleDither.step``; ``read``: no frozen or unread
        cycle came since). A scale already in force is not returned again
        (``level``); ``moved`` says one was.
        """
        want = self._owed(configured, now, read)
        self.dither.admitted = False  # read by the step alone, and only this cycle
        self.moved = want is not None and want != self.level
        self.level = want
        return want if self.moved else None

    def _owed(self, configured: Callable[[], float], now: datetime, read: bool) -> float | None:
        """:meth:`owed_scale`'s rule: the scale the probe wants in force, or None."""
        if self.restore_due:
            self.restore_due, self.owed, self.level = False, None, None
            scale = float(np.clip(configured(), COP_SCALE_MIN, COP_SCALE_MAX))
            if self.response == ASK_PENDING:
                self.base = scale
            return scale
        if self.owed is not None:
            want, self.owed, self.level = self.owed, None, None
            return want
        if self.base is None:
            return None
        if self.parked_at is not None:
            if 0.0 <= utc_elapsed_seconds(now, self.parked_at) <= COP_HOLD_HORIZON_S:
                return self.base
            self.parked_at, self.voided = None, 0
        return self.dither.step(self.base, read, now)

    def reset(self, measured_heat: bool) -> None:
        """The window's evidence, or measured heat, governs again: the verdict
        and the experiment clear, and a running probe's ``base`` falls owed.
        A due restore survives it, but not measured heat, whose folds are no ratio's.
        A running probe that read no pair counts towards ``PROBE_VOID_CAP``; one that read a pair clears the count."""
        if self.base is not None and self.parked_at is None:
            self.voided = 0 if self.dither.contrasts else self.voided + 1
        self.owed = self.base if self.owed is None else self.owed
        self.base = self.parked_at = None
        self.dither.clear()
        self.response, self.reseeded = ASK_PENDING, False
        self.restore_due = self.restore_due and not measured_heat

    def as_dict(self) -> dict[str, Any]:
        """The verdict, and a running probe's ``base``."""
        return {"scale_response": self.response, "scale_base": self.base}

    @classmethod
    def from_dict(cls, raw: Any) -> ScaleProbe:
        """A stored verdict; absent or unreadable, pending.

        A stored ``ASK_IGNORED`` loads with the restore due, so a save between
        the latch and the restore it owes loses neither (restoring the
        configured scale twice is restoring it once). A pending verdict
        loads the ``base`` stored beside it, where that is a scale the clamps
        admit: the stored COP scale may be a dither level, and
        :meth:`owed_scale` returns to ``base`` on the first cycle. The pairs
        and a parked probe's wait are not stored: the probe starts over.
        """
        probe = cls()
        response = raw.get("scale_response") if isinstance(raw, dict) else None
        if isinstance(response, str) and response in (ASK_FOLLOWS, ASK_IGNORED):
            probe.response, probe.restore_due = response, response == ASK_IGNORED
        elif isinstance(raw, dict):
            base = finite_float(raw.get("scale_base"))
            probe.base = base if base is not None and COP_SCALE_MIN <= base <= COP_SCALE_MAX else None
        return probe


@dataclass
class MeasuredCop:
    """The COP learner's last word: the COP it measured, or why it refused.

    ``cop`` and the curve it was judged against -- ``curve_dhw``, and the tank
    temperature ``dhw_temp`` that curve was evaluated at -- are written together
    by :meth:`record` and nowhere else, and persist and load as one record, so
    the pair the accuracy residual reads cannot be mismatched, a restart
    included. The curve *choice* is kept rather than the modelled value: the
    residual is taken at the settling sample's own outdoor temperature.

    ``at`` is when that COP folded, persisted with it: the latch outlives
    every later refusal, so its age is part of the reading (``None``: a record
    stored before the instant was, whose age is unknown).

    ``refusal`` is one of the ``COP_REFUSED_*`` codes for the latest interval
    (``None`` once one folds). It is not persisted, and diagnostics publish it
    (:func:`diagnostics_view`): the observed-COP sensor is unavailable exactly
    while it is the explanation, and Home Assistant hides an unavailable
    entity's attributes.

    ``held`` is the departures from the ask waiting for the evidence that
    judges them, and every interval ``probe`` admitted while its verdict was
    pending: :meth:`judge_ratio` appends, :meth:`release` is the only way
    out. Neither it nor ``ratio_ewma`` is persisted: a restart drops both.

    ``probe`` answers what the window's evidence cannot where it is
    unobtainable on an install with no measured heat (:meth:`_admits`):
    whether the draw follows the HEAT ask (:class:`ScaleProbe`, whose verdict
    ``scale_response`` reads). While it is pending no admitted interval
    folds, and :meth:`owed_scale` is the scale it owes each cycle.
    """

    cop: float | None = None
    curve_dhw: bool = False
    dhw_temp: float | None = None
    refusal: str | None = None
    at: datetime | None = None
    #: Intervals a learner freeze refused since start (not persisted): the
    #: heat-pump grade's no-grade evidence (``coordinator.machine_evidence``).
    frozen_refusals: int = 0

    #: The walking metered/asked ratio (:meth:`walk_ratio`); ``None`` before
    #: the first interval, which is judged against 1.0.
    ratio_ewma: float | None = None
    #: Intervals awaiting ``draw_range.ask_evidence`` or ``probe``'s verdict, oldest first.
    held: Deque[CopInterval] = field(default_factory=deque)
    #: The heat-ask probe: its verdict, and the scale it owes meanwhile.
    probe: ScaleProbe = field(default_factory=ScaleProbe)

    @property
    def scale_response(self) -> str:
        """``probe``'s verdict: ``ASK_PENDING``, ``ASK_FOLLOWS`` or ``ASK_IGNORED``."""
        return self.probe.response

    @staticmethod
    def judge_floor(asked_kw: float, drawn_kw: float | None, params: Any, draw: DrawRange | None = None) -> str | None:
        """``COP_REFUSED_DUTY_FLOOR`` when the ask or the draw is under the duty
        floor (``draw_range.power_floor_kw`` on the window ``draw``), else None;
        None with no draw (a heat counter's install, judged at its span close)."""
        if drawn_kw is not None and min(asked_kw, drawn_kw) < power_floor_kw(draw, params):
            return COP_REFUSED_DUTY_FLOOR
        return None

    def walk_ratio(self, ratio: float) -> float:
        """Walk the metered/asked EWMA by one interval; the value BEFORE it.

        Seeded at 1.0, the model's own expectation. :meth:`judge_ratio` gates
        an interval against the returned value, so a first-sample blip cannot
        vouch for itself; it walks on every sample, accepted or not, so a
        persistent efficiency shift can still teach.
        """
        before = 1.0 if self.ratio_ewma is None else self.ratio_ewma
        self.ratio_ewma = 0.9 * before + 0.1 * ratio
        return before

    @staticmethod
    def _base_folds(row: CopInterval, params: Any) -> bool:
        """The pre-evidence rule for a departure: the ask and the draw both
        clear the nameplate third (``nameplate_power_floor_kw``)."""
        return bool(min(row.asked_kw, row.ratio * row.asked_kw) >= params.nameplate_power_floor_kw)

    @staticmethod
    def _admits(state: str, draw: DrawRange | None, measured_heat: bool) -> bool:
        """Whether an interval is judged on the heat ask (``scale_response``):
        the window's evidence is unobtainable, a window exists, and the
        install measures no heat (``probe_install(...).measured_heat``)."""
        return state == ASK_UNOBTAINABLE and draw is not None and not measured_heat

    def owed_scale(self, configured: Callable[[], float], now: datetime) -> float | None:
        """The COP scale ``probe`` owes this cycle, or None (``ScaleProbe.owed_scale``).
        A frozen or unread cycle since the last one (``refusal``) read no interval."""
        return self.probe.owed_scale(configured, now, self.refusal not in (COP_REFUSED_FROZEN, COP_REFUSED_NO_POWER))

    def judge_ratio(
        self, ewma: float, row: CopInterval, params: Any, draw: DrawRange | None, measured_heat: bool = False
    ) -> str | None:
        """The ratio gates' refusal for the interval ``row``, or None; a refusal is logged."""
        refusal = self._judge_ratio(ewma, row, params, draw, measured_heat)
        if refusal is not None:
            _LOGGER.debug(
                "Skipping COP sample (%s): commanded %.2f kW vs measured %.2f kW "
                "against the running ratio %.2f -- not an efficiency reading",
                refusal, row.asked_kw, row.drawn_kw, ewma,
            )
        return refusal

    def _judge_ratio(
        self, ewma: float, row: CopInterval, params: Any, draw: DrawRange | None, measured_heat: bool
    ) -> str | None:
        """:meth:`judge_ratio`'s rule.

        ``ewma`` is the walking ratio BEFORE this interval (:meth:`walk_ratio`).
        ``COP_REFUSED_TRACKING``: a one-off blip off the walking ratio
        (v4.0.5). Evidence that the draw does not follow the ask
        (``draw_range.ask_evidence``) refuses every interval, within the
        tolerance or not (``COP_REFUSED_OFF_ASK``: a pump that sets its own
        power, whose ratio would fold as a COP shift, #2262). A departure
        beyond ``COP_ASK_TOLERANCE`` is then judged on that evidence: it folds
        where the draw follows the ask (an efficiency shift). While the
        evidence is pending it is HELD, not folded -- ``row`` joins ``held``,
        the interval reads ``COP_REFUSED_NO_EVIDENCE``, and :meth:`release`
        folds or drops it once the evidence says which, so a pump that sets
        its own power folds no departure while the window fills. Where the
        evidence is unobtainable nothing would ever release it, so it folds
        only where base would have -- :meth:`_base_folds` -- and is otherwise
        ``COP_REFUSED_NO_EVIDENCE``: an install whose asks never span
        ``FOLLOW_ASK_SPAN`` keeps base's reach for them. Where :meth:`_admits`
        holds, the interval joins the probe instead: under ``ASK_IGNORED`` it
        reads ``COP_REFUSED_OFF_ASK``, under ``ASK_FOLLOWS`` it folds, and
        while ``ASK_PENDING`` it is held, whatever its ratio: the draw must
        not move the scale it is judged against. So is an interval judged
        while the probe is ``unsettled``, by whichever evidence: it ran under
        another scale than the one in force, and folds from the hold against
        its own.
        """
        ratio = row.ratio
        if abs(ratio - ewma) / max(ewma, 1e-6) > COP_TRACKING_ERROR_GATE:
            return COP_REFUSED_TRACKING
        state = ask_evidence(draw)
        if state == ASK_IGNORED:
            # #2262: a draw the evidence shows does not follow its ask is no
            # efficiency reading at ANY ratio; one within the tolerance only
            # happened to land near the ask.
            return COP_REFUSED_OFF_ASK
        verdict = self.probe.admit(row) if self._admits(state, draw, measured_heat) else None
        if verdict == ASK_IGNORED:
            return COP_REFUSED_OFF_ASK
        if verdict == ASK_PENDING or self.probe.unsettled:
            self.held.append(row)
            return COP_REFUSED_NO_EVIDENCE
        if verdict == ASK_FOLLOWS:
            return None
        if abs(ratio - 1.0) <= COP_ASK_TOLERANCE or state == ASK_FOLLOWS:
            return None
        if state == ASK_PENDING:
            self.held.append(row)
            return COP_REFUSED_NO_EVIDENCE
        return None if self._base_folds(row, params) else COP_REFUSED_NO_EVIDENCE

    def release(
        self, draw: DrawRange | None, params: Any, now: datetime, measured_heat: bool = False
    ) -> list[CopInterval]:
        """The held intervals to fold now, oldest first; the one place one is judged.

        Called ahead of a cycle's own judgement, never on a frozen or unread cycle. On evidence
        the hold empties: every row folds where the draw follows the ask, none
        where it does not. Where the evidence is unobtainable it empties by
        base's rule (:meth:`_base_folds`). While the evidence is pending a row
        waits, and leaves by base's rule in two cases only: it has waited past
        ``COP_HOLD_HORIZON_S`` (or its age is unknowable, stamped ahead of
        ``now``), or the hold is over ``draw_range.WINDOW`` rows and it is the
        oldest. So every held row leaves, and none that base folded is lost
        for want of evidence that never came.

        The state is read first. Where :meth:`_admits` holds, the probe's
        verdict stands in for the evidence: every row folds once it reads
        ``ASK_FOLLOWS``, none under ``ASK_IGNORED``, and while it is pending
        each waits as above -- but a row that leaves the wait is dropped, not
        folded by base's rule: nothing folds on a pending verdict. Where it
        does not hold, the probe resets (``ScaleProbe.reset``) and the arms
        above run as before. Either way no row leaves while the probe still
        owes a scale (``ScaleProbe.owed``): the folds would start from the
        scale it is about to replace.
        """
        state, rows = ask_evidence(draw), list(self.held)
        self.held.clear()
        if probed := self._admits(state, draw, measured_heat):
            state = self.scale_response
        else:
            self.probe.reset(measured_heat)
        if waits := self.probe.owed is not None or (probed and state == ASK_PENDING):
            state = ASK_PENDING
        if state == ASK_FOLLOWS:
            return rows
        if state == ASK_IGNORED:
            return []
        if state == ASK_PENDING:
            over, due = len(rows) - WINDOW, []
            for i, row in enumerate(rows):
                if i >= over and 0.0 <= utc_elapsed_seconds(now, row.at) <= COP_HOLD_HORIZON_S:
                    self.held.append(row)
                else:
                    due.append(row)
            rows = due
        return [r for r in rows if not waits and self._base_folds(r, params)]

    def record(self, cop: float, curve_dhw: bool, dhw_temp: float | None, at: datetime) -> None:
        """One folded interval's COP, its curve and when it folded, together."""
        self.cop, self.curve_dhw, self.dhw_temp = round(float(cop), 2), curve_dhw, dhw_temp
        self.at = at

    def residual(self, since: datetime, outdoor: float | None, model: Any) -> float | None:
        """Observed minus modelled COP for an interval that began at ``since``.

        ``None`` unless the latch folded after ``since``: a COP latched on an
        earlier interval re-subtracted on every later sample is a function of
        outdoor temperature alone (#2262), not a reading of this one. The
        modelled curve is the one the observation was referenced to; no
        outdoor temperature, no residual.
        """
        if outdoor is None or self.cop is None or self.at is None or utc_elapsed_seconds(self.at, since) <= 0.0:
            return None
        if self.curve_dhw and self.dhw_temp is not None:
            modelled = model.compute_cop_dhw(outdoor, self.dhw_temp)
        else:
            modelled = model.compute_cop(outdoor)
        return round(float(self.cop) - float(modelled), 3)

    def as_dict(self) -> dict[str, Any]:
        """The measurement and what ``probe`` stores; a refusal describes one interval."""
        at = None if self.at is None else self.at.isoformat()
        return {"cop": self.cop, "curve_dhw": self.curve_dhw, "dhw_temp": self.dhw_temp, "at": at, **self.probe.as_dict()}

    @classmethod
    def from_dict(cls, raw: Any) -> MeasuredCop:
        """A stored record, with the probe's part read apart from it
        (``ScaleProbe.from_dict``): absent or unreadable, the verdict is
        pending and the measurement stands."""
        record = cls._stored_measurement(raw)
        record.probe = ScaleProbe.from_dict(raw)
        return record

    @classmethod
    def _stored_measurement(cls, raw: Any) -> MeasuredCop:
        """A stored measurement, or none: an unreadable field drops the record whole.

        The record is the unit: a COP without a readable curve would be judged
        against the wrong one. A COP the learner could not have written (not
        finite, or under its own 0.1 refusal once rounded) is unreadable.
        """
        try:
            cop, dhw = float(raw["cop"]), raw.get("curve_dhw") is True
            temp = None if raw.get("dhw_temp") is None else float(raw["dhw_temp"])
            at = None if raw.get("at") is None else stored_instant(raw["at"])
        except (TypeError, ValueError, KeyError, AttributeError, OverflowError):
            return cls()
        if not np.isfinite(cop) or cop < 0.1 or (dhw and temp is None):
            return cls()
        if (temp is not None and not np.isfinite(temp)) or (raw.get("at") is not None and at is None):
            return cls()
        return cls(cop=cop, curve_dhw=dhw, dhw_temp=temp, at=at)


def diagnostics_view(record: MeasuredCop, params: Any, draw: DrawRange | None) -> dict[str, Any]:
    """The COP learner's diagnostics: its last refusal and the floor it judged by.

    ``params`` is the live ``ThermalParameters``, ``draw`` the running-draw
    window. ``power_floor_kw`` is ``draw_range.power_floor_kw`` on that window,
    the floor the COP and flow-lift folds read (the configured
    ``flow_lift_power_floor_kw``, capped by the metered running draw) -- not
    the optimizer's ``duty_floor_kw``, a different quantity;
    ``draw_follows_ask`` is the evidence a departure from the ask is judged on
    (None: none yet), and ``held_intervals`` counts the departures waiting for
    it (``MeasuredCop.held``): with ``last_refusal`` at
    ``COP_REFUSED_NO_EVIDENCE``, a count above zero says the interval is held
    for replay rather than refused; ``scale_response`` is whether the draw
    follows the heat ask where that evidence is unobtainable.
    """
    return {
        "last_refusal": record.refusal,
        "measured_cop": record.cop,
        "measured_at": None if record.at is None else record.at.isoformat(),
        "power_floor_kw": round(power_floor_kw(draw, params), 3),
        "draw_follows_ask": follows_ask(draw),
        "held_intervals": len(record.held),
        "scale_response": record.scale_response,
    }
