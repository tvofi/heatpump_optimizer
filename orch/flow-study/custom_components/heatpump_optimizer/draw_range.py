"""The electrical draw the pump is metered running at, and the plan's clamp to it.

The planner books ``min_electrical_power``..``max_electrical_power`` as the
draw a step may run at and credits COP times that draw as delivered heat.
Nothing checked those two figures against the meter: a pump whose configured
maximum is several times its real running draw had every plan book levels it
never reached, and the heat they were credited with was never delivered.

``DrawRange`` keeps the running samples -- the metered draw beside the space
level the plan asked for -- and answers one question: the range the plan
may book. Until there is evidence the configured figures stand; with it, the
plan is clamped to the metered range. ``is_running_space`` is the one
filter saying which intervals are running samples, from values the
coordinator reads (it alone can see the meter, the freezes, a resistive
element and the defrost window); ``planned_range`` is the one answer to
which installs the clamp applies to and how far. Nothing here takes the
coordinator.

**Why evidence, and a latch.** A pump in mild weather runs well below its
rating, so a low running ceiling alone is not a contradiction of the
configuration: a pump that realizes what it is asked must plan exactly as
before. The clamp engages only once the plan and the meter disagree -- the
plan asked a running level the pump did not draw, or the pump drew well
above a running level it was asked -- in a share of running samples. Once
engaged the plan no longer asks above the clamp, so that same evidence
fades from the window; re-testing it would release the clamp and re-book the
fiction a window later. So it latches for the configuration it judged. Nor
can the metered range release it: a pump that never needs its lowest level
shows a running floor above the configured one however right that is. A
changed configuration is what releases it, with fresh evidence: the samples
it judged were asked by a plan priced on the old figures.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any, Deque

import numpy as np

from .thermal_model import InstallCapability, planned_draw_runs

#: A metered draw at or below this is standby, circulation and controller
#: draw, not the compressor running: it says nothing about the run range.
RUNNING_FLOOR_KW = 0.25
#: Running samples kept: a week of the default half-hour cycle running
#: around the clock, so a season's change in draw walks the window.
WINDOW = 336
#: The clamp waits for this many running samples (a day of continuous
#: running at the default cadence); until then the configured values stand.
MIN_SAMPLES = 48
#: The run range is these percentiles of the running draws, so a meter glitch
#: or a start-up ramp in under a tenth of samples cannot move either end.
LOW_PERCENTILE = 10.0
HIGH_PERCENTILE = 90.0
#: A sample disagrees with the plan when one of asked and drawn exceeds the
#: other by this factor ...
DISAGREE_FACTOR = 1.25
#: ... and the clamp engages when this share of running samples disagree.
DISAGREE_SHARE = 0.25
#: Each configured end stands while the metered end is within this share of
#: it: a correctly configured pump keeps its configured figures.
AGREE_TOLERANCE = 0.15
#: ``follows_ask``: the asked running levels must span this ratio (90th over
#: 10th percentile) before the window can say whether the draw follows them;
#: a flat ask is no test of following.
FOLLOW_ASK_SPAN = 1.15
#: ... and the draw follows when the slope of log drawn on log asked is at
#: least this. A draw proportional to its ask has slope 1, an efficiency shift
#: included (it scales every draw alike); a draw the pump's own controller
#: sets has slope 0 whatever its level. Halfway between the two.
FOLLOW_SLOPE_MIN = 0.5
#: Idle draws kept: a day of the default cycle. An install the arbiter
#: commands through a flow set-point (``command``) is idle while the held
#: set-point is the gate, and its meter then reads the circulation pump and
#: the controller, which on some pumps sit above ``RUNNING_FLOOR_KW``.
IDLE_WINDOW = 48
#: The idle draw is the median of at least this many idle readings ...
MIN_IDLE = 12
#: ... and a sample at or below this multiple of it is that draw, not the
#: compressor: it is no evidence about the run range.
IDLE_MARGIN = 1.25
#: A set-point within this of the ceiling commanded full power: the
#: arbiter writes on the entity's step and rounds the ceiling down.
CEILING_TOLERANCE_K = 0.5
#: A set-point within this of the gate commanded no heat.
GATE_TOLERANCE_K = 0.25


@dataclass
class DrawRange:
    """Running draw samples and the latched clamp they justify.

    For a consumer reading ``engaged`` (the nameplate notice, the COP floor):
    it says the plan's running levels and the meter disagree, not that a
    configured figure is wrong. A correctly sized pump whose draw follows the
    level it is asked never engages; one whose own controller ignores that
    level engages, sized correctly or not
    (``dev/audit/harnesses/draw_range_evidence.py``, shape ``mild-indep``).
    """

    #: ``(drawn_kw, asked_kw)`` per running sample, oldest first.
    samples: Deque[tuple[float, float]] = field(
        default_factory=lambda: deque(maxlen=WINDOW)
    )
    engaged: bool = False
    #: The configured ``(min, max)`` the samples and the latch belong to.
    config: tuple[float, float] | None = None
    #: Beside each sample, ``(written_c, ceiling_c)`` -- the flow set-point
    #: the arbiter held and the ceiling it writes at full power -- or
    #: ``None`` where nothing commanded the draw (the pump's own choice).
    commands: Deque[tuple[float, float] | None] = field(
        default_factory=lambda: deque(maxlen=WINDOW)
    )
    #: Whether ``commands`` describes ``samples``: False for a record stored
    #: before the commands were, whose evidence a commanded install drops.
    commands_known: bool = True
    #: Metered draw while the held set-point was the gate, oldest first.
    idle: Deque[float] = field(default_factory=lambda: deque(maxlen=IDLE_WINDOW))

    def idle_kw(self) -> float | None:
        """The learned idle draw, or ``None`` while too few readings."""
        return float(np.median(self.idle)) if len(self.idle) >= MIN_IDLE else None

    def _evidence(self) -> list[tuple[float, float, bool]]:
        """``(drawn, asked, full)`` per sample that is the compressor running.

        A sample at or below ``IDLE_MARGIN`` times the learned idle draw is
        the idle draw, and is no evidence. ``full``: the command could have
        drawn the maximum -- the ceiling was written, or nothing commanded the
        draw. A sub-ceiling set-point caps what the pump draws (R10-SETPOINT-
        BOOST), so a draw under one says nothing about the pump's maximum: the
        window would otherwise learn the set-points it was written.
        """
        idle = self.idle_kw()
        above = 0.0 if idle is None else IDLE_MARGIN * idle
        return [
            (d, a, cmd is None or cmd[0] >= cmd[1] - CEILING_TOLERANCE_K)
            for (d, a), cmd in zip(self.samples, self._aligned())
            if d > above
        ]

    def _aligned(self) -> list[tuple[float, float] | None]:
        cmds = list(self.commands)
        return cmds if len(cmds) == len(self.samples) else [None] * len(self.samples)

    def observed(self) -> tuple[float, float | None] | None:
        """``(low, high)`` metered running draw, or ``None`` while too few.

        ``high`` is ``None`` while fewer than ``MIN_SAMPLES`` samples could
        have drawn the maximum (``_evidence``).
        """
        evidence = self._evidence()
        if len(evidence) < MIN_SAMPLES:
            return None
        drawn = np.fromiter((e[0] for e in evidence), dtype=float)
        full = np.fromiter((e[0] for e in evidence if e[2]), dtype=float)
        low = float(np.percentile(drawn, LOW_PERCENTILE))
        high = float(np.percentile(full, HIGH_PERCENTILE)) if full.size >= MIN_SAMPLES else None
        return low, high

    def _metered_range(
        self, cfg_min: float, cfg_max: float
    ) -> tuple[float, float] | None:
        """The configured range with each contradicted end replaced."""
        seen = self.observed()
        if seen is None:
            return None
        low, high = seen
        top = high if high is not None and high < (1.0 - AGREE_TOLERANCE) * cfg_max else cfg_max
        bottom = cfg_min if abs(low - cfg_min) <= AGREE_TOLERANCE * cfg_min else low
        return min(bottom, top), top

    def _disagrees(self, cfg_min: float) -> bool:
        """Enough running samples where the plan and the meter disagree.

        Only a running level at or above the configured floor is a level the
        pump was asked to RUN at; below it the plan books a duty-cycle average,
        which a running pump overdraws by design. A pump drawing less than it was asked counts only where the command
        could have drawn the maximum (``_evidence``).
        """
        evidence = self._evidence()
        disagree = sum(
            1 for d, a, full in evidence
            if a >= cfg_min
            and ((full and a > DISAGREE_FACTOR * d) or d > DISAGREE_FACTOR * a)
        )
        return len(evidence) >= MIN_SAMPLES and disagree >= DISAGREE_SHARE * len(evidence)

    def observe(
        self, drawn_kw: float, asked_kw: float, cfg_min: float, cfg_max: float,
        command: tuple[float, float] | None = None,
    ) -> None:
        """Fold one running sample and update the latch.

        ``command`` is the sample's ``(written_c, ceiling_c)``. A commanded
        sample meeting evidence stored without commands drops it, as a
        changed configuration does: what capped those draws is unknown.
        """
        configured = (float(cfg_min), float(cfg_max))
        legacy = command is not None and not self.commands_known
        if self.config != configured or legacy:
            self.samples.clear()
            self.commands.clear()
            self.engaged = False
            self.config = configured
        self.commands_known = True
        self.samples.append((float(drawn_kw), float(asked_kw)))
        self.commands.append(command)
        if self._disagrees(cfg_min):
            self.engaged = True

    def observe_idle(self, drawn_kw: float) -> None:
        """Fold one reading taken while the held set-point was the gate."""
        self.idle.append(float(drawn_kw))

    def planned(
        self, cfg_min: float, cfg_max: float
    ) -> tuple[float, float] | None:
        """``(min, max)`` the plan may book, or ``None``: configured stands."""
        if not self.engaged or self.config != (float(cfg_min), float(cfg_max)):
            return None
        metered = self._metered_range(cfg_min, cfg_max)
        if metered is None or metered == (cfg_min, cfg_max):
            return None
        return metered

    def summary(self) -> dict[str, Any]:
        """The learned values, for the diagnostics download."""
        seen = self.observed()
        return {
            "running_samples": len(self.samples),
            "observed_min_kw": None if seen is None else round(seen[0], 3),
            "observed_max_kw": None if seen is None or seen[1] is None else round(seen[1], 3),
            "idle_kw": None if (idle := self.idle_kw()) is None else round(idle, 3),
            "engaged": self.engaged,
        }

    def as_dict(self) -> dict[str, Any]:
        rows = [
            [round(d, 3), round(a, 3)] + ([None, None] if cmd is None else [cmd[0], cmd[1]])
            for (d, a), cmd in zip(self.samples, self._aligned())
        ]
        return {
            "samples": rows if self.commands_known else [r[:2] for r in rows],
            "engaged": self.engaged,
            "config": None if self.config is None else list(self.config),
            "idle": [round(v, 3) for v in self.idle],
        }

    @classmethod
    def from_dict(cls, data: Any) -> "DrawRange":
        """A stored range; an unreadable sample is dropped, not the record.

        The configuration is the record's key: samples and latch are judged
        against it, so without a readable one the record is dropped whole and
        the evidence starts afresh -- never samples with nothing to judge them
        against, which a reader of ``samples`` alone would misjudge.
        """
        out = cls()
        try:
            lo, hi = (float(v) for v in data["config"])
        except (TypeError, ValueError, OverflowError, KeyError, IndexError):
            return out
        if not (np.isfinite(lo) and np.isfinite(hi)):
            return out
        out.config = (lo, hi)
        out.engaged = data.get("engaged") is True
        raw = data.get("samples")
        rows = raw if isinstance(raw, list) else []
        # A record whose rows carry no command cells predates them.
        out.commands_known = not rows or all(
            isinstance(r, list) and len(r) >= 4 for r in rows
        )
        for entry in rows:
            try:
                drawn, asked = float(entry[0]), float(entry[1])
            except (TypeError, ValueError, OverflowError, IndexError, KeyError):
                continue
            if np.isfinite(drawn) and np.isfinite(asked) and drawn > RUNNING_FLOOR_KW and asked >= 0.0:
                out.samples.append((drawn, asked))
                out.commands.append(_command_cells(entry))
        out.idle.extend(_stored_idle(data.get("idle")))
        return out


def _stored_idle(raw: Any) -> list[float]:
    """The readable idle readings of a stored record; a bad one is dropped."""
    return [
        float(v) for v in (raw if isinstance(raw, list) else ())
        if isinstance(v, (int, float)) and not isinstance(v, bool)
        and np.isfinite(v) and v >= 0.0
    ]


def _command_cells(entry: Any) -> tuple[float, float] | None:
    """A stored row's ``(written_c, ceiling_c)``, or ``None``."""
    try:
        written, ceiling = float(entry[2]), float(entry[3])
    except (TypeError, ValueError, OverflowError, IndexError, KeyError):
        return None
    return (written, ceiling) if np.isfinite(written) and np.isfinite(ceiling) else None


