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
import math
from dataclasses import dataclass, field, replace
from typing import Any

import numpy as np

from . import mixing_valve
from .mixing_valve import MODE_NONE as MIXING_VALVE_MODE_NONE
from .const import (
    WATER_SPECIFIC_HEAT as _WATER_SPECIFIC_HEAT,
    BUFFER_STORE_MIN_VOLUME,
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
    DEFAULT_LOWER_FLOOR_LOSS_RATIO,
    DEFAULT_INTER_ZONE_TRANSFER,
    DEFAULT_RADIATOR_POWER_FRACTION,
    DEFAULT_UPPER_FLOOR_AREA_RATIO,
    DEFAULT_BUFFER_TANK_VOLUME,
    BUFFER_COOLING_RATE_MAX,
    BUFFER_COOLING_RATE_MIN,
    DEFAULT_BUFFER_COOLING_RATE,
    buffer_cooling_rate_bounds,
    default_buffer_cooling_rate,
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
    DHW_MIXED_USE_TEMP,
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
    DEFAULT_WOOD_TANK_VOLUME,
    DEFAULT_DHW_WOOD_COIL_ENABLED,
    DHW_COLD_WATER_TEMP,
    DHW_WOOD_COIL_EFFECTIVENESS,
    TOPOLOGY_NO_VALVE,
    TOPOLOGY_SINGLE_TANK_VALVE,
    TOPOLOGY_TWO_TANK_4WAY,
    TOPOLOGY_VALVE_UPPER_DIRECT_SLAB,
    WOOD_TANK_MAX_TEMP,
    WOOD_TANK_MIN_MARGIN,
    topology_layout_valid,
)
from .dhw_schedule import (
    DHWWindowError,
    FULL_DAY,
    Window,
    overlap_fraction,
    parse_weekly_windows,
    parse_windows,
)

_LOGGER = logging.getLogger(__name__)

# Specific heat capacity of water: ~0.00116 kWh/(liter·°C).
# Defined in `const` because the tank-geometry helpers there need it too, and
# re-exported here so the many uses below read unchanged.
WATER_SPECIFIC_HEAT: float = _WATER_SPECIFIC_HEAT

# Air temperature around the storage tanks; they are assumed to stand indoors.
# This is the reference ambient the learned DHW cooling rate is stated against.
DHW_AMBIENT_TEMP: float = DHW_COOLING_REFERENCE_AMBIENT_TEMP

# Physical floor for the thermal-mass stores the per-step model divides by.
# 0.1 kWh/°C is about 90 litres of water — already implausibly small for a
# room, a slab or a floor; anything below it is a typo or a bad service
# write, and as a divisor it turns the objective into inf/NaN. Enforced once
# at the parameter boundary (``ThermalParameters.clamp``) so the simulate
# steps can keep dividing without per-call guards.
THERMAL_MASS_FLOOR: float = 0.1

