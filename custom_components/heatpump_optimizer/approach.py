"""What the pump draws in a space run's first steps, and in a pause's first.

The finding and its series are Bankaifan's (comment 6944433306 on pull
request 3670). An on/off install holds its running floor, but a space run
entered from a higher compressor state (off, or a hot-water charge) draws well
above the floor for most of an hour before it settles there. Once the gate is
written, the compressor winds down for minutes while the plan books the step
as off. The plan booked the floor; the meter read more.

:class:`ApproachProfile` keeps that evidence. Per age bin since a
**space-run entry** (a step with a space level after one with none) it keeps
the draw while the space ask sat at the floor in force. Per age bin since a
space run's end it keeps the draw while nothing was asked. It keeps the live
run's age too. :func:`entry_levels`
and :func:`ramp_levels` read it as levels by bin, which ``runs.received``
reads as the draw a plan's run takes. Nothing here books a fee: the heat the
excess buys is delivered, so the plan reads it as received draw.

A leaf: numpy and the plan's running rule, no Home Assistant.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any, Deque

import numpy as np

from .const import finite_float
from .thermal_model import planned_draw_runs

#: Age bin width, minutes. This, :data:`BINS`, :data:`RAMP_BINS`,
#: :data:`DEPTH` and :data:`MIN_COUNT` are constants from one install's series
#: (Bankaifan's series D and H), not measured thresholds.
BIN_MIN = 5.0
#: The longest age the entry profile keeps, in bins (2 h): series D settles
#: at the floor after 50 to 60 minutes.
BINS = 24
#: The longest age the ramp-down profile keeps, in bins: series H's wind-down
#: lasted 330 s.
RAMP_BINS = 3
#: Samples kept per bin; a bin's level is their median.
DEPTH = 9
#: Samples a bin needs before it reads as a level.
MIN_COUNT = 3
#: Float slack on an age read into a bin, in bins.
_SLACK = 1e-9


def _bins(n: int) -> list[Deque[float]]:
    return [deque(maxlen=DEPTH) for _ in range(n)]


@dataclass
class ApproachProfile:
    """Draw by age since a space-run entry and since a space run's end."""

    #: Metered draw per :data:`BIN_MIN` bin after an entry, oldest first.
    entry: list[Deque[float]] = field(default_factory=lambda: _bins(BINS))
    #: Metered draw per bin after a space run's end while nothing was asked.
    ramp: list[Deque[float]] = field(default_factory=lambda: _bins(RAMP_BINS))
    #: Epoch seconds the live space run was entered, or ``None``: unknown, or
    #: no space run live (``running`` says which).
    entered_s: float | None = None
    #: Epoch seconds the last space run ended, or ``None``.
    ended_s: float | None = None
    #: Whether the last folded interval asked a space level; ``None`` unknown.
    running: bool | None = None
    #: The configured ``(min, max)`` the evidence belongs to.
    config: tuple[float, float] | None = None
    #: Epoch seconds the last folded interval ended, or ``None``.
    seen_s: float | None = None
    #: The draw expected of the interval in hand where it sits inside the
    #: profile, kW (``draw_range.expect``); not stored: a restart pairs none.
    expected_kw: float | None = None

    def observe(
        self, drawn_kw: float | None, split: tuple[float, float], floor_kw: float,
        start_s: float, end_s: float, *, sample: bool, standby_kw: float,
        tolerance: float, config: tuple[float, float],
    ) -> str | None:
        """Fold one interval ``[start_s, end_s)`` and move the run's clock:
        ``"ramp"`` for a wind-down sample, ``"inside"`` for an entry sample at
        an age the profile still covers, else ``None``.

        ``sample`` is ``draw_range.is_running_space`` for a space interval
        and the learners' gates (not frozen, not distorted, no defrost) for
        one asking nothing. An entry sample is a running space interval whose
        ask sits at or under ``floor_kw`` by ``tolerance``: a higher ask draws
        more by asking more. A ramp-down sample is the first interval after
        a space run, asking nothing, metered above ``standby_kw``. A changed
        ``config`` drops the evidence, as ``DrawRange.observe`` drops its own.
        A gap since the last interval longer than this one (a restart, a
        stall) leaves the run's state unknown: no entry is read across it.
        """
        if self.config != config:
            self.entry, self.ramp, self.config = _bins(BINS), _bins(RAMP_BINS), config
        runs, was = self._clock(split[0], start_s, end_s)
        if drawn_kw is None or not sample:
            return None
        if runs and self.entered_s is not None and split[0] <= (1.0 + tolerance) * floor_kw:
            age_min = (start_s - self.entered_s) / 60.0
            _put(self.entry, age_min, drawn_kw)
            return "inside" if age_min < _levels(self.entry, floor_kw, tolerance).size * BIN_MIN else None
        quiet = not runs and not planned_draw_runs(split[1], modulation_floor=0.0)
        if quiet and was and drawn_kw > standby_kw and self.ended_s is not None:
            _put(self.ramp, (start_s - self.ended_s) / 60.0, drawn_kw)
            return "ramp"
        return None

    def _clock(self, space_kw: float, start_s: float, end_s: float) -> tuple[bool, bool | None]:
        """Move the run's clock by one interval: whether it asks a space
        level, and whether the one before did (``None`` across a gap)."""
        runs = planned_draw_runs(space_kw, modulation_floor=0.0)
        gap = self.seen_s is None or start_s - self.seen_s > end_s - start_s
        was = None if gap else self.running
        self.seen_s, self.running = end_s, runs
        if runs and was is False:
            self.entered_s = start_s
        elif not runs and was:
            self.ended_s, self.entered_s = start_s, None
        elif gap or not runs:
            self.entered_s = None
        return runs, was

    def expect(self, total_kw: float, *, inside: bool) -> float:
        """Keep the draw expected of the interval in hand where it sits
        inside the profile (``expected_kw``); ``total_kw`` back."""
        self.expected_kw = total_kw if inside else None
        return total_kw

    def age_h(self, now_s: float) -> float | None:
        """The live space run's age, hours: ``0.0`` with none live (a step
        that runs space next is an entry), ``None`` where unknown, which books
        no entry and reads as no profile."""
        if self.running is False:
            return 0.0
        if self.running is None or self.entered_s is None or now_s < self.entered_s:
            return None
        return (now_s - self.entered_s) / 3600.0

    def as_dict(self) -> dict[str, Any]:
        return {
            "entry": [[round(v, 3) for v in b] for b in self.entry],
            "ramp": [[round(v, 3) for v in b] for b in self.ramp],
            **({} if self.config is None else {"config": list(self.config)}),
            **({} if self.entered_s is None else {"entered_s": self.entered_s}),
            **({} if self.ended_s is None else {"ended_s": self.ended_s}),
            **({} if self.running is None else {"running": self.running}),
            **({} if self.seen_s is None else {"seen_s": self.seen_s}),
        }

    @classmethod
    def of_record(cls, draw: Any) -> "ApproachProfile":
        """The profile a stored ``DrawRange`` record carries, if any."""
        return cls.from_dict(draw.get("approach") if isinstance(draw, dict) else None)

    @classmethod
    def from_dict(cls, data: Any) -> "ApproachProfile":
        """A stored profile; a bad cell costs that cell, a bad key its field."""
        out = cls()
        out.config = stored_config(data)
        if out.config is None:
            return out
        out.entry = _stored_bins(data.get("entry"), BINS)
        out.ramp = _stored_bins(data.get("ramp"), RAMP_BINS)
        out.entered_s = finite_float(data.get("entered_s"))
        out.ended_s = finite_float(data.get("ended_s"))
        out.seen_s = finite_float(data.get("seen_s"))
        running = data.get("running")
        out.running = running if isinstance(running, bool) else None
        if out.running and out.entered_s is None:
            out.running = None
        return out


