"""The heat a delivered-heat counter measured, and which duty it served (#2261).

A ``total_increasing`` kWh counter of the heat the pump delivered answers
what a point reading cannot: the heat over a span, compressor cycling
included. This module owns that span (:class:`HeatEnergyMeter`), the time the
pump spent in each duty (:class:`ModeDwell`), and the one rule that splits an
interval between space heating and hot water (:func:`attribution`) with its
three consumers. Pure, with no Home Assistant import: the coordinator reads
the entities and calls in, and holds one meter per coordinator in a weak map
(:func:`meter_of`, ``boost.py``'s pattern), so its class grows no attribute.

**The span closes on elapsed time** between read instants, never on a cycle
count, at the first read past :func:`close_after_h`, and one past the
learners' own sample bound is refused, so an accepted span always lands
inside the bounds the interval learners check. Both counters are read in the
same cycle, so their deltas share instants; a counter not read at both ends
leaves its delta out. A span is accepted on a figure independent of its own
quantised delta (:func:`resolution_refusal`), never on the delta itself: a
selection on the quantised value biases the mean (a 0.6 kW load on an
integer-kWh counter read 2.0).

**The mode is the selector, not the duty.** A single-duty mode (``heat`` or
``DHW``) read live is observed; a combination mode, an unrecognised one and a
last-good fallback (whose ``last_changed`` is the stale state's own) are not,
and an interval touching one splits by the plan, which is the whole-unit rule
the tree had before the dwell (#2753). A point reading is never time-split:
it says what the pump delivered at one instant, not over the interval.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, NamedTuple
from weakref import WeakKeyDictionary

from .const import HEAT_LOSS_BASES
from .drift import utc_elapsed_seconds
from .pump_mode import MODE_DHW, MODE_HEAT

SPACE = "space"
DHW = "dhw"

#: Refresh drift tolerated in the close: Home Assistant schedules a refresh
#: after the previous one ends, so the cadence is the interval plus the
#: solve time, and an event-driven refresh lands at any time (3 min).
SPAN_CLOSE_ALLOWANCE_H = 0.05
#: The largest counter step a span may carry against the heat it should
#: show. At 1.0 a span must expect at least one step: an integer-kWh counter
#: is refused at 0.6 kW over the one-hour span a 30 min cadence closes, and
#: read at 1.5 kW. The quantisation stays in the sample as noise of at most
#: one step, unbiased because the span is fixed in time.
HEAT_RESOLUTION_EPS = 1.0
#: Headroom over the thermal nameplate before a delta reads as a rollover.
HEAT_COUNTER_SLACK = 1.5

SPAN_REFUSED_RESET = "counter_reset"
SPAN_REFUSED_ROLLOVER = "counter_rollover"
SPAN_REFUSED_RESOLUTION = "counter_resolution"
SPAN_REFUSED_LONG = "span_too_long"


def _after(newer: datetime, older: datetime) -> bool:
    return utc_elapsed_seconds(newer, older) > 0.0


def _hours(newer: datetime, older: datetime) -> float:
    return utc_elapsed_seconds(newer, older) / 3600.0


@dataclass
class CounterDelta:
    """One counter over the open span: where it opened, its latest read, its step.

    ``quantum`` is the smallest positive step seen between two consecutive
    reads, kept across spans: it is the counter's resolution, not a span's.
    """

    start: float | None = None
    start_at: datetime | None = None
    last: float | None = None
    last_at: datetime | None = None
    quantum: float | None = None

    def observe(self, kwh: float | None, at: datetime) -> None:
        """Fold one read; ``None`` (unread this cycle) leaves the counter as it was."""
        if kwh is None:
            return
        if self.last is not None and kwh > self.last:
            step = kwh - self.last
            self.quantum = step if self.quantum is None else min(self.quantum, step)
        self.last, self.last_at = kwh, at
        if self.start is None:
            self.rebase()

    def delta_over(self, start_at: datetime | None, end_at: datetime) -> float | None:
        """The delta between exactly these read instants, else ``None`` (unaligned)."""
        aligned = self.start_at == start_at and self.last_at == end_at
        if not aligned or self.start is None or self.last is None:
            return None
        return self.last - self.start

    def rebase(self) -> None:
        """Open the next span on the latest read."""
        self.start, self.start_at = self.last, self.last_at


class SpanEnergy(NamedTuple):
    """A closed span: its read instants, its length and both counters' deltas."""

    start: datetime
    end: datetime
    hours: float
    heat_kwh: float
    #: ``None`` with no electric counter, or one not read at both instants.
    elec_kwh: float | None
    #: The heat counter's resolution (:attr:`CounterDelta.quantum`).
    quantum: float | None


