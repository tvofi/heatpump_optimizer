"""Learned capacity and efficiency derate in the frosting band.

The COP model is a clean monotonic function of outdoor temperature. Real
air-to-water units are not: between roughly 0 and +5 °C in humid air, frost
accumulates on the evaporator and the unit must periodically reverse to clear
it. Capacity and efficiency both fall, and the loss is largest exactly where
the Swedish shoulder season lives — and exactly where the optimizer is most
aggressive about coasting on stored heat.

The failure mode is quiet. Plans made in that band under-deliver, and the
shortfall surfaces as a comfort miss rather than as an obvious fault.

**The derate is learned, not tabulated.** A datasheet curve would be wrong for
most units, and the between-unit spread is larger than the effect being
modelled. What is learned is a multiplicative factor per (temperature,
humidity) bucket. With no evidence, the factor is exactly 1.0 and this module
changes nothing.

Two estimators, and which one is right
--------------------------------------

**The measured one (v5.2.0, preferred).** With a defrost flag from the pump,
duty is directly countable: fraction of the interval the unit spent defrosting.
The derate then follows from physics rather than from inference —
``factor = 1 - duty x DEFROST_LOSS_MULTIPLIER`` — where the multiplier is
above 1 because a defrost costs more than its own duration: output is not
merely zero, heat is actively pulled back out of the water loop to melt the
ice, and the minutes after it ends are spent recovering the loop temperature
before useful output resumes.

**The inferred one (pre-v5.2.0, the fallback).** Without a flag, the derate is
inferred from ``accuracy.delivered_ratio`` — and it is worth being explicit
about what that ratio is, because its own docstring is misleading. It is
``predicted_power / actual_power``: purely electrical, with no heat and no
temperature term anywhere in it. Two consequences follow, and both are why the
measured estimator exists:

1. *It cannot see a defrost at all.* During a real defrost the compressor
   draws roughly its normal power while delivering approximately no useful
   heat, so the ratio sits near 1.0 — the signature of a perfectly performing
   unit. Gating this estimator on a genuine defrost flag would therefore teach
   it "no derate", which is exactly backwards, and is why v5.2.0 does not do
   that.
2. *Its error is biased optimistic.* The gaps between commanded and measured
   power are dominated by the pump drawing LESS than commanded (compressor
   limits, cycling, ramp lag), so the ratio comes out above 1 — and until
   v5.2.0 the clamp allowed up to 1.05, i.e. "delivers 5% MORE than modelled",
   in the one band that exists to be pessimistic. That clamp is now 1.0 on
   both estimators: this module models a loss, and a defrost cycle cannot make
   a heat pump exceed its own curve. The bound is arithmetic, not a judgement
   call.

**Honesty about resolution.** Duty is only as good as the flag's sampling. The
reference Tuya integration polls the cloud every three minutes by default, and
a defrost that starts and finishes between two polls is invisible — so under
polling the measured duty is biased LOW and the derate correspondingly
optimistic. It is trustworthy at full resolution only under MQTT push, where
the flag arrives on change. :meth:`DefrostDerate.summary` therefore reports
``events`` alongside the duty, so a bucket learned from a handful of
transitions can be recognised as the coarse estimate it is, and the fallback
estimator's samples are never silently mixed in with the measured ones.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

_LOGGER = logging.getLogger(__name__)

# Bucket edges in °C. The frosting band is resolved finely and everything
# outside it coarsely, because that is where the physics actually varies.
TEMP_EDGES: tuple[float, ...] = (-30.0, -5.0, 0.0, 2.0, 5.0, 8.0, 40.0)
# Humidity split. Frost needs moisture; dry cold air barely frosts at all.
HUMIDITY_EDGES: tuple[float, ...] = (0.0, 70.0, 101.0)

# The band whose under-delivery is attributed to frost. Two learners watch the
# same commanded-versus-measured signal — the global COP scale and this derate —
# and if both fold in the same interval, one shortfall is corrected twice and
# plans in the band overshoot the compensation. So the attribution is disjoint:
# inside the band the shortfall belongs to frost and only this module learns
# from it; outside, frost is physically implausible and only the COP scale does.
FROST_BAND_MIN_C = 0.0
FROST_BAND_MAX_C = 5.0


def in_frost_band(outdoor_temp: float) -> bool:
    """Whether under-delivery at this outdoor temperature reads as frost."""
    return FROST_BAND_MIN_C <= float(outdoor_temp) < FROST_BAND_MAX_C

# Derate is bounded. A unit that appears to deliver less than half its rated
# output is telling us about a broken sensor, not about frost.
DERATE_MIN = 0.55
# v5.2.0: 1.0, previously 1.05. This module models a LOSS; a derate above 1
# says frost makes the pump exceed its own curve, which is not a thing that
# happens. The old bound let the fallback estimator's optimistic bias (see the
# module docstring) park at "5% better than modelled" in precisely the band
# that exists to make plans more careful. Lowering it can only ever make a
# frost-band plan more conservative.
DERATE_MAX = 1.0
# Slow, because each sample is a single noisy interval.
DERATE_ALPHA = 0.05
# Until a bucket has this many samples the derate is blended towards 1.0, so a
# first observation cannot swing a plan.
DERATE_CONFIDENCE_SAMPLES = 12

# --- the measured estimator (v5.2.0) ---------------------------------------
#: What a defrost costs, per unit of its own duration. Above 1 because output
#: does not merely stop: the reversing valve pulls heat back out of the water
#: loop to melt the ice, and the loop then has to recover before useful output
#: resumes. A modelling constant, deliberately NOT learned — the learned part
#: is the duty, which is what the flag actually measures. 1.5 is the middle of
#: the range reported for air-to-water units; the error it carries is small
#: next to the duty's own sampling error (see the module docstring).
DEFROST_LOSS_MULTIPLIER = 1.5
#: Duty above this is a latched flag or a miswired entity, not physics: a unit
#: spending a third of its life defrosting would be unusable and its owner
#: would not be reading this. Clamped rather than rejected, so a genuinely
#: awful hour still counts as "a lot" instead of vanishing.
DEFROST_DUTY_MAX = 0.30
#: Faster than the ratio estimator's: a duty measurement is a count, not an
#: inference from two noisy power figures, so it deserves more weight per
#: sample.
DUTY_ALPHA = 0.10

#: Persisted schema version. v1 stored only ``factors``/``counts`` from the
#: fallback estimator.
STORE_VERSION = 2


def _bucket_index(value: float, edges: tuple[float, ...]) -> int:
    for i in range(len(edges) - 1):
        if edges[i] <= value < edges[i + 1]:
            return i
    return len(edges) - 2 if value >= edges[-1] else 0


def _grid(fill):
    return [
        [fill for _ in range(len(HUMIDITY_EDGES) - 1)]
        for _ in range(len(TEMP_EDGES) - 1)
    ]


def derate_from_duty(duty: float) -> float:
    """The capacity/efficiency multiplier a measured defrost duty implies.

    The whole of the measured estimator, in one line of arithmetic:
    ``1 - duty x DEFROST_LOSS_MULTIPLIER``, bounded. Separate from the class
    so the physics can be read, and tested, without a learner around it.
    """
    duty = min(max(float(duty), 0.0), DEFROST_DUTY_MAX)
    return min(DERATE_MAX, max(DERATE_MIN, 1.0 - duty * DEFROST_LOSS_MULTIPLIER))


@dataclass
class DefrostDerate:
    """Per-bucket multiplicative COP/capacity derate, learned online.

    Holds both estimators. The measured one wins in any bucket that has a duty
    sample, because it rests on a count rather than an inference; the inferred
    one keeps every pre-v5.2.0 install working exactly as it did. They are
    never averaged: mixing a measurement with an inference of the same quantity
    produces a number that is neither.
    """

    #: ``factors[temp_bucket][humidity_bucket]`` — the INFERRED estimator.
    factors: list[list[float]] = field(default_factory=lambda: _grid(1.0))
    counts: list[list[int]] = field(default_factory=lambda: _grid(0))
    #: Learned mean defrost duty per bucket — the MEASURED estimator.
    duty: list[list[float]] = field(default_factory=lambda: _grid(0.0))
    duty_counts: list[list[int]] = field(default_factory=lambda: _grid(0))
    #: Defrost starts actually witnessed per bucket. Reported, never used in
    #: the arithmetic: it is how a user tells a duty learned from two coarse
    #: cloud polls from one learned from three hundred MQTT transitions.
    duty_events: list[list[int]] = field(default_factory=lambda: _grid(0))
    #: True when a v1 store was loaded and its inferred arrays were dropped.
    #: Surfaced in :meth:`summary` so the reset is visible rather than silent.
    migrated: bool = False

    # -- lookup -------------------------------------------------------------

    def _bucket(
        self, outdoor_temp: float, humidity: float | None
    ) -> tuple[int, int]:
        return (
            _bucket_index(float(outdoor_temp), TEMP_EDGES),
            _bucket_index(
                float(humidity) if humidity is not None else 60.0,
                HUMIDITY_EDGES,
            ),
        )

    def factor(self, outdoor_temp: float, humidity: float | None = None) -> float:
        """Derate for these conditions, blended towards 1.0 while uncertain."""
        t, h = self._bucket(outdoor_temp, humidity)
        n_duty = self.duty_counts[t][h]
        if n_duty > 0:
            raw = derate_from_duty(self.duty[t][h])
            n = n_duty
        else:
            raw = self.factors[t][h]
            n = self.counts[t][h]
            if n <= 0:
                return 1.0
        # Linear ramp of trust. A derate the size of the effect being measured
        # should not be applied on the strength of one observation.
        trust = min(1.0, n / DERATE_CONFIDENCE_SAMPLES)
        return 1.0 + (raw - 1.0) * trust

    def samples(self, outdoor_temp: float, humidity: float | None = None) -> int:
        t, h = self._bucket(outdoor_temp, humidity)
        return self.duty_counts[t][h] or self.counts[t][h]

    def measured(self, outdoor_temp: float, humidity: float | None = None) -> bool:
        """Whether this bucket's derate rests on a counted duty."""
        t, h = self._bucket(outdoor_temp, humidity)
        return self.duty_counts[t][h] > 0

    # -- learning -----------------------------------------------------------

    def observe(
        self,
        outdoor_temp: float,
        humidity: float | None,
        delivered_ratio: float,
    ) -> None:
        """Fold in one INFERRED observation, from the electrical power ratio.

        The pre-v5.2.0 estimator, kept for every install with no defrost flag.
        ``delivered_ratio`` is nominally realised over predicted thermal
        output, but is in fact ``predicted_power / actual_power`` — see the
        module docstring for why that cannot see a defrost and why its error
        is biased optimistic.
        """
        if delivered_ratio <= 0 or delivered_ratio > 3.0:
            return
        t, h = self._bucket(outdoor_temp, humidity)
        target = min(max(float(delivered_ratio), DERATE_MIN), DERATE_MAX)
        current = self.factors[t][h]
        self.factors[t][h] = (1.0 - DERATE_ALPHA) * current + DERATE_ALPHA * target
        self.counts[t][h] += 1

    def observe_duty(
        self,
        outdoor_temp: float,
        humidity: float | None,
        duty: float,
        events: int = 0,
    ) -> None:
        """Fold in one MEASURED observation: the interval's defrost duty.

        ``duty`` is the fraction of the settled interval the pump reported
        defrosting, ``events`` how many defrost starts were witnessed in it.
        A duty of zero is a real observation and is folded like any other —
        "no defrost happened in this hour at 3 °C" is exactly the evidence
        that stops a bucket carrying a derate it no longer earns.
        """
        duty = float(duty)
        if not 0.0 <= duty <= 1.0:
            return
        t, h = self._bucket(outdoor_temp, humidity)
        current = self.duty[t][h]
        self.duty[t][h] = (1.0 - DUTY_ALPHA) * current + DUTY_ALPHA * duty
        self.duty_counts[t][h] += 1
        self.duty_events[t][h] += max(0, int(events))

    # -- persistence --------------------------------------------------------

    def as_dict(self) -> dict:
        """The persisted form.

        ``factors``/``counts`` are still written, and still describe the
        inferred estimator, so a downgrade to v5.1.5 loads a store it fully
        understands instead of one it silently rejects. The measured arrays
        ride alongside under their own keys; v5.1.5's strict validator ignores
        keys it does not know.
        """
        return {
            "version": STORE_VERSION,
            "factors": self.factors,
            "counts": self.counts,
            "duty": self.duty,
            "duty_counts": self.duty_counts,
            "duty_events": self.duty_events,
        }

    @classmethod
    def from_dict(cls, data: dict | None) -> "DefrostDerate":
        """Load, tolerating both schema versions.

        A v1 store (no ``duty`` arrays) has its inferred ``factors``/``counts``
        **dropped**, not carried forward, and the instance is marked
        ``migrated``. That is a deliberate reset, not an oversight: those
        numbers were learned through a clamp that allowed 1.05, from a signal
        whose error is biased optimistic, in the one band where the derate
        exists to be pessimistic. Importing them into the new estimator would
        launder a known-wrong prior into a measurement. Starting from 1.0 —
        the module's own no-evidence default, which changes nothing — is the
        honest baseline, and a bucket re-earns its derate within a day or two
        of real duty samples.

        A v1 store on an install with no defrost flag is the same reset. It
        costs those installs their accumulated inferred derate once, which is
        the price of removing a bias that was making frost-band plans more
        aggressive than the physics allows.
        """
        instance = cls()
        if not isinstance(data, dict):
            return instance
        n_t = len(TEMP_EDGES) - 1
        n_h = len(HUMIDITY_EDGES) - 1

        def _grid_of(key, cast):
            raw = data.get(key)
            if (
                isinstance(raw, list)
                and len(raw) == n_t
                and all(isinstance(row, list) and len(row) == n_h for row in raw)
            ):
                try:
                    return [[cast(v) for v in row] for row in raw]
                except (TypeError, ValueError):
                    return None
            return None

        duty = _grid_of("duty", float)
        duty_counts = _grid_of("duty_counts", int)
        if duty is None or duty_counts is None:
            # v1, or a v2 store whose measured half is unreadable. Either way
            # there is no measured evidence to keep, and the inferred half is
            # not worth importing. Fresh, and marked.
            instance.migrated = isinstance(data.get("factors"), list)
            if instance.migrated:
                _LOGGER.info(
                    "Defrost derate: a pre-v5.2.0 store was found and reset. "
                    "Its factors were inferred from an electrical power ratio "
                    "that cannot see a defrost and is biased optimistic; the "
                    "derate relearns from measured duty (or from the same "
                    "ratio, unbiased at the clamp) from 1.0"
                )
            return instance

        instance.duty = duty
        instance.duty_counts = duty_counts
        events = _grid_of("duty_events", int)
        if events is not None:
            instance.duty_events = events
        factors = _grid_of("factors", float)
        if factors is not None:
            # Re-clamped on load: a store written before DERATE_MAX dropped to
            # 1.0 can carry factors up to 1.05, and reading them back
            # unchanged would let the old optimistic bound outlive the fix.
            instance.factors = [
                [min(DERATE_MAX, max(DERATE_MIN, v)) for v in row]
                for row in factors
            ]
        counts = _grid_of("counts", int)
        if counts is not None:
            instance.counts = counts
        return instance

    def summary(self) -> list[dict]:
        """Human-readable view for the diagnostics attributes.

        ``source`` says which estimator a bucket rests on, and ``events`` how
        many defrost starts were actually witnessed — the pair a user needs to
        judge a measured bucket, because a duty counted from three-minute
        cloud polls is a much weaker number than the same duty counted from
        MQTT transitions and nothing else on the row would show that.
        """
        out = []
        for t in range(len(TEMP_EDGES) - 1):
            for h in range(len(HUMIDITY_EDGES) - 1):
                measured = self.duty_counts[t][h] > 0
                if not measured and self.counts[t][h] <= 0:
                    continue
                entry = {
                    "outdoor_range": [TEMP_EDGES[t], TEMP_EDGES[t + 1]],
                    "humidity_range": [
                        HUMIDITY_EDGES[h],
                        HUMIDITY_EDGES[h + 1],
                    ],
                    "source": "measured" if measured else "inferred",
                    "derate": round(
                        derate_from_duty(self.duty[t][h])
                        if measured
                        else self.factors[t][h],
                        3,
                    ),
                    "samples": (
                        self.duty_counts[t][h] if measured else self.counts[t][h]
                    ),
                }
                if measured:
                    entry["duty"] = round(self.duty[t][h], 4)
                    entry["events"] = self.duty_events[t][h]
                out.append(entry)
        return out

    @property
    def total_samples(self) -> int:
        return sum(sum(row) for row in self.counts) + sum(
            sum(row) for row in self.duty_counts
        )

    @property
    def measured_samples(self) -> int:
        return sum(sum(row) for row in self.duty_counts)


