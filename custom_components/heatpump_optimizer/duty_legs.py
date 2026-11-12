"""The legs a plan step is served in, the switches between them, and what a stop costs.

One concern with one owner, on ``plan_step.py``'s own argument: the pump
arbiter serves a planned both step as a hot-water leg and a heating leg, and
the optimizer prices the switches that serving makes, so two modules need one
rule and neither may import the other. A leaf: numpy, the plan's running rule
and the step width, nothing of Home Assistant.

A switch between duties at constant draw is invisible to the cycling term,
which prices the swing of the combined draw. On an install whose compressor
stops at such a switch (pull request 3420, Bankaifan: hot water to heating,
three times out of three) the stop turns the swing ``|a - b|`` into ``a + b``.
The difference, ``2 * min(a, b)``, is ``min(a, b) / p_max`` cycles in the
cycling term's own unit, and that is the weight a switch carries here, taken
with the learned probability that the direction stops the compressor.

A pair of per-direction values is always ``(hot water to heating, heating to
hot water)``.
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np

from .batchmath import row_sums
from .plan_step import PLAN_STEP_MINUTES
from .thermal_model import MIN_RUNNING_DRAW_KW

#: The shortest single-duty share of a both step; a shorter share goes to
#: the other duty for the whole step (valve travel and compressor cycling).
SPLIT_MIN_MINUTES = 5.0

#: Leg codes of :func:`leg_ends`.
IDLE, SPACE, DHW = 0, 1, 2


def both_step_legs(
    space_kw: float, dhw_kw: float, step_minutes: float = PLAN_STEP_MINUTES
) -> tuple[tuple[str, float], ...]:
    """The legs of a step both circuits run in, in order, each with its minutes.

    Hot water's share is the step's hot-water power over its total (tvofi,
    2026-09-27); a share under :data:`SPLIT_MIN_MINUTES` on either side
    collapses the step onto the other duty. Hot water goes first.
    """
    dhw_min = step_minutes * dhw_kw / (space_kw + dhw_kw)
    if dhw_min < SPLIT_MIN_MINUTES:
        return (("space", step_minutes),)
    if step_minutes - dhw_min < SPLIT_MIN_MINUTES:
        return (("dhw", step_minutes),)
    return (("dhw", dhw_min), ("space", step_minutes - dhw_min))


def _runs(kw: np.ndarray, floor: float | None) -> np.ndarray:
    """``planned_draw_runs`` for one circuit, elementwise (pinned equal by test)."""
    on = kw > MIN_RUNNING_DRAW_KW
    return on if floor is None else on & ~(kw < floor)


def leg_ends(
    space_kw: Any,
    dhw_kw: Any,
    floor: float | None = None,
    step_minutes: float = PLAN_STEP_MINUTES,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Per step: the first leg, the last leg, and whether the step has two.

    The arbiter's rule elementwise: ``step_duty`` reads each circuit alone
    against the plan's ``floor``, and a both step splits by
    :func:`both_step_legs`. ``space_kw`` may be a ``[B, n]`` batch against one
    ``[n]`` hot-water plan.
    """
    space = np.asarray(space_kw, dtype=float)
    dhw = np.asarray(dhw_kw, dtype=float)
    s_on, d_on = _runs(space, floor), _runs(dhw, floor)
    both = s_on & d_on
    dhw_min = step_minutes * dhw / np.where(both, space + dhw, 1.0)
    to_space = both & (dhw_min < SPLIT_MIN_MINUTES)
    to_dhw = both & ~to_space & (step_minutes - dhw_min < SPLIT_MIN_MINUTES)
    two = both & ~to_space & ~to_dhw
    single = np.where(
        (s_on & ~d_on) | to_space, SPACE, np.where((d_on & ~s_on) | to_dhw, DHW, IDLE)
    )
    return np.where(two, DHW, single), np.where(two, SPACE, single), two


def priced_pair(values: Any, upper: float = math.inf) -> tuple[float, float]:
    """A per-direction pair as two floats in ``[0, upper]``, else zero."""
    try:
        pair = [float(v) for v in values]
    except (TypeError, ValueError):
        return 0.0, 0.0
    if len(pair) != 2:
        return 0.0, 0.0
    a, b = (max(v, 0.0) if math.isfinite(v) and v <= upper else 0.0 for v in pair)
    return a, b


#: A boundary pairs each step but the last with the step after it; the legs
#: that meet there and the levels they run at are read through the same pair.
_BEFORE, _AFTER = np.s_[:, :-1], np.s_[:, 1:]