def follows_ask(draw: DrawRange | None) -> bool | None:
    """Whether the metered draw follows the running level the plan asks.

    ``None`` without the evidence: fewer than ``MIN_SAMPLES`` running samples
    asked at or above the configured floor, or asks that never moved
    (``FOLLOW_ASK_SPAN``). Read by the COP learner, whose ratio of drawn to
    asked is an efficiency reading only where the draw follows the ask.
    """
    if draw is None:
        return None
    floor = draw.config[0] if draw.config is not None else 0.0
    pairs = np.array(
        [(d, a) for d, a, _ in draw._evidence() if a >= floor and a > 0.0], dtype=float
    ).reshape(-1, 2)
    if len(pairs) < MIN_SAMPLES:
        return None
    low, high = np.percentile(pairs[:, 1], (LOW_PERCENTILE, HIGH_PERCENTILE))
    if high < FOLLOW_ASK_SPAN * low:
        return None
    asked, drawn = np.log(pairs[:, 1]), np.log(pairs[:, 0])
    asked = asked - asked.mean()
    slope = float(np.dot(asked, drawn - drawn.mean()) / np.dot(asked, asked))
    return slope >= FOLLOW_SLOPE_MIN


def is_running_space(
    drawn_kw: float | None,
    space_kw: float,
    dhw_kw: float,
    *,
    frozen: bool,
    distorted: bool,
    defrost: bool,
) -> bool:
    """One interval is a running sample: the compressor running the space
    level the plan asked for, and nothing else on the meter.

    * a metered draw above standby (``RUNNING_FLOOR_KW``), while the plan
      had the space circuit running -- ``planned_draw_runs`` on the space
      level alone, with no modulation floor: the question is whether the plan
      asked the circuit to run, not whether a switch surface could realize it;
    * no hot water asked: a charge runs at another flow temperature, and
      the plan's DHW level is a configured figure, not this range;
    * the learners not frozen on the meter -- a stale meter, a live
      defrost, an external heat source (``frozen``);
    * no resistive element and no capped compressor on the meter
      (``distorted``);
    * no defrost in the interval just closed, where a flag can say so
      (``defrost``).
    """
    return (
        drawn_kw is not None
        and drawn_kw > RUNNING_FLOOR_KW
        and planned_draw_runs(space_kw, modulation_floor=0.0)
        and not planned_draw_runs(dhw_kw, modulation_floor=0.0)
        and not (frozen or distorted or defrost)
    )


