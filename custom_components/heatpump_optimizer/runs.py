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
from typing import Any, Callable, NamedTuple

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

class Start(NamedTuple):
    """What a start costs :func:`commit`: its price, and the learned entry's
    energy above the level a run out of a pause draws (:meth:`Approach.entry_kwh`)."""

    cost: float
    entry_kwh: float = 0.0


class Approach(NamedTuple):
    """The learned approach a plan's runs draw (``approach.entry_levels``,
    ``approach.ramp_levels``): levels by ``bin_h`` bin after a space-run
    entry and after a run's end, kW, and the live run's age at step 0, hours
    (``ApproachProfile.age_h``: ``0.0`` with none live, ``None`` unknown)."""

    entry: np.ndarray
    ramp: np.ndarray
    age_h: float | None
    bin_h: float

    def entry_kwh(self, level: float) -> float:
        """The entry's energy above ``level``, kWh: what a run started from a
        pause draws beyond its shipped level."""
        return float(np.sum(np.maximum(self.entry - level, 0.0))) * self.bin_h


#: One thing a step may do in a program: from the scalars of the cells it
#: leaves, and whether those cells were running, to the scalars it arrives
#: with and what it pays (infinite where it may not be done).
Action = Callable[[np.ndarray, bool], tuple[np.ndarray, Any]]
#: A program's cell rule: from arriving scalars, and whether they arrive in
#: a run, to their cells and whatever arriving there costs besides (infinite
#: where the scalar is out of bounds).
CellRule = Callable[[np.ndarray, bool], tuple[np.ndarray, np.ndarray]]


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


