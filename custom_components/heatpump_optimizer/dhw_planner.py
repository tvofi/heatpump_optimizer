"""The hot-water planner: when the DHW tank is charged over the horizon.

Hot water is a deferrable on/off load, so the optimizer plans it before space
heating rather than handing it to the gradient solver, which would smear it
into an unrealizable trickle. ``DhwPlanner._build_dhw_requirements`` turns the
demand windows, the learned draw profile, the anti-legionella cycle and any
manual pins into a per-step temperature floor, then plans the cheapest charge
that holds it: a linear program (``_plan_dhw_min_cost``) with a greedy
fallback (``_plan_dhw_cheapest_first``), repaired against the real tank
simulation (``_repair_dhw_floor``, ``_clamp_dhw_to_capacity``,
``_apply_dhw_min_run``).

``HeatPumpOptimizer.optimize`` builds one planner per solve from explicit
inputs -- the thermal model, the PV export price, and that solve's PV surplus
and price-known mask -- and passes it down to the two DHW builds a solve
makes. The planner writes no attribute after construction: everything it
decides is in what it returns (#1743).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable, NamedTuple, Protocol

import numpy as np
from scipy.optimize import linprog

from . import pv
from .const import DHW_QUANTILE_MIN_EVENTS
from .dhw_draws import window_label as draw_window_label
from .dhw_schedule import (
    FULL_DAY,
    Window,
    format_windows,
    hour_in_windows,
    hours_until_next_window,
    parse_windows,
    windows_for_day,
)
from .manual_plan import _pin_is_free
from .thermal_model import (
    TANK_ROOM_AMBIENT_TEMP,
    ThermalModel,
    ThermalParameters,
    ThermalState,
    WeatherSeries,
    _mean_humidity,
    _step_humidity,
    dhw_coil_draw_reduction,
    dhw_draw_scale,
)

_LOGGER = logging.getLogger(__name__)


def _dhw_windows_at(
    weekly: list[list[Window]] | None,
    step_weekdays: np.ndarray | None,
    index: int,
    windows: list[Window],
    holiday_windows: list[Window] | None,
    holiday_flags: np.ndarray | None,
    day_overrides: list[list[Window] | None] | None = None,
) -> list[Window]:
    weekday = None if step_weekdays is None else int(step_weekdays[index])
    holiday = False
    if holiday_flags is not None and index < len(holiday_flags):
        holiday = bool(holiday_flags[index])
    return windows_for_day(
        weekly,
        weekday,
        windows,
        holiday_windows=holiday_windows,
        holiday=holiday,
        day_overrides=day_overrides,
    )


# How far either side of a contended step space heating may look for spare
# compressor capacity when its energy is displaced by hot water. Beyond a few
# hours the building has already lost the heat, so a cheap slot that far away
# is not a real substitute.
_DHW_REFILL_WINDOW_HOURS = 6.0


#: Steps the DHW min-run repair extends a raised slot by before it checks the
#: tank against its ceiling again (``_dhw_raise_fits``): two hours at the
#: 15-minute step, so a refusal stops within that of its first breach.
_DHW_MIN_RUN_CHUNK = 8


def _tank_decay(ua: float, dt: float, c_dhw: float) -> tuple[float, float]:
    """The tank's per-step recursion ``T' = decay * T + gain - draw``: the share of stored heat kept,
    guarded so an absurdly leaky tank or a long step cannot make it negative (unstable), and the
    standby gain from the room around the tank. The one copy the LP, the run-up walk and the
    floor repair share."""
    return float(np.clip(1.0 - ua * dt / c_dhw, 0.0, 1.0)), ua * TANK_ROOM_AMBIENT_TEMP * dt / c_dhw


def _within_ceiling(requirement: Any, max_temp: Any) -> tuple[np.ndarray, np.ndarray]:
    """The requirement held to each step's own ceiling, and the ceiling, as float arrays.

    A requirement above the ceiling can never be met, and asking for it would only make a planner
    give up; elementwise, so the disinfection requirement survives at the one step whose ceiling
    was raised for it."""
    ceiling = np.asarray(max_temp, dtype=float)
    return np.minimum(np.asarray(requirement, dtype=float), ceiling), ceiling


def _forced_off_with(
    forced_off: np.ndarray | None, off_steps: Any, n_steps: int
) -> np.ndarray:
    """``forced_off`` with the quiet Off window's steps OR'd in (#1910).

    The one place the off mask is fitted to the horizon: cut to
    ``n_steps``, padded False, and merged with whatever pins and blocks
    already forced off. All-zero on no off steps is fine — the callers
    gate on ``off_steps is not None`` for the semantics, not the mask.
    """
    mask = np.asarray(off_steps, dtype=bool)[:n_steps]
    if mask.size < n_steps:
        mask = np.concatenate(
            [mask, np.zeros(n_steps - mask.size, dtype=bool)]
        )
    if forced_off is None:
        return mask
    return forced_off | mask


def _legionella_off_mask(off_steps: Any, n_steps: int) -> np.ndarray | None:
    """The Off window as a horizon mask, or None when there is no window."""
    if off_steps is None:
        return None
    return _forced_off_with(None, off_steps, n_steps)


def _legionella_charge(
    n_steps: int, p_dhw_run: float, off: np.ndarray | None
) -> np.ndarray:
    """Flat-out DHW power for the reach simulation, zero on Off steps.

    The tank cannot heat during an Off window. A reach computed as if
    those steps ran would call a step reachable that the window then
    deletes, and the cycle would never be bought.
    """
    power = np.full(n_steps, p_dhw_run)
    if off is None:
        return power
    return np.where(off, 0.0, power)


def _place_legionella_step(
    prices: np.ndarray, first: int, limit: int, off: np.ndarray | None
) -> int | None:
    """Cheapest step in ``[first, limit)`` the Off window leaves runnable.

    When that slice is entirely off, the earliest later free step: the
    cycle is bought in the steps that remain. None when none remain.
    With no window this is ``first + argmin(prices[first:limit])``.
    """
    if off is None:
        return first + int(np.argmin(prices[first:limit]))
    window = off[first:limit]
    if bool(np.all(window)):
        later = np.flatnonzero(~off[first:])
        if later.size == 0:
            return None
        return first + int(later[0])
    scored = np.array(prices[first:limit], dtype=float, copy=True)
    scored[window] = np.inf
    return first + int(np.argmin(scored))


def _drop_off_steps(mask: np.ndarray, off: np.ndarray | None) -> np.ndarray:
    """``mask`` with Off steps removed. The same array when there is no window."""
    if off is None:
        return mask
    # The numpy stub types ``&`` of two unparameterised ndarrays as ``Any``.
    # The annotated name is what ``-> np.ndarray`` returns; a bare return of
    # the expression is the ruler's ``no-any-return``.
    kept: np.ndarray = mask & ~off
    return kept


class _DhwLegionellaPlan(NamedTuple):
    """What the anti-legionella stage decides, and the ceilings it sets."""

    due: bool
    hour: float | None
    step: int | None
    max_temp: "np.ndarray"
    lp_max_temp: "np.ndarray"
    runup_temps: "np.ndarray"


@dataclass(frozen=True)
class DhwPlan:
    """The 14 keys ``_build_dhw_requirements`` already returns.

    Assembled at that method's ``return`` — not a state object threaded
    through the planner. Fields are exactly the published dict's keys.
    """

    floor_temps: np.ndarray
    ready_temps: np.ndarray
    draw_rates: np.ndarray
    in_window: np.ndarray
    max_temp: float
    schedule: np.ndarray
    windows_text: str
    windows_learned: bool
    next_window_in_hours: float | None
    legionella_due: bool
    legionella_hour: float | None
    legionella_step: int | None
    external_heat_suppressed_steps: int
    max_lead_hours: float


@dataclass(frozen=True)
class _DhwPlanContext:
    """What the three DHW planners share, built once per plan (#1776).

    The derived price series the plan is bought at (the surplus-covered
    fraction priced at the export rate), the horizon geometry and the tank
    envelope -- run power, energy cost, standby floor and lead time -- used
    to travel as positional lists through three near-identical signatures.
    The floor repair ranks its top-ups at the RAW import price instead -- a
    top-up buys real energy, not the plan's smoothed view of it -- so the
    raw series travels beside the derived one.
    """

    prices: np.ndarray
    import_prices: np.ndarray
    outdoor_temps: np.ndarray
    humidity: np.ndarray | None
    n_steps: int
    dt: float
    c_dhw: float
    p_dhw_max: float
    min_run_power: float
    max_lead_steps: int


class _Horizon(Protocol):
    """The planner's read-only view of the optimizer's per-solve horizon.

    ``optimizer._Horizon`` satisfies it structurally; declaring the fields
    here keeps this module free of an import of ``optimizer``, which imports
    it.
    """

    @property
    def initial_state(self) -> ThermalState: ...
    @property
    def prices(self) -> np.ndarray: ...
    @property
    def n_steps(self) -> int: ...
    @property
    def dt(self) -> float: ...
    @property
    def step_hours(self) -> np.ndarray: ...
    @property
    def outdoor_temps(self) -> np.ndarray: ...
    @property
    def wind_speeds(self) -> np.ndarray: ...
    @property
    def precipitation(self) -> np.ndarray: ...
    @property
    def solar_radiation(self) -> np.ndarray: ...
    @property
    def external_heat_kw(self) -> np.ndarray | None: ...
    @property
    def valve_targets(self) -> np.ndarray | None: ...
    @property
    def humidity(self) -> np.ndarray | None: ...
    @property
    def dhw_pins(self) -> np.ndarray | None: ...
    @property
    def step_weekdays(self) -> np.ndarray | None: ...
    @property
    def holiday_flags(self) -> np.ndarray | None: ...


class _PlannerConfig(Protocol):
    """The one optimizer setting the planner prices with."""

    @property
    def pv_export_price(self) -> float: ...


class DhwPlanner:
    """Plans the hot-water charge for one solve; built once per ``optimize``.

    Every input is explicit and fixed at construction. ``pv_surplus`` and
    ``price_known`` default to None, which is what a fresh optimizer held
    before its first solve.
    """

    def __init__(
        self,
        model: ThermalModel,
        config: _PlannerConfig,
        pv_surplus: np.ndarray | None = None,
        price_known: np.ndarray | None = None,
    ) -> None:
        self.model = model
        self.config = config
        self._pv_surplus = pv_surplus
        self._price_known = price_known

    def _dhw_planning_prices(
        self,
        prices: np.ndarray,
        p_dhw_run: float,
        space_demand: np.ndarray | None = None,
    ) -> np.ndarray:
        """The per-step prices the hot-water planners rank steps by.

        A DHW block draws a fixed power, so its piecewise PV cost folds into
        one blended per-kWh rate per step (`pv.blended_block_prices`). On the
        co-optimization replan the space profile is already known and takes
        its share of the surplus first.
        """
        surplus = self._pv_surplus
        if surplus is None or not np.any(surplus[: len(prices)] > 1e-6):
            return prices
        surplus = surplus[: len(prices)]
        if space_demand is not None:
            surplus = np.clip(surplus - space_demand[: len(prices)], 0.0, None)
        return pv.blended_block_prices(
            prices, surplus, self.config.pv_export_price, p_dhw_run
        )

    def _baseline_dhw_economics(
        self,
        initial_state: ThermalState,
        outdoor_temps: np.ndarray,
        n_steps: int,
        dhw_setpoint: float,
        energy_cost_of: Callable[[np.ndarray], Any],
        baseline_power: np.ndarray,
        optimal_space: np.ndarray,
        optimal_dhw: np.ndarray,
        humidity: np.ndarray | None = None,
    ) -> tuple[np.ndarray, float, float, float]:
        """Always-hot DHW baseline, then the space/DHW cost split.

        The baseline house keeps the tank at setpoint around the clock.
        That costs draw plus standby, converted through COP. The three
        money figures are piecewise in the PV surplus, like the objective.
        """
        # Baseline DHW: an always-hot tank held at the setpoint. That costs the
        # energy drawn off as hot water plus the standby loss of keeping a tank
        # at setpoint around the clock, which is exactly the behaviour the
        # demand time frames exist to avoid.
        p = self.model.params
        cop_dhw = max(
            self.model.compute_cop_dhw(
                float(np.mean(outdoor_temps)), dhw_setpoint,
                humidity=_mean_humidity(humidity),
            ),
            1e-3,
        )
        standby_loss = p.dhw_tank_heat_loss_coefficient * max(
            dhw_setpoint - TANK_ROOM_AMBIENT_TEMP, 0.0
        )
        baseline_draw = p.dhw_draw_power
        if (
            p.dhw_coil_active
            and initial_state.wood_tank_temperature is not None
        ):
            # The baseline house owns the same refill coil (v3.15.1) — the
            # plumbing is not optimizer value. Held at the initial wood
            # temperature for the whole day: the real coil weakens as the
            # tank cools, so this makes the baseline at least as cheap as
            # reality and the reported savings err low, never high.
            baseline_draw, _ = dhw_coil_draw_reduction(
                baseline_draw,
                initial_state.wood_tank_temperature,
                p.dhw_setpoint,
                # The same inlet reference the draw itself was computed from;
                # see dhw_coil_draw_reduction for why the two must agree.
                inlet_temp=p.dhw_inlet_reference,
            )
        baseline_dhw = np.full(n_steps, (baseline_draw + standby_loss) / cop_dhw)
        # All three figures are piecewise in the PV surplus, like the objective.
        # The baseline house would self-consume the same sun, so pricing only
        # the optimized plan that way would manufacture fictitious savings.
        baseline_cost = float(energy_cost_of(baseline_power + baseline_dhw))
        total_optimal_power = optimal_space + optimal_dhw
        predicted_cost = float(energy_cost_of(total_optimal_power))
        # Hot water's share is its marginal cost on top of space heating, so
        # the two attributions sum exactly to the total.
        dhw_cost = predicted_cost - float(energy_cost_of(optimal_space))
        return baseline_dhw, baseline_cost, predicted_cost, dhw_cost

    # ------------------------------------------------------------------
    # DHW demand-window planning
    # ------------------------------------------------------------------

    def _effective_dhw_windows(self) -> tuple[list[Window], bool]:
        """Return the demand windows to plan against and whether they're learned.

        When the user configured explicit windows those are authoritative. When
        the schedule is switched off, hot water is required around the clock —
        the pre-2.3 behaviour. In between (schedule on but no windows entered)
        the windows are derived from the learned hourly usage profile, so the
        optimizer still avoids keeping the tank hot when nobody draws water.
        """
        params = self.model.params
        if params.dhw_windows_active:
            return list(params.dhw_windows), False
        if not params.dhw_schedule_enabled:
            return [FULL_DAY], False

        pattern = params.effective_dhw_draw_pattern()
        threshold = max(1.0, float(np.percentile(pattern, 60)))
        busy_hours = [h for h in range(24) if pattern[h] >= threshold]
        if not busy_hours:
            return [FULL_DAY], True

        learned: list[Window] = []
        run_start = busy_hours[0]
        prev = busy_hours[0]
        for hour in busy_hours[1:]:
            if hour == prev + 1:
                prev = hour
                continue
            learned.append((float(run_start), float(prev + 1)))
            run_start = hour
            prev = hour
        learned.append((float(run_start), float(prev + 1)))
        return parse_windows(format_windows(learned)) or [FULL_DAY], True

    def _dhw_legionella_due(
        self,
        h: _Horizon,
        *,
        params: ThermalParameters,
        hours_mod: np.ndarray,
        draw_rates: np.ndarray,
        ready_temps: np.ndarray,
        p_dhw_run: float,
        dhw_prices: np.ndarray,
        off_steps: np.ndarray | None = None,
    ) -> tuple[bool, float | None, int | None]:
        """Whether the anti-legionella cycle is due, and which step it lands on.

        The decision half of the cycle (#224 stage 1), verbatim. Returns
        ``(due, hour, step)``; the ceilings the cycle then needs are
        ``_dhw_legionella_ceilings``.
        """
        initial_state = h.initial_state
        n_steps = h.n_steps
        dt = h.dt
        outdoor_temps = h.outdoor_temps
        humidity = h.humidity
        legionella_due = False
        legionella_hour: float | None = None
        legionella_step: int | None = None
        interval_hours = float(params.dhw_legionella_interval_days) * 24.0
        hours_since = initial_state.dhw_hours_since_legionella
        if (
            params.dhw_legionella_enabled
            and interval_hours > 0
            and hours_since is not None
            and n_steps > 0
        ):
            hours_remaining = interval_hours - float(hours_since)
            deadline_step = int(np.floor(hours_remaining / dt))
            place_idx: int | None = None
            # The earliest step the tank can physically be AT the disinfection
            # temperature by, charging flat out from where it is now. Both
            # branches below need it: a cycle target the tank cannot reach by
            # its step is not a plan, it is a constraint the solver quietly
            # relaxes. (The elastic branch has always applied this; the hard
            # deadline used not to, which is what let an overdue cycle pin
            # step 0 — see below.)
            # Simulated rather than estimated. A closed-form lift ÷ rate
            # ignores the draws and the standby losses the charge has to pay
            # for on the way, and one fixed COP ignores how the same pump
            # slows down as the tank warms. On a big tank with a small pump
            # that was wrong by hours: it called step 91 of 96 reachable on a
            # 3000 L tank that actually tops out at 52 °C, so the cycle was
            # pinned near the end of every plan, never became the current
            # action, and the shortfall was never observed, never reported
            # and never retried. This is the same simulation every later
            # stage runs, so the two cannot disagree about what is reachable.
            off = _legionella_off_mask(off_steps, n_steps)
            ramp = np.asarray(
                self.model.simulate_dhw_only(
                    initial_temp=float(initial_state.dhw_temperature),
                    dhw_power_schedule=_legionella_charge(n_steps, p_dhw_run, off),
                    outdoor_temps=outdoor_temps,
                    draw_rates=draw_rates,
                    dt_hours=dt,
                    humidity=humidity,
                )
            )
            hot = np.where(ramp[1:] >= params.dhw_legionella_temp - 1e-6)[0]
            reach_step = int(hot[0]) if hot.size else n_steps
            if deadline_step < n_steps:
                # The hard deadline is inside this horizon: place the cycle
                # at the cheapest hour before it, elastic or not. Hygiene
                # never waits for a better price.
                #
                # An OVERDUE cycle (a negative deadline, from a timer that
                # never got its reset) used to collapse this to
                # ``limit = 1`` and pin the requirement on step 0 of every
                # single solve. Step 0 is the one step the tank provably
                # cannot reach 60 °C in, so the requirement was missed, the
                # timer stayed overdue, and the next solve pinned step 0
                # again — a latch that never disinfected anything. Overdue
                # therefore means "at the cheapest step from the moment the
                # tank can actually be there", not "now".
                if reach_step >= n_steps:
                    # The tank cannot be AT the disinfection temperature
                    # anywhere in this horizon — a big tank, a small pump, or
                    # simply a cold start. Clamping the placement to the
                    # last step is the worst of the three options: the
                    # cycle is then never the current action, so the boost
                    # is never commanded, the tracker never runs, and the
                    # "cannot reach temperature" notice can never be
                    # raised — a permanent latch nobody is told about.
                    # Starting at the first step the pump may run is what
                    # makes progress: the tank charges, the next solve starts
                    # warmer, `reach_step` shrinks, and if it never does, the
                    # shortfall is observed and reported. An Off window on
                    # step 0 moves that start to the next free step.
                    place_idx = _place_legionella_step(dhw_prices, 0, 1, off)
                else:
                    first = min(max(reach_step, 0), n_steps - 1)
                    limit = max(first + 1, min(deadline_step + 1, n_steps))
                    place_idx = _place_legionella_step(
                        dhw_prices, first, limit, off
                    )
            elif (
                params.dhw_elastic_legionella_enabled
                and params.dhw_legionella_price_ceiling is not None
                and float(hours_since)
                >= float(params.dhw_legionella_min_interval_days) * 24.0
            ):
                # #47: inside the elastic window the cycle shops. Run it
                # early only when a *known* price beats what a typical
                # remaining day is expected to bottom out at (the ceiling,
                # from the learned prior). Prior-guessed steps never
                # qualify — a cycle is real money spent on a guess. The
                # ceiling exists only once the prior is fully trained
                # (None otherwise ⇒ this branch is inert); both sides of
                # the comparison are built from the same fee-inclusive
                # published prices, and any surplus discount inside
                # dhw_prices only makes a genuinely sunny hour qualify.
                known = getattr(self, "_price_known", None)
                if known is not None:
                    known_mask = np.zeros(n_steps, dtype=bool)
                    arr = np.asarray(known, dtype=bool)[:n_steps]
                    known_mask[: arr.size] = arr
                else:
                    known_mask = np.ones(n_steps, dtype=bool)
                # A cycle target the tank cannot physically reach by its
                # step is not a plan, it is a constraint the solver will
                # quietly relax. Only steps the pump can actually heat to
                # the disinfection temperature by are candidates —
                # `reach_step`, shared with the hard-deadline branch above
                # so the two can never disagree about what is reachable.
                known_mask[: min(reach_step, n_steps)] = False
                known_mask = _drop_off_steps(known_mask, off)
                candidates = np.where(known_mask)[0]
                if candidates.size:
                    idx = int(candidates[np.argmin(dhw_prices[candidates])])
                    if float(dhw_prices[idx]) <= float(
                        params.dhw_legionella_price_ceiling
                    ):
                        place_idx = idx
            if place_idx is not None:
                ready_temps[place_idx] = max(
                    ready_temps[place_idx], params.dhw_legionella_temp
                )
                legionella_due = True
                legionella_hour = float(hours_mod[place_idx])
                legionella_step = place_idx
        return legionella_due, legionella_hour, legionella_step

    def _dhw_legionella_ceilings(
        self,
        h: _Horizon,
        *,
        params: ThermalParameters,
        c_dhw: float,
        draw_rates: np.ndarray,
        floor_temps: np.ndarray,
        p_dhw_run: float,
        legionella_due: bool,
        legionella_hour: float | None,
        legionella_step: int | None,
    ) -> _DhwLegionellaPlan:
        """The tank ceilings and run-up floor the cycle needs, verbatim.

        ``max_temp`` is the everyday ceiling, ``lp_max_temp`` the one the LP
        may exceed during a boost, ``runup_temps`` the per-step floor the
        cycle needs beforehand.
        """
        n_steps = h.n_steps
        dt = h.dt
        outdoor_temps = h.outdoor_temps
        humidity = h.humidity
        max_temp = np.full(max(n_steps, 0), float(params.dhw_max_temp))
        lp_max_temp = max_temp
        # The run-up the cycle needs, as a per-step FLOOR. Folded into
        # ``requirement`` below rather than into ``ready_temps``, so the step
        # reason codes and the published "required now" keep meaning what
        # they meant.
        runup_temps = np.zeros(max(n_steps, 0))
        boost_top = min(70.0, float(params.dhw_hard_max_temp))
        if c_dhw > 0.0 and legionella_step is not None and n_steps > 0 and (
            boost_top > float(params.dhw_max_temp)
        ):
            ua = params.dhw_tank_heat_loss_coefficient
            decay, gain = _tank_decay(ua, dt, c_dhw)
            everyday = float(params.dhw_max_temp)
            max_temp[legionella_step] = boost_top

            # Run-up: walk backwards along the fastest charge the pump can
            # actually deliver, inverting the same tank recursion the LP
            # uses. `need` is the coolest the tank may be at the end of a
            # step and still reach `boost_top` on time, so a ceiling of
            # `need` grants the cycle exactly the headroom it needs and not
            # a degree more. Draws are carried, because water taken during
            # the run-up is heat the charge has to make up as well.
            #
            # The ramp is an OBLIGATION, not merely a permission, so each
            # step of the walk records `need` as a floor too and the walk
            # runs all the way down to the floor the plan already has to
            # honour rather than stopping at the charge limit. Raising the
            # ceiling alone would say the tank MAY climb without anything
            # making it, which is only safe while something else happens to
            # leave it at the charge limit when the ramp starts — and with
            # the limit honoured a summer plan legitimately parks the tank at
            # ~37 °C. The repair stage does find the ramp from the cycle's
            # own requirement, so this is belt and braces rather than the
            # only thing holding the cycle up; it is cheap, it is what the
            # linear program needs to seed a sensible shape, and it states
            # the obligation where the ramp is computed instead of leaving it
            # to be rediscovered.
            need = boost_top
            for m in range(legionella_step - 1, -1, -1):
                # The transition from the END of step m to the END of step
                # m+1 is step m+1's own weather and draw, not step m's.
                nxt = m + 1
                cop = max(
                    self.model.compute_cop_dhw(
                        float(outdoor_temps[nxt]), need,
                        humidity=_step_humidity(humidity, nxt),
                    ),
                    0.5,
                )
                rise = p_dhw_run * cop * dt / c_dhw
                drawn = float(draw_rates[nxt]) * dt / c_dhw
                need = (need + drawn - gain - rise) / max(decay, 1e-6)
                if need > boost_top:
                    # Even starting AT the disinfection temperature the pump
                    # could not carry the ramp from here. Nothing earlier can
                    # help, and demanding it would only buy heat the cycle
                    # cannot use.
                    break
                if need > everyday:
                    max_temp[m] = min(boost_top, need)
                runup_temps[m] = need
                if need <= floor_temps[m]:
                    # From here the ordinary availability floor is already at
                    # least as high as the ramp needs, so the plan is obliged
                    # to be there anyway.
                    break

            # Coast-down, LP only: a tank left alone from `boost_top`.
            # Standby-only, so it is the upper envelope of what the cycle can
            # leave behind — the linear program needs room for heat that is
            # genuinely in the tank, and nothing more.
            lp_max_temp = max_temp.copy()
            temp = boost_top
            for m in range(legionella_step + 1, n_steps):
                temp = decay * temp + gain
                if temp <= everyday:
                    break
                lp_max_temp[m] = max(lp_max_temp[m], temp)
        return _DhwLegionellaPlan(
            due=legionella_due,
            hour=legionella_hour,
            step=legionella_step,
            max_temp=max_temp,
            lp_max_temp=lp_max_temp,
            runup_temps=runup_temps,
        )

    def _dhw_legionella_plan(
        self,
        h: _Horizon,
        *,
        params: ThermalParameters,
        c_dhw: float,
        hours_mod: np.ndarray,
        draw_rates: np.ndarray,
        ready_temps: np.ndarray,
        floor_temps: np.ndarray,
        p_dhw_run: float,
        dhw_prices: np.ndarray,
        off_steps: np.ndarray | None = None,
    ) -> "_DhwLegionellaPlan":
        """The anti-legionella stage: when the cycle runs, and its ceilings.

        Two halves, split because the ratchet is right that a 268-line
        helper is not a decomposition (#224 stage 1). ``off_steps`` keeps
        the cycle off an Off window: the reach and the placement both
        treat those steps as unusable (#1910).
        """
        legionella_due, legionella_hour, legionella_step = self._dhw_legionella_due(
            h,
            params=params,
            hours_mod=hours_mod,
            draw_rates=draw_rates,
            ready_temps=ready_temps,
            p_dhw_run=p_dhw_run,
            dhw_prices=dhw_prices,
            off_steps=off_steps,
        )
        return self._dhw_legionella_ceilings(
            h,
            params=params,
            c_dhw=c_dhw,
            draw_rates=draw_rates,
            floor_temps=floor_temps,
            p_dhw_run=p_dhw_run,
            legionella_due=legionella_due,
            legionella_hour=legionella_hour,
            legionella_step=legionella_step,
        )

    def _dhw_coil_wood_forecast(
        self,
        h: _Horizon,
        space_power: np.ndarray | None = None,
        dhw_power: np.ndarray | None = None,
    ) -> np.ndarray | None:
        """Per-step wood temps the DHW coil credit is priced against (#400).

        Read from ``simulate_trajectory_with_dhw`` with the DHW plan in hand
        (none before the first), the physics the published plan runs -- the
        coil drains the wood tank on the DHW tank's own draw scale, so the
        tank's plan moves the read (R9 D2-s1-02): standby loss, ``wood_share``, the
        external-heat forecast and the coil's own drain, coupled step by step.
        A re-derived drain beside it drifted both ways (RCA coil-drain, R8-P3).
        Step i is the temperature the coil reads mid-step, not the trajectory's
        ``wood[i]``: pricing at the step's start over-credited the coil, and the
        plan breached the window floor by 0.115 K at a low ``cop_scale``.
        """
        p = self.model.params
        if not p.dhw_coil_active or h.initial_state.wood_tank_temperature is None:
            return None
        n = h.n_steps
        power = (
            np.zeros(n)
            if space_power is None
            else np.asarray(space_power, dtype=float)[:n]
        )
        hours = np.asarray(h.step_hours, dtype=float) % 24.0
        raw = np.asarray(self.model.dhw_draw_rates(hours), dtype=float)
        read = np.empty(n)
        *_, wood = self.model.simulate_trajectory_with_dhw(
            h.initial_state,
            power,
            (
                np.zeros(n)
                if dhw_power is None
                else np.asarray(dhw_power, dtype=float)[:n]
            ),
            WeatherSeries.from_horizon(h),
            start_hour=float(h.step_hours[0]),
            dt_hours=h.dt,
            dhw_draw_rates=raw,
            valve_targets=h.valve_targets,
            coil_wood_read=read,
        )
        return None if wood is None else read

    def _dhw_planner_draws(
        self,
        raw_draw_rates: np.ndarray,
        wood_temps: np.ndarray | None,
    ) -> np.ndarray:
        """Coil-reduced draws for planning. Caller keeps the raw array for physics."""
        if wood_temps is None:
            return raw_draw_rates
        p = self.model.params
        wt = np.asarray(wood_temps, dtype=float)
        out = np.empty_like(raw_draw_rates, dtype=float)
        last = len(wt) - 1
        setpoint = p.dhw_setpoint
        inlet = p.dhw_inlet_reference
        for i, rate in enumerate(raw_draw_rates):
            idx = i if i <= last else last
            out[i], _ = dhw_coil_draw_reduction(
                float(rate), float(wt[idx]), setpoint, inlet_temp=inlet,
            )
        return out

    def _dhw_window_floors(
        self,
        params: ThermalParameters,
        windows: list[Window],
        step_hours: np.ndarray,
        step_weekdays: np.ndarray | None,
        dt: float,
        n_steps: int,
        wood_temps: np.ndarray | None,
        holiday_flags: np.ndarray | None = None,
    ) -> tuple[
        float, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray
    ]:
        """Window mask, floors, ready temps, and the planner draw series."""
        dhw_min_temp = params.dhw_min_temp
        dhw_setpoint = params.dhw_setpoint
        idle_min_temp = min(params.dhw_idle_min_temp, dhw_min_temp)
        # The tank's own capacity, unfloored: the three planners this is
        # threaded into and the legionella run-up all read this one value
        # (D2-03, the class D2-01 closed in thermal_model.py).
        c_dhw = params.dhw_tank_thermal_mass

        hours_mod = np.asarray(step_hours, dtype=float) % 24.0
        # Weekly windows (#3): when the configured spec names days, the
        # window set is chosen per step from that step's own weekday.
        # `step_weekdays` is None on the flat (dayless) spec every install
        # already has, and `windows_for_day` then returns the fallback
        # unchanged -- the every-day behaviour, bit for bit. The per-weekday
        # overrides (#1260) ride the same array: a flat spec with overrides
        # set computes weekdays too, and `windows_for_day` applies the
        # whole precedence chain (override > holiday > default) per step.
        weekly = params.dhw_weekly_windows
        holiday_windows = getattr(params, "dhw_holiday_windows", None)
        day_overrides = getattr(params, "dhw_day_windows", None)
        in_window = np.array(
            [
                hour_in_windows(
                    float(h),
                    _dhw_windows_at(
                        weekly,
                        step_weekdays,
                        i + 1,
                        windows,
                        holiday_windows,
                        holiday_flags,
                        day_overrides,
                    ),
                )
                for i, h in enumerate(hours_mod)
            ],
            dtype=bool,
        )
        prev_in_window = np.array(
            [
                hour_in_windows(
                    float(h) - dt,
                    _dhw_windows_at(
                        weekly,
                        step_weekdays,
                        i,
                        windows,
                        holiday_windows,
                        holiday_flags,
                        day_overrides,
                    ),
                )
                for i, h in enumerate(hours_mod)
            ],
            dtype=bool,
        )
        window_starts = np.where(in_window & ~prev_in_window)[0].tolist()

        raw_draw_rates = self.model.dhw_draw_rates(hours_mod)
        # Planners may see the coil; physics must not — simulate_trajectory_with_dhw
        # applies dhw_coil_draw_reduction itself (#400).
        draw_rates = self._dhw_planner_draws(raw_draw_rates, wood_temps)

        floor_temps = np.where(in_window, dhw_min_temp, idle_min_temp).astype(float)
        ready_temps = np.zeros(n_steps)

        # "Ready" temperature per window: only as hot as the window's expected
        # draw actually requires, capped at the configured setpoint.
        for start_idx in window_starts:
            end_idx = start_idx
            while end_idx < n_steps and in_window[end_idx]:
                end_idx += 1
            window_hours = max((end_idx - start_idx) * dt, dt)
            draw_energy = float(np.sum(draw_rates[start_idx:end_idx])) * dt
            # #20: the learned per-window quantile replaces the profile mean,
            # ramped by evidence — w = n/8 keeps a fresh install answering
            # exactly as before and stops one early outlier yanking the
            # target. The blend lives HERE, where the mean it blends against
            # is computed, so the two can never diverge.
            stats = params.dhw_window_ready_energy
            if stats:
                label = draw_window_label(float(hours_mod[start_idx]), windows)
                entry = stats.get(label)
                if entry is not None:
                    try:
                        p90, count = float(entry[0]), int(entry[1])
                    except (TypeError, ValueError, IndexError):
                        p90, count = None, 0
                    if p90 is not None and np.isfinite(p90) and count > 0:
                        w = min(1.0, count / float(DHW_QUANTILE_MIN_EVENTS))
                        draw_energy = (1.0 - w) * draw_energy + w * max(
                            0.0, p90
                        )
            standby_energy = (
                params.dhw_tank_heat_loss_coefficient
                * max(0.5 * (dhw_setpoint + dhw_min_temp) - TANK_ROOM_AMBIENT_TEMP, 0.0)
                * window_hours
            )
            needed_delta = (draw_energy + standby_energy) / c_dhw if c_dhw else 0.0
            # T4a #11 (gated): when the immersion element keeps rescuing
            # late tanks, the coordinator asks for a little extra
            # readiness. 0.0 — the default — is byte-inert.
            required_ready = float(
                np.clip(
                    dhw_min_temp + needed_delta + params.dhw_ready_margin_c,
                    dhw_min_temp,
                    dhw_setpoint,
                )
            )
            # The tank must be ready by the END of the step before the window.
            ready_idx = max(0, start_idx - 1)
            ready_temps[ready_idx] = max(ready_temps[ready_idx], required_ready)
        return (
            c_dhw,
            hours_mod,
            in_window,
            raw_draw_rates,
            draw_rates,
            floor_temps,
            ready_temps,
        )

    def _build_dhw_requirements(
        self,
        h: _Horizon,
        *,
        p_max: float,
        space_demand: np.ndarray | None = None,
        p_run_cap: float | None = None,
        blocked: bool = False,
        off_steps: np.ndarray | None = None,
        wood_temps: np.ndarray | None = None,
    ) -> tuple[DhwPlan, np.ndarray]:
        """Build the DHW availability requirements and a cheapest-first plan.

        The requirement is a per-step temperature *floor*, not a target to
        track:

        * inside a demand window the tank must stay at or above the usable
          minimum temperature, and it must be "ready" (hot enough to cover the
          window's expected draw) when the window opens;
        * outside the windows only the idle floor applies, which defaults to
          the tank's ambient temperature, i.e. no requirement at all.

        Because nothing rewards a hot tank per se, the electricity cost term is
        the only thing left to decide *when* the pump runs — so it runs at the
        cheapest hours that still satisfy the windows.
        """
        initial_state = h.initial_state
        prices = h.prices
        outdoor_temps = h.outdoor_temps
        step_hours = h.step_hours
        n_steps = h.n_steps
        dt = h.dt
        dhw_pins = h.dhw_pins
        step_weekdays = h.step_weekdays
        holiday_flags = h.holiday_flags
        humidity = h.humidity
        params = self.model.params
        windows, learned_windows = self._effective_dhw_windows()
        (
            c_dhw,
            hours_mod,
            in_window,
            raw_draw_rates,
            draw_rates,
            floor_temps,
            ready_temps,
        ) = self._dhw_window_floors(
            params,
            windows,
            step_hours,
            step_weekdays,
            dt,
            n_steps,
            wood_temps,
            holiday_flags,
        )

        # The pump serves DHW as an on/off block, not a trickle, so the planner
        # allocates at a realistic run power and never below the level at which
        # the pump would actually be considered running. An external total-power
        # cap (fuse guard, shadow solves) bounds the block too — otherwise a
        # DHW slot alone could blow through the very limit the cap encodes.
        # Two accepted approximations: the cap is the horizon's *minimum*
        # (a single low-headroom step throttles every block — conservative,
        # never over the line), and the 0.1 kW planning floor still wins
        # below it, because a fuse leaving under 100 W for hot water is not
        # a plan, it is an infeasibility the breach report already states.
        p_dhw_run = max(0.1, min(p_max * 0.8, p_max))
        if p_run_cap is not None:
            p_dhw_run = max(0.1, min(p_dhw_run, float(p_run_cap)))
        min_run_power = min(p_dhw_run, max(0.15, self.model.params.min_electrical_power * 0.6))

        # What a DHW block actually costs per kWh at each step, with the
        # surplus-covered fraction at the export price. Everything below that
        # ranks or optimizes against these, so a sunny midday can win a slot
        # over a merely cheap night without repricing the whole step.
        dhw_prices = self._dhw_planning_prices(prices, p_dhw_run, space_demand)

        # --- Anti-legionella cycle (see _dhw_legionella_plan) ---
        (
            legionella_due,
            legionella_hour,
            legionella_step,
            max_temp,
            lp_max_temp,
            runup_temps,
        ) = self._dhw_legionella_plan(
            h,
            params=params,
            c_dhw=c_dhw,
            hours_mod=hours_mod,
            draw_rates=draw_rates,
            ready_temps=ready_temps,
            floor_temps=floor_temps,
            p_dhw_run=p_dhw_run,
            dhw_prices=dhw_prices,
            off_steps=off_steps,
        )

        # How long stored heat actually survives in this tank. The learned
        # cooling rate drives it, so a well-insulated tank is allowed to
        # pre-heat much further ahead than a leaky one.
        max_lead_hours = self.model.dhw_hold_hours()
        requirement = np.maximum(np.maximum(floor_temps, ready_temps), runup_temps)

        # Steps a manual plan forces off. The planners must know these up
        # front: overlaying the pins on a finished schedule deleted the energy
        # in those steps without moving it anywhere, so the tank simply missed
        # its requirement — by several degrees in a demand window — and nothing
        # re-bought the shortfall in the steps that remained free. Force-on
        # stays an overlay below, because it adds energy rather than removing
        # planned energy the tank was counting on.
        forced_off: np.ndarray | None = None
        if dhw_pins is not None:
            pins_arr = np.asarray(dhw_pins, dtype=float)[:n_steps]
            mask = np.zeros(n_steps, dtype=bool)
            mask[: pins_arr.size] = ~np.isnan(pins_arr) & (pins_arr < 0.5)
            if mask.any():
                forced_off = mask
        if blocked:
            # v5.3.0: the pump's mode makes no hot water at all. Entering
            # through the same door as a forced-off pin is what keeps the
            # planners coherent: the LP, the greedy pass and the floor repair
            # all already know how to plan *around* unusable steps, so the
            # requirement stays visibly unmet rather than being deleted, and
            # nothing tries to buy the shortfall in a step that is equally
            # unusable. The difference from a pin is that this one is never
            # released — see ``optimize``'s docstring.
            forced_off = np.ones(n_steps, dtype=bool)
        if off_steps is not None:
            # #1910 (D1): a quiet Off window plans no hot-water slots in
            # exactly its steps, through that same door — the anti-legionella
            # run and every window's pre-heat are planned around it like any
            # other unusable step, buying their energy in the steps that
            # remain. Not a pin: the window is a scheduled decision, so the
            # pin-safety release loop in ``optimize`` never frees these.
            forced_off = _forced_off_with(forced_off, off_steps, n_steps)

        # Pre-heating is allowed anywhere in the horizon: the planners price the
        # standby losses of storing heat, so an early cheap hour wins only when
        # it is still cheaper after those losses. Capping the lead time instead
        # of pricing it is what used to pin heating to the demand windows.
        max_lead_steps = max(1, min(n_steps, int(np.ceil(max_lead_hours / dt))))

        # What the three planners share, built once: the derived price
        # series, the horizon geometry and the tank envelope (#1776).
        ctx = _DhwPlanContext(
            prices=dhw_prices,
            import_prices=prices,
            outdoor_temps=outdoor_temps,
            humidity=humidity,
            n_steps=n_steps,
            dt=dt,
            c_dhw=c_dhw,
            p_dhw_max=p_dhw_run,
            min_run_power=min_run_power,
            max_lead_steps=max_lead_steps,
        )

        # Stage 1: a linear program over the whole horizon finds the truly
        # cheapest feasible allocation. Stage 2 repairs whatever the linear
        # approximation got wrong against the real tank simulation.
        seed = self._plan_dhw_min_cost(
            ctx,
            initial_temp=initial_state.dhw_temperature,
            requirement=requirement,
            draw_rates=draw_rates,
            # The LP alone gets the coast-down band — see the ceiling block.
            max_temp=lp_max_temp,
            space_demand=space_demand,
            p_total_max=p_max,
            forced_off=forced_off,
        )

        schedule = self._plan_dhw_cheapest_first(
            ctx,
            initial_temp=initial_state.dhw_temperature,
            requirement=requirement,
            draw_rates=draw_rates,
            max_temp=max_temp,
            initial_plan=seed,
            forced_off=forced_off,
        )

        schedule = self._apply_dhw_min_run(
            plan=schedule,
            initial_temp=initial_state.dhw_temperature,
            outdoor_temps=outdoor_temps,
            draw_rates=draw_rates,
            dt=dt,
            p_dhw_max=p_dhw_run,
            min_run_power=min_run_power,
            max_temp=max_temp,
            humidity=humidity,
        )

        # Rounding weak slots down leaves energy the tank was counting on
        # unbought, so the greedy planner runs once more to re-buy any
        # shortfall in steps that can still take a real block.
        schedule = self._plan_dhw_cheapest_first(
            ctx,
            initial_temp=initial_state.dhw_temperature,
            requirement=requirement,
            draw_rates=draw_rates,
            max_temp=max_temp,
            initial_plan=schedule,
            forced_off=forced_off,
        )

        # The tank's rating is physics, not preference, so it is enforced after
        # the economics rather than inside them. A step the clamp truncates
        # below the pump's practical minimum is then zeroed, never re-raised:
        # the rating always wins, and a published trickle is a power level the
        # on/off hardware cannot deliver.
        schedule = self._clamp_dhw_to_capacity(
            plan=schedule,
            initial_temp=initial_state.dhw_temperature,
            outdoor_temps=outdoor_temps,
            draw_rates=draw_rates,
            dt=dt,
            max_temp=max_temp,
            humidity=humidity,
        )
        schedule = np.where(schedule < min_run_power - 1e-9, 0.0, schedule)

        # The floor gets the same physics check the rating just got. The LP
        # and the greedy passes plan on an affine tank; the trajectory the
        # house actually runs is the simulation's, and the gap between the
        # two let a plan that satisfied every linear floor drain the real
        # tank ~1-2 °C below the promised minimum inside an evening demand
        # window (stress: winter_mild). Top up at the cheapest usable step
        # before each breach until the simulated trajectory honours the
        # requirement, then re-apply the rating, which always wins.
        schedule = self._repair_dhw_floor(
            ctx,
            plan=schedule,
            initial_temp=initial_state.dhw_temperature,
            draw_rates=draw_rates,
            requirement=requirement,
            max_temp=max_temp,
            forced_off=forced_off,
        )
        # Not re-clamped here, because the repair now carries the clamp
        # inside its own loop: every top-up it places is followed by one,
        # so a plan leaves this stage already bounded by the per-step
        # ceiling and already free of sub-minimum trickles. Doing it there
        # rather than here is what lets the two agree — the repair sizes its
        # room on the END of a step, draw and standby loss included, and so
        # does the clamp, so a block placed to close a breach is no longer
        # deleted by the very check meant to bound it.

        # --- External heat source (item 5) ---------------------------------
        # While something else is charging the tank for free, buying electric
        # hot water is the most expensive mistake available. Suppress the
        # planned slots that are *discretionary* — pre-heating ahead of a
        # window, and the topping-up inside one — for as long as the tank is
        # actually above the floor it has to meet.
        #
        # The legionella cycle is deliberately not suppressed by removing it:
        # instead, if the external source gets the tank to the disinfection
        # temperature on its own, the coordinator's existing observer resets
        # the timer and the requirement disappears by itself. That is a real
        # saving and an easy one to miss.
        suppress_steps = 0
        if getattr(initial_state, "external_heat_active", False) or getattr(
            initial_state, "peak_guard_active", False
        ):
            free_temps = self.model.simulate_dhw_only(
                initial_temp=initial_state.dhw_temperature,
                dhw_power_schedule=np.zeros(n_steps),
                outdoor_temps=outdoor_temps,
                draw_rates=draw_rates,
                dt_hours=dt,
                humidity=humidity,
            )
            # Only suppress while coasting still meets the requirement. Running
            # out of hot water because a fire was assumed to keep burning is
            # exactly the asymmetric failure the detector is biased against.
            covered = free_temps[1:] >= requirement - 0.5
            horizon = min(n_steps, max(1, int(round(2.0 / max(dt, 1e-6)))))
            mask = np.zeros(n_steps, dtype=bool)
            mask[:horizon] = covered[:horizon]
            if legionella_step is not None:
                mask[legionella_step] = False
            suppress_steps = int(np.sum(mask & (schedule > 1e-6)))
            schedule = np.where(mask, 0.0, schedule)

        next_window = hours_until_next_window(
            float(hours_mod[0]) if n_steps else 0.0, windows
        )

        # A manual plan overrides *timing* last, after the economics and the
        # external-heat suppression, because it expresses the user's explicit
        # intent: force-off zeroes the step, force-on gives it at least a run's
        # worth of power. The rating clamp is re-applied so a pinned-on step can
        # never be asked to boil an already-hot tank; the safety-release loop in
        # ``optimize`` handles the opposite risk, a force-off that would empty
        # it. The requirement is stashed for that loop to check against.
        if dhw_pins is not None:
            schedule = self._apply_dhw_pins(schedule, dhw_pins, min_run_power)
            schedule = self._clamp_dhw_to_capacity(
                plan=schedule,
                initial_temp=initial_state.dhw_temperature,
                outdoor_temps=outdoor_temps,
                draw_rates=draw_rates,
                dt=dt,
                max_temp=max_temp,
                humidity=humidity,
            )
            # Same hygiene as the automatic path: a step the rating truncated
            # below the pump's minimum cannot actually run, even a pinned one.
            schedule = np.where(schedule < min_run_power - 1e-9, 0.0, schedule)
        if blocked:
            # The invariant, restated after every path that can add energy —
            # including the manual force-on overlay directly above, which a
            # user may well have set before switching the pump to a mode that
            # cannot honour it. A pin expresses a preference; the mode is the
            # hardware. Cheap, and it means no future addition to this method
            # can quietly reopen a channel the pump refuses to serve.
            schedule = np.zeros_like(schedule)
        if off_steps is not None:
            # #1910: the same invariant for the Off window's steps, restated
            # for the same reason — a manual force-on pin inside a window
            # must not reopen what the schedule refuses to plan (D1: the
            # window means no slots there, nothing else).
            schedule = np.where(
                _forced_off_with(None, off_steps, n_steps), 0.0, schedule
            )
        return DhwPlan(
            floor_temps=floor_temps,
            ready_temps=ready_temps,
            draw_rates=raw_draw_rates,
            in_window=in_window,
            # The everyday charge limit, as one number: this is the plan's
            # published ceiling, and a disinfection cycle is an exception to
            # it rather than a redefinition of it. The per-step array stays
            # internal to the planning stages above.
            max_temp=float(params.dhw_max_temp),
            schedule=schedule,
            windows_text=format_windows(windows),
            windows_learned=learned_windows,
            next_window_in_hours=(
                round(next_window, 2) if next_window is not None else None
            ),
            legionella_due=legionella_due,
            legionella_hour=(
                round(legionella_hour, 2) if legionella_hour is not None else None
            ),
            legionella_step=legionella_step,
            external_heat_suppressed_steps=suppress_steps,
            max_lead_hours=max_lead_hours,
        ), requirement

    def _dhw_cop_profile(
        self,
        outdoor_temps: np.ndarray,
        tank_temps: np.ndarray,
        humidity: np.ndarray | None = None,
    ) -> np.ndarray:
        """Per-step DHW COP for a given assumed tank temperature trajectory."""
        return np.array(
            [
                max(
                    1.0,
                    self.model.compute_cop_dhw(
                        float(outdoor_temps[i]), float(tank_temps[i]),
                        humidity=_step_humidity(humidity, i),
                    ),
                )
                for i in range(len(outdoor_temps))
            ]
        )

    def _plan_dhw_min_cost(
        self,
        ctx: _DhwPlanContext,
        initial_temp: float,
        requirement: np.ndarray,
        draw_rates: np.ndarray,
        max_temp: np.ndarray,
        space_demand: np.ndarray | None = None,
        p_total_max: float | None = None,
        forced_off: np.ndarray | None = None,
    ) -> np.ndarray | None:
        """Minimum-cost DHW schedule over the whole horizon, as a linear program.

        ``forced_off`` marks steps a manual plan has pinned off. They enter as
        bounds rather than as a post-overlay, so the program buys the energy
        those steps would have carried in the free steps that remain instead of
        silently under-delivering against the availability floors.

        The tank is a linear store. Writing its dynamics out,

            T[m+1] = a·T[m] + (E[m] - D[m])/C + b
            a = 1 - UA·dt/C,  b = UA·T_ambient·dt/C

        makes the temperature at any step an affine function of the heat put
        in earlier: a kWh delivered at step ``j`` still contributes
        ``a^(m-1-j)/C`` degrees at step ``m``. The ``a^(m-1-j)`` factor *is*
        the standby loss, so buying heat early is automatically priced higher
        than buying it late — no artificial "don't pre-heat more than N hours
        ahead" cap is needed, and none is applied.

        Minimising ``Σ price[j]·E[j]/COP[j]`` subject to the availability
        floors and the tank's maximum temperature therefore yields the
        genuinely cheapest way to have hot water when the demand windows need
        it, whether that means heating inside the window or twelve hours
        earlier at the night tariff.

        ``space_demand`` closes the loop with the space-heating side. The pump
        serves one circuit at a time, so hot water bought in an hour where
        space heating already wants the whole compressor is not free: it
        displaces space heating into a more expensive hour. That displacement
        is piecewise linear in the DHW power, so it is modelled exactly, with
        an auxiliary variable per step priced at the premium space heating
        would have to pay to buy the same kWh in the cheapest hour that still
        has spare capacity. DHW therefore fills the cheap hours only up to the
        point where it starts competing, and pays the real price beyond it.

        ``max_temp`` is a per-step ceiling. The program wants the whole array:
        its tank-maximum block is one row per step, so a ceiling that rises
        for a disinfection cycle and decays afterwards is expressed exactly,
        with no scalar compromise between "hot enough to disinfect" and "no
        hotter than the user asked for on an ordinary evening".

        Returns ``None`` when the solve fails, so the caller can fall back to
        the greedy planner.
        """
        prices = ctx.prices
        outdoor_temps = ctx.outdoor_temps
        humidity = ctx.humidity
        n_steps = ctx.n_steps
        dt = ctx.dt
        p_dhw_max = ctx.p_dhw_max
        c_dhw = ctx.c_dhw
        if n_steps == 0 or c_dhw <= 0.0:
            return None

        requirement, max_temp = _within_ceiling(requirement, max_temp)
        params = self.model.params
        ua = params.dhw_tank_heat_loss_coefficient
        decay, gain = _tank_decay(ua, dt, c_dhw)

        # Free trajectory: what the tank does with no heating at all.
        free = np.zeros(n_steps + 1)
        free[0] = initial_temp
        for i in range(n_steps):
            free[i + 1] = (
                decay * free[i] - float(draw_rates[i]) * dt / c_dhw + gain
            )

        # Influence matrix: A[m, j] = degrees at step m+1 per thermal kWh at j.
        idx = np.arange(n_steps)
        lag = idx[:, None] - idx[None, :]
        influence = np.where(lag >= 0, np.power(decay, np.maximum(lag, 0)) / c_dhw, 0.0)

        # COP is temperature dependent; solve once against the requirement
        # level, then re-solve against the trajectory the first pass produced.
        cop = self._dhw_cop_profile(
            outdoor_temps, np.maximum(requirement, params.dhw_min_temp), humidity
        )

        # --- Capacity contention with space heating -------------------------
        # Without this the DHW plan happily fills the cheapest hours right up
        # to the compressor ceiling, and space heating - which wants exactly
        # the same hours - gets pushed into more expensive ones. Price the
        # displacement instead of ignoring it.
        headroom: np.ndarray | None = None
        premium: np.ndarray | None = None
        if space_demand is not None and p_total_max is not None:
            demand = np.clip(np.asarray(space_demand, dtype=float), 0.0, None)
            headroom = np.clip(p_total_max - demand, 0.0, None)
            spare = demand < p_total_max - 1e-6
            # Displaced space heating has to be re-bought somewhere with room
            # for it, and it has to be near enough in time that the building
            # can still carry the heat to where it was needed. Search a local
            # window rather than the whole horizon: the cheapest hour tomorrow
            # is no use for a shortfall this morning.
            window = max(1, int(round(_DHW_REFILL_WINDOW_HOURS / max(dt, 1e-6))))
            premium = np.zeros(n_steps)
            for j in range(n_steps):
                lo = max(0, j - window)
                hi = min(n_steps, j + window + 1)
                local = spare[lo:hi]
                if local.any():
                    refill = float(np.min(prices[lo:hi][local]))
                else:
                    refill = float(np.max(prices[lo:hi]))
                premium[j] = max(0.0, refill - float(prices[j]))
            if not np.any(premium > 1e-9):
                headroom = None
                premium = None

        n_extra = n_steps if headroom is not None else 0

        best: np.ndarray | None = None
        for _ in range(2):
            energy_max = np.maximum(p_dhw_max * cop * dt, 1e-9)
            # Shortfall slack keeps the program feasible when the requirement
            # simply cannot be met (cold start, undersized pump); it is priced
            # far above any real electricity cost so it is only ever used as a
            # last resort.
            shortfall_price = 1000.0 * (float(np.max(np.abs(prices))) + 1.0)
            objective = np.concatenate(
                [prices / cop, np.full(n_steps, shortfall_price)]
                + ([premium * dt] if premium is not None else [])
            )

            zeros = np.zeros((n_steps, n_steps))
            eye = np.eye(n_steps)
            rows = [
                np.hstack([-influence, -eye]),  # availability floor
                np.hstack([influence, zeros]),  # tank maximum temperature
            ]
            b_parts = [
                -(requirement - free[1:]),
                np.maximum(0.0, max_temp - free[1:]),
            ]
            if headroom is not None:
                # E[j]/(cop[j]*dt) - disp[j] <= headroom[j]
                rows.append(np.hstack([np.diag(1.0 / (cop * dt)), zeros]))
                b_parts.append(headroom)
            a_ub = np.vstack(rows)
            if n_extra:
                extra = np.zeros((a_ub.shape[0], n_extra))
                extra[2 * n_steps:, :] = -eye
                a_ub = np.hstack([a_ub, extra])
            b_ub = np.concatenate(b_parts)

            bounds = (
                [
                    (
                        0.0,
                        0.0
                        if forced_off is not None and forced_off[j]
                        else float(energy_max[j]),
                    )
                    for j in range(n_steps)
                ]
                + [(0.0, None)] * n_steps
                + [(0.0, None)] * n_extra
            )

            try:
                result = linprog(
                    objective, A_ub=a_ub, b_ub=b_ub, bounds=bounds, method="highs"
                )
            except Exception as err:  # pragma: no cover - solver availability
                _LOGGER.debug("DHW cost LP raised %s; using greedy planner", err)
                return best

            if not result.success:
                _LOGGER.debug(
                    "DHW cost LP did not solve (%s); using greedy planner",
                    result.message,
                )
                return best

            solution = result.x
            if solution is None:  # pragma: no cover - success implies a vector
                return best
            energy = np.asarray(solution[:n_steps], dtype=float)
            best = np.clip(energy / (cop * dt), 0.0, p_dhw_max)

            # Refine the COP estimate against the tank temperatures this plan
            # actually produces, so the cost ranking reflects reality.
            temps = self.model.simulate_dhw_only(
                initial_temp=initial_temp,
                dhw_power_schedule=best,
                outdoor_temps=outdoor_temps,
                draw_rates=draw_rates,
                dt_hours=dt,
                humidity=humidity,
            )
            refined = self._dhw_cop_profile(outdoor_temps, temps[:-1], humidity)
            if np.allclose(refined, cop, rtol=0.02):
                break
            cop = refined

        return best

    @staticmethod
    def _apply_dhw_pins(
        plan: np.ndarray, dhw_pins: np.ndarray, min_run_power: float
    ) -> np.ndarray:
        """Overlay manual hot-water pins on a planned schedule.

        Force-off zeroes the step. Force-on guarantees at least a run's worth of
        power without capping how much more the planner already allocated, so
        the tank rating — re-applied by the caller — remains the only ceiling.
        Free steps (NaN) keep whatever the economics chose.
        """
        out = np.array(plan, dtype=float)
        for i in range(min(len(out), len(dhw_pins))):
            pin = float(dhw_pins[i])
            if _pin_is_free(pin):
                continue
            if pin >= 0.5:
                out[i] = max(out[i], min_run_power)
            else:
                out[i] = 0.0
        return out

    def _dhw_shortfall(
        self,
        temps: np.ndarray | None,
        plan: np.ndarray,
        initial_temp: float,
        outdoor_temps: np.ndarray,
        draw_rates: np.ndarray,
        dt: float,
        humidity: np.ndarray | None,
        requirement: np.ndarray,
        unreachable: set[int],
    ) -> tuple[np.ndarray, np.ndarray, int | None]:
        """One round of a planner that fills breaches in time order: the tank
        trajectory under ``plan`` (re-simulated when ``temps`` is ``None``), the
        shortfall below ``requirement`` at each step, and the first step short
        by more than 0.05 K that is not already known ``unreachable`` (``None``
        when there is none). The greedy planner and the floor repair share it."""
        if temps is None:
            temps = self._dhw_plan_temps(
                plan, initial_temp, outdoor_temps, draw_rates, dt, humidity
            )
        gaps = requirement - temps[1 : plan.size + 1]
        for i in np.where(gaps > 0.05)[0]:
            if int(i) not in unreachable:
                return temps, gaps, int(i)
        return temps, gaps, None

    def _dhw_plan_temps(
        self,
        plan: np.ndarray,
        initial_temp: float,
        outdoor_temps: np.ndarray,
        draw_rates: np.ndarray,
        dt: float,
        humidity: np.ndarray | None = None,
    ) -> np.ndarray:
        return np.asarray(
            self.model.simulate_dhw_only(
                initial_temp=initial_temp,
                dhw_power_schedule=plan,
                outdoor_temps=outdoor_temps,
                draw_rates=draw_rates,
                dt_hours=dt,
                humidity=humidity,
            )
        )

    def _repair_dhw_floor(
        self,
        ctx: _DhwPlanContext,
        *,
        plan: np.ndarray,
        initial_temp: float,
        draw_rates: np.ndarray,
        requirement: np.ndarray,
        max_temp: np.ndarray,
        forced_off: np.ndarray | None = None,
    ) -> np.ndarray:
        """Top up the plan until the SIMULATED trajectory meets the floor.

        Bounded best-effort: each round finds the first step whose simulated
        temperature breaches the requirement, sizes the missing electrical
        energy at the tank's own marginal COP, and adds it at the cheapest
        step with headroom that can still reach the breach — after the last
        rating-pinned step before it, since heat added ahead of a full tank
        is refused, not stored. A demand no ceiling-legal plan can meet exits
        after the round limit with the closest achievable trajectory.

        ``max_temp`` is the per-step ceiling and is read per step: "full" is
        a local property once the ceiling moves. In the hours after a
        disinfection cycle the tank really is full against the everyday
        charge limit, and a top-up placed before one of those steps would be
        refused by the capacity clamp rather than stored — which is exactly
        what this search is trying to avoid.

        This stage runs AFTER the capacity clamp and is deliberately not
        re-clamped (see the caller), so it has to carry its own ceiling: it
        is the last word on the plan, and until v5.1.10 it relied on the
        model's tank-rating clamp to bound it, which only worked while the
        charge limit and the rating were the same number.
        """
        outdoor_temps = ctx.outdoor_temps
        humidity = ctx.humidity
        dt = ctx.dt
        p_dhw_max = ctx.p_dhw_max
        min_run_power = ctx.min_run_power
        prices = ctx.import_prices
        c_dhw = ctx.c_dhw
        plan = np.asarray(plan, dtype=float).copy()
        n = plan.size
        if n == 0 or requirement is None or c_dhw <= 0.0:
            return plan
        # Clipped to the ceiling, exactly as both planners clip it: a floor
        # the tank is not allowed to reach is not a target, it is a loop that
        # keeps buying blocks the tank cannot hold.
        req, ceiling = _within_ceiling(
            np.asarray(requirement, dtype=float)[:n], np.asarray(max_temp, dtype=float)[:n]
        )
        # The tank's own per-step decay, the same factor the linear program
        # uses: heat added now is worth less later, so the ceiling bound
        # below can price how much of a top-up still survives at each step.
        decay, _ = _tank_decay(self.model.params.dhw_tank_heat_loss_coefficient, dt, c_dhw)
        # Breaches no ceiling-legal top-up can close. Skipped rather than
        # returned on: a demand window later in the day is not helped by
        # giving up at the first step the tank cannot quite reach, and a
        # "ready" target that sits exactly ON the ceiling is exactly such a
        # step. Same shape as the greedy planner's `unreachable`.
        unreachable: set[int] = set()
        # Convergence is a min-run trickle per round in the worst case (a
        # cheap-step landscape already near the run cap), so the bound is
        # sized for a multi-degree breach at trickle pace, not for elegance.
        temps: np.ndarray | None = None
        for _ in range(48):
            temps, deficit, b = self._dhw_shortfall(
                temps, plan, initial_temp, outdoor_temps, draw_rates, dt,
                humidity, req, unreachable,
            )
            if b is None:
                return plan
            # Heat added before a rating-pinned step is refused, so only
            # steps after the last full-tank moment can feed the breach.
            pinned = np.where(temps[: b + 1] >= ceiling[: b + 1] - 0.1)[0]
            lo = int(pinned[-1]) if pinned.size else 0
            headroom = p_dhw_max - plan[lo : b + 1]
            usable = headroom > 1e-6
            if forced_off is not None:
                usable &= ~np.asarray(forced_off[lo : b + 1], dtype=bool)
            # Degrees of room under the ceiling for heat added at each
            # candidate. The heat is stored from the candidate to the breach,
            # decaying as it leaks away, so the bound is the tightest of
            # (room at m) / decay^(m-j) across that stretch — a step already
            # at its limit refuses the heat rather than passing it on.
            #
            # Beyond the breach the ceiling is not *bounded* here, it is
            # ENFORCED: heat the tank cannot hold later is refused, not
            # stored, so a top-up displaces the plan's own later charging
            # instead of stacking on top of it, and the capacity clamp below
            # performs exactly that displacement. Stating the bound over
            # the whole tail instead — the first cut of this change — made
            # every later step sitting ON the charge limit read as zero
            # room, the suffix-minimum carried that zero back over every
            # earlier candidate, and the repair refused every top-up there
            # was: a 24 h matrix went from a worst deficit of 0.03 °C to
            # 1.11 °C, inside a demand window, with no cycle due, and the
            # run-up to a disinfection cycle was refused the same way.
            gap = ceiling[lo : b + 1] - temps[lo + 1 : b + 2]
            if decay > 1e-6:
                weight = np.power(decay, np.arange(b + 1 - lo))
                scaled = gap / weight
                room_c = np.minimum.accumulate(scaled[::-1])[::-1] * weight
            else:
                room_c = gap
            usable &= room_c > 0.01
            # Cheapest first, and the whole ranking is walked here rather than
            # one candidate per re-simulation: a step that cannot take a
            # runnable block is not a reason to re-solve, only a reason to try
            # the next one.
            costs = np.where(usable, prices[lo : b + 1], np.inf)
            before = plan.copy()
            placed = False
            for j_local in np.argsort(costs, kind="stable"):
                j_local = int(j_local)
                if not usable[j_local]:
                    break
                j = lo + j_local
                cop_j = max(
                    self.model.marginal_cop(
                        float(outdoor_temps[j]), "dhw", store_temp=float(temps[j]),
                        humidity=_step_humidity(humidity, j),
                    ),
                    0.5,
                )
                needed = float(deficit[b]) * c_dhw / max(dt * cop_j, 1e-6)
                # The room bound is sized against the HIGHEST COP that could
                # apply at this step, not the marginal one used to size the
                # need: the simulation delivers `compute_cop_dhw` thermal kWh
                # per electrical kWh, so a bound computed at a lower COP lets
                # the top-up quietly overshoot the ceiling it exists to
                # respect.
                cop_room = max(
                    cop_j,
                    self.model.compute_cop_dhw(
                        float(outdoor_temps[j]), float(temps[j]),
                        humidity=_step_humidity(humidity, j),
                    ),
                )
                room_kw = float(room_c[j_local]) * c_dhw / max(dt * cop_room, 1e-6)
                add = min(
                    float(np.clip(needed, min_run_power, headroom[j_local])),
                    room_kw,
                )
                new_level = plan[j] + add
                if new_level < min_run_power - 1e-9:
                    runnable = min(min_run_power, p_dhw_max)
                    if runnable > plan[j] + room_kw + 1e-9:
                        # A block the pump could actually run would push the
                        # tank past the charge limit. Overshooting the user's
                        # own ceiling to close a fraction of a degree is the
                        # wrong trade, so this step drops out.
                        continue
                    new_level = runnable
                plan[j] = min(p_dhw_max, new_level)
                placed = True
                break
            if placed:
                # The top-up is legal up to the breach by construction; past
                # it, the tank simply has less room left for what the plan
                # was going to buy anyway. The clamp takes that back — it is
                # exact against the same simulation this loop runs, so it
                # removes only heat the tank would genuinely have refused,
                # and it cannot touch the step just topped up. A step it
                # truncates below a runnable block is zeroed, the same rule
                # the caller applies to its own clamp: a published trickle is
                # a power the on/off hardware cannot deliver.
                plan = self._clamp_dhw_to_capacity(
                    plan=plan,
                    initial_temp=initial_temp,
                    outdoor_temps=outdoor_temps,
                    draw_rates=draw_rates,
                    dt=dt,
                    max_temp=ceiling,
                    humidity=humidity,
                )
                plan = np.where(plan < min_run_power - 1e-9, 0.0, plan)
                if np.array_equal(plan, before):
                    # The block went in and came straight back out. Repeating
                    # it is a loop, not a repair, so this breach is recorded
                    # as one nothing ceiling-legal closes and the search moves
                    # on to the next.
                    unreachable.add(b)
                else:
                    temps = self._dhw_plan_temps(
                        plan, initial_temp, outdoor_temps, draw_rates, dt, humidity
                    )
            else:
                # Nothing ceiling-legal can fix this step; move on rather than
                # abandoning every later breach with it.
                unreachable.add(b)
        return plan

    def _clamp_dhw_to_capacity(
        self,
        plan: np.ndarray,
        initial_temp: float,
        outdoor_temps: np.ndarray,
        draw_rates: np.ndarray,
        dt: float,
        max_temp: np.ndarray,
        humidity: np.ndarray | None = None,
    ) -> np.ndarray:
        """Never deliver more heat than the tank has room for.

        The planners work against a linearised tank and a fixed run power, and
        both approximations can overshoot the tank's rating:

        * the minimum-run rounding raises a sub-minimum slot to a power the
          hardware can actually deliver, which on a small tank is an enormous
          step — a 20 L tank gains nearly 20 °C from one 15-minute block;
        * with negative prices the cost term *rewards* consumption, so the LP
          pushes against its temperature ceiling and the linearisation's error
          lands on the wrong side of it.

        This walks the plan through the real tank simulation and truncates any
        step that would exceed the rating. It is a physical bound rather than a
        preference, so it belongs after the economics rather than inside them:
        no plan may boil the tank, however cheap the electricity.

        Takes the per-step value of ``max_temp``: this walks the trajectory
        one step at a time, so each step is truncated against its own
        ceiling. That is what lets a disinfection cycle charge past the
        everyday limit at the step it was placed at, and what stops the plan
        re-heating the tank in the hours after it while the boost heat is
        still coasting out.
        """
        plan = np.array(plan, dtype=float)
        if plan.size == 0:
            return plan

        ceiling = np.asarray(max_temp, dtype=float)
        params = self.model.params
        capacity = params.dhw_tank_thermal_mass
        ua = params.dhw_tank_heat_loss_coefficient
        inlet = params.dhw_inlet_reference
        temp = float(initial_temp)

        for i in range(len(plan)):
            cop = max(
                self.model.compute_cop_dhw(
                    float(outdoor_temps[i]), temp,
                    humidity=_step_humidity(humidity, i),
                ),
                0.1,
            )
            # Headroom in kW electrical: how much may be delivered this step
            # before the tank passes its rating. Negative when the tank is
            # already over, which happens when it *starts* over — heating is
            # then simply forbidden rather than reversed, because the plan
            # cannot un-heat water.
            #
            # The step the tank actually runs is
            #
            #     T' = T + (cop·P − q_draw − q_loss)·dt / C
            #
            # so the power that lands exactly ON the ceiling has to pay for
            # the draw and the standby loss as well as the rise. Sizing the
            # allowance from the rise alone (as this did until v5.1.10) made
            # the clamp systematically tight: every truncated step landed
            # BELOW the ceiling it was aimed at, which is why a disinfection
            # ramp pinned to its own per-step band topped out at 59.90
            # instead of 60.00, and why the floor repair's in-window top-ups
            # read as rating breaches and were truncated back out. Both
            # terms are taken at the same tank temperature and the same COP
            # the simulation below uses, so the two cannot disagree.
            # Bounding on the step's END rather than its start is what makes
            # this agree with the floor repair, which measures its room the
            # same way: a tank that begins a step ON the limit and is drawn
            # 2 °C down during it does have room, and a clamp that answered
            # "none" there deleted the very top-up the repair had just placed,
            # round after round. A tank genuinely over the limit still cannot
            # be heated — `allowed` comes out negative and floors at zero,
            # so the hours after a disinfection cycle stay closed to
            # re-heating exactly as before.
            q_draw = float(draw_rates[i]) * dhw_draw_scale(temp, inlet)
            q_loss = ua * (temp - TANK_ROOM_AMBIENT_TEMP)
            headroom_c = float(ceiling[i]) - temp
            allowed = (headroom_c * capacity / dt + q_draw + q_loss) / cop
            plan[i] = float(np.clip(plan[i], 0.0, max(0.0, allowed)))

            # Stepped through the same simulation the planners use, so the
            # clamp cannot disagree with the trajectory it is protecting.
            temp = float(
                self.model.simulate_dhw_step(
                    dhw_temp=temp,
                    dhw_power_thermal=cop * plan[i],
                    hour_of_day=0.0,
                    dt_hours=dt,
                    draw_power=float(draw_rates[i]),
                )
            )

        return plan

    def _apply_dhw_min_run(
        self,
        plan: np.ndarray,
        initial_temp: float,
        outdoor_temps: np.ndarray,
        draw_rates: np.ndarray,
        dt: float,
        p_dhw_max: float,
        min_run_power: float,
        max_temp: np.ndarray,
        humidity: np.ndarray | None = None,
    ) -> np.ndarray:
        """Round sub-minimum runs up to a power the pump can actually deliver.

        A DHW valve is on or off; a planned 0.05 kW trickle is not something
        the hardware can do. Each slot below the practical minimum is raised to
        it while the tank stays within its rating, and zeroed when raising it
        would boil the plan over. Deciding per slot matters: the all-or-nothing
        version of this repair gave up on *every* weak slot whenever raising
        them all at once would overshoot, and published a plan full of powers
        the hardware cannot run. The energy a zeroed slot was carrying is
        re-bought by the greedy pass the caller runs after this.

        ``max_temp`` is the per-step ceiling, and this test needs it aligned
        with the trajectory rather than reduced to one number: after a
        disinfection cycle the tank sits legitimately above the everyday
        charge limit while the boost heat coasts out of it, and a
        ``max(trajectory) <= one scalar`` test would read that as a breach
        and refuse every weak slot for the rest of the day. The reference is
        therefore the ceiling *or* the trajectory the plan already produces,
        whichever is higher — raising a slot has to make nothing worse, which
        is the question this repair is actually asking.

        Each weak slot's check extends the current trajectory from the
        slot's own start state rather than replaying the horizon from t=0
        (#1230): the candidate's prefix is the current plan's prefix, so the
        same step function in the same order yields bit-identical decisions
        and plans.
        """
        plan = np.array(plan, dtype=float)
        weak = np.where((plan > 1e-6) & (plan < min_run_power))[0]
        if weak.size == 0:
            unchanged: np.ndarray = np.clip(plan, 0.0, p_dhw_max)
            return unchanged

        # temps[0] is the tank as found, which no plan can change, so it is
        # held to the first step's ceiling exactly as the flat test did.
        ceiling = np.asarray(max_temp, dtype=float)
        ceiling = np.concatenate([ceiling[:1], ceiling]) + 0.5

        def trajectory(schedule: np.ndarray) -> np.ndarray:
            return np.asarray(
                self.model.simulate_dhw_only(
                    initial_temp=initial_temp,
                    dhw_power_schedule=schedule,
                    outdoor_temps=outdoor_temps,
                    draw_rates=draw_rates,
                    dt_hours=dt,
                    humidity=humidity,
                )
            )

        run_power = min(min_run_power, p_dhw_max)
        base = trajectory(plan)
        joint = plan.copy()
        joint[weak] = run_power
        joint_temps = trajectory(joint)
        joint_limit = np.maximum(
            ceiling[: joint_temps.size], base[: joint_temps.size]
        )
        if bool(np.all(joint_temps <= joint_limit + 1e-9)):
            jointly_raised: np.ndarray = np.clip(joint, 0.0, p_dhw_max)
            return jointly_raised

        for i in weak:
            slot = int(i)
            # The candidate is the current plan with this one slot raised, and
            # a raise at `slot` cannot change any state before it, so its
            # trajectory shares the current one's prefix exactly. Extending
            # from the state at the slot's own start — instead of replaying
            # the horizon from t=0 per weak slot (#1230) — runs the same step
            # function in the same order on the same values, so every
            # decision and the plan it produces are bit-identical to the full
            # replay's; only the skipped prefix work differs.
            plan[slot] = run_power
            candidate = base.copy()
            if self._dhw_raise_fits(
                candidate, base, ceiling, slot, plan, outdoor_temps,
                draw_rates, dt, humidity,
            ):
                base = candidate
            else:
                plan[slot] = 0.0
                # Zeroing a slot only lowers the trajectory, so the reference
                # is refreshed rather than left describing a plan that no
                # longer exists — from the slot, for the same prefix-reuse
                # reason as the check itself.
                self.model.extend_dhw_temps(
                    base, slot, plan, outdoor_temps, draw_rates, dt_hours=dt,
                    humidity=humidity,
                )
        repaired: np.ndarray = np.clip(plan, 0.0, p_dhw_max)
        return repaired

    def _dhw_raise_fits(
        self,
        candidate: np.ndarray,
        base: np.ndarray,
        ceiling: np.ndarray,
        slot: int,
        plan: np.ndarray,
        outdoor_temps: np.ndarray,
        draw_rates: np.ndarray,
        dt: float,
        humidity: np.ndarray | None,
    ) -> bool:
        """Extend ``candidate`` from ``slot`` and say whether it stays in bounds.

        The extension runs ``_DHW_MIN_RUN_CHUNK`` steps at a time and stops at
        the first chunk with a step above ``max(ceiling, base)``: a raise that
        breaches at once used to be simulated to the horizon anyway, 12-23 %
        of a single-zone DHW solve (R9 D9-s1-04). The same step function runs
        on the same values in the same order, so every decision is the whole
        suffix's; a refused candidate is discarded, never read past its stop.
        """
        size = plan.size
        pos = slot
        while pos < size:
            end = pos + _DHW_MIN_RUN_CHUNK
            self.model.extend_dhw_temps(
                candidate, pos, plan[:end], outdoor_temps, draw_rates,
                dt_hours=dt, humidity=humidity,
            )
            limit = np.maximum(ceiling[pos + 1: end + 1], base[pos + 1: end + 1])
            if not bool(np.all(candidate[pos + 1: end + 1] <= limit + 1e-9)):
                return False
            pos = end
        return True

    def _plan_dhw_cheapest_first(
        self,
        ctx: _DhwPlanContext,
        initial_temp: float,
        requirement: np.ndarray,
        draw_rates: np.ndarray,
        max_temp: np.ndarray,
        initial_plan: np.ndarray | None = None,
        forced_off: np.ndarray | None = None,
    ) -> np.ndarray:
        """Greedily top up a DHW plan in the cheapest feasible hours.

        Steps in ``forced_off`` are never candidates: a manual pin removed them
        from play, and the shortfall they leave has to be bought elsewhere.

        Used to repair whatever the linear cost program left short — the linear
        tank model ignores the COP's dependence on tank temperature and the
        10 °C cold-water floor — and as a complete fallback when that solve is
        unavailable.

        Repeatedly simulates the tank, finds the first step where the
        availability requirement would be missed, and buys the missing energy
        from the cheapest steps that precede it.

        Slots are ranked by *effective* price, i.e. the raw price inflated by
        the standby energy that would be lost while the heat waits in the tank.
        Storing early is therefore only chosen when it is genuinely cheaper than
        heating closer to the moment the water is needed.

        Because DHW production is a deferrable, essentially on/off load, this
        cheapest-first allocation is the cost-optimal strategy for it — and,
        unlike a gradient solve, it produces blocks the heat pump can actually
        run.
        """
        prices = ctx.prices
        outdoor_temps = ctx.outdoor_temps
        humidity = ctx.humidity
        n_steps = ctx.n_steps
        dt = ctx.dt
        p_dhw_max = ctx.p_dhw_max
        min_run_power = ctx.min_run_power
        max_lead_steps = ctx.max_lead_steps
        c_dhw = ctx.c_dhw
        if initial_plan is None:
            plan = np.zeros(n_steps)
        else:
            plan = np.clip(
                np.array(initial_plan, dtype=float), 0.0, p_dhw_max
            )
        if n_steps == 0 or c_dhw <= 0.0:
            return plan

        requirement, max_temp = _within_ceiling(requirement, max_temp)

        # Fraction of stored heat lost per hour of storage: raising the tank by
        # ΔT stores C·ΔT kWh but adds U·ΔT kW of standby loss.
        loss_rate_per_hour = (
            self.model.params.dhw_tank_heat_loss_coefficient / c_dhw
        )

        unreachable: set[int] = set()
        temps: np.ndarray | None = None
        for _ in range(400):
            temps, gaps, k = self._dhw_shortfall(
                temps, plan, initial_temp, outdoor_temps, draw_rates, dt,
                humidity, requirement, unreachable,
            )
            if k is None:
                break

            needed_kwh = float(gaps[k]) * c_dhw

            # The tank may not be planned above its ceiling, except that a
            # requirement (an anti-legionella cycle, typically) always has to
            # remain reachable. Per step, because the ceiling itself is: the
            # 1 °C working margin comes off each step's own limit, and the
            # step carrying the disinfection requirement keeps it.
            ceiling = np.maximum(max_temp - 1.0, float(requirement[k]))

            def usable(j: int) -> bool:
                if forced_off is not None and forced_off[j]:
                    return False
                return bool(
                    plan[j] < p_dhw_max - 1e-6
                    and temps[j + 1] < ceiling[j] - 0.1
                )

            candidates = [
                j for j in range(max(0, k - max_lead_steps), k + 1) if usable(j)
            ]
            if not candidates:
                candidates = [j for j in range(0, k + 1) if usable(j)]
            if not candidates:
                # Nothing can fix this step; move on rather than abandoning the
                # rest of the horizon.
                unreachable.add(k)
                continue

            def retained_fraction(j: int) -> float:
                return max(0.15, 1.0 - loss_rate_per_hour * (k - j) * dt)

            # Cheapest first, where "cheap" accounts for the heat lost while
            # stored; on a tie prefer the latest slot so the heat is stored for
            # as short a time as possible and blocks stay contiguous.
            candidates.sort(
                key=lambda j: (float(prices[j]) / retained_fraction(j), -j)
            )

            added = 0.0
            for j in candidates:
                cop = max(
                    1.0,
                    self.model.compute_cop_dhw(
                        float(outdoor_temps[j]), float(requirement[k]),
                        humidity=_step_humidity(humidity, j),
                    ),
                )
                spare_thermal_kwh = (p_dhw_max - plan[j]) * cop * dt
                # Heat added at step j raises every later tank temperature, so
                # the ceiling has to be respected across the whole stretch the
                # heat is stored for — not just at step j. With a per-step
                # ceiling the binding step is whichever has the least room
                # left, which is the same "peak against a flat ceiling" test
                # when the ceiling does not move.
                headroom_kwh = max(
                    0.0,
                    float(np.min(ceiling[j : k + 1] - temps[j + 1 : k + 2]))
                    * c_dhw,
                )
                take = min(
                    needed_kwh / retained_fraction(j),
                    spare_thermal_kwh,
                    headroom_kwh,
                )
                if take <= 1e-6:
                    continue
                plan[j] += take / (cop * dt)
                # Never plan a run below the pump's practical minimum: a
                # fraction of a kW cannot be delivered by an on/off DHW valve.
                if 0.0 < plan[j] < min_run_power:
                    plan[j] = min_run_power
                added = take
                # Charging one slot changes every later tank temperature, so
                # re-simulate before choosing the next one. This is what keeps
                # the plan from overshooting the tank's maximum temperature.
                self.model.extend_dhw_temps(
                    temps,
                    j,
                    plan,
                    outdoor_temps,
                    draw_rates,
                    dt_hours=dt,
                    humidity=humidity,
                )
                break

            if added <= 1e-9:
                # No candidate could absorb energy for this step either.
                unreachable.add(k)

        return np.clip(plan, 0.0, p_dhw_max)