def close_after_h(cadence_h: float, bounds_h: tuple[float, float]) -> float:
    """The elapsed hours a span closes at: the last cadence that still fits the bound."""
    return max(bounds_h[0], bounds_h[1] - cadence_h - SPAN_CLOSE_ALLOWANCE_H)


def resolution_refusal(span: SpanEnergy, expected_kwh: float) -> str | None:
    """Why the span's heat is too coarse to read, or ``None``.

    ``expected_kwh`` is the heat the span should show by a figure the counter
    did not produce (the electric delta, or the commanded energy, at the
    modelled COP). Refused until the counter has shown a step at all.
    """
    q = span.quantum
    if q is None or not expected_kwh > 0.0 or q / expected_kwh > HEAT_RESOLUTION_EPS:
        return SPAN_REFUSED_RESOLUTION
    return None


class Segment(NamedTuple):
    """One stretch of the pump's mode: from ``start`` until the next segment."""

    start: datetime
    #: :data:`SPACE` or :data:`DHW` when observed, else ``None``.
    duty: str | None


@dataclass
class ModeDwell:
    """The pump's duty over time, from the mode entity's reads and their ``last_changed``.

    A change lands at the state's own ``last_changed``; one between two reads
    that returned to the same duty is an unseen excursion, unobserved from the
    earlier read. Without a known change time a new segment starts at the
    previous read, the conservative end.
    """

    segments: list[Segment] = field(default_factory=list)
    seen_at: datetime | None = None

    def observe(self, at: datetime, duty: str | None, changed_at: datetime | None) -> None:
        """Fold one cycle's mode read; ``changed_at`` ahead of the read is the read."""
        seen, self.seen_at = self.seen_at, at
        if changed_at is not None and _after(changed_at, at):
            changed_at = at
        if not self.segments or seen is None:
            self.segments.append(Segment(changed_at or at, duty))
            return
        moved = changed_at is not None and _after(changed_at, seen)
        last = self.segments[-1].duty
        if moved and duty is not None and last == duty:
            self.segments.append(Segment(seen, None))
        if moved or last != duty:
            self.segments.append(Segment(changed_at if changed_at is not None and moved else seen, duty))

    def shares(self, since: datetime | None, until: datetime | None) -> tuple[float, float] | None:
        """``(space hours, hot-water hours)`` over the window, ``None`` if any of it is unobserved."""
        if since is None or until is None or not _after(until, since):
            return None
        if not self.segments or _after(self.segments[0].start, since):
            return None
        space = dhw = 0.0
        for i, seg in enumerate(self.segments):
            end = self.segments[i + 1].start if i + 1 < len(self.segments) else until
            lo = since if _after(since, seg.start) else seg.start
            hi = end if _after(until, end) else until
            if not _after(hi, lo):
                continue
            if seg.duty is None:
                return None
            if seg.duty == SPACE:
                space += _hours(hi, lo)
            else:
                dhw += _hours(hi, lo)
        return space, dhw

    def prune(self, before: datetime) -> None:
        """Drop the segments that end before ``before``; the one covering it stays."""
        keep = 0
        for i, seg in enumerate(self.segments):
            if not _after(seg.start, before):
                keep = i
        del self.segments[:keep]


def observed_duty(mode_key: str | None, live: bool) -> str | None:
    """The single duty a live mode read names, else ``None`` (unobserved)."""
    return {MODE_HEAT: SPACE, MODE_DHW: DHW}.get(mode_key or "") if live else None


class Attribution(NamedTuple):
    """One interval's split between the two duties, by weight.

    Observed: the dwell's hours in each duty. Otherwise the caller's plan
    split, as the site read it before the dwell existed, so every consumer
    below reproduces that site's own rule on it.
    """

    space: float
    dhw: float
    observed: bool


def attribution(shares: tuple[float, float] | None, plan_split: tuple[float, float]) -> Attribution:
    """The dwell's shares when observed, else the plan's split: the one owner of the choice."""
    if shares is not None:
        return Attribution(shares[0], shares[1], True)
    return Attribution(float(plan_split[0]), float(plan_split[1]), False)


def space_heat_kw(heat_kw: float | None, a: Attribution, integrated: bool) -> float | None:
    """The space circuit's share of a heat reading, or ``None`` when there is none.

    ``integrated``: a counter span's mean over the dwell's own window, which
    the observed split divides by time. A point reading, and any unobserved
    interval, is the whole-unit rule: the reading where the interval served
    space alone, else nothing.
    """
    if heat_kw is None:
        return None
    total = a.space + a.dhw
    if a.observed and integrated:
        return heat_kw * a.space / total if total > 0.0 else None
    return heat_kw if a.dhw <= 0.0 < a.space else None


