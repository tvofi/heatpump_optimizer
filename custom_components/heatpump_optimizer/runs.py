"""Compressor starts and runs: what a start is in a plan, and which runs ship.

The finding, the count and the commit program are Bankaifan's (pull request
3529), rebuilt here on one owner.

A start is an off-to-on edge of the compressor, whatever level it starts to; a
level change inside a run is none. :func:`start_count` reads them off the
combined draw ``q``. With ``f`` the pump's running floor, a step runs the
share ``r = min(1, q / f)`` of itself and needs the compressor running as it
begins by ``a = min(1, q / MIN_RUNNING_DRAW_KW)``, so it makes the share of a
start its predecessor left open, ``a[k] * (1 - r[k-1])``. On a plan whose
steps are all off or at the floor or above, the sum is the integer number of
off-to-on edges (:func:`edge_count`). A level under the floor is a duty-cycle
average: it leaves its successor a start to make and makes one itself, so
cycling under the floor is counted as the starts it is.

:func:`commit` turns a relaxed plan, one that books levels under the floor as
duty-cycle averages, into an on/off mask of runs and pauses the pump can run
at the relaxed plan's energy: a step raised to the floor is paid for by a step
left out, never raised on its own.

A leaf: numpy, ``row_sums`` and the plan's running rule, nothing of Home
Assistant, so the optimizer, the supply gate and the early cut-off read one
shortest run and pause.
"""
from __future__ import annotations

from datetime import timedelta
from typing import Any

import numpy as np

from .batchmath import AFTER, BEFORE, row_sums
from .thermal_model import MIN_RUNNING_DRAW_KW

#: The shortest run and pause: the supply gate lets no write end a younger
#: one, the early cut-off cuts none, and :func:`candidates` plans none.
MIN_RUN = timedelta(minutes=10)
MIN_PAUSE = timedelta(minutes=10)

#: :func:`commit`'s energy bands, in floor steps either side of the relaxed
#: plan's cumulative energy. These three, :data:`QUANTA_PER_STEP` and
#: :data:`OUT_OF_BAND` are constants from the contributor's spike on one
#: install, not measured thresholds.
BANDS = (2, 6, 24)
#: The balance grid: cells per floor step of energy.
QUANTA_PER_STEP = 4
#: A balance outside its band pays this many times the horizon's dearest
#: price per kWh outside it: penalised, never refused.
OUT_OF_BAND = 10.0
#: What a step pays for leaving the relaxed plan's own on/off reading: a tie
#: break, so a mask that saves nothing keeps the plan's runs.
_TIE_BREAK = 1e-9
#: Float slack on a level or an energy compared against the floor, kW or kWh.
_SLACK = 1e-9


def floor_kw(floor: float) -> float:
    """The running floor a start is counted against, kW; a configured 0 still
    runs at ``MIN_RUNNING_DRAW_KW``."""
    return max(float(floor), MIN_RUNNING_DRAW_KW)


def steps_at_least(span: timedelta, dt_hours: float) -> int:
    """Whole plan steps covering ``span``, at least one."""
    return max(1, int(np.ceil(span.total_seconds() / 3600.0 / dt_hours - _SLACK)))


def running_share(total: Any, floor: float) -> np.ndarray:
    """``r``: the share of each step the compressor runs at the combined draw."""
    return np.clip(np.asarray(total, dtype=float) / floor_kw(floor), 0.0, 1.0)


def start_count_batch(total: np.ndarray, floor: float, running: bool = False) -> np.ndarray:
    """The start count of each row of a ``[B, n]`` batch of combined draws.

    ``running``: the compressor runs at solve time, so a run continuing from
    it is no start. Elementwise up to ``row_sums``, so each row is
    :func:`start_count` of that plan bit for bit.
    """
    rows = np.asarray(total, dtype=float)
    through = np.empty_like(rows)
    through[:, 0] = 1.0 if running else 0.0
    through[AFTER] = running_share(rows, floor)[BEFORE]
    needs = np.clip(rows / MIN_RUNNING_DRAW_KW, 0.0, 1.0)
    count: np.ndarray = row_sums(needs * (1.0 - through))
    return count