def stored_config(data: Any) -> tuple[float, float] | None:
    """A stored record's configured ``(min, max)`` key, or ``None`` where
    unreadable or not finite: the evidence it keys is dropped with it."""
    try:
        lo, hi = (finite_float(v) for v in data["config"])
    except (TypeError, ValueError, KeyError, IndexError):
        return None
    return None if lo is None or hi is None else (lo, hi)


def _put(bins: list[Deque[float]], age_min: float, drawn_kw: float) -> None:
    j = int(np.floor(age_min / BIN_MIN + _SLACK))
    if 0 <= j < len(bins):
        bins[j].append(float(drawn_kw))


def _stored_bins(raw: Any, n: int) -> list[Deque[float]]:
    out = _bins(n)
    for b, cells in zip(out, raw if isinstance(raw, list) else []):
        b.extend(v for cell in (cells if isinstance(cells, list) else []) if (v := finite_float(cell)) is not None and v >= 0.0)
    return out


def _levels(bins: list[Deque[float]], floor_kw: float, tolerance: float) -> np.ndarray:
    """Median per bin, at least ``floor_kw``, up to the first bin with too
    few samples or within ``tolerance`` of the floor: the profile ends there."""
    out: list[float] = []
    for b in bins:
        if len(b) < MIN_COUNT:
            break
        level = max(float(np.median(list(b))), floor_kw)
        if level <= (1.0 + tolerance) * floor_kw:
            break
        out.append(level)
    return np.array(out, dtype=np.float64)


def entry_levels(profile: ApproachProfile | None, floor_kw: float, tolerance: float) -> np.ndarray:
    """The space draw by :data:`BIN_MIN` bin after an entry, kW; empty with
    no evidence above the floor."""
    if profile is None or floor_kw <= 0.0:
        return np.zeros(0)
    return _levels(profile.entry, floor_kw, tolerance)


def ramp_levels(profile: ApproachProfile | None, floor_kw: float, tolerance: float) -> np.ndarray:
    """The draw by bin after a space run's end, kW; empty with no evidence.
    Read against the floor, as the entry is: a wind-down at or under it is
    noise beside the standby draw."""
    if profile is None or floor_kw <= 0.0:
        return np.zeros(0)
    return _levels(profile.ramp, floor_kw, tolerance)