def _mean_excess(levels: np.ndarray, bin_h: float, age_h: float, dt: float, shipped: float) -> float:
    """The mean over ``[age_h, age_h + dt)`` of ``levels`` (one per ``bin_h``
    bin, none past the last) above ``shipped``, kW."""
    total = 0.0
    for j in range(max(int(age_h // bin_h), 0), min(levels.size, int(np.ceil((age_h + dt) / bin_h)))):
        overlap = min(age_h + dt, (j + 1) * bin_h) - max(age_h, j * bin_h)
        if overlap > 0.0:
            total += max(float(levels[j]) - shipped, 0.0) * overlap
    return total / dt


def received(space: Any, dhw: Any, approach: Approach | None, *, dt: float, p_max: float) -> Any:
    """The space draw the pump takes for a shipped space plan, kW per step,
    given the learned ``approach``. A ``[B, n]`` batch is read row by row, so
    each row is the one-row answer bit for bit.

    A space run is read off the space plan alone (``MIN_RUNNING_DRAW_KW``): a
    charge beside a run is no entry, a charge before one leaves it one. A step
    inside a run at age ``a`` takes the shipped level plus the mean of
    ``approach.entry`` above it over ``[a, a + dt)``: ``max(shipped, entry)``
    at bin resolution. A pause's steps after a run's end take
    ``approach.ramp`` alike, and every other step the shipped level. What is added never
    takes the step above ``p_max`` less its hot water. ``approach.age_h`` is
    the live run's age at step 0: ``0.0`` with no run live, ``None`` unknown,
    which books no entry and no ramp until the plan's next edge. No approach
    or no levels: ``space`` itself, the same object.
    """
    if approach is None or (approach.entry.size == 0 and approach.ramp.size == 0):
        return space
    shipped = np.asarray(space, dtype=float)
    hot = np.broadcast_to(np.asarray(dhw, dtype=float), shipped.shape)
    if shipped.ndim == 2:
        return np.stack([_received_row(shipped[b], hot[b], approach, dt, p_max) for b in range(shipped.shape[0])])
    return _received_row(shipped, hot, approach, dt, p_max)


def _received_row(shipped: np.ndarray, hot: np.ndarray, approach: Approach, dt: float, p_max: float) -> np.ndarray:
    """:func:`received` of one plan: a walk carrying the run's age and the
    time since its end."""
    out = shipped.copy()
    age_h = approach.age_h
    live = age_h is None or age_h > 0.0
    age: float | None = None if age_h is None or age_h <= 0.0 else float(age_h)
    for k in range(shipped.size):
        on = bool(shipped[k] > MIN_RUNNING_DRAW_KW)
        if on != live:
            # an edge: a run entered starts its age at 0, a run left starts the pause's;
            # a run of unknown age leaves no pause to time
            age = 0.0 if on or age is not None else None
        live = on
        if age is None:
            continue
        add = _mean_excess(approach.entry if on else approach.ramp, approach.bin_h, age, dt, float(shipped[k]))
        out[k] = shipped[k] + min(add, max(float(p_max) - float(hot[k]) - float(shipped[k]), 0.0))
        age += dt
    return out


def realizable(total: Any, floor: float) -> bool:
    """Every step off or at the floor or above: the plan runs as it stands."""
    q = np.asarray(total, dtype=float)
    return bool(np.all((q <= 0.0) | (q >= floor_kw(floor) - _SLACK)))


def commit(
    q: Any, prices: Any, floor: float, caps: Any, start_cost: float | Start, band: int,
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
    A :class:`Start` carries the learned entry's energy above the level: a
    run started out of a pause also moves the balance by it and pays its
    step's price for it, so the energy an entry delivers is left out later.
    At zero the run action is :func:`_shift`.
    """
    q = np.asarray(q, dtype=float)
    n = q.size
    min_on = lengths[0]
    start_cost, entry_kwh = start_cost if isinstance(start_cost, Start) else Start(float(start_cost))
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

    def cells(b: np.ndarray, _runs: bool) -> tuple[np.ndarray, np.ndarray]:
        outside = np.maximum(np.abs(b) - half * quantum, 0.0)
        return np.clip(np.rint(b / quantum).astype(np.int64) + half, 0, 2 * half), fine * outside

    for k in range(n):
        ran, paused = tie_break(bool(q[k] > 0.0))
        cost, bal, back = advance(
            cost, bal, state_moves(*lengths, want[k]),
            ([_entry_action((level[k] - q[k]) * dt, price[k] * level[k] * dt + ran, entry_kwh, price[k])], [_shift(-q[k] * dt, paused)]),
            float(start_cost), cells, min_on)
        trail.append(back)
    ending = cost + fine * np.maximum(np.abs(bal) - f * dt / 2.0, 0.0)
    mask = read_back(trail, ending, min_on)[0]
    entered = mask & ~np.r_[bool(running), mask[:-1]]
    walk = np.cumsum(np.where(mask, level, 0.0) * dt + entered * float(entry_kwh) - q * dt)
    tracked = bool(
        np.all(np.abs(walk) <= half * quantum + _SLACK) and abs(walk[-1]) <= f * dt / 2.0 + _SLACK)
    return mask, tracked


def candidates(
    q: Any, prices: Any, floor: float, caps: Any, start_cost: float,
    *, dt: float, running: bool = False, forced: Any = None, entry_kwh: float = 0.0,
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
            q, prices, floor, caps, Start(float(start_cost), entry_kwh), band, dt=dt, running=running,
            forced=forced, lengths=lengths,
        )
        tracked |= exact
        if not any(np.array_equal(mask, m) for m in masks):
            masks.append(mask)
    return masks


def tie_break(asked: bool) -> tuple[float, float]:
    """What running and pausing a step pay for leaving the plan's own on/off
    reading of it (``asked``): a mask that saves nothing keeps the plan's runs."""
    return _TIE_BREAK * (not asked), _TIE_BREAK * asked


def state_moves(min_on: int, min_off: int, want: float, may_start: bool = True) -> list[tuple[int, int, bool]]:
    """``(source, destination, starts)`` state moves one step allows.

    States ``0 .. min_on - 1`` are a run of that many steps plus one (the last
    one long enough to stop), then the pauses alike. A forced step may leave
    any run or pause; otherwise only the long-enough one switches. With
    ``may_start`` false a free step begins no run: the caller's answer to
    whether the pump would start there, which this leaf does not ask.
    """
    last_on, states = min_on - 1, min_on + min_off
    free = bool(np.isnan(want))
    out: list[tuple[int, int, bool]] = []
    if not want == 0.0:
        out += [(i, min(i + 1, last_on), False) for i in range(min_on)]
        if may_start or not free:
            out += [(i, 0, True) for i in range(min_on, states) if not free or i == states - 1]
    if not want == 1.0:
        out += [(i, min(i + 1, states - 1), False) for i in range(min_on, states)]
        out += [(i, min_on, False) for i in range(min_on) if not free or i == last_on]
    return out


def _shift(change: float, paid: float) -> Action:
    """:func:`commit`'s action: the balance moved by ``change`` for ``paid``."""
    return lambda bal, _ran: (bal + change, paid)


def _entry_action(change: float, paid: float, entry_kwh: float, price: float) -> Action:
    """:func:`commit`'s run action: :func:`_shift`, and out of a pause the
    entry's energy above the level besides, at the step's price."""
    if not entry_kwh > 0.0:
        return _shift(change, paid)
    return lambda bal, ran: (bal + change + (0.0 if ran else entry_kwh), paid + (0.0 if ran else price * entry_kwh))


def advance(
    cost: np.ndarray, val: np.ndarray, allowed: list[tuple[int, int, bool]],
    actions: tuple[list[Action], list[Action]], start_cost: float, place: CellRule, min_on: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """One step of a program over (run or pause length, a scalar on a grid):
    the cheapest arrival per cell, its exact scalar, and where it came from.

    ``allowed`` is :func:`state_moves`' answer for the step; ``actions`` are what a
    step into a run and into a pause may do; a start pays ``start_cost``
    besides. ``place`` is the caller's cell rule. The
    scalar is the caller's alone (an energy balance, a tank temperature):
    its meaning, grid and bounds are in the two calls, and each cell keeps
    the exact value of the cheapest path into it, so rounding does not
    accrue. The third layer of the back pointers is the action taken.
    """
    width = cost.shape[1]
    new_cost = np.full_like(cost, np.inf)
    new_val = np.zeros_like(val)
    back = np.zeros((3,) + cost.shape, dtype=np.int32)
    cells = np.arange(width)
    for dest in sorted({m[1] for m in allowed}):
        took = [
            (s, starts, a, *act(val[s], s < min_on))
            for s, d, starts in allowed if d == dest
            for a, act in enumerate(actions[0] if dest < min_on else actions[1])
        ]
        b = np.concatenate([t[3] for t in took])
        j, extra = place(b, dest < min_on)
        c = np.concatenate([cost[s] + paid + start_cost * starts for s, starts, _, _, paid in took]) + extra
        origin, action = (np.concatenate([np.full(width, t[i]) for t in took]) for i in (0, 2))
        came = np.tile(cells, len(took))
        ok = np.isfinite(c)
        if not ok.any():
            continue
        c, b, origin, came, action, j = c[ok], b[ok], origin[ok], came[ok], action[ok], j[ok]
        order = np.lexsort((c, j))
        first = order[np.r_[True, j[order][1:] != j[order][:-1]]]
        new_cost[dest, j[first]] = c[first]
        new_val[dest, j[first]] = b[first]
        back[:, dest, j[first]] = origin[first], came[first], action[first]
    return new_cost, new_val, back


def read_back(trail: list[np.ndarray], ending: np.ndarray, min_on: int) -> tuple[np.ndarray, np.ndarray]:
    """The cheapest path through ``trail`` (one :func:`advance` back pointer
    per step) to the cheapest cell of ``ending``: per step, whether it ran
    and the index of the action it took."""
    u, j = (int(a) for a in np.unravel_index(np.argmin(ending), ending.shape))
    mask, action = np.zeros(len(trail), dtype=bool), np.zeros(len(trail), dtype=np.int64)
    for k in range(len(trail) - 1, -1, -1):
        mask[k], action[k] = u < min_on, trail[k][2, u, j]
        u, j = (int(v) for v in trail[k][:2, u, j])
    return mask, action
