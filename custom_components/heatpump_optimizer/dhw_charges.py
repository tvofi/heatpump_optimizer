"""Hot-water charges the pump would start and run, for the planner's plan.

Two stages ``DhwPlanner._build_dhw_requirements`` calls after the planners
have bought the floor. The start condition: the tank temperature below
which the pump starts a charge (:func:`dhw_start_temps`), and the floor
repair under it (:func:`place_startable`), which keeps no charge the pump
would not start. The commit (:func:`commit_charges`), on a solve that plans
runs (:class:`ChargeRuns`): the plan as charges that run at the pump's
floor or above, chosen between the store program's plan
(:class:`_StoreProgram`) and the lifted one.

Pure computation over arrays and the planner's own tank walk; the planner
is passed in, never imported at run time.
"""
from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, Any, Callable, NamedTuple

import numpy as np

from . import runs
from .thermal_model import (
    ThermalParameters,
    ThermalState,
    dhw_start_below_c,
    dhw_step_target_c,
    heat_per_cop_kw,
    power_for_heat_per_cop_kw,
)

if TYPE_CHECKING:
    from .dhw_planner import DhwPlanner, _DhwPlanContext


#: How many times :func:`place_startable` re-buys what the start condition
#: barred before it settles for dropping. A round re-buys under the charges
#: the round before kept, and the measured placements settle in two or three
#: (``dev/audit/harnesses/r10_dhw_start_hysteresis.py``, repair_rounds_max),
#: so eight is that with room to spare and still a bound.
STARTABLE_ROUNDS = 8


def dhw_start_temps(
    params: ThermalParameters, state: ThermalState, n_steps: int, cycle_step: int | None
) -> np.ndarray | None:
    """Per step, the tank temperature below which the pump starts a charge, °C.

    The target the arbiter writes on that step (``dhw_step_target_c`` on the
    set-point entity's grid, ``state.dhw_setpoint_grid``: the cycle's on
    ``cycle_step``, the everyday one elsewhere) less the pump's start
    hysteresis (``state.dhw_start_hysteresis_k``), so a disinfection charge
    is judged against its own target and a stepped entity's against the step
    it lands on. ``None`` where no start condition is known
    (``dhw_start_below_c``).
    """
    hysteresis_k, grid = state.dhw_start_hysteresis_k, state.dhw_setpoint_grid
    everyday = dhw_start_below_c(dhw_step_target_c(params, False, grid), hysteresis_k)
    if everyday is None:
        return None
    start = np.full(n_steps, everyday)
    if cycle_step is not None and 0 <= cycle_step < n_steps:
        start[cycle_step] = dhw_start_below_c(dhw_step_target_c(params, True, grid), hysteresis_k)
    return start


def startable_steps(
    plan: np.ndarray, temps: np.ndarray, start_below: np.ndarray | None
) -> np.ndarray:
    """The steps where charging is something the pump does.

    A step that opens on a tank below its start temperature (``temps[i]``,
    the simulated level at its start), and the step after one of a charge
    under way, which runs on to its target. A charge is under way from the
    step it opens below its start temperature, or from the first step, where
    it is kept as one that may be (:func:`drop_unstartable`); a charge the
    pump would not start carries nothing on, so the repair buys neither
    inside it nor behind it. Every step where no start condition is known
    (``start_below`` ``None``).
    """
    on = np.asarray(plan, dtype=float) > 0.0
    if start_below is None:
        return np.ones(on.size, dtype=bool)
    ok: np.ndarray = np.asarray(temps, dtype=float)[: on.size] < start_below[: on.size]
    under_way = bool(on[:1].any())
    for i in range(1, on.size):
        ok[i] |= under_way
        under_way = bool(on[i] and ok[i])
    return ok


