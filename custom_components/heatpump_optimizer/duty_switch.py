"""Duty-switch restart learning: does a duty switch stop a running compressor?

Design: ``docs/design/2026-11-10-duty-switch-restart-learning/design.md``,
part A. On some pumps a mode write from hot water to heating while the
compressor runs stops it: the controller judges the heating request on a
return the hot-water leg has just heated. Whether it does, and for how long
the pump then stays off, is learned per install and per direction. **Nothing
reads the estimate to change a plan or a write**; it is recorded, persisted
and published on the compressor-starts sensor.

**Observe** (:class:`DutySwitchLearner`, no Home Assistant object). An
episode opens at a landed mode write between the two single duties while the
compressor runs (:meth:`DutySwitchLearner.mode_write`), when the source leg
counts (:func:`_heated`), the target duty has demand and the plan keeps it
on. Inside :data:`STOP_WINDOW_S` it closes **stopped** on a stop edge, **kept**
at expiry, and **void** when anything else could explain a stop
(:meth:`SwitchContext.void_cause`, another mode write, a person's change, a
lost running signal). A stop's off time runs to the next start edge and is
censored by any write of the arbiter, or the supply switch, in between.

**The running signal** is ``wear.compressor_running`` over the reading the
arbiter's reader hands in, its edges ``wear.EdgeTracker``'s. This module's
own listener (:func:`attach`) feeds the tracker and never triggers an arbiter
pass; the pass (:func:`note_pass`) confirms a pending edge. Everything below
the registry takes the pump's :class:`_Record`, never the coordinator.

**Estimate.** Per direction two decayed counts, ``k`` stops over ``n``
episodes (stored as the stopped and the kept weight), half-life :data:`HALF_LIFE_DAYS`: decay scales both alike, so
``p = k / n`` never moves with age and only ``n`` falls. ``usable`` latches on
at a decayed weight of :data:`N_ON`, not a count (five stops ten hours apart
weigh under five, and a sixth latches), spanning :data:`SPAN_DAYS_ON` days with ``p`` at
:data:`P_ON`, and off under :data:`N_OFF` or :data:`P_OFF`. The span is of
the evidence that still weighs: under :data:`SPAN_FLOOR_N` the days are
forgotten with it. Every threshold
here is a named constant from one day on one install, not a measurement.
"""
from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Callable
from weakref import WeakKeyDictionary

from homeassistant.core import callback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.util import dt as dt_util

from . import pump_mode, wear
from .const import DOMAIN
from .drift import stored_instant, utc_elapsed_seconds
from .store import QuarantiningStore

_LOGGER = logging.getLogger(__name__)

#: The learned directions: the single duty switched from, then to.
DIRECTIONS = ("dhw_space", "space_dhw")
_DIRECTION = {(pump_mode.MODE_DHW, pump_mode.MODE_HEAT): "dhw_space",
              (pump_mode.MODE_HEAT, pump_mode.MODE_DHW): "space_dhw"}
#: Seconds after the write inside which a stop is the switch's.
STOP_WINDOW_S = 180.0
#: Kelvin the inlet must sit over the space circuit's water set-point for the
#: hot-water leg to have heated the circuit; without an inlet reading or a
#: water set-point (an indoor-unit set-point is a room temperature, which the
#: water is always over), and into hot water (whose inlet is never over a
#: set-point), the source leg's least seconds.
HEATED_MARGIN_K = 2.0
SOURCE_LEG_MIN_S = 60.0
HALF_LIFE_DAYS = 14.0
N_ON, N_OFF = 5.0, 2.5
P_ON, P_OFF = 0.5, 0.3
SPAN_DAYS_ON = 2
#: Decayed episodes under which a direction's days span nothing any more: one
#: episode a half-life old. Without it the first day never moved, and a year-old
#: episode made six stops on one day read as a year's span.
SPAN_FLOOR_N = 0.5
OFF_SAMPLES_MAX = 32
#: Load bounds: a count or an off time past these was not written here.
_N_MAX = 1e6
_OFF_MAX_S = 86400.0
_TALLY_MAX = 10**9
STORE_VERSION = 1
_TALLIES = ("stopped", "kept", "void", "censored")
_ROW_KEYS = frozenset(("k", "kept_w", "decayed_at", "first_day", "last_day", "usable", "off_s", *_TALLIES))


