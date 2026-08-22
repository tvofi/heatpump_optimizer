"""Two-zone thermal model with DHW tank for house with radiator and slab floor heating.

This module models the thermal dynamics of a house with two heating zones
served by an air-to-water heat pump with a buffer tank, plus a DHW (Domestic
Hot Water) storage tank:

    Zone 1 (Upper Floor): Radiator heating — fast thermal response (low mass)
    Zone 2 (Lower Floor): Slab floor heating — slow thermal response (high mass)
    Buffer Tank: 35L buffer coupling the heat pump to both circuits
    DHW Tank: 200-300L hot water tank with its own thermal dynamics

The thermal dynamics are governed by:

    C_upper * dT_upper/dt = Q_rad - Q_loss_upper + Q_inter + Q_solar_upper + Q_internal_upper
    C_slab  * dT_slab/dt  = Q_floor_hp - Q_slab_to_lower
    C_lower * dT_lower/dt = Q_slab_to_lower - Q_loss_lower - Q_inter + Q_solar_lower + Q_internal_lower
    C_buf   * dT_buf/dt   = Q_hp - Q_rad_draw - Q_floor_draw - Q_buf_loss
    C_dhw   * dT_dhw/dt   = Q_hp_dhw - Q_dhw_draw - Q_dhw_loss

Where:
    Q_hp_dhw = heat pump power allocated to DHW heating
    Q_dhw_draw = heat lost from DHW draws (consumption)
    Q_dhw_loss = standby heat loss from DHW tank

Heat loss model includes:
    - Wind speed effect: h_conv = h_base * (1 + wind_sensitivity * wind_speed)
    - Rain effect: U_eff = U_base * rain_multiplier when raining
    - Both use FORECASTED values per time step for true predictive control

The model falls back to the original single-zone behaviour when two-zone
parameters are not provided.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from .const import (
    DEFAULT_HOUSE_THERMAL_MASS,
    DEFAULT_HOUSE_HEAT_LOSS_COEFFICIENT,
    DEFAULT_SLAB_THERMAL_MASS,
    DEFAULT_SLAB_HEAT_TRANSFER,
    DEFAULT_HEAT_PUMP_COP_NOMINAL,
    DEFAULT_HEAT_PUMP_MAX_POWER,
    DEFAULT_HEAT_PUMP_MIN_POWER,
    DEFAULT_COP_SCALE,
    DEFAULT_UPPER_FLOOR_THERMAL_MASS,
    DEFAULT_LOWER_FLOOR_THERMAL_MASS,
    DEFAULT_UPPER_FLOOR_HEAT_LOSS,
    DEFAULT_LOWER_FLOOR_HEAT_LOSS,
    DEFAULT_INTER_ZONE_TRANSFER,
    DEFAULT_RADIATOR_POWER_FRACTION,
    DEFAULT_BUFFER_TANK_VOLUME,
    BUFFER_COOLING_RATE_MAX,
    BUFFER_COOLING_RATE_MIN,
    DEFAULT_BUFFER_COOLING_RATE,
    DEFAULT_BUFFER_TANK_LOSS,
    DEFAULT_HOUSE_HEAT_LOSS_SCALE,
    DEFAULT_WINDOW_AREA,
    DEFAULT_SOLAR_ORIENTATION_FACTOR,
    DEFAULT_SOLAR_HEAT_GAIN_COEFF,
    DEFAULT_SOLAR_UPPER_FRACTION,
    DEFAULT_DHW_TANK_VOLUME,
    DEFAULT_DHW_SETPOINT,
    DEFAULT_DHW_MIN_TEMP,
    DEFAULT_DHW_DAILY_CONSUMPTION,
    DEFAULT_DHW_COOLING_RATE,
    DHW_COOLING_REFERENCE_DELTA,
    DHW_COOLING_REFERENCE_AMBIENT_TEMP,
    DHW_COOLING_RATE_MIN,
    DHW_COOLING_RATE_MAX,
    DEFAULT_DHW_SCHEDULE_ENABLED,
    DEFAULT_DHW_WINDOWS,
    DEFAULT_DHW_IDLE_MIN_TEMP,
    DEFAULT_DHW_LEGIONELLA_ENABLED,
    DEFAULT_DHW_LEGIONELLA_TEMP,
    DEFAULT_DHW_LEGIONELLA_INTERVAL_DAYS,
    DEFAULT_WIND_SENSITIVITY,
    DEFAULT_RAIN_HEAT_LOSS_MULTIPLIER,
    DEFAULT_ECL110_DISPLACE_MIN,
    DEFAULT_ECL110_DISPLACE_MAX,
    DEFAULT_ECL110_PID_TIME_CONSTANT,
)
from .dhw_schedule import (
    DHWWindowError,
    FULL_DAY,
    Window,
    overlap_fraction,
    parse_windows,
)

_LOGGER = logging.getLogger(__name__)

# Specific heat capacity of water: ~0.00116 kWh/(liter·°C)
WATER_SPECIFIC_HEAT: float = 0.00116

# Air temperature around the storage tanks; they are assumed to stand indoors.
# This is the reference ambient the learned DHW cooling rate is stated against.
DHW_AMBIENT_TEMP: float = DHW_COOLING_REFERENCE_AMBIENT_TEMP


@dataclass
class ThermalParameters:
    """Parameters for the two-zone thermal model with DHW."""

    # --- Legacy single-zone parameters (kept for backward compat) ---
    room_thermal_mass: float = DEFAULT_HOUSE_THERMAL_MASS
    slab_thermal_mass: float = DEFAULT_SLAB_THERMAL_MASS
    heat_loss_coefficient: float = DEFAULT_HOUSE_HEAT_LOSS_COEFFICIENT
    # Learned dimensionless correction applied to every house heat loss
    # coefficient (single-zone and both two-zone floors). The configured
    # coefficients stay as the user entered them; this carries what the
    # coordinator has observed about the real building.
    house_heat_loss_scale: float = DEFAULT_HOUSE_HEAT_LOSS_SCALE
    slab_heat_transfer: float = DEFAULT_SLAB_HEAT_TRANSFER

    # --- Two-zone parameters ---
    upper_floor_thermal_mass: float = DEFAULT_UPPER_FLOOR_THERMAL_MASS  # kWh/°C
    lower_floor_thermal_mass: float = DEFAULT_LOWER_FLOOR_THERMAL_MASS  # kWh/°C
    upper_floor_heat_loss: float = DEFAULT_UPPER_FLOOR_HEAT_LOSS  # kW/°C
    lower_floor_heat_loss: float = DEFAULT_LOWER_FLOOR_HEAT_LOSS  # kW/°C
    inter_zone_transfer: float = DEFAULT_INTER_ZONE_TRANSFER  # kW/°C
    radiator_power_fraction: float = DEFAULT_RADIATOR_POWER_FRACTION  # 0-1

    # Buffer tank
    buffer_tank_volume: float = DEFAULT_BUFFER_TANK_VOLUME  # liters
    buffer_tank_heat_loss: float = DEFAULT_BUFFER_TANK_LOSS  # kW/°C, legacy
    # Standby cooling in °C/h at the same reference ΔT used for the DHW tank.
    # Like the DHW rate this is stated as an observable so it can be learned
    # from a buffer tank temperature sensor; the UA the simulation needs is
    # derived from it. When ``buffer_cooling_rate`` is set the derived UA wins
    # over the legacy ``buffer_tank_heat_loss``.
    buffer_cooling_rate: float = DEFAULT_BUFFER_COOLING_RATE  # °C/h

    # Solar gain parameters
    window_area: float = DEFAULT_WINDOW_AREA  # m²
    solar_orientation_factor: float = DEFAULT_SOLAR_ORIENTATION_FACTOR
    solar_heat_gain_coefficient: float = DEFAULT_SOLAR_HEAT_GAIN_COEFF
    solar_upper_fraction: float = DEFAULT_SOLAR_UPPER_FRACTION

    # DHW tank parameters
    dhw_tank_volume: float = DEFAULT_DHW_TANK_VOLUME  # liters
    dhw_setpoint: float = DEFAULT_DHW_SETPOINT  # °C "ready" temp at window start
    dhw_min_temp: float = DEFAULT_DHW_MIN_TEMP  # °C usable min inside windows
    dhw_daily_consumption: float = DEFAULT_DHW_DAILY_CONSUMPTION  # liters/day
    # Standby cooling in °C/h at the reference condition (45 °C tank, 20 °C
    # ambient). This is the parameter the coordinator learns; the UA value the
    # simulation needs is derived from it and the tank's thermal mass.
    dhw_cooling_rate: float = DEFAULT_DHW_COOLING_RATE  # °C/h

    # DHW demand windows (time frames where hot water must be available)
    dhw_schedule_enabled: bool = DEFAULT_DHW_SCHEDULE_ENABLED
    dhw_windows: list[Window] = field(default_factory=list)
    dhw_idle_min_temp: float = DEFAULT_DHW_IDLE_MIN_TEMP  # °C outside windows

    # Anti-legionella cycle
    dhw_legionella_enabled: bool = DEFAULT_DHW_LEGIONELLA_ENABLED
    dhw_legionella_temp: float = DEFAULT_DHW_LEGIONELLA_TEMP  # °C
    dhw_legionella_interval_days: float = DEFAULT_DHW_LEGIONELLA_INTERVAL_DAYS

    # Weather sensitivity parameters (configurable)
    wind_sensitivity: float = DEFAULT_WIND_SENSITIVITY  # fraction per m/s
    rain_heat_loss_multiplier: float = DEFAULT_RAIN_HEAT_LOSS_MULTIPLIER  # multiplier

    # ECL110 displace / PID approximation
    ecl110_displace_min: float = DEFAULT_ECL110_DISPLACE_MIN
    ecl110_displace_max: float = DEFAULT_ECL110_DISPLACE_MAX
    ecl110_pid_time_constant_hours: float = DEFAULT_ECL110_PID_TIME_CONSTANT

    # Heat pump parameters
    cop_nominal: float = DEFAULT_HEAT_PUMP_COP_NOMINAL
    cop_reference_temp: float = 7.0  # °C
    max_electrical_power: float = DEFAULT_HEAT_PUMP_MAX_POWER  # kW
    min_electrical_power: float = DEFAULT_HEAT_PUMP_MIN_POWER  # kW
    # Learned multiplicative correction to the modelled COP curve. 1.0 leaves
    # the nameplate-derived curve untouched; the coordinator moves it only when
    # a measured power entity makes real efficiency observable.
    cop_scale: float = DEFAULT_COP_SCALE
    # Learned capacity/efficiency derate as a function of outdoor temperature
    # and humidity — see ``defrost.py``. ``None`` means no derate is applied.
    defrost_derate: Any = None
    # Current outdoor relative humidity, used to select the derate bucket when
    # a caller does not pass one explicitly.
    #
    # Carried on the parameters rather than threaded through every
    # ``compute_cop`` call because the humidity dimension of the derate is a
    # single coarse split (dry versus humid), and a 24-hour horizon rarely
    # crosses it. Threading a per-step array through the whole simulation to
    # resolve a binary bucket would be a lot of plumbing for no accuracy. The
    # learner records the humidity that was actually present when it observed
    # an interval, so lookup and learning agree on what "now" means.
    ambient_humidity: Any = None

    # Internal gains (kW) - baseline heat from occupancy, appliances, etc.
    internal_gains: float = 0.3

    # Whether to use the enhanced two-zone model
    two_zone_enabled: bool = False

    # Whether DHW optimization is enabled
    dhw_enabled: bool = False

    # Learned/adjustable DHW usage profile (hourly multipliers, avg ~= 1.0)
    dhw_hourly_draw_pattern: list[float] = field(
        default_factory=lambda: DHW_HOURLY_DRAW_PATTERN.copy()
    )

    @property
    def buffer_tank_thermal_mass(self) -> float:
        """Thermal mass of buffer tank in kWh/°C."""
        return self.buffer_tank_volume * WATER_SPECIFIC_HEAT

    @property
    def buffer_tank_heat_loss_coefficient(self) -> float:
        """Standby loss of the buffer tank in kW/°C.

        Derived from ``buffer_cooling_rate`` exactly as the DHW tank UA is
        derived from ``dhw_cooling_rate``, so both tanks can be learned by the
        same estimator.
        """
        rate = float(
            np.clip(
                self.buffer_cooling_rate,
                BUFFER_COOLING_RATE_MIN,
                BUFFER_COOLING_RATE_MAX,
            )
        )
        return rate * self.buffer_tank_thermal_mass / DHW_COOLING_REFERENCE_DELTA

    @property
    def dhw_tank_thermal_mass(self) -> float:
        """Thermal mass of DHW tank in kWh/°C."""
        return self.dhw_tank_volume * WATER_SPECIFIC_HEAT

    @property
    def dhw_tank_heat_loss_coefficient(self) -> float:
        """Standby loss of the DHW tank in kW/°C.

        Derived from the observable cooling rate rather than configured
        directly: a tank that drops ``dhw_cooling_rate`` °C per hour while
        sitting ``DHW_COOLING_REFERENCE_DELTA`` °C above its surroundings has

            UA = rate * C_tank / ΔT_reference

        Stating the parameter as a cooling rate is what makes it learnable —
        it is exactly what a temperature sensor measures when nobody is
        drawing water.
        """
        rate = float(
            np.clip(self.dhw_cooling_rate, DHW_COOLING_RATE_MIN, DHW_COOLING_RATE_MAX)
        )
        return rate * self.dhw_tank_thermal_mass / DHW_COOLING_REFERENCE_DELTA

    @property
    def dhw_draw_power(self) -> float:
        """Average DHW draw power in kW (heat lost from tank due to consumption).

        Based on daily consumption heated from ~10°C cold water to tank temp.
        """
        # Average draw rate in liters per hour
        liters_per_hour = self.dhw_daily_consumption / 24.0
        # Heat needed: mass * Cp * delta_T
        # Assume cold water at 10°C, mixing with tank water
        delta_t = self.dhw_setpoint - 10.0  # °C temperature rise
        # Power = volume_flow * Cp * delta_T
        return liters_per_hour * WATER_SPECIFIC_HEAT * delta_t

    @property
    def dhw_windows_active(self) -> bool:
        """True when user-configured DHW demand windows should be honoured."""
        return bool(self.dhw_schedule_enabled and self.dhw_windows)

    @property
    def dhw_demand_windows(self) -> list[Window]:
        """Windows during which hot water must be available.

        Falls back to the whole day when the schedule is off or unset, which
        reproduces the previous "hot water always available" behaviour.
        """
        if not self.dhw_windows_active:
            return [FULL_DAY]
        return list(self.dhw_windows)

    @property
    def dhw_max_temp(self) -> float:
        """Highest tank temperature the optimizer is allowed to plan for."""
        top = self.dhw_setpoint
        if self.dhw_legionella_enabled:
            top = max(top, self.dhw_legionella_temp)
        return min(70.0, top)

    def effective_dhw_draw_pattern(self) -> list[float]:
        """Hourly draw multipliers restricted to the configured demand windows.

        The daily hot water volume is preserved: when windows are configured the
        learned pattern is masked by the window coverage of each hour and then
        re-scaled so the 24-hour sum stays at 24 (average multiplier 1.0).
        """
        base = list(self.dhw_hourly_draw_pattern)
        if len(base) != 24:
            base = DHW_HOURLY_DRAW_PATTERN.copy()
        if not self.dhw_windows_active:
            return base

        masked = [
            value * overlap_fraction(float(hour), float(hour) + 1.0, self.dhw_windows)
            for hour, value in enumerate(base)
        ]
        total = sum(masked)
        if total <= 1e-6:
            return base
        scale = 24.0 / total
        return [value * scale for value in masked]

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> ThermalParameters:
        """Create ThermalParameters from a config dictionary.

        The mapping is a table rather than ninety lines of near-identical
        ``config.get(KEY, DEFAULT)`` calls. Adding a parameter is one row, and
        a typo in a key or a default is visible by comparison with its
        neighbours instead of buried in prose.
        """
        from . import const

        # field name -> (config key, default). Both are resolved from ``const``
        # by name so the table stays readable and a missing constant fails
        # loudly at import rather than silently substituting a default.
        table = {
            # Single-zone / legacy
            "room_thermal_mass": ("HOUSE_THERMAL_MASS", "HOUSE_THERMAL_MASS"),
            "slab_thermal_mass": ("SLAB_THERMAL_MASS", "SLAB_THERMAL_MASS"),
            "heat_loss_coefficient": (
                "HOUSE_HEAT_LOSS_COEFFICIENT", "HOUSE_HEAT_LOSS_COEFFICIENT"
            ),
            "slab_heat_transfer": ("SLAB_HEAT_TRANSFER", "SLAB_HEAT_TRANSFER"),
            # Two-zone
            "upper_floor_thermal_mass": (
                "UPPER_FLOOR_THERMAL_MASS", "UPPER_FLOOR_THERMAL_MASS"
            ),
            "lower_floor_thermal_mass": (
                "LOWER_FLOOR_THERMAL_MASS", "LOWER_FLOOR_THERMAL_MASS"
            ),
            "upper_floor_heat_loss": (
                "UPPER_FLOOR_HEAT_LOSS", "UPPER_FLOOR_HEAT_LOSS"
            ),
            "lower_floor_heat_loss": (
                "LOWER_FLOOR_HEAT_LOSS", "LOWER_FLOOR_HEAT_LOSS"
            ),
            "inter_zone_transfer": ("INTER_ZONE_TRANSFER", "INTER_ZONE_TRANSFER"),
            "radiator_power_fraction": (
                "RADIATOR_POWER_FRACTION", "RADIATOR_POWER_FRACTION"
            ),
            # Buffer tank
            "buffer_tank_volume": ("BUFFER_TANK_VOLUME", "BUFFER_TANK_VOLUME"),
            "buffer_tank_heat_loss": ("BUFFER_TANK_LOSS", "BUFFER_TANK_LOSS"),
            # Solar gain
            "window_area": ("WINDOW_AREA", "WINDOW_AREA"),
            "solar_orientation_factor": (
                "SOLAR_ORIENTATION_FACTOR", "SOLAR_ORIENTATION_FACTOR"
            ),
            "solar_heat_gain_coefficient": (
                "SOLAR_HEAT_GAIN_COEFF", "SOLAR_HEAT_GAIN_COEFF"
            ),
            "solar_upper_fraction": (
                "SOLAR_UPPER_FRACTION", "SOLAR_UPPER_FRACTION"
            ),
            # Hot water
            "dhw_tank_volume": ("DHW_TANK_VOLUME", "DHW_TANK_VOLUME"),
            "dhw_setpoint": ("DHW_SETPOINT", "DHW_SETPOINT"),
            "dhw_min_temp": ("DHW_MIN_TEMP", "DHW_MIN_TEMP"),
            "dhw_daily_consumption": (
                "DHW_DAILY_CONSUMPTION", "DHW_DAILY_CONSUMPTION"
            ),
            "dhw_cooling_rate": ("DHW_COOLING_RATE", "DHW_COOLING_RATE"),
            "dhw_idle_min_temp": ("DHW_IDLE_MIN_TEMP", "DHW_IDLE_MIN_TEMP"),
            "dhw_legionella_temp": (
                "DHW_LEGIONELLA_TEMP", "DHW_LEGIONELLA_TEMP"
            ),
            "dhw_legionella_interval_days": (
                "DHW_LEGIONELLA_INTERVAL_DAYS", "DHW_LEGIONELLA_INTERVAL_DAYS"
            ),
            # Learned corrections
            "buffer_cooling_rate": ("BUFFER_COOLING_RATE", "BUFFER_COOLING_RATE"),
            "house_heat_loss_scale": (
                "HOUSE_HEAT_LOSS_SCALE", "HOUSE_HEAT_LOSS_SCALE"
            ),
            # Weather sensitivity
            "wind_sensitivity": ("WIND_SENSITIVITY", "WIND_SENSITIVITY"),
            "rain_heat_loss_multiplier": (
                "RAIN_HEAT_LOSS_MULTIPLIER", "RAIN_HEAT_LOSS_MULTIPLIER"
            ),
            # ECL110 heat curve control
            "ecl110_displace_min": (
                "ECL110_DISPLACE_MIN", "ECL110_DISPLACE_MIN"
            ),
            "ecl110_displace_max": (
                "ECL110_DISPLACE_MAX", "ECL110_DISPLACE_MAX"
            ),
            "ecl110_pid_time_constant_hours": (
                "ECL110_PID_TIME_CONSTANT", "ECL110_PID_TIME_CONSTANT"
            ),
            # Heat pump
            "cop_nominal": ("HEAT_PUMP_COP_NOMINAL", "HEAT_PUMP_COP_NOMINAL"),
            "max_electrical_power": (
                "HEAT_PUMP_MAX_POWER", "HEAT_PUMP_MAX_POWER"
            ),
            "min_electrical_power": (
                "HEAT_PUMP_MIN_POWER", "HEAT_PUMP_MIN_POWER"
            ),
        }

        values = {
            name: config.get(
                getattr(const, f"CONF_{conf}"), getattr(const, f"DEFAULT_{default}")
            )
            for name, (conf, default) in table.items()
        }

        # Booleans are coerced because a config entry may carry a string.
        for name, conf, default in (
            ("dhw_schedule_enabled", "DHW_SCHEDULE_ENABLED", "DHW_SCHEDULE_ENABLED"),
            (
                "dhw_legionella_enabled",
                "DHW_LEGIONELLA_ENABLED",
                "DHW_LEGIONELLA_ENABLED",
            ),
        ):
            values[name] = bool(
                config.get(
                    getattr(const, f"CONF_{conf}"), getattr(const, f"DEFAULT_{default}")
                )
            )

        # Two-zone and DHW are inferred from whether their settings are present
        # at all, rather than from a flag, so an entry written before either
        # existed keeps working.
        values["two_zone_enabled"] = any(
            key in config
            for key in (
                const.CONF_UPPER_FLOOR_THERMAL_MASS,
                const.CONF_LOWER_FLOOR_THERMAL_MASS,
                const.CONF_INTER_ZONE_TRANSFER,
                const.CONF_RADIATOR_POWER_FRACTION,
            )
        )
        values["dhw_enabled"] = any(
            key in config
            for key in (
                const.CONF_DHW_TANK_VOLUME,
                const.CONF_DHW_TEMP_ENTITY,
                const.CONF_DHW_WINDOWS,
            )
        )

        # Demand windows: fall back to the default schedule when the stored
        # value is missing, and to "always available" when it cannot be parsed.
        windows_spec = config.get(const.CONF_DHW_WINDOWS, DEFAULT_DHW_WINDOWS)
        try:
            values["dhw_windows"] = parse_windows(windows_spec)
        except DHWWindowError as err:
            _LOGGER.warning(
                "Invalid DHW window configuration %r (%s); falling back to "
                "always-available hot water",
                windows_spec,
                err,
            )
            values["dhw_windows"] = []

        return cls(**values)


@dataclass
class WeatherForecastPoint:
    """A single point in the weather forecast."""

    timestamp: float  # Unix timestamp
    temperature: float  # °C
    wind_speed: float = 0.0  # m/s
    precipitation: float = 0.0  # mm/h
    solar_radiation: float = 0.0  # W/m² (global horizontal irradiance)


@dataclass
class ThermalState:
    """Current thermal state of the two-zone system with DHW.

    Falls back to single-zone semantics when two_zone_enabled is False:
    - room_temperature is the single room temp
    - slab_temperature is the single slab temp
    """

    room_temperature: float = 21.0  # °C (or upper floor temp in two-zone)
    slab_temperature: float = 22.0  # °C
    outdoor_temperature: float = 5.0  # °C

    # Two-zone additions
    upper_floor_temperature: float = 21.0  # °C
    lower_floor_temperature: float = 21.0  # °C
    buffer_tank_temperature: float = 40.0  # °C
    floor_return_temperature: float | None = None  # °C (from real sensor)
    solar_radiation: float = 0.0  # W/m² current solar irradiance

    # DHW state
    dhw_temperature: float = 55.0  # °C current DHW tank temperature
    # Hours since the tank was last known to be at anti-legionella temperature.
    # None means "unknown" and is treated as not due.
    dhw_hours_since_legionella: float | None = None

    # ECL110 control state
    ecl110_displace_command: float = 0.0  # °C requested parallel shift
    ecl110_effective_displace: float = 0.0  # °C filtered PI/PID effect

    # Whether something other than the heat pump (typically a wood furnace) is
    # currently charging the tanks. Set by the coordinator's detector; the
    # optimizer reads it to suppress discretionary electric hot water.
    external_heat_active: bool = False


# DHW draw pattern: normalized hourly multipliers (24 values, sum=24)
# Morning peak (6-9), evening peak (17-21), low overnight
DHW_HOURLY_DRAW_PATTERN: list[float] = [
    0.2, 0.1, 0.1, 0.1, 0.2, 0.5,   # 00-05: very low
    1.5, 2.5, 2.0, 1.0, 0.8, 0.7,   # 06-11: morning peak
    0.8, 0.7, 0.6, 0.6, 0.8, 1.5,   # 12-17: afternoon
    2.0, 2.2, 1.8, 1.2, 0.8, 0.4,   # 18-23: evening peak
]
# Normalize so average = 1.0
_DHW_SUM = sum(DHW_HOURLY_DRAW_PATTERN)
DHW_HOURLY_DRAW_PATTERN = [x * 24.0 / _DHW_SUM for x in DHW_HOURLY_DRAW_PATTERN]


class ThermalModel:
    """Thermal model supporting single-zone, two-zone, and DHW operation."""

    def __init__(self, params: ThermalParameters) -> None:
        """Initialize the thermal model."""
        self.params = params

    # ------------------------------------------------------------------
    # Common helpers
    # ------------------------------------------------------------------

    def compute_cop(
        self, outdoor_temp: float, humidity: float | None = None
    ) -> float:
        """Compute heat pump COP as function of outdoor temperature.

        COP ≈ COP_nominal * (1 + 0.025 * (T_outdoor - T_ref))

        Two learned corrections are applied on top of the nameplate curve:
        ``cop_scale``, a single multiplier fitted from measured electrical
        input, and the defrost derate, which is a function of outdoor
        temperature and humidity and captures the frosting band the smooth
        curve cannot represent. Both default to no change.

        ``humidity`` falls back to ``params.ambient_humidity`` so that the
        derate's humidity dimension is actually used. Without that fallback
        every lookup landed in the dry bucket while learning wrote into
        whichever bucket was real, so everything observed in humid frosting
        conditions — the conditions the derate exists for — was recorded and
        then never applied.
        """
        delta = outdoor_temp - self.params.cop_reference_temp
        factor = max(0.3, 1.0 + 0.025 * delta)
        cop = self.params.cop_nominal * min(factor, 1.5) * self.params.cop_scale
        derate = self.params.defrost_derate
        if derate is not None:
            if humidity is None:
                humidity = self.params.ambient_humidity
            cop *= derate.factor(outdoor_temp, humidity)
        return max(cop, 0.5)

    def compute_cop_dhw(self, outdoor_temp: float, dhw_temp: float) -> float:
        """Compute heat pump COP for DHW mode.

        DHW requires higher supply temperature (55-65°C vs 35-45°C for space
        heating), so COP is lower.  Rough model:
        COP_dhw ≈ COP_space * 0.7 (penalty for higher supply temp)
        """
        base_cop = self.compute_cop(outdoor_temp)
        # Higher DHW temp → lower COP (Carnot-like penalty)
        dhw_penalty = max(0.5, 1.0 - 0.008 * (dhw_temp - 35.0))
        return base_cop * dhw_penalty

    def effective_outdoor_temp(
        self, temp: float, wind_speed: float = 0.0, precipitation: float = 0.0
    ) -> float:
        """Compute effective outdoor temperature accounting for wind chill and rain."""
        wind_effect = wind_speed * 0.3
        rain_effect = precipitation * 0.5
        return temp - wind_effect - rain_effect

    def effective_heat_loss_coefficient(
        self, base_u: float, wind_speed: float = 0.0, precipitation: float = 0.0
    ) -> float:
        """Compute effective heat loss coefficient using configurable weather sensitivity.

        Wind effect: convective heat transfer increases with wind speed.
        h_eff = h_base * (1 + wind_sensitivity * wind_speed)

        Rain effect: wet building envelope has higher U-value.
        U_eff = U_wind_adjusted * rain_multiplier (when precipitation > 0)
        """
        p = self.params
        # The configured coefficient is a nameplate estimate; the learned scale
        # corrects it towards what this house actually does.
        base_u = base_u * p.house_heat_loss_scale
        # Wind-enhanced convective loss
        wind_factor = 1.0 + p.wind_sensitivity * wind_speed
        u_wind = base_u * wind_factor

        # Rain effect: apply multiplier when raining
        if precipitation > 0.1:  # threshold for "raining"
            # Scale rain multiplier based on precipitation intensity
            # Light rain (0.1-1 mm/h): partial multiplier
            # Heavy rain (>2 mm/h): full multiplier
            rain_intensity = min(precipitation / 2.0, 1.0)
            rain_factor = 1.0 + (p.rain_heat_loss_multiplier - 1.0) * rain_intensity
            u_wind *= rain_factor

        return u_wind

    def effective_heat_loss_coefficient_legacy(
        self, wind_speed: float = 0.0, precipitation: float = 0.0
    ) -> float:
        """Compute effective heat loss coefficient (backward compat wrapper)."""
        return self.effective_heat_loss_coefficient(
            self.params.heat_loss_coefficient, wind_speed, precipitation
        )

    def compute_solar_gain(self, solar_radiation: float) -> float:
        """Compute total solar heat gain in kW from solar radiation (W/m²).

        Q_solar = solar_radiation * window_area * orientation_factor * SHGC / 1000
        """
        p = self.params
        if solar_radiation <= 0:
            return 0.0
        return (
            solar_radiation
            * p.window_area
            * p.solar_orientation_factor
            * p.solar_heat_gain_coefficient
            / 1000.0  # W → kW
        )

    def solar_gain_per_zone(
        self, solar_radiation: float
    ) -> tuple[float, float]:
        """Split solar gain between upper and lower floor.

        Returns: (Q_solar_upper, Q_solar_lower) in kW
        """
        total = self.compute_solar_gain(solar_radiation)
        upper = total * self.params.solar_upper_fraction
        lower = total * (1.0 - self.params.solar_upper_fraction)
        return upper, lower

    def update_ecl110_displace_state(
        self,
        state: ThermalState,
        displace_command: float,
        dt_hours: float = 0.25,
    ) -> ThermalState:
        """Update ECL110 effective displace with first-order PI/PID-like lag.

        The manual documents that ECL110 applies PI-style loop dynamics. We model
        this as a first-order response from commanded to effective displace.
        """
        p = self.params
        cmd = float(np.clip(displace_command, p.ecl110_displace_min, p.ecl110_displace_max))
        tau = max(0.1, p.ecl110_pid_time_constant_hours)
        alpha = float(np.clip(dt_hours / tau, 0.0, 1.0))

        effective = state.ecl110_effective_displace + alpha * (
            cmd - state.ecl110_effective_displace
        )
        state.ecl110_displace_command = cmd
        state.ecl110_effective_displace = float(
            np.clip(effective, p.ecl110_displace_min, p.ecl110_displace_max)
        )
        return state

    # ------------------------------------------------------------------
    # DHW tank model
    # ------------------------------------------------------------------

    def dhw_draw_rate(self, hour_of_day: float) -> float:
        """Get DHW draw rate in kW for a given hour of day.

        Uses a time-of-day pattern multiplied by average draw power. When the
        user configured DHW demand windows, draws only occur inside them.
        """
        hour_idx = int(hour_of_day) % 24
        pattern = self.params.effective_dhw_draw_pattern()
        return self.params.dhw_draw_power * pattern[hour_idx]

    def dhw_draw_rates(self, step_hours: np.ndarray) -> np.ndarray:
        """Vectorized draw rates (kW) for a sequence of hour-of-day values."""
        pattern = np.asarray(self.params.effective_dhw_draw_pattern(), dtype=float)
        indices = (np.asarray(step_hours, dtype=float).astype(int)) % 24
        return self.params.dhw_draw_power * pattern[indices]

    def dhw_usage_intensity(self, hour_of_day: float) -> float:
        """Return normalized DHW usage intensity for a given hour (avg ~= 1.0)."""
        return self.params.effective_dhw_draw_pattern()[int(hour_of_day) % 24]

    def dhw_hold_hours(self) -> float:
        """Hours a fully charged tank can coast before dropping to the min temp.

        Purely standby-driven, i.e. how long stored heat survives when nobody
        draws water. It is reported for diagnostics and used as a fallback
        pre-heating horizon; the cost planner itself does not need a lead-time
        cap because it prices the storage losses directly.
        """
        p = self.params
        top = max(p.dhw_max_temp, p.dhw_min_temp + 1.0)
        floor = p.dhw_min_temp
        return self.dhw_coast_hours(top, floor)

    def dhw_coast_hours(
        self,
        from_temp: float,
        to_temp: float,
        ambient_temp: float = DHW_AMBIENT_TEMP,
    ) -> float:
        """Hours of pure standby decay between two tank temperatures.

        Exact solution of ``C·dT/dt = -UA·(T - T_ambient)``:

            t = (C / UA) · ln((T_from - T_amb) / (T_to - T_amb))

        Returns 0 when the tank is already at or below the target, and the
        model's horizon cap when the tank barely loses heat at all.
        """
        p = self.params
        if to_temp >= from_temp:
            return 0.0
        c_dhw = max(p.dhw_tank_thermal_mass, 0.01)
        ua = max(p.dhw_tank_heat_loss_coefficient, 1e-5)
        hot = from_temp - ambient_temp
        cold = to_temp - ambient_temp
        if hot <= 0.0:
            return 0.0
        if cold <= 0.0:
            # The target is at or below ambient; the tank never gets there.
            return 168.0
        return float(np.clip((c_dhw / ua) * np.log(hot / cold), 0.0, 168.0))

    def simulate_dhw_step(
        self,
        dhw_temp: float,
        dhw_power_thermal: float,
        hour_of_day: float,
        ambient_temp: float = DHW_AMBIENT_TEMP,
        dt_hours: float = 0.25,
        draw_power: float | None = None,
    ) -> float:
        """Simulate one time step of DHW tank dynamics.

        Args:
            dhw_temp: Current DHW tank temperature (°C)
            dhw_power_thermal: Thermal power from HP to DHW (kW)
            hour_of_day: Current hour (0-24) for draw pattern
            ambient_temp: Ambient temperature near the tank (°C)
            dt_hours: Time step (hours)
            draw_power: Pre-computed draw power (kW); avoids recomputing the
                hourly pattern inside hot optimization loops.

        Returns:
            New DHW tank temperature (°C)
        """
        p = self.params
        C_dhw = p.dhw_tank_thermal_mass
        if C_dhw < 0.01:
            return dhw_temp

        # Heat input from heat pump
        q_in = dhw_power_thermal

        # Heat drawn by consumption
        q_draw = (
            self.dhw_draw_rate(hour_of_day) if draw_power is None else draw_power
        )

        # Standby heat loss to ambient
        q_loss = p.dhw_tank_heat_loss_coefficient * (dhw_temp - ambient_temp)

        # Temperature change
        dT = (q_in - q_draw - q_loss) / C_dhw
        new_temp = dhw_temp + dT * dt_hours

        # Physical bounds (can't go below cold water inlet ~10°C)
        new_temp = max(10.0, new_temp)

        return new_temp

    def simulate_dhw_only(
        self,
        initial_temp: float,
        dhw_power_schedule: np.ndarray,
        outdoor_temps: np.ndarray,
        draw_rates: np.ndarray,
        dt_hours: float = 0.25,
    ) -> np.ndarray:
        """Simulate the DHW tank alone (used for fast schedule planning).

        Returns an array of length ``n_steps + 1`` starting at ``initial_temp``.
        """
        n_steps = len(dhw_power_schedule)
        temps = np.zeros(n_steps + 1)
        temps[0] = initial_temp
        temp = initial_temp
        for i in range(n_steps):
            cop = self.compute_cop_dhw(float(outdoor_temps[i]), temp)
            temp = self.simulate_dhw_step(
                dhw_temp=temp,
                dhw_power_thermal=cop * float(dhw_power_schedule[i]),
                hour_of_day=0.0,
                dt_hours=dt_hours,
                draw_power=float(draw_rates[i]),
            )
            temps[i + 1] = temp
        return temps

    # ------------------------------------------------------------------
    # Single-zone simulation (backward compatible)
    # ------------------------------------------------------------------

    def _simulate_step_single(
        self,
        state: ThermalState,
        electrical_power: float,
        outdoor_temp: float,
        wind_speed: float = 0.0,
        precipitation: float = 0.0,
        solar_radiation: float = 0.0,
        dt_hours: float = 0.25,
    ) -> ThermalState:
        """Simulate one step with the original single-zone model."""
        p = self.params
        cop = self.compute_cop(outdoor_temp)
        thermal_power = cop * electrical_power

        u_eff = self.effective_heat_loss_coefficient(
            p.heat_loss_coefficient, wind_speed, precipitation
        )
        q_slab_to_room = p.slab_heat_transfer * (
            state.slab_temperature - state.room_temperature
        )
        q_loss = u_eff * (state.room_temperature - outdoor_temp)
        q_internal = p.internal_gains
        q_solar = self.compute_solar_gain(solar_radiation)

        dT_room = (q_slab_to_room - q_loss + q_internal + q_solar) / p.room_thermal_mass
        dT_slab = (thermal_power - q_slab_to_room) / p.slab_thermal_mass

        new_room = state.room_temperature + dT_room * dt_hours
        new_slab = state.slab_temperature + dT_slab * dt_hours

        return ThermalState(
            room_temperature=new_room,
            slab_temperature=new_slab,
            outdoor_temperature=outdoor_temp,
            upper_floor_temperature=new_room,
            lower_floor_temperature=new_room,
            buffer_tank_temperature=state.buffer_tank_temperature,
            floor_return_temperature=state.floor_return_temperature,
            solar_radiation=solar_radiation,
            dhw_temperature=state.dhw_temperature,
            ecl110_displace_command=state.ecl110_displace_command,
            ecl110_effective_displace=state.ecl110_effective_displace,
        )

    # ------------------------------------------------------------------
    # Two-zone simulation
    # ------------------------------------------------------------------

    def _simulate_step_two_zone(
        self,
        state: ThermalState,
        electrical_power: float,
        outdoor_temp: float,
        wind_speed: float = 0.0,
        precipitation: float = 0.0,
        solar_radiation: float = 0.0,
        dt_hours: float = 0.25,
    ) -> ThermalState:
        """Simulate one step with the two-zone model including buffer tank.

        State vector: [T_upper, T_lower, T_slab, T_buffer]
        """
        p = self.params
        cop = self.compute_cop(outdoor_temp)
        thermal_power = cop * electrical_power  # total heat from HP to buffer

        # Weather-adjusted heat loss using configurable sensitivity
        u_upper = self.effective_heat_loss_coefficient(
            p.upper_floor_heat_loss, wind_speed, precipitation
        )
        # Lower floor less exposed to wind (partially underground/sheltered)
        u_lower = self.effective_heat_loss_coefficient(
            p.lower_floor_heat_loss, wind_speed * 0.5, precipitation * 0.5
        )

        # Solar gains per zone
        q_solar_upper, q_solar_lower = self.solar_gain_per_zone(solar_radiation)

        # Internal gains split proportional to area ratio
        area_ratio = getattr(p, "upper_floor_area_ratio", 0.5) if hasattr(p, "upper_floor_area_ratio") else 0.5
        q_internal_upper = p.internal_gains * area_ratio
        q_internal_lower = p.internal_gains * (1.0 - area_ratio)

        T_upper = state.upper_floor_temperature
        T_lower = state.lower_floor_temperature
        T_slab = state.slab_temperature
        T_buf = state.buffer_tank_temperature

        # --- Buffer tank dynamics ---
        C_buf = p.buffer_tank_thermal_mass
        if C_buf < 1e-6:
            C_buf = 0.04  # fallback for 35L

        # Heat drawn from buffer to radiators (upper floor)
        rad_fraction = p.radiator_power_fraction
        q_rad_from_buf = rad_fraction * thermal_power
        q_floor_from_buf = (1.0 - rad_fraction) * thermal_power

        # Buffer tank loss to ambient (assume ~20°C ambient indoors)
        q_buf_loss = p.buffer_tank_heat_loss_coefficient * (T_buf - 20.0)

        dT_buf = (thermal_power - q_rad_from_buf - q_floor_from_buf - q_buf_loss) / max(C_buf, 0.01)

        # --- Slab dynamics ---
        q_slab_to_lower = p.slab_heat_transfer * (T_slab - T_lower)
        dT_slab = (q_floor_from_buf - q_slab_to_lower) / p.slab_thermal_mass

        # --- Inter-zone heat transfer ---
        q_inter = p.inter_zone_transfer * (T_lower - T_upper)

        # --- Upper floor (radiators) ---
        q_loss_upper = u_upper * (T_upper - outdoor_temp)
        dT_upper = (
            q_rad_from_buf - q_loss_upper + q_inter + q_solar_upper + q_internal_upper
        ) / p.upper_floor_thermal_mass

        # --- Lower floor (slab heated) ---
        q_loss_lower = u_lower * (T_lower - outdoor_temp)
        dT_lower = (
            q_slab_to_lower - q_loss_lower - q_inter + q_solar_lower + q_internal_lower
        ) / p.lower_floor_thermal_mass

        # Euler integration
        new_upper = T_upper + dT_upper * dt_hours
        new_lower = T_lower + dT_lower * dt_hours
        new_slab = T_slab + dT_slab * dt_hours
        new_buf = T_buf + dT_buf * dt_hours

        # Weighted average for legacy room_temperature field
        avg_room = new_upper * area_ratio + new_lower * (1.0 - area_ratio)

        return ThermalState(
            room_temperature=avg_room,
            slab_temperature=new_slab,
            outdoor_temperature=outdoor_temp,
            upper_floor_temperature=new_upper,
            lower_floor_temperature=new_lower,
            buffer_tank_temperature=new_buf,
            floor_return_temperature=state.floor_return_temperature,
            solar_radiation=solar_radiation,
            dhw_temperature=state.dhw_temperature,
            dhw_hours_since_legionella=state.dhw_hours_since_legionella,
            ecl110_displace_command=state.ecl110_displace_command,
            ecl110_effective_displace=state.ecl110_effective_displace,
        )

    # ------------------------------------------------------------------
    # Public simulation interface
    # ------------------------------------------------------------------

    def simulate_step(
        self,
        state: ThermalState,
        electrical_power: float,
        outdoor_temp: float,
        wind_speed: float = 0.0,
        precipitation: float = 0.0,
        solar_radiation: float = 0.0,
        dt_hours: float = 0.25,
    ) -> ThermalState:
        """Simulate one time step (dispatches to single or two-zone)."""
        if self.params.two_zone_enabled:
            return self._simulate_step_two_zone(
                state, electrical_power, outdoor_temp,
                wind_speed, precipitation, solar_radiation, dt_hours,
            )
        return self._simulate_step_single(
            state, electrical_power, outdoor_temp,
            wind_speed, precipitation, solar_radiation, dt_hours,
        )

    def simulate_trajectory(
        self,
        initial_state: ThermalState,
        power_schedule: np.ndarray,
        outdoor_temps: np.ndarray,
        wind_speeds: np.ndarray | None = None,
        precipitation: np.ndarray | None = None,
        solar_radiation: np.ndarray | None = None,
        dt_hours: float = 0.25,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Simulate the full trajectory given a power schedule.

        Returns:
            Tuple of (room_temperatures, slab_temperatures,
                       upper_floor_temperatures, lower_floor_temperatures)
        """
        n_steps = len(power_schedule)

        if wind_speeds is None:
            wind_speeds = np.zeros(n_steps)
        if precipitation is None:
            precipitation = np.zeros(n_steps)
        if solar_radiation is None:
            solar_radiation = np.zeros(n_steps)

        room_temps = np.zeros(n_steps + 1)
        slab_temps = np.zeros(n_steps + 1)
        upper_temps = np.zeros(n_steps + 1)
        lower_temps = np.zeros(n_steps + 1)

        room_temps[0] = initial_state.room_temperature
        slab_temps[0] = initial_state.slab_temperature
        upper_temps[0] = initial_state.upper_floor_temperature
        lower_temps[0] = initial_state.lower_floor_temperature

        state = initial_state
        for i in range(n_steps):
            state = self.simulate_step(
                state=state,
                electrical_power=power_schedule[i],
                outdoor_temp=outdoor_temps[i],
                wind_speed=wind_speeds[i],
                precipitation=precipitation[i],
                solar_radiation=solar_radiation[i],
                dt_hours=dt_hours,
            )
            room_temps[i + 1] = state.room_temperature
            slab_temps[i + 1] = state.slab_temperature
            upper_temps[i + 1] = state.upper_floor_temperature
            lower_temps[i + 1] = state.lower_floor_temperature

        return room_temps, slab_temps, upper_temps, lower_temps

    def simulate_trajectory_with_dhw(
        self,
        initial_state: ThermalState,
        space_power_schedule: np.ndarray,
        dhw_power_schedule: np.ndarray,
        outdoor_temps: np.ndarray,
        wind_speeds: np.ndarray | None = None,
        precipitation: np.ndarray | None = None,
        solar_radiation: np.ndarray | None = None,
        start_hour: float = 0.0,
        dt_hours: float = 0.25,
        dhw_draw_rates: np.ndarray | None = None,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Simulate full trajectory with coordinated space + DHW heating.

        Args:
            dhw_draw_rates: Optional pre-computed per-step DHW draw power (kW).
                Passing it avoids re-deriving the hourly pattern on every call,
                which matters because the optimizer evaluates this thousands of
                times per solve.

        Returns:
            Tuple of (room_temps, slab_temps, upper_temps, lower_temps, dhw_temps)
        """
        n_steps = len(space_power_schedule)

        if wind_speeds is None:
            wind_speeds = np.zeros(n_steps)
        if precipitation is None:
            precipitation = np.zeros(n_steps)
        if solar_radiation is None:
            solar_radiation = np.zeros(n_steps)
        if dhw_draw_rates is None:
            hours = (start_hour + np.arange(n_steps) * dt_hours) % 24.0
            dhw_draw_rates = self.dhw_draw_rates(hours)

        room_temps = np.zeros(n_steps + 1)
        slab_temps = np.zeros(n_steps + 1)
        upper_temps = np.zeros(n_steps + 1)
        lower_temps = np.zeros(n_steps + 1)
        dhw_temps = np.zeros(n_steps + 1)

        room_temps[0] = initial_state.room_temperature
        slab_temps[0] = initial_state.slab_temperature
        upper_temps[0] = initial_state.upper_floor_temperature
        lower_temps[0] = initial_state.lower_floor_temperature
        dhw_temps[0] = initial_state.dhw_temperature

        state = initial_state
        current_hour = start_hour

        for i in range(n_steps):
            # Space heating simulation
            state = self.simulate_step(
                state=state,
                electrical_power=space_power_schedule[i],
                outdoor_temp=outdoor_temps[i],
                wind_speed=wind_speeds[i],
                precipitation=precipitation[i],
                solar_radiation=solar_radiation[i],
                dt_hours=dt_hours,
            )

            # DHW simulation (runs in parallel with space heating)
            cop_dhw = self.compute_cop_dhw(outdoor_temps[i], state.dhw_temperature)
            dhw_thermal_power = cop_dhw * dhw_power_schedule[i]

            new_dhw = self.simulate_dhw_step(
                dhw_temp=state.dhw_temperature,
                dhw_power_thermal=dhw_thermal_power,
                hour_of_day=current_hour % 24.0,
                ambient_temp=DHW_AMBIENT_TEMP,
                dt_hours=dt_hours,
                draw_power=float(dhw_draw_rates[i]),
            )
            state.dhw_temperature = new_dhw

            room_temps[i + 1] = state.room_temperature
            slab_temps[i + 1] = state.slab_temperature
            upper_temps[i + 1] = state.upper_floor_temperature
            lower_temps[i + 1] = state.lower_floor_temperature
            dhw_temps[i + 1] = new_dhw

            current_hour += dt_hours

        return room_temps, slab_temps, upper_temps, lower_temps, dhw_temps

    def get_state_matrices(
        self,
        outdoor_temp: float,
        wind_speed: float = 0.0,
        precipitation: float = 0.0,
        dt_hours: float = 0.25,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Get discrete-time state-space matrices for the thermal model.

        For single-zone: State x = [T_room, T_slab], Input u = P_el
        For two-zone: State x = [T_upper, T_lower, T_slab, T_buf], Input u = P_el

        Returns: (A, B, E) for x[k+1] = A*x[k] + B*u[k] + E*d[k]
        """
        p = self.params

        if not p.two_zone_enabled:
            return self._get_state_matrices_single(
                outdoor_temp, wind_speed, precipitation, dt_hours
            )
        return self._get_state_matrices_two_zone(
            outdoor_temp, wind_speed, precipitation, dt_hours
        )

    def _get_state_matrices_single(
        self,
        outdoor_temp: float,
        wind_speed: float,
        precipitation: float,
        dt_hours: float,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """State-space matrices for the single-zone model."""
        p = self.params
        cop = self.compute_cop(outdoor_temp)
        u_eff = self.effective_heat_loss_coefficient(
            p.heat_loss_coefficient, wind_speed, precipitation
        )

        a11 = -(p.slab_heat_transfer + u_eff) / p.room_thermal_mass
        a12 = p.slab_heat_transfer / p.room_thermal_mass
        a21 = -p.slab_heat_transfer / p.slab_thermal_mass
        a22 = -p.slab_heat_transfer / p.slab_thermal_mass

        A_cont = np.array([[a11, a12], [a21, a22]])
        B_cont = np.array([[0.0], [cop / p.slab_thermal_mass]])
        E_cont = np.array([
            [u_eff / p.room_thermal_mass, 1.0 / p.room_thermal_mass],
            [0.0, 0.0],
        ])

        A = np.eye(2) + A_cont * dt_hours
        B = B_cont * dt_hours
        E = E_cont * dt_hours
        return A, B, E

    def _get_state_matrices_two_zone(
        self,
        outdoor_temp: float,
        wind_speed: float,
        precipitation: float,
        dt_hours: float,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """State-space matrices for the two-zone model.

        State: [T_upper, T_lower, T_slab, T_buf]
        """
        p = self.params
        cop = self.compute_cop(outdoor_temp)

        u_upper = self.effective_heat_loss_coefficient(
            p.upper_floor_heat_loss, wind_speed, precipitation
        )
        u_lower = self.effective_heat_loss_coefficient(
            p.lower_floor_heat_loss, wind_speed * 0.5, precipitation * 0.5
        )

        C_u = p.upper_floor_thermal_mass
        C_l = p.lower_floor_thermal_mass
        C_s = p.slab_thermal_mass
        C_b = max(p.buffer_tank_thermal_mass, 0.01)

        k_inter = p.inter_zone_transfer
        k_slab = p.slab_heat_transfer
        k_buf = p.buffer_tank_heat_loss_coefficient
        f_rad = p.radiator_power_fraction

        A_cont = np.zeros((4, 4))
        # T_upper row
        A_cont[0, 0] = -(u_upper + k_inter) / C_u
        A_cont[0, 1] = k_inter / C_u
        # T_lower row
        A_cont[1, 0] = k_inter / C_l
        A_cont[1, 1] = -(u_lower + k_inter) / C_l
        A_cont[1, 2] = k_slab / C_l
        # T_slab row
        A_cont[2, 1] = -k_slab / C_s
        A_cont[2, 2] = -k_slab / C_s
        # T_buffer row
        A_cont[3, 3] = -k_buf / C_b

        # B (4x1) - input = P_electrical
        B_cont = np.array([
            [f_rad * cop / C_u],
            [0.0],
            [(1 - f_rad) * cop / C_s],
            [cop / C_b],
        ])

        # E (4x2) - disturbance = [T_outdoor, Q_internal_total]
        E_cont = np.array([
            [u_upper / C_u, 0.5 / C_u],
            [u_lower / C_l, 0.5 / C_l],
            [0.0, 0.0],
            [k_buf / C_b, 0.0],
        ])

        A = np.eye(4) + A_cont * dt_hours
        B = B_cont * dt_hours
        E = E_cont * dt_hours
        return A, B, E

    def update_slab_from_return_temp(
        self, state: ThermalState, return_temp: float
    ) -> ThermalState:
        """Update slab temperature estimate from actual floor return sensor.

        The return temperature of the floor heating circuit is a good proxy
        for the average slab temperature (typically return_temp ≈ T_slab - 2°C
        to T_slab + 0°C depending on flow rate and delta-T).

        We use a simple weighted merge: 70% sensor, 30% model to smooth noise.
        """
        if return_temp is None:
            return state

        # Return temp is typically close to slab temp
        estimated_slab = return_temp + 1.0

        # Weighted merge with model prediction
        merged_slab = 0.7 * estimated_slab + 0.3 * state.slab_temperature

        state.slab_temperature = merged_slab
        state.floor_return_temperature = return_temp
        return state