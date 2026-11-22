"""The legs a plan step is served in, the switches between them, and what a stop costs.

One concern with one owner, on ``plan_step.py``'s own argument. The pump
arbiter serves a planned both step as a hot-water leg and a heating leg, and
the optimizer prices the switches that serving makes. So two modules need one
rule and neither may import the other. A leaf: numpy, the plan's running rule
and the step width, nothing of Home Assistant.

A switch between duties inside a run is invisible to the start term, which
counts the off-to-on edges of the combined draw (``runs``). On an install
whose compressor stops at such a switch (pull request 3420, Bankaifan: hot
water to heating, three times out of three) the stop is a start the plan did
not count. A switch between the levels ``a`` and ``b`` weighs
``min(a, b) / p_max`` cycles, taken with the learned probability that the
direction stops the compressor; weighed at ``p_max`` times the running share
it is that probability of one start.

A pair of per-direction values is always ``(hot water to heating, heating to
hot water)``.
"""
from __future__ import annotations

import math
from typing import Any, NamedTuple

import numpy as np

from .batchmath import AFTER as _AFTER, BEFORE as _BEFORE, row_sums
from .plan_step import PLAN_STEP_MINUTES
from .thermal_model import MIN_RUNNING_DRAW_KW

#: The shortest single-duty share of a both step; a shorter share goes to
#: the other duty for the whole step (valve travel and compressor cycling).
SPLIT_MIN_MINUTES = 5.0

#: Leg codes of :func:`leg_ends`.
IDLE, SPACE, DHW = 0, 1, 2

#: The longest minimum leg: one plan step. Whole steps are never shorter, so
#: only a split step can make a short leg and the rule reads adjacent steps.
LEG_MIN_MAX_MINUTES = PLAN_STEP_MINUTES


class LegRule(NamedTuple):
    """How a both step is served, and the shortest legs (R11-OWNER-MODE-LEGS).

    ``first`` is the duty served first; ``extra`` the minutes past
    :data:`SPLIT_MIN_MINUTES` the second share must reach to be served when
    the switch into it stops the compressor (``None``: it is never merged).
    ``heat_min`` and ``dhw_min`` are the shortest heating leg between two
    hot-water legs and the shortest hot-water leg, in minutes, 0 off;
    ``before`` is the leg code the pump is in as the plan starts, step 0's
    left neighbour.
    """

    first: str
    extra: float | None
    heat_min: float = 0.0
    dhw_min: float = 0.0
    before: int = IDLE


#: The legs of one step, in order, each with its minutes.
Legs = tuple[tuple[str, float], ...]
#: The rule with no learned stop and no minimum leg: hot water first, never merged.
DEFAULT_RULE = LegRule("dhw", None)
_NAMES = {IDLE: "idle", SPACE: "space", DHW: "dhw"}


def leg_minimum(minutes: Any) -> float:
    """A minimum leg in ``[0, LEG_MIN_MAX_MINUTES]``; anything not a finite number is 0, off."""
    try:
        value = float(minutes)
    except (TypeError, ValueError):
        return 0.0
    return min(max(value, 0.0), LEG_MIN_MAX_MINUTES) if math.isfinite(value) else 0.0


def leg_rule(
    stop_probability: tuple[float, float], off_seconds: tuple[float, float],
    heat_min: float = 0.0, dhw_min: float = 0.0, before: int = IDLE,
) -> LegRule:
    """The leg order and whole-step rule of a both step, from the per-direction pairs.

    One rule for the arbiter, which serves the legs (``duty_switch``, fed by
    the learner's latched pairs), and the planner, which prices them (fed by
    the same pairs through its configuration). Space goes first only where
    hot water to heating alone stops the compressor. Where the switch into
    the second duty stops it, a second share shorter than
    :data:`SPLIT_MIN_MINUTES` plus that direction's off time goes to the
    first duty when the next step serves the second. Its delivery then moves
    one step and is not dropped. With no stop priced and no minimum leg this
    is :data:`DEFAULT_RULE`.
    """
    first = "space" if stop_probability[0] > 0 and not stop_probability[1] > 0 else "dhw"
    into = 0 if first == "dhw" else 1
    return LegRule(first, (off_seconds[into] / 60.0 if stop_probability[into] > 0 else None),
                   leg_minimum(heat_min), leg_minimum(dhw_min), before)


def _runs(kw: np.ndarray, floor: float | None) -> np.ndarray:
    """``planned_draw_runs`` for one circuit, elementwise (pinned equal by test)."""
    on = kw > MIN_RUNNING_DRAW_KW
    return on if floor is None else on & ~(kw < floor)


