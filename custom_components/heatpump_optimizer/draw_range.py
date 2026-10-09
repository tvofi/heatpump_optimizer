"""The electrical draw the pump is metered running at, and the plan's clamp to it.

The planner books ``min_electrical_power``..``max_electrical_power`` as the
draw a step may run at and credits COP times that draw as delivered heat.
Nothing checked those two figures against the meter: an install configured
at 14 kW whose pump runs at 1.9-2.55 kW had every plan book levels the pump
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


@dataclass
class DrawRange:
    """Running draw samples and the latched clamp they justify.

    For a consumer reading ``engaged`` (the nameplate notice, the COP floor):
    it says the plan's running levels and the meter disagree, not that a
    configured figure is wrong. A correctly sized pump whose draw follows the
    level it is asked never engages; one whose own controller ignores that
    level engages, sized correctly or not
    (``tools/audit/harnesses/draw_range_evidence.py``, shape ``mild-indep``).
    """

    #: ``(drawn_kw, asked_kw)`` per running sample, oldest first.
    samples: Deque[tuple[float, float]] = field(
        default_factory=lambda: deque(maxlen=WINDOW)
    )
    engaged: bool = False
    #: The configured ``(min, max)`` the samples and the latch belong to.
    config: tuple[float, float] | None = None

    def observed(self) -> tuple[float, float] | None:
        """``(low, high)`` metered running draw, or ``None`` while too few."""
        if len(self.samples) < MIN_SAMPLES:
            return None
        drawn = np.fromiter((s[0] for s in self.samples), dtype=float)
        low, high = np.percentile(drawn, (LOW_PERCENTILE, HIGH_PERCENTILE))
        return float(low), float(high)

    def _metered_range(
        self, cfg_min: float, cfg_max: float
    ) -> tuple[float, float] | None:
        """The configured range with each contradicted end replaced."""
        seen = self.observed()
        if seen is None:
            return None
        low, high = seen
        top = high if high < (1.0 - AGREE_TOLERANCE) * cfg_max else cfg_max
        bottom = cfg_min if abs(low - cfg_min) <= AGREE_TOLERANCE * cfg_min else low
        return min(bottom, top), top

    def _disagrees(self, cfg_min: float) -> bool:
        """Enough running samples where the plan and the meter disagree.

        Only a running level at or above the configured floor is a level the
        pump was asked to RUN at; below it the plan books a duty-cycle average,
        which a running pump overdraws by design.
        """
        on_level = [(d, a) for d, a in self.samples if a >= cfg_min]
        disagree = sum(
            1 for d, a in on_level
            if a > DISAGREE_FACTOR * d or d > DISAGREE_FACTOR * a
        )
        return disagree >= DISAGREE_SHARE * len(self.samples)

    def observe(
        self, drawn_kw: float, asked_kw: float, cfg_min: float, cfg_max: float
    ) -> None:
        """Fold one running sample and update the latch."""
        configured = (float(cfg_min), float(cfg_max))
        if self.config != configured:
            self.samples.clear()
            self.engaged = False
            self.config = configured
        self.samples.append((float(drawn_kw), float(asked_kw)))
        if len(self.samples) >= MIN_SAMPLES and self._disagrees(cfg_min):
            self.engaged = True

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
            "observed_max_kw": None if seen is None else round(seen[1], 3),
            "engaged": self.engaged,
        }

    def as_dict(self) -> dict[str, Any]:
        return {
            "samples": [[round(d, 3), round(a, 3)] for d, a in self.samples],
            "engaged": self.engaged,
            "config": None if self.config is None else list(self.config),
        }

    @classmethod
    def from_dict(cls, data: Any) -> "DrawRange":
        """A stored range; an unreadable sample is dropped, not the record.

        Without a readable configuration the latch is not trusted: the next
        sample re-keys the range and starts the evidence afresh.
        """
        out = cls()
        if not isinstance(data, dict):
            return out
        raw = data.get("samples")
        for entry in raw if isinstance(raw, list) else ():
            try:
                drawn, asked = float(entry[0]), float(entry[1])
            except (TypeError, ValueError, OverflowError, IndexError, KeyError):
                continue
            if np.isfinite(drawn) and np.isfinite(asked) and drawn > RUNNING_FLOOR_KW and asked >= 0.0:
                out.samples.append((drawn, asked))
        try:
            lo, hi = (float(v) for v in data["config"])
        except (TypeError, ValueError, OverflowError, KeyError):
            return out  # samples with no configuration to judge them against
        if not (np.isfinite(lo) and np.isfinite(hi)):
            return out
        out.config = (lo, hi)
        out.engaged = data.get("engaged") is True
        return out


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
) -> None:
    """Fold one interval into ``draw`` when it is a running sample.

    ``split`` is the plan's (space, hot water) ask as the pump can serve
    it; ``params`` the LIVE parameters, whose configured range the latch is
    keyed to.
    """
    space, dhw = split
    if drawn_kw is not None and is_running_space(
        drawn_kw, space, dhw, frozen=frozen, distorted=distorted, defrost=defrost
    ):
        draw.observe(
            drawn_kw, space, params.min_electrical_power, params.max_electrical_power
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