@dataclass
class DefrostObservation:
    """One settled interval's defrost measurement."""

    #: Fraction of the interval the pump reported defrosting, 0..1.
    duty: float = 0.0
    #: Defrost starts witnessed in the interval.
    events: int = 0
    #: Whether the flag was legible at all. False means "no evidence", which
    #: is never the same as "no defrost": a duty of 0 from an unreadable flag
    #: is a confident claim nobody can make.
    observed: bool = False
    #: Wall-clock length of the interval, seconds. Reported so a caller can
    #: reject an interval too short or too long to mean anything.
    seconds: float = 0.0

    @property
    def any_defrost(self) -> bool:
        """Whether a defrost was actually seen. Only true when observed."""
        return self.observed and (self.events > 0 or self.duty > 0.0)


class DefrostWindow:
    """Integrates a defrost flag into on-time over one measurement interval.

    Two things feed it and both are needed. The coordinator's per-cycle read
    supplies the flag's *level* every update, which is what a flag that never
    changes (the normal case: not defrosting) can supply — Home Assistant
    fires no state-change event when a value is rewritten unchanged. A state
    listener supplies the *transitions*, which is the only way to see a
    defrost that starts and finishes between two cycles: a defrost runs
    minutes and the optimization interval is typically thirty of them, so
    without the listener a real defrost would settle as a confident duty of
    zero — wrong, and wrong in the optimistic direction.

    Both call :meth:`observe`; it is idempotent in level and only transitions
    count as events, so the two sources cannot double-count.

    Everything takes ``now`` as an argument. The class holds no clock, which
    is what lets a test drive a whole winter through it in a loop.
    """

    def __init__(self) -> None:
        self._opened: Any = None
        self._seconds_on: float = 0.0
        self._events: int = 0
        self._state: bool | None = None
        self._since: Any = None
        self._observed: bool = False

    @staticmethod
    def _elapsed(now: Any, then: Any) -> float | None:
        """Seconds between two stamps, or ``None`` if they cannot be compared.

        Same discipline as ``InputReader._age_minutes``: mixing a naive and an
        aware datetime raises, and without a comparable pair the elapsed time
        is *unknown*, which is not the same as zero. A window that cannot
        measure its own length must decline to answer rather than report a
        duty computed from a fiction.
        """
        try:
            return (now - then).total_seconds()
        except TypeError:
            return None

    def _accrue(self, now: Any) -> None:
        if self._state and self._since is not None:
            delta = self._elapsed(now, self._since)
            if delta is not None and delta > 0:
                self._seconds_on += delta
        self._since = now

    def observe(self, now: Any, flag: bool | None) -> None:
        """Fold one reading of the flag, from either source.

        ``flag is None`` means the signal was unreadable — unconfigured,
        unavailable, or past its horizon. Any open on-period is closed out at
        ``now`` (the pump was defrosting up to the moment the evidence
        stopped, and no further), and the interval is *not* marked observed.
        """
        if self._opened is None:
            self._opened = now
            self._since = now
        self._accrue(now)
        if flag is None:
            self._state = None
            return
        if flag and not self._state:
            self._events += 1
        self._state = bool(flag)
        self._observed = True

    def peek(self, now: Any) -> DefrostObservation:
        """What the open interval looks like right now, without closing it.

        ``_learn_measured_cop`` runs earlier in the cycle than the settlement
        that closes the window, and it needs the same answer: did the elapsed
        interval contain a defrost?
        """
        if self._opened is None:
            return DefrostObservation()
        total = self._elapsed(now, self._opened)
        if total is None:
            return DefrostObservation()
        total = max(0.0, total)
        seconds_on = self._seconds_on
        if self._state and self._since is not None:
            open_for = self._elapsed(now, self._since)
            seconds_on += max(0.0, open_for) if open_for is not None else 0.0
        return DefrostObservation(
            duty=min(1.0, seconds_on / total) if total > 0 else 0.0,
            events=self._events,
            observed=self._observed,
            seconds=total,
        )

    def close(self, now: Any) -> DefrostObservation:
        """Settle the interval and start the next one at ``now``.

        The flag's current level carries over: an interval boundary in the
        middle of a defrost must not lose the second half of it.
        """
        self._accrue(now)
        result = self.peek(now)
        self._opened = now
        self._seconds_on = 0.0
        self._events = 0
        self._since = now
        self._observed = self._state is not None
        return result