@dataclass(frozen=True)
class SwitchContext:
    """What the arbiter read on one pass or at one mode write.

    The first block can explain a compressor stop without the switch; the
    second says what the arbiter itself wrote; the third is read at a mode
    write only and gates whether the switch counts.
    """

    supply_on: bool = True
    #: Auto or Economy under duty control: the plan is what commands.
    plan_control: bool = True
    defrosting: bool = False
    disinfecting: bool = False
    boost_held: bool = False
    #: A backup heater or the hot-water booster element reads on.
    electric_heat: bool = False
    fault: bool = False
    #: The power-feedback loop moved the space target off today's open-loop one.
    loop_moved: bool = False

    #: When the mode record was written (``None``: dropped, a person's change),
    #: and the latest write over every slot.
    mode_written_at: datetime | None = None
    last_write_at: datetime | None = None

    inlet_c: float | None = None
    #: The space set-point where it is a water temperature (unit flow or
    #: return); ``None`` on an indoor-unit set-point, a room temperature.
    water_setpoint_c: float | None = None
    source_leg_s: float | None = None
    target_demand: bool = False
    plan_stays: bool = False

    def void_cause(self) -> str | None:
        """The first reading that could stop the compressor by itself."""
        causes = (
            ("supply_off", not self.supply_on), ("not_plan_control", not self.plan_control),
            ("defrost", self.defrosting), ("disinfection", self.disinfecting),
            ("boost", self.boost_held), ("electric_heat", self.electric_heat),
            ("fault", self.fault), ("feedback_loop", self.loop_moved),
        )
        return next((name for name, on in causes if on), None)


def _heated(direction: str, ctx: SwitchContext) -> bool:
    """Whether the source leg counts as having set the circuit up for a stop."""
    if direction == "dhw_space" and ctx.inlet_c is not None and ctx.water_setpoint_c is not None:
        return ctx.inlet_c - ctx.water_setpoint_c >= HEATED_MARGIN_K
    return ctx.source_leg_s is not None and ctx.source_leg_s >= SOURCE_LEG_MIN_S