def drop_unstartable(
    plan: np.ndarray, start_below: np.ndarray, temps_of: Callable[[np.ndarray], np.ndarray]
) -> np.ndarray:
    """``plan`` without the charges the pump would never start.

    Each run is judged in time order on the trajectory ``temps_of`` simulates
    for the runs kept before it: one that begins on a tank at or above its
    step's start temperature is removed whole. A run at the first step is
    kept, as it may be a charge already under way (Bankaifan, #3440).
    """
    plan = np.array(plan, dtype=float)
    on = plan > 0.0
    for i in np.flatnonzero(on[1:] & ~on[:-1]) + 1:
        end = i + int(np.argmin(np.append(on[i:], False)))
        if temps_of(plan)[i] >= start_below[i]:
            plan[i:end] = 0.0
    return plan


def place_startable(
    plan: np.ndarray,
    start_below: np.ndarray | None,
    temps_of: Callable[[np.ndarray], np.ndarray],
    repair: Callable[..., np.ndarray],
) -> np.ndarray:
    """The floor repair of ``plan`` under the pump's start condition.

    With no condition, ``repair(plan=plan)``, the call as it always was. With
    one, the charges the pump would not start are dropped and ``repair``,
    handed the condition so it places only on :func:`startable_steps`,
    re-buys what the floor still needs; a top-up
    warms the tank under every later charge, so the two repeat until the
    plan stands, at most :data:`STARTABLE_ROUNDS` times. The plan that leaves
    holds no charge the pump would not start, and is short of the floor only
    where no startable step can hold it.
    """
    if start_below is None:
        return repair(plan=plan)
    for _ in range(STARTABLE_ROUNDS):
        fixed = repair(plan=drop_unstartable(plan, start_below, temps_of), start_below=start_below)
        if np.array_equal(fixed, plan):
            break
        plan = fixed
    return drop_unstartable(plan, start_below, temps_of)


#: How far under a floor a tank may read and still hold it, K: the planners'
#: shortfall tolerance (``DhwPlanner._dhw_shortfall``) and the commit's.
SHORTFALL_K = 0.05

#: The store program's temperature cell, K, and the spacing of its COP table.
#: Constants from the contributor's spike on one install, not measured
#: thresholds: the grid decides how cheap a committed plan is, never whether
#: it ships, which is :func:`charge_refusal`'s on the planner's own walk.
_STORE_GRID_K = 0.25
_COP_KNOT_K = 1.0
#: How far inside its bounds the program keeps its store, K, so the rating
#: clamp trims no committed step on the walk. The linear store and the walk
#: differ by about a thousandth of a kelvin along the fixtures' plans
#: (``dev/audit/harnesses/r11_honest_dhw_runs.py``, ``stores``).
_STORE_MARGIN_K = 0.02


def charge_refusal(
    candidate: np.ndarray,
    start_below: np.ndarray | None,
    temps_of: Callable[[np.ndarray], np.ndarray],
    held: np.ndarray,
) -> tuple[str, int] | None:
    """Why the commit may not ship ``candidate``, or ``None`` where it may.

    ``("start", step)``: on the candidate's own walk the pump would not start
    the charge that opens there (:func:`drop_unstartable` removes it).
    ``("floor", step)``: the walk falls under ``held``, the floors the
    uncommitted plan held, by more than the planners' tolerance. With no
    start condition known every charge is taken to start.
    """
    if start_below is not None:
        lost = np.flatnonzero(drop_unstartable(candidate, start_below, temps_of) != candidate)
        if lost.size:
            return "start", int(lost[0])
    short = np.flatnonzero(temps_of(candidate)[1 : candidate.size + 1] < held - SHORTFALL_K)
    return ("floor", int(short[0])) if short.size else None


def charges_run(plan: np.ndarray, floor: float, tails: bool) -> bool:
    """Every charging step of ``plan`` runs at ``floor`` or above; with
    ``tails``, a charge's last step may end inside it, at any level."""
    on, low = plan > 0.0, (plan > 0.0) & (plan < floor - 1e-9)
    ends = np.r_[False, on[:-1] & ~low[:-1]] & ~np.r_[on[1:], False]
    return not bool(np.any(low & ~(ends & tails)))