def ran_hot_water(a: Attribution) -> bool:
    """Whether the dwell saw the pump on hot water within the interval.

    A meter reading taken at the close is then not the interval's space
    figure, whatever the plan asked. An unobserved interval says nothing
    here: the caller's own plan rule stands.
    """
    return a.observed and a.dhw > 0.0


def cop_duty(a: Attribution, share_limit: float) -> str | None:
    """The curve a COP sample is judged against: one duty, or ``None`` for a blend."""
    total = a.space + a.dhw
    if total <= 1e-6:
        return SPACE
    share = a.dhw / total
    if share <= share_limit:
        return SPACE
    return DHW if share >= 1.0 - share_limit else None


def dhw_share(a: Attribution) -> float:
    """Hot water's share of one metered sum; a split with no weight is all space."""
    total = a.space + a.dhw
    return a.dhw / total if total > 1e-6 else 0.0


class SpanEvidence(NamedTuple):
    """What a span hands its learners at its close: its energy, or why it was refused."""

    energy: SpanEnergy | None
    refusal: str | None
    #: The learners' baseline state at the span's opening cycle, and its time.
    state: Any
    state_at: datetime
    #: Each learner's per-cycle gates, ANDed over the span.
    clean: dict[str, bool]
    #: The plan's ``(space, hot water)`` commanded kWh over the span.
    plan_kwh: tuple[float, float]
    attribution: Attribution


class SpanHeat(NamedTuple):
    """A closed span read: its mean heat, space share, ask and draw, in kW."""

    #: ``None`` when the span or its resolution was refused.
    heat_kw: float | None
    space_kw: float | None
    asked_kw: float
    #: ``None`` without an electric delta at both of the span's instants.
    elec_kw: float | None
    #: Why the span was refused, or its heat too coarse, or ``None``.
    refusal: str | None


def span_heat(ev: SpanEvidence, modelled_cop: float) -> SpanHeat:
    """Read a span's evidence: refused, too coarse, or its heat and its split.

    The heat the span should show is the electric delta at ``modelled_cop``,
    or the commanded energy at it without an electric counter, a figure the
    counter did not produce (:func:`resolution_refusal`). The house replay
    reads the heat without an electric counter; the COP cannot.
    """
    e = ev.energy
    if e is None:
        return SpanHeat(None, None, 0.0, None, ev.refusal)
    asked_kwh = ev.plan_kwh[0] + ev.plan_kwh[1]
    refusal = resolution_refusal(e, modelled_cop * (asked_kwh if e.elec_kwh is None else e.elec_kwh))
    heat_kw = None if refusal else e.heat_kwh / e.hours
    elec_kw = None if e.elec_kwh is None else e.elec_kwh / e.hours
    return SpanHeat(heat_kw, space_heat_kw(heat_kw, ev.attribution, integrated=True), asked_kwh / e.hours, elec_kw, refusal)


class SpanClose(NamedTuple):
    """What a cycle's span close hands the learners (:meth:`HeatEnergyMeter.close_span`).

    ``lower``, ``house`` and ``cop`` name the learners it reaches.
    """

    #: The fabric interval the span replays, as ``interval_of`` built it from
    #: its opening state and time, its end, its hours and the plan's asked
    #: kW; ``None`` when it replays none.
    interval: Any
    space_kw: float | None
    asked_kw: float
    heat_kw: float | None
    #: The span's mean draw. Read only when ``refusal`` is ``None``, which a
    #: span without an electric delta at both instants never is; 0.0 there.
    elec_kw: float
    #: The COP learner's refusal, or ``None`` when the span's draw folds.
    refusal: str | None
    #: The ``(heat kW, attribution)`` the COP reference curve is chosen on.
    reference: tuple[float | None, Attribution]
    lower: bool
    house: bool
    cop: bool


#: No span closed or was refused this cycle: no learner is reached.
NO_SPAN = SpanClose(None, None, 0.0, None, 0.0, None, (None, Attribution(0.0, 0.0, False)), False, False, False)