def _split(
    space: np.ndarray, dhw: np.ndarray, floor: float | None, step_minutes: float, rule: LegRule,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Per step, before the minimum legs: first leg, last leg, two legs, the first leg's minutes."""
    s_on, d_on = _runs(space, floor), _runs(dhw, floor)
    both = s_on & d_on
    dhw_min = step_minutes * dhw / np.where(both, space + dhw, 1.0)
    to_space = both & (dhw_min < SPLIT_MIN_MINUTES)
    to_dhw = both & ~to_space & (step_minutes - dhw_min < SPLIT_MIN_MINUTES)
    split = both & ~to_space & ~to_dhw
    lead, trail = (DHW, SPACE) if rule.first == "dhw" else (SPACE, DHW)
    whole = np.zeros(split.shape, dtype=bool)
    if rule.extra is not None:
        second_on, second_min = (s_on, step_minutes - dhw_min) if rule.first == "dhw" else (d_on, dhw_min)
        next_second = np.zeros(np.shape(second_on), dtype=bool)
        next_second[..., :-1] = second_on[..., 1:]
        whole = split & next_second & (second_min < SPLIT_MIN_MINUTES + rule.extra)
    two = split & ~whole
    single = np.where(
        (s_on & ~d_on) | to_space | (whole & (lead == SPACE)), SPACE,
        np.where((d_on & ~s_on) | to_dhw | (whole & (lead == DHW)), DHW, IDLE),
    )
    first_min = np.where(two, dhw_min if lead == DHW else step_minutes - dhw_min, step_minutes)
    return np.where(two, lead, single), np.where(two, trail, single), two, first_min


def _mode_runs(
    first: np.ndarray, last: np.ndarray, two: np.ndarray, first_min: np.ndarray, before: int, step_minutes: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Per leg slot (two per step): its run's minutes, the code left of the run, the code right of it.

    A run is mode time: an idle step writes no mode, so it continues the leg
    before it (``before`` ahead of step 0), and so does a single step's empty
    second slot. A first run continuing ``before`` is joined to the leg the
    pump is in, of unknown length (``inf``); nothing is known right of the
    plan's last run (``IDLE``).
    """
    codes = np.stack([first, np.where(two, last, IDLE)], axis=-1).reshape(*first.shape[:-1], -1)
    minutes = np.stack([first_min, step_minutes - first_min], axis=-1).reshape(codes.shape)
    idx = np.arange(codes.shape[-1])
    known = np.maximum.accumulate(np.where(codes != IDLE, idx, -1), axis=-1)
    codes = np.where(known >= 0, np.take_along_axis(codes, np.maximum(known, 0), axis=-1), before)
    change, edge = np.diff(codes, axis=-1) != 0, np.ones(codes.shape[:-1] + (1,), dtype=bool)
    starts, ends = np.concatenate([edge, change], axis=-1), np.concatenate([change, edge], axis=-1)
    s_idx = np.maximum.accumulate(np.where(starts, idx, 0), axis=-1)
    e_idx = np.flip(np.minimum.accumulate(np.flip(np.where(ends, idx, idx[-1]), -1), axis=-1), -1)
    cum = np.concatenate([np.zeros(codes.shape[:-1] + (1,)), np.cumsum(minutes, axis=-1)], axis=-1)
    run = np.take_along_axis(cum, e_idx + 1, axis=-1) - np.take_along_axis(cum, s_idx, axis=-1)
    run = np.where((s_idx == 0) & (codes == before), math.inf, run)
    left = np.where(s_idx > 0, np.take_along_axis(codes, np.maximum(s_idx - 1, 0), axis=-1), before)
    right = np.where(e_idx < idx[-1], np.take_along_axis(codes, np.minimum(e_idx + 1, idx[-1]), axis=-1), IDLE)
    return run, left, right


def _with_minimums(
    first: np.ndarray, last: np.ndarray, two: np.ndarray, first_min: np.ndarray, rule: LegRule, step_minutes: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """The legs after the minimum-leg rule, to a fixed point.

    R1: a hot-water run shorter than ``dhw_min`` in a split step is lengthened
    to it, the heating leg shrinking; a heating leg left under
    :data:`SPLIT_MIN_MINUTES` serves the step whole hot water. R2: a heating
    run with hot water on both sides and shorter than ``heat_min`` serves its
    step whole hot water. Both only turn legs into hot water or lengthen it,
    so the loop ends; one pass is not enough (a merge makes a new sandwich
    next door), and it is capped at two passes a step.
    """
    heat_min, dhw_min = leg_minimum(rule.heat_min), leg_minimum(rule.dhw_min)
    if not (heat_min > 0 or dhw_min > 0):
        return first, last, two, first_min
    lead_dhw = rule.first == "dhw"
    d_slot = np.arange(first.shape[-1]) * 2 + (0 if lead_dhw else 1)
    s_slot = d_slot + (1 if lead_dhw else -1)
    for _ in range(2 * first.shape[-1] + 1):
        run, left, right = _mode_runs(first, last, two, first_min, rule.before, step_minutes)
        dhw_run, space_run = run[..., d_slot], run[..., s_slot]
        dhw_leg = first_min if lead_dhw else step_minutes - first_min
        short = two & (dhw_run < dhw_min)
        longer = dhw_leg + (dhw_min - dhw_run)
        sandwich = two & (space_run < heat_min) & (left[..., s_slot] == DHW) & (right[..., s_slot] == DHW)
        whole = (short & (step_minutes - longer < SPLIT_MIN_MINUTES)) | sandwich
        lengthen = short & ~whole
        if not (whole.any() or lengthen.any()):
            break
        first, last, two = np.where(whole, DHW, first), np.where(whole, DHW, last), two & ~whole
        stretched = np.where(lengthen, longer if lead_dhw else step_minutes - longer, first_min)
        first_min = np.where(whole, step_minutes, stretched)
    return first, last, two, first_min


def _legs(
    space_kw: Any, dhw_kw: Any, floor: float | None, step_minutes: float, rule: LegRule,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """:func:`_split` then :func:`_with_minimums`: the legs the arbiter serves."""
    space, rule = np.asarray(space_kw, dtype=float), LegRule(*rule)
    dhw = np.broadcast_to(np.asarray(dhw_kw, dtype=float), space.shape)
    return _with_minimums(*_split(space, dhw, floor, step_minutes, rule), rule, step_minutes)


def leg_ends(
    space_kw: Any,
    dhw_kw: Any,
    floor: float | None = None,
    step_minutes: float = PLAN_STEP_MINUTES,
    rule: LegRule = DEFAULT_RULE,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Per step: the first leg, the last leg, and whether the step has two.

    The arbiter's rule elementwise. ``step_duty`` reads each circuit alone
    against the plan's ``floor``. A both step's hot-water share is its
    hot-water power over its total (tvofi, 2026-09-27); a share under
    :data:`SPLIT_MIN_MINUTES` on either side collapses the step onto the
    other duty. ``rule`` orders the legs, merges them onto the first where
    the next step serves the second, and applies the minimum legs.
    ``space_kw`` may be a ``[B, n]`` batch against one ``[n]`` hot-water plan.
    """
    first, last, two, _first_min = _legs(space_kw, dhw_kw, floor, step_minutes, rule)
    return first, last, two


def plan_legs(
    space_kw: Any, dhw_kw: Any, floor: float | None = None, rule: LegRule = DEFAULT_RULE,
    step_minutes: float = PLAN_STEP_MINUTES,
) -> tuple[Legs, ...]:
    """Each step's legs of one plan, in order, each with its minutes: :func:`leg_ends` as legs."""
    first, last, two, first_min = _legs(space_kw, dhw_kw, floor, step_minutes, rule)
    return tuple(
        ((_NAMES[int(f)], float(m)), (_NAMES[int(l)], step_minutes - float(m))) if t
        else ((_NAMES[int(f)], float(step_minutes)),)
        for f, l, t, m in zip(first, last, two, first_min)
    )


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


def switch_weights_batch(
    space_matrix: np.ndarray,
    dhw_kw: np.ndarray,
    stop_probability: tuple[float, float],
    p_max: float,
    floor: float | None = None,
    rule: LegRule = DEFAULT_RULE,
    *,
    level: np.ndarray | None = None,
) -> np.ndarray:
    """Expected compressor stops at duty switches, in cycles, per row of plans.

    Every pair of consecutive legs of different duty with no idle step
    between weighs ``p * level / p_max``, in the direction ``rule`` orders the
    legs. Inside a two-leg step both legs run at the step's combined level; across a boundary the stop adds the smaller
    of the two levels. ``level`` is what the pairs are weighed at, the
    combined draw unless given: ``p_max`` times the running share
    (``runs.running_share``) weighs a pair in starts, so a boundary's switch
    weight and its start share never sum past one start. ``row_sums`` reduces
    each row on its own, so a row is :func:`switch_weight` of that plan bit
    for bit.
    """
    space = np.asarray(space_matrix, dtype=float)
    p_ds, p_sd = stop_probability
    if p_max <= 0:
        return np.zeros(space.shape[0])
    first, last, two = leg_ends(space, dhw_kw, floor, rule=rule)
    if level is None:
        level = space + np.asarray(dhw_kw, dtype=float)
    before, after = last[_BEFORE], first[_AFTER]
    stops = np.where(
        (before == DHW) & (after == SPACE),
        p_ds,
        np.where((before == SPACE) & (after == DHW), p_sd, 0.0),
    )
    across = stops * np.minimum(level[_BEFORE], level[_AFTER])
    inside = np.where(two, (p_ds if rule[0] == "dhw" else p_sd) * level, 0.0)
    return row_sums(np.concatenate([inside, across], axis=1)) / p_max


def switch_weight(
    space_kw: np.ndarray,
    dhw_kw: np.ndarray,
    stop_probability: tuple[float, float],
    p_max: float,
    floor: float | None = None,
    rule: LegRule = DEFAULT_RULE,
    *,
    level: np.ndarray | None = None,
) -> float:
    """The one-row case of :func:`switch_weights_batch`."""
    return float(switch_weights_batch(
        np.asarray(space_kw, dtype=float)[None, :], dhw_kw, stop_probability, p_max, floor, rule,
        level=None if level is None else np.asarray(level, dtype=float)[None, :],
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


def _space_minutes(first: np.ndarray, two: np.ndarray, first_min: np.ndarray, step_minutes: float) -> np.ndarray:
    """Per step, the minutes its legs serve heating."""
    return np.where(two, np.where(first == SPACE, first_min, step_minutes - first_min),
                    np.where(first == SPACE, step_minutes, 0.0))


def availability(
    space_start_kw: np.ndarray,
    dhw_kw: np.ndarray,
    lost: float,
    floor: float | None = None,
    rule: LegRule = DEFAULT_RULE,
    step_minutes: float = PLAN_STEP_MINUTES,
) -> np.ndarray | None:
    """Per step, the share of it heating can run: less a priced stop, less what the minimum legs moved.

    One step is charged ``lost`` per hot-water block end: the step holding
    the heating leg that follows the hot-water leg in ``space_start_kw``
    under ``rule``, the profile the solve starts from, because which step that
    is is the solve's own variable. The minimum legs move a step's heating
    minutes to hot water at its fixed draw (R11-OWNER-MODE-LEGS), so the
    house gets fewer: those minutes over the step come off it too. ``None``
    when nothing is charged, so the caller makes today's calls on today's
    arrays instead of multiplying by ones.
    """
    space, rule = np.asarray(space_start_kw, dtype=float), LegRule(*rule)
    dhw = np.asarray(dhw_kw, dtype=float)
    split = _split(space, dhw, floor, step_minutes, rule)
    first, last, two, first_min = _with_minimums(*split, rule, step_minutes)
    moved = (_space_minutes(split[0], split[2], split[3], step_minutes)
             - _space_minutes(first, two, first_min, step_minutes)) / step_minutes
    charged = two & (first == DHW)
    charged[1:] |= (last[:-1] == DHW) & (first[1:] == SPACE)
    charged &= lost > 0
    if not (charged.any() or (moved > 0).any()):
        return None
    avail: np.ndarray = np.clip(1.0 - moved - np.where(charged, lost, 0.0), 0.0, 1.0)
    return avail


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
    space_kw: np.ndarray,
    stop_probability: tuple[float, float],
    floor: float | None,
    rule: LegRule = DEFAULT_RULE,
) -> np.ndarray:
    """The steps hot water may not be placed on to avoid a priced switch.

    For hot water to heating: where heating runs in that step or the next, so
    a block can only end into a planned stop or into more hot water. Where
    ``rule`` serves space first, a both step ends on its hot-water leg, so
    only heating in the next step bans it. For heating to hot water it
    mirrors onto the previous step.
    """
    on = _runs(np.asarray(space_kw, dtype=float), floor)
    ban = np.zeros(on.shape, dtype=bool)
    if stop_probability[0] > 0:
        if rule[0] == "dhw":
            ban |= on
        ban[:-1] |= on[1:]
    if stop_probability[1] > 0:
        ban |= on
        ban[1:] |= on[:-1]
    return ban
