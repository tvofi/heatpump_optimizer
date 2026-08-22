"""Model Predictive Control optimizer for heat pump cost minimization.

This module implements a TRUE predictive MPC optimizer that determines the
optimal heat pump power schedule over a 24-hour horizon to minimize electricity
costs while maintaining indoor temperature and DHW within comfort bounds.

KEY PREDICTIVE FEATURES (anticipatory, not just reactive):

1. **Solar Anticipation**: If high solar radiation is forecasted in next 12-24h,
   REDUCE current slab pre-heating because solar will provide free heat later.
   This saves money by not pre-heating what the sun will heat for free.

2. **Wind/Rain Anticipation**: If high wind/rain is forecasted, INCREASE current
   pre-heating during cheap electricity periods to buffer against upcoming
   higher heat loss. The slab thermal mass stores this heat.

3. **DHW Co-optimization**: Coordinate space heating and DHW heating to use
   the heat pump capacity optimally. DHW is heated during cheap electricity
   when possible, subject to minimum temperature constraints.

The optimization problem is:

    minimize   Σ price[k] * (P_space[k] + P_dhw[k]) * dt
             + comfort_weight * Σ penalty_space[k]
             + dhw_weight * Σ penalty_dhw[k]
    subject to T_min ≤ T_room[k] ≤ T_max  (soft constraint)
               T_dhw[k] ≥ T_dhw_min  (hard-ish constraint)
               P_space[k] + P_dhw[k] ≤ P_max  (capacity constraint)
               P_min ≤ P_space[k], P_dhw[k] ≤ P_max
               Thermal dynamics (two-zone + DHW state model)
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

import numpy as np
from scipy.optimize import linprog, minimize

from .thermal_model import (
    DHW_AMBIENT_TEMP,
    ThermalModel,
    ThermalParameters,
    ThermalState,
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


def capacity_penalty(
    total_power: np.ndarray,
    baseline_load: np.ndarray,
    threshold_kw: float,
    price_per_kw: float,
    window_minutes: int,
    dt_hours: float,
) -> float:
    """Cost of the new monthly peak this plan would set.

    Only the single largest metering-window excess counts. Charging per hour
    would price a whole month's tariff into every busy hour of one day.
    """
    if price_per_kw <= 0:
        return 0.0
    house = np.asarray(total_power, dtype=float) + np.asarray(
        baseline_load, dtype=float
    )
    if house.size == 0:
        return 0.0
    per_window = max(1, int(round(window_minutes / max(dt_hours * 60.0, 1e-6))))
    if per_window > 1:
        n_full = house.size // per_window
        if n_full:
            windows = house[: n_full * per_window].reshape(n_full, per_window).mean(
                axis=1
            )
            tail = house[n_full * per_window :]
            if tail.size:
                windows = np.append(windows, tail.mean())
        else:
            windows = np.array([house.mean()])
    else:
        windows = house
    excess = float(np.max(windows) - threshold_kw)
    return price_per_kw * max(0.0, excess)


# ---------------------------------------------------------------------------
# Plan reason codes (item 16)
# ---------------------------------------------------------------------------

REASON_COMFORT_FLOOR = "comfort_floor"
REASON_CHEAP_PRICE = "cheap_price"
REASON_PREHEAT_WEATHER = "preheat_weather"
REASON_TERMINAL_VALUE = "terminal_value"
REASON_SOLAR_SURPLUS = "solar_surplus"
REASON_RECOVERY = "recovery"
REASON_DHW_WINDOW = "dhw_window"
REASON_DHW_READY = "dhw_ready"
REASON_DHW_PREHEAT = "dhw_preheat"
REASON_LEGIONELLA = "legionella"
REASON_PEAK_AVOIDANCE = "peak_avoidance"
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
    cycling_cost: float = 0.0

    # --- Capacity tariff (item 8) --------------------------------------
    #: Currency per kW of new monthly peak, already divided by the number of
    #: peaks the DSO averages. Zero disables the term entirely.
    peak_price_per_kw: float = 0.0
    #: The level above which a new peak would raise the bill, in kW.
    peak_threshold_kw: float = 0.0
    #: Metering window of the tariff, in minutes.
    peak_window_minutes: int = 60
    #: Whole-house load excluding the heat pump, per step, in kW.
    baseline_load_kw: Any = None

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

    # ------------------------------------------------------------------
    # Shared cost terms
    # ------------------------------------------------------------------

    def _grid_terms(self, n_steps: int, dt: float):
        """Closures for the cycling and capacity-tariff penalties.

        Both are shared between the space-only and DHW paths. Keeping them in
        one place is not just tidiness: the previous divergence between the two
        objectives meant that simply enabling hot water changed the space
        heating objective, which is a class of bug worth designing out.
        """
        cfg = self.config
        p_max = self.model.params.max_electrical_power
        baseline = cfg.baseline_load_array(n_steps)

        def cycling(power: np.ndarray) -> float:
            return cycling_penalty(power, cfg.cycling_cost, p_max)

        def capacity(total_power: np.ndarray) -> float:
            return capacity_penalty(
                total_power,
                baseline,
                cfg.peak_threshold_kw,
                cfg.peak_price_per_kw,
                cfg.peak_window_minutes,
                dt,
            )

        return cycling, capacity, baseline

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
        """Analyze the full 24-hour forecast for anticipatory control signals.

        This is the core of the PREDICTIVE optimization — looking ahead to
        determine how current actions should be modified.

        Returns a dict with anticipatory signals:
        - future_solar_energy: total forecasted solar gain (kWh) over horizon
        - solar_peak_hours: indices of high solar radiation periods
        - future_wind_loss_factor: weighted future wind heat loss increase
        - future_rain_loss_factor: weighted future rain heat loss increase
        - pre_heat_urgency: 0-1 signal indicating how much to pre-heat now
        - solar_savings_potential: how much the sun will heat for free
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
    ) -> OptimizationResult:
        """Run the MPC optimization with predictive weather anticipation.

        This is the CORE of true MPC: the optimizer uses the FULL 24-hour
        forecast trajectory (solar, wind, rain, temperature) to make decisions
        about CURRENT actions. It doesn't just react to current conditions.

        Key anticipatory behaviors:
        - Reduces pre-heating before forecasted sunny periods
        - Increases pre-heating before forecasted windy/rainy periods
        - Coordinates DHW heating with space heating and electricity prices

        ``prices`` are *marginal* prices: where PV surplus exists the caller
        substitutes the export compensation, because that is what consuming a
        kWh actually costs there. ``price_known`` marks which steps rest on
        published market data rather than on the learned diurnal prior, and
        ``pv_surplus`` is carried through for reporting and reason codes.
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
        self._pv_surplus = pv_surplus

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

        p_min = self.model.params.min_electrical_power
        p_max = self.model.params.max_electrical_power
        two_zone = self.model.params.two_zone_enabled
        dhw_enabled = self.model.params.dhw_enabled

        # Compute comfort targets for each time step
        comfort_targets = np.array([
            self.config.get_comfort_temp(
                (start_time + timedelta(hours=i * dt)).hour
                + (start_time + timedelta(hours=i * dt)).minute / 60.0
            )
            for i in range(n_steps)
        ])

        temp_min_bounds = np.array([
            self.config.get_temp_bounds(
                (start_time + timedelta(hours=i * dt)).hour
                + (start_time + timedelta(hours=i * dt)).minute / 60.0
            )[0]
            for i in range(n_steps)
        ])

        temp_max_bounds = np.array([
            self.config.get_temp_bounds(
                (start_time + timedelta(hours=i * dt)).hour
                + (start_time + timedelta(hours=i * dt)).minute / 60.0
            )[1]
            for i in range(n_steps)
        ])

        # Hours for each time step (for DHW draw pattern)
        step_hours = np.array([
            ((start_time + timedelta(hours=i * dt)).hour
             + (start_time + timedelta(hours=i * dt)).minute / 60.0)
            for i in range(n_steps)
        ])

        # --- Precompute per-step solar gains for the cost function ---
        solar_gains_per_step = np.array([
            self.model.compute_solar_gain(sr) for sr in solar_radiation
        ])

        # --- Precompute per-step effective heat loss (using FORECAST data) ---
        # This is critical: use forecasted wind and rain at EACH future step
        forecast_heat_loss_factors = np.array([
            self.model.effective_heat_loss_coefficient(
                self.model.params.heat_loss_coefficient,
                wind_speeds[i],
                precipitation[i],
            ) / max(self.model.params.heat_loss_coefficient, 0.001)
            for i in range(n_steps)
        ])

        if dhw_enabled:
            result = self._optimize_with_dhw(
                initial_state, prices, outdoor_temps, wind_speeds,
                precipitation, solar_radiation, start_time, n_steps, dt,
                comfort_targets, temp_min_bounds, temp_max_bounds,
                step_hours, solar_gains_per_step, forecast_heat_loss_factors,
                forecast_analysis, t_start,
            )
        else:
            result = self._optimize_space_only(
                initial_state, prices, outdoor_temps, wind_speeds,
                precipitation, solar_radiation, start_time, n_steps, dt,
                comfort_targets, temp_min_bounds, temp_max_bounds,
                solar_gains_per_step, forecast_heat_loss_factors,
                forecast_analysis, t_start,
            )

        existing_info = result.predictive_info if result.predictive_info else {}
        result.predictive_info = {**forecast_analysis, **existing_info}
        return result

    def _optimize_space_only(
        self,
        initial_state: ThermalState,
        prices: np.ndarray,
        outdoor_temps: np.ndarray,
        wind_speeds: np.ndarray,
        precipitation: np.ndarray,
        solar_radiation: np.ndarray,
        start_time: datetime,
        n_steps: int,
        dt: float,
        comfort_targets: np.ndarray,
        temp_min_bounds: np.ndarray,
        temp_max_bounds: np.ndarray,
        solar_gains_per_step: np.ndarray,
        forecast_heat_loss_factors: np.ndarray,
        forecast_analysis: dict,
        t_start: float,
    ) -> OptimizationResult:
        """Optimize space heating only (no DHW)."""
        import time

        p_min = self.model.params.min_electrical_power
        p_max = self.model.params.max_electrical_power
        two_zone = self.model.params.two_zone_enabled

        # --- Warm-start shaping --------------------------------------------
        # A cheap forecast-aware nudge for the *initial guess* only: start the
        # solver lower where sun is coming and higher where the weather is
        # about to turn, so L-BFGS-B begins near the shape of the answer.
        #
        # These weights used to scale the comfort-violation penalty as well,
        # which discounted a real breach of the user's minimum temperature
        # because the sun might come out later. That is backwards: if the sun
        # does arrive, the simulated trajectory is not cold and no penalty
        # arises anyway, so the discount could only ever buy under-heating.
        # The penalty now means exactly what it says.
        anticipatory_weights = np.ones(n_steps)
        for i in range(n_steps):
            lookahead_end = min(i + int(8 / dt), n_steps)
            if lookahead_end > i:
                future_solar = np.mean(solar_gains_per_step[i:lookahead_end])
                if future_solar > 0.5:  # > 0.5 kW solar gain is significant
                    anticipatory_weights[i] *= max(0.6, 1.0 - future_solar * 0.3)

                future_loss_factor = np.mean(
                    forecast_heat_loss_factors[i:lookahead_end]
                )
                if future_loss_factor > 1.1:
                    anticipatory_weights[i] *= min(1.5, future_loss_factor)

        # How far the user is willing to let the house drift below target.
        # The pull-to-target term is normalised by this so that widening the
        # allowed band actually buys cheaper operation instead of being
        # overwhelmed by a fixed quadratic penalty. With a wide band (target
        # 21, min 17) the optimizer is free to coast; narrowing the band makes
        # it hold the setpoint more tightly.
        comfort_band = np.maximum(comfort_targets - temp_min_bounds, 1.0)

        # --- Terminal cost -------------------------------------------------
        # Nothing beyond the horizon is scored, so without a terminal term the
        # optimizer always dumps the last couple of hours: it coasts the house
        # down because the resulting cold never shows up in the objective. That
        # both breaches the comfort floor at the tail of the plan and reports a
        # saving that was really borrowed heat. Price the end-of-horizon
        # shortfall using the same reference the savings settle-up uses, so the
        # plan and the reported savings agree.
        _caps = self._settlement_caps(outdoor_temps)
        _refill_price = float(np.percentile(prices, 25))
        _cop_end = self.model.compute_cop(float(outdoor_temps[-1]))
        _mp = self.model.params
        if _mp.two_zone_enabled:
            _stores = (
                (_mp.upper_floor_thermal_mass, "upper", _caps["room"]),
                (_mp.lower_floor_thermal_mass, "lower", _caps["room"]),
                (_mp.slab_thermal_mass, "slab", _caps["slab"]),
            )
        else:
            _stores = (
                (_mp.room_thermal_mass, "room", _caps["room"]),
                (_mp.slab_thermal_mass, "slab", _caps["slab"]),
            )

        def _ends(room_temps, slab_temps, upper_temps, lower_temps):
            return {
                "room": float(room_temps[-1]),
                "slab": float(slab_temps[-1]),
                "upper": float(upper_temps[-1]),
                "lower": float(lower_temps[-1]),
            }

        def terminal_cost(ends: dict[str, float]) -> float:
            deficit = 0.0
            for mass, name, cap in _stores:
                deficit += mass * max(0.0, cap - ends[name])
            return _refill_price * deficit / max(_cop_end, 1e-6)

        _cycling, _capacity, _baseline_load = self._grid_terms(n_steps, dt)

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
                )
            )

            # Electricity cost
            energy_cost = (
                np.sum(prices * power_schedule * dt) * self.config.price_weight
            )

            if two_zone:
                upper_t = upper_temps[1:]
                lower_t = lower_temps[1:]

                undershoot_u = np.maximum(0, temp_min_bounds - upper_t)
                overshoot_u = np.maximum(0, upper_t - temp_max_bounds)
                undershoot_l = np.maximum(0, temp_min_bounds - lower_t)
                overshoot_l = np.maximum(0, lower_t - temp_max_bounds)

                # Weight comfort penalties by anticipatory weights
                # During periods before sunny weather, allow slightly lower temps
                # Averaged over the two zones, not summed. Summing made a
                # two-zone house behave as if ``comfort_weight`` were set twice
                # as high as configured, so it hugged the setpoint and gave up
                # most of the available savings.
                penalty = 0.5 * self.config.comfort_weight * (
                    np.sum(undershoot_u ** 2) * 10.0
                    + np.sum(overshoot_u ** 2) * 5.0
                    + np.sum(undershoot_l ** 2) * 10.0
                    + np.sum(overshoot_l ** 2) * 5.0
                    + (np.sum(undershoot_u) + np.sum(undershoot_l))
                    * _COMFORT_FLOOR_L1
                )

                comfort_dev_u = upper_t - comfort_targets
                comfort_dev_l = lower_t - comfort_targets
                comfort_cost = 0.025 * self.config.comfort_weight * (
                    np.sum((comfort_dev_u / comfort_band) ** 2)
                    + np.sum((comfort_dev_l / comfort_band) ** 2)
                )
            else:
                room_t = room_temps[1:]
                undershoot = np.maximum(0, temp_min_bounds - room_t)
                overshoot = np.maximum(0, room_t - temp_max_bounds)

                penalty = self.config.comfort_weight * (
                    np.sum(undershoot ** 2) * 10.0
                    + np.sum(overshoot ** 2) * 5.0
                    + np.sum(undershoot) * _COMFORT_FLOOR_L1
                )

                comfort_deviation = room_t - comfort_targets
                comfort_cost = 0.05 * self.config.comfort_weight * np.sum(
                    (comfort_deviation / comfort_band) ** 2
                )

            # Smoothness penalty
            if len(power_schedule) > 1:
                smoothness = 0.01 * np.sum(np.diff(power_schedule) ** 2)
            else:
                smoothness = 0.0

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
                energy_cost + penalty + comfort_cost + smoothness
                + _cycling(power_schedule)
                + _capacity(power_schedule)
                + terminal_cost(
                    _ends(room_temps, slab_temps, upper_temps, lower_temps)
                )
            )

        # Initial guess: smart initialization considering forecasts
        price_normalized = prices / (np.mean(prices) + 1e-6)
        initial_power = p_max * np.clip(1.5 - price_normalized, 0.2, 1.0)

        # Apply predictive adjustments to initial guess
        for i in range(n_steps):
            # Reduce power before solar periods
            initial_power[i] *= anticipatory_weights[i]

        initial_power = np.clip(initial_power, p_min, p_max)
        # A heat pump can be off. min_electrical_power is the lowest it can
        # modulate to while running, not a floor it must burn every step, so
        # allow 0 and read sub-minimum values as duty cycling within the step.
        bounds = [(0.0, p_max)] * n_steps

        # Multiple starting points: the smooth price-weighted guess above, a
        # bang-bang schedule that buys the cheapest steps first, and a flat
        # schedule. See _multi_start_minimize for why one guess is not enough.
        baseline_guess, _ = self._compute_baseline_power(
            initial_state, outdoor_temps, wind_speeds, precipitation,
            solar_radiation, dt,
        )
        baseline_energy = float(np.sum(baseline_guess) * dt)
        starts = [
            initial_power,
            _price_ranked_start(prices, baseline_energy, p_max, dt),
            np.clip(baseline_guess, 0.0, p_max),
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
            )
        )

        solar_gains = [self.model.compute_solar_gain(sr) for sr in solar_radiation]

        # Compute baseline cost
        baseline_power, baseline_end = self._compute_baseline_power(
            initial_state, outdoor_temps, wind_speeds, precipitation,
            solar_radiation, dt,
        )
        baseline_cost = float(np.sum(prices * baseline_power * dt))
        predicted_cost = float(np.sum(prices * optimal_power * dt))

        optimized_end = self._replay_end_state(
            initial_state, optimal_power, outdoor_temps, wind_speeds,
            precipitation, solar_radiation, dt,
        )
        deferred_cost = self._deferred_energy_cost(
            baseline_end, optimized_end, prices, outdoor_temps,
            caps=self._settlement_caps(outdoor_temps),
        )
        savings = baseline_cost - predicted_cost - deferred_cost

        timestamps = [
            start_time + timedelta(hours=i * dt) for i in range(n_steps)
        ]

        optimal_setpoints = self._power_to_setpoints(
            optimal_power, room_temps[:-1], outdoor_temps
        )
        displace_schedule = self._power_to_displace_schedule(
            optimal_power, outdoor_temps, forecast_analysis
        )
        heat_pump_schedule = self._power_to_heat_pump_schedule(optimal_power)

        upper_setpoints = []
        lower_setpoints = []
        if two_zone:
            for i, power in enumerate(optimal_power):
                p_norm = (power - p_min) / max(p_max - p_min, 0.1)
                p_norm = np.clip(p_norm, 0, 1)
                upper_sp = self.config.min_temp + p_norm * (
                    self.config.max_temp - self.config.min_temp
                )
                lower_sp = self.config.min_temp + p_norm * (
                    self.config.max_temp - self.config.min_temp + 1.0
                )
                upper_setpoints.append(round(float(upper_sp), 1))
                lower_setpoints.append(round(float(lower_sp), 1))

        t_elapsed = (time.monotonic() - t_start) * 1000

        _LOGGER.info(
            "Optimization completed in %.0fms: cost=%.2f, baseline=%.2f, savings=%.1f%%, "
            "solar_reduction=%.2f, wind_factor=%.2f",
            t_elapsed, predicted_cost, baseline_cost,
            _savings_percentage(savings, baseline_cost),
            forecast_analysis["solar_reduction_factor"],
            forecast_analysis["wind_anticipation_factor"],
        )

        grid = self._grid_report(optimal_power, _baseline_load, dt)
        reasons = classify_space_steps(
            optimal_power,
            prices,
            room_temps if not two_zone else upper_temps,
            temp_min_bounds,
            forecast_heat_loss_factors,
            self._pv_surplus,
            n_steps,
        )

        return OptimizationResult(
            power_schedule=optimal_power.tolist(),
            room_temp_trajectory=room_temps.tolist(),
            slab_temp_trajectory=slab_temps.tolist(),
            timestamps=timestamps,
            prices=prices.tolist(),
            outdoor_temps=outdoor_temps.tolist(),
            predicted_cost=predicted_cost,
            baseline_cost=baseline_cost,
            predicted_savings=savings,
            savings_percentage=_savings_percentage(savings, baseline_cost),
            deferred_energy_cost=deferred_cost,
            optimal_setpoints=optimal_setpoints,
            status=status,
            solve_time_ms=t_elapsed,
            displace_schedule=displace_schedule,
            heat_pump_on_schedule=heat_pump_schedule,
            upper_temp_trajectory=upper_temps.tolist(),
            lower_temp_trajectory=lower_temps.tolist(),
            solar_gain_trajectory=solar_gains,
            upper_setpoints=upper_setpoints,
            lower_setpoints=lower_setpoints,
            space_reasons=reasons,
            dhw_reasons=[],
            price_known=self._price_known_list(n_steps),
            projected_peak_kw=grid["peak_kw"],
            peak_cost=grid["peak_cost"],
            compressor_starts=grid["starts"],
            pv_surplus=self._pv_surplus_list(n_steps),
            pv_self_consumed_kwh=self._pv_self_consumed(optimal_power, dt),
        )

    # ------------------------------------------------------------------
    # Reporting helpers shared by both solve paths
    # ------------------------------------------------------------------

    def _grid_report(
        self, total_power: np.ndarray, baseline_load: np.ndarray, dt: float
    ) -> dict[str, Any]:
        """Peak and cycling figures for the solved plan."""
        cfg = self.config
        house = np.asarray(total_power, dtype=float) + baseline_load
        per_window = max(
            1, int(round(cfg.peak_window_minutes / max(dt * 60.0, 1e-6)))
        )
        if per_window > 1 and house.size >= per_window:
            n_full = house.size // per_window
            windows = house[: n_full * per_window].reshape(
                n_full, per_window
            ).mean(axis=1)
        else:
            windows = house
        peak = float(np.max(windows)) if windows.size else 0.0
        return {
            "peak_kw": round(peak, 3),
            "peak_cost": round(
                capacity_penalty(
                    total_power,
                    baseline_load,
                    cfg.peak_threshold_kw,
                    cfg.peak_price_per_kw,
                    cfg.peak_window_minutes,
                    dt,
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
            standby_energy = (
                params.dhw_tank_heat_loss_coefficient
                * max(0.5 * (dhw_setpoint + dhw_min_temp) - 20.0, 0.0)
                * window_hours
            )
            needed_delta = (draw_energy + standby_energy) / c_dhw
            required_ready = float(
                np.clip(dhw_min_temp + needed_delta, dhw_min_temp, dhw_setpoint)
            )
            # The tank must be ready by the END of the step before the window.
            ready_idx = max(0, start_idx - 1)
            ready_temps[ready_idx] = max(ready_temps[ready_idx], required_ready)

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
            if deadline_step < n_steps:
                limit = max(1, min(deadline_step + 1, n_steps))
                idx = int(np.argmin(prices[:limit]))
                ready_temps[idx] = max(ready_temps[idx], params.dhw_legionella_temp)
                legionella_due = True
                legionella_hour = float(hours_mod[idx])
                legionella_step = idx

        max_temp = params.dhw_max_temp
        # How long stored heat actually survives in this tank. The learned
        # cooling rate drives it, so a well-insulated tank is allowed to
        # pre-heat much further ahead than a leaky one.
        max_lead_hours = self.model.dhw_hold_hours()
        requirement = np.maximum(floor_temps, ready_temps)

        # The pump serves DHW as an on/off block, not a trickle, so the planner
        # allocates at a realistic run power and never below the level at which
        # the pump would actually be considered running.
        p_dhw_run = max(0.1, min(p_max * 0.8, p_max))
        min_run_power = min(p_dhw_run, max(0.15, self.model.params.min_electrical_power * 0.6))

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
            prices=prices,
            outdoor_temps=outdoor_temps,
            draw_rates=draw_rates,
            n_steps=n_steps,
            dt=dt,
            p_dhw_max=p_dhw_run,
            c_dhw=c_dhw,
            max_temp=max_temp,
            space_demand=space_demand,
            p_total_max=p_max,
        )

        schedule = self._plan_dhw_cheapest_first(
            initial_temp=initial_state.dhw_temperature,
            requirement=requirement,
            prices=prices,
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
        if getattr(initial_state, "external_heat_active", False):
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
    ) -> np.ndarray | None:
        """Minimum-cost DHW schedule over the whole horizon, as a linear program.

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
                [(0.0, float(energy_max[j])) for j in range(n_steps)]
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
        the hardware can do. Slots below the practical minimum are raised to
        it, but only while the tank stays within its rating — otherwise the
        rounding would boil the plan over.
        """
        plan = np.array(plan, dtype=float)
        weak = np.where((plan > 1e-6) & (plan < min_run_power))[0]
        if weak.size == 0:
            return np.clip(plan, 0.0, p_dhw_max)

        candidate = plan.copy()
        candidate[weak] = min(min_run_power, p_dhw_max)
        temps = self.model.simulate_dhw_only(
            initial_temp=initial_temp,
            dhw_power_schedule=candidate,
            outdoor_temps=outdoor_temps,
            draw_rates=draw_rates,
            dt_hours=dt,
        )
        if float(np.max(temps)) <= max_temp + 0.5:
            return np.clip(candidate, 0.0, p_dhw_max)
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
    ) -> np.ndarray:
        """Greedily top up a DHW plan in the cheapest feasible hours.

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

            candidates = [
                j
                for j in range(max(0, k - max_lead_steps), k + 1)
                if plan[j] < p_dhw_max - 1e-6 and temps[j + 1] < temp_ceiling - 0.1
            ]
            if not candidates:
                candidates = [
                    j
                    for j in range(0, k + 1)
                    if plan[j] < p_dhw_max - 1e-6 and temps[j + 1] < temp_ceiling - 0.1
                ]
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

    def _optimize_with_dhw(
        self,
        initial_state: ThermalState,
        prices: np.ndarray,
        outdoor_temps: np.ndarray,
        wind_speeds: np.ndarray,
        precipitation: np.ndarray,
        solar_radiation: np.ndarray,
        start_time: datetime,
        n_steps: int,
        dt: float,
        comfort_targets: np.ndarray,
        temp_min_bounds: np.ndarray,
        temp_max_bounds: np.ndarray,
        step_hours: np.ndarray,
        solar_gains_per_step: np.ndarray,
        forecast_heat_loss_factors: np.ndarray,
        forecast_analysis: dict,
        t_start: float,
    ) -> OptimizationResult:
        """Optimize coordinated space heating + DHW heating.

        Decision variables: [P_space[0..n-1], P_dhw[0..n-1]]
        The heat pump can allocate power to space OR DHW, with total
        constrained by max capacity.
        """
        import time

        p_min = self.model.params.min_electrical_power
        p_max = self.model.params.max_electrical_power
        two_zone = self.model.params.two_zone_enabled
        dhw_min_temp = self.model.params.dhw_min_temp
        dhw_setpoint = self.model.params.dhw_setpoint

        start_hour = (
            start_time.hour + start_time.minute / 60.0
        )

        # Anticipatory weights (same as space-only)
        anticipatory_weights = np.ones(n_steps)
        for i in range(n_steps):
            lookahead_end = min(i + int(8 / dt), n_steps)
            if lookahead_end > i:
                future_solar = np.mean(solar_gains_per_step[i:lookahead_end])
                if future_solar > 0.5:
                    anticipatory_weights[i] *= max(0.6, 1.0 - future_solar * 0.3)
                future_loss = np.mean(forecast_heat_loss_factors[i:lookahead_end])
                if future_loss > 1.1:
                    anticipatory_weights[i] *= min(1.5, future_loss)

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
        def dhw_cost_of(plan: np.ndarray) -> float:
            return float(np.sum(prices * plan * dt) * self.config.price_weight)

        # How far the user is willing to let the house drift below target.
        # The pull-to-target term is normalised by this so that widening the
        # allowed band actually buys cheaper operation instead of being
        # overwhelmed by a fixed quadratic penalty. With a wide band (target
        # 21, min 17) the optimizer is free to coast; narrowing the band makes
        # it hold the setpoint more tightly.
        comfort_band = np.maximum(comfort_targets - temp_min_bounds, 1.0)

        # --- Terminal cost -------------------------------------------------
        # Nothing beyond the horizon is scored, so without a terminal term the
        # optimizer always dumps the last couple of hours: it coasts the house
        # down because the resulting cold never shows up in the objective. That
        # both breaches the comfort floor at the tail of the plan and reports a
        # saving that was really borrowed heat. Price the end-of-horizon
        # shortfall using the same reference the savings settle-up uses, so the
        # plan and the reported savings agree.
        _caps = self._settlement_caps(outdoor_temps)
        _refill_price = float(np.percentile(prices, 25))
        _cop_end = self.model.compute_cop(float(outdoor_temps[-1]))
        _mp = self.model.params
        if _mp.two_zone_enabled:
            _stores = (
                (_mp.upper_floor_thermal_mass, "upper", _caps["room"]),
                (_mp.lower_floor_thermal_mass, "lower", _caps["room"]),
                (_mp.slab_thermal_mass, "slab", _caps["slab"]),
            )
        else:
            _stores = (
                (_mp.room_thermal_mass, "room", _caps["room"]),
                (_mp.slab_thermal_mass, "slab", _caps["slab"]),
            )

        def _ends(room_temps, slab_temps, upper_temps, lower_temps):
            return {
                "room": float(room_temps[-1]),
                "slab": float(slab_temps[-1]),
                "upper": float(upper_temps[-1]),
                "lower": float(lower_temps[-1]),
            }

        def terminal_cost(ends: dict[str, float]) -> float:
            deficit = 0.0
            for mass, name, cap in _stores:
                deficit += mass * max(0.0, cap - ends[name])
            return _refill_price * deficit / max(_cop_end, 1e-6)

        _cycling, _capacity, _baseline_load = self._grid_terms(n_steps, dt)

        def objective(
            space_power: np.ndarray,
            dhw_energy_cost: float = 0.0,
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
                )
            )

            # --- Electricity cost (total: space + DHW) ---
            energy_cost = (
                np.sum(prices * space_power * dt) * self.config.price_weight
                + dhw_energy_cost
            )

            # --- Space heating comfort penalty ---
            if two_zone:
                upper_t = upper_temps[1:]
                lower_t = lower_temps[1:]
                undershoot_u = np.maximum(0, temp_min_bounds - upper_t)
                overshoot_u = np.maximum(0, upper_t - temp_max_bounds)
                undershoot_l = np.maximum(0, temp_min_bounds - lower_t)
                overshoot_l = np.maximum(0, lower_t - temp_max_bounds)
                # Averaged over the two zones so that ``comfort_weight`` means
                # the same thing as in single-zone mode; see the space-only
                # objective for the reasoning.
                space_penalty = 0.5 * self.config.comfort_weight * (
                    np.sum(undershoot_u ** 2) * 10.0
                    + np.sum(overshoot_u ** 2) * 5.0
                    + np.sum(undershoot_l ** 2) * 10.0
                    + np.sum(overshoot_l ** 2) * 5.0
                    + (np.sum(undershoot_u) + np.sum(undershoot_l))
                    * _COMFORT_FLOOR_L1
                )
                comfort_dev_u = upper_t - comfort_targets
                comfort_dev_l = lower_t - comfort_targets
                comfort_cost = 0.025 * self.config.comfort_weight * (
                    np.sum((comfort_dev_u / comfort_band) ** 2)
                    + np.sum((comfort_dev_l / comfort_band) ** 2)
                )
            else:
                room_t = room_temps[1:]
                undershoot = np.maximum(0, temp_min_bounds - room_t)
                overshoot = np.maximum(0, room_t - temp_max_bounds)
                space_penalty = self.config.comfort_weight * (
                    np.sum(undershoot ** 2) * 10.0
                    + np.sum(overshoot ** 2) * 5.0
                    + np.sum(undershoot) * _COMFORT_FLOOR_L1
                )
                comfort_deviation = room_t - comfort_targets
                comfort_cost = 0.05 * self.config.comfort_weight * np.sum(
                    (comfort_deviation / comfort_band) ** 2
                )

            # Smoothness
            smoothness = 0.0
            if n_steps > 1:
                smoothness += 0.01 * np.sum(np.diff(space_power) ** 2)

            # Weather anticipation is left to the simulation, which already
            # applies solar gain and the wind/rain loss factors; see the
            # space-only objective for why the extra heuristic terms were
            # removed.

            # The compressor is one machine, so cycling and the house peak are
            # properties of the *combined* draw, not of space heating alone.
            combined = (
                space_power
                if dhw_plan_power is None
                else space_power + dhw_plan_power
            )

            return (
                energy_cost + space_penalty + comfort_cost
                + smoothness
                + _cycling(combined)
                + _capacity(combined)
                + terminal_cost(
                    _ends(room_temps, slab_temps, upper_temps, lower_temps)
                )
            )

        # Initial guess: space heating inversely proportional to price.
        price_normalized = prices / (np.mean(prices) + 1e-6)
        init_base = p_max * 0.6 * np.clip(1.5 - price_normalized, 0.2, 1.0)
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
            guess = init_base if warm_start is None else warm_start
            guess = np.minimum(np.clip(guess, 0.0, p_max), headroom)
            cost_dhw = dhw_cost_of(dhw_plan)
            bounds = [(0.0, float(headroom[i])) for i in range(n_steps)]
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
                    objective, starts, bounds, args=(cost_dhw, dhw_plan), maxiter=300
                )
                power = np.clip(res.x, 0.0, headroom)
                return (
                    power,
                    _solver_status(
                        res, lambda x: objective(x, cost_dhw, dhw_plan), guess
                    ),
                    float(objective(power, cost_dhw, dhw_plan)),
                )
            except Exception as e:
                _LOGGER.error("Space heating optimization (with DHW) failed: %s", e)
                return (
                    guess,
                    f"failed ({e})",
                    float(objective(guess, cost_dhw, dhw_plan)),
                )

        optimal_space, status, best_score = solve_space(optimal_dhw, None)

        # --- Re-plan DHW against the space heating it competes with ---------
        # The first DHW plan was made in ignorance of space heating, so it
        # tends to fill the cheapest hours to the compressor ceiling and push
        # space heating into dearer ones. Now that the space-heating profile is
        # known, price that contention and re-plan. The result is only adopted
        # if it actually scores better on the same objective, so this can never
        # make the plan worse.
        try:
            headroom_1 = np.maximum(0.0, p_max - optimal_dhw)
            # Where space heating sits hard against the ceiling that DHW left
            # it, it wanted more power than it could have. Its unconstrained
            # demand there is at least the full compressor.
            pinned = (optimal_dhw > 1e-6) & (optimal_space >= headroom_1 - 1e-3)
            if bool(np.any(pinned)):
                space_demand = np.where(pinned, p_max, optimal_space)
                dhw_plan_2 = self._build_dhw_requirements(
                    initial_state=initial_state,
                    prices=prices,
                    outdoor_temps=outdoor_temps,
                    step_hours=step_hours,
                    n_steps=n_steps,
                    dt=dt,
                    p_max=p_max,
                    space_demand=space_demand,
                )["schedule"]
                if not np.allclose(dhw_plan_2, optimal_dhw, atol=1e-4):
                    space_2, status_2, score_2 = solve_space(
                        dhw_plan_2, optimal_space
                    )
                    if score_2 < best_score - 1e-9:
                        optimal_dhw = dhw_plan_2
                        optimal_space = space_2
                        status, best_score = status_2, score_2
                        dhw_plan["schedule"] = dhw_plan_2
        except Exception as err:  # pragma: no cover - defensive
            _LOGGER.debug("DHW/space co-optimization pass skipped: %s", err)

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
            )
        )

        solar_gains = [self.model.compute_solar_gain(sr) for sr in solar_radiation]

        # Baseline cost
        baseline_power, baseline_end = self._compute_baseline_power(
            initial_state, outdoor_temps, wind_speeds, precipitation,
            solar_radiation, dt,
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
        baseline_dhw = np.full(n_steps, (p.dhw_draw_power + standby_loss) / cop_dhw)
        baseline_cost = float(np.sum(prices * (baseline_power + baseline_dhw) * dt))
        total_optimal_power = optimal_space + optimal_dhw
        predicted_cost = float(np.sum(prices * total_optimal_power * dt))
        dhw_cost = float(np.sum(prices * optimal_dhw * dt))

        # Settle up the heat the optimized plan left unstored at the horizon end.
        # The baseline reference ends with a tank at setpoint, so compare against
        # that rather than against the optimized tank's own starting point.
        baseline_end.dhw_temperature = dhw_setpoint
        optimized_end = self._replay_end_state(
            initial_state, optimal_space, outdoor_temps, wind_speeds,
            precipitation, solar_radiation, dt,
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

        timestamps = [
            start_time + timedelta(hours=i * dt) for i in range(n_steps)
        ]

        optimal_setpoints = self._power_to_setpoints(
            optimal_space, room_temps[:-1], outdoor_temps
        )
        displace_schedule = self._power_to_displace_schedule(
            optimal_space, outdoor_temps, forecast_analysis
        )
        heat_pump_schedule = self._power_to_heat_pump_schedule(
            optimal_space,
            optimal_dhw,
        )

        upper_setpoints = []
        lower_setpoints = []
        if two_zone:
            for i, power in enumerate(optimal_space):
                p_norm = (power - p_min) / max(p_max - p_min, 0.1)
                p_norm = np.clip(p_norm, 0, 1)
                upper_sp = self.config.min_temp + p_norm * (
                    self.config.max_temp - self.config.min_temp
                )
                lower_sp = self.config.min_temp + p_norm * (
                    self.config.max_temp - self.config.min_temp + 1.0
                )
                upper_setpoints.append(round(float(upper_sp), 1))
                lower_setpoints.append(round(float(lower_sp), 1))

        t_elapsed = (time.monotonic() - t_start) * 1000

        dhw_active_steps = int(np.sum(optimal_dhw > 0.1))
        _LOGGER.info(
            "DHW+Space optimization completed in %.0fms: cost=%.2f (DHW=%.2f in "
            "%d steps), baseline=%.2f, savings=%.1f%%, windows=%s",
            t_elapsed, predicted_cost, dhw_cost, dhw_active_steps, baseline_cost,
            _savings_percentage(savings, baseline_cost),
            dhw_plan["windows_text"] or "always",
        )

        grid = self._grid_report(total_optimal_power, _baseline_load, dt)
        space_reason_codes = classify_space_steps(
            optimal_space,
            prices,
            room_temps if not two_zone else upper_temps,
            temp_min_bounds,
            forecast_heat_loss_factors,
            self._pv_surplus,
            n_steps,
        )
        dhw_reason_codes = classify_dhw_steps(
            optimal_dhw,
            in_demand_window,
            dhw_ready_temps,
            dhw_plan.get("legionella_step"),
            n_steps,
        )

        return OptimizationResult(
            power_schedule=optimal_space.tolist(),
            room_temp_trajectory=room_temps.tolist(),
            slab_temp_trajectory=slab_temps.tolist(),
            timestamps=timestamps,
            prices=prices.tolist(),
            outdoor_temps=outdoor_temps.tolist(),
            predicted_cost=predicted_cost,
            baseline_cost=baseline_cost,
            predicted_savings=savings,
            savings_percentage=_savings_percentage(savings, baseline_cost),
            deferred_energy_cost=deferred_cost,
            optimal_setpoints=optimal_setpoints,
            status=status,
            solve_time_ms=t_elapsed,
            displace_schedule=displace_schedule,
            heat_pump_on_schedule=heat_pump_schedule,
            upper_temp_trajectory=upper_temps.tolist(),
            lower_temp_trajectory=lower_temps.tolist(),
            solar_gain_trajectory=solar_gains,
            upper_setpoints=upper_setpoints,
            lower_setpoints=lower_setpoints,
            dhw_power_schedule=optimal_dhw.tolist(),
            dhw_temp_trajectory=dhw_temps.tolist(),
            dhw_heating_cost=dhw_cost,
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
            space_reasons=space_reason_codes,
            dhw_reasons=dhw_reason_codes,
            price_known=self._price_known_list(n_steps),
            projected_peak_kw=grid["peak_kw"],
            peak_cost=grid["peak_cost"],
            compressor_starts=grid["starts"],
            pv_surplus=self._pv_surplus_list(n_steps),
            pv_self_consumed_kwh=self._pv_self_consumed(total_optimal_power, dt),
        )

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
        if p.two_zone_enabled:
            u_eff = p.upper_floor_heat_loss + p.lower_floor_heat_loss
        else:
            u_eff = p.heat_loss_coefficient
        # Slab has to run above the room to push heat into it, so its useful
        # ceiling is the temperature that sustains the target, not the target.
        q_demand = max(0.0, u_eff * (target - out_mean) - p.internal_gains)
        slab_cap = target + q_demand / max(p.slab_heat_transfer, 1e-6)
        caps = {"room": target, "slab": slab_cap}
        if dhw_cap is not None:
            caps["dhw"] = dhw_cap
        return caps

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

        Only a genuine *deficit* is charged. If the optimized plan ends with
        more useful heat in store than the reference, that surplus is not paid
        back as a bonus, because the reference is a thermostat and not a
        competing plan.
        """
        stored_gap = self._stored_thermal_energy(
            baseline_end, include_dhw, caps
        ) - self._stored_thermal_energy(optimized_end, include_dhw, caps)
        if stored_gap <= 1e-9:
            return 0.0

        cop = max(self.model.compute_cop(float(np.mean(outdoor_temps))), 1e-3)
        # Heat is topped up when it is cheap, so settle at a low percentile
        # rather than the mean; using the mean would over-charge the optimizer
        # for heat it would obviously buy back in a cheap hour.
        refill_price = float(np.percentile(prices, 25))
        return stored_gap / cop * refill_price

    def _compute_baseline_power(
        self,
        initial_state: ThermalState,
        outdoor_temps: np.ndarray,
        wind_speeds: np.ndarray,
        precipitation: np.ndarray,
        solar_radiation: np.ndarray,
        dt: float,
    ) -> tuple[np.ndarray, ThermalState]:
        """Simulate a conventional thermostat holding ``target_temp``.

        This is the reference the reported savings are measured against, so it
        has to behave like a real thermostat in the same physics as the
        optimized schedule. Anything it wastes is reported to the user as a
        saving, so the controller is built from the model's own steady state
        rather than from a heuristic.

        Heat is delivered to the slab and only reaches the room on the
        following step, so power is set by a cascade: the slab is driven to the
        temperature that sustains the setpoint, with a proportional term that
        pulls the room back if it has drifted.

        Returns the power schedule and the final state, the latter so the
        caller can account for the thermal energy left stored at the end of the
        horizon.
        """
        n_steps = len(outdoor_temps)
        target = self.config.target_temp
        p = self.model.params
        k_slab = max(p.slab_heat_transfer, 1e-6)

        baseline_power = np.zeros(n_steps)
        state = initial_state

        for i in range(n_steps):
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
            p.lower_floor_heat_loss, wind_speed * 0.5, precipitation * 0.5
        )
        q_solar_upper, q_solar_lower = self.model.solar_gain_per_zone(solar_radiation)
        area_ratio = getattr(p, "upper_floor_area_ratio", 0.5)
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
                * _t(state.buffer_tank_temperature, "slab")
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
        """Convert optimized power to ON/OFF decisions for supply enable.

        Heat pump is considered ON when either space heating power OR DHW power
        is above the activation threshold.
        """
        p = self.model.params
        on_threshold = max(0.1, p.min_electrical_power * 0.5)

        if dhw_power_schedule is None:
            dhw_power_schedule = np.zeros_like(space_power_schedule)

        schedule: list[bool] = []
        for i, (space_power, dhw_power) in enumerate(
            zip(space_power_schedule, dhw_power_schedule)
        ):
            space_on = bool(space_power >= on_threshold)
            dhw_on = bool(dhw_power >= on_threshold)
            heat_pump_on = space_on or dhw_on

            reason = "off"
            if space_on and dhw_on:
                reason = "space_and_dhw"
            elif space_on:
                reason = "space_only"
            elif dhw_on:
                reason = "dhw_only"

            _LOGGER.debug(
                (
                    "Heat pump decision step=%d: optimal_space=%.3f kW, "
                    "optimal_dhw=%.3f kW, threshold=%.3f kW -> "
                    "heat_pump_on=%s (%s)"
                ),
                i,
                float(space_power),
                float(dhw_power),
                float(on_threshold),
                heat_pump_on,
                reason,
            )
            schedule.append(heat_pump_on)

        if len(space_power_schedule) > 0:
            first_space = float(space_power_schedule[0])
            first_dhw = float(dhw_power_schedule[0])
            first_space_on = first_space >= on_threshold
            first_dhw_on = first_dhw >= on_threshold
            first_on = first_space_on or first_dhw_on

            first_reason = "off"
            if first_space_on and first_dhw_on:
                first_reason = "space_and_dhw"
            elif first_space_on:
                first_reason = "space_only"
            elif first_dhw_on:
                first_reason = "dhw_only"

            _LOGGER.debug(
                (
                    "Heat pump first-step summary: optimal_space[0]=%.3f kW, "
                    "optimal_dhw[0]=%.3f kW -> heat_pump_on=%s (%s)"
                ),
                first_space,
                first_dhw,
                first_on,
                first_reason,
            )

        return schedule

    def get_current_action(
        self, result: OptimizationResult, current_time: datetime
    ) -> dict[str, Any]:
        """Get the current recommended action from the optimization result."""
        if not result.timestamps:
            return {
                "power": self.model.params.min_electrical_power,
                "setpoint": self.config.target_temp,
                "mode": "idle",
                "price": 0.0,
                "heat_pump_on": False,
                "displace_value": 0.0,
            }

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
        }

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