def switch_weights_batch(
    space_matrix: np.ndarray,
    dhw_kw: np.ndarray,
    stop_probability: tuple[float, float],
    p_max: float,
    floor: float | None = None,
) -> np.ndarray:
    """Expected compressor stops at duty switches, in cycles, per row of plans.

    Every pair of consecutive legs of different duty with no idle step
    between weighs ``p * level / p_max``: inside a two-leg step both legs run
    at the step's combined level; across a boundary the stop adds the smaller
    of the two levels. ``row_sums`` reduces each row on its own, so a row is
    :func:`switch_weight` of that plan bit for bit.
    """
    space = np.asarray(space_matrix, dtype=float)
    p_ds, p_sd = stop_probability
    if p_max <= 0:
        return np.zeros(space.shape[0])
    first, last, two = leg_ends(space, dhw_kw, floor)
    level = space + np.asarray(dhw_kw, dtype=float)
    before, after = last[_BEFORE], first[_AFTER]
    stops = np.where(
        (before == DHW) & (after == SPACE),
        p_ds,
        np.where((before == SPACE) & (after == DHW), p_sd, 0.0),
    )
    across = stops * np.minimum(level[_BEFORE], level[_AFTER])
    inside = np.where(two, p_ds * level, 0.0)
    return row_sums(np.concatenate([inside, across], axis=1)) / p_max


def switch_weight(
    space_kw: np.ndarray,
    dhw_kw: np.ndarray,
    stop_probability: tuple[float, float],
    p_max: float,
    floor: float | None = None,
) -> float:
    """The one-row case of :func:`switch_weights_batch`."""
    return float(switch_weights_batch(
        np.asarray(space_kw, dtype=float)[None, :], dhw_kw, stop_probability, p_max, floor
    )[0])


def lost_share(
    stop_probability: tuple[float, float],
    off_seconds: tuple[float, float],
    step_minutes: float = PLAN_STEP_MINUTES,
) -> float:
    """The share of one step a hot-water to heating stop keeps the compressor off.

    Only that direction carries lost time: its stop shortens the heating leg
    that follows, and no install has measured an off time the other way.
    """
    return min(1.0, stop_probability[0] * off_seconds[0] / (step_minutes * 60.0))


def availability(
    space_start_kw: np.ndarray,
    dhw_kw: np.ndarray,
    lost: float,
    floor: float | None = None,
) -> np.ndarray | None:
    """Per step, the share of it the compressor can run after a priced stop.

    One step is charged per hot-water block end: the step holding the heating
    leg that follows the hot-water leg in ``space_start_kw``, the profile the
    solve starts from, because which step that is is the solve's own variable.
    ``None`` when nothing is charged, so the caller makes today's calls on
    today's arrays instead of multiplying by ones.
    """
    if not lost > 0:
        return None
    first, last, two = leg_ends(space_start_kw, dhw_kw, floor)
    charged = two.copy()
    charged[1:] |= (last[:-1] == DHW) & (first[1:] == SPACE)
    if not charged.any():
        return None
    return np.where(charged, 1.0 - lost, 1.0)


def space_headroom(
    p_max: float, dhw_kw: np.ndarray, avail: np.ndarray | None, floor: float | None
) -> np.ndarray:
    """The space draw a hot-water plan leaves, less a stop's lost running time.

    On a duty-cycle install (no ``floor``) a schedule value is a step average
    and the stop is part of the off time, so the bound carries it. On a
    clamped install a value is the level the compressor runs at and the bound
    is today's; :func:`delivered_space` carries the lost time there.
    """
    if avail is None or floor is not None:
        return np.maximum(0.0, p_max - dhw_kw)
    charged: np.ndarray = np.maximum(0.0, avail * p_max - dhw_kw)
    return charged


def delivered_space(
    space_kw: np.ndarray, dhw_kw: np.ndarray, avail: np.ndarray, floor: float | None
) -> np.ndarray:
    """The step average the house receives from a shipped space level.

    On a clamped install the compressor is off for ``1 - avail`` of a step it
    runs at level ``space + dhw``, and hot water keeps the level its planner
    booked. On a duty-cycle install the shipped draw is already the average.
    """
    if floor is None:
        return space_kw
    delivered: np.ndarray = np.maximum(0.0, space_kw - (1.0 - avail) * (space_kw + dhw_kw))
    return delivered


def switch_ban(
    space_kw: np.ndarray, stop_probability: tuple[float, float], floor: float | None
) -> np.ndarray:
    """The steps hot water may not be placed on to avoid a priced switch.

    For hot water to heating: where heating runs in that step or the next, so
    a block can only end into a planned stop or into more hot water. For
    heating to hot water it mirrors onto the previous step.
    """
    on = _runs(np.asarray(space_kw, dtype=float), floor)
    ban = np.zeros(on.shape, dtype=bool)
    if stop_probability[0] > 0:
        ban |= on
        ban[:-1] |= on[1:]
    if stop_probability[1] > 0:
        ban |= on
        ban[1:] |= on[:-1]
    return ban