@dataclass
class Direction:
    """One direction's decayed evidence, latch, off times and tallies."""

    #: Decayed weight of the stopped and of the kept episodes. Two addends,
    #: not ``k`` and ``n``: every stored pair is then a valid one.
    k: float = 0.0
    kept_w: float = 0.0
    decayed_at: datetime | None = None
    first_day: date | None = None
    last_day: date | None = None
    usable: bool = False
    off_s: list[float] = field(default_factory=list)
    stopped: int = 0
    kept: int = 0
    void: int = 0
    censored: int = 0

    @property
    def n(self) -> float:
        return self.k + self.kept_w

    @property
    def p(self) -> float:
        return self.k / self.n if self.n > 0.0 else 0.0

    @property
    def span_days(self) -> int:
        return 0 if self.first_day is None or self.last_day is None else (self.last_day - self.first_day).days + 1

    @property
    def median_off_s(self) -> float | None:
        offs = sorted(self.off_s)
        return (offs[(len(offs) - 1) // 2] + offs[len(offs) // 2]) / 2.0 if offs else None

    def weights(self, when: datetime) -> tuple[float, float]:
        """``(k, n)`` as of ``when``; a stamp ahead of ``when`` decays nothing."""
        if self.decayed_at is None:
            return self.k, self.n
        age_s = max(0.0, utc_elapsed_seconds(when, self.decayed_at))
        factor = 0.5 ** (age_s / (HALF_LIFE_DAYS * 86400.0))
        return self.k * factor, self.n * factor

    def decay(self, when: datetime) -> bool:
        """Age the counts to ``when``; whether the latch or the span's days moved."""
        n = self.n
        factor = self.weights(when)[1] / n if n > 0.0 else 1.0
        self.k, self.kept_w = self.k * factor, self.kept_w * factor
        if self.decayed_at is None or utc_elapsed_seconds(when, self.decayed_at) > 0.0:
            self.decayed_at = when
        aged_out = self.first_day is not None and self.n < SPAN_FLOOR_N
        if aged_out:
            self.first_day = self.last_day = None
        return self._latch() or aged_out

    def _latch(self) -> bool:
        was = self.usable
        if was:
            self.usable = not (self.n < N_OFF or self.p < P_OFF)
        else:
            self.usable = self.n >= N_ON and self.p >= P_ON and self.span_days >= SPAN_DAYS_ON
        return self.usable != was

    def book(self, when: datetime, stopped: bool, off_s: float | None) -> None:
        self.decay(when)
        self.k, self.kept_w = self.k + (1.0 if stopped else 0.0), self.kept_w + (0.0 if stopped else 1.0)
        day = when.date()
        self.first_day, self.last_day = self.first_day or day, max(self.last_day or day, day)
        if not stopped:
            self.kept += 1
        else:
            self.stopped += 1
            if off_s is None:
                self.censored += 1
            else:
                self.off_s = [*self.off_s, off_s][-OFF_SAMPLES_MAX:]
        self._latch()

    def stored_row(self) -> dict[str, Any]:
        return {
            "k": self.k, "kept_w": self.kept_w,
            "decayed_at": None if self.decayed_at is None else self.decayed_at.isoformat(),
            "first_day": None if self.first_day is None else self.first_day.isoformat(),
            "last_day": None if self.last_day is None else self.last_day.isoformat(),
            "usable": self.usable, "off_s": list(self.off_s),
            "stopped": self.stopped, "kept": self.kept, "void": self.void, "censored": self.censored,
        }

    @classmethod
    def from_row(cls, row: Any) -> "Direction":
        """The stored row, or ``ValueError`` on any shape or bound it could not have written."""
        if not isinstance(row, dict) or set(row) != _ROW_KEYS or not all(
                check(row[key]) for key, check in _ROW_CHECKS.items()):
            raise ValueError("row")
        stamp = row["decayed_at"]
        decayed_at = None if stamp is None else stored_instant(stamp)
        first, last = (None if row[key] is None else date.fromisoformat(row[key])
                       for key in ("first_day", "last_day"))
        if (stamp is None) != (decayed_at is None) or (first is None) != (last is None) or (
                first is not None and last is not None and first > last):
            raise ValueError("stamps")
        return cls(float(row["k"]), float(row["kept_w"]), decayed_at, first, last, row["usable"],
                   [float(o) for o in row["off_s"]], *(row[t] for t in _TALLIES))


def _stored_number(value: Any, hi: float = math.inf) -> bool:
    return (isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
            and 0.0 <= value <= hi)


def _tally(value: Any) -> bool:
    return isinstance(value, int) and _stored_number(value, _TALLY_MAX)


#: What each stored leaf must be before it is parsed; the stamps are parsed after.
_ROW_CHECKS: dict[str, Callable[[Any], bool]] = {
    "k": lambda v: _stored_number(v, _N_MAX), "kept_w": lambda v: _stored_number(v, _N_MAX),
    "off_s": lambda v: isinstance(v, list) and len(v) <= OFF_SAMPLES_MAX and all(_stored_number(o, _OFF_MAX_S) for o in v),
    "usable": lambda v: isinstance(v, bool),
    **{t: _tally for t in _TALLIES},
}


@dataclass
class Episode:
    at: datetime
    direction: str
    stop_at: datetime | None = None
    #: The stop was void-checked on the pass after it.
    checked: bool = False


@dataclass
class DutySwitchLearner:
    """Episodes and estimate for one pump. Every method returns whether the
    stored record changed."""

    directions: dict[str, Direction] = field(default_factory=lambda: {d: Direction() for d in DIRECTIONS})
    episode: Episode | None = None

    def mode_write(self, when: datetime, old: Any, new: Any, running: bool, ctx: SwitchContext) -> bool:
        """A mode write landed: it ends an open episode, and may open one.

        A re-send (``old`` unknown or equal to ``new``) opens nothing.
        """
        changed = self._interrupt()
        direction = _DIRECTION.get((old, new))
        if (direction is not None and running and _heated(direction, ctx) and ctx.target_demand
                and ctx.plan_stays and ctx.void_cause() is None):
            self.episode = Episode(when, direction)
        return changed

    def _interrupt(self) -> bool:
        ep = self.episode
        if ep is None:
            return False
        return self._void(ep) if ep.stop_at is None else self._close(ep, True, None)

    def edge(self, when: datetime, running: bool | None) -> bool:
        """A confirmed edge of the running class, at the time it began."""
        ep = self.episode
        if ep is None:
            return False
        if running is None:
            # No signal is never "stopped"; a stop already attributed keeps its count.
            return self._close(ep, True, None) if ep.checked else self._void(ep)
        if ep.stop_at is not None:
            return self._close(ep, True, utc_elapsed_seconds(when, ep.stop_at)) if running else False
        since_s = utc_elapsed_seconds(when, ep.at)
        if running:
            return False
        if since_s < 0.0:
            return self._void(ep)  # it had stopped before the write
        if since_s > STOP_WINDOW_S:
            return self._close(ep, False, None)
        ep.stop_at = when
        return False

    def note_pass(self, when: datetime, ctx: SwitchContext, pending: bool) -> bool:
        """One arbiter pass: age the latches, void, expire or censor the episode.

        ``pending`` is whether a change of the running class awaits its
        debounce. A lost signal is a confirmed edge (:meth:`edge`), never
        this call's to judge.
        """
        changed = any([d.decay(when) for d in self.directions.values()])
        ep = self.episode
        if ep is None:
            return changed
        explained = ctx.void_cause() is not None or ctx.mode_written_at != ep.at
        if ep.stop_at is None:
            if explained:
                return self._void(ep)
            if not pending and utc_elapsed_seconds(when, ep.at) >= STOP_WINDOW_S:
                return self._close(ep, False, None)
            return changed
        if not ep.checked:
            ep.checked = True
            if explained:
                return self._void(ep)
        wrote = ctx.last_write_at is not None and utc_elapsed_seconds(ctx.last_write_at, ep.stop_at) > 0.0
        if wrote or explained:
            return self._close(ep, True, None)
        return changed

    def _void(self, ep: Episode) -> bool:
        self.episode = None
        self.directions[ep.direction].void += 1
        return True

    def _close(self, ep: Episode, stopped: bool, off_s: float | None) -> bool:
        self.episode = None
        self.directions[ep.direction].book(ep.at, stopped, off_s)
        return True

    def published(self, when: datetime) -> dict[str, float]:
        """Counts and durations per direction, flat and numeric. A direction
        nothing was observed in publishes no key, and no off time yet is no
        key: an install that never switches duty while running reads as before.

        Age alone moves ``n`` only, and only by a whole episode: ``n`` is the
        whole episodes still weighing, and ``p`` does not decay (``k`` is ``p``
        times ``n``, so it is not published)."""
        out: dict[str, float] = {}
        for name, d in self.directions.items():
            if not (d.stopped or d.kept or d.void):
                continue
            row: dict[str, float | None] = {
                "p": round(d.p, 2), "n": float(math.floor(d.weights(when)[1])),
                "stopped": d.stopped, "kept": d.kept, "void": d.void, "censored": d.censored,
                "median_off_s": None if d.median_off_s is None else round(d.median_off_s, 1),
                "span_days": d.span_days,
            }
            out.update({f"duty_switch_{name}_{key}": value for key, value in row.items() if value is not None})
        return out

    def stored_record(self) -> dict[str, Any]:
        return {"directions": {name: d.stored_row() for name, d in self.directions.items()}}

    @classmethod
    def from_record(cls, data: Any) -> "DutySwitchLearner":
        """The stored learner, or an empty one on any invalid shape or bound.

        ``QuarantiningStore`` scrubs a poisoned leaf to a default and does not
        reject, so a record is whole or it is not read: a half-kept row would
        be evidence nobody observed.
        """
        try:
            rows = data["directions"]
            if not isinstance(rows, dict) or set(rows) != set(DIRECTIONS):
                raise ValueError("directions")
            return cls({name: Direction.from_row(rows[name]) for name in DIRECTIONS})
        except (TypeError, KeyError, ValueError, OverflowError):
            return cls()


# -- the Home Assistant edge: listener, store, per-coordinator record ---------

#: ``() -> (frequency Hz, power kW, threshold kW, by frequency)``, the
#: arguments of ``wear.compressor_running``; built by the arbiter.
Reader = Callable[[], tuple[float | None, float | None, float | None, bool]]


@dataclass
class _Record:
    """One pump's learner, running signal and store."""

    hass: Any
    store: Any
    learner: DutySwitchLearner = field(default_factory=DutySwitchLearner)
    tracker: wear.EdgeTracker = field(default_factory=wear.EdgeTracker)
    reader: Reader | None = None
    unsub: Callable[[], None] | None = None
    loaded: bool = False
    dirty: bool = False

    def feed(self, edge: tuple[datetime, bool | None] | None) -> None:
        """Hand a confirmed edge, if any, to the learner."""
        if edge is not None:
            self.dirty = self.learner.edge(*edge) or self.dirty


_RECORDS: WeakKeyDictionary[Any, _Record] = WeakKeyDictionary()


def record_for(coord: Any) -> _Record:
    """The pump's record, made on first use; one config entry is one pump."""
    rec = _RECORDS.get(coord)
    if rec is None:
        rec = _RECORDS[coord] = _Record(coord.hass, QuarantiningStore(
            coord.hass, STORE_VERSION, f"{DOMAIN}_{coord.entry.entry_id}_duty_switch"))
    return rec


def attach(rec: _Record, entity: str | None, reader: Reader) -> None:
    """Listen on the running signal's ``entity``; idempotent, and a no-op without one."""
    if rec.unsub is not None or not entity:
        return
    rec.reader = reader

    @callback
    def _changed(_event: Any) -> None:
        note_signal(rec, dt_util.now())

    rec.unsub = async_track_state_change_event(rec.hass, [entity], _changed)
    note_signal(rec, dt_util.now())


def detach(coord: Any) -> None:
    """Stop listening; an open episode is dropped uncounted, the signal forgotten."""
    rec = _RECORDS.get(coord)
    if rec is None or rec.unsub is None:
        return
    rec.unsub()
    rec.unsub, rec.reader, rec.tracker, rec.learner.episode = None, None, wear.EdgeTracker(), None


def note_signal(rec: _Record, when: datetime) -> None:
    """One reading of the running signal; never triggers an arbiter pass."""
    if rec.reader is not None:
        rec.feed(rec.tracker.note(when, wear.compressor_running(*rec.reader())))


def note_mode_write(rec: _Record, when: datetime, old: Any, new: Any, ctx: SwitchContext) -> None:
    """The arbiter's mode write landed. A report before the load is dropped."""
    if not rec.loaded:
        return
    running = rec.tracker.settled is True and rec.tracker.pending is None
    rec.dirty = rec.learner.mode_write(when, old, new, running, ctx) or rec.dirty


async def note_pass(rec: _Record, when: datetime, ctx: SwitchContext) -> None:
    """Each arbiter pass: load once, confirm a pending edge, judge the episode, save a change."""
    if not await _load(rec):
        return
    rec.feed(rec.tracker.confirm(when))
    rec.dirty = rec.learner.note_pass(when, ctx, rec.tracker.pending is not None) or rec.dirty
    if rec.dirty:
        await _persist(rec)


async def _load(rec: _Record) -> bool:
    """Read the stored learner once; a failed read is tried again on the next pass."""
    if not rec.loaded:
        try:
            raw = await rec.store.async_load()
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Could not load the duty-switch record: %s", err)
            return False
        rec.learner, rec.loaded = DutySwitchLearner.from_record(raw), True
    return True


async def _persist(rec: _Record) -> None:
    try:
        await rec.store.async_save(rec.learner.stored_record())
    except Exception as err:  # noqa: BLE001 - still dirty: saved on the next pass
        _LOGGER.debug("Could not persist the duty-switch record: %s", err)
        return
    rec.dirty = False


def starts_attributes(coord: Any) -> dict[str, float]:
    """The compressor-starts sensor's duty-switch attributes; a pump never arbitrated reads empty."""
    rec = _RECORDS.get(coord)
    return (rec.learner if rec is not None else DutySwitchLearner()).published(dt_util.now())
