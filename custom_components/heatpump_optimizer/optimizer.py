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
from scipy.optimize import minimize

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


def _savings_percentage(savings: float, baseline_cost: float) -> float:
    """Savings as a percentage of the baseline, clamped to a sensible range.

    A baseline at or near zero (a warm day where a thermostat would barely run)
    would otherwise turn rounding noise into a huge percentage.
    """
    if baseline_cost <= 0.01:
        return 0.0
    return float(np.clip(savings / baseline_cost * 100.0, -100.0, 100.0))


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
    ) -> OptimizationResult:
        """Run the MPC optimization with predictive weather anticipation.

        This is the CORE of true MPC: the optimizer uses the FULL 24-hour
        forecast trajectory (solar, wind, rain, temperature) to make decisions
        about CURRENT actions. It doesn't just react to current conditions.

        Key anticipatory behaviors:
        - Reduces pre-heating before forecasted sunny periods
        - Increases pre-heating before forecasted windy/rainy periods
        - Coordinates DHW heating with space heating and electricity prices
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

        if start_time is None:
            start_time = datetime.now()

        # Truncate arrays to n_steps
        prices = prices[:n_steps]
        outdoor_temps = outdoor_temps[:n_steps]
        wind_speeds = wind_speeds[:n_steps]
        precipitation = precipitation[:n_steps]
        solar_radiation = solar_radiation[:n_steps]

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

        # --- Predictive cost function weights ---
        # Adjust per-step weights based on forecast analysis
        solar_reduction = forecast_analysis["solar_reduction_factor"]
        wind_factor = forecast_analysis["wind_anticipation_factor"]
        rain_factor = forecast_analysis["rain_anticipation_factor"]

        # Per-step weight modifiers based on forecasted conditions
        # Steps BEFORE high solar get reduced heating weight (solar will help)
        # Steps BEFORE high wind/rain get increased heating weight (need to pre-heat)
        anticipatory_weights = np.ones(n_steps)
        for i in range(n_steps):
            # Look ahead: is there significant solar in the next 4-8 hours?
            lookahead_start = i
            lookahead_end = min(i + int(8 / dt), n_steps)
            if lookahead_end > lookahead_start:
                future_solar = np.mean(solar_gains_per_step[lookahead_start:lookahead_end])
                # If significant solar coming, reduce current heating motivation
                if future_solar > 0.5:  # > 0.5 kW solar gain is significant
                    anticipatory_weights[i] *= max(0.6, 1.0 - future_solar * 0.3)

                # If bad weather coming, increase pre-heating motivation
                future_loss_factor = np.mean(forecast_heat_loss_factors[lookahead_start:lookahead_end])
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
                    np.sum(undershoot_u ** 2 * anticipatory_weights) * 10.0
                    + np.sum(overshoot_u ** 2) * 5.0
                    + np.sum(undershoot_l ** 2 * anticipatory_weights) * 10.0
                    + np.sum(overshoot_l ** 2) * 5.0
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
                    np.sum(undershoot ** 2 * anticipatory_weights) * 10.0
                    + np.sum(overshoot ** 2) * 5.0
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

            # --- Predictive solar anticipation penalty ---
            # Penalize heating during periods just BEFORE high solar
            # This encourages the optimizer to "wait for the sun"
            solar_anticipation_cost = 0.0
            for i in range(min(n_steps - 1, int(12 / dt))):
                # Check if significant solar is coming in the next 4-8 hours
                future_start = i + int(2 / dt)  # 2 hours from now
                future_end = min(i + int(8 / dt), n_steps)
                if future_end > future_start:
                    future_solar_avg = np.mean(
                        solar_gains_per_step[future_start:future_end]
                    )
                    if future_solar_avg > 0.3:  # significant solar coming
                        # Penalize high power usage NOW if sun is coming soon
                        solar_anticipation_cost += (
                            0.02 * power_schedule[i] * future_solar_avg * dt
                        )

            # --- Predictive wind/rain pre-heating incentive ---
            # Incentivize pre-heating BEFORE bad weather arrives
            pre_heat_incentive = 0.0
            for i in range(min(n_steps - 1, int(12 / dt))):
                future_start = i + int(2 / dt)
                future_end = min(i + int(8 / dt), n_steps)
                if future_end > future_start:
                    future_loss = np.mean(
                        forecast_heat_loss_factors[future_start:future_end]
                    )
                    if future_loss > 1.15 and prices[i] < np.median(prices):
                        # Cheap electricity now AND bad weather coming
                        # Incentivize higher power to pre-charge thermal mass
                        pre_heat_incentive -= (
                            0.01 * power_schedule[i] * (future_loss - 1.0) * dt
                        )

            return (
                energy_cost + penalty + comfort_cost + smoothness
                + solar_anticipation_cost + pre_heat_incentive
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

        try:
            result = minimize(
                objective,
                initial_power,
                method="L-BFGS-B",
                bounds=bounds,
                options={"maxiter": 200, "ftol": 1e-6, "eps": 1e-4},
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

        return OptimizationResult(
            power_schedule=optimal_power.tolist(),
            room_temp_trajectory=room_temps.tolist(),
            slab_temp_trajectory=slab_temps.tolist(),
            timestamps=timestamps,
            prices=prices.tolist(),
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
        )

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

        max_temp = params.dhw_max_temp
        max_lead_hours = self.model.dhw_hold_hours()
        requirement = np.maximum(floor_temps, ready_temps)

        # The pump serves DHW as an on/off block, not a trickle, so the planner
        # allocates at a realistic run power and never below the level at which
        # the pump would actually be considered running.
        p_dhw_run = max(0.1, min(p_max * 0.8, p_max))
        min_run_power = min(p_dhw_run, max(0.15, self.model.params.min_electrical_power * 0.6))

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
            max_lead_steps=max(1, int(np.ceil(max_lead_hours / dt))),
            c_dhw=c_dhw,
            max_temp=max_temp,
        )

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
            "max_lead_hours": max_lead_hours,
        }

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
    ) -> np.ndarray:
        """Greedily schedule DHW heating into the cheapest feasible hours.

        Repeatedly simulates the tank, finds the first step where the
        availability requirement would be missed, and buys the missing energy
        from the cheapest steps that precede it (within the tank's heat-holding
        time, so the plan never pre-heats so early that standby losses dominate).

        Slots are ranked by *effective* price, i.e. the raw price inflated by
        the standby energy that would be lost while the heat waits in the tank.
        Storing early is therefore only chosen when it is genuinely cheaper than
        heating closer to the moment the water is needed.

        Because DHW production is a deferrable, essentially on/off load, this
        cheapest-first allocation is the cost-optimal strategy for it — and,
        unlike a gradient solve, it produces blocks the heat pump can actually
        run.
        """
        plan = np.zeros(n_steps)
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
        # the cheapest-first planner above rather than by the gradient solver
        # (which would smear it into an unrealizable trickle). Space heating is
        # then optimized *around* the fixed DHW blocks: the pump's remaining
        # capacity during a DHW block is what bounds space heating power.
        dhw_energy_cost = float(
            np.sum(prices * optimal_dhw * dt) * self.config.price_weight
        )
        space_power_headroom = np.maximum(0.0, p_max - optimal_dhw)

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

        def objective(space_power: np.ndarray) -> float:
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
                    np.sum(undershoot_u ** 2 * anticipatory_weights) * 10.0
                    + np.sum(overshoot_u ** 2) * 5.0
                    + np.sum(undershoot_l ** 2 * anticipatory_weights) * 10.0
                    + np.sum(overshoot_l ** 2) * 5.0
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
                    np.sum(undershoot ** 2 * anticipatory_weights) * 10.0
                    + np.sum(overshoot ** 2) * 5.0
                )
                comfort_deviation = room_t - comfort_targets
                comfort_cost = 0.05 * self.config.comfort_weight * np.sum(
                    (comfort_deviation / comfort_band) ** 2
                )

            # Smoothness
            smoothness = 0.0
            if n_steps > 1:
                smoothness += 0.01 * np.sum(np.diff(space_power) ** 2)

            # Solar anticipation cost (same as space-only)
            solar_anticipation_cost = 0.0
            for i in range(min(n_steps - 1, int(12 / dt))):
                future_start = i + int(2 / dt)
                future_end = min(i + int(8 / dt), n_steps)
                if future_end > future_start:
                    future_solar_avg = np.mean(
                        solar_gains_per_step[future_start:future_end]
                    )
                    if future_solar_avg > 0.3:
                        solar_anticipation_cost += (
                            0.02 * space_power[i] * future_solar_avg * dt
                        )

            return (
                energy_cost + space_penalty + comfort_cost
                + smoothness + solar_anticipation_cost
                + terminal_cost(
                    _ends(room_temps, slab_temps, upper_temps, lower_temps)
                )
            )

        # Initial guess: space heating inversely proportional to price.
        price_normalized = prices / (np.mean(prices) + 1e-6)
        init_space = p_max * 0.6 * np.clip(1.5 - price_normalized, 0.2, 1.0)
        for i in range(n_steps):
            init_space[i] *= anticipatory_weights[i]
        init_space = np.clip(init_space, p_min * 0.5, p_max * 0.8)
        init_space = np.minimum(init_space, space_power_headroom)

        # The heat pump serves one circuit at a time, so a DHW block eats into
        # the capacity available for space heating during that step.
        bounds = [(0.0, float(space_power_headroom[i])) for i in range(n_steps)]

        try:
            result = minimize(
                objective,
                init_space,
                method="L-BFGS-B",
                bounds=bounds,
                options={"maxiter": 300, "ftol": 1e-6, "eps": 1e-4},
            )
            optimal_space = np.clip(result.x, 0.0, space_power_headroom)
            status = _solver_status(result, objective, init_space)
        except Exception as e:
            _LOGGER.error("Space heating optimization (with DHW) failed: %s", e)
            optimal_space = init_space
            status = f"failed ({e})"

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

        return OptimizationResult(
            power_schedule=optimal_space.tolist(),
            room_temp_trajectory=room_temps.tolist(),
            slab_temp_trajectory=slab_temps.tolist(),
            timestamps=timestamps,
            prices=prices.tolist(),
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
            },
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
        thermal += p.buffer_tank_heat_loss * max(
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