def start_count(total: Any, floor: float, running: bool = False) -> float:
    """The one-row case of :func:`start_count_batch`."""
    return float(start_count_batch(np.asarray(total, dtype=float)[None, :], floor, running)[0])


def edge_count(total: Any, running: bool = False) -> int:
    """The off-to-on edges of a plan by its running rule
    (``MIN_RUNNING_DRAW_KW``); none at step 0 while the compressor runs."""
    on = np.asarray(total, dtype=float) > MIN_RUNNING_DRAW_KW
    return int(np.sum(on & ~np.r_[bool(running), on[:-1]]))


def realizable(total: Any, floor: float) -> bool:
    """Every step off or at the floor or above: the plan runs as it stands."""
    q = np.asarray(total, dtype=float)
    return bool(np.all((q <= 0.0) | (q >= floor_kw(floor) - _SLACK)))


def commit(
    q: Any, prices: Any, floor: float, caps: Any, start_cost: float, band: int,
    *, dt: float, running: bool = False, forced: Any = None,
    lengths: tuple[int, int] = (1, 1),
) -> tuple[np.ndarray, bool]:
    """The on/off mask that runs the relaxed plan ``q`` cheapest, and whether
    it tracked ``q``'s energy within its band.

    A dynamic program over the steps with the state (on or off, run or pause
    length up to ``lengths``, energy balance). The balance is the committed
    energy less ``q``'s up to that step, on a grid of
    :data:`QUANTA_PER_STEP` cells per floor step, held within ``band`` floor
    steps and within half a floor step at the end. An on step runs at
    ``max(q, floor)`` under ``caps`` and pays its price; an off-to-on edge
    pays ``start_cost``. ``forced`` is the pin encoding (NaN free, 0 off, 1
    on), and a cap under the floor forces a free step off; a forced step may
    cut a run or a pause short. A balance outside the band is held at the
    edge cell and pays :data:`OUT_OF_BAND` for the energy outside: ``False``
    says the mask left the band, a best effort and never a refusal.
    """
    q = np.asarray(q, dtype=float)
    n = q.size
    min_on = lengths[0]
    f = floor_kw(floor)
    cap = np.broadcast_to(np.asarray(caps, dtype=float), (n,))
    want = np.full(n, np.nan) if forced is None else np.array(forced, dtype=float)[:n]
    want = np.where(np.isnan(want) & (cap < f - _SLACK), 0.0, want)
    level = np.minimum(np.maximum(q, f), cap)
    price = np.broadcast_to(np.asarray(prices, dtype=float), (n,))
    quantum = f * dt / QUANTA_PER_STEP
    half = QUANTA_PER_STEP * int(band)
    fine = OUT_OF_BAND * max(float(np.max(np.abs(price))), 1e-6)
    cost = np.full((sum(lengths), 2 * half + 1), np.inf)
    bal = np.zeros_like(cost)
    cost[min_on - 1 if running else sum(lengths) - 1, half] = 0.0
    trail = []
    for k in range(n):
        asked = bool(q[k] > 0.0)
        step = (
            ((level[k] - q[k]) * dt, price[k] * level[k] * dt + _TIE_BREAK * (not asked)),
            (-q[k] * dt, _TIE_BREAK * asked),
        )
        cost, bal, back = _advance(
            cost, bal, _moves(*lengths, want[k]), step, float(start_cost), (quantum, half, fine), min_on)
        trail.append(back)
    ending = cost + fine * np.maximum(np.abs(bal) - f * dt / 2.0, 0.0)
    u, j = (int(a) for a in np.unravel_index(np.argmin(ending), ending.shape))
    mask = np.zeros(n, dtype=bool)
    for k in range(n - 1, -1, -1):
        mask[k] = u < min_on
        u, j = (int(v) for v in trail[k][:, u, j])
    walk = np.cumsum(np.where(mask, level, 0.0) - q) * dt
    tracked = bool(
        np.all(np.abs(walk) <= half * quantum + _SLACK) and abs(walk[-1]) <= f * dt / 2.0 + _SLACK)
    return mask, tracked


