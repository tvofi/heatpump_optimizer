"""Model Predictive Control optimizer for heat pump cost minimization.

Plans the heat pump's power schedule over the forecast horizon (24 h by
default, 15-minute steps) against forecast prices and weather, re-solved every
update interval with only the first step ever acted on.

**How the solve is structured.** Hot water is a deferrable on/off load, so it
is planned first by a linear program plus a cheapest-first repair against the
real tank simulation (`_build_dhw_requirements`); a gradient solver would
smear it into an unrealizable trickle. Space heating is then optimized around
the fixed DHW blocks by multi-start L-BFGS-B, and one co-optimization pass
re-plans hot water against the solved space profile where the two competed
for the compressor.

**What the space objective actually minimizes:**

    grid_cost(P_space + P_dhw)        piecewise in PV surplus, × price_weight
    + comfort terms                   pull-to-target, floor/ceiling penalties
    + (cycling + capacity tariff)     × price_weight
    + terminal cost                   value of heat stored at the horizon end

Every term but the comfort penalties is in currency. There used to be one more
— a `0.01 · Σ ΔP²` smoothness regulariser — and it was removed in v3.9.0
because it was priced in invented units and cost real money: about 5 % of the
two-zone winter bill, at no reduction in compressor starts. Discouraging
chatter is `cycling_cost`'s job, and that is denominated in currency per
start-stop cycle, so the trade against electricity is one the user can read.

subject to 0 ≤ P_space[k] ≤ P_max − P_dhw[k] (the pump can be off; values
below its modulation floor read as duty cycling within the step) and the
thermal dynamics of the configured model. Comfort bounds are soft penalties,
not constraints — a hard band could make a cold morning infeasible.

Weather anticipation is emergent rather than a separate term: the trajectory
simulation applies forecast solar gain and wind/rain loss factors at each
step, so heating before a sunny spell or coasting into a windy evening prices
itself.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

import numpy as np
from scipy.optimize import linprog, minimize

from . import mixing_valve, pv
from .const import (
    DEFAULT_CYCLING_COST,
    DEFAULT_PRICE_RISK_LAMBDA,
    DHW_QUANTILE_MIN_EVENTS,
    WOOD_TANK_MAX_TEMP,
)
from .dhw_draws import window_label as draw_window_label
from .thermal_model import (
    DHW_AMBIENT_TEMP,
    ThermalModel,
    ThermalState,
    dhw_coil_draw_reduction,
    wood_share,
)
from .tariff import (
    CapacityTariff,
    metering_windows,
    peak_cost,
    realised_peak,
    window_factors,
)
from .dhw_schedule import (
    FULL_DAY,
    Window,
    format_windows,
    hour_in_windows,
    hours_until_next_window,
    parse_windows,
)

_LOGGER = logging.getLogger(__name__)

# How far either side of a contended step space heating may look for spare
# compressor capacity when its energy is displaced by hot water. Beyond a few
# hours the building has already lost the heat, so a cheap slot that far away
# is not a real substitute.
_DHW_REFILL_WINDOW_HOURS = 6.0

# The comfort penalty on breaching the user's minimum temperature is quadratic,
# which means its gradient vanishes as the violation approaches zero: a 0.05 C
# breach costs almost nothing while the electricity it saves is worth real
# money, so the solver settles just under the bound. Adding a small linear term
# gives the penalty a non-zero slope at the boundary, which is the standard
# exact penalty construction and pins the trajectory to the floor instead of
# just below it. Tuned to the smallest value that removes the residual
# violations across the validation scenarios; larger values buy nothing and
# start holding a wasteful margin above the floor.
_COMFORT_FLOOR_L1 = 2.0

# Strength of the pull towards the comfort *target*, as distinct from the
# penalty for breaching the user's *bounds*. Halved in v3.9.0 after measuring
# what the old strength cost: on the winter scenario the plan spent 28.55 SEK
# instead of 23.28 -- 18 % of the bill -- buying an average 0.32 K of warmth
# above what the band required, while never coming near the floor. Below half
# the saving plateaus (23.28 at every lower value tested), so this is the point
# where the money stops improving and a real preference for the setpoint is
# still expressed. The two-zone figure is half again because that branch
# averages two zones rather than summing them.
_COMFORT_PULL_SINGLE_ZONE = 0.025
_COMFORT_PULL_TWO_ZONE = 0.0125

# How many of the candidate starting points are actually optimized. Going from
# one to two removes most of the local-optimum gap in the two-zone model
# (2.2% cheaper in the validation scenarios); a third start buys a further
# 0.2% for another full solve, which is not worth roughly doubling the runtime
# again on the low-powered hardware Home Assistant usually runs on.
_MULTI_START_SOLVES = 2


def _multi_start_minimize(
    objective,
    candidates: list[np.ndarray],
    bounds: list[tuple[float, float]],
    args: tuple = (),
    maxiter: int = 300,
):
    """Run L-BFGS-B from several starting points and keep the best result.

    The space heating objective is not convex: the comfort penalty is only
    active on one side of the temperature band, and the price signal creates
    several distinct "charge here, coast there" patterns that are each locally
    optimal. A gradient method started from a single guess can therefore stop
    at a schedule that random perturbation can beat, which is exactly what the
    two-zone case showed.

    Rather than pay for a full solve from every candidate, the candidates are
    first scored on the objective directly, which is cheap, and only the two
    most promising are actually optimized. That keeps the cost at roughly two
    solves while removing the dependence on a single lucky initial guess.
    """
    scored = []
    for guess in candidates:
        try:
            score = float(objective(guess, *args))
        except Exception:
            continue
        if np.isfinite(score):
            scored.append((score, guess))
    if not scored:
        raise ValueError("no usable starting point")
    scored.sort(key=lambda item: item[0])

    best = None
    best_score = np.inf
    last_error: Exception | None = None
    for _, guess in scored[:_MULTI_START_SOLVES]:
        try:
            res = minimize(
                objective,
                guess,
                args=args,
                method="L-BFGS-B",
                bounds=bounds,
                options={"maxiter": maxiter, "ftol": 1e-6, "eps": 1e-4},
            )
        except Exception as err:  # pragma: no cover - solver blow-up
            last_error = err
            continue
        score = float(objective(res.x, *args))
        if np.isfinite(score) and score < best_score:
            best, best_score = res, score
    if best is None:
        raise last_error or ValueError("all starting points failed")
    return best


#: Below this horizon-mean price (SEK/kWh) the smooth guess's normalisation
#: is meaningless: a negative mean flips its sign — the cheapest (most
#: negative) steps clip to the LOW floor and the guess starts inverted — and
#: a near-zero mean divides by ~1e-6 and saturates the clip into bang-bang
#: at arbitrary steps. Real Nordic spring days do average below zero.
PRICE_MEAN_GUESS_EPS = 1e-3


def _price_guess_weights(prices: np.ndarray) -> np.ndarray:
    """Per-step initial-guess weight in [0.2, 1.0], high where cheap.

    On any meaningfully positive horizon mean this is the historical smooth
    mean-normalised guess, arithmetic untouched so every normal solve starts
    from bit-identical floats. Otherwise the same [0.2, 1.0] band is filled
    by price rank — relative ordering is all the guess exists to encode, and
    ranks keep it under any sign or scale. Shift-by-min would not: it warps
    the relative spacing the clip band then quantises.
    """
    if float(np.mean(prices)) > PRICE_MEAN_GUESS_EPS:
        return np.clip(1.5 - prices / (np.mean(prices) + 1e-6), 0.2, 1.0)
    ranks = np.argsort(np.argsort(prices)).astype(float)
    return 1.0 - 0.8 * ranks / float(max(len(prices) - 1, 1))


def _price_ranked_start(
    prices: np.ndarray, energy_kwh: float, p_max: float, dt: float
) -> np.ndarray:
    """A bang-bang schedule that buys the cheapest steps first.

    This is the shape a cost-minimal plan takes when comfort is not binding,
    and it is structurally very different from the smooth price-weighted guess,
    which is what makes it useful as a second starting point.
    """
    schedule = np.zeros_like(prices, dtype=float)
    if energy_kwh <= 0 or p_max <= 0 or dt <= 0:
        return schedule
    remaining = float(energy_kwh)
    for idx in np.argsort(prices):
        if remaining <= 0:
            break
        take = min(p_max, remaining / dt)
        schedule[idx] = take
        remaining -= take * dt
    return schedule


def _savings_percentage(savings: float, baseline_cost: float) -> float:
    """Savings as a percentage of the baseline, clamped to a sensible range.

    A baseline at or near zero (a warm day where a thermostat would barely run)
    would otherwise turn rounding noise into a huge percentage.
    """
    if baseline_cost <= 0.01:
        return 0.0
    return float(np.clip(savings / baseline_cost * 100.0, -100.0, 100.0))


# ---------------------------------------------------------------------------
# Compressor cycling and capacity tariff
# ---------------------------------------------------------------------------


def count_compressor_starts(power: np.ndarray, threshold: float = 0.1) -> int:
    """Number of off→on transitions in a schedule.

    Measurement first: the backlog note for this feature was explicit that a
    cycling penalty should only be paid for if realistic plans actually
    chatter. This is what the validation harness reports, and it is published
    on the result so the question stays answerable after the fact.
    """
    running = np.asarray(power, dtype=float) > threshold
    if running.size == 0:
        return 0
    starts = int(running[0])
    starts += int(np.sum(running[1:] & ~running[:-1]))
    return starts


def cycling_penalty(
    power: np.ndarray, cost_per_cycle: float, p_max: float
) -> float:
    """Smooth stand-in for a per-start cost.

    ``sum |ΔP|`` over the schedule counts total power swing. One complete
    start-stop cycle at full power contributes ``2·p_max``, so dividing by that
    expresses the L1 term in units of whole cycles and makes ``cost_per_cycle``
    mean what its name says.
    """
    if cost_per_cycle <= 0 or p_max <= 0 or len(power) < 2:
        return 0.0
    swing = float(np.sum(np.abs(np.diff(np.asarray(power, dtype=float)))))
    return cost_per_cycle * swing / (2.0 * p_max)


# ---------------------------------------------------------------------------
# Plan reason codes (item 16)
# ---------------------------------------------------------------------------

REASON_COMFORT_FLOOR = "comfort_floor"
REASON_CHEAP_PRICE = "cheap_price"
REASON_PREHEAT_WEATHER = "preheat_weather"
REASON_TERMINAL_VALUE = "terminal_value"
REASON_SOLAR_SURPLUS = "solar_surplus"
REASON_DHW_WINDOW = "dhw_window"
REASON_DHW_READY = "dhw_ready"
REASON_DHW_PREHEAT = "dhw_preheat"
REASON_LEGIONELLA = "legionella"
REASON_IDLE = "idle"


def classify_space_steps(
    power: np.ndarray,
    prices: np.ndarray,
    room_temps: np.ndarray,
    temp_min_bounds: np.ndarray,
    heat_loss_factors: np.ndarray,
    surplus: np.ndarray | None,
    n_steps: int,
    threshold: float = 0.05,
) -> list[str]:
    """Why each space-heating step is where it is.

    The plan sensors published *which* slots were chosen but never *why*. A
    slot could be cheapest-price, comfort-floor, weather pre-heat, terminal
    value or solar self-consumption, and nothing distinguished them — so an
    unexpected slot was indistinguishable from a bug. That makes the optimizer
    hard to trust and hard to support, and it makes bug reports much weaker
    than they could be.

    The classification is a post-hoc reading of the solved plan rather than
    something the solver emits, because the objective is a single scalar and
    there is no point in the LP at which one term "wins". Ranked, so the most
    specific explanation is the one reported.
    """
    reasons: list[str] = []
    if n_steps == 0:
        return reasons
    cheap_cut = float(np.percentile(prices, 35)) if len(prices) else 0.0
    for i in range(n_steps):
        if power[i] <= threshold:
            reasons.append(REASON_IDLE)
            continue
        # Closest to a hard requirement wins: at or below the comfort floor,
        # the plan has no choice.
        room = room_temps[i + 1] if i + 1 < len(room_temps) else room_temps[-1]
        if room <= temp_min_bounds[i] + 0.15:
            reasons.append(REASON_COMFORT_FLOOR)
            continue
        if surplus is not None and i < len(surplus) and surplus[i] > 1e-6:
            reasons.append(REASON_SOLAR_SURPLUS)
            continue
        if i >= n_steps - max(1, int(0.08 * n_steps)):
            reasons.append(REASON_TERMINAL_VALUE)
            continue
        if i < len(heat_loss_factors) and heat_loss_factors[i] > 1.1:
            reasons.append(REASON_PREHEAT_WEATHER)
            continue
        if prices[i] <= cheap_cut:
            reasons.append(REASON_CHEAP_PRICE)
            continue
        reasons.append(REASON_PREHEAT_WEATHER)
    return reasons


def classify_dhw_steps(
    power: np.ndarray,
    in_window: np.ndarray,
    ready_temps: np.ndarray,
    legionella_step: int | None,
    n_steps: int,
    threshold: float = 0.05,
) -> list[str]:
    """Why each hot-water step is where it is."""
    reasons: list[str] = []
    for i in range(n_steps):
        if power[i] <= threshold:
            reasons.append(REASON_IDLE)
            continue
        if legionella_step is not None and i == legionella_step:
            reasons.append(REASON_LEGIONELLA)
            continue
        if i < len(ready_temps) and ready_temps[i] > 0:
            reasons.append(REASON_DHW_READY)
            continue
        if i < len(in_window) and in_window[i]:
            reasons.append(REASON_DHW_WINDOW)
            continue
        reasons.append(REASON_DHW_PREHEAT)
    return reasons


# ---------------------------------------------------------------------------
# Manual plan override (pinning when the pump runs)
# ---------------------------------------------------------------------------
#
# A user who hand-arranges their day pins individual steps on or off. The pin
# arrays are floats — NaN means "leave it to the optimizer", 0 forces the step
# off, 1 forces it on — so a whole channel is a single array the solver bounds
# can be built from directly. See ``manual_plan.py`` for how they are produced.

#: A step ran because the manual plan said so, not because the optimizer chose
#: it. Kept distinct from the automatic reasons so a pinned slot is never
#: mistaken for the solver's own decision.
REASON_MANUAL = "manual_plan"

#: How many times a manual plan may be repaired before its forced-off slots are
#: abandoned entirely. Each round costs a full solve, so this trades run time
#: against how precisely an unsafe plan can be salvaged.
_SAFETY_REPAIR_ROUNDS = 3

#: Reasons a pinned-on step keeps rather than being relabelled manual: they are
#: hard requirements it would have run for regardless of the pin.
_MANUAL_KEEP_REASONS = frozenset(
    {REASON_IDLE, REASON_COMFORT_FLOOR, REASON_LEGIONELLA}
)


def _pin_is_free(pin: float) -> bool:
    """True when a pin leaves the step to the optimizer (NaN)."""
    return pin != pin


def _apply_pins_to_bounds(
    bounds: list[tuple[float, float]],
    pins: np.ndarray | None,
    min_on_power: float,
) -> list[tuple[float, float]]:
    """Rewrite per-step solver bounds so pinned steps run or stay off.

    A forced-off step is clamped shut. A forced-on step has its *lower* bound
    raised to ``min_on_power`` so L-BFGS-B must actually run it, while its upper
    bound is left alone — the user pinned *when* the pump runs, not *how hard*,
    so the magnitude is still the optimizer's to choose. The lower bound is
    clamped to the existing upper bound because that upper bound can legitimately
    be zero (the other channel has taken all the capacity), and a lower bound
    above the upper bound makes the solve diverge.
    """
    if pins is None:
        return bounds
    out = list(bounds)
    for i in range(min(len(out), len(pins))):
        pin = float(pins[i])
        if _pin_is_free(pin):
            continue
        _low, high = out[i]
        if pin >= 0.5:
            out[i] = (min(min_on_power, high), high)
        else:
            out[i] = (0.0, 0.0)
    return out


def _mark_manual_reasons(
    reasons: list[str], pins: np.ndarray | None
) -> list[str]:
    """Relabel steps the manual plan forced on, unless a hard reason applies.

    A forced-on step that would have run anyway — because it is at the comfort
    floor or is the legionella cycle — keeps that more specific reason; every
    other running forced-on step is attributed to the manual plan.
    """
    if pins is None:
        return reasons
    out = list(reasons)
    for i in range(min(len(out), len(pins))):
        pin = float(pins[i])
        if _pin_is_free(pin) or pin < 0.5:
            continue
        if out[i] not in _MANUAL_KEEP_REASONS:
            out[i] = REASON_MANUAL
    return out


@dataclass
class OptimizationResult:
    """Result of the MPC optimization."""

    power_schedule: list[float]  # kW electrical per time step (space heating)
    room_temp_trajectory: list[float]  # °C predicted avg room temp
    slab_temp_trajectory: list[float]  # °C predicted slab temp
    timestamps: list[datetime]  # timestamp for each step
    prices: list[float]  # electricity price per step
    predicted_cost: float  # total cost in currency units
    baseline_cost: float  # cost with constant-temp strategy
    predicted_savings: float  # savings vs baseline
    savings_percentage: float  # savings as percentage
    optimal_setpoints: list[float]  # recommended setpoints per step
    status: str  # optimization status
    solve_time_ms: float = 0.0
    # Cost of restoring heat the plan left unstored at the end of the horizon.
    # Excluded from predicted_cost (which is what will actually be spent in the
    # window) but charged against the savings so borrowed heat is not counted
    # as a saving.
    deferred_energy_cost: float = 0.0

    # Outdoor temperature actually used for each step, so consumers can plot
    # the plan against the weather it was made for.
    outdoor_temps: list[float] = field(default_factory=list)

    # ECL110-oriented control outputs
    displace_schedule: list[float] = field(default_factory=list)
    heat_pump_on_schedule: list[bool] = field(default_factory=list)

    # The planned buffer-tank temperature, one entry per step boundary. Empty
    # without a mixing valve, where the tank is a hydraulic separator and its
    # temperature is not a decision. It is the only view anyone -- a sensor, the
    # card, a test -- has of whether the plan intends to store anything: the
    # model stashes the series on itself for the terminal-cost term and nothing
    # else could reach it.
    buffer_temp_trajectory: list[float] = field(default_factory=list)
    # The valve target the plan wants at each step, fully resolved. Non-empty
    # only in smart_write mode when a hold schedule beat the fixed target on
    # the objective: low between charging and the price peak so the tank keeps
    # its heat, back to the working target through the peak. The actuator
    # writes the current step's entry each cycle.
    valve_target_schedule: list[float] = field(default_factory=list)
    # The planned wood-tank temperature, one entry per step boundary. Empty
    # unless the two-tank topology is modelled (issue #40) — mirrors
    # buffer_temp_trajectory as the only external view of the wood store.
    wood_temp_trajectory: list[float] = field(default_factory=list)
    # The achieved objective value of this plan, for candidate comparison --
    # two solves under different valve schedules are two controls priced by
    # the same physics, so the smaller wins. NaN when a solve failed.
    objective_value: float = float("nan")
    # Two-zone trajectories
    upper_temp_trajectory: list[float] = field(default_factory=list)
    lower_temp_trajectory: list[float] = field(default_factory=list)
    solar_gain_trajectory: list[float] = field(default_factory=list)
    upper_setpoints: list[float] = field(default_factory=list)
    lower_setpoints: list[float] = field(default_factory=list)

    # DHW optimization results
    dhw_power_schedule: list[float] = field(default_factory=list)
    dhw_temp_trajectory: list[float] = field(default_factory=list)
    dhw_heating_cost: float = 0.0

    # Predictive insights
    predictive_info: dict[str, Any] = field(default_factory=dict)

    # --- Plan reason codes (item 16) -----------------------------------
    #: Per-step explanation of why the plan does what it does.
    space_reasons: list[str] = field(default_factory=list)
    dhw_reasons: list[str] = field(default_factory=list)

    # --- Price provenance (item 7) -------------------------------------
    #: True where the price came from the published market data, False where
    #: it came from the learned diurnal prior. A plan that looks identical
    #: whether or not it rests on real prices cannot be audited.
    price_known: list[bool] = field(default_factory=list)

    # --- Capacity tariff and cycling (items 8, 10) ---------------------
    #: Peak the plan would set, in kW at the house connection.
    projected_peak_kw: float = 0.0
    #: Cost of that peak above what the month has already committed to.
    peak_cost: float = 0.0
    #: Off→on transitions in the space heating schedule.
    compressor_starts: int = 0

    # --- PV self-consumption (item 9) ----------------------------------
    #: Forecast surplus (production minus baseline load) per step, kW.
    pv_surplus: list[float] = field(default_factory=list)
    #: Heat pump energy served from surplus rather than imported, kWh.
    pv_self_consumed_kwh: float = 0.0

    # --- Manual plan override ------------------------------------------
    #: True when a manual plan pinned any step in this solve.
    manual_pins_active: bool = False
    #: Steps whose forced-off pin had to be released for safety (comfort floor,
    #: tank minimum or legionella), so the UI can show where the plan yielded.
    manual_released_space: list[int] = field(default_factory=list)
    manual_released_dhw: list[int] = field(default_factory=list)


@dataclass
class OptimizationConfig:
    """Configuration for the optimizer."""

    # Temperature constraints
    target_temp: float = 21.0
    min_temp: float = 19.0
    max_temp: float = 23.0
    comfort_temp_day: float = 21.0
    comfort_temp_night: float = 19.5
    day_start_hour: int = 7
    day_end_hour: int = 22

    # Optimization parameters
    horizon_hours: float = 24.0
    time_step_minutes: float = 15.0
    price_weight: float = 1.0
    comfort_weight: float = 5.0

    # --- Compressor cycling (item 10) ---------------------------------
    # Every compressor start has real costs: oil dilution and wear, the loss
    # while the system re-establishes steady state, and on some units a
    # defrost penalty. Nothing in either optimizer path used to stop a plan
    # from chattering between steps.
    #
    # Modelled as a smooth L1 term on the step-to-step power difference rather
    # than a true minimum-runtime constraint. The L1 keeps the problem
    # continuous and cheap; a minimum-runtime constraint would make it a MILP,
    # which is not affordable inside a 30-second Home Assistant update on the
    # hardware this usually runs on.
    #: Currency cost attributed to one full start-stop cycle.
    #: Mirrors ``const.DEFAULT_CYCLING_COST`` rather than restating it, so the
    #: objective a harness builds directly is the objective that ships. The two
    #: had silently drifted apart once before, which meant the tests were
    #: measuring a slightly different optimizer from the integration.
    cycling_cost: float = DEFAULT_CYCLING_COST

    # --- Capacity tariff (item 8) --------------------------------------
    #: Currency per kW of new monthly peak, already divided by the number of
    #: peaks the DSO averages. Zero disables the term entirely.
    peak_price_per_kw: float = 0.0
    #: The level above which a new peak would raise the bill, in kW.
    peak_threshold_kw: float = 0.0
    #: Metering window of the tariff, in minutes.
    peak_window_minutes: int = 60
    #: How many of the month's highest peaks the DSO averages for the bill.
    peak_count: int = 3
    #: Whole-house load excluding the heat pump, per step, in kW.
    baseline_load_kw: Any = None

    # --- PV self-consumption (item 9) -----------------------------------
    #: What an exported kWh earns, in the currency of the import price. With
    #: forecast surplus available, consumption up to it is priced at this
    #: rather than at the import price; see `pv.piecewise_cost`.
    pv_export_price: float = 0.0

    # --- Effekttariff masks (#13) --------------------------------------
    #: Months the capacity tariff applies in at all; empty = every month.
    peak_months: Any = frozenset()
    #: Peak-hour windows (dhw_schedule ``Window`` tuples); empty = always.
    peak_hours: Any = ()
    #: Weekends bill as off-peak when set.
    peak_weekdays_only: bool = False
    #: What an off-peak window's kW counts at; 1.0 = the flat model.
    peak_offpeak_factor: float = 1.0

    # --- Risk-adjusted unknown-horizon pricing (#34) --------------------
    #: Premium multiplier on the prior's per-step dispersion. Zero prices
    #: prior-filled steps at the mean, exactly as before.
    price_risk_lambda: float = DEFAULT_PRICE_RISK_LAMBDA

    @property
    def n_steps(self) -> int:
        """Number of optimization steps."""
        return int(self.horizon_hours * 60 / self.time_step_minutes)

    @property
    def dt_hours(self) -> float:
        """Time step in hours."""
        return self.time_step_minutes / 60.0

    def get_comfort_temp(self, hour: float) -> float:
        """Get comfort temperature for a given hour of day."""
        if self.day_start_hour <= hour < self.day_end_hour:
            return self.comfort_temp_day
        return self.comfort_temp_night

    def get_temp_bounds(self, hour: float) -> tuple[float, float]:
        """Get temperature bounds for a given hour."""
        if self.day_start_hour <= hour < self.day_end_hour:
            return (self.min_temp, self.max_temp)
        return (self.min_temp - 0.5, self.max_temp)

    def baseline_load_array(self, n_steps: int) -> np.ndarray:
        """Per-step whole-house baseline load, padded or truncated to fit."""
        if self.baseline_load_kw is None:
            return np.zeros(n_steps, dtype=float)
        values = np.asarray(self.baseline_load_kw, dtype=float).ravel()
        if values.size == 0:
            return np.zeros(n_steps, dtype=float)
        if values.size >= n_steps:
            return values[:n_steps]
        return np.concatenate(
            [values, np.full(n_steps - values.size, float(values[-1]))]
        )


def _solver_status(result, objective, initial_guess) -> str:
    """Classify a SciPy result, tolerating benign line-search aborts.

    L-BFGS-B reports ABNORMAL_TERMINATION_IN_LNSRCH whenever the line search
    cannot make further progress. On a flat price curve the cost surface is
    genuinely degenerate along the arbitrage direction, so this fires routinely
    even though the returned point is perfectly good. Surfacing that to the
    user as "suboptimal" is misleading, so only call it suboptimal when the
    solver actually failed to improve on the starting point.
    """
    if result.success:
        return "optimal"
    try:
        if objective(result.x) <= objective(initial_guess):
            return "optimal"
    except Exception:  # pragma: no cover - defensive
        pass
    return f"suboptimal ({result.message})"


@dataclass(frozen=True)
class _Horizon:
    """Everything about one solve that both optimization paths need.

    These eighteen values were previously threaded through two near-identical
    eighteen-parameter signatures. Collecting them removes that duplication,
    but the real benefit is that adding a new per-solve input is now a single
    edit instead of four (two signatures, two call sites) — which is exactly
    the kind of divergence that let the two objectives drift apart before.

    Frozen because nothing downstream should be rewriting the horizon it was
    handed; a path that wants a variation makes its own.
    """

    initial_state: ThermalState
    prices: np.ndarray
    outdoor_temps: np.ndarray
    wind_speeds: np.ndarray
    precipitation: np.ndarray
    solar_radiation: np.ndarray
    start_time: datetime
    n_steps: int
    dt: float
    #: Per-step comfort target and the bounds either side of it.
    comfort_targets: np.ndarray
    temp_min_bounds: np.ndarray
    temp_max_bounds: np.ndarray
    #: Hour-of-day per step, for the DHW draw pattern and demand windows.
    step_hours: np.ndarray
    #: Solar gain in kW, and the wind/rain multiplier on heat loss, per step.
    solar_gains: np.ndarray
    heat_loss_factors: np.ndarray
    #: Output of ``_analyze_forecast_trajectory``.
    forecast: dict
    #: ``time.monotonic()`` at the start of the solve, for the timing report.
    t_start: float
    #: Optional per-step manual pins, one array per channel, or ``None`` when
    #: that channel is fully automatic. Encoding: NaN free, 0 off, 1 on.
    space_pins: np.ndarray | None = None
    dhw_pins: np.ndarray | None = None
    #: Optional per-step ceiling on space-heating power, kW. The pin encoding
    #: can force a step on or off but cannot say "at most this much", which is
    #: what the buffer tank's hard temperature cap needs: the tighten-and-
    #: re-solve loop in ``optimize`` lowers entries here at steps that charged
    #: a full tank. ``None`` means the nameplate maximum everywhere.
    power_caps: np.ndarray | None = None
    #: Optional per-step *total electrical* ceiling, kW — the fuse guard and
    #: shadow solves (item 3). ``power_caps`` above bounds space heating
    #: alone; this one bounds space **plus** hot water, so the DHW planner
    #: and ``solve_space`` both have to respect it. Already clipped to ≥ 0
    #: and padded to ``n_steps``. ``None`` means uncapped.
    power_caps_extra: np.ndarray | None = None
    #: Optional per-step forecast of free thermal input, kW — a wood furnace
    #: burn (item 28). Both objectives and the savings baseline simulate with
    #: it, so the plan defers electric heat the furnace is already providing
    #: and the reference thermostat is granted the same free heat rather than
    #: booking it as savings. ``None`` means none.
    external_heat_kw: np.ndarray | None = None
    #: Optional per-step mixing-valve target schedule, fully resolved. Only
    #: the objectives simulate with it — the savings baseline is a thermostat
    #: and a thermostat does not schedule a valve. ``None`` means the static
    #: configured target, which is byte-for-byte the previous behaviour.
    valve_targets: np.ndarray | None = None
    #: Optional forecast relative humidity per step (#21), for the defrost
    #: derate; NaN marks unknown steps. ``None`` falls back to the single
    #: ambient value, which is byte-for-byte the previous behaviour.
    humidity: np.ndarray | None = None

    @property
    def timestamps(self) -> list[datetime]:
        return [
            self.start_time + timedelta(hours=i * self.dt)
            for i in range(self.n_steps)
        ]

    @property
    def weather(self) -> dict[str, np.ndarray]:
        """Keyword arguments the simulation and baseline calls share."""
        return {
            "outdoor_temps": self.outdoor_temps,
            "wind_speeds": self.wind_speeds,
            "precipitation": self.precipitation,
            "solar_radiation": self.solar_radiation,
        }


class HeatPumpOptimizer:
    """MPC-based heat pump cost optimizer with predictive weather anticipation and DHW."""

    def __init__(
        self,
        thermal_model: ThermalModel,
        config: OptimizationConfig,
    ) -> None:
        """Initialize the optimizer."""
        self.model = thermal_model
        self.config = config
        # Populated per solve by ``optimize``; kept as attributes so the two
        # solve paths can reach them without threading five more parameters
        # through their already long signatures.
        self._price_known: np.ndarray | None = None
        self._pv_surplus: np.ndarray | None = None
        # Stashed by ``_build_dhw_requirements`` for the safety-release loop:
        # the tank temperature the plan must keep the DHW trajectory above, and
        # which step (if any) carries the legionella cycle.
        self._dhw_requirement: np.ndarray | None = None
        self._dhw_legionella_step: int | None = None
        #: The solve's starting buffer temperature; floors the settlement
        #: value cap so pre-stored heat cannot be drained for free.
        self._initial_buffer_temp: float | None = None

    # ------------------------------------------------------------------
    # Shared cost terms
    # ------------------------------------------------------------------

    def _anticipatory_weights(
        self,
        n_steps: int,
        dt: float,
        solar_gains: np.ndarray,
        heat_loss_factors: np.ndarray,
    ) -> np.ndarray:
        """Warm-start shaping for the *initial guess* only.

        A cheap forecast-aware nudge: start the solver lower where sun is
        coming and higher where the weather is about to turn, so L-BFGS-B
        begins near the shape of the answer.

        These weights used to scale the comfort-violation penalty as well,
        which discounted a real breach of the user's minimum temperature
        because the sun might come out later. That is backwards — if the sun
        does arrive, the simulated trajectory is not cold and no penalty arises
        anyway, so the discount could only ever buy under-heating.
        """
        weights = np.ones(n_steps)
        lookahead = int(8 / dt)
        for i in range(n_steps):
            end = min(i + lookahead, n_steps)
            if end <= i:
                continue
            future_solar = np.mean(solar_gains[i:end])
            if future_solar > 0.5:  # > 0.5 kW solar gain is significant
                weights[i] *= max(0.6, 1.0 - future_solar * 0.3)
            future_loss = np.mean(heat_loss_factors[i:end])
            if future_loss > 1.1:
                weights[i] *= min(1.5, future_loss)
        return weights

    def _comfort_terms(
        self,
        room_temps: np.ndarray,
        upper_temps: np.ndarray,
        lower_temps: np.ndarray,
        comfort_targets: np.ndarray,
        temp_min_bounds: np.ndarray,
        temp_max_bounds: np.ndarray,
        comfort_band: np.ndarray,
    ) -> tuple[float, float]:
        """The comfort penalty and the pull-to-target cost.

        Returns them separately because they mean different things: the first
        is the price of breaching the user's bounds, the second is a mild
        preference for sitting near the target inside them.

        Two-zone penalties are *averaged* over the zones rather than summed.
        Summing made a two-zone house behave as if ``comfort_weight`` were set
        twice as high as configured, so it hugged the setpoint and gave up most
        of the available savings.

        **The pull is deliberately weak.** The user states a *band*, and the
        band is what the plan owes them; the target is a preference inside it.
        At twice the current strength the pull was quietly expensive: measured
        on the winter scenario it cost 28.55 SEK against 23.28 -- 18 % of the
        bill -- to hold the house 0.32 K warmer on average while never
        approaching the floor. Nobody asked for that trade, and
        ``comfort_weight`` is the knob for anyone who wants it back.
        """
        weight = self.config.comfort_weight

        if self.model.params.two_zone_enabled:
            upper_t = upper_temps[1:]
            lower_t = lower_temps[1:]

            undershoot_u = np.maximum(0, temp_min_bounds - upper_t)
            overshoot_u = np.maximum(0, upper_t - temp_max_bounds)
            undershoot_l = np.maximum(0, temp_min_bounds - lower_t)
            overshoot_l = np.maximum(0, lower_t - temp_max_bounds)

            penalty = 0.5 * weight * (
                np.sum(undershoot_u ** 2) * 10.0
                + np.sum(overshoot_u ** 2) * 5.0
                + np.sum(undershoot_l ** 2) * 10.0
                + np.sum(overshoot_l ** 2) * 5.0
                + (np.sum(undershoot_u) + np.sum(undershoot_l)) * _COMFORT_FLOOR_L1
            )

            comfort_dev_u = upper_t - comfort_targets
            comfort_dev_l = lower_t - comfort_targets
            comfort_cost = _COMFORT_PULL_TWO_ZONE * weight * (
                np.sum((comfort_dev_u / comfort_band) ** 2)
                + np.sum((comfort_dev_l / comfort_band) ** 2)
            )
            return penalty, comfort_cost

        room_t = room_temps[1:]
        undershoot = np.maximum(0, temp_min_bounds - room_t)
        overshoot = np.maximum(0, room_t - temp_max_bounds)

        penalty = weight * (
            np.sum(undershoot ** 2) * 10.0
            + np.sum(overshoot ** 2) * 5.0
            + np.sum(undershoot) * _COMFORT_FLOOR_L1
        )
        deviation = room_t - comfort_targets
        comfort_cost = (
            _COMFORT_PULL_SINGLE_ZONE
            * weight
            * np.sum((deviation / comfort_band) ** 2)
        )
        return penalty, comfort_cost

    def _terminal_cost(self, prices: np.ndarray, outdoor_temps: np.ndarray):
        """Price the heat the plan leaves unstored at the end of the horizon.

        Nothing beyond the horizon is scored, so without this the optimizer
        always dumps the last couple of hours: it coasts the house down because
        the resulting cold never appears in the objective. That both breaches
        the comfort floor at the tail of the plan and reports a saving that was
        really borrowed heat.

        The shortfall is priced against the same reference the savings
        settle-up uses — the 25th-percentile price and the mean-outdoor COP,
        exactly as ``_deferred_energy_cost`` prices it — so the plan and the
        reported savings agree. Scaled by ``price_weight`` because the energy
        term is: an unscaled terminal cost at a non-default weight changes the
        exchange rate between buying heat now and buying it back later, which
        re-creates the tail-dumping this term exists to prevent.

        Each store's deficit converts at that store's own marginal COP
        (v4.0.5, ``ThermalModel.marginal_cop``). The building mass refills at
        the plain curve, but the buffer tank charges at the flow-derated COP
        of its settlement temperature — the same physics the simulation
        applies while charging it. Pricing the tank's terminal kWh at the
        plain curve paid back less per kWh than storing it cost, so the
        solver only stored when the price spread also covered a COP gap the
        physics never charged: systematic under-charging.
        """
        caps = self._settlement_caps(outdoor_temps)
        refill_price = (
            float(np.percentile(prices, 25)) * self.config.price_weight
        )
        out_mean = float(np.mean(outdoor_temps))
        cop_end = self.model.compute_cop(out_mean)
        # Equal to `cop_end` bit for bit whenever no valve throttles (the
        # `cop_flow_carnot` gate) or the cap sits at the flow reference; the
        # branch below keeps those paths on the historical arithmetic.
        cop_buffer = self.model.marginal_cop(
            out_mean, "buffer", store_temp=caps["buffer"]
        )
        params = self.model.params

        if params.two_zone_enabled:
            stores = (
                (params.upper_floor_thermal_mass, "upper", caps["room"]),
                (params.lower_floor_thermal_mass, "lower", caps["room"]),
                (params.slab_thermal_mass, "slab", caps["slab"]),
            )
            if params.buffer_is_store:
                # Only with a valve, and only a tank big enough to matter.
                # Without a valve the tank cannot be charged, so adding it
                # here would put a constant in the objective -- it would not
                # change which plan wins, but it would move every reported
                # number for no reason. A tiny tank (item 27) holds less than
                # one step of heat, and crediting it has the solver planning
                # around noise.
                stores = stores + (
                    (params.buffer_tank_thermal_mass, "buffer", caps["buffer"]),
                )
        else:
            stores = (
                (params.room_thermal_mass, "room", caps["room"]),
                (params.slab_thermal_mass, "slab", caps["slab"]),
            )

        def cost(
            room_temps, slab_temps, upper_temps, lower_temps, buffer_temps=None
        ) -> float:
            ends = {
                "room": float(room_temps[-1]),
                "slab": float(slab_temps[-1]),
                "upper": float(upper_temps[-1]),
                "lower": float(lower_temps[-1]),
                # A tank left cold is heat that has to be bought back, exactly
                # like a cold slab. Leaving it out is what made charging look
                # like pure cost with no benefit, so no starting point could
                # ever descend towards storing anything.
                "buffer": (
                    float(buffer_temps[-1]) if buffer_temps is not None else 0.0
                ),
            }
            # The buffer's deficit converts at its own (flow-derated) COP;
            # everything else at the plain curve. Split only when the two
            # actually differ, so every unthrottled configuration keeps the
            # single-sum arithmetic — and therefore the solver's descent
            # path — bit for bit.
            if cop_buffer != cop_end:
                deficit = 0.0
                buffer_deficit = 0.0
                for mass, name, cap in stores:
                    if name == "buffer":
                        buffer_deficit += mass * max(0.0, cap - ends[name])
                    else:
                        deficit += mass * max(0.0, cap - ends[name])
                return refill_price * (
                    deficit / max(cop_end, 1e-6)
                    + buffer_deficit / max(cop_buffer, 1e-6)
                )
            deficit = sum(
                mass * max(0.0, cap - ends[name]) for mass, name, cap in stores
            )
            return refill_price * deficit / max(cop_end, 1e-6)

        return cost

    def _zone_setpoints(
        self, power: np.ndarray
    ) -> tuple[list[float], list[float]]:
        """Per-zone setpoints implied by a power schedule.

        Empty in single-zone mode, where there is only one setpoint series.
        """
        if not self.model.params.two_zone_enabled:
            return [], []

        p_min = self.model.params.min_electrical_power
        p_max = self.model.params.max_electrical_power
        span = self.config.max_temp - self.config.min_temp

        upper: list[float] = []
        lower: list[float] = []
        for value in power:
            p_norm = np.clip((value - p_min) / max(p_max - p_min, 0.1), 0, 1)
            upper.append(round(float(self.config.min_temp + p_norm * span), 1))
            lower.append(
                round(float(self.config.min_temp + p_norm * (span + 1.0)), 1)
            )
        return upper, lower

    def _build_result(
        self,
        h: _Horizon,
        *,
        space_power: np.ndarray,
        trajectories: tuple,
        status: str,
        predicted_cost: float,
        baseline_cost: float,
        savings: float,
        deferred_cost: float,
        dhw_power: np.ndarray | None = None,
        dhw_temps: np.ndarray | None = None,
        dhw_cost: float = 0.0,
        buffer_temps: np.ndarray | None = None,
        wood_temps: np.ndarray | None = None,
        predictive_info: dict | None = None,
        objective_value: float = float("nan"),
    ) -> OptimizationResult:
        """Assemble the result both solve paths return.

        Roughly thirty field assignments that were previously written out twice
        and had already begun to diverge — the DHW path was carrying fields the
        space-only path had quietly stopped setting. Anything genuinely
        specific to hot water arrives through the optional arguments.
        """
        import time

        room_temps, slab_temps, upper_temps, lower_temps = trajectories
        total_power = (
            space_power if dhw_power is None else space_power + dhw_power
        )
        # Only the start-time-independent baseline array is wanted here; the
        # previous ``_grid_terms(h.n_steps, h.dt)`` call built offset-0
        # cycling/capacity closures just to discard them, and read as if the
        # published grid figures were folded without the anchor. They are
        # not: ``_grid_report`` below gets ``h.start_time``.
        baseline_load = self.config.baseline_load_array(h.n_steps)
        grid = self._grid_report(total_power, baseline_load, h.dt, h.start_time)
        upper_setpoints, lower_setpoints = self._zone_setpoints(space_power)
        two_zone = self.model.params.two_zone_enabled

        return OptimizationResult(
            power_schedule=space_power.tolist(),
            room_temp_trajectory=room_temps.tolist(),
            slab_temp_trajectory=slab_temps.tolist(),
            buffer_temp_trajectory=(
                [float(v) for v in buffer_temps]
                if buffer_temps is not None
                and mixing_valve.is_throttling(self.model.params.mixing_valve_mode)
                else []
            ),
            valve_target_schedule=(
                [float(v) for v in h.valve_targets]
                if h.valve_targets is not None
                else []
            ),
            wood_temp_trajectory=(
                [float(v) for v in wood_temps]
                if wood_temps is not None
                and self.model.params.two_tank_modelled
                else []
            ),
            objective_value=objective_value,
            timestamps=h.timestamps,
            prices=h.prices.tolist(),
            outdoor_temps=h.outdoor_temps.tolist(),
            predicted_cost=predicted_cost,
            baseline_cost=baseline_cost,
            predicted_savings=savings,
            savings_percentage=_savings_percentage(savings, baseline_cost),
            deferred_energy_cost=deferred_cost,
            optimal_setpoints=self._power_to_setpoints(
                space_power, room_temps[:-1], h.outdoor_temps
            ),
            status=status,
            solve_time_ms=(time.monotonic() - h.t_start) * 1000,
            displace_schedule=self._power_to_displace_schedule(
                space_power, h.outdoor_temps, h.forecast
            ),
            heat_pump_on_schedule=self._power_to_heat_pump_schedule(
                space_power, dhw_power
            ),
            upper_temp_trajectory=upper_temps.tolist(),
            lower_temp_trajectory=lower_temps.tolist(),
            solar_gain_trajectory=[
                self.model.compute_solar_gain(sr) for sr in h.solar_radiation
            ],
            upper_setpoints=upper_setpoints,
            lower_setpoints=lower_setpoints,
            dhw_power_schedule=(
                dhw_power.tolist() if dhw_power is not None else []
            ),
            dhw_temp_trajectory=(
                dhw_temps.tolist() if dhw_temps is not None else []
            ),
            dhw_heating_cost=dhw_cost,
            space_reasons=_mark_manual_reasons(
                classify_space_steps(
                    space_power,
                    h.prices,
                    upper_temps if two_zone else room_temps,
                    h.temp_min_bounds,
                    h.heat_loss_factors,
                    self._pv_surplus,
                    h.n_steps,
                ),
                h.space_pins,
            ),
            dhw_reasons=[],
            price_known=self._price_known_list(h.n_steps),
            projected_peak_kw=grid["peak_kw"],
            peak_cost=grid["peak_cost"],
            compressor_starts=grid["starts"],
            pv_surplus=self._pv_surplus_list(h.n_steps),
            pv_self_consumed_kwh=self._pv_self_consumed(total_power, h.dt),
            predictive_info=predictive_info or {},
        )

    def _co_optimize(
        self,
        h: _Horizon,
        *,
        dhw_plan: dict,
        space_power: np.ndarray,
        dhw_power: np.ndarray,
        status: str,
        best_score: float,
        solve_space,
        p_max: float,
    ) -> tuple[np.ndarray, np.ndarray, str]:
        """Re-plan hot water against the space heating it competes with.

        The first DHW plan is made in ignorance of space heating, so it fills
        the cheapest hours to the compressor ceiling and pushes space heating
        into dearer ones. Now that the space profile is known, that contention
        can be priced and the tank re-planned around it.

        The second plan is adopted **only if it scores better on the same
        objective**, so this pass can never make the plan worse — which is what
        makes a single extra iteration safe rather than something that needs to
        run to convergence.
        """
        try:
            headroom = np.maximum(0.0, p_max - dhw_power)
            # Where space heating sits hard against the ceiling hot water left
            # it, it wanted more power than it could have; its unconstrained
            # demand there is at least the full compressor.
            pinned = (dhw_power > 1e-6) & (space_power >= headroom - 1e-3)
            if not bool(np.any(pinned)):
                return space_power, dhw_power, status

            replanned = self._build_dhw_requirements(
                initial_state=h.initial_state,
                prices=h.prices,
                outdoor_temps=h.outdoor_temps,
                step_hours=h.step_hours,
                n_steps=h.n_steps,
                dt=h.dt,
                p_max=p_max,
                space_demand=np.where(pinned, p_max, space_power),
                dhw_pins=h.dhw_pins,
                p_run_cap=(
                    float(np.min(h.power_caps_extra))
                    if h.power_caps_extra is not None
                    else None
                ),
            )["schedule"]
            if np.allclose(replanned, dhw_power, atol=1e-4):
                return space_power, dhw_power, status

            candidate_space, candidate_status, score = solve_space(
                replanned, space_power
            )
            if score < best_score - 1e-9:
                dhw_plan["schedule"] = replanned
                return candidate_space, replanned, candidate_status
        except Exception as err:  # pragma: no cover - defensive
            _LOGGER.debug("DHW/space co-optimization pass skipped: %s", err)

        return space_power, dhw_power, status

    def _energy_cost_fn(self, prices: np.ndarray, dt: float):
        """Closure pricing a total electrical draw against the grid, exactly.

        Piecewise in each step's PV surplus: energy up to it displaces an
        export and costs the export compensation, everything beyond it is
        imported at the market price. An earlier formulation substituted the
        export price for the *whole* step whenever any surplus existed, so
        0.05 kW of winter sun made 6 kW of grid import look nearly free and
        the plan piled into steps with trivial surplus.

        Inlined rather than delegated to `pv.piecewise_cost` because this
        runs inside the objective, thousands of times per solve.
        """
        surplus = self._pv_surplus
        if surplus is None or not np.any(surplus[: len(prices)] > 1e-6):
            def energy_cost(total_power: np.ndarray) -> float:
                return float(np.sum(prices * total_power) * dt)

            return energy_cost

        surplus = surplus[: len(prices)]
        margin = pv.import_margin(prices, self.config.pv_export_price)

        def energy_cost(total_power: np.ndarray) -> float:
            covered = np.minimum(total_power, surplus)
            return float(
                (np.sum(prices * total_power) - np.sum(margin * covered)) * dt
            )

        return energy_cost

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

    def _window_offset_steps(self, start_time: datetime | None, dt: float) -> int:
        """Steps until the DSO's next metering-window boundary.

        The plan rarely starts on one, and folding windows from step 0 splits
        a burst across two billed windows; see ``metering_windows``.
        """
        if start_time is None:
            return 0
        window = max(1, int(self.config.peak_window_minutes))
        phase = (start_time.hour * 60 + start_time.minute) % window
        if phase == 0:
            return 0
        return max(0, int(round((window - phase) / max(dt * 60.0, 1e-6))))

    def _grid_terms(self, n_steps: int, dt: float, start_time: datetime | None = None):
        """Closures for the cycling and capacity-tariff penalties.

        Both are shared between the space-only and DHW paths. Keeping them in
        one place is not just tidiness: the previous divergence between the two
        objectives meant that simply enabling hot water changed the space
        heating objective, which is a class of bug worth designing out.
        """
        cfg = self.config
        p_max = self.model.params.max_electrical_power
        baseline = cfg.baseline_load_array(n_steps)
        offset_steps = self._window_offset_steps(start_time, dt)
        factors = self._peak_window_factors(n_steps, dt, start_time, offset_steps)

        def cycling(power: np.ndarray) -> float:
            return cycling_penalty(power, cfg.cycling_cost, p_max)

        def capacity(total_power: np.ndarray) -> float:
            return peak_cost(
                total_power,
                baseline,
                cfg.peak_threshold_kw,
                cfg.peak_price_per_kw,
                cfg.peak_window_minutes,
                dt,
                cfg.peak_count,
                offset_steps,
                window_factors=factors,
            )

        return cycling, capacity, baseline

    def _peak_window_factors(
        self,
        n_steps: int,
        dt: float,
        start_time: datetime | None,
        offset_steps: int,
    ) -> np.ndarray | None:
        """Per-window billing factors for the #13 masks, or None unmasked.

        Composed from the same ``CapacityTariff.sample_factor`` the realised
        tracker uses, so the plan's cost term and the live meter can never
        disagree about which hour a window bills under.
        """
        cfg = self.config
        mask = CapacityTariff(
            enabled=True,
            window_minutes=cfg.peak_window_minutes,
            months=frozenset(cfg.peak_months or ()),
            peak_hours=tuple(cfg.peak_hours or ()),
            weekdays_only=bool(cfg.peak_weekdays_only),
            offpeak_factor=float(cfg.peak_offpeak_factor),
        )
        n_windows = metering_windows(
            np.zeros(n_steps), cfg.peak_window_minutes, dt, offset_steps
        ).size
        return window_factors(mask, start_time, n_windows, dt)

    # ------------------------------------------------------------------
    # Predictive weather analysis
    # ------------------------------------------------------------------

    def _analyze_forecast_trajectory(
        self,
        solar_radiation: np.ndarray,
        wind_speeds: np.ndarray,
        precipitation: np.ndarray,
        outdoor_temps: np.ndarray,
        dt_hours: float,
    ) -> dict[str, Any]:
        """Summarise the forecast into a few scalar anticipation signals.

        The real anticipation lives in the trajectory simulation, which
        applies forecast solar gain and wind/rain loss factors step by step;
        these scalars only shape the solver's *initial guess* and give the
        log a one-line summary of what the horizon looks like.
        """
        n = len(solar_radiation)
        if n == 0:
            return {
                "future_solar_energy_kwh": 0.0,
                "solar_peak_indices": [],
                "pre_heat_urgency": 0.5,
                "solar_reduction_factor": 1.0,
                "wind_anticipation_factor": 1.0,
                "rain_anticipation_factor": 1.0,
            }

        # --- Solar analysis ---
        # Compute total solar gain over the horizon
        solar_gains_kw = np.array([
            self.model.compute_solar_gain(sr) for sr in solar_radiation
        ])
        total_solar_energy = float(np.sum(solar_gains_kw) * dt_hours)  # kWh

        # Find peak solar periods (>200 W/m² is significant)
        solar_peak_mask = solar_radiation > 200.0
        solar_peak_indices = np.where(solar_peak_mask)[0].tolist()

        # Solar energy in the FUTURE (next 6-24 hours)
        # Weight more heavily the solar coming in the next 6-12 hours
        n_6h = min(int(6 / dt_hours), n)
        n_12h = min(int(12 / dt_hours), n)
        future_solar_6_12h = float(np.sum(solar_gains_kw[n_6h:n_12h]) * dt_hours)

        # If lots of solar is coming in 6-12h, reduce current heating
        # The slab has enough thermal mass to coast through to solar period
        typical_heat_loss = (
            self.model.params.heat_loss_coefficient
            * (self.config.target_temp - np.mean(outdoor_temps))
        )
        if typical_heat_loss > 0:
            solar_fraction = min(future_solar_6_12h / max(typical_heat_loss * 6, 0.1), 1.0)
        else:
            solar_fraction = 0.0

        # Solar reduction factor: 1.0 = no reduction, 0.5 = reduce heating by 50%
        # Only reduce slab pre-heating, not immediate comfort heating
        solar_reduction = 1.0 - 0.4 * solar_fraction  # max 40% reduction

        # --- Wind analysis ---
        # Look at future wind speeds and compute anticipated heat loss increase
        wind_weights = np.exp(-np.arange(n) * dt_hours / 12.0)  # decay over 12h
        wind_weights /= wind_weights.sum()
        avg_future_wind = float(np.sum(wind_speeds * wind_weights))
        wind_anticipation = 1.0 + self.model.params.wind_sensitivity * avg_future_wind

        # --- Rain analysis ---
        # Upcoming rain increases heat loss
        rain_weights = np.exp(-np.arange(n) * dt_hours / 12.0)
        rain_weights /= rain_weights.sum()
        avg_future_precip = float(np.sum(precipitation * rain_weights))
        rain_anticipation = 1.0
        if avg_future_precip > 0.1:
            rain_intensity = min(avg_future_precip / 2.0, 1.0)
            rain_anticipation = 1.0 + (
                self.model.params.rain_heat_loss_multiplier - 1.0
            ) * rain_intensity

        # --- Pre-heat urgency ---
        # High if bad weather (wind + rain) is coming AND cheap electricity now
        # Low if sunny weather is coming (solar will help)
        pre_heat_urgency = min(1.0, max(0.0,
            (wind_anticipation - 1.0) * 3.0 +
            (rain_anticipation - 1.0) * 5.0 -
            (1.0 - solar_reduction) * 2.0
        ))

        return {
            "future_solar_energy_kwh": total_solar_energy,
            "solar_peak_indices": solar_peak_indices,
            "pre_heat_urgency": pre_heat_urgency,
            "solar_reduction_factor": solar_reduction,
            "wind_anticipation_factor": wind_anticipation,
            "rain_anticipation_factor": rain_anticipation,
            "avg_future_wind_ms": avg_future_wind,
            "avg_future_precip_mmh": avg_future_precip,
            "future_solar_6_12h_kwh": future_solar_6_12h,
        }

    # ------------------------------------------------------------------
    # Main optimization
    # ------------------------------------------------------------------

    def optimize(
        self,
        initial_state: ThermalState,
        prices: np.ndarray,
        outdoor_temps: np.ndarray,
        wind_speeds: np.ndarray | None = None,
        precipitation: np.ndarray | None = None,
        solar_radiation: np.ndarray | None = None,
        start_time: datetime | None = None,
        price_known: np.ndarray | None = None,
        pv_surplus: np.ndarray | None = None,
        space_pins: np.ndarray | None = None,
        dhw_pins: np.ndarray | None = None,
        external_heat_kw: np.ndarray | None = None,
        price_sigma: np.ndarray | None = None,
        power_caps_extra: np.ndarray | None = None,
        humidity: np.ndarray | None = None,
        # Keyword-only: both are per-step temperature series, the same shape
        # and dtype as half the arrays above — a positional transposition
        # would be silent and plausible-looking.
        *,
        min_temp_margins: np.ndarray | None = None,
        min_temp_floors: np.ndarray | None = None,
    ) -> OptimizationResult:
        """Run the MPC optimization with predictive weather anticipation.

        This is the CORE of true MPC: the optimizer uses the FULL 24-hour
        forecast trajectory (solar, wind, rain, temperature) to make decisions
        about CURRENT actions. It doesn't just react to current conditions.

        Key anticipatory behaviors:
        - Reduces pre-heating before forecasted sunny periods
        - Increases pre-heating before forecasted windy/rainy periods
        - Coordinates DHW heating with space heating and electricity prices

        ``prices`` are the raw import prices. Where ``pv_surplus`` forecasts
        spare production, the objectives price consumption piecewise — the
        surplus-covered energy at ``config.pv_export_price``, the rest at the
        import price — so a step with trivial sun is not repriced wholesale.
        ``price_known`` marks which steps rest on published market data rather
        than on the learned diurnal prior.
        """
        import time

        t_start = time.monotonic()

        n_steps = min(len(prices), len(outdoor_temps), self.config.n_steps)
        dt = self.config.dt_hours

        if wind_speeds is None:
            wind_speeds = np.zeros(n_steps)
        if precipitation is None:
            precipitation = np.zeros(n_steps)
        if solar_radiation is None:
            solar_radiation = np.zeros(n_steps)
        if price_known is None:
            price_known = np.ones(n_steps, dtype=bool)
        if pv_surplus is None:
            pv_surplus = np.zeros(n_steps)

        if start_time is None:
            start_time = datetime.now()

        # Truncate arrays to n_steps
        prices = prices[:n_steps]
        outdoor_temps = outdoor_temps[:n_steps]
        wind_speeds = wind_speeds[:n_steps]
        precipitation = precipitation[:n_steps]
        solar_radiation = solar_radiation[:n_steps]
        price_known = np.asarray(price_known, dtype=bool)[:n_steps]
        pv_surplus = np.asarray(pv_surplus, dtype=float)[:n_steps]
        if price_known.size < n_steps:
            price_known = np.concatenate(
                [price_known, np.zeros(n_steps - price_known.size, dtype=bool)]
            )
        if pv_surplus.size < n_steps:
            pv_surplus = np.concatenate(
                [pv_surplus, np.zeros(n_steps - pv_surplus.size)]
            )

        self._price_known = price_known
        self._initial_buffer_temp = (
            float(initial_state.buffer_tank_temperature)
            if self.model.params.buffer_is_store
            and initial_state.buffer_tank_temperature is not None
            else None
        )
        self._pv_surplus = pv_surplus

        # Risk-adjusted pricing on the unpublished horizon (#34). The prior
        # fills unknown steps with its mean, so the optimizer treats a
        # guessed trough as bankable; the error is asymmetric — a trough
        # that fails to appear forces buying at a peak, while charging
        # slightly early costs only standby loss. Deferral into guessed
        # steps therefore pays λ·sigma on top of the mean; known steps carry
        # sigma 0 by construction and λ defaults to 0, which skips this
        # entirely and leaves the array untouched.
        if price_sigma is not None and self.config.price_risk_lambda > 0.0:
            sig = np.clip(np.asarray(price_sigma, dtype=float), 0.0, None)
            if sig.size < n_steps:
                sig = np.concatenate([sig, np.zeros(n_steps - sig.size)])
            risk = self.config.price_risk_lambda * sig[:n_steps]
            risk = np.where(price_known, 0.0, risk)
            if np.any(risk > 0.0):
                prices = np.asarray(prices, dtype=float) + risk

        # Forecast humidity (#21), normalised to horizon length; short
        # series pad with NaN, which the model reads as "unknown, use the
        # ambient value" — never as 0 % humidity. An all-NaN series is the
        # same as none at all, and dropping it keeps the objective's inner
        # loop free of per-step lookups that can only fall back.
        if humidity is not None:
            hum = np.asarray(humidity, dtype=float)
            if hum.size < n_steps:
                hum = np.concatenate(
                    [hum, np.full(n_steps - hum.size, np.nan)]
                )
            humidity = hum[:n_steps]
            if not np.any(np.isfinite(humidity)):
                humidity = None

        # Free-heat forecast, normalised to horizon length like the arrays
        # above. All-zero is the same as none at all, and is treated so.
        if external_heat_kw is not None:
            ext = np.clip(np.asarray(external_heat_kw, dtype=float), 0.0, None)
            if ext.size < n_steps:
                ext = np.concatenate([ext, np.zeros(n_steps - ext.size)])
            external_heat_kw = ext[:n_steps]
            if not np.any(external_heat_kw > 0.0):
                external_heat_kw = None

        # --- Analyze forecast trajectory for predictive signals ---
        forecast_analysis = self._analyze_forecast_trajectory(
            solar_radiation, wind_speeds, precipitation, outdoor_temps, dt
        )

        _LOGGER.debug(
            "Predictive analysis: solar_reduction=%.2f, wind_factor=%.2f, "
            "rain_factor=%.2f, pre_heat_urgency=%.2f, future_solar=%.1f kWh",
            forecast_analysis["solar_reduction_factor"],
            forecast_analysis["wind_anticipation_factor"],
            forecast_analysis["rain_anticipation_factor"],
            forecast_analysis["pre_heat_urgency"],
            forecast_analysis["future_solar_energy_kwh"],
        )

        dhw_enabled = self.model.params.dhw_enabled

        # Hour of day at each step. Computed once: the comfort target, both
        # temperature bounds and the DHW draw pattern all key off it, and it
        # was previously rebuilt from scratch for each of the four.
        step_hours = np.array([
            (
                (start_time + timedelta(hours=i * dt)).hour
                + (start_time + timedelta(hours=i * dt)).minute / 60.0
            )
            for i in range(n_steps)
        ])

        comfort_targets = np.array(
            [self.config.get_comfort_temp(hour) for hour in step_hours]
        )
        bounds = [self.config.get_temp_bounds(hour) for hour in step_hours]
        temp_min_bounds = np.array([low for low, _ in bounds])
        temp_max_bounds = np.array([high for _, high in bounds])

        # T5 (#16 #54): the comfort floor's two adjustments, both optional
        # and both applied HERE — the single site where the bounds are
        # built — so every consumer (objectives, safety releases, pin
        # repair) sees the same effective floor. ``min_temp_margins`` is a
        # per-step raise (the model's own expected error at that lead);
        # ``min_temp_floors`` an absolute per-step floor (the mold guard).
        # None for both is byte-for-byte the previous bounds.
        if min_temp_margins is not None or min_temp_floors is not None:
            if min_temp_margins is not None:
                m = np.clip(np.asarray(min_temp_margins, dtype=float), 0.0, None)
                if m.size < n_steps:
                    m = np.concatenate([m, np.zeros(n_steps - m.size)])
                temp_min_bounds = temp_min_bounds + m[:n_steps]
            if min_temp_floors is not None:
                f = np.asarray(min_temp_floors, dtype=float)
                if f.size < n_steps:
                    f = np.concatenate(
                        [f, np.full(n_steps - f.size, -np.inf)]
                    )
                temp_min_bounds = np.maximum(temp_min_bounds, f[:n_steps])
            # Whatever raised the floor, the band never squeezes shut: a
            # floor at or above the ceiling makes the solve infeasible and
            # the comfort penalty unbounded.
            temp_min_bounds = np.minimum(
                temp_min_bounds, temp_max_bounds - 0.5
            )

        # Per-step solar gain, and the wind/rain multiplier on heat loss. Both
        # use the *forecast* at each future step rather than current
        # conditions, which is what makes the control anticipatory.
        solar_gains_per_step = np.array([
            self.model.compute_solar_gain(sr) for sr in solar_radiation
        ])
        base_loss = max(self.model.params.heat_loss_coefficient, 0.001)
        forecast_heat_loss_factors = np.array([
            self.model.effective_heat_loss_coefficient(
                self.model.params.heat_loss_coefficient,
                wind_speeds[i],
                precipitation[i],
            )
            / base_loss
            for i in range(n_steps)
        ])

        # --- Manual plan pins ------------------------------------------
        # Normalise both channels to writable float arrays of horizon length so
        # the safety-release loop below can relax individual steps in place. A
        # channel left ``None`` stays fully automatic and costs nothing.
        space_pins = self._normalise_pins(space_pins, n_steps)
        dhw_pins = self._normalise_pins(dhw_pins, n_steps)
        self._dhw_requirement = None
        self._dhw_legionella_step = None
        released_space: set[int] = set()
        released_dhw: set[int] = set()

        # Per-step ceiling on space power, lowered by the buffer-cap loop
        # below (valve installs) and by external per-step caps (T2's fuse
        # guard and shadow solves). It exists only when a valve can charge
        # the tank OR extra caps were supplied, so every no-valve, no-cap
        # install stays byte-for-byte identical.
        throttling = mixing_valve.is_throttling(
            self.model.params.mixing_valve_mode
        )
        power_caps: np.ndarray | None = None
        caps_extra_arr: np.ndarray | None = None
        if throttling or power_caps_extra is not None:
            power_caps = np.full(
                n_steps, self.model.params.max_electrical_power
            )
        if power_caps_extra is not None:
            extra = np.clip(
                np.asarray(power_caps_extra, dtype=float), 0.0, None
            )
            if extra.size < n_steps:
                extra = np.concatenate(
                    [
                        extra,
                        np.full(
                            n_steps - extra.size,
                            self.model.params.max_electrical_power,
                        ),
                    ]
                )
            caps_extra_arr = extra[:n_steps]
            power_caps = np.minimum(power_caps, caps_extra_arr)

        # Per-step valve target schedule, set by the hold-candidate pass below
        # and read by every solve and re-simulation through the closure.
        valve_targets: np.ndarray | None = None

        # Solve, then check the solved trajectory against the hard safety lines,
        # release any forced-off pin that would breach one, and solve again.
        # The comfort and tank floors are *soft* penalties in the objective, so
        # clamping a step off does not actually protect the house or tank — only
        # re-solving with the offending pin freed does.
        def _solve() -> OptimizationResult:
            horizon = _Horizon(
                initial_state=initial_state,
                prices=prices,
                outdoor_temps=outdoor_temps,
                wind_speeds=wind_speeds,
                precipitation=precipitation,
                solar_radiation=solar_radiation,
                start_time=start_time,
                n_steps=n_steps,
                dt=dt,
                comfort_targets=comfort_targets,
                temp_min_bounds=temp_min_bounds,
                temp_max_bounds=temp_max_bounds,
                step_hours=step_hours,
                solar_gains=solar_gains_per_step,
                heat_loss_factors=forecast_heat_loss_factors,
                forecast=forecast_analysis,
                t_start=t_start,
                space_pins=space_pins,
                dhw_pins=dhw_pins,
                power_caps=power_caps,
                power_caps_extra=caps_extra_arr,
                external_heat_kw=external_heat_kw,
                valve_targets=valve_targets,
                humidity=humidity,
            )
            if dhw_enabled:
                return self._optimize_with_dhw(horizon)
            return self._optimize_space_only(horizon)

        result = _solve()

        if space_pins is not None or dhw_pins is not None:
            # Every release must be followed by a re-solve: releasing a pin and
            # then returning the plan that was built *with* it would hand back a
            # schedule already known to be unsafe, while reporting the step as
            # released. Bounded so a physically infeasible plan cannot spin.
            for _ in range(_SAFETY_REPAIR_ROUNDS):
                rel_s, rel_d = self._safety_release_steps(
                    result, temp_min_bounds, space_pins, dhw_pins
                )
                if not rel_s and not rel_d:
                    break
                for i in rel_s:
                    space_pins[i] = float("nan")
                    released_space.add(i)
                for i in rel_d:
                    dhw_pins[i] = float("nan")
                    released_dhw.add(i)
                result = _solve()
            else:
                # Out of repair rounds. If anything is still breaching, abandon
                # the forced-off pins wholesale rather than return a plan that
                # leaves the house or the tank below its limit: the user asked
                # for timing, not for the heating to be unsafe.
                rel_s, rel_d = self._safety_release_steps(
                    result, temp_min_bounds, space_pins, dhw_pins
                )
                if rel_s or rel_d:
                    # Only the channel that is actually breaching is abandoned.
                    # Discarding the other one as well would throw away an
                    # arrangement that was never unsafe -- letting the pump heat
                    # in exactly the expensive hours the user excluded -- and
                    # then report those slots as released for safety, which
                    # would not be true.
                    for name, pins, released, breaching in (
                        ("space", space_pins, released_space, bool(rel_s)),
                        ("hot water", dhw_pins, released_dhw, bool(rel_d)),
                    ):
                        if pins is None or not breaching:
                            continue
                        for i in range(len(pins)):
                            value = float(pins[i])
                            if not _pin_is_free(value) and value < 0.5:
                                pins[i] = float("nan")
                                released.add(i)
                        _LOGGER.warning(
                            "Manual %s plan could not be made safe in %d "
                            "rounds; releasing every forced-off slot on that "
                            "channel and planning it freely",
                            name,
                            _SAFETY_REPAIR_ROUNDS,
                        )
                    result = _solve()

        # --- The hold candidate: can a commanded valve wait for the peak? ---
        #
        # A fixed-curve valve starts feeding the house the moment the tank is
        # warmer than the curve, so storage mostly shifts the hours right
        # after charging (measured in v3.10.0 at roughly a fifth of the
        # analytical value). A valve the optimizer can *command* does not have
        # to: lower the curve to the comfort floor between charging and the
        # price peak and the tank holds its heat for when it is worth most.
        #
        # The schedule is a derived candidate, not a rule: it is guessed from
        # the structure of the solved plan, re-solved in full, and adopted
        # only if it beats the fixed target on the same objective -- exactly
        # `_co_optimize`'s discipline, and what makes a heuristic safe here.
        # At flat prices no candidate is even proposed, which is the null
        # control. Gated on smart_write (no other mode can actuate it), on
        # the tank being a real store, and away from manual pins -- the
        # pin-safety loop above has already finished, and a hand-pinned day
        # is not the day to get clever with the valve.
        if (
            self.model.params.mixing_valve_mode == mixing_valve.MODE_SMART_WRITE
            and self.model.params.buffer_is_store
            and space_pins is None
            and dhw_pins is None
            and np.isfinite(result.objective_value)
        ):
            schedule = self._derive_hold_schedule(
                np.asarray(result.power_schedule), prices, temp_min_bounds
            )
            if schedule is not None:
                fixed_objective = result.objective_value
                valve_targets = schedule
                candidate = _solve()
                if (
                    np.isfinite(candidate.objective_value)
                    and candidate.objective_value < fixed_objective - 1e-9
                ):
                    result = candidate
                    _LOGGER.debug(
                        "Valve hold schedule adopted: objective %.3f -> %.3f",
                        fixed_objective,
                        candidate.objective_value,
                    )
                else:
                    valve_targets = None

        if power_caps is not None and throttling:
            # The tank's safe ceiling as a hard constraint. The model's clamp
            # already stops the simulated temperature exceeding the cap, but it
            # does so by *deleting* the excess heat -- so a plan that charges a
            # full tank is merely wasteful in the objective while boiling the
            # tank on the real system, and at a low enough price the solver is
            # indifferent to the waste. A soft penalty is explicitly ruled out
            # by item 29 (the solver would plan to boil the tank at a small
            # modelled cost); instead, mirror the pin-safety loop above with
            # the opposite polarity: find the steps whose heat the cap
            # refused, lower their power ceiling to what the tank could
            # actually accept, and re-solve. Bounded like the release loop, and
            # for the same reason.
            for _ in range(_SAFETY_REPAIR_ROUNDS):
                if not self._tighten_buffer_caps(
                    result, power_caps, initial_state, outdoor_temps,
                    wind_speeds, precipitation, solar_radiation, dt,
                    external_heat_kw=external_heat_kw,
                    valve_targets=valve_targets,
                    humidity=humidity,
                    start_hour=float(step_hours[0]),
                ):
                    break
                result = _solve()

        result.manual_pins_active = space_pins is not None or dhw_pins is not None
        result.manual_released_space = sorted(released_space)
        result.manual_released_dhw = sorted(released_dhw)

        existing_info = result.predictive_info if result.predictive_info else {}
        result.predictive_info = {**forecast_analysis, **existing_info}

        if power_caps_extra is not None:
            # An externally capped plan must say when the cap made the floor
            # unreachable — a fuse guard that silently plans a cold house is
            # the program's worst failure mode. Zero when the cap is
            # feasible; the worst floor shortfall in °C when it is not.
            trajectory = np.asarray(
                result.upper_temp_trajectory
                if self.model.params.two_zone_enabled
                and result.upper_temp_trajectory
                else result.room_temp_trajectory,
                dtype=float,
            )
            # Trajectories carry n+1 entries with index 0 the *initial*
            # state — the same convention the objectives use (`room_t[1:]`
            # vs bounds). Judging the starting temperature against the cap
            # would blame the fuse for the weather; dropping the last step
            # would miss a breach at the horizon's edge.
            planned = trajectory[1:] if trajectory.size > n_steps else trajectory
            steps = min(planned.size, temp_min_bounds.size)
            breach = 0.0
            if steps > 0:
                breach = float(
                    np.max(
                        np.clip(
                            temp_min_bounds[:steps] - planned[:steps],
                            0.0,
                            None,
                        )
                    )
                )
            result.predictive_info["power_cap_breach_c"] = round(breach, 3)
        return result

    @staticmethod
    def _normalise_pins(
        pins: np.ndarray | None, n_steps: int
    ) -> np.ndarray | None:
        """Copy pins to a float array of horizon length, or pass ``None`` on.

        A copy because the safety-release loop frees individual steps in place
        and must not mutate the caller's array; padded or truncated to the
        horizon so a stale-length override cannot misalign the schedule.
        """
        if pins is None:
            return None
        arr = np.full(n_steps, float("nan"), dtype=float)
        src = np.asarray(pins, dtype=float)
        take = min(n_steps, src.size)
        arr[:take] = src[:take]
        return arr

    def _derive_hold_schedule(
        self,
        power: np.ndarray,
        prices: np.ndarray,
        temp_min_bounds: np.ndarray,
    ) -> np.ndarray | None:
        """A candidate valve-target schedule: hold between charging and peak.

        Fully resolved -- every entry a real temperature. Default steps carry
        the working target (the configured static target, else the comfort
        ceiling); hold steps carry the per-step comfort floor, which is the
        lowest target the solve is allowed to plan for anyway, so a hold can
        never ask for a house the objective would not accept.

        Hold steps are the ones after charging has begun and before the last
        expensive block ends, that are neither charging nor expensive
        themselves: the stretch where a fixed-curve valve bleeds the tank into
        the house at mid prices. ``None`` -- no candidate at all -- when there
        is nothing to arbitrage: no charging, no expensive block, or a price
        spread too flat to name one. That refusal is the null control; the
        caller adopts a candidate only if it beats the fixed target on the
        same objective, so this function only has to be plausible, not right.
        """
        n = len(power)
        if n == 0 or len(prices) != n:
            return None
        # p85 rather than p75 for the peak. A real day is often a long flat
        # plateau with a short tall spike -- sixteen expensive steps in
        # ninety-six -- and at p75 the threshold lands *on* the plateau: the
        # whole day reads as expensive, the spread test then sees p75 == p25
        # and refuses a schedule on exactly the profile that most wants one.
        p25, p40, p85 = np.percentile(prices, [25, 40, 85])
        # Flat prices: nothing to arbitrage, so no candidate. The margin is
        # deliberately generous -- a 5 % spread cannot pay for a hold.
        if p85 <= p25 * 1.05:
            return None
        p_max = self.model.params.max_electrical_power
        expensive = prices >= p85
        charging = (power > 0.5 * p_max) & (prices <= p40)
        if not bool(expensive.any()) or not bool(charging.any()):
            return None

        after_charge = np.zeros(n, dtype=bool)
        seen = False
        for i in range(n):
            seen = seen or bool(charging[i])
            after_charge[i] = seen
        before_peak = np.zeros(n, dtype=bool)
        seen = False
        for i in reversed(range(n)):
            seen = seen or bool(expensive[i])
            before_peak[i] = seen

        hold = after_charge & before_peak & ~charging & ~expensive
        if not bool(hold.any()):
            return None

        params = self.model.params
        default_target = params.mixing_valve_target or params.comfort_ceiling
        targets = np.full(n, float(default_target))
        floors = np.asarray(temp_min_bounds, dtype=float)
        targets[hold] = floors[hold]
        return targets

    def _tighten_buffer_caps(
        self,
        result: OptimizationResult,
        power_caps: np.ndarray,
        initial_state: ThermalState,
        outdoor_temps: np.ndarray,
        wind_speeds: np.ndarray,
        precipitation: np.ndarray,
        solar_radiation: np.ndarray,
        dt: float,
        external_heat_kw: np.ndarray | None = None,
        valve_targets: np.ndarray | None = None,
        humidity: np.ndarray | None = None,
        start_hour: float | None = None,
    ) -> bool:
        """Lower per-step power ceilings where the plan charged a full tank.

        Re-simulates the returned space schedule and reads the heat the
        buffer cap refused at each step. A refusing step gets its ceiling cut
        to the power whose heat the tank could actually take, converted at
        that step's own COP (the flow temperature is the cap itself, since
        that is where the tank sits when it refuses). Mutates ``power_caps``
        in place, exactly as the pin-release loop mutates the pins, and
        returns whether anything changed so the caller knows to re-solve.
        """
        schedule = np.asarray(result.power_schedule, dtype=float)
        self.model.simulate_trajectory(
            initial_state=initial_state,
            power_schedule=schedule,
            outdoor_temps=outdoor_temps,
            wind_speeds=wind_speeds,
            precipitation=precipitation,
            solar_radiation=solar_radiation,
            dt_hours=dt,
            external_heat_kw=external_heat_kw,
            valve_targets=valve_targets,
            humidity=humidity,
            # The refusal check must simulate the same physics the
            # objective did — with #53's profile active, flat internal
            # gains would judge the caps on a trajectory the solve does
            # not believe.
            start_hour=start_hour,
        )
        refused = self.model.last_buffer_refused
        if refused is None:
            return False
        changed = False
        for i in np.nonzero(refused > 1e-9)[0]:
            # The shared marginal-COP helper (v4.0.5): this loop was the one
            # optimizer site already converting at the dynamics' flow-derated
            # convention, and the terminal/deferred valuations now draw from
            # the same code path so the three cannot drift apart again.
            cop_i = self.model.marginal_cop(
                float(outdoor_temps[i]),
                "buffer",
                store_temp=self.model.params.buffer_max_temp,
            )
            allowed = float(schedule[i]) - float(refused[i]) / max(cop_i, 1e-6)
            # Slightly under, or float noise re-trips the same step and burns
            # a repair round confirming it.
            new_cap = max(0.0, allowed) * 0.999
            if new_cap < float(power_caps[i]) - 1e-9:
                power_caps[i] = new_cap
                changed = True
        if changed:
            _LOGGER.debug(
                "Buffer cap tightened %d step(s); re-solving",
                int(np.count_nonzero(refused > 1e-9)),
            )
        return changed

    def _safety_release_steps(
        self,
        result: OptimizationResult,
        temp_min_bounds: np.ndarray,
        space_pins: np.ndarray | None,
        dhw_pins: np.ndarray | None,
    ) -> tuple[list[int], list[int]]:
        """Which forced-off steps must be released so safety is not breached.

        Reads the solved trajectories against the same hard lines the plan
        classifiers use — the comfort floor for space heating, and the DHW
        requirement (which already folds in the usable minimum, the idle floor
        and any due legionella cycle) for hot water.

        Every step is checked, not just the forced-off ones: an off-block's
        deficit surfaces *later*, at free steps — typically in the demand
        window just after the override expires — and checking only the pinned
        steps let exactly those breaches through with nothing releasing
        anything. A breach is attributed to the nearest preceding forced-off
        step, and the whole contiguous off-block it belongs to is released,
        because a tank or slab that is already cold needs the run-up freed,
        not just the final step. A breach with no forced-off step before it
        has nothing to release and is left to the ordinary penalties — that is
        genuine infeasibility, not the pins' doing.
        """

        def _preceding_off(pins: np.ndarray, i: int) -> int | None:
            j = i
            while j >= 0:
                pin = float(pins[j]) if j < len(pins) else float("nan")
                if not _pin_is_free(pin) and pin < 0.5:
                    return j
                j -= 1
            return None

        release_space: list[int] = []
        if space_pins is not None:
            two_zone = self.model.params.two_zone_enabled
            room = (
                result.upper_temp_trajectory
                if two_zone and result.upper_temp_trajectory
                else result.room_temp_trajectory
            )
            for i in range(len(result.power_schedule)):
                temp = room[i + 1] if i + 1 < len(room) else room[-1]
                floor = (
                    temp_min_bounds[i]
                    if i < len(temp_min_bounds)
                    else temp_min_bounds[-1]
                )
                pin = float(space_pins[i]) if i < len(space_pins) else float("nan")
                pinned_off = not _pin_is_free(pin) and pin < 0.5
                # At a forced-off step, sitting *at* the floor already means
                # the pin is what is holding the house there. At a free step
                # the solver legitimately rides the floor, so only a clear
                # violation beyond its tolerance counts.
                if pinned_off:
                    breach = temp <= floor + 0.15
                else:
                    breach = temp < floor - 0.25
                if not breach:
                    continue
                j = _preceding_off(space_pins, i)
                if j is not None:
                    release_space.append(j)

        release_dhw: list[int] = []
        if dhw_pins is not None and self._dhw_requirement is not None:
            traj = result.dhw_temp_trajectory
            req = self._dhw_requirement
            for i in range(min(len(result.dhw_power_schedule), len(req))):
                temp = traj[i + 1] if traj and i + 1 < len(traj) else 0.0
                if temp >= float(req[i]) - 0.5:
                    continue
                j = _preceding_off(dhw_pins, i)
                if j is not None:
                    release_dhw.append(j)

        return (
            self._expand_off_blocks(space_pins, release_space),
            self._expand_off_blocks(dhw_pins, release_dhw),
        )

    @staticmethod
    def _expand_off_blocks(
        pins: np.ndarray | None, breaches: list[int]
    ) -> list[int]:
        """Grow each breach back over its contiguous forced-off run."""
        if pins is None or not breaches:
            return []
        out: set[int] = set()
        for i in breaches:
            j = i
            while j >= 0 and not _pin_is_free(float(pins[j])) and float(pins[j]) < 0.5:
                out.add(j)
                j -= 1
        return sorted(out)

    def _pin_on_power(self, upper: float) -> float:
        """Lower bound for a forced-on step: the pump's minimum running power.

        Kept a touch above the classifier's idle threshold so a pinned-on step
        is unambiguously "running", but never above the capacity actually
        available, which the bounds helper clamps to.
        """
        floor = max(float(self.model.params.min_electrical_power), 0.1)
        return min(floor, upper)

    @staticmethod
    def _seed_pinned_guess(
        guess: np.ndarray, bounds: list[tuple[float, float]]
    ) -> np.ndarray:
        """Clamp a starting guess inside the (possibly pinned) bounds."""
        out = np.array(guess, dtype=float)
        for i in range(min(len(out), len(bounds))):
            low, high = bounds[i]
            out[i] = min(max(out[i], low), high)
        return out

    def _optimize_space_only(self, h: _Horizon) -> OptimizationResult:
        """Optimize space heating only (no DHW)."""
        import time

        # Unpacked rather than accessed through ``h`` throughout: the body is
        # dense numpy, and ``h.prices * h.dt`` forty times over reads far worse
        # than the equations it is meant to express.
        initial_state, prices, dt, n_steps = (
            h.initial_state, h.prices, h.dt, h.n_steps
        )
        outdoor_temps, wind_speeds = h.outdoor_temps, h.wind_speeds
        precipitation, solar_radiation = h.precipitation, h.solar_radiation
        comfort_targets = h.comfort_targets
        temp_min_bounds, temp_max_bounds = h.temp_min_bounds, h.temp_max_bounds
        solar_gains_per_step = h.solar_gains
        forecast_heat_loss_factors = h.heat_loss_factors
        forecast_analysis, t_start = h.forecast, h.t_start

        p_min = self.model.params.min_electrical_power
        p_max = self.model.params.max_electrical_power

        anticipatory_weights = self._anticipatory_weights(
            n_steps, dt, solar_gains_per_step, forecast_heat_loss_factors
        )
        # How far the user is willing to let the house drift below target. The
        # pull-to-target term is normalised by this, so widening the allowed
        # band actually buys cheaper operation instead of being overwhelmed by
        # a fixed quadratic penalty.
        comfort_band = np.maximum(comfort_targets - temp_min_bounds, 1.0)
        terminal_cost = self._terminal_cost(prices, outdoor_temps)
        cycling, capacity, baseline_load = self._grid_terms(
            n_steps, dt, h.start_time
        )
        energy_cost_of = self._energy_cost_fn(prices, dt)

        def objective(power_schedule: np.ndarray) -> float:
            """Compute the total cost with predictive weather anticipation."""
            room_temps, slab_temps, upper_temps, lower_temps = (
                self.model.simulate_trajectory(
                    initial_state=initial_state,
                    power_schedule=power_schedule,
                    outdoor_temps=outdoor_temps,
                    wind_speeds=wind_speeds,
                    precipitation=precipitation,
                    solar_radiation=solar_radiation,
                    dt_hours=dt,
                    external_heat_kw=h.external_heat_kw,
                    valve_targets=h.valve_targets,
                    humidity=h.humidity,
                    start_hour=float(h.step_hours[0]),
                )
            )

            # Electricity cost, piecewise in PV surplus
            energy_cost = energy_cost_of(power_schedule) * self.config.price_weight

            penalty, comfort_cost = self._comfort_terms(
                room_temps, upper_temps, lower_temps,
                comfort_targets, temp_min_bounds, temp_max_bounds, comfort_band,
            )


            # --- Weather anticipation is the simulation's job ----------------
            # ``simulate_trajectory`` already applies the solar gain and the
            # wind/rain heat loss factors to the real physics, so the predicted
            # trajectory itself tells the optimizer that heating just before a
            # sunny spell is wasted and that coasting into a windy evening is
            # expensive. Two extra objective terms used to re-state the same
            # thing in invented currency: a penalty for heating before sun, and
            # a *negative* cost that paid the plan to burn electricity before
            # bad weather. Both double-counted, and the second existed only on
            # this path and not on the DHW one, so simply enabling hot water
            # changed the space heating objective. Removing them made the
            # shoulder season 4-6% cheaper at identical comfort.

            return (
                energy_cost + penalty + comfort_cost
                # Currency terms scale with price_weight as the energy cost
                # does, or a non-default weight silently re-prices starts and
                # peaks relative to the electricity they trade against.
                + (cycling(power_schedule) + capacity(power_schedule))
                * self.config.price_weight
                + terminal_cost(
                    room_temps,
                    slab_temps,
                    upper_temps,
                    lower_temps,
                    # Recorded by the call above rather than returned, because
                    # nine call sites unpack a four-tuple.
                    self.model.last_buffer_trajectory,
                )
            )

        # Initial guess: smart initialization considering forecasts
        initial_power = p_max * _price_guess_weights(prices)

        # Apply predictive adjustments to initial guess
        for i in range(n_steps):
            # Reduce power before solar periods
            initial_power[i] *= anticipatory_weights[i]

        initial_power = np.clip(initial_power, p_min, p_max)
        # A heat pump can be off. min_electrical_power is the lowest it can
        # modulate to while running, not a floor it must burn every step, so
        # allow 0 and read sub-minimum values as duty cycling within the step.
        if h.power_caps is not None:
            bounds = [
                (0.0, float(min(p_max, h.power_caps[i]))) for i in range(n_steps)
            ]
        else:
            bounds = [(0.0, p_max)] * n_steps
        # A manual plan pins individual steps on or off. Forcing on raises the
        # lower bound to the pump's minimum running power so the step must run
        # without fixing how hard; the initial guess is nudged into the pinned
        # band so the solver starts feasible.
        bounds = _apply_pins_to_bounds(bounds, h.space_pins, self._pin_on_power(p_max))
        initial_power = self._seed_pinned_guess(initial_power, bounds)

        # Multiple starting points: the smooth price-weighted guess above, a
        # bang-bang schedule that buys the cheapest steps first, and a flat
        # schedule. See _multi_start_minimize for why one guess is not enough.
        # Computed once and reused below for the savings reference; the same
        # simulation also makes a good solver start.
        baseline_power, baseline_end = self._compute_baseline_power(
            initial_state, outdoor_temps, wind_speeds, precipitation,
            solar_radiation, dt, comfort_targets,
            external_heat_kw=h.external_heat_kw,
        )
        baseline_energy = float(np.sum(baseline_power) * dt)
        starts = [
            initial_power,
            _price_ranked_start(prices, baseline_energy, p_max, dt),
            np.clip(baseline_power, 0.0, p_max),
        ]

        try:
            result = _multi_start_minimize(
                objective, starts, bounds, maxiter=200
            )
            optimal_power = result.x
            status = _solver_status(result, objective, initial_power)
        except Exception as e:
            _LOGGER.error("Optimization failed: %s", e)
            optimal_power = initial_power
            status = f"failed ({e})"

        # Simulate with optimal schedule
        room_temps, slab_temps, upper_temps, lower_temps = (
            self.model.simulate_trajectory(
                initial_state=initial_state,
                power_schedule=optimal_power,
                outdoor_temps=outdoor_temps,
                wind_speeds=wind_speeds,
                precipitation=precipitation,
                solar_radiation=solar_radiation,
                dt_hours=dt,
                external_heat_kw=h.external_heat_kw,
                valve_targets=h.valve_targets,
                humidity=h.humidity,
                start_hour=float(h.step_hours[0]),
            )
        )
        # Captured here, next to the call that wrote it, rather than read back
        # at assembly time -- by then further simulations have run.
        buffer_temps = self.model.last_buffer_trajectory
        wood_temps = self.model.last_wood_trajectory
        # The achieved objective, for candidate comparison across valve
        # schedules. One extra evaluation, robust on the failure path too.
        achieved_objective = float(objective(optimal_power))

        baseline_cost = energy_cost_of(baseline_power)
        predicted_cost = energy_cost_of(optimal_power)

        optimized_end = self._replay_end_state(
            initial_state, optimal_power, outdoor_temps, wind_speeds,
            precipitation, solar_radiation, dt,
            external_heat_kw=h.external_heat_kw,
            valve_targets=h.valve_targets,
        )
        deferred_cost = self._deferred_energy_cost(
            baseline_end, optimized_end, prices, outdoor_temps,
            caps=self._settlement_caps(outdoor_temps),
        )
        savings = baseline_cost - predicted_cost - deferred_cost

        t_elapsed = (time.monotonic() - t_start) * 1000
        _LOGGER.info(
            "Optimization completed in %.0fms: cost=%.2f, baseline=%.2f, "
            "savings=%.1f%%, solar_reduction=%.2f, wind_factor=%.2f",
            t_elapsed, predicted_cost, baseline_cost,
            _savings_percentage(savings, baseline_cost),
            forecast_analysis["solar_reduction_factor"],
            forecast_analysis["wind_anticipation_factor"],
        )

        return self._build_result(
            h,
            space_power=optimal_power,
            trajectories=(room_temps, slab_temps, upper_temps, lower_temps),
            buffer_temps=buffer_temps,
            wood_temps=wood_temps,
            objective_value=achieved_objective,
            status=status,
            predicted_cost=predicted_cost,
            baseline_cost=baseline_cost,
            savings=savings,
            deferred_cost=deferred_cost,
        )

    # ------------------------------------------------------------------
    # Reporting helpers shared by both solve paths
    # ------------------------------------------------------------------

    def _grid_report(
        self,
        total_power: np.ndarray,
        baseline_load: np.ndarray,
        dt: float,
        start_time: datetime | None = None,
    ) -> dict[str, Any]:
        """Peak and cycling figures for the solved plan."""
        cfg = self.config
        offset_steps = self._window_offset_steps(start_time, dt)
        n = len(np.asarray(total_power))
        factors = self._peak_window_factors(n, dt, start_time, offset_steps)
        if factors is None:
            peak_kw = realised_peak(
                total_power,
                baseline_load,
                cfg.peak_window_minutes,
                dt,
                offset_steps,
            )
        else:
            # Billed-equivalent projection when the #13 masks are active:
            # this figure is published beside the billed-equivalent threshold
            # and the peak cost, and a physical 8 kW above a half-rate 4 kW
            # threshold with zero cost read as three mutually contradictory
            # numbers. Unmasked, this is the physical window max, as always.
            house = np.asarray(total_power, dtype=float) + np.asarray(
                baseline_load, dtype=float
            )
            windows = metering_windows(
                house, cfg.peak_window_minutes, dt, offset_steps
            )
            f = factors[: windows.size]
            if f.size < windows.size:
                f = np.concatenate([f, np.ones(windows.size - f.size)])
            peak_kw = float(np.max(windows * f)) if windows.size else 0.0
        return {
            "peak_kw": round(peak_kw, 3),
            "peak_cost": round(
                peak_cost(
                    total_power,
                    baseline_load,
                    cfg.peak_threshold_kw,
                    cfg.peak_price_per_kw,
                    cfg.peak_window_minutes,
                    dt,
                    cfg.peak_count,
                    offset_steps,
                    window_factors=self._peak_window_factors(
                        len(np.asarray(total_power)), dt, start_time,
                        offset_steps,
                    ),
                ),
                3,
            ),
            "starts": count_compressor_starts(total_power),
        }

    def _price_known_list(self, n_steps: int) -> list[bool]:
        if self._price_known is None:
            return [True] * n_steps
        return [bool(v) for v in self._price_known[:n_steps]]

    def _pv_surplus_list(self, n_steps: int) -> list[float]:
        if self._pv_surplus is None:
            return []
        if not np.any(self._pv_surplus > 1e-6):
            return []
        return [round(float(v), 3) for v in self._pv_surplus[:n_steps]]

    def _pv_self_consumed(self, power: np.ndarray, dt: float) -> float:
        """Heat pump energy that lands inside forecast surplus, kWh."""
        if self._pv_surplus is None or not np.any(self._pv_surplus > 1e-6):
            return 0.0
        n = min(len(power), len(self._pv_surplus))
        served = np.minimum(
            np.asarray(power[:n], dtype=float), self._pv_surplus[:n]
        )
        return round(float(np.sum(served) * dt), 3)

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

    def _build_dhw_requirements(
        self,
        initial_state: ThermalState,
        prices: np.ndarray,
        outdoor_temps: np.ndarray,
        step_hours: np.ndarray,
        n_steps: int,
        dt: float,
        p_max: float,
        space_demand: np.ndarray | None = None,
        dhw_pins: np.ndarray | None = None,
        p_run_cap: float | None = None,
    ) -> dict[str, Any]:
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
        params = self.model.params
        windows, learned_windows = self._effective_dhw_windows()

        dhw_min_temp = params.dhw_min_temp
        dhw_setpoint = params.dhw_setpoint
        idle_min_temp = min(params.dhw_idle_min_temp, dhw_min_temp)
        c_dhw = max(params.dhw_tank_thermal_mass, 0.05)

        hours_mod = np.asarray(step_hours, dtype=float) % 24.0
        in_window = np.array(
            [hour_in_windows(float(h), windows) for h in hours_mod], dtype=bool
        )
        prev_in_window = np.array(
            [hour_in_windows(float(h) - dt, windows) for h in hours_mod], dtype=bool
        )
        window_starts = np.where(in_window & ~prev_in_window)[0].tolist()

        draw_rates = self.model.dhw_draw_rates(hours_mod)

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
                * max(0.5 * (dhw_setpoint + dhw_min_temp) - 20.0, 0.0)
                * window_hours
            )
            needed_delta = (draw_energy + standby_energy) / c_dhw
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

        # --- Anti-legionella cycle ---
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
            if deadline_step < n_steps:
                # The hard deadline is inside this horizon: place the cycle
                # at the cheapest hour before it, elastic or not. Hygiene
                # never waits for a better price.
                limit = max(1, min(deadline_step + 1, n_steps))
                place_idx = int(np.argmin(dhw_prices[:limit]))
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
                # the disinfection temperature by are candidates.
                lift = max(
                    0.0,
                    params.dhw_legionella_temp
                    - float(initial_state.dhw_temperature),
                )
                thermal_kw = p_dhw_run * max(
                    self.model.compute_cop_dhw(
                        float(outdoor_temps[0]) if n_steps else 0.0,
                        params.dhw_legionella_temp,
                    ),
                    0.5,
                )
                min_step = int(np.ceil(lift * c_dhw / max(thermal_kw, 0.1) / dt))
                known_mask[: min(min_step, n_steps)] = False
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

        max_temp = params.dhw_max_temp
        # How long stored heat actually survives in this tank. The learned
        # cooling rate drives it, so a well-insulated tank is allowed to
        # pre-heat much further ahead than a leaky one.
        max_lead_hours = self.model.dhw_hold_hours()
        requirement = np.maximum(floor_temps, ready_temps)

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

        # Pre-heating is allowed anywhere in the horizon: the planners price the
        # standby losses of storing heat, so an early cheap hour wins only when
        # it is still cheaper after those losses. Capping the lead time instead
        # of pricing it is what used to pin heating to the demand windows.
        max_lead_steps = max(1, min(n_steps, int(np.ceil(max_lead_hours / dt))))

        # Stage 1: a linear program over the whole horizon finds the truly
        # cheapest feasible allocation. Stage 2 repairs whatever the linear
        # approximation got wrong against the real tank simulation.
        seed = self._plan_dhw_min_cost(
            initial_temp=initial_state.dhw_temperature,
            requirement=requirement,
            prices=dhw_prices,
            outdoor_temps=outdoor_temps,
            draw_rates=draw_rates,
            n_steps=n_steps,
            dt=dt,
            p_dhw_max=p_dhw_run,
            c_dhw=c_dhw,
            max_temp=max_temp,
            space_demand=space_demand,
            p_total_max=p_max,
            forced_off=forced_off,
        )

        schedule = self._plan_dhw_cheapest_first(
            initial_temp=initial_state.dhw_temperature,
            requirement=requirement,
            prices=dhw_prices,
            outdoor_temps=outdoor_temps,
            draw_rates=draw_rates,
            n_steps=n_steps,
            dt=dt,
            p_dhw_max=p_dhw_run,
            min_run_power=min_run_power,
            max_lead_steps=max_lead_steps,
            c_dhw=c_dhw,
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
        )

        # Rounding weak slots down leaves energy the tank was counting on
        # unbought, so the greedy planner runs once more to re-buy any
        # shortfall in steps that can still take a real block.
        schedule = self._plan_dhw_cheapest_first(
            initial_temp=initial_state.dhw_temperature,
            requirement=requirement,
            prices=dhw_prices,
            outdoor_temps=outdoor_temps,
            draw_rates=draw_rates,
            n_steps=n_steps,
            dt=dt,
            p_dhw_max=p_dhw_run,
            min_run_power=min_run_power,
            max_lead_steps=max_lead_steps,
            c_dhw=c_dhw,
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
            plan=schedule,
            initial_temp=initial_state.dhw_temperature,
            outdoor_temps=outdoor_temps,
            draw_rates=draw_rates,
            dt=dt,
            requirement=requirement,
            max_temp=max_temp,
            p_dhw_max=p_dhw_run,
            min_run_power=min_run_power,
            prices=prices,
            c_dhw=c_dhw,
            forced_off=forced_off,
        )
        # Deliberately NOT re-clamped: the external clamp predicts the tank
        # without draw relief (conservative by design), so it reads the
        # repair's in-window top-ups — which exist precisely because the
        # window is draining the tank — as rating breaches and truncates
        # them back out. The repair's own simulation runs the real step,
        # whose internal rating clamp books any genuinely refused heat, so
        # a repaired plan cannot overshoot where it matters.

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
            )
            # Same hygiene as the automatic path: a step the rating truncated
            # below the pump's minimum cannot actually run, even a pinned one.
            schedule = np.where(schedule < min_run_power - 1e-9, 0.0, schedule)
        self._dhw_requirement = requirement
        self._dhw_legionella_step = legionella_step

        return {
            "floor_temps": floor_temps,
            "ready_temps": ready_temps,
            "draw_rates": draw_rates,
            "in_window": in_window,
            "max_temp": max_temp,
            "schedule": schedule,
            "windows_text": format_windows(windows),
            "windows_learned": learned_windows,
            "next_window_in_hours": (
                round(next_window, 2) if next_window is not None else None
            ),
            "legionella_due": legionella_due,
            "legionella_hour": (
                round(legionella_hour, 2) if legionella_hour is not None else None
            ),
            "legionella_step": legionella_step,
            "external_heat_suppressed_steps": suppress_steps,
            "max_lead_hours": max_lead_hours,
        }

    def _dhw_cop_profile(
        self,
        outdoor_temps: np.ndarray,
        tank_temps: np.ndarray,
    ) -> np.ndarray:
        """Per-step DHW COP for a given assumed tank temperature trajectory."""
        return np.array(
            [
                max(
                    1.0,
                    self.model.compute_cop_dhw(
                        float(outdoor_temps[i]), float(tank_temps[i])
                    ),
                )
                for i in range(len(outdoor_temps))
            ]
        )

    def _plan_dhw_min_cost(
        self,
        initial_temp: float,
        requirement: np.ndarray,
        prices: np.ndarray,
        outdoor_temps: np.ndarray,
        draw_rates: np.ndarray,
        n_steps: int,
        dt: float,
        p_dhw_max: float,
        c_dhw: float,
        max_temp: float,
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

        Returns ``None`` when the solve fails, so the caller can fall back to
        the greedy planner.
        """
        if n_steps == 0:
            return None

        requirement = np.minimum(np.asarray(requirement, dtype=float), max_temp)
        params = self.model.params
        ua = max(params.dhw_tank_heat_loss_coefficient, 1e-6)
        c = max(c_dhw, 0.05)

        # Per-step decay of stored heat. Guarded so an absurdly leaky tank or a
        # long time step cannot produce a negative (unstable) factor.
        decay = float(np.clip(1.0 - ua * dt / c, 0.0, 1.0))
        gain = ua * DHW_AMBIENT_TEMP * dt / c

        # Free trajectory: what the tank does with no heating at all.
        free = np.zeros(n_steps + 1)
        free[0] = initial_temp
        for i in range(n_steps):
            free[i + 1] = (
                decay * free[i] - float(draw_rates[i]) * dt / c + gain
            )

        # Influence matrix: A[m, j] = degrees at step m+1 per thermal kWh at j.
        idx = np.arange(n_steps)
        lag = idx[:, None] - idx[None, :]
        influence = np.where(lag >= 0, np.power(decay, np.maximum(lag, 0)) / c, 0.0)

        # COP is temperature dependent; solve once against the requirement
        # level, then re-solve against the trajectory the first pass produced.
        cop = self._dhw_cop_profile(
            outdoor_temps, np.maximum(requirement, params.dhw_min_temp)
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

            energy = np.asarray(result.x[:n_steps], dtype=float)
            best = np.clip(energy / (cop * dt), 0.0, p_dhw_max)

            # Refine the COP estimate against the tank temperatures this plan
            # actually produces, so the cost ranking reflects reality.
            temps = self.model.simulate_dhw_only(
                initial_temp=initial_temp,
                dhw_power_schedule=best,
                outdoor_temps=outdoor_temps,
                draw_rates=draw_rates,
                dt_hours=dt,
            )
            refined = self._dhw_cop_profile(outdoor_temps, temps[:-1])
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

    def _repair_dhw_floor(
        self,
        *,
        plan: np.ndarray,
        initial_temp: float,
        outdoor_temps: np.ndarray,
        draw_rates: np.ndarray,
        dt: float,
        requirement: np.ndarray,
        max_temp: float,
        p_dhw_max: float,
        min_run_power: float,
        prices: np.ndarray,
        c_dhw: float,
        forced_off: np.ndarray | None = None,
    ) -> np.ndarray:
        """Top up the plan until the SIMULATED trajectory meets the floor.

        Bounded best-effort: each round finds the first step whose simulated
        temperature breaches the requirement, sizes the missing electrical
        energy at the tank's own marginal COP, and adds it at the cheapest
        step with headroom that can still reach the breach — after the last
        rating-pinned step before it, since heat added ahead of a full tank
        is refused, not stored. A demand no rating-legal plan can meet exits
        after the round limit with the closest achievable trajectory; the
        rating clamp re-runs after and always wins.
        """
        plan = np.asarray(plan, dtype=float).copy()
        n = plan.size
        if n == 0 or requirement is None:
            return plan
        req = np.asarray(requirement, dtype=float)[:n]
        # Convergence is a min-run trickle per round in the worst case (a
        # cheap-step landscape already near the run cap), so the bound is
        # sized for a multi-degree breach at trickle pace, not for elegance.
        for _ in range(48):
            temps = np.asarray(
                self.model.simulate_dhw_only(
                    initial_temp=initial_temp,
                    dhw_power_schedule=plan,
                    outdoor_temps=outdoor_temps,
                    draw_rates=draw_rates,
                    dt_hours=dt,
                )
            )
            deficit = req - temps[1 : n + 1]
            breach = np.where(deficit > 0.05)[0]
            if breach.size == 0:
                return plan
            b = int(breach[0])
            # Heat added before a rating-pinned step is refused, so only
            # steps after the last full-tank moment can feed the breach.
            pinned = np.where(temps[: b + 1] >= max_temp - 0.1)[0]
            lo = int(pinned[-1]) if pinned.size else 0
            headroom = p_dhw_max - plan[lo : b + 1]
            usable = headroom > 1e-6
            if forced_off is not None:
                usable &= ~np.asarray(forced_off[lo : b + 1], dtype=bool)
            if not np.any(usable):
                return plan
            costs = np.where(usable, prices[lo : b + 1], np.inf)
            j_local = int(np.argmin(costs))
            j = lo + j_local
            cop_j = max(
                self.model.marginal_cop(
                    float(outdoor_temps[j]), "dhw", store_temp=float(temps[j])
                ),
                0.5,
            )
            needed = float(deficit[b]) * c_dhw / max(dt * cop_j, 1e-6)
            add = float(np.clip(needed, min_run_power, headroom[j_local]))
            new_level = plan[j] + add
            if new_level < min_run_power - 1e-9:
                new_level = min(min_run_power, p_dhw_max)
            plan[j] = min(p_dhw_max, new_level)
        return plan

    def _clamp_dhw_to_capacity(
        self,
        plan: np.ndarray,
        initial_temp: float,
        outdoor_temps: np.ndarray,
        draw_rates: np.ndarray,
        dt: float,
        max_temp: float,
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
        """
        plan = np.array(plan, dtype=float)
        if plan.size == 0:
            return plan

        params = self.model.params
        capacity = max(params.dhw_tank_thermal_mass, 1e-6)
        temp = float(initial_temp)

        for i in range(len(plan)):
            cop = max(
                self.model.compute_cop_dhw(float(outdoor_temps[i]), temp), 0.1
            )
            # Headroom in kW electrical: how much may be delivered this step
            # before the tank passes its rating. Negative when the tank is
            # already over, which happens when it *starts* over — heating is
            # then simply forbidden rather than reversed, because the plan
            # cannot un-heat water.
            headroom_c = max_temp - temp
            allowed = headroom_c * capacity / (cop * dt) if headroom_c > 0 else 0.0
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
        max_temp: float,
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
        """
        plan = np.array(plan, dtype=float)
        weak = np.where((plan > 1e-6) & (plan < min_run_power))[0]
        if weak.size == 0:
            return np.clip(plan, 0.0, p_dhw_max)

        run_power = min(min_run_power, p_dhw_max)
        for i in weak:
            raised = plan.copy()
            raised[i] = run_power
            temps = self.model.simulate_dhw_only(
                initial_temp=initial_temp,
                dhw_power_schedule=raised,
                outdoor_temps=outdoor_temps,
                draw_rates=draw_rates,
                dt_hours=dt,
            )
            if float(np.max(temps)) <= max_temp + 0.5:
                plan = raised
            else:
                plan[i] = 0.0
        return np.clip(plan, 0.0, p_dhw_max)

    def _plan_dhw_cheapest_first(
        self,
        initial_temp: float,
        requirement: np.ndarray,
        prices: np.ndarray,
        outdoor_temps: np.ndarray,
        draw_rates: np.ndarray,
        n_steps: int,
        dt: float,
        p_dhw_max: float,
        min_run_power: float,
        max_lead_steps: int,
        c_dhw: float,
        max_temp: float,
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
        if initial_plan is None:
            plan = np.zeros(n_steps)
        else:
            plan = np.clip(
                np.array(initial_plan, dtype=float), 0.0, p_dhw_max
            )
        if n_steps == 0:
            return plan

        # A requirement above the tank's rated maximum can never be met; asking
        # for it would only make the planner give up.
        requirement = np.minimum(np.asarray(requirement, dtype=float), max_temp)

        # Fraction of stored heat lost per hour of storage: raising the tank by
        # ΔT stores C·ΔT kWh but adds U·ΔT kW of standby loss.
        loss_rate_per_hour = (
            self.model.params.dhw_tank_heat_loss_coefficient / max(c_dhw, 0.05)
        )

        tolerance = 0.05  # °C
        unreachable: set[int] = set()
        for _ in range(400):
            temps = self.model.simulate_dhw_only(
                initial_temp=initial_temp,
                dhw_power_schedule=plan,
                outdoor_temps=outdoor_temps,
                draw_rates=draw_rates,
                dt_hours=dt,
            )
            gaps = requirement - temps[1:]
            violations = [
                int(i) for i in np.where(gaps > tolerance)[0] if int(i) not in unreachable
            ]
            if not violations:
                break

            k = violations[0]
            needed_kwh = float(gaps[k]) * c_dhw

            # The tank may not be planned above its rating, except that a
            # requirement (an anti-legionella cycle, typically) always has to
            # remain reachable.
            temp_ceiling = max(max_temp - 1.0, float(requirement[k]))

            def usable(j: int) -> bool:
                if forced_off is not None and forced_off[j]:
                    return False
                return plan[j] < p_dhw_max - 1e-6 and temps[j + 1] < temp_ceiling - 0.1

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
                        float(outdoor_temps[j]), float(requirement[k])
                    ),
                )
                spare_thermal_kwh = (p_dhw_max - plan[j]) * cop * dt
                # Heat added at step j raises every later tank temperature, so
                # the ceiling has to be respected across the whole stretch the
                # heat is stored for — not just at step j.
                peak_ahead = float(np.max(temps[j + 1 : k + 2]))
                headroom_kwh = max(0.0, (temp_ceiling - peak_ahead) * c_dhw)
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
                break

            if added <= 1e-9:
                # No candidate could absorb energy for this step either.
                unreachable.add(k)

        return np.clip(plan, 0.0, p_dhw_max)

    def _optimize_with_dhw(self, h: _Horizon) -> OptimizationResult:
        """Optimize coordinated space heating + DHW heating.

        Decision variables: [P_space[0..n-1], P_dhw[0..n-1]]
        The heat pump can allocate power to space OR DHW, with total
        constrained by max capacity.
        """
        import time

        # See ``_optimize_space_only`` for why the context is unpacked.
        initial_state, prices, dt, n_steps = (
            h.initial_state, h.prices, h.dt, h.n_steps
        )
        outdoor_temps, wind_speeds = h.outdoor_temps, h.wind_speeds
        precipitation, solar_radiation = h.precipitation, h.solar_radiation
        comfort_targets = h.comfort_targets
        temp_min_bounds, temp_max_bounds = h.temp_min_bounds, h.temp_max_bounds
        step_hours, solar_gains_per_step = h.step_hours, h.solar_gains
        forecast_heat_loss_factors = h.heat_loss_factors
        start_time, t_start = h.start_time, h.t_start

        p_min = self.model.params.min_electrical_power
        p_max = self.model.params.max_electrical_power
        dhw_min_temp = self.model.params.dhw_min_temp
        dhw_setpoint = self.model.params.dhw_setpoint

        start_hour = (
            start_time.hour + start_time.minute / 60.0
        )

        anticipatory_weights = self._anticipatory_weights(
            n_steps, dt, solar_gains_per_step, forecast_heat_loss_factors
        )

        # ----------------------------------------------------------------
        # DHW demand model
        # ----------------------------------------------------------------
        # The DHW requirement is expressed as a per-step temperature floor
        # rather than a target trajectory. Inside a configured demand window
        # hot water must be available; outside it there is no requirement, so
        # the only reason to run the pump is to be ready for the *next* window
        # — and the energy-cost term then decides *when* that happens.
        dhw_plan = self._build_dhw_requirements(
            initial_state=initial_state,
            prices=prices,
            outdoor_temps=outdoor_temps,
            step_hours=step_hours,
            n_steps=n_steps,
            dt=dt,
            p_max=p_max,
            dhw_pins=h.dhw_pins,
            p_run_cap=(
                float(np.min(h.power_caps_extra))
                if h.power_caps_extra is not None
                else None
            ),
        )

        dhw_floor_temps = dhw_plan["floor_temps"]
        dhw_ready_temps = dhw_plan["ready_temps"]
        dhw_draw_rates = dhw_plan["draw_rates"]
        in_demand_window = dhw_plan["in_window"]
        optimal_dhw = dhw_plan["schedule"]

        # Kept for reporting/back-compat: which hours the learned profile still
        # considers high-usage (restricted to the configured windows).
        usage_intensity = np.array([
            self.model.dhw_usage_intensity(h) for h in step_hours
        ])
        high_usage_mask = in_demand_window & (
            usage_intensity >= max(1.0, float(np.percentile(usage_intensity, 70)))
        )

        # DHW is a deferrable, effectively on/off load, so it is scheduled by
        # the min-cost planner above rather than by the gradient solver (which
        # would smear it into an unrealizable trickle). Space heating is then
        # optimized *around* the fixed DHW blocks: the pump's remaining
        # capacity during a DHW block is what bounds space heating power.
        #
        # That decomposition is only exact when the two loads do not compete
        # for the compressor. They do: both want the cheapest hours. So the
        # split is iterated below, re-planning DHW against the space-heating
        # profile it actually has to share the pump with.

        # See ``_optimize_space_only`` for why the band normalises the
        # pull-to-target term.
        comfort_band = np.maximum(comfort_targets - temp_min_bounds, 1.0)
        terminal_cost = self._terminal_cost(prices, outdoor_temps)
        cycling, capacity, baseline_load = self._grid_terms(
            n_steps, dt, start_time
        )
        energy_cost_of = self._energy_cost_fn(prices, dt)

        def objective(
            space_power: np.ndarray,
            dhw_plan_power: np.ndarray | None = None,
        ) -> float:
            """Space heating objective given the fixed DHW schedule."""
            room_temps, slab_temps, upper_temps, lower_temps = (
                self.model.simulate_trajectory(
                    initial_state=initial_state,
                    power_schedule=space_power,
                    outdoor_temps=outdoor_temps,
                    wind_speeds=wind_speeds,
                    precipitation=precipitation,
                    solar_radiation=solar_radiation,
                    dt_hours=dt,
                    external_heat_kw=h.external_heat_kw,
                    valve_targets=h.valve_targets,
                    humidity=h.humidity,
                    start_hour=float(h.step_hours[0]),
                )
            )

            # The compressor is one machine: the grid sees the *combined*
            # draw, so the energy cost, the PV surplus it may consume, the
            # cycling term and the house peak are all properties of the sum,
            # not of space heating alone.
            combined = (
                space_power
                if dhw_plan_power is None
                else space_power + dhw_plan_power
            )

            # --- Electricity cost (total: space + DHW), piecewise in PV ---
            energy_cost = energy_cost_of(combined) * self.config.price_weight

            space_penalty, comfort_cost = self._comfort_terms(
                room_temps, upper_temps, lower_temps,
                comfort_targets, temp_min_bounds, temp_max_bounds, comfort_band,
            )


            # Weather anticipation is left to the simulation, which already
            # applies solar gain and the wind/rain loss factors; see the
            # space-only objective for why the extra heuristic terms were
            # removed.

            return (
                energy_cost + space_penalty + comfort_cost
                # Same price_weight scaling as the space-only objective.
                + (cycling(combined) + capacity(combined))
                * self.config.price_weight
                + terminal_cost(
                    room_temps,
                    slab_temps,
                    upper_temps,
                    lower_temps,
                    # Recorded by the call above rather than returned, because
                    # nine call sites unpack a four-tuple.
                    self.model.last_buffer_trajectory,
                )
            )

        # Initial guess: space heating inversely proportional to price.
        init_base = p_max * 0.6 * _price_guess_weights(prices)
        for i in range(n_steps):
            init_base[i] *= anticipatory_weights[i]
        init_base = np.clip(init_base, p_min * 0.5, p_max * 0.8)

        def solve_space(
            dhw_plan: np.ndarray, warm_start: np.ndarray | None
        ) -> tuple[np.ndarray, str, float]:
            """Optimize space heating around a fixed DHW schedule."""
            # The heat pump serves one circuit at a time, so a DHW block eats
            # into the capacity available for space heating during that step.
            headroom = np.maximum(0.0, p_max - dhw_plan)
            if h.power_caps is not None:
                headroom = np.minimum(headroom, h.power_caps)
            if h.power_caps_extra is not None:
                # power_caps bounds space heating alone, so during a DHW block
                # space + DHW could still exceed an external *total* cap. The
                # fuse guard's whole promise is that total draw stays under
                # the limit, so subtract the block from the cap here too.
                headroom = np.minimum(
                    headroom,
                    np.maximum(0.0, h.power_caps_extra - dhw_plan),
                )
            guess = init_base if warm_start is None else warm_start
            guess = np.minimum(np.clip(guess, 0.0, p_max), headroom)
            bounds = [(0.0, float(headroom[i])) for i in range(n_steps)]
            # Manual space pins apply here just as in the DHW-free path. Forcing
            # a step on raises its lower bound, but only as far as the headroom
            # the DHW block left it — a slot the user pinned for both channels
            # cannot demand more than the compressor has.
            bounds = _apply_pins_to_bounds(
                bounds, h.space_pins, self._pin_on_power(p_max)
            )
            guess = self._seed_pinned_guess(guess, bounds)
            # A warm start is a genuinely good lead, so keep it first; the
            # extra structural candidates only matter on the initial solve.
            starts = [guess]
            if warm_start is None:
                energy = float(np.sum(np.minimum(init_base, headroom)) * dt)
                starts.append(
                    np.minimum(
                        _price_ranked_start(prices, energy, p_max, dt), headroom
                    )
                )
                starts.append(headroom * 0.5)
            try:
                res = _multi_start_minimize(
                    objective, starts, bounds, args=(dhw_plan,), maxiter=300
                )
                power = np.clip(res.x, 0.0, headroom)
                return (
                    power,
                    _solver_status(
                        res, lambda x: objective(x, dhw_plan), guess
                    ),
                    float(objective(power, dhw_plan)),
                )
            except Exception as e:
                _LOGGER.error("Space heating optimization (with DHW) failed: %s", e)
                return (
                    guess,
                    f"failed ({e})",
                    float(objective(guess, dhw_plan)),
                )

        optimal_space, status, best_score = solve_space(optimal_dhw, None)
        optimal_space, optimal_dhw, status = self._co_optimize(
            h,
            dhw_plan=dhw_plan,
            space_power=optimal_space,
            dhw_power=optimal_dhw,
            status=status,
            best_score=best_score,
            solve_space=solve_space,
            p_max=p_max,
        )

        # Simulate with optimal schedule
        room_temps, slab_temps, upper_temps, lower_temps, dhw_temps = (
            self.model.simulate_trajectory_with_dhw(
                initial_state=initial_state,
                space_power_schedule=optimal_space,
                dhw_power_schedule=optimal_dhw,
                outdoor_temps=outdoor_temps,
                wind_speeds=wind_speeds,
                precipitation=precipitation,
                solar_radiation=solar_radiation,
                start_hour=start_hour,
                dt_hours=dt,
                dhw_draw_rates=dhw_draw_rates,
                external_heat_kw=h.external_heat_kw,
                valve_targets=h.valve_targets,
                humidity=h.humidity,
            )
        )
        # Captured next to the call that wrote it. Before this method recorded
        # the series, whatever the last space-only simulation had left on the
        # model was a trajectory for a different power schedule.
        buffer_temps = self.model.last_buffer_trajectory
        wood_temps = self.model.last_wood_trajectory
        # The achieved objective, for candidate comparison across valve
        # schedules.
        achieved_objective = float(objective(optimal_space, optimal_dhw))

        # Baseline cost
        baseline_power, baseline_end = self._compute_baseline_power(
            initial_state, outdoor_temps, wind_speeds, precipitation,
            solar_radiation, dt, comfort_targets,
            external_heat_kw=h.external_heat_kw,
        )
        # Baseline DHW: an always-hot tank held at the setpoint. That costs the
        # energy drawn off as hot water plus the standby loss of keeping a tank
        # at setpoint around the clock, which is exactly the behaviour the
        # demand time frames exist to avoid.
        p = self.model.params
        cop_dhw = max(
            self.model.compute_cop_dhw(float(np.mean(outdoor_temps)), dhw_setpoint),
            1e-3,
        )
        standby_loss = p.dhw_tank_heat_loss_coefficient * max(
            dhw_setpoint - DHW_AMBIENT_TEMP, 0.0
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
        baseline_cost = energy_cost_of(baseline_power + baseline_dhw)
        total_optimal_power = optimal_space + optimal_dhw
        predicted_cost = energy_cost_of(total_optimal_power)
        # Hot water's share is its marginal cost on top of space heating, so
        # the two attributions sum exactly to the total.
        dhw_cost = predicted_cost - energy_cost_of(optimal_space)

        # Settle up the heat the optimized plan left unstored at the horizon end.
        # The baseline reference ends with a tank at setpoint, so compare against
        # that rather than against the optimized tank's own starting point.
        baseline_end.dhw_temperature = dhw_setpoint
        optimized_end = self._replay_end_state(
            initial_state, optimal_space, outdoor_temps, wind_speeds,
            precipitation, solar_radiation, dt,
            external_heat_kw=h.external_heat_kw,
            valve_targets=h.valve_targets,
        )
        optimized_end.dhw_temperature = float(dhw_temps[-1])
        # The tank only has to satisfy the requirement in force at the end of
        # the horizon. Outside a demand window that is the idle minimum, so a
        # cold tank at midnight is not treated as borrowed heat.
        deferred_cost = self._deferred_energy_cost(
            baseline_end, optimized_end, prices, outdoor_temps, include_dhw=True,
            caps=self._settlement_caps(
                outdoor_temps, dhw_cap=float(dhw_floor_temps[-1])
            ),
        )
        savings = baseline_cost - predicted_cost - deferred_cost


        t_elapsed = (time.monotonic() - t_start) * 1000

        dhw_active_steps = int(np.sum(optimal_dhw > 0.1))
        _LOGGER.info(
            "DHW+Space optimization completed in %.0fms: cost=%.2f (DHW=%.2f in "
            "%d steps), baseline=%.2f, savings=%.1f%%, windows=%s",
            t_elapsed, predicted_cost, dhw_cost, dhw_active_steps, baseline_cost,
            _savings_percentage(savings, baseline_cost),
            dhw_plan["windows_text"] or "always",
        )

        result = self._build_result(
            h,
            space_power=optimal_space,
            trajectories=(room_temps, slab_temps, upper_temps, lower_temps),
            buffer_temps=buffer_temps,
            wood_temps=wood_temps,
            objective_value=achieved_objective,
            status=status,
            predicted_cost=predicted_cost,
            baseline_cost=baseline_cost,
            savings=savings,
            deferred_cost=deferred_cost,
            dhw_power=optimal_dhw,
            dhw_temps=dhw_temps,
            dhw_cost=dhw_cost,
            predictive_info={
                "dhw_peak_usage_hours": [
                    int(step_hours[idx]) % 24
                    for idx in np.where(high_usage_mask)[0][:24].tolist()
                ],
                "dhw_preheat_lead_hours": round(dhw_plan["max_lead_hours"], 2),
                "dhw_min_temperature": float(dhw_min_temp),
                "dhw_target_temperature": float(dhw_setpoint),
                "dhw_usage_intensity_now": float(usage_intensity[0]) if len(usage_intensity) else 1.0,
                "dhw_windows": dhw_plan["windows_text"],
                "dhw_in_demand_window": bool(in_demand_window[0]) if n_steps else False,
                "dhw_next_window_in_hours": dhw_plan["next_window_in_hours"],
                "dhw_required_temperature_now": (
                    float(max(dhw_floor_temps[0], dhw_ready_temps[0]))
                    if n_steps
                    else float(dhw_min_temp)
                ),
                "dhw_idle_min_temperature": float(
                    self.model.params.dhw_idle_min_temp
                ),
                "dhw_legionella_due": dhw_plan["legionella_due"],
                "dhw_legionella_step_hour": dhw_plan["legionella_hour"],
                "dhw_planned_heating_hours": [
                    round(float(step_hours[idx]), 2)
                    for idx in np.where(optimal_dhw > 0.1)[0][:48].tolist()
                ],
                # Hours of planned heating that happen ahead of a demand
                # window rather than inside it — the visible sign that the
                # tank is being charged when electricity is cheap.
                "dhw_preheat_hours": round(
                    float(np.sum((optimal_dhw > 0.1) & ~in_demand_window) * dt), 2
                ),
                "dhw_cooling_rate": round(
                    float(self.model.params.dhw_cooling_rate), 3
                ),
                "dhw_hold_hours": round(float(self.model.dhw_hold_hours()), 1),
            },
        )
        # The only reason codes the shared builder cannot produce: they depend
        # on the demand windows and legionella deadline this path computed.
        result.dhw_reasons = _mark_manual_reasons(
            classify_dhw_steps(
                optimal_dhw,
                in_demand_window,
                dhw_ready_temps,
                dhw_plan.get("legionella_step"),
                n_steps,
            ),
            h.dhw_pins,
        )
        return result

    def _settlement_caps(
        self, outdoor_temps: np.ndarray, dhw_cap: float | None = None
    ) -> dict[str, float]:
        """Temperatures above which stored heat is worth nothing.

        Heat carried past the horizon is only an asset up to the point where it
        is actually needed. A house sitting at 25 °C in July because the sun
        heated it is not holding 4 °C of useful charge, and settling that up
        would charge the optimizer for failing to be as overheated as the
        reference. Cap every store at what the comfort target and the hot water
        requirement genuinely call for.
        """
        p = self.model.params
        target = self.config.target_temp
        out_mean = float(np.mean(outdoor_temps))
        # Slab has to run above the room to push heat into it, so its useful
        # ceiling is the temperature that sustains the target, not the target.
        if p.two_zone_enabled:
            # The slab feeds ONLY the lower zone (`q_slab_to_lower` in the
            # dynamics; the upper zone is radiator-fed), so its ceiling is
            # sized from the lower zone's demand alone — the learned loss,
            # because every consumer of the dynamics goes through it — and
            # the lower zone's share of the internal gains. Sizing it from
            # the whole house inflated the cap by the upper zone's demand
            # and over-valued hot-slab end states by exactly that much.
            q_demand = max(
                0.0,
                p.lower_floor_heat_loss_learned * (target - out_mean)
                - p.internal_gains * (1.0 - p.upper_floor_area_ratio),
            )
        else:
            u_eff = p.heat_loss_coefficient
            q_demand = max(0.0, u_eff * (target - out_mean) - p.internal_gains)
        slab_cap = target + q_demand / max(p.slab_heat_transfer, 1e-6)
        caps = {"room": target, "slab": slab_cap}
        # The buffer tank needs its own ceiling, and it is much higher than the
        # slab's.
        #
        # The cap exists to stop *passive* overheating being counted as charge:
        # a house at 25 C in July is not holding useful heat. That reasoning does
        # not transfer to a tank. A tank only gets hot because the pump
        # deliberately heated it, and the valve stops it overheating anything, so
        # every degree in it is heat that will genuinely be used.
        #
        # Sharing the slab's cap made the tank invisible as a store: with a slab
        # ceiling near 28 C, charging a tank from 45 C to 70 C was credited with
        # 0.0 kWh of the 21.8 kWh actually stored. Charging was pure cost with no
        # modelled benefit, which is why every starting point descended to the
        # same no-storage plan.
        if p.buffer_is_store:
            # Valued up to the ceiling the plan can actually charge to, not
            # the raw safety rating. The rating is where the simulation's
            # clamp and the cap-refusal loop stop the tank — but reaching it
            # requires the pump to out-run the house's standing draw and the
            # tank's own loss at an ever-worsening flow-derated COP, and in
            # cold weather a real pump cannot. Settling the full distance to
            # 70 °C charged every plan for failing to hold a temperature no
            # plan could reach, an asymmetry the room cap (the target, not
            # the comfort ceiling) never had.
            ceiling = self._buffer_charge_ceiling(out_mean)
            # Heat ALREADY in the tank above the charging ceiling is real:
            # it was paid for, and draining it displaces bought electricity
            # at the derated COP. Capping the value at the ceiling alone let
            # a plan drain a pre-charged tank (a mild evening's 60 °C before
            # a cold snap) to the ceiling with zero settlement — re-creating
            # the tail-dumping this term exists to prevent, in exactly the
            # regime storage matters most (v4.0.5 review). The floor at the
            # solve's initial temperature keeps the deficit direction
            # honest too: no plan can charge past the ceiling, so the
            # unavoidable decay from a hot start prices every candidate
            # identically and only the drained difference separates them.
            initial = self._initial_buffer_temp
            if initial is not None:
                ceiling = min(
                    float(p.buffer_max_temp), max(ceiling, float(initial))
                )
            caps["buffer"] = ceiling
        else:
            # Without a valve the tank cannot be charged at all, and below the
            # store threshold (item 27) it holds too little to matter, so its
            # cap cannot change any decision. Left alone so these paths stay
            # byte-for-byte identical.
            caps["buffer"] = slab_cap
        if p.two_tank_modelled:
            # The wood tank is a genuine store too (issue #40): a burn's heat
            # still in it at the horizon end displaces bought heat exactly as
            # the buffer's does. Report-only and symmetric, like every
            # settlement figure -- the objective's terminal cost deliberately
            # excludes it (nobody refills it with electricity, so crediting
            # it there would create a hoarding incentive with no refill cost).
            caps["wood"] = WOOD_TANK_MAX_TEMP
        if dhw_cap is not None:
            caps["dhw"] = dhw_cap
        return caps

    def _buffer_charge_ceiling(self, out_mean: float) -> float:
        """The tank temperature the pump can still charge past, °C.

        The bound the solve actually operates under. The simulation's clamp
        sits at ``buffer_max_temp``, but the tank only rises while the pump's
        thermal output at the tank's own flow temperature exceeds the house's
        standing draw plus the tank's standby loss — and the flow-derated COP
        falls as the tank warms, so in cold weather that balance closes below
        the rating and no schedule can push further. Bisection on the net
        charge rate, which is monotone decreasing in tank temperature; the
        answer is the rating whenever the pump still out-runs the drains
        there (every mild-weather case, where this changes nothing).
        """
        p = self.model.params
        hi = float(p.buffer_max_temp)
        # Below the flow reference no derate applies and the tank is just the
        # hydronic loop; heat down there is always chargeable.
        lo = max(20.0, float(p.cop_flow_reference_temp))
        if hi <= lo:
            return hi
        target = self.config.target_temp
        if p.two_zone_enabled:
            u_house = p.upper_floor_heat_loss + p.lower_floor_heat_loss_learned
        else:
            u_house = p.heat_loss_coefficient
        # The learned leakage scale rides along: the dynamics and the battery
        # view both apply it, and a learned-leaky house that omitted it here
        # got an optimistic ceiling — the one direction this bound must not
        # err (v4.0.5 review).
        u_house *= p.house_heat_loss_scale
        # What the valve keeps feeding the house while the tank charges: the
        # standing demand at the comfort target, the same steady-state frame
        # as the settlement caps themselves.
        q_house = max(0.0, u_house * (target - out_mean) - p.internal_gains)
        ua_tank = p.buffer_tank_heat_loss_coefficient
        p_max = p.max_electrical_power

        def net(temp: float) -> float:
            cop = self.model.marginal_cop(out_mean, "buffer", store_temp=temp)
            return p_max * cop - q_house - ua_tank * max(0.0, temp - 20.0)

        if net(hi) > 0.0:
            return hi
        if net(lo) <= 0.0:
            return lo
        for _ in range(32):
            mid = 0.5 * (lo + hi)
            if net(mid) > 0.0:
                lo = mid
            else:
                hi = mid
        return lo

    def _deferred_energy_cost(
        self,
        baseline_end: ThermalState,
        optimized_end: ThermalState,
        prices: np.ndarray,
        outdoor_temps: np.ndarray,
        include_dhw: bool = False,
        caps: dict[str, float] | None = None,
    ) -> float:
        """Cost of restoring the heat the optimized plan left unstored.

        Nothing beyond the horizon is penalised, so the optimizer will happily
        coast the house (and tank) down as the window closes. That heat is
        borrowed, not saved, and counting it as a saving is what makes the
        savings figure drift upwards. Value the difference at the price the
        heat would actually be bought back at, which is the cheapest part of the
        upcoming window rather than the average.

        Symmetric: a surplus is credited exactly as a deficit is charged. It
        used to be one-sided, on the reasoning that the reference is a
        thermostat rather than a competing plan -- but that argument forbids
        charging just as much as it forbids crediting, and what it produced was
        a savings figure that understated itself precisely when the plan chose
        to end the window warm. Measured across ten scenarios, three ended with
        more useful heat than the thermostat baseline and were given nothing for
        it: shoulder by 2.29 SEK on a reported 27.64 (8 %), flat prices by 3.52
        on 14.85 (24 %), and flat prices with no mixing valve at all by 6.06 on
        9.84 -- a 62 % understatement, and nothing to do with storage. It is the
        building's own mass ending warmer than a thermostat would have left it.

        What makes the credit safe is ``caps``: every store is already limited
        to the temperature above which its heat is of no further use, so this
        cannot pay out for a house that merely overheated in the sun.

        Note this figure is reported, not optimised -- it reaches
        ``predicted_savings`` and the sensors, and never the objective, which
        prices its own end state through ``_terminal_cost``. Changing it makes
        the number honest; it does not change a single plan.
        """
        stored_gap = self._stored_thermal_energy(
            baseline_end, include_dhw, caps
        ) - self._stored_thermal_energy(optimized_end, include_dhw, caps)

        out_mean = float(np.mean(outdoor_temps))
        cop = max(self.model.compute_cop(out_mean), 1e-3)
        # Heat is topped up when it is cheap, so settle at a low percentile
        # rather than the mean; using the mean would over-charge the optimizer
        # for heat it would obviously buy back in a cheap hour. The same
        # percentile prices a credit, where it errs the other way and is the
        # conservative choice: heat already in store displaces whatever the next
        # window would have paid, which is the average and not the cheap tail.
        refill_price = float(np.percentile(prices, 25))
        electrical = stored_gap / cop

        # v4.0.5: the tank shares of the gap re-price at their own marginal
        # COP — the buffer refills at the flow-derated COP of its settlement
        # temperature, the DHW tank at `compute_cop_dhw` — because that is
        # what the simulation would actually charge to put the heat back.
        # Pricing them at the plain space curve made a cold tank cheap to
        # refill and a warm one rich to credit, so the reported savings
        # overstated themselves exactly when the plan ended with a cold tank.
        # Written as corrections on the plain-COP total rather than a clean
        # per-store split so every store still priced at the plain curve —
        # and every configuration where the tank COPs collapse to it —
        # keeps the historical arithmetic bit for bit.
        p = self.model.params
        caps = caps or {}

        def _capped(value: float, cap_key: str) -> float:
            cap = caps.get(cap_key)
            return min(value, cap) if cap is not None else value

        if p.two_zone_enabled:
            cop_buffer = max(
                self.model.marginal_cop(
                    out_mean, "buffer", store_temp=caps.get("buffer")
                ),
                1e-3,
            )
            if cop_buffer != cop:
                buffer_gap = p.buffer_tank_thermal_mass * (
                    _capped(baseline_end.buffer_tank_temperature, "buffer")
                    - _capped(optimized_end.buffer_tank_temperature, "buffer")
                )
                electrical += buffer_gap / cop_buffer - buffer_gap / cop
        if include_dhw:
            dhw_cap = caps.get("dhw")
            cop_dhw = max(
                self.model.marginal_cop(
                    out_mean,
                    "dhw",
                    store_temp=(
                        dhw_cap if dhw_cap is not None else p.dhw_setpoint
                    ),
                ),
                1e-3,
            )
            if cop_dhw != cop:
                dhw_gap = p.dhw_tank_thermal_mass * (
                    _capped(baseline_end.dhw_temperature, "dhw")
                    - _capped(optimized_end.dhw_temperature, "dhw")
                )
                electrical += dhw_gap / cop_dhw - dhw_gap / cop
        return electrical * refill_price

    def _compute_baseline_power(
        self,
        initial_state: ThermalState,
        outdoor_temps: np.ndarray,
        wind_speeds: np.ndarray,
        precipitation: np.ndarray,
        solar_radiation: np.ndarray,
        dt: float,
        comfort_targets: np.ndarray | None = None,
        external_heat_kw: np.ndarray | None = None,
    ) -> tuple[np.ndarray, ThermalState]:
        """Simulate a conventional thermostat following the comfort schedule.

        This is the reference the reported savings are measured against, so it
        has to behave like a real thermostat in the same physics as the
        optimized schedule. Anything it wastes is reported to the user as a
        saving, so the controller is built from the model's own steady state
        rather than from a heuristic.

        The thermostat tracks the same per-step comfort targets the plan is
        held to. Holding the flat ``target_temp`` around the clock instead
        made the reference heat to the *day* temperature all night, and a
        configured night setback was then booked as optimizer savings — value
        any ordinary programmable thermostat delivers.

        Heat is delivered to the slab and only reaches the room on the
        following step, so power is set by a cascade: the slab is driven to the
        temperature that sustains the setpoint, with a proportional term that
        pulls the room back if it has drifted.

        Returns the power schedule and the final state, the latter so the
        caller can account for the thermal energy left stored at the end of the
        horizon.
        """
        n_steps = len(outdoor_temps)
        p = self.model.params

        baseline_power = np.zeros(n_steps)
        state = initial_state

        for i in range(n_steps):
            target = (
                float(comfort_targets[i])
                if comfort_targets is not None and i < len(comfort_targets)
                else self.config.target_temp
            )
            if p.two_zone_enabled:
                required_thermal = self._baseline_thermal_demand_two_zone(
                    state, target, outdoor_temps[i], wind_speeds[i],
                    precipitation[i], solar_radiation[i], dt,
                )
            else:
                required_thermal = self._baseline_thermal_demand_single(
                    state, target, outdoor_temps[i], wind_speeds[i],
                    precipitation[i], solar_radiation[i], dt,
                )

            # A thermostat's house receives a furnace burn too, and its
            # sensor sees the warmth: the reference backs off by the free
            # heat, or the burn would be booked as optimizer savings.
            ext_i = (
                float(external_heat_kw[i])
                if external_heat_kw is not None and i < len(external_heat_kw)
                else 0.0
            )
            if (
                p.two_tank_modelled
                and state.wood_tank_temperature is not None
            ):
                # With the wood tank modelled, the 4-way valve covers part
                # of the draw from the wood side; the reference backs its
                # electric demand off by that share, computed with the SAME
                # wood_share law the plan's physics uses so the two cannot
                # drift. Subtracting ext_i afterwards as well is deliberate
                # double counting in the conservative direction: the
                # baseline can only get cheaper, so reported savings are
                # understated, never inflated.
                u_up = self.model.effective_heat_loss_coefficient(
                    p.upper_floor_heat_loss, wind_speeds[i], precipitation[i]
                )
                u_lo = self.model.effective_heat_loss_coefficient(
                    p.lower_floor_heat_loss_learned,
                    wind_speeds[i] * 0.5, precipitation[i] * 0.5,
                )
                design_power = p.max_electrical_power * max(p.cop_nominal, 1.0)
                flow_set = mixing_valve.flow_setpoint(
                    target_temp=p.mixing_valve_target or p.comfort_ceiling,
                    outdoor_temp=float(outdoor_temps[i]),
                    heat_loss_coefficient=u_up + u_lo,
                    emitter_ua=design_power / max(p.emitter_design_delta_t, 1.0),
                )
                w_i = wood_share(
                    state.wood_tank_temperature,
                    state.buffer_tank_temperature,
                    flow_set,
                    min(
                        state.upper_floor_temperature, state.slab_temperature
                    ),
                )
                required_thermal *= 1.0 - w_i
            required_thermal = max(0.0, required_thermal - ext_i)

            cop = self.model.compute_cop(outdoor_temps[i])
            # No lower clamp to ``min_electrical_power``: a pump that cannot
            # modulate that low cycles on and off, and over a step the average
            # power is what determines energy use. Forcing the baseline up to
            # the minimum modulation power made it burn a constant
            # min_power * 24 h per day even when the house needed no heat at
            # all, which inflated both the baseline and the savings.
            power = float(
                np.clip(required_thermal / cop, 0.0, p.max_electrical_power)
            )
            baseline_power[i] = power

            state = self.model.simulate_step(
                state, power, outdoor_temps[i],
                wind_speeds[i], precipitation[i], solar_radiation[i], dt,
                external_heat_kw=ext_i,
            )

        return baseline_power, state

    def _baseline_thermal_demand_single(
        self,
        state: ThermalState,
        target: float,
        outdoor_temp: float,
        wind_speed: float,
        precipitation: float,
        solar_radiation: float,
        dt: float,
    ) -> float:
        """Thermal power a thermostat needs this step in the single-zone model."""
        p = self.model.params
        k_slab = max(p.slab_heat_transfer, 1e-6)

        u_eff = self.model.effective_heat_loss_coefficient(
            p.heat_loss_coefficient, wind_speed, precipitation
        )
        q_solar = self.model.compute_solar_gain(solar_radiation)

        # Thermal power the room needs to sit at the setpoint.
        q_demand = u_eff * (target - outdoor_temp) - p.internal_gains - q_solar
        # Slab temperature that delivers exactly that, plus a pull-back term
        # if the room has drifted away from the setpoint.
        slab_target = (
            target
            + max(0.0, q_demand) / k_slab
            + 2.0 * (target - state.room_temperature)
        )

        q_slab_to_room = k_slab * (state.slab_temperature - state.room_temperature)
        # Replace what the slab gives up to the room, and move the slab to
        # where it needs to be.
        return q_slab_to_room + p.slab_thermal_mass * (
            slab_target - state.slab_temperature
        ) / dt

    def _baseline_thermal_demand_two_zone(
        self,
        state: ThermalState,
        target: float,
        outdoor_temp: float,
        wind_speed: float,
        precipitation: float,
        solar_radiation: float,
        dt: float,
    ) -> float:
        """Thermal power a thermostat needs this step in the two-zone model.

        The upper floor is fed directly by radiators while the lower floor is
        fed through the slab, and the split between them is fixed by
        ``radiator_power_fraction``. One control cannot hold both zones exactly,
        which is also true of the real system being modelled, so the demand of
        the two zones is summed the way an outdoor-reset curve on a single
        mixing valve would.
        """
        p = self.model.params
        k_slab = max(p.slab_heat_transfer, 1e-6)

        u_upper = self.model.effective_heat_loss_coefficient(
            p.upper_floor_heat_loss, wind_speed, precipitation
        )
        u_lower = self.model.effective_heat_loss_coefficient(
            p.lower_floor_heat_loss_learned, wind_speed * 0.5, precipitation * 0.5
        )
        q_solar_upper, q_solar_lower = self.model.solar_gain_per_zone(solar_radiation)
        area_ratio = p.upper_floor_area_ratio
        q_int_upper = p.internal_gains * area_ratio
        q_int_lower = p.internal_gains * (1.0 - area_ratio)

        t_upper = state.upper_floor_temperature
        t_lower = state.lower_floor_temperature
        q_inter = p.inter_zone_transfer * (t_lower - t_upper)

        # Radiators reach the upper floor within the step, so its demand is
        # met directly, including the pull-back on any drift.
        q_upper = (
            u_upper * (target - outdoor_temp)
            - q_solar_upper
            - q_int_upper
            - q_inter
            + p.upper_floor_thermal_mass * (target - t_upper) / dt
        )
        q_upper = max(0.0, q_upper)

        # The lower floor is heated through the slab, so drive the slab to the
        # temperature that sustains it and charge it over this step.
        q_lower = (
            u_lower * (target - outdoor_temp) - q_solar_lower - q_int_lower + q_inter
        )
        slab_target = (
            target + max(0.0, q_lower) / k_slab + 2.0 * (target - t_lower)
        )
        q_slab_to_lower = k_slab * (state.slab_temperature - t_lower)
        q_floor = q_slab_to_lower + p.slab_thermal_mass * (
            slab_target - state.slab_temperature
        ) / dt
        q_floor = max(0.0, q_floor)

        # The heat pump makes one water temperature and the split between
        # radiators and floor is fixed, so total output is sized to total
        # demand the way an outdoor-reset curve does. The zones then settle at
        # slightly different temperatures, which is what the real system does
        # too, and inter-zone transfer pulls them back together.
        thermal = q_upper + q_floor

        # Replace what the buffer tank leaks so it does not sag over the day.
        thermal += p.buffer_tank_heat_loss_coefficient * max(
            0.0, state.buffer_tank_temperature - 20.0
        )
        return thermal

    def _stored_thermal_energy(
        self,
        state: ThermalState,
        include_dhw: bool = False,
        caps: dict[str, float] | None = None,
    ) -> float:
        """Thermal energy stored in the building mass (and optionally the tank).

        Used to settle up at the end of the horizon. The optimizer is free to
        run the house and tank down towards the end of the window because
        nothing past the horizon is penalised, and without this correction that
        borrowed heat is reported as a saving even though it has to be paid back
        in the next window.

        ``caps`` limits each store to the temperature above which the heat is of
        no further use, so that passive overheating is not mistaken for charge.
        """
        p = self.model.params
        caps = caps or {}

        def _t(value: float, cap_key: str) -> float:
            cap = caps.get(cap_key)
            return min(value, cap) if cap is not None else value

        if p.two_zone_enabled:
            stored = (
                p.slab_thermal_mass * _t(state.slab_temperature, "slab")
                + p.upper_floor_thermal_mass
                * _t(state.upper_floor_temperature, "room")
                + p.lower_floor_thermal_mass
                * _t(state.lower_floor_temperature, "room")
                + p.buffer_tank_thermal_mass
                * _t(state.buffer_tank_temperature, "buffer")
            )
            if (
                p.two_tank_modelled
                and state.wood_tank_temperature is not None
            ):
                # Symmetric with the buffer: heat still in the wood tank at
                # the horizon end is heat the next window does not buy.
                stored += p.wood_tank_thermal_mass * _t(
                    state.wood_tank_temperature, "wood"
                )
        else:
            stored = (
                p.slab_thermal_mass * _t(state.slab_temperature, "slab")
                + p.room_thermal_mass * _t(state.room_temperature, "room")
            )
        if include_dhw:
            stored += p.dhw_tank_thermal_mass * _t(state.dhw_temperature, "dhw")
        return float(stored)

    def _replay_end_state(
        self,
        initial_state: ThermalState,
        power_schedule: np.ndarray,
        outdoor_temps: np.ndarray,
        wind_speeds: np.ndarray,
        precipitation: np.ndarray,
        solar_radiation: np.ndarray,
        dt: float,
        external_heat_kw: np.ndarray | None = None,
        valve_targets: np.ndarray | None = None,
    ) -> ThermalState:
        """Final state after running a power schedule through the model.

        The optimizer's own trajectories only carry the room and slab, so a
        state rebuilt from them silently falls back to defaults for the zone and
        buffer temperatures. Replaying the schedule keeps every part of the
        state consistent with the model in both single and two-zone mode.
        """
        state = initial_state
        for i in range(len(power_schedule)):
            state = self.model.simulate_step(
                state, float(power_schedule[i]), outdoor_temps[i],
                wind_speeds[i], precipitation[i], solar_radiation[i], dt,
                external_heat_kw=(
                    float(external_heat_kw[i])
                    if external_heat_kw is not None
                    else 0.0
                ),
                valve_target=(
                    float(valve_targets[i])
                    if valve_targets is not None
                    else None
                ),
            )
        return state

    def _power_to_setpoints(
        self,
        power_schedule: np.ndarray,
        room_temps: np.ndarray,
        outdoor_temps: np.ndarray,
    ) -> list[float]:
        """Convert power schedule to equivalent temperature setpoints."""
        setpoints: list[float] = []
        p_range = (
            self.model.params.max_electrical_power
            - self.model.params.min_electrical_power
        )

        for power, _room_t in zip(power_schedule, room_temps):
            p_norm = (
                power - self.model.params.min_electrical_power
            ) / max(p_range, 0.1)
            p_norm = np.clip(p_norm, 0, 1)
            displacement = p_norm * (self.config.max_temp - self.config.min_temp)
            setpoint = self.config.min_temp + displacement
            setpoints.append(round(float(setpoint), 1))

        return setpoints

    def _power_to_displace_schedule(
        self,
        power_schedule: np.ndarray,
        outdoor_temps: np.ndarray,
        forecast_analysis: dict[str, Any] | None = None,
    ) -> list[float]:
        """Map optimized power to ECL110 displace values with PID-aware smoothing."""
        p = self.model.params
        p_min = p.min_electrical_power
        p_max = p.max_electrical_power
        d_min = p.ecl110_displace_min
        d_max = p.ecl110_displace_max

        solar_reduction = (forecast_analysis or {}).get("solar_reduction_factor", 1.0)
        wind_factor = (forecast_analysis or {}).get("wind_anticipation_factor", 1.0)
        rain_factor = (forecast_analysis or {}).get("rain_anticipation_factor", 1.0)

        displacement_bias = (
            (wind_factor - 1.0) * 3.0
            + (rain_factor - 1.0) * 4.0
            - (1.0 - solar_reduction) * 5.0
        )

        raw_displace: list[float] = []
        for i, power in enumerate(power_schedule):
            p_norm = (power - p_min) / max(p_max - p_min, 0.1)
            p_norm = float(np.clip(p_norm, 0.0, 1.0))
            displace = d_min + p_norm * (d_max - d_min)

            if i < int(max(1, 8 / self.config.dt_hours)):
                displace += displacement_bias

            out_t = outdoor_temps[i] if i < len(outdoor_temps) else outdoor_temps[-1]
            if out_t < 0:
                displace += min(2.0, abs(out_t) * 0.08)

            raw_displace.append(float(np.clip(displace, d_min, d_max)))

        tau = max(0.1, p.ecl110_pid_time_constant_hours)
        alpha = float(np.clip(self.config.dt_hours / tau, 0.0, 1.0))
        effective = 0.0
        filtered: list[float] = []
        for cmd in raw_displace:
            effective = effective + alpha * (cmd - effective)
            filtered.append(round(float(np.clip(effective, d_min, d_max)), 1))

        return filtered

    def _power_to_heat_pump_schedule(
        self,
        space_power_schedule: np.ndarray,
        dhw_power_schedule: np.ndarray | None = None,
    ) -> list[bool]:
        """ON/OFF supply-enable decisions: ON when either circuit clears the
        activation threshold."""
        p = self.model.params
        on_threshold = max(0.1, p.min_electrical_power * 0.5)
        space = np.asarray(space_power_schedule, dtype=float)
        dhw = (
            np.zeros_like(space)
            if dhw_power_schedule is None
            else np.asarray(dhw_power_schedule, dtype=float)
        )
        return (np.maximum(space, dhw) >= on_threshold).tolist()

    def _idle_action(self) -> dict[str, Any]:
        """The do-nothing action: shared by the empty-plan branch and the
        pre-horizon clamp so the two fallbacks cannot drift apart."""
        return {
            "power": self.model.params.min_electrical_power,
            "setpoint": self.config.target_temp,
            "mode": "idle",
            "price": 0.0,
            "heat_pump_on": False,
            "displace_value": 0.0,
            "space_reason": None,
            "dhw_reason": None,
        }

    def get_current_action(
        self, result: OptimizationResult, current_time: datetime
    ) -> dict[str, Any]:
        """Get the current recommended action from the optimization result."""
        if not result.timestamps:
            return self._idle_action()

        if current_time < result.timestamps[0]:
            # A pre-horizon clock (NTP step back, restored stale plan) would
            # fall through the loop below to the LAST step — the 24h-ahead
            # slot where terminal-value charging lives. Clamp to step 0 only
            # while the gap is within one step length; beyond that the plan
            # says nothing about now, so idle like the empty-plan branch.
            if len(result.timestamps) > 1:
                step = result.timestamps[1] - result.timestamps[0]
            else:
                step = timedelta(minutes=15)
            if result.timestamps[0] - current_time > step:
                return self._idle_action()
            i = 0
        else:
            # Find the current time step
            for i, ts in enumerate(result.timestamps):
                if i + 1 < len(result.timestamps):
                    if ts <= current_time < result.timestamps[i + 1]:
                        break
                else:
                    i = len(result.timestamps) - 1
                    break

        power = result.power_schedule[i]
        setpoint = result.optimal_setpoints[i]
        price = result.prices[i]
        displace_value = (
            result.displace_schedule[i]
            if result.displace_schedule and i < len(result.displace_schedule)
            else 0.0
        )
        heat_pump_on = (
            result.heat_pump_on_schedule[i]
            if result.heat_pump_on_schedule and i < len(result.heat_pump_on_schedule)
            else power > max(0.1, self.model.params.min_electrical_power * 0.5)
        )

        p_range = (
            self.model.params.max_electrical_power
            - self.model.params.min_electrical_power
        )
        p_norm = (
            power - self.model.params.min_electrical_power
        ) / max(p_range, 0.1)

        if p_norm < 0.1:
            mode = "off"
        elif p_norm < 0.4:
            mode = "eco"
        elif p_norm < 0.7:
            mode = "normal"
        elif p_norm < 0.9:
            mode = "pre_heat"
        else:
            mode = "boost"

        action = {
            "power": round(power, 2),
            "setpoint": setpoint,
            "mode": mode,
            "price": round(price, 4),
            "power_normalized": round(p_norm, 2),
            "heat_pump_on": bool(heat_pump_on),
            "displace_value": float(displace_value),
            # T6: the reason codes for THIS step ride with the action, so
            # the settlement can tag every booked SEK with why the plan
            # wanted that draw. This method already owns the one search for
            # the step covering now; re-deriving the index at settle time
            # would be a second chance to disagree about which step ran.
            "space_reason": (
                result.space_reasons[i]
                if result.space_reasons and i < len(result.space_reasons)
                else None
            ),
            "dhw_reason": (
                result.dhw_reasons[i]
                if result.dhw_reasons and i < len(result.dhw_reasons)
                else None
            ),
        }

        # The valve target for *this* step, when a hold schedule is in force.
        # It rides with the rest of the current action rather than being
        # re-derived by the actuator: this method already owns the one search
        # for the step covering now, and a second copy of that search is a
        # second chance to disagree about which step is current.
        if result.valve_target_schedule and i < len(result.valve_target_schedule):
            action["valve_target"] = round(
                float(result.valve_target_schedule[i]), 1
            )

        # Add zone-specific setpoints if available
        if result.upper_setpoints and i < len(result.upper_setpoints):
            action["upper_setpoint"] = result.upper_setpoints[i]
        if result.lower_setpoints and i < len(result.lower_setpoints):
            action["lower_setpoint"] = result.lower_setpoints[i]

        # Add solar gain info
        if result.solar_gain_trajectory and i < len(result.solar_gain_trajectory):
            action["solar_gain_kw"] = round(result.solar_gain_trajectory[i], 3)

        # Add DHW info
        if result.dhw_power_schedule and i < len(result.dhw_power_schedule):
            dhw_power = result.dhw_power_schedule[i]
            action["dhw_power"] = round(dhw_power, 2)
            action["dhw_heating_active"] = dhw_power > 0.1
        if result.dhw_temp_trajectory and i < len(result.dhw_temp_trajectory):
            action["dhw_temperature"] = round(result.dhw_temp_trajectory[i], 1)
        if result.predictive_info.get("dhw_target_temperature") is not None:
            action["dhw_target_temperature"] = result.predictive_info.get(
                "dhw_target_temperature"
            )

        # Add predictive info
        if result.predictive_info:
            action["solar_reduction_factor"] = round(
                result.predictive_info.get("solar_reduction_factor", 1.0), 2
            )
            action["wind_anticipation_factor"] = round(
                result.predictive_info.get("wind_anticipation_factor", 1.0), 2
            )
            action["pre_heat_urgency"] = round(
                result.predictive_info.get("pre_heat_urgency", 0.0), 2
            )

        return action