@dataclass
class HeatEnergyMeter:
    """One coordinator's heat and electric counters, its mode dwell and the open span."""

    heat: CounterDelta = field(default_factory=CounterDelta)
    elec: CounterDelta = field(default_factory=CounterDelta)
    dwell: ModeDwell = field(default_factory=ModeDwell)
    #: Whether a heat counter is configured; the span folds are its alone.
    counter: bool = False
    #: The heat-loss learners' basis is ``measured_heat``: earned at the
    #: first fold that replayed a measured heat, restored from the store.
    earned: bool = False
    #: This cycle's closed span, or why its close was refused.
    closed: SpanEnergy | None = None
    refusal: str | None = None
    #: The read instants of the previous and this cycle: the window every
    #: per-cycle attribution splits.
    cycle: tuple[datetime | None, datetime | None] = (None, None)
    _opened: bool = False
    _anchor: tuple[Any, datetime] | None = None
    _clean: dict[str, bool] = field(default_factory=dict)
    _plan: tuple[float, float] = (0.0, 0.0)

    def observe_mode(
        self, at: datetime, mode_key: str | None, live: bool, changed_at: datetime | None
    ) -> None:
        """Fold this cycle's mode read into the dwell: its key, whether it was read live, and when it changed."""
        self.dwell.observe(at, observed_duty(mode_key, live), changed_at)

    def observe_cycle(
        self, at: datetime, signals: Any, heat: Any, elec_kwh: float | None, cadence_min: float,
        bounds_h: tuple[float, float], params: Any,
    ) -> None:
        """This cycle's mode and counter reads (#2261), as the coordinator holds them.

        ``signals`` is the pump's ``PumpSignals`` (a mode read live,
        ``mode_live``, is observed), ``heat`` the heat counter's reading (its
        value only when it read, configured when it names an entity),
        ``cadence_min`` the optimization interval in minutes, ``bounds_h`` the
        interval learners' sample bounds and ``params`` the thermal parameters
        whose nameplate heat bounds a rollover.
        """
        self.observe_mode(at, signals.mode.key, signals.mode_live, signals.mode_changed_at)
        self.observe_counters(
            at, heat.value if heat.ok else None, elec_kwh, configured=bool(heat.entity_id),
            cadence_h=cadence_min / 60.0, bounds_h=bounds_h,
            max_heat_kw=params.max_electrical_power * params.cop_nominal_floored,
        )

    def attribution(self, plan_split: tuple[float, float]) -> Attribution:
        """This cycle's interval, split by the dwell where observed, else by ``plan_split``."""
        return attribution(self.dwell.shares(*self.cycle), plan_split)

    def observe_counters(
        self,
        at: datetime,
        heat_kwh: float | None,
        elec_kwh: float | None,
        *,
        configured: bool,
        cadence_h: float,
        bounds_h: tuple[float, float],
        max_heat_kw: float,
    ) -> None:
        """Fold this cycle's counter reads; close the span when its time has come.

        ``bounds_h`` is the interval learners' ``(min, max)`` sample length,
        ``max_heat_kw`` the thermal nameplate the rollover bound scales.
        """
        self.closed = self.refusal = None
        self.counter, self.cycle = configured, (self.cycle[1], at)
        start, start_at = self.heat.start, self.heat.start_at
        self.heat.observe(heat_kwh, at)
        self.elec.observe(elec_kwh, at)
        self._opened = start is None and self.heat.start is not None
        if heat_kwh is not None and start is not None and start_at is not None:
            self._close(at, start_at, heat_kwh - start, cadence_h, bounds_h, max_heat_kw)
        # A span closed this cycle is read by ``settle`` after this prune, so
        # its own opening instant bounds the prune, not the next span's.
        keep, opened_at = self.cycle[0], self.heat.start_at if start_at is None else start_at
        if opened_at is not None and (keep is None or _after(keep, opened_at)):
            keep = opened_at
        if keep is not None:
            self.dwell.prune(keep)

    def _close(
        self, at: datetime, start_at: datetime, heat_kwh: float, cadence_h: float,
        bounds_h: tuple[float, float], max_heat_kw: float,
    ) -> None:
        """Close, refuse or keep open the span that opened at ``start_at``."""
        hours = _hours(at, start_at)
        if hours > bounds_h[1]:
            self.refusal = SPAN_REFUSED_LONG
        elif hours < close_after_h(cadence_h, bounds_h):
            return
        elif heat_kwh < 0.0:
            self.refusal = SPAN_REFUSED_RESET
        elif heat_kwh > max_heat_kw * hours * HEAT_COUNTER_SLACK:
            self.refusal = SPAN_REFUSED_ROLLOVER
        else:
            elec = self.elec.delta_over(start_at, at)
            self.closed = SpanEnergy(start_at, at, hours, heat_kwh, elec, self.heat.quantum)
        self.heat.rebase()
        self.elec.rebase()
        self._opened = True

    def settle(
        self, clean: dict[str, bool], plan_kw: tuple[float, float], anchor: tuple[Any, datetime | None]
    ) -> SpanEvidence | None:
        """This cycle's gates and plan into the span; its evidence when it closed or was refused.

        Called once per cycle after the learners' per-cycle runs, with each
        learner's gate outcome and the plan split that governed the elapsed
        interval. A span (re)opened at this cycle's reads starts from
        ``anchor``, the learners' baseline state taken this cycle.
        """
        prev, now = self.cycle
        dt_h = _hours(now, prev) if prev is not None and now is not None else 0.0
        self._clean = {k: self._clean.get(k, True) and v for k, v in clean.items()}
        self._plan = (self._plan[0] + plan_kw[0] * dt_h, self._plan[1] + plan_kw[1] * dt_h)
        out = None
        if (self.closed is not None or self.refusal is not None) and self._anchor is not None:
            e = self.closed
            shares = self.dwell.shares(e.start, e.end) if e is not None else None
            out = SpanEvidence(
                e, self.refusal, *self._anchor, self._clean, self._plan, attribution(shares, self._plan)
            )
        if self._opened and anchor[1] is not None:
            self._anchor, self._clean, self._plan = (anchor[0], anchor[1]), {}, (0.0, 0.0)
        elif self._opened:
            self._anchor = None
        return out

    def earns_basis(self, measured_heat: bool) -> bool:
        """Whether a replay of a measured heat earns the ``measured_heat`` basis now:
        the first, on an install whose heat figure is measured."""
        return not self.earned and measured_heat

    def earn_basis(self) -> None:
        """The ``measured_heat`` basis is earned (after the void path took its prior anchors)."""
        self.earned = True

    def restore_basis(self, stored: Any) -> None:
        """A stored ``measured_heat`` basis restores the earned flag; nothing here clears it."""
        self.earned |= stored == HEAT_LOSS_BASES[-1]

    @property
    def spans_own_scale(self) -> bool:
        """Whether the heat-loss scale folds at span close alone (point B)."""
        return self.counter and self.earned