def whole_charges(charge_runs: ChargeRuns | None, plan: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """``mask``, the steps a suppression would zero, without the steps of any
    charge it does not cover whole, on a solve that plans runs. A committed
    charge is suppressed whole or kept whole, so no fragment is left shorter
    than a run or under the floor. ``mask`` itself on a solve that does not."""
    if charge_runs is None:
        return mask
    on, kept = np.r_[False, plan > 0.0, False], mask.copy()
    for a, b in zip(np.flatnonzero(on[1:] & ~on[:-1]), np.flatnonzero(~on[1:] & on[:-1])):
        kept[a:b] &= bool(np.all(mask[a:b]))
    return kept


class ChargeRuns(NamedTuple):
    """What a solve that plans runs hands the planner (``optimizer._engaged``):
    a start's price, whether the compressor runs at solve time, and whether
    the install can only run at its floor or above. ``None`` on a solve that
    plans duty-cycle averages, whose hot-water plan is left as planned."""

    start_cost: float
    running: bool
    clamped: bool


class _StoreProgram:
    """The cheapest charges that keep the planner's linear store in bounds:
    ``runs``' program with the tank temperature as its scalar.

    The state is the run or pause length and the tank on a
    :data:`_STORE_GRID_K` grid. A step pauses (``_DhwPlanContext.coast``) or
    charges at the pump's floor or at the run power, at the planning price
    and the COP of the cell's temperature. A charge that would pass the
    ceiling fills the tank to it instead, at the level that takes, where
    that is the floor or above. Under the floor it does so only as a run's
    last step, which ends inside it (the contributor's tail), and only on an
    install that can end a run at any moment. The bounds are the caller's floors
    and, on a charging step, ceilings; a forced-off step stays off, and a
    start is made only where the caller says the pump would make one.

    What a start pays inside the program is ``start_cost`` less the share of
    it the space plan's step before already carries (``runs.running_share``):
    an estimate that steers the search. The committed plan is priced by the
    start count of the combined draw, in :func:`commit_charges`.
    """

    def __init__(
        self,
        planner: DhwPlanner,
        ctx: _DhwPlanContext,
        asked: np.ndarray,
        tank: tuple[float, np.ndarray],
        bounds: tuple[np.ndarray, np.ndarray],
        forced_off: np.ndarray | None,
        space: np.ndarray,
    ) -> None:
        charge, self.params = planner.charge_runs, planner.model.params
        assert charge is not None
        self.ctx, self.asked, (self.initial, self.draws), (self.floors, self.ceilings) = ctx, asked, tank, bounds
        n, floor = ctx.n_steps, runs.floor_kw(self.params.min_electrical_power)
        self.floor, self.levels = floor, sorted({floor, ctx.p_dhw_max})
        self.tails, self.running = not charge.clamped, charge.running
        self.lo = float(np.floor(min(self.initial, float(np.min(self.floors))))) - _COP_KNOT_K
        self.knots = np.arange(
            self.lo, float(np.ceil(max(self.initial, float(np.max(self.ceilings))))) + 2.0 * _COP_KNOT_K, _COP_KNOT_K)
        self.cop = np.array(
            [planner._dhw_cop_profile(ctx.outdoor_temps, np.full(n, t), ctx.humidity) for t in self.knots])
        self.forced = np.where(np.zeros(n, dtype=bool) if forced_off is None else forced_off[:n], 0.0, np.nan)
        before = np.r_[1.0 if charge.running else 0.0, runs.running_share(space, floor)[:-1]]
        self.start_price = charge.start_cost * (1.0 - before)

    def _rise(self, k: int, temp: Any, level: float) -> Any:
        """K a whole step ``k`` at ``level`` kW adds to a tank at ``temp``."""
        heat = np.interp(temp, self.knots, self.cop[:, k]) * heat_per_cop_kw(self.params, level)
        return heat * self.ctx.dt / self.ctx.c_dhw

    def _to_ceiling(self, k: int, temp: Any) -> tuple[Any, Any]:
        """The level that takes a tank at ``temp`` to step ``k``'s ceiling
        by the step's end, kW, and where there is one: a whole step at the
        run power would pass the ceiling and a part of one reaches it."""
        room = self.ceilings[k] - _STORE_MARGIN_K - self.ctx.coast(self.draws, k, temp)
        share = room / self._rise(k, temp, self.levels[-1])
        fills = (share > 0.0) & (share < 1.0)
        return power_for_heat_per_cop_kw(
            self.params, np.where(fills, share, 0.0) * heat_per_cop_kw(self.params, self.levels[-1])), fills

    def _actions(self, k: int) -> tuple[list[runs.Action], list[runs.Action]]:
        """What step ``k`` may do in a run and in a pause. In a run: each
        level, and the fill to the ceiling where its level is the floor or
        above. In a pause: idle, and the tail, a fill under the floor that
        ends the run before it."""
        ctx, price, floor = self.ctx, float(self.ctx.prices[k]) * self.ctx.dt, self.floor
        ran, paused = runs.tie_break(bool(self.asked[k] > 0.0))

        def at(level: float) -> runs.Action:
            return lambda temp, _ran: (ctx.coast(self.draws, k, temp) + self._rise(k, temp, level), price * level + ran)

        def idle(temp: np.ndarray, _ran: bool) -> tuple[np.ndarray, Any]:
            return ctx.coast(self.draws, k, temp), paused

        def fill(temp: np.ndarray, ran_before: bool, tail: bool = False) -> tuple[np.ndarray, Any]:
            level, fills = self._to_ceiling(k, temp)
            under = level < floor - 1e-9
            fills = fills & (under & (level >= ctx.min_run_power) & ran_before if tail else ~under)
            return (
                np.where(fills, self.ceilings[k] - _STORE_MARGIN_K, ctx.coast(self.draws, k, temp)),
                np.where(fills, price * level + ran, np.inf),
            )

        pauses: list[runs.Action] = [idle, partial(fill, tail=True)] if self.tails else [idle]
        return [*(at(level) for level in self.levels), fill], pauses

    def plan(self, may_start: np.ndarray) -> np.ndarray | None:
        """The program's plan, kW per step, or ``None`` where no mask keeps
        the store in bounds."""
        n, dt = self.ctx.n_steps, self.ctx.dt
        lengths = (runs.steps_at_least(runs.MIN_RUN, dt), runs.steps_at_least(runs.MIN_PAUSE, dt))
        width = int(round((self.knots[-1] - self.lo) / _STORE_GRID_K)) + 1
        cost = np.full((sum(lengths), width), np.inf)
        temp = np.zeros_like(cost)
        row = lengths[0] - 1 if self.running else sum(lengths) - 1
        cell = int(round((self.initial - self.lo) / _STORE_GRID_K))
        cost[row, cell], temp[row, cell] = 0.0, self.initial
        trail = []
        for k in range(n):
            def place(t: np.ndarray, charged: bool, k: int = k) -> tuple[np.ndarray, np.ndarray]:
                j = np.rint((t - self.lo) / _STORE_GRID_K).astype(np.int64)
                inside = (t >= self.floors[k] - SHORTFALL_K + _STORE_MARGIN_K) & (j >= 0) & (j < width)
                if charged:
                    inside &= t <= self.ceilings[k] - _STORE_MARGIN_K + 1e-9
                return np.clip(j, 0, width - 1), np.where(inside, 0.0, np.inf)

            cost, temp, back = runs.advance(
                cost, temp, runs.state_moves(*lengths, self.forced[k], bool(may_start[k])),
                self._actions(k), float(self.start_price[k]), place, lengths[0])
            trail.append(back)
        if not np.isfinite(cost).any():
            return None
        mask, action = runs.read_back(trail, cost, lengths[0])
        out, at = np.zeros(n), np.array([self.initial])
        for k in range(n):
            if mask[k] or action[k]:
                out[k] = self.levels[action[k]] if mask[k] and action[k] < len(self.levels) else float(
                    self._to_ceiling(k, at)[0][0])
            at = self._actions(k)[0 if mask[k] else 1][action[k]](at, True)[0]
        return out


    def accepted(
        self, may_start: np.ndarray, fits: Callable[[np.ndarray | None], Any]
    ) -> np.ndarray | None:
        """The program's plan as ``fits`` passes it, where the pump would
        start it: a charge ``fits`` refuses for its start clears that step
        and the program runs again, at most :data:`STARTABLE_ROUNDS` times."""
        for _ in range(STARTABLE_ROUNDS):
            fitted = fits(self.plan(may_start))
            if fitted is None or isinstance(fitted, np.ndarray):
                return fitted
            if fitted[0] != "start":
                break
            may_start[fitted[1]] = False
        return None


def commit_charges(
    planner: DhwPlanner,
    plan: np.ndarray,
    store: tuple[_DhwPlanContext, float, np.ndarray],
    limits: tuple[np.ndarray, np.ndarray],
    forced_off: np.ndarray | None,
    start_below: np.ndarray | None,
    space_demand: np.ndarray | None,
) -> np.ndarray:
    """The planner's finished, uncommitted ``plan`` as charges the pump can
    run, on a solve that plans runs (``planner.charge_runs``). ``plan``
    itself on one that does not, where its cap is under the floor, and where
    it already runs and no start has a price. The finding and the program
    are Bankaifan's (pull request 3529).

    The candidates are the store program's plan and the lifted plan (each
    step under the floor raised to it), each clamped to the rating and kept
    only if every charge runs (:func:`charges_run`) and
    :func:`charge_refusal` passes it on its own walk. The cheapest ships:
    its energy at the planning prices plus the starts of the combined draw,
    so a charge beside a space run is no start. With no candidate, ``plan``,
    which ``place_startable`` already left startable.
    """
    charge, floor = planner.charge_runs, runs.floor_kw(planner.model.params.min_electrical_power)
    ctx, tank = store[0], store[1:]
    if charge is None or ctx.p_dhw_max < floor or ctx.c_dhw <= 0.0 or not np.any(plan > 0.0):
        return plan
    if not charge.start_cost > 0 and charges_run(plan, floor, not charge.clamped):
        return plan
    temps_of = partial(planner._ctx_temps, ctx, *tank)
    walk = temps_of(plan)
    held = np.minimum(limits[0], walk[1:])
    space = np.zeros(ctx.n_steps) if space_demand is None else np.clip(space_demand, 0.0, None)

    def fits(candidate: np.ndarray | None) -> np.ndarray | tuple[str, int] | None:
        """``candidate`` as the rating leaves it, or why it may not ship."""
        if candidate is None:
            return None
        candidate = planner._ctx_clamp(ctx, tank[0], tank[1], limits[1], candidate)
        if not charges_run(candidate, floor, not charge.clamped):
            return "level", 0
        return charge_refusal(candidate, start_below, temps_of, held) or candidate

    def cost(candidate: np.ndarray) -> float:
        starts = runs.start_count(space + candidate, floor, charge.running)
        return float(np.sum(ctx.prices * candidate) * ctx.dt) + charge.start_cost * starts

    program = _StoreProgram(planner, ctx, plan, tank, (held, np.maximum(limits[1], walk[1:])), forced_off, space)
    proposed = (
        program.accepted(startable_steps(plan, walk, start_below), fits),
        fits(np.where((plan > 0.0) & (plan < floor), floor, plan)),
    )
    return min((c for c in proposed if isinstance(c, np.ndarray)), key=cost, default=plan)