def candidates(
    q: Any, prices: Any, floor: float, caps: Any, start_cost: float,
    *, dt: float, running: bool = False, forced: Any = None,
) -> list[np.ndarray]:
    """:func:`commit`'s distinct masks over :data:`BANDS`, tightest first, at
    the step counts of :data:`MIN_RUN` and :data:`MIN_PAUSE`.

    Where no band tracks, the whole horizon is one more; every mask is
    returned, best efforts included, for the true objective to judge.
    """
    masks: list[np.ndarray] = []
    lengths = (steps_at_least(MIN_RUN, dt), steps_at_least(MIN_PAUSE, dt))
    tracked = False
    for band in (*BANDS, int(np.size(q))):
        if tracked and band > BANDS[-1]:
            break
        mask, exact = commit(
            q, prices, floor, caps, start_cost, band, dt=dt, running=running,
            forced=forced, lengths=lengths,
        )
        tracked |= exact
        if not any(np.array_equal(mask, m) for m in masks):
            masks.append(mask)
    return masks


def _moves(min_on: int, min_off: int, want: float) -> list[tuple[int, int, bool]]:
    """``(source, destination, starts)`` state moves one step allows.

    States ``0 .. min_on - 1`` are a run of that many steps plus one (the last
    one long enough to stop), then the pauses alike. A forced step may leave
    any run or pause; otherwise only the long-enough one switches.
    """
    last_on, states = min_on - 1, min_on + min_off
    free = bool(np.isnan(want))
    out: list[tuple[int, int, bool]] = []
    if not want == 0.0:
        out += [(i, min(i + 1, last_on), False) for i in range(min_on)]
        out += [(i, 0, True) for i in range(min_on, states) if not free or i == states - 1]
    if not want == 1.0:
        out += [(i, min(i + 1, states - 1), False) for i in range(min_on, states)]
        out += [(i, min_on, False) for i in range(min_on) if not free or i == last_on]
    return out


def _advance(
    cost: np.ndarray, bal: np.ndarray, moves: list[tuple[int, int, bool]],
    step: tuple[tuple[float, float], tuple[float, float]], start_cost: float,
    grid: tuple[float, int, float], min_on: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """One step of :func:`commit`: the cheapest arrival per cell, its exact
    balance, and where it came from.

    ``step`` is ``(balance change, cost)`` for running and for pausing;
    ``grid`` is the cell width, the band's half width in cells and the price
    of a kWh outside the band.
    """
    quantum, half, fine = grid
    width = cost.shape[1]
    new_cost = np.full_like(cost, np.inf)
    new_bal = np.zeros_like(bal)
    back = np.zeros((2,) + cost.shape, dtype=np.int32)
    cells = np.arange(width)
    for dest in sorted({m[1] for m in moves}):
        srcs = [(s, starts) for s, d, starts in moves if d == dest]
        change, paid = step[0] if dest < min_on else step[1]
        b = np.concatenate([bal[s] + change for s, _ in srcs])
        outside = np.maximum(np.abs(b) - half * quantum, 0.0)
        c = np.concatenate([cost[s] + paid + start_cost * starts for s, starts in srcs]) + fine * outside
        origin = np.concatenate([np.full(width, s) for s, _ in srcs])
        came = np.tile(cells, len(srcs))
        j = np.clip(np.rint(b / quantum).astype(np.int64) + half, 0, 2 * half)
        ok = np.isfinite(c)
        if not ok.any():
            continue
        c, b, origin, came, j = c[ok], b[ok], origin[ok], came[ok], j[ok]
        order = np.lexsort((c, j))
        first = order[np.r_[True, j[order][1:] != j[order][:-1]]]
        new_cost[dest, j[first]] = c[first]
        new_bal[dest, j[first]] = b[first]
        back[0, dest, j[first]] = origin[first]
        back[1, dest, j[first]] = came[first]
    return new_cost, new_bal, back