# Explicit Euler diverges once a store's coupling-to-mass ratio u·dt/C
# passes 2; 1.5 leaves margin without ever triggering for a plausible house
# (defaults sit near 0.05). Above it, ``simulate_step`` subdivides the step.
EULER_STABILITY_MAX_RATIO: float = 1.5


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
    # Learned redistribution between the zones (item 31). 1.0 is the configured
    # split; the learner only moves it when a real lower-floor sensor exists.
    lower_floor_loss_ratio: float = DEFAULT_LOWER_FLOOR_LOSS_RATIO

    # --- Mixing valve and the buffer tank as a store (items 27/29) ---------
    #
    # `none` is the default and keeps the existing `draw == supply` identity,
    # which is *correct* for a system with no valve: whatever the pump makes
    # goes straight to the emitters. This is an added branch, not a fix.
    mixing_valve_mode: str = MIXING_VALVE_MODE_NONE
    # Indoor temperature the valve regulates to. 0.0 means "not configured",
    # and the comfort ceiling below is used instead — which is also what the
    # dumb-valve recommendation says to set a real valve to.
    mixing_valve_target: float = 0.0  # °C
    # The user's configured comfort maximum, carried here so the valve target
    # can genuinely default to "the top of the comfort band" as documented.
    # The previous fallback was `house_temp + 1.0` — a target that recedes
    # 1 K above wherever the house currently is, so the default valve never
    # throttled: the house overheated (29 °C in the release-notes scenario)
    # and the tank could not charge at all.
    comfort_ceiling: float = 23.0  # °C
    # Flow-to-zone difference the emitters are sized for, used to back an
    # emitter UA out of the nameplate output so the throttled branch reproduces
    # today's delivery at the design point rather than inventing a new balance.
    emitter_design_delta_t: float = 15.0  # K

    def __post_init__(self) -> None:
        # Every construction path — ``from_config``, snapshots, tests — runs
        # through here, so the divisor floor holds from birth. Attribute
        # writes after construction (the set_thermal_params service) call
        # ``clamp`` again at their own chokepoint.
        self.clamp()

    def clamp(self) -> None:
        """Enforce the physical floor on every thermal-mass divisor.

        The per-step simulate functions divide by these four stores raw; a
        zero or near-zero value from config or a service write would put
        inf/NaN inside the objective. One boundary owns the guard so the
        divisions stay unguarded.
        """
        for name in (
            "room_thermal_mass",
            "slab_thermal_mass",
            "upper_floor_thermal_mass",
            "lower_floor_thermal_mass",
        ):
            try:
                value = float(getattr(self, name))
            except (TypeError, ValueError):
                value = THERMAL_MASS_FLOOR
            if not np.isfinite(value) or value < THERMAL_MASS_FLOOR:
                value = THERMAL_MASS_FLOOR
            setattr(self, name, value)

    @property
    def buffer_is_store(self) -> bool:
        """Whether the buffer tank is worth planning around as a store.

        Needs both a valve (or nothing can charge it) and enough volume to
        matter: the default 35 L tank holds less than one optimizer step of
        heat, and letting the terminal credit see it would have the solver
        planning around noise. The physics stay modelled either way.
        """
        return (
            mixing_valve.is_throttling(self.mixing_valve_mode)
            and self.buffer_tank_volume >= BUFFER_STORE_MIN_VOLUME
        )
    # The tank's safe ceiling. In the model this clamps the state; in the
    # optimizer it must become a hard constraint, because comfort and tank
    # limits there are soft penalties and the solver would plan to boil it.
    buffer_max_temp: float = 70.0  # °C

    # --- Two-tank topology (issue #40) --------------------------------------
    #
    # Whether a wood-tank probe is configured (CONF_WOOD_TANK_TOP_ENTITY).
    # Deliberately stricter than the diagram's "wood present": the two-tank
    # model activates only when it can be initialized from a real
    # measurement, never from a flue switch alone.
    wood_tank_configured: bool = False
    # Shares the detector's config key (CONF_WOOD_TANK_VOLUME) — one number
    # for one physical tank, no migration.
    wood_tank_volume: float = DEFAULT_WOOD_TANK_VOLUME  # liters
    # The DHW tank refills through a coil in the wood tank (v3.15.1).
    dhw_wood_coil_enabled: bool = DEFAULT_DHW_WOOD_COIL_ENABLED

    @property
    def dhw_coil_active(self) -> bool:
        """Whether DHW refill water is preheated by the modelled wood tank.

        Requires the option, hot water, and the two-tank model — the
        preheat is a function of a real wood-tank temperature, so without
        the modelled tank there is nothing sound to compute it from.
        """
        return (
            self.dhw_wood_coil_enabled
            and self.dhw_enabled
            and self.two_tank_modelled
        )

    # The user's stored layout choice (v3.16.0, CONF_TOPOLOGY_LAYOUT).
    # None = derive the default below, which is every pre-editor install.
    topology_layout_override: str | None = None

    #: Memo for `topology_layout`, keyed on its inputs like the UA caches:
    #: the step function asks `two_tank_modelled`/`slab_fed_direct` once
    #: per step, a few million times per solve, and re-deriving a constant
    #: there is the exact mistake the buffer-UA profiling found.
    _layout_cache: tuple | None = field(
        default=None, init=False, repr=False, compare=False
    )

    @property
    def topology_layout(self) -> str:
        """The hydronic layout key this configuration resolves to.

        A stored choice wins when it is still honest for the configuration
        (``topology_layout_valid`` — the same predicate the apply_topology
        service enforces at write time, so a key can only stop being valid
        when the configuration changes underneath it, and then it falls
        back to the derived default rather than erroring). Everything that
        needs "is the two-tank model active" reads ``two_tank_modelled``
        below — one home for the gating, as the config flow, the
        coordinator and ``describe_setup`` must all agree.
        """
        key = (
            self.topology_layout_override,
            self.mixing_valve_mode,
            self.two_zone_enabled,
            self.wood_tank_configured,
        )
        cached = self._layout_cache
        if cached is not None and cached[0] == key:
            return cached[1]
        throttling = mixing_valve.is_throttling(self.mixing_valve_mode)
        if self.topology_layout_override and topology_layout_valid(
            self.topology_layout_override,
            two_zone=self.two_zone_enabled,
            throttling=throttling,
            wood_probe=self.wood_tank_configured,
        ):
            value = self.topology_layout_override
        elif not throttling:
            value = TOPOLOGY_NO_VALVE
        elif self.two_zone_enabled and self.wood_tank_configured:
            value = TOPOLOGY_TWO_TANK_4WAY
        else:
            value = TOPOLOGY_SINGLE_TANK_VALVE
        self._layout_cache = (key, value)
        return value

    @property
    def two_tank_modelled(self) -> bool:
        """Whether the wood tank is simulated as its own store."""
        return self.topology_layout == TOPOLOGY_TWO_TANK_4WAY

    @property
    def slab_fed_direct(self) -> bool:
        """Whether the slab circuit bypasses the valve (v3.16.0 layout).

        The layout the pre-v3.14.1 drawing showed, and some houses have:
        the valve throttles the radiator circuit while the slab drinks raw
        tank water. Its validity predicate excludes a wood probe, so this
        can never be true together with ``two_tank_modelled``.
        """
        return self.topology_layout == TOPOLOGY_VALVE_UPPER_DIRECT_SLAB

    @property
    def wood_tank_thermal_mass(self) -> float:
        """Thermal mass of the wood tank in kWh/°C."""
        return self.wood_tank_volume * WATER_SPECIFIC_HEAT
    # Carnot-derived COP penalty for charging hot. Off keeps `compute_cop`
    # exactly as it was. Without it, storing heat at 70 °C appears to cost the
    # same per kWh as delivering it at 35 °C, so storage looks free.
    cop_flow_carnot: bool = False
    cop_flow_reference_temp: float = 35.0  # °C
    inter_zone_transfer: float = DEFAULT_INTER_ZONE_TRANSFER  # kW/°C
    radiator_power_fraction: float = DEFAULT_RADIATOR_POWER_FRACTION  # 0-1
    #: Share of the heated area on the upper floor; splits internal gains.
    upper_floor_area_ratio: float = DEFAULT_UPPER_FLOOR_AREA_RATIO

    # Buffer tank
    buffer_tank_volume: float = DEFAULT_BUFFER_TANK_VOLUME  # liters
    buffer_tank_heat_loss: float = DEFAULT_BUFFER_TANK_LOSS  # kW/°C, legacy
    # Standby cooling in °C/h at the same reference ΔT used for the DHW tank.
    # Like the DHW rate this is stated as an observable so it can be learned
    # from a buffer tank temperature sensor; the UA the simulation needs is
    # derived from it. When ``buffer_cooling_rate`` is set the derived UA wins
    # over the legacy ``buffer_tank_heat_loss``.
    #
    # 0.0 means "not known yet, derive a prior from the tank's size". It cannot
    # be a fixed default because the right rate depends on the volume, and it is
    # resolved in the property rather than in __post_init__ so that changing the
    # volume at runtime still produces a sensible prior.
    buffer_cooling_rate: float = 0.0  # °C/h

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
    #: The seven-day window structure when the configured spec carries day
    #: selectors (weekly windows, owner request #3); None when it does not,
    #: which is every spec written before the feature and the common case.
    #: ``dhw_windows`` above is always the merged every-day view, so every
    #: existing consumer keeps working unchanged; day-aware consumers ask
    #: this instead.
    dhw_weekly_windows: list[list[Window]] | None = None
    dhw_idle_min_temp: float = DEFAULT_DHW_IDLE_MIN_TEMP  # °C outside windows

    # Anti-legionella cycle
    dhw_legionella_enabled: bool = DEFAULT_DHW_LEGIONELLA_ENABLED
    dhw_legionella_temp: float = DEFAULT_DHW_LEGIONELLA_TEMP  # °C
    dhw_legionella_interval_days: float = DEFAULT_DHW_LEGIONELLA_INTERVAL_DAYS

    # --- Hot water, v4.0.0 T3 ------------------------------------------
    # The cold-water inlet (annual mean), previously two hard-coded 10.0 s.
    # The default IS 10.0 and every existing ready target sits on it.
    dhw_inlet_temp: float = 10.0  # °C
    #: Seasonal swing amplitude, °C; 0 keeps the inlet constant year-round.
    dhw_inlet_seasonal_amplitude: float = 0.0
    #: The inlet the coordinator resolved for "now" (live sensor, or the
    #: seasonal model). None means the configured annual mean — which is
    #: how every pre-T3 install behaves.
    dhw_inlet_current: Any = None
    #: Fraction of drain heat a greywater recovery unit gives back (#3
    #: of the draw energy chain); 0 = none installed.
    greywater_recovery: float = 0.0
    #: #20: learned per-window ready energies in kWh, keyed by the demand
    #: window's label. None (the default) keeps the mean-profile targets.
    dhw_window_ready_energy: Any = None
    #: #47: the legionella cycle may shop for a cheap day inside its
    #: interval. The price ceiling is set per solve by the coordinator
    #: from the learned prior's expected daily minimum; None = inelastic.
    dhw_elastic_legionella_enabled: bool = False
    dhw_legionella_min_interval_days: float = 5.0
    dhw_legionella_price_ceiling: Any = None
    #: T4a #11 (gated): extra readiness the coordinator asks for when the
    #: immersion element keeps rescuing late tanks, °C. 0 = inert.
    dhw_ready_margin_c: float = 0.0
    #: T4b #36 (gated): learned scale on the modelled solar aperture.
    #: 1.0 = inert; set per solve by the coordinator when the flag is on.
    solar_aperture_scale: float = 1.0
    #: T4b #53 (gated): learned per-hour internal gains, kW, 24 entries.
    #: None = the flat ``internal_gains`` constant, byte-inert.
    internal_gains_profile: Any = None

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
    def lower_floor_heat_loss_learned(self) -> float:
        """The lower zone's loss after the learned redistribution.

        Every consumer of the *dynamics* must go through this rather than the
        raw configured value, or the learner would fit a number the model never
        actually uses.
        """
        return self.lower_floor_heat_loss * self.lower_floor_loss_ratio

    #: Memo for `buffer_tank_heat_loss_coefficient`, keyed on its own inputs.
    #: `init=False` and `compare=False` so it is neither a constructor argument
    #: nor part of equality -- it is a cache, not a parameter.
    _buffer_ua_cache: tuple | None = field(
        default=None, init=False, repr=False, compare=False
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

        Memoised on the two values it reads, because the simulation asks for it
        once per step and a 24-hour solve runs a few million steps: profiled, it
        and the volume^(2/3) surface area behind it were 29 % of a valved
        solve's entire runtime, recomputing a constant. The key is the inputs
        rather than a dirty flag, so the learner writing a new cooling rate --
        or anything else mutating the parameters in place, which the coordinator
        does -- invalidates it for free.
        """
        # Bounds depend on the tank: UA follows surface area, which grows as
        # volume^(2/3), while the rate is UA/C and so falls as volume^(-1/3).
        # Clamping every size against a 35 L tank's numbers is what floored a
        # large accumulator an order of magnitude above its real standby loss.
        key = (self.buffer_tank_volume, self.buffer_cooling_rate)
        cached = self._buffer_ua_cache
        if cached is not None and cached[0] == key:
            return cached[1]
        low, high = buffer_cooling_rate_bounds(self.buffer_tank_volume)
        rate = self.buffer_cooling_rate
        if rate <= 0.0:
            rate = default_buffer_cooling_rate(self.buffer_tank_volume)
        # min/max rather than np.clip: this is a scalar, and np.clip on a
        # Python float costs about six microseconds, which at a few million
        # calls per solve is seconds for nothing.
        rate = min(max(float(rate), low), high)
        value = rate * self.buffer_tank_thermal_mass / DHW_COOLING_REFERENCE_DELTA
        self._buffer_ua_cache = (key, value)
        return value

    #: Memo for `wood_tank_heat_loss_coefficient`, same shape as the buffer's.
    _wood_ua_cache: tuple | None = field(
        default=None, init=False, repr=False, compare=False
    )

    @property
    def wood_tank_heat_loss_coefficient(self) -> float:
        """Standby loss of the wood tank in kW/°C.

        No learner and no configured rate in v1: the prior derived from the
        tank's volume by the same volume^(2/3) surface law as the buffer is
        used directly. Memoised for the same reason as the buffer's UA — the
        two-tank step asks once per step, a few million times per solve.
        """
        key = self.wood_tank_volume
        cached = self._wood_ua_cache
        if cached is not None and cached[0] == key:
            return cached[1]
        rate = default_buffer_cooling_rate(self.wood_tank_volume)
        value = rate * self.wood_tank_thermal_mass / DHW_COOLING_REFERENCE_DELTA
        self._wood_ua_cache = (key, value)
        return value

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
    def dhw_inlet_reference(self) -> float:
        """The cold-water temperature the tank refills at, °C.

        The coordinator-resolved value (live sensor or seasonal model) wins
        when present; otherwise the configured annual mean, whose default is
        the 10.0 the model always assumed.
        """
        current = self.dhw_inlet_current
        if isinstance(current, (int, float)) and np.isfinite(current):
            return float(current)
        return float(self.dhw_inlet_temp)

    def seasonal_inlet_temp(self, day_of_year: int) -> float:
        """The inlet model: annual mean minus a cosine dipping in late winter.

        Swedish tap water bottoms out around day 60 (late February) and
        peaks in late summer; the amplitude is the half-swing in °C. With
        the default amplitude of 0 this is exactly the constant mean.
        """
        swing = float(self.dhw_inlet_seasonal_amplitude)
        if swing <= 0.0:
            return float(self.dhw_inlet_temp)
        phase = 2.0 * np.pi * (float(day_of_year) - 60.0) / 365.0
        return float(self.dhw_inlet_temp - swing * np.cos(phase))

    @property
    def dhw_draw_power(self) -> float:
        """Average DHW draw power in kW (heat lost from tank due to consumption).

        Based on daily consumption heated from the cold-water inlet to tank
        temp. A greywater recovery unit pre-warms the incoming water with
        drain heat, which scales the whole chain down by its effectiveness.
        """
        # Average draw rate in liters per hour
        liters_per_hour = self.dhw_daily_consumption / 24.0
        # Heat needed: mass * Cp * delta_T
        delta_t = self.dhw_setpoint - self.dhw_inlet_reference  # °C rise
        recovery = float(np.clip(self.greywater_recovery, 0.0, 0.9))
        # Power = volume_flow * Cp * delta_T
        return (
            liters_per_hour * WATER_SPECIFIC_HEAT * max(delta_t, 0.0)
            * (1.0 - recovery)
        )

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
        """The everyday charge limit: how hot a plan may take the tank.

        This is the user's own "Highest tank temperature to charge to", and
        nothing else. Until v5.1.10 the disinfection temperature was folded
        in here permanently, which turned a 60 °C hygiene setting into the
        ceiling the cost planner spent every single day: pre-buying at the
        night trough beats heating at the evening window even after standby
        losses, and how far the plan over-charges is bounded by exactly this
        number. A 52/60 pair therefore ran the tank to ~58 °C on a day with
        no cycle due — the field did the opposite of what its help text
        promises ("An upper limit on charging, not a target").

        A disinfection cycle legitimately goes above this, but only while it
        is running: the optimizer raises the ceiling per step around the
        cycle it has actually scheduled, and ``dhw_hard_max_temp`` below is
        the physical rating that bounds even that.
        """
        return min(70.0, self.dhw_setpoint)

    @property
    def dhw_hard_max_temp(self) -> float:
        """The tank's rating: the hottest this tank may ever be driven.

        The everyday ceiling is a preference; this is physics, and it has to
        stay above the disinfection temperature or the model would refuse
        the very boost the hygiene cycle exists to deliver. ``simulate_dhw_step``
        clamps to this, so a pinned plan, a replayed trajectory or a
        legionella boost is bounded without the everyday limit silently
        capping a cycle at the setpoint.
        """
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
            "upper_floor_area_ratio": (
                "UPPER_FLOOR_AREA_RATIO", "UPPER_FLOOR_AREA_RATIO"
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
            # Hot water, v4.0.0 T3. None of these joins the dhw_enabled
            # presence trio below — a configured inlet must never phantom-
            # enable hot water on an entry that has none.
            "dhw_inlet_temp": ("DHW_INLET_TEMP", "DHW_INLET_TEMP"),
            "dhw_inlet_seasonal_amplitude": (
                "DHW_INLET_SEASONAL_AMPLITUDE", "DHW_INLET_SEASONAL_AMPLITUDE"
            ),
            "greywater_recovery": ("GREYWATER_RECOVERY", "GREYWATER_RECOVERY"),
            "dhw_legionella_min_interval_days": (
                "DHW_LEGIONELLA_MIN_INTERVAL_DAYS",
                "DHW_LEGIONELLA_MIN_INTERVAL_DAYS",
            ),
            # Learned corrections
            "buffer_cooling_rate": ("BUFFER_COOLING_RATE", "BUFFER_COOLING_RATE"),
            "house_heat_loss_scale": (
                "HOUSE_HEAT_LOSS_SCALE", "HOUSE_HEAT_LOSS_SCALE"
            ),
            "lower_floor_loss_ratio": (
                "LOWER_FLOOR_LOSS_RATIO", "LOWER_FLOOR_LOSS_RATIO"
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
            (
                "dhw_elastic_legionella_enabled",
                "DHW_ELASTIC_LEGIONELLA_ENABLED",
                "DHW_ELASTIC_LEGIONELLA_ENABLED",
            ),
        ):
            values[name] = bool(
                config.get(
                    getattr(const, f"CONF_{conf}"), getattr(const, f"DEFAULT_{default}")
                )
            )

        # The buffer cooling rate has no single right default: it depends on the
        # tank's size. Leave it unset when the user has not configured one, so
        # the prior is derived from the volume instead of from a 35 L tank's
        # number. `DEFAULT_BUFFER_COOLING_RATE` is kept only so an existing
        # entry that stored it explicitly keeps working.
        if const.CONF_BUFFER_COOLING_RATE not in config:
            values["buffer_cooling_rate"] = 0.0

        # Mixing valve. The mode is validated here rather than trusted, because
        # an unknown string would silently fall through to the unthrottled
        # branch and the user would see no valve behaviour with no explanation.
        mode = config.get(const.CONF_MIXING_VALVE_MODE, mixing_valve.MODE_NONE)
        values["mixing_valve_mode"] = (
            mode if mode in mixing_valve.MODES else mixing_valve.MODE_NONE
        )
        values["mixing_valve_target"] = float(
            config.get(
                const.CONF_MIXING_VALVE_TARGET, const.DEFAULT_MIXING_VALVE_TARGET
            )
            or 0.0
        )
        values["buffer_max_temp"] = float(
            config.get(const.CONF_BUFFER_MAX_TEMP, const.DEFAULT_BUFFER_MAX_TEMP)
        )
        values["comfort_ceiling"] = float(
            config.get(const.CONF_MAX_TEMP, const.DEFAULT_MAX_TEMP)
        )
        # The COP penalty only means anything when a valve can actually charge
        # the tank, so it follows the mode rather than being separately switched.
        values["cop_flow_carnot"] = mixing_valve.is_throttling(
            values["mixing_valve_mode"]
        )

        # Two-tank gating (issue #40): a probe, not a flag. The volume shares
        # the external-heat detector's key — one number for one physical tank.
        values["wood_tank_configured"] = bool(
            config.get(const.CONF_WOOD_TANK_TOP_ENTITY)
        )
        values["wood_tank_volume"] = float(
            config.get(const.CONF_WOOD_TANK_VOLUME)
            or const.DEFAULT_WOOD_TANK_VOLUME
        )
        values["dhw_wood_coil_enabled"] = bool(
            config.get(
                const.CONF_DHW_WOOD_COIL_ENABLED,
                const.DEFAULT_DHW_WOOD_COIL_ENABLED,
            )
        )
        # The stored layout choice (v3.16.0). An unknown string is dropped
        # here rather than carried: the property would refuse it anyway,
        # and carrying it would make diagnostics show a key that does
        # nothing.
        stored_layout = config.get(const.CONF_TOPOLOGY_LAYOUT)
        values["topology_layout_override"] = (
            str(stored_layout)
            if stored_layout
            and str(stored_layout)
            in (
                const.TOPOLOGY_NO_VALVE,
                const.TOPOLOGY_SINGLE_TANK_VALVE,
                const.TOPOLOGY_TWO_TANK_4WAY,
                const.TOPOLOGY_VALVE_UPPER_DIRECT_SLAB,
            )
            else None
        )

        # Two-zone and DHW are inferred from whether their settings are present
        # at all, rather than from a flag, so an entry written before either
        # existed keeps working. The mode key (v4.0.0) is an explicit override
        # on top: presence alone can never turn the model *off*, because the
        # initial flow writes the zone keys into entry.data where the options
        # flow cannot erase them. "auto" — the default, so every entry without
        # the key — is the presence rule unchanged; an unknown value is
        # treated as "auto" rather than silently disabling a running model.
        two_zone_mode = str(
            config.get(const.CONF_TWO_ZONE_MODE, const.DEFAULT_TWO_ZONE_MODE)
        )
        if two_zone_mode == const.TWO_ZONE_MODE_ON:
            values["two_zone_enabled"] = True
        elif two_zone_mode == const.TWO_ZONE_MODE_OFF:
            values["two_zone_enabled"] = False
        else:
            values["two_zone_enabled"] = any(
                key in config
                for key in (
                    const.CONF_UPPER_FLOOR_THERMAL_MASS,
                    const.CONF_LOWER_FLOOR_THERMAL_MASS,
                    const.CONF_INTER_ZONE_TRANSFER,
                    const.CONF_RADIATOR_POWER_FRACTION,
                )
            )
        # A None value does NOT count as presence (v4.0.0 T3): clearing the
        # DHW temperature sensor on the entities page writes the key back as
        # None, and counting that as "configured" phantom-enabled hot water
        # on entries that never had it. An empty string still counts — an
        # empty ``dhw_windows`` legitimately means "learned windows".
        values["dhw_enabled"] = any(
            config.get(key) is not None
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
            # Weekly windows (#3): None unless the spec names days, so the
            # field costs nothing on the flat specs every install has.
            # Parsed with the same call the optimizer will use, so the two
            # structures can never disagree about what was configured.
            values["dhw_weekly_windows"] = parse_weekly_windows(windows_spec)
        except DHWWindowError as err:
            _LOGGER.warning(
                "Invalid DHW window configuration %r (%s); falling back to "
                "always-available hot water",
                windows_spec,
                err,
            )
            values["dhw_windows"] = []
            values["dhw_weekly_windows"] = None

        return cls(**values)


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

    # The live peak guard is holding electric DHW back for the rest of the
    # billed metering window (#7, v4.0.0 T2). Consumed by the same
    # discretionary-DHW suppression gate as external heat; carries no
    # free-heat forecast semantics.
    peak_guard_active: bool = False

    # Measured wood-tank temperature (issue #40). None means "not sensed or
    # not modelled" and reproduces the single-tank abstraction exactly; a
    # value activates the two-tank draw law when the parameters gate it on.
    # None rather than a sentinel temperature so a silent reset is visible.
    wood_tank_temperature: float | None = None


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


def saturation_vapor_pressure(temp_c: float) -> float:
    """Magnus saturation vapour pressure over water, hPa (T5 #54).

    Magnus-Tetens with the WMO coefficients; good to a few hundredths of
    a hPa across the -40..+50 °C span a dwelling can see.
    """
    return 6.112 * math.exp(17.62 * temp_c / (243.12 + temp_c))


def dew_point_for_pressure(vapor_pressure_hpa: float) -> float:
    """The Magnus inverse: temperature at which this pressure saturates."""
    ln = math.log(max(vapor_pressure_hpa, 1e-9) / 6.112)
    return 243.12 * ln / (17.62 - ln)


def mold_safe_room_floor(
    room_temp_c: float,
    indoor_rh_percent: float,
    outdoor_temp_c: float,
    frsi: float,
    surface_rh_limit: float = 0.8,
) -> float:
    """Lowest room temperature keeping the worst surface under mold RH (#54).

    The indoor vapour pressure is taken from the measured room state and
    held constant — cooling the room does not remove moisture. The worst
    surface sits at ``T_out + fRsi (T_room − T_out)``; its RH stays under
    the limit iff the surface stays above the dew point of
    ``e / limit``, which inverts to a closed-form floor on the room:

        T_room ≥ T_out + (T_dew(e / limit) − T_out) / fRsi

    Colder outside means a higher floor (fRsi < 1), which is the physics
    the guard exists for.
    """
    frsi = min(max(frsi, 0.3), 0.98)
    rh = min(max(indoor_rh_percent, 0.0), 100.0) / 100.0
    e = rh * saturation_vapor_pressure(room_temp_c)
    if e <= 1e-9:
        return -100.0  # bone-dry air: no floor at all
    t_surface_min = dew_point_for_pressure(e / max(surface_rh_limit, 0.05))
    return outdoor_temp_c + (t_surface_min - outdoor_temp_c) / frsi


def wood_share(
    wood_temp: float,
    hp_temp: float,
    flow_set: float,
    floor_temp: float,
    margin: float = WOOD_TANK_MIN_MARGIN,
) -> float:
    """Fraction of the emitter draw the 4-way valve takes from the wood tank.

    The valve's priority law is **wood-while-usable** (the owner's ESBE
    setting, recorded in issue #40): draw from the wood tank while it can
    meet the needed flow temperature, shifting to the heat-pump tank as the
    wood side depletes — *not* hotter-tank-first. Three regions, continuous
    in ``w * Q_draw`` across every boundary:

    * ``wood_temp >= flow_set`` — all wood, even when the HP tank is hotter.
    * ``hp_temp > flow_set > wood_temp`` — the maximum-wood blend: the valve
      mixes just enough HP water to reach the curve,
      ``f_w = (hp_temp - flow_set) / (hp_temp - wood_temp)``, derated by how
      much useful heat the wood side still holds above the coldest zone.
      In this region the modelled outlet is ``flow_set``, so
      ``(t_out - hp_temp) / (wood_temp - hp_temp) == f_w`` — the model
      reproduces exactly the blend fraction the displacement estimator
      *measures* at the valve outlet (external_heat.py), one law for both.
    * both at/below the curve — a smooth switch to the hotter source over
      ``margin`` (the same margin below which the estimator calls the mix
      unidentifiable).

    Pure energy-priority ("drain the wood tank first, whatever its
    temperature") was considered and rejected: the Euler availability term
    lets any real tank cover a whole step, so priority degenerates to
    "wood to the floor" even at 30 °C against a 40 °C curve.

    Module-level and pure so the savings baseline can reuse it verbatim —
    two copies of this law would drift the first time one is tuned.
    """
    if wood_temp >= flow_set:
        return 1.0
    if hp_temp > flow_set:
        f_w = (hp_temp - flow_set) / (hp_temp - wood_temp)
        useful = max(0.0, wood_temp - floor_temp)
        span = max(flow_set - floor_temp, 1e-6)
        return min(1.0, max(0.0, f_w * useful / span))
    return min(1.0, max(0.0, (wood_temp - hp_temp) / max(margin, 1e-6)))


def _wood_share_vec(
    wood_temp: np.ndarray,
    hp_temp: np.ndarray,
    flow_set: float,
    floor_temp: np.ndarray,
    margin: float = WOOD_TANK_MIN_MARGIN,
) -> np.ndarray:
    """``wood_share`` element-wise for the batched trajectory (issue #97).

    The three regions are disjoint, so every element's value comes from
    exactly one region's formula -- computed on guarded denominators and
    selected with ``np.where``, which is bitwise-faithful to the scalar
    law for each element (the guard never touches the region that
    element actually lands in).
    """
    r1 = wood_temp >= flow_set
    r2 = (~r1) & (hp_temp > flow_set)
    # Region 2: the maximum-wood blend. span is per element (floor_temp
    # varies across the batch), guarded so the division never sees the
    # denominator of a region this element is not in.
    denom2 = np.where(r2, hp_temp - wood_temp, 1.0)
    f_w = np.where(r2, (hp_temp - flow_set) / denom2, 0.0)
    useful = np.maximum(0.0, wood_temp - floor_temp)
    span = np.maximum(flow_set - floor_temp, 1e-6)
    v2 = np.minimum(1.0, np.maximum(0.0, f_w * useful / span))
    # Region 3: the smooth switch to the hotter source.
    v3 = np.minimum(
        1.0,
        np.maximum(0.0, (wood_temp - hp_temp) / max(margin, 1e-6)),
    )
    return np.where(r1, 1.0, np.where(r2, v2, v3))


def dhw_coil_draw_reduction(
    draw_kw: float,
    wood_temp: float,
    dhw_setpoint: float,
    inlet_temp: float = DHW_COLD_WATER_TEMP,
) -> tuple[float, float]:
    """The DHW draw after the wood-tank refill coil, and the coil's heat.

    The owner's DHW tank refills through a coil immersed in the wood tank
    (v3.15.1): cold mains water enters at ``inlet_temp`` and
    leaves the coil at ``mains + ε·(T_wood − mains)⁺``, never usefully
    hotter than the DHW setpoint the draw model heats to. The draw the
    electric side must cover scales with the remaining temperature rise,
    and the exact difference is the heat the coil pulled from the wood
    tank — the two are one identity, so conservation holds by
    construction.

    ``inlet_temp`` must be the same reference the draw itself was computed
    from — ``ThermalParameters.dhw_inlet_reference`` at every real call
    site. Hard-coding ``DHW_COLD_WATER_TEMP`` here while the draw used the
    live/seasonal inlet split a (setpoint − 4 °C)-sized winter draw with
    10 °C-based ratios: the identity still held arithmetically but both
    halves were misallocated between the wood tank and the electric side.
    The default keeps the annual-mean configuration byte-identical.

    Returns ``(reduced_draw_kw, coil_heat_kw)`` with
    ``reduced + coil == draw`` exactly. Pure and module-level so the
    savings baseline prices the same coil the simulation runs.
    """
    if draw_kw <= 0.0:
        return draw_kw, 0.0
    t_in = inlet_temp + DHW_WOOD_COIL_EFFECTIVENESS * max(
        0.0, wood_temp - inlet_temp
    )
    t_in = min(t_in, dhw_setpoint)
    span = max(dhw_setpoint - inlet_temp, 1e-6)
    reduced = draw_kw * max(0.0, dhw_setpoint - t_in) / span
    return reduced, draw_kw - reduced


class _StaleTrajectory(np.ndarray):
    """A poison array left on the ``last_*_trajectory`` side-channels by
    ``simulate_trajectory_batch``.

    The batch returns every row's buffer/wood trajectory in its result dict,
    so it has no single trajectory to publish on the scalar path's
    ``last_buffer_trajectory`` / ``last_wood_trajectory`` attributes -- yet it
    used to leave whatever the previous scalar ``simulate_trajectory`` wrote
    there, so any code reading the attribute after a batch call silently got a
    trajectory belonging to a different power schedule. That is a quiet
    correctness trap.

    This sentinel makes the contract explicit and safe: the batch overwrites
    the attributes with a poison value that reads fine when merely stored or
    identity-checked, but raises loudly the instant anyone tries to USE it as
    a trajectory (index it, or do arithmetic on it). The message points the
    caller at the batch result dict, which carries the per-row trajectories.
    """

    def __new__(cls):
        return np.empty(0, dtype=float).view(cls)

    @staticmethod
    def _boom(*_a, **_k):
        raise RuntimeError(
            "last_buffer_trajectory/last_wood_trajectory were poisoned by "
            "simulate_trajectory_batch: the batch has no single scalar "
            "trajectory to publish -- read the per-row 'buffer'/'wood' arrays "
            "from the batch result dict instead. Call simulate_trajectory for "
            "a fresh scalar side-channel before reading these attributes."
        )

    def __array_function__(self, *_a, **_k):
        self._boom()

    def __array_ufunc__(self, *_a, **_k):
        self._boom()

    def __getitem__(self, _key):
        self._boom()

    def __len__(self):
        self._boom()

    def __iter__(self):
        self._boom()


#: Singleton poison written by the batch. It is a distinct object so callers
#: may still cheaply test ``x is _STALE_TRAJECTORY`` without tripping it.
_STALE_TRAJECTORY = _StaleTrajectory()


class ThermalModel:
    """Thermal model supporting single-zone, two-zone, and DHW operation."""

    #: Buffer trajectory of the last `simulate_trajectory` call.
    last_buffer_trajectory: np.ndarray | None = None
    #: Heat (kW) the buffer cap refused per step of that call. The clamp in
    #: `_simulate_step_two_zone` deletes heat that would push the tank past
    #: its safe ceiling; the optimizer's hard-cap loop reads this to find the
    #: steps that tried, because a plan that pays for deleted heat is merely
    #: wasteful in the model but boils the tank on the real system.
    last_buffer_refused: np.ndarray | None = None
    #: Per-step scratch for the above, written by the step function.
    _step_buffer_refused: float = 0.0
    #: Wood-tank trajectory of the last trajectory call, ``None`` whenever
    #: the two-tank topology is not being simulated (issue #40).
    last_wood_trajectory: np.ndarray | None = None
    #: DHW analogue of the buffer's refused-heat ledger (v4.0.5). The DHW
    #: step now clamps charging at the tank rating instead of trusting every
    #: caller to pre-clamp, and heat the rating refuses is booked here (kW)
    #: rather than silently deleted — the same reasoning as the buffer: a
    #: trajectory that pays for deleted heat is merely wasteful in the model
    #: but boils the tank on the real system.
    _step_dhw_refused: float = 0.0
    #: Heat the inlet floor would have had to fabricate this step (kW). With
    #: the temperature-dependent draw the floor is a genuine no-op safety
    #: bound — the draw vanishes as the tank approaches the inlet — so any
    #: non-zero value here is a conservation bug, and the tests assert it.
    _step_dhw_floor_injected: float = 0.0
    #: The draw the DHW step actually debited (kW), after tank-temperature
    #: scaling. Recorded so energy accounting outside the model can balance
    #: the step exactly instead of assuming the nominal demand was met.
    _step_dhw_draw_kw: float = 0.0
    #: Per-step refused DHW heat of the last `simulate_trajectory_with_dhw`.
    last_dhw_refused: np.ndarray | None = None

    def __init__(self, params: ThermalParameters) -> None:
        """Initialize the thermal model."""
        self.params = params

    # ------------------------------------------------------------------
    # Common helpers
    # ------------------------------------------------------------------

    def compute_cop(
        self,
        outdoor_temp: float,
        humidity: float | None = None,
        flow_temp: float | None = None,
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
            # A forecast humidity series marks unknown steps as NaN (#21);
            # those fall back exactly like an absent argument.
            if humidity is not None and not np.isfinite(humidity):
                humidity = None
            if humidity is None:
                humidity = self.params.ambient_humidity
            cop *= derate.factor(outdoor_temp, humidity)
        # Lifting water to a higher flow temperature costs COP. Carnot-derived
        # rather than a fitted %/K: a linear term is fine over the 5-15 K a
        # weather curve moves through, but storage deliberately goes far beyond
        # that, and at 2 %/K a 70 °C flow costs 70 % of COP and hits the floor.
        # A real unit manages 1.5-2.0 there, which the Carnot ratio reproduces
        # because it is the actual shape of the physics.
        if flow_temp is not None and self.params.cop_flow_carnot:
            ref = self.params.cop_flow_reference_temp
            if flow_temp > ref:
                t_out = outdoor_temp + 273.15
                # A minimum lift keeps this finite as outdoor approaches flow.
                carnot_flow = (flow_temp + 273.15) / max(
                    flow_temp + 273.15 - t_out, 1.0
                )
                carnot_ref = (ref + 273.15) / max(ref + 273.15 - t_out, 1.0)
                if carnot_ref > 1e-9:
                    cop *= max(0.25, carnot_flow / carnot_ref)
        return max(cop, 0.5)

    def marginal_cop(
        self,
        outdoor_temp: float,
        store: str,
        store_temp: float | None = None,
        humidity: float | None = None,
    ) -> float:
        """The COP at which one more kWh actually enters a given store.

        One price of heat per (store, temperature, outdoor), shared by the
        simulation and by every terminal/deferred valuation. The divergence
        this closes (v4.0.5): the simulation charges a throttled buffer tank
        at the flow-derated COP of the tank's own temperature and charges
        the DHW tank at ``compute_cop_dhw``, while the optimizer's
        settlement terms priced every stored kWh at the plain space curve.
        Marginal value below marginal cost means systematic under-charging —
        the solver only stored when the price spread also paid for an
        artificial COP gap that the physics never charged.

        ``store`` is ``"buffer"``, ``"dhw"``, or any of the building-mass
        stores (``"room"``, ``"slab"``, ``"upper"``, ``"lower"``, ``"wood"``),
        which heat at the plain curve. ``store_temp`` is the settlement or
        charge temperature of a tank store; for ``"buffer"`` the
        ``cop_flow_carnot`` gate inside :meth:`compute_cop` makes the derate
        a no-op whenever no valve throttles, so unthrottled paths return the
        plain curve bit for bit.
        """
        if store == "dhw":
            return self.compute_cop_dhw(
                outdoor_temp,
                store_temp if store_temp is not None else self.params.dhw_setpoint,
                humidity=humidity,
            )
        if store == "buffer":
            return self.compute_cop(
                outdoor_temp, humidity=humidity, flow_temp=store_temp
            )
        return self.compute_cop(outdoor_temp, humidity=humidity)

    def compute_cop_dhw(
        self,
        outdoor_temp: float,
        dhw_temp: float,
        humidity: float | None = None,
    ) -> float:
        """Compute heat pump COP for DHW mode.

        DHW requires higher supply temperature (55-65°C vs 35-45°C for space
        heating), so COP is lower.  Rough model:
        COP_dhw ≈ COP_space * 0.7 (penalty for higher supply temp)
        """
        base_cop = self.compute_cop(outdoor_temp, humidity=humidity)
        # Higher DHW temp → lower COP (Carnot-like penalty)
        dhw_penalty = max(0.5, 1.0 - 0.008 * (dhw_temp - 35.0))
        return base_cop * dhw_penalty

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

    def compute_solar_gain(self, solar_radiation: float) -> float:
        """Compute total solar heat gain in kW from solar radiation (W/m²).

        Q_solar = solar_radiation * window_area * orientation_factor * SHGC / 1000

        ``solar_aperture_scale`` is #36's learned correction on the whole
        aperture product — window area, orientation and SHGC are configured
        guesses, and only their product is observable. 1.0 (the default,
        and the value whenever the learning flag is off) is byte-inert.
        """
        p = self.params
        if solar_radiation <= 0:
            return 0.0
        return (
            solar_radiation
            * p.window_area
            * p.solar_orientation_factor
            * p.solar_heat_gain_coefficient
            * p.solar_aperture_scale
            / 1000.0  # W → kW
        )

    def internal_gains_at(self, hour_of_day: float | None) -> float:
        """Internal gains in kW for one hour of the day (#53).

        The learned per-hour profile applies only when it exists AND the
        caller knows the hour; every other combination is the configured
        constant, byte-for-byte the previous behaviour.
        """
        profile = self.params.internal_gains_profile
        if profile is None or hour_of_day is None:
            return self.params.internal_gains
        try:
            return float(profile[int(hour_of_day) % 24])
        except (TypeError, ValueError, IndexError):
            return self.params.internal_gains

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
        # "Fully charged" means the everyday charge limit, not the rating: a
        # disinfection cycle is a few hours a week, and sizing the pre-heat
        # horizon off a temperature the tank only sees during one would
        # over-state how far ahead ordinary hot water may be bought.
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
        self._step_dhw_refused = 0.0
        self._step_dhw_floor_injected = 0.0
        self._step_dhw_draw_kw = 0.0
        C_dhw = p.dhw_tank_thermal_mass
        if C_dhw < 0.01:
            return dhw_temp

        # Heat input from heat pump
        q_in = dhw_power_thermal

        # Heat drawn by consumption. The passed/pattern value is the NOMINAL
        # demand — volume heated from the inlet to the setpoint — and that is
        # what a tank at or above the setpoint genuinely supplies: mixing at
        # the tap shrinks the drawn volume so the enthalpy removed stays
        # exactly nominal (the `MixedHotWater` convention,
        # coordinator._dhw_mixed_water). A colder tank cannot be debited
        # energy referenced to a rise it does not hold, so the debit scales
        # with the rise it can actually deliver:
        #
        #     q_eff = q_nominal · min(1, (T − inlet) / (T_use − inlet))
        #
        # with T_use the 40 °C mixed-water temperature: the tap draws MORE
        # volume from a cooler tank to make the same mixed water, so the
        # enthalpy removed stays exactly nominal all the way down to T_use,
        # and only below it does the service itself degrade. Referencing the
        # setpoint instead under-debited the 40..setpoint band — the very
        # band cost optimization rides — by up to a third, and booked the
        # deleted demand as savings (v4.0.5 review, blocker). Unscaled, a
        # 30 °C tank was charged the full (setpoint − inlet) per litre and
        # the inlet floor below silently refunded the fabricated deficit.
        # Demand-side quantities (planner ready-energy targets, the
        # always-hot baseline) stay nominal on purpose: what the user wants
        # delivered does not shrink because the tank is cold.
        q_draw = (
            self.dhw_draw_rate(hour_of_day) if draw_power is None else draw_power
        )
        span = max(DHW_MIXED_USE_TEMP - p.dhw_inlet_reference, 1e-6)
        q_draw = q_draw * min(
            1.0,
            max(0.0, dhw_temp - p.dhw_inlet_reference) / span,
        )
        self._step_dhw_draw_kw = q_draw

        # Standby heat loss to ambient
        q_loss = p.dhw_tank_heat_loss_coefficient * (dhw_temp - ambient_temp)

        # Temperature change
        dT = (q_in - q_draw - q_loss) / C_dhw

        # The tank rating, enforced in the model itself rather than trusted
        # to every caller's pre-clamp: the optimizer's `_clamp_dhw_to_capacity`
        # protects planned schedules, but the published trajectory also
        # replays pinned plans and legionella boosts, and those paths could
        # exceed the rating with no accounting. Same shape as the buffer
        # clamp: only the charging direction is limited (a tank read above
        # the rating cools at its physical rate, it is not snapped down),
        # and the refused heat is booked, never deleted.
        # The *rating*, not the everyday charge limit: a disinfection boost is
        # meant to go above the user's charge limit, and clamping it here
        # would make the cycle silently fail to reach temperature. The
        # everyday limit is enforced per step by the planner instead.
        dT_cap = max(0.0, p.dhw_hard_max_temp - dhw_temp) / max(dt_hours, 1e-6)
        if dT > dT_cap:
            self._step_dhw_refused = (dT - dT_cap) * C_dhw
            dT = dT_cap
        new_temp = dhw_temp + dT * dt_hours

        # Physical bounds (can't go below the cold water inlet). With the
        # scaled draw this floor is a genuine no-op safety bound — the draw
        # vanishes as the tank approaches the inlet, and the tank's ambient
        # (20 °C) sits above the inlet so standby "loss" warms a colder tank.
        # Any heat it does have to fabricate is booked so the energy balance
        # stays honest instead of silently created.
        floor = p.dhw_inlet_reference
        if new_temp < floor:
            self._step_dhw_floor_injected = (
                (floor - new_temp) * C_dhw / max(dt_hours, 1e-6)
            )
            new_temp = floor

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
        external_heat_kw: float = 0.0,
        humidity: float | None = None,
        hour_of_day: float | None = None,
    ) -> ThermalState:
        """Simulate one step with the original single-zone model."""
        p = self.params
        cop = self.compute_cop(outdoor_temp, humidity=humidity)
        # Free thermal input (a wood furnace, item 28) joins the pump's output
        # at the hydronic mix. It is heat, not electricity, so it never touches
        # the COP and costs the plan nothing.
        thermal_power = cop * electrical_power + max(0.0, external_heat_kw)

        u_eff = self.effective_heat_loss_coefficient(
            p.heat_loss_coefficient, wind_speed, precipitation
        )
        q_slab_to_room = p.slab_heat_transfer * (
            state.slab_temperature - state.room_temperature
        )
        q_loss = u_eff * (state.room_temperature - outdoor_temp)
        # Attribute read on the default path: this runs thousands of times
        # per solve, and the trajectory loops only pass an hour when a
        # learned profile exists.
        q_internal = (
            self.internal_gains_at(hour_of_day)
            if hour_of_day is not None
            else p.internal_gains
        )
        q_solar = self.compute_solar_gain(solar_radiation)

        dT_room = (q_slab_to_room - q_loss + q_internal + q_solar) / p.room_thermal_mass
        dT_slab = (thermal_power - q_slab_to_room) / p.slab_thermal_mass

        new_room = state.room_temperature + dT_room * dt_hours
        new_slab = state.slab_temperature + dT_slab * dt_hours

        # ``replace`` carries every field not overridden — enumerating them
        # here silently reset the legionella clock and the external-heat flag
        # to their defaults on every simulated step.
        return replace(
            state,
            room_temperature=new_room,
            slab_temperature=new_slab,
            outdoor_temperature=outdoor_temp,
            upper_floor_temperature=new_room,
            lower_floor_temperature=new_room,
            solar_radiation=solar_radiation,
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
        external_heat_kw: float = 0.0,
        valve_target: float | None = None,
        humidity: float | None = None,
        hour_of_day: float | None = None,
    ) -> ThermalState:
        """Simulate one step with the two-zone model including buffer tank.

        State vector: [T_upper, T_lower, T_slab, T_buffer]
        """
        p = self.params
        throttled = mixing_valve.is_throttling(p.mixing_valve_mode)
        # Two-tank topology (issue #40): active only when the parameters gate
        # it on AND a real wood temperature is in the state. With either
        # missing, everything below reduces byte-for-byte to the single-tank
        # abstraction, wood heat and all — which is also the stale-probe
        # fallback: free heat is routed into the HP tank rather than dropped.
        two_tank = (
            throttled
            and p.two_tank_modelled
            and state.wood_tank_temperature is not None
        )
        # With a valve the pump is charging the tank, so the tank temperature is
        # the flow temperature and charging it hotter costs COP. That coupling is
        # the entire economics of storing heat; without it storage looks free.
        # In the two-tank model this is the HP tank's own temperature — the
        # fix issue #40 exists for: a wood burn heats the *wood* tank, so it
        # can no longer penalize the modelled COP or eat cap headroom.
        cop = self.compute_cop(
            outdoor_temp,
            humidity=humidity,
            flow_temp=state.buffer_tank_temperature if throttled else None,
        )
        # Free thermal input (a wood furnace, item 28) joins the pump's output
        # at the hydronic mix — into the tank when a valve exists, straight to
        # the emitters when not, exactly like the pump's own heat. It is heat,
        # not electricity, so it never touches the COP. When the wood tank is
        # modelled it charges that tank instead (below), never this sum.
        ext = max(0.0, external_heat_kw)
        thermal_power = (
            cop * electrical_power + (0.0 if two_tank else ext)
        )  # total heat into the buffer

        # Weather-adjusted heat loss using configurable sensitivity
        u_upper = self.effective_heat_loss_coefficient(
            p.upper_floor_heat_loss, wind_speed, precipitation
        )
        # Lower floor less exposed to wind (partially underground/sheltered)
        u_lower = self.effective_heat_loss_coefficient(
            p.lower_floor_heat_loss_learned, wind_speed * 0.5, precipitation * 0.5
        )

        # Solar gains per zone
        q_solar_upper, q_solar_lower = self.solar_gain_per_zone(solar_radiation)

        # Internal gains split proportional to area ratio
        area_ratio = p.upper_floor_area_ratio
        q_internal = (
            self.internal_gains_at(hour_of_day)
            if hour_of_day is not None
            else p.internal_gains
        )
        q_internal_upper = q_internal * area_ratio
        q_internal_lower = q_internal * (1.0 - area_ratio)

        T_upper = state.upper_floor_temperature
        T_lower = state.lower_floor_temperature
        T_slab = state.slab_temperature
        T_buf = state.buffer_tank_temperature

        # --- Buffer tank dynamics ---
        C_buf = p.buffer_tank_thermal_mass
        if C_buf < 1e-6:
            C_buf = 0.04  # fallback for 35L

        rad_fraction = p.radiator_power_fraction

        # Buffer tank loss to ambient (assume ~20°C ambient indoors)
        q_buf_loss = p.buffer_tank_heat_loss_coefficient * (T_buf - 20.0)

        if throttled:
            # --- A valve exists: it regulates flow temperature ----------------
            #
            # The emitter UA is backed out of the nameplate output at a design
            # flow-to-zone difference, so when the valve saturates wide open
            # (tank at or below the curve) this reproduces the delivery the
            # unthrottled branch would give at the design point rather than
            # inventing a new balance.
            design_power = p.max_electrical_power * max(p.cop_nominal, 1.0)
            design_dt = max(p.emitter_design_delta_t, 1.0)
            ua_rad = rad_fraction * design_power / design_dt
            ua_floor = (1.0 - rad_fraction) * design_power / design_dt

            # An unconfigured target means the top of the comfort band, as
            # documented everywhere the option is described. A per-step
            # override (`valve_target`) beats both: it is how a commanded
            # valve holds its charge -- the plan lowers the curve between
            # charging and the price peak so the tank keeps its heat for when
            # it is worth most, which a fixed target physically cannot do.
            if valve_target is not None:
                target = float(valve_target)
            else:
                target = p.mixing_valve_target or p.comfort_ceiling
            flow_set = mixing_valve.flow_setpoint(
                target_temp=target,
                outdoor_temp=outdoor_temp,
                heat_loss_coefficient=u_upper + u_lower,
                emitter_ua=ua_rad + ua_floor,
            )
            # The valve mixes return water into the flow, so the emitters see
            # the curve temperature, never raw tank water -- that is what makes
            # stored heat leave at house-demand rate instead of dumping within
            # a step. It cannot make water hotter than the tank, so below the
            # curve it saturates wide open. With two tanks the supply side is
            # whichever tank is hotter -- the 4-way valve draws on both.
            supply_temp = (
                max(state.wood_tank_temperature, T_buf) if two_tank else T_buf
            )
            t_mix = min(supply_temp, flow_set)
            q_rad_from_buf = mixing_valve.emitter_delivery(
                mix_temp=t_mix, zone_temp=T_upper, ua=ua_rad
            )
            # In the valve_upper_direct_slab layout (v3.16.0) only the
            # radiator circuit sits behind the valve; the slab drinks raw
            # tank water, so its delivery follows the tank temperature with
            # no curve cap. Its validity predicate excludes a wood probe,
            # so this and the two-tank branch are mutually exclusive by
            # construction. The energy bound below still applies: a direct
            # pipe cannot draw heat the tank does not hold.
            q_floor_from_buf = mixing_valve.emitter_delivery(
                mix_temp=(T_buf if p.slab_fed_direct else t_mix),
                zone_temp=T_slab,
                ua=ua_floor,
            )

            # ...and the tank cannot deliver heat it does not have. Capping the
            # emitters at the curve made the discharge physical for any tank big
            # enough that a step cannot empty it, which is every realistic size
            # -- but a 10 L separator against a 40 K flow-to-room difference
            # still overshoots its own Euler step and goes through zero.
            # Measured before this bound, a 10 L tank coasting from 60 C reached
            # -8.04 C with a 34 K single-step swing.
            #
            # Bound the *energy*, not the temperature: clipping T_buf at a floor
            # while still crediting the emitters conserves nothing and turns the
            # tank into a heat source. The floor is the coldest zone it feeds,
            # which is where `emitter_delivery` reaches zero of its own accord.
            floor_temp = min(T_upper, T_slab)
            drawn = q_rad_from_buf + q_floor_from_buf
            if two_tank:
                # Per-tank energy bounds, the same fix generalized: neither
                # tank can deliver heat it does not have, each judged against
                # its own contents and its own input. Every expression here
                # deliberately mirrors the single-tank branch's arithmetic
                # (same operations, same order, division not reciprocal
                # multiplication) so that at w == 0 this path is
                # bit-identical to it — one ulp of difference moved a
                # 96-step solve into a different basin when this was first
                # written with `* (1/dt)`.
                T_w = state.wood_tank_temperature
                C_w = p.wood_tank_thermal_mass
                q_wood_loss = p.wood_tank_heat_loss_coefficient * (T_w - 20.0)
                w = wood_share(T_w, T_buf, flow_set, floor_temp)
                avail_wood = ext - q_wood_loss + C_w * max(
                    0.0, T_w - floor_temp
                ) / max(dt_hours, 1e-6)
                avail_hp = thermal_power - q_buf_loss + C_buf * max(
                    0.0, T_buf - floor_temp
                ) / max(dt_hours, 1e-6)
                wood_draw = min(w * drawn, max(avail_wood, 0.0))
                # A wood shortfall shifts to the HP side first — the physical
                # valve shift as the wood side depletes — and only what
                # neither tank can back starves the emitters, proportionally.
                hp_draw = min(drawn - wood_draw, max(avail_hp, 0.0))
                delivered = wood_draw + hp_draw
                if drawn > delivered > 0.0:
                    scale = delivered / drawn
                    q_rad_from_buf *= scale
                    q_floor_from_buf *= scale
                elif delivered <= 0.0:
                    q_rad_from_buf = 0.0
                    q_floor_from_buf = 0.0
            else:
                available = thermal_power - q_buf_loss + C_buf * max(
                    0.0, T_buf - floor_temp
                ) / max(dt_hours, 1e-6)
                if drawn > available > 0.0:
                    scale = available / drawn
                    q_rad_from_buf *= scale
                    q_floor_from_buf *= scale
                elif available <= 0.0:
                    q_rad_from_buf = 0.0
                    q_floor_from_buf = 0.0
        else:
            # No valve: whatever the pump makes reaches the emitters. These two
            # sum to `thermal_power` identically, so the tank is a pass-through
            # with a standing loss -- which is a fair model of this topology and
            # remains the default.
            q_rad_from_buf = rad_fraction * thermal_power
            q_floor_from_buf = (1.0 - rad_fraction) * thermal_power

        new_wood = state.wood_tank_temperature
        if two_tank:
            # The HP tank supplies what the emitters received minus the wood
            # side's contribution — written as the single-tank expression
            # plus `wood_draw` so that at w == 0 the bits are identical, and
            # so that per-step conservation is exact by construction. Wood
            # heat charges the wood tank, whose ceiling is a sanity clamp
            # with no refused accounting: nothing the optimizer commands
            # charges that tank, so there is nothing for the cap loop to
            # act on.
            dT_buf = (
                thermal_power - q_rad_from_buf - q_floor_from_buf
                - q_buf_loss + wood_draw
            ) / max(C_buf, 0.01)
            dT_wood = (ext - wood_draw - q_wood_loss) / max(C_w, 0.01)
            dT_wood_cap = max(0.0, WOOD_TANK_MAX_TEMP - T_w) / max(
                dt_hours, 1e-6
            )
            new_wood = T_w + min(dT_wood, dT_wood_cap) * dt_hours
        else:
            dT_buf = (thermal_power - q_rad_from_buf - q_floor_from_buf - q_buf_loss) / max(C_buf, 0.01)
        self._step_buffer_refused = 0.0
        if throttled:
            # Physical ceiling: heat that would push the tank past its safe
            # temperature cannot go there.
            # Charging must not push past the cap — but only the charging
            # direction is clamped. An unconditional min() forced a tank read
            # *above* the cap down to it within one step, deleting the excess
            # stored energy from the model (13.4 kWh in a 15-minute step for a
            # 75 °C reading against a 60 °C cap) instead of letting it cool at
            # its physical rate.
            dT_cap = max(0.0, p.buffer_max_temp - T_buf) / max(dt_hours, 1e-6)
            if dT_buf > dT_cap:
                self._step_buffer_refused = (dT_buf - dT_cap) * max(C_buf, 0.01)
                dT_buf = dT_cap

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

        # Same ``replace`` discipline as the single-zone step: fields not
        # overridden are carried, not reset.
        return replace(
            state,
            room_temperature=avg_room,
            slab_temperature=new_slab,
            outdoor_temperature=outdoor_temp,
            upper_floor_temperature=new_upper,
            lower_floor_temperature=new_lower,
            buffer_tank_temperature=new_buf,
            wood_tank_temperature=new_wood,
            solar_radiation=solar_radiation,
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
        external_heat_kw: float = 0.0,
        valve_target: float | None = None,
        humidity: float | None = None,
        hour_of_day: float | None = None,
    ) -> ThermalState:
        """Simulate one time step (dispatches to single or two-zone).

        ``valve_target`` overrides the configured mixing-valve target for this
        step. The single-zone model has no valve branch, so it is accepted and
        ignored there rather than being a two-zone-only signature.
        ``humidity`` is the step's forecast relative humidity (#21) for the
        defrost derate; ``hour_of_day`` selects the learned internal-gains
        hour (#53). ``None`` for either falls back to the single configured
        value, which is byte-for-byte the previous behaviour.
        """
        # The single-zone path has no buffer cap, so the scratch would
        # otherwise carry a stale value from an earlier two-zone step.
        self._step_buffer_refused = 0.0
        # Explicit-Euler stability: with u·dt/C past ~2 the update
        # overshoots equilibrium and oscillates divergently. The parameter
        # boundary floors the masses, but a floored mass against a large
        # coupling can still land in that regime, so the step is subdivided
        # to the smallest n that brings every store's ratio under the
        # margin. n == 1 — the untouched original arithmetic, bit for bit —
        # for every sane configuration; the fixtures prove it.
        n_sub = self._stability_substeps(wind_speed, precipitation, dt_hours)
        if self.params.two_zone_enabled:
            if n_sub == 1:
                return self._simulate_step_two_zone(
                    state, electrical_power, outdoor_temp,
                    wind_speed, precipitation, solar_radiation, dt_hours,
                    external_heat_kw, valve_target, humidity, hour_of_day,
                )
            refused = 0.0
            for _ in range(n_sub):
                state = self._simulate_step_two_zone(
                    state, electrical_power, outdoor_temp,
                    wind_speed, precipitation, solar_radiation,
                    dt_hours / n_sub,
                    external_heat_kw, valve_target, humidity, hour_of_day,
                )
                refused += self._step_buffer_refused
            # Refused charge is a power (kW); equal sub-steps make the
            # step's figure the plain mean.
            self._step_buffer_refused = refused / n_sub
            return state
        if n_sub == 1:
            return self._simulate_step_single(
                state, electrical_power, outdoor_temp,
                wind_speed, precipitation, solar_radiation, dt_hours,
                external_heat_kw, humidity, hour_of_day,
            )
        for _ in range(n_sub):
            state = self._simulate_step_single(
                state, electrical_power, outdoor_temp,
                wind_speed, precipitation, solar_radiation, dt_hours / n_sub,
                external_heat_kw, humidity, hour_of_day,
            )
        return state

    def _stability_substeps(
        self, wind_speed: float, precipitation: float, dt_hours: float
    ) -> int:
        """Sub-steps needed to keep every store's u·dt/C under the margin.

        Only the four boundary-floored masses are judged: the buffer and
        wood tanks already carry their own energy bounds and dT caps, and a
        genuinely small separator tank is a sane configuration this guard
        must not touch.
        """
        p = self.params
        if p.two_zone_enabled:
            u_upper = self.effective_heat_loss_coefficient(
                p.upper_floor_heat_loss, wind_speed, precipitation
            )
            u_lower = self.effective_heat_loss_coefficient(
                p.lower_floor_heat_loss_learned,
                wind_speed * 0.5,
                precipitation * 0.5,
            )
            worst = max(
                (u_upper + p.inter_zone_transfer) / p.upper_floor_thermal_mass,
                (u_lower + p.inter_zone_transfer + p.slab_heat_transfer)
                / p.lower_floor_thermal_mass,
                p.slab_heat_transfer / p.slab_thermal_mass,
            )
        else:
            u_eff = self.effective_heat_loss_coefficient(
                p.heat_loss_coefficient, wind_speed, precipitation
            )
            worst = max(
                (u_eff + p.slab_heat_transfer) / p.room_thermal_mass,
                p.slab_heat_transfer / p.slab_thermal_mass,
            )
        ratio = worst * dt_hours
        if ratio <= EULER_STABILITY_MAX_RATIO:
            return 1
        return int(np.ceil(ratio / EULER_STABILITY_MAX_RATIO))

    def simulate_trajectory(
        self,
        initial_state: ThermalState,
        power_schedule: np.ndarray,
        outdoor_temps: np.ndarray,
        wind_speeds: np.ndarray | None = None,
        precipitation: np.ndarray | None = None,
        solar_radiation: np.ndarray | None = None,
        dt_hours: float = 0.25,
        external_heat_kw: np.ndarray | None = None,
        valve_targets: np.ndarray | None = None,
        humidity: np.ndarray | None = None,
        start_hour: float | None = None,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Simulate the full trajectory given a power schedule.

        ``external_heat_kw`` is an optional per-step forecast of free thermal
        input (a wood furnace, item 28). ``valve_targets`` is an optional
        per-step mixing-valve target schedule, fully resolved -- every entry a
        real temperature, no sentinel values -- which is how a commanded valve
        holds its charge between cheap hours and the price peak.
        ``humidity`` is the forecast relative humidity per step (#21), for
        the defrost derate. ``None`` for
        any of them is the default and is byte-for-byte the previous
        behaviour.

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
        buffer_temps = np.zeros(n_steps + 1)
        buffer_temps[0] = initial_state.buffer_tank_temperature
        buffer_refused = np.zeros(n_steps)
        wood_temps = None
        if initial_state.wood_tank_temperature is not None:
            wood_temps = np.zeros(n_steps + 1)
            wood_temps[0] = initial_state.wood_tank_temperature

        # The hour only matters when a learned gains profile exists (#53);
        # this loop runs thousands of times per solve, so the per-step
        # modulo is not paid on the default path.
        hours_matter = (
            start_hour is not None
            and self.params.internal_gains_profile is not None
        )

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
                humidity=(
                    float(humidity[i]) if humidity is not None else None
                ),
                hour_of_day=(
                    (start_hour + i * dt_hours) % 24.0
                    if hours_matter
                    else None
                ),
            )
            room_temps[i + 1] = state.room_temperature
            slab_temps[i + 1] = state.slab_temperature
            upper_temps[i + 1] = state.upper_floor_temperature
            lower_temps[i + 1] = state.lower_floor_temperature
            buffer_temps[i + 1] = state.buffer_tank_temperature
            buffer_refused[i] = self._step_buffer_refused
            if wood_temps is not None:
                wood_temps[i + 1] = state.wood_tank_temperature

        # Recorded rather than returned: nine call sites unpack a four-tuple,
        # and the buffer is only wanted by the terminal-cost term. Without this
        # the tank's end state is invisible to the objective, so charging it can
        # only ever look like cost.
        self.last_buffer_trajectory = buffer_temps
        self.last_buffer_refused = buffer_refused
        self.last_wood_trajectory = wood_temps
        return room_temps, slab_temps, upper_temps, lower_temps

    def simulate_trajectory_batch(
        self,
        initial_state: ThermalState,
        power_matrix: np.ndarray,
        outdoor_temps: np.ndarray,
        wind_speeds: np.ndarray | None = None,
        precipitation: np.ndarray | None = None,
        solar_radiation: np.ndarray | None = None,
        dt_hours: float = 0.25,
        external_heat_kw: np.ndarray | None = None,
        valve_targets: np.ndarray | None = None,
        humidity: np.ndarray | None = None,
        start_hour: float | None = None,
    ) -> dict[str, np.ndarray]:
        """Simulate B trajectories at once: ``power_matrix`` is [B, n].

        The vectorized twin of ``simulate_trajectory``, built for the
        solver's finite-difference gradient (issue #97): the 97 perturbed
        schedules a gradient costs are simulated as one batch, cutting the
        gradient's simulation cost from 97 sequential scalar loops to one
        vectorized one.

        **Bitwise parity is the contract.** Every row must equal what the
        scalar path produces for the same schedule, to the last bit -- the
        solver's iterates depend on it, and the equivalence harness in
        tests/features.py plus the drift gate hold it. The rules that make
        that true: ``min``/``max`` become ``np.minimum``/``np.maximum``
        (IEEE-identical for the finite values states carry), branch
        conditionals become ``np.where`` selections of already-computed
        values (never re-associated arithmetic), and every expression keeps
        the scalar code's exact operation order -- the comments in the
        two-zone step about division-vs-reciprocal ulps apply here doubly.

        Returns dict of arrays shaped [B, n+1]: room, slab, upper, lower,
        buffer, wood (None when not modelled), plus refused [B, n].
        """
        p = self.params
        power_matrix = np.asarray(power_matrix, dtype=float)
        n_steps = power_matrix.shape[1]
        if wind_speeds is None:
            wind_speeds = np.zeros(n_steps)
        if precipitation is None:
            precipitation = np.zeros(n_steps)
        if solar_radiation is None:
            solar_radiation = np.zeros(n_steps)

        room = np.zeros((power_matrix.shape[0], n_steps + 1))
        slab = np.zeros_like(room)
        upper = np.zeros_like(room)
        lower = np.zeros_like(room)
        buf = np.zeros_like(room)
        refused = np.zeros((power_matrix.shape[0], n_steps))
        wood = None
        if initial_state.wood_tank_temperature is not None:
            wood = np.zeros_like(room)
            wood[:, 0] = initial_state.wood_tank_temperature
        room[:, 0] = initial_state.room_temperature
        slab[:, 0] = initial_state.slab_temperature
        upper[:, 0] = initial_state.upper_floor_temperature
        lower[:, 0] = initial_state.lower_floor_temperature
        buf[:, 0] = initial_state.buffer_tank_temperature

        throttled = mixing_valve.is_throttling(p.mixing_valve_mode)
        # Uniform across the batch by construction: every row shares the
        # initial state, so the wood probe's presence cannot vary per row.
        two_tank = (
            throttled
            and p.two_tank_modelled
            and initial_state.wood_tank_temperature is not None
        )
        hours_matter = (
            start_hour is not None and p.internal_gains_profile is not None
        )
        # Configuration constants hoisted out of the step (uniform per batch).
        C_buf = p.buffer_tank_thermal_mass
        if C_buf < 1e-6:
            C_buf = 0.04
        C_buf_div = max(C_buf, 0.01)
        rad_fraction = p.radiator_power_fraction
        area_ratio = p.upper_floor_area_ratio
        q_internal_upper_base = None
        # Two-zone valve geometry: uniform per batch.
        if p.two_zone_enabled and throttled:
            design_power = p.max_electrical_power * max(p.cop_nominal, 1.0)
            design_dt = max(p.emitter_design_delta_t, 1.0)
            ua_rad = rad_fraction * design_power / design_dt
            ua_floor = (1.0 - rad_fraction) * design_power / design_dt
        if two_tank:
            C_w = p.wood_tank_thermal_mass
            C_w_div = max(C_w, 0.01)

        T_upper = upper[:, 0].copy()
        T_lower = lower[:, 0].copy()
        T_slab = slab[:, 0].copy()
        T_buf = buf[:, 0].copy()
        T_wood = wood[:, 0].copy() if wood is not None else None
        # The single-zone branch carries the room as its own state (the
        # scalar step sets upper/lower to it rather than the other way
        # round), so it is seeded here beside the rest. It used to be seeded
        # lazily inside the step loop under `if i == 0`, which re-seeded it
        # from the initial state on every sub-step of step 0 and threw away
        # the sub-steps already taken.
        T_room = room[:, 0].copy()

        for i in range(n_steps):
            out_i = outdoor_temps[i]
            wind_i = float(wind_speeds[i])
            rain_i = float(precipitation[i])
            sol_i = float(solar_radiation[i])
            power_i = power_matrix[:, i]
            ext_i = (
                float(external_heat_kw[i])
                if external_heat_kw is not None
                else 0.0
            )
            ext = np.maximum(0.0, ext_i)
            hum_i = float(humidity[i]) if humidity is not None else None
            hour_i = (
                (start_hour + i * dt_hours) % 24.0
                if hours_matter
                else None
            )

            n_sub = self._stability_substeps(wind_i, rain_i, dt_hours)
            # Uniform across the batch: substeps depend on weather and
            # dt only. The scalar path subdivides the same way; the
            # refused figure averages over substeps exactly as it does.
            refused_acc = np.zeros_like(buf[:, 0])
            for _sub in range(n_sub):
                dt = dt_hours / n_sub
                if p.two_zone_enabled:
                    u_upper = self.effective_heat_loss_coefficient(
                        p.upper_floor_heat_loss, wind_i, rain_i
                    )
                    u_lower = self.effective_heat_loss_coefficient(
                        p.lower_floor_heat_loss_learned, wind_i * 0.5, rain_i * 0.5
                    )
                    q_solar_upper, q_solar_lower = self.solar_gain_per_zone(sol_i)
                    q_internal = (
                        self.internal_gains_at(hour_i)
                        if hour_i is not None
                        else p.internal_gains
                    )
                    q_int_up = q_internal * area_ratio
                    q_int_lo = q_internal * (1.0 - area_ratio)
                    q_buf_loss = p.buffer_tank_heat_loss_coefficient * (
                        T_buf - 20.0
                    )
                    # COP: only the flow-temp correction varies per element.
                    # The scalar path computes cop = nameplate*factor*scale
                    # [*derate] [*carnot]; replicate the exact order with the
                    # per-element carnot factor applied where the scalar does.
                    delta = out_i - p.cop_reference_temp
                    factor = max(0.3, 1.0 + 0.025 * delta)
                    cop = p.cop_nominal * min(factor, 1.5) * p.cop_scale
                    derate = p.defrost_derate
                    if derate is not None:
                        if hum_i is not None and not np.isfinite(hum_i):
                            hum_i = None
                        if hum_i is None:
                            hum_i = p.ambient_humidity
                        cop = cop * derate.factor(out_i, hum_i)
                    if throttled and p.cop_flow_carnot:
                        ref = p.cop_flow_reference_temp
                        t_out = out_i + 273.15
                        carnot_flow = (T_buf + 273.15) / np.maximum(
                            T_buf + 273.15 - t_out, 1.0
                        )
                        carnot_ref = (ref + 273.15) / max(ref + 273.15 - t_out, 1.0)
                        if carnot_ref > 1e-9:
                            # The scalar applies the lift cost only ABOVE the
                            # reference flow temperature; below it the term is
                            # skipped, not clipped -- a below-ref tank must not
                            # earn a COP boost it never gets.
                            carnot_mult = np.where(
                                T_buf > ref,
                                np.maximum(0.25, carnot_flow / carnot_ref),
                                1.0,
                            )
                            cop = cop * carnot_mult
                    cop = np.maximum(cop, 0.5)
                    thermal_power = (
                        cop * power_i + (0.0 if two_tank else ext)
                    )
                    if throttled:
                        target = (
                            float(valve_targets[i])
                            if valve_targets is not None
                            else (p.mixing_valve_target or p.comfort_ceiling)
                        )
                        flow_set = mixing_valve.flow_setpoint(
                            target_temp=target,
                            outdoor_temp=out_i,
                            heat_loss_coefficient=u_upper + u_lower,
                            emitter_ua=ua_rad + ua_floor,
                        )
                        supply = (
                            np.maximum(T_wood, T_buf) if two_tank else T_buf
                        )
                        t_mix = np.minimum(supply, flow_set)
                        q_rad = np.maximum(0.0, ua_rad * (t_mix - T_upper))
                        q_floor = np.maximum(
                            0.0,
                            ua_floor
                            * ((T_buf if p.slab_fed_direct else t_mix) - T_slab),
                        )
                        floor_temp = np.minimum(T_upper, T_slab)
                        drawn = q_rad + q_floor
                        if two_tank:
                            q_wood_loss = p.wood_tank_heat_loss_coefficient * (
                                T_wood - 20.0
                            )
                            w = _wood_share_vec(
                                T_wood, T_buf, flow_set, floor_temp
                            )
                            avail_wood = ext - q_wood_loss + C_w * np.maximum(
                                0.0, T_wood - floor_temp
                            ) / max(dt, 1e-6)
                            avail_hp = (
                                thermal_power
                                - q_buf_loss
                                + C_buf
                                * np.maximum(0.0, T_buf - floor_temp)
                                / max(dt, 1e-6)
                            )
                            wood_draw = np.minimum(
                                w * drawn, np.maximum(avail_wood, 0.0)
                            )
                            hp_draw = np.minimum(
                                drawn - wood_draw, np.maximum(avail_hp, 0.0)
                            )
                            delivered = wood_draw + hp_draw
                        else:
                            available = (
                                thermal_power
                                - q_buf_loss
                                + C_buf
                                * np.maximum(0.0, T_buf - floor_temp)
                                / max(dt, 1e-6)
                            )
                            delivered = np.minimum(
                                drawn, np.maximum(available, 0.0)
                            )
                        # The scalar three-way branch, as multiplicative
                        # selectors on already-computed values: bit-identical
                        # in every arm (q*scale, q*1.0, or 0.0 exactly). The
                        # division guards drawn==0 -- np.where evaluates both
                        # arms, and an unguarded 0/0 NaN would poison states
                        # through the subsequent multiplications.
                        cond_scale = (drawn > delivered) & (delivered > 0.0)
                        drawn_safe = np.where(drawn > 0.0, drawn, 1.0)
                        scale = np.where(cond_scale, delivered / drawn_safe, 1.0)
                        zero = np.where(delivered <= 0.0, 0.0, 1.0)
                        q_rad = q_rad * scale * zero
                        q_floor = q_floor * scale * zero
                    else:
                        q_rad = rad_fraction * thermal_power
                        q_floor = (1.0 - rad_fraction) * thermal_power

                    if two_tank:
                        # One expression, exactly as the scalar step writes it:
                        # the wood_draw joins the numerator before the division,
                        # never as a separate add of quotients -- that
                        # re-association is a different float (the ulp class the
                        # scalar comment here warns about).
                        dT_buf = (
                            thermal_power
                            - q_rad
                            - q_floor
                            - q_buf_loss
                            + wood_draw
                        ) / C_buf_div
                        dT_wood = (ext - wood_draw - q_wood_loss) / C_w_div
                        dT_wood_cap = np.maximum(
                            0.0, WOOD_TANK_MAX_TEMP - T_wood
                        ) / max(dt, 1e-6)
                        T_wood = T_wood + np.minimum(
                            dT_wood, dT_wood_cap
                        ) * dt
                    else:
                        dT_buf = (
                            thermal_power - q_rad - q_floor - q_buf_loss
                        ) / C_buf_div
                    pass  # refused handled after the substep below
                    if throttled:
                        dT_cap = np.maximum(
                            0.0, p.buffer_max_temp - T_buf
                        ) / max(dt, 1e-6)
                        over = dT_buf > dT_cap
                        # Accumulated per substep, averaged at record time --
                        # exactly the scalar path's refused += / n_sub.
                        refused_acc = refused_acc + np.where(
                            over, (dT_buf - dT_cap) * C_buf_div, 0.0
                        )
                        dT_buf = np.where(over, dT_cap, dT_buf)

                    q_slab_to_lower = p.slab_heat_transfer * (T_slab - T_lower)
                    dT_slab = (
                        q_floor - q_slab_to_lower
                    ) / p.slab_thermal_mass
                    q_inter = p.inter_zone_transfer * (T_lower - T_upper)
                    q_loss_upper = u_upper * (T_upper - out_i)
                    dT_upper = (
                        q_rad - q_loss_upper + q_inter + q_solar_upper + q_int_up
                    ) / p.upper_floor_thermal_mass
                    q_loss_lower = u_lower * (T_lower - out_i)
                    dT_lower = (
                        q_slab_to_lower
                        - q_loss_lower
                        - q_inter
                        + q_solar_lower
                        + q_int_lo
                    ) / p.lower_floor_thermal_mass
                    T_upper = T_upper + dT_upper * dt
                    T_lower = T_lower + dT_lower * dt
                    T_slab = T_slab + dT_slab * dt
                    T_buf = T_buf + dT_buf * dt
                    avg_room = T_upper * area_ratio + T_lower * (1.0 - area_ratio)
                    room[:, i + 1] = avg_room
                    slab[:, i + 1] = T_slab
                    upper[:, i + 1] = T_upper
                    lower[:, i + 1] = T_lower
                    buf[:, i + 1] = T_buf
                    if wood is not None:
                        wood[:, i + 1] = T_wood
                    refused[:, i] = refused_acc / n_sub
                else:
                    # Single-zone twin of _simulate_step_single. The room is
                    # its own state here (upper/lower are set to it by the
                    # scalar step), so it carries its own initial value --
                    # starting it from the upper-floor field is the classic
                    # parity bug when the two differ in the initial state.
                    # T_room is seeded with the other states above the step
                    # loop and carried across sub-steps from there.
                    delta = out_i - p.cop_reference_temp
                    factor = max(0.3, 1.0 + 0.025 * delta)
                    cop = p.cop_nominal * min(factor, 1.5) * p.cop_scale
                    derate = p.defrost_derate
                    if derate is not None:
                        if hum_i is not None and not np.isfinite(hum_i):
                            hum_i = None
                        if hum_i is None:
                            hum_i = p.ambient_humidity
                        cop = cop * derate.factor(out_i, hum_i)
                    cop = np.maximum(cop, 0.5)
                    thermal_power = cop * power_i + ext
                    u_eff = self.effective_heat_loss_coefficient(
                        p.heat_loss_coefficient, wind_i, rain_i
                    )
                    q_slab_to_room = p.slab_heat_transfer * (T_slab - T_room)
                    q_loss = u_eff * (T_room - out_i)
                    q_internal = (
                        self.internal_gains_at(hour_i)
                        if hour_i is not None
                        else p.internal_gains
                    )
                    q_solar = self.compute_solar_gain(sol_i)
                    dT_room = (
                        q_slab_to_room - q_loss + q_internal + q_solar
                    ) / p.room_thermal_mass
                    dT_slab = (
                        thermal_power - q_slab_to_room
                    ) / p.slab_thermal_mass
                    # dt, not dt_hours: this is one sub-step of the
                    # stability subdivision, exactly as _simulate_step_single
                    # takes it. Integrating n_sub sub-steps at the full step
                    # length is the divergence the guard exists to prevent.
                    T_room = T_room + dT_room * dt
                    T_slab = T_slab + dT_slab * dt
                    room[:, i + 1] = T_room
                    slab[:, i + 1] = T_slab
                    upper[:, i + 1] = T_room
                    lower[:, i + 1] = T_room
                    buf[:, i + 1] = T_buf
                    if wood is not None:
                        wood[:, i + 1] = T_wood

        # The batch has no single scalar trajectory to publish on the
        # ``last_*_trajectory`` side-channels the scalar path maintains: every
        # row's buffer/wood trajectory is in the result dict below. Leaving the
        # attributes holding a previous scalar call's arrays let a later read
        # silently pick up a trajectory for a different power schedule, so poison
        # them -- a stale read now raises loudly and points at the result dict.
        self.last_buffer_trajectory = _STALE_TRAJECTORY
        self.last_wood_trajectory = _STALE_TRAJECTORY
        return {
            "room": room, "slab": slab, "upper": upper, "lower": lower,
            "buffer": buf, "wood": wood, "refused": refused,
        }

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
        external_heat_kw: np.ndarray | None = None,
        valve_targets: np.ndarray | None = None,
        humidity: np.ndarray | None = None,
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
        buffer_temps = np.zeros(n_steps + 1)
        dhw_refused = np.zeros(n_steps)

        room_temps[0] = initial_state.room_temperature
        slab_temps[0] = initial_state.slab_temperature
        upper_temps[0] = initial_state.upper_floor_temperature
        lower_temps[0] = initial_state.lower_floor_temperature
        dhw_temps[0] = initial_state.dhw_temperature
        buffer_temps[0] = initial_state.buffer_tank_temperature
        wood_temps = None
        if initial_state.wood_tank_temperature is not None:
            wood_temps = np.zeros(n_steps + 1)
            wood_temps[0] = initial_state.wood_tank_temperature

        state = initial_state
        current_hour = start_hour
        # The DHW refill coil (v3.15.1): active only with the two-tank
        # model, and only while the wood state is real. Hoisted so the
        # feature-off path stays byte-identical inside the loop.
        coil = self.params.dhw_coil_active
        # #53: the space step needs its hour only when a learned gains
        # profile exists — hoisted for the same reason as the coil flag.
        gains_hours_matter = self.params.internal_gains_profile is not None

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
                humidity=(
                    float(humidity[i]) if humidity is not None else None
                ),
                hour_of_day=(
                    current_hour % 24.0 if gains_hours_matter else None
                ),
            )

            draw_i = float(dhw_draw_rates[i])
            if coil and state.wood_tank_temperature is not None:
                # Refill water arrives preheated by the wood tank; the coil's
                # heat leaves that tank in the same step, floored at the
                # mains temperature it can never cool below. The mains
                # temperature is the shared inlet reference — the same number
                # the draw was computed from — so the coil's cold-side base
                # and the wood tank's floor are one value, not two.
                draw_i, q_coil = dhw_coil_draw_reduction(
                    draw_i,
                    state.wood_tank_temperature,
                    self.params.dhw_setpoint,
                    inlet_temp=self.params.dhw_inlet_reference,
                )
                if q_coil > 0.0:
                    state.wood_tank_temperature = max(
                        self.params.dhw_inlet_reference,
                        state.wood_tank_temperature
                        - q_coil * dt_hours
                        / max(self.params.wood_tank_thermal_mass, 0.01),
                    )

            # DHW simulation (runs in parallel with space heating)
            cop_dhw = self.compute_cop_dhw(
                outdoor_temps[i],
                state.dhw_temperature,
                humidity=(
                    float(humidity[i]) if humidity is not None else None
                ),
            )
            dhw_thermal_power = cop_dhw * dhw_power_schedule[i]

            new_dhw = self.simulate_dhw_step(
                dhw_temp=state.dhw_temperature,
                dhw_power_thermal=dhw_thermal_power,
                hour_of_day=current_hour % 24.0,
                ambient_temp=DHW_AMBIENT_TEMP,
                dt_hours=dt_hours,
                draw_power=draw_i,
            )
            state.dhw_temperature = new_dhw
            dhw_refused[i] = self._step_dhw_refused

            room_temps[i + 1] = state.room_temperature
            slab_temps[i + 1] = state.slab_temperature
            upper_temps[i + 1] = state.upper_floor_temperature
            lower_temps[i + 1] = state.lower_floor_temperature
            dhw_temps[i + 1] = new_dhw
            buffer_temps[i + 1] = state.buffer_tank_temperature
            if wood_temps is not None:
                wood_temps[i + 1] = state.wood_tank_temperature

            current_hour += dt_hours

        # Recorded on the same attribute as `simulate_trajectory`, which is not
        # decoration: this method used to leave it holding whatever the last
        # space-only simulation put there, so anything reading it afterwards got
        # a trajectory belonging to a different power schedule.
        self.last_buffer_trajectory = buffer_temps
        self.last_wood_trajectory = wood_temps
        self.last_dhw_refused = dhw_refused
        return room_temps, slab_temps, upper_temps, lower_temps, dhw_temps

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