def fold(
    draw: DrawRange,
    drawn_kw: float | None,
    split: tuple[float, float],
    params: Any,
    *,
    frozen: bool,
    distorted: bool,
    defrost: bool,
    command: Any = None,
) -> None:
    """Fold one interval into ``draw`` when it is a running sample.

    ``split`` is the plan's (space, hot water) ask as the pump can serve
    it; ``params`` the LIVE parameters, whose configured range the latch is
    keyed to. ``command`` is the flow set-point the arbiter holds
    (``pump_arbiter.flow_command``: ``written_c``, ``gate_c``,
    ``ceiling_c``), or ``None`` where nothing commands the draw. An interval
    held at the gate with no hot water asked is an idle reading.
    """
    space, dhw = split
    if drawn_kw is not None and not (frozen or distorted or defrost) and command is not None and command.written_c <= command.gate_c + GATE_TOLERANCE_K and not planned_draw_runs(dhw, modulation_floor=0.0):
        draw.observe_idle(drawn_kw)
    if drawn_kw is not None and is_running_space(
        drawn_kw, space, dhw, frozen=frozen, distorted=distorted, defrost=defrost
    ):
        draw.observe(
            drawn_kw, space, params.min_electrical_power, params.max_electrical_power,
            None if command is None else (command.written_c, command.ceiling_c),
        )