def close_span(
    meter: HeatEnergyMeter, clean: dict[str, bool], plan_kw: tuple[float, float], anchor_state: Any,
    anchor_at: datetime | None, modelled_cop: float, unaligned: str, interval_of: Any,
) -> SpanClose:
    """Settle this cycle (:meth:`HeatEnergyMeter.settle`) and read a closed span for its learners.

    A span whose space share was read replays, as ``interval_of(state,
    state_at, end, hours, asked_kw)``, into each fabric learner whose gates
    held over it; the COP learner takes the span when its gates held, or the
    refusal of a span that closed on none. It folds the two counters'
    deltas, or refuses with ``unaligned`` (the COP evidence's own code)
    without an electric delta at both instants.
    """
    ev = meter.settle(clean, plan_kw, (anchor_state, anchor_at))
    if ev is None:
        return NO_SPAN
    got, e = span_heat(ev, modelled_cop), ev.energy
    interval = None
    if got.space_kw is not None and e is not None:
        interval = interval_of(ev.state, ev.state_at, e.end, e.hours, got.asked_kw)
    return SpanClose(
        interval, got.space_kw, got.asked_kw, got.heat_kw, 0.0 if got.elec_kw is None else got.elec_kw,
        got.refusal or (unaligned if got.elec_kw is None else None), (got.heat_kw, ev.attribution),
        interval is not None and bool(ev.clean.get("lower")), interval is not None and bool(ev.clean.get("house")),
        bool(ev.clean.get("cop")) or e is None,
    )


def replay_gate(
    span_heat_kw: float | None, interval: Any, unmeasured: str | None, frozen: str | None,
    heat_kw: float | None, spans_own_scale: bool,
) -> tuple[float | None, bool, str | None, bool]:
    """A fabric learner's ``(heat kW, span clean, freeze, folds)`` for one run (#2261).

    A span run (``span_heat_kw``) passed its gates on every cycle already
    and folds. Otherwise the run reads ``heat_kw``; it leaves the span clean
    when it had an interval and no freeze with no heat measured
    (``unmeasured``: the unmetered-power freeze is lifted, since the span
    replays measured heat); its freeze is ``frozen``, the one with
    ``heat_kw``; and it folds unless the span folds the scale alone
    (``spans_own_scale``).
    """
    if span_heat_kw is not None:
        return span_heat_kw, False, None, True
    return heat_kw, interval is not None and unmeasured is None, frozen, not spans_own_scale


_METERS: WeakKeyDictionary[Any, HeatEnergyMeter] = WeakKeyDictionary()


def meter_of(owner: Any) -> HeatEnergyMeter:
    """``owner``'s meter, made on first use (a meter is always truthy)."""
    return _METERS.get(owner) or _METERS.setdefault(owner, HeatEnergyMeter())