def planned_range(
    draw: DrawRange, params: Any, cap: InstallCapability
) -> tuple[float, float] | None:
    """The effective ``(min, max)`` a solve may book, or ``None``.

    ``None`` -- the configured figures stand -- until ``draw`` has the
    evidence, and always where the plan writes the power itself
    (``plan_writes_power``): there the metered draw is the plan's own echo.
    On an install that can duty-cycle the min end stays configured: a level
    below it is an average over the step, which a pump running at its metered
    floor for part of the step delivers, so raising the floor would change a
    correctly configured install's plan.
    """
    if cap.plan_writes_power():
        return None
    cfg_min = float(params.min_electrical_power)
    cfg_max = float(params.max_electrical_power)
    metered = draw.planned(cfg_min, cfg_max)
    if metered is None:
        return None
    low, high = metered
    if cap.can_duty_cycle():
        low = min(cfg_min, high)
    return None if (low, high) == (cfg_min, cfg_max) else (low, high)


def diagnostics_view(
    draw: DrawRange, params: Any, cap: InstallCapability
) -> dict[str, Any]:
    """The learned values and the range they would clamp the plan to."""
    view = draw.summary()
    effective = planned_range(draw, params, cap)
    view["effective_min_kw"] = None if effective is None else round(effective[0], 3)
    view["effective_max_kw"] = None if effective is None else round(effective[1], 3)
    return view
