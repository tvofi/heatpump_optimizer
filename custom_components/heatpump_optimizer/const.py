"""Constants for Heat Pump Cost Optimizer."""
from __future__ import annotations

from datetime import timedelta
from typing import Final

DOMAIN: Final = "heatpump_optimizer"
PLATFORMS: Final = ["sensor", "binary_sensor", "button", "climate", "switch"]

# Schema version of the config entry. Bump when stored keys change in a way
# that needs migrating, and handle it in ``async_migrate_entry``.
CONFIG_ENTRY_VERSION: Final = 7

# Configuration keys
CONF_TIBBER_TOKEN: Final = "tibber_token"
CONF_WEATHER_ENTITY: Final = "weather_entity"
CONF_INDOOR_TEMP_ENTITY: Final = "indoor_temp_entity"
CONF_OUTDOOR_TEMP_ENTITY: Final = "outdoor_temp_entity"
CONF_HEAT_PUMP_SWITCH_ENTITY: Final = "heat_pump_switch_entity"

# Two-zone sensor configuration
CONF_SOLAR_RADIATION_ENTITY: Final = "solar_radiation_entity"
CONF_FLOOR_RETURN_TEMP_ENTITY: Final = "floor_return_temp_entity"
# A real thermometer in the lower zone, if the house has one.
#
# Without it the lower zone's *room* temperature is inferred as the floor return
# temperature plus 0.5 K -- a water temperature standing in for an air
# temperature, typically 3-9 K too warm. That value is judged against the same
# comfort bounds as the upper floor, so the zone reads as permanently
# overshooting and the optimizer under-heats the one room it cannot see.
CONF_LOWER_FLOOR_TEMP_ENTITY: Final = "lower_floor_temp_entity"

# Solar irradiance forecast source.
#
# Most Home Assistant weather integrations do not publish irradiance at all, so
# the default path leaves the model with no solar gain to plan against. Open-
# Meteo exposes a free global horizontal irradiance forecast that needs only a
# coordinate, so it can be used instead of (or alongside) a local sensor.
CONF_SOLAR_FORECAST_SOURCE: Final = "solar_forecast_source"
CONF_SOLAR_LOCATION: Final = "solar_location"

SOLAR_SOURCE_WEATHER: Final = "weather"
SOLAR_SOURCE_OPEN_METEO: Final = "open_meteo"
SOLAR_SOURCES: Final = (SOLAR_SOURCE_WEATHER, SOLAR_SOURCE_OPEN_METEO)
DEFAULT_SOLAR_FORECAST_SOURCE: Final = SOLAR_SOURCE_WEATHER

# Forward-looking irradiance. The satellite API is archive-only, so a forecast
# horizon can only come from the regular forecast endpoint.
OPEN_METEO_FORECAST_URL: Final = "https://api.open-meteo.com/v1/forecast"
# Observed (satellite-derived) irradiance for the recent past, which is more
# accurate than the modelled forecast for "what is the sun doing right now".
OPEN_METEO_SATELLITE_URL: Final = "https://satellite-api.open-meteo.com/v1/archive"
OPEN_METEO_SATELLITE_MODEL: Final = "satellite_radiation_seamless"
# Open-Meteo publishes new forecast runs hourly; refreshing faster than this
# spends API quota re-fetching identical numbers.
OPEN_METEO_MIN_REFRESH_MINUTES: Final = 20
OPEN_METEO_TIMEOUT_SECONDS: Final = 15
# How stale an observed satellite sample may be and still count as "now".
OPEN_METEO_OBSERVED_MAX_AGE_MINUTES: Final = 90

# DHW sensor configuration
CONF_DHW_TEMP_ENTITY: Final = "dhw_temp_entity"

# --- Measured electrical draw (item 6) -------------------------------------
#
# ``CONF_HEAT_PUMP_MAX_POWER`` / ``MIN_POWER`` are nameplate limits, and the
# "Recommended Power" sensor publishes what the optimizer is *commanding*.
# Neither is a measurement. An optional real power entity closes that gap: it
# makes COP observable, lets predicted cost be checked against reality, and
# gives the external-heat-source detector its cleanest signal ("the tank is
# heating while the compressor draws nothing").
CONF_POWER_ENTITY: Final = "heat_pump_power_entity"
# Optional cumulative energy meter (kWh). Integrating power over a coarse
# polling interval loses short compressor runs entirely, so a real meter is
# preferred for cost accounting when one exists.
CONF_ENERGY_ENTITY: Final = "heat_pump_energy_entity"
# Whole-house load, needed for a capacity tariff (the peak is metered at the
# house connection, not at the heat pump) and for PV surplus.
CONF_HOUSE_POWER_ENTITY: Final = "house_power_entity"

# Power units the optional entities may report in, normalised to kW. Assuming
# kW because the internal model uses kW misreads a 3000 W draw as 3000 kW.
POWER_UNIT_TO_KW: Final = {
    "W": 0.001,
    "kW": 1.0,
    "MW": 1000.0,
    "mW": 1e-6,
}

# Learned correction to the modelled COP, from measured electrical input
# against modelled thermal output. 1.0 means the COP curve is taken at face
# value. The bounds stop a mis-scaled power entity from destroying the model.
CONF_COP_SCALE: Final = "cop_scale"
DEFAULT_COP_SCALE: Final = 1.0
COP_SCALE_MIN: Final = 0.5
COP_SCALE_MAX: Final = 1.6
# The meter measures electrical input, never delivered heat, so a
# commanded-vs-measured gap is ambiguous: a modest one is efficiency signal,
# a large one means the pump simply is not running the plan (compressor
# limits, cycling, ramp lag) and delivered thermal is unknown. Booking such
# an interval as efficiency wrote tracking error into ``cop_scale`` — and
# from there into every priced plan. Beyond this relative gap the sample is
# discarded as untrustworthy rather than folded (v4.0.5).
COP_TRACKING_ERROR_GATE: Final = 0.3

# --- Input staleness watchdog (item 12) ------------------------------------
#
# Every sensor read is guarded against ``unavailable``/``unknown``, but a dead
# battery or a dropped radio leaves a perfectly valid-looking constant in the
# state machine forever. The optimizer then plans against a fiction, and worse,
# the learners observe a flatline, attribute it to thermal behaviour, and
# persist a corrupted parameter that survives a restart. Fail closed: an
# over-age value is treated as missing, not as data.
CONF_STALENESS_ENABLED: Final = "staleness_watchdog_enabled"
DEFAULT_STALENESS_ENABLED: Final = True
# How much slack to allow on top of the per-input limits, for installs with
# deliberately slow-reporting sensors.
CONF_STALENESS_SCALE: Final = "staleness_max_age_scale"
DEFAULT_STALENESS_SCALE: Final = 1.0
STALENESS_SCALE_MIN: Final = 0.5
STALENESS_SCALE_MAX: Final = 10.0

# Per-input age limits in minutes. A room temperature may reasonably be minutes
# old; an outdoor forecast, hours. These are deliberately generous multiples of
# a normal reporting interval so that a healthy sensor never trips them.
INPUT_MAX_AGE_MINUTES: Final = {
    CONF_INDOOR_TEMP_ENTITY: 60.0,
    CONF_OUTDOOR_TEMP_ENTITY: 180.0,
    CONF_DHW_TEMP_ENTITY: 60.0,
    CONF_FLOOR_RETURN_TEMP_ENTITY: 60.0,
    CONF_SOLAR_RADIATION_ENTITY: 90.0,
    CONF_POWER_ENTITY: 30.0,
    CONF_ENERGY_ENTITY: 180.0,
    CONF_HOUSE_POWER_ENTITY: 30.0,
}
# Buffer tank and other keys defined later in this module are added to the map
# at the bottom of the file, where their names exist.


# --- External heat source detection (item 5) -------------------------------
#
# Defaults to off. Most users have no wood furnace, and a feature that cannot
# save them anything should not be able to cost them anything either.
CONF_EXTERNAL_HEAT_ENABLED: Final = "external_heat_detection_enabled"
CONF_EXTERNAL_HEAT_ENTITY: Final = "external_heat_entity"
CONF_EXTERNAL_HEAT_MIN_RISE: Final = "external_heat_min_rise"  # °C/h
CONF_EXTERNAL_HEAT_DECAY_MINUTES: Final = "external_heat_decay_minutes"

DEFAULT_EXTERNAL_HEAT_ENABLED: Final = False
DEFAULT_EXTERNAL_HEAT_MIN_RISE: Final = 1.5  # °C/h
DEFAULT_EXTERNAL_HEAT_DECAY_MINUTES: Final = 90.0

# --- Wood furnace displacement (item 28) -----------------------------------
#
# Three optional sensors on a wood-furnace topology: the temperature after
# the valve mixing the wood tank and the heat-pump tank, and top/bottom
# probes in the wood tank. The outlet identifies how much of what the house
# receives is coming from the wood side (a continuous 0-1 displacement,
# where the plain detector only knows a boolean), and the tank pair bounds
# how long the fire can keep it up.
CONF_VALVE_OUTLET_TEMP_ENTITY: Final = "valve_outlet_temp_entity"
CONF_WOOD_TANK_TOP_ENTITY: Final = "wood_tank_top_entity"
CONF_WOOD_TANK_BOTTOM_ENTITY: Final = "wood_tank_bottom_entity"
CONF_WOOD_TANK_VOLUME: Final = "wood_tank_volume"  # liters
DEFAULT_WOOD_TANK_VOLUME: Final = 500.0

# The forecast fed to the optimizer is deliberately short-lived, mirroring
# the DHW suppression's hard cap: whatever the detector's own decay says,
# free heat is never promised further ahead than this. A fire is human
# behaviour -- only the decay of one already lit is forecastable, and a
# wrong promise here is a cold house in winter.
EXTERNAL_HEAT_FORECAST_MAX_HOURS: Final = 2.0
# Below this margin between the wood tank and the heat-pump tank the mixing
# fraction is unidentifiable and the displacement reads zero.
WOOD_TANK_MIN_MARGIN: Final = 2.0  # °C
# Sanity ceiling for the modelled wood tank (issue #40). A wood boiler is
# not commanded by the optimizer, so unlike the buffer cap there is no
# refused-heat accounting behind this — it only stops a runaway Euler step
# from planning against steam.
WOOD_TANK_MAX_TEMP: Final = 95.0  # °C

# The temperature people actually use hot water at, after mixing at the tap.
# Shared by the MixedHotWater sensor and the tank's draw debit: enthalpy per
# nominal draw is constant for any tank at or above this, and degrades below.
DHW_MIXED_USE_TEMP: Final = 40.0

# --- DHW refill coil in the wood tank (v3.15.1, issue #40) ------------------
#
# The owner's DHW tank refills through a coil immersed in the wood buffer
# tank, so incoming mains water arrives preheated when that tank is hot.
# Off by default; only acts when the wood tank is modelled as its own store
# (the preheat depends on a real wood-tank temperature).
CONF_DHW_WOOD_COIL_ENABLED: Final = "dhw_wood_coil_enabled"
DEFAULT_DHW_WOOD_COIL_ENABLED: Final = False
# Heat-exchanger effectiveness: the fraction of the wood-tank-to-mains
# temperature difference the coil recovers. Deliberately conservative — a
# generous value would promise free hot water a mediocre coil cannot
# deliver, and the failure directions are not symmetric. Constant, not
# config, until someone measures a real coil; no learner in v1.
DHW_WOOD_COIL_EFFECTIVENESS: Final = 0.5
# The mains temperature the DHW draw model already assumes (thermal_model's
# dhw_draw_power heats from ~10 °C) — named so the coil math and the draw
# model cannot quietly disagree about the cold end.
DHW_COLD_WATER_TEMP: Final = 10.0  # °C

# --- Topology layout keys (issue #40) --------------------------------------
#
# Named hydronic layouts. v3.15.0 uses them to gate the two-tank model; the
# v3.16.0 catalog carries one entry per key (edge set, required slots,
# model variant) so the editor, the diagram and the model dispatch share one
# vocabulary. Strings, not an enum, because they are stored in config
# options and shown in diagnostics.
TOPOLOGY_NO_VALVE: Final = "no_valve"
TOPOLOGY_SINGLE_TANK_VALVE: Final = "single_tank_valve"
TOPOLOGY_TWO_TANK_4WAY: Final = "two_tank_4way"
# The layout the pre-v3.14.1 drawing showed; some houses genuinely have it
# (valve on the radiator circuit, slab fed direct from the tank).
TOPOLOGY_VALVE_UPPER_DIRECT_SLAB: Final = "valve_upper_direct_slab"
# Known, not yet modelled: drawable in the catalog, selectable never, until
# physics exists for a shunt on the slab circuit.
TOPOLOGY_SLAB_SHUNT: Final = "slab_shunt"

# The user's chosen layout (v3.16.0). Absent = the derived default, so
# untouched installs are byte-identical. Only catalog keys whose
# requirements the configuration meets are ever stored (the apply_topology
# service validates), and a stored key that stops being valid — the valve
# mode changed, the probe was removed — falls back to the derived default
# rather than erroring.
CONF_TOPOLOGY_LAYOUT: Final = "topology_layout"
# Cosmetic box positions from the layout editor, {place: [x, y]}. Never
# affects physics; free-form edges are never stored — snapping means the
# drawn edge set is matched against the catalog and only the KEY is saved.
CONF_TOPOLOGY_POSITIONS: Final = "topology_positions"


def topology_layout_valid(
    key: str, *, two_zone: bool, throttling: bool, wood_probe: bool
) -> bool:
    """Whether a stored layout key is honest for this configuration.

    Lives here, beside the keys, because both ``ThermalParameters`` (model
    dispatch) and ``topology`` (catalog, service validation) need the same
    answer and importing either from the other is circular. A key is valid
    when the model variant it names can actually run on what is configured:

    * ``no_valve`` — no throttling valve (with one, delivery IS throttled
      and drawing it otherwise would lie);
    * ``single_tank_valve`` — a throttling valve. Deliberately valid even
      when the two-tank layout is available: storing it is the user's
      off-switch for the two-tank model;
    * ``two_tank_4way`` — valve + two zones + a real wood-tank probe (the
      v3.15.0 gate, unchanged);
    * ``valve_upper_direct_slab`` — valve + two zones, and NO wood probe:
      no model variant exists for two tanks with a direct-fed slab, and a
      catalog that accepted the combination would be promising physics
      nobody wrote;
    * ``slab_shunt`` — never: recorded as known-but-unmodelled.
    """
    if key == TOPOLOGY_NO_VALVE:
        return not throttling
    if key == TOPOLOGY_SINGLE_TANK_VALVE:
        return throttling
    if key == TOPOLOGY_TWO_TANK_4WAY:
        return throttling and two_zone and wood_probe
    if key == TOPOLOGY_VALVE_UPPER_DIRECT_SLAB:
        return throttling and two_zone and not wood_probe
    return False


# --- Unknown price horizon (item 7) ----------------------------------------
#
# Prices past the published horizon used to be a flat repeat of the last known
# value. A flat tail has no trough, so the optimizer could not see a cheap
# period ahead worth waiting for and systematically under-deferred load.
CONF_PRICE_PRIOR_ENABLED: Final = "price_prior_enabled"
DEFAULT_PRICE_PRIOR_ENABLED: Final = True
PRICE_MODEL_STORE_VERSION: Final = 1


# --- Capacity (peak power) tariff, item 8 ----------------------------------
CONF_PEAK_TARIFF_ENABLED: Final = "peak_tariff_enabled"
CONF_PEAK_TARIFF_PRICE: Final = "peak_tariff_price_per_kw"
CONF_PEAK_TARIFF_COUNT: Final = "peak_tariff_peaks_averaged"
CONF_PEAK_TARIFF_WINDOW: Final = "peak_tariff_window_minutes"

DEFAULT_PEAK_TARIFF_ENABLED: Final = False
# A representative Swedish effekttariff. Only used as the form default; the
# real figure is on the user's grid invoice.
DEFAULT_PEAK_TARIFF_PRICE: Final = 45.0  # currency per kW per month
DEFAULT_PEAK_TARIFF_COUNT: Final = 3
DEFAULT_PEAK_TARIFF_WINDOW: Final = 60  # minutes

# --- The bill beyond spot: v4.0.0 T1 ---------------------------------------
#
# Every key here is optional and default inert: mode "none" produces a zero
# fee vector, empty masks are "all hours count at full rate" (exactly the
# pre-T1 model), λ = 0 prices prior-filled steps at the mean as before, and
# a zero fixed contract price disables that shadow column.

# Time-of-use grid transfer fees (#1). Tibber's `total` includes tax and VAT
# but not the DSO transfer fee, so the layer is additive, never double
# counted.
CONF_GRID_FEE_MODE: Final = "grid_fee_mode"  # none | rules | entity
DEFAULT_GRID_FEE_MODE: Final = "none"
CONF_GRID_FEE_RULES: Final = "grid_fee_rules"
DEFAULT_GRID_FEE_RULES: Final = ""
CONF_GRID_FEE_ENTITY: Final = "grid_fee_entity"  # SEK/kWh sensor
CONF_GRID_FEE_FIXED: Final = "grid_fee_fixed"  # SEK/kWh always added
DEFAULT_GRID_FEE_FIXED: Final = 0.0

# Windowed and seasonal effekttariff structures (#13). Empty month/hour
# masks mean every hour counts, and factor 1.0 means off-peak hours count
# at full rate — together exactly the flat model that shipped before.
CONF_PEAK_TARIFF_MONTHS: Final = "peak_tariff_months"  # e.g. "Nov-Mar"
DEFAULT_PEAK_TARIFF_MONTHS: Final = ""
CONF_PEAK_TARIFF_HOURS: Final = "peak_tariff_hours"  # e.g. "07:00-19:00"
DEFAULT_PEAK_TARIFF_HOURS: Final = ""
CONF_PEAK_TARIFF_WEEKDAYS_ONLY: Final = "peak_tariff_weekdays_only"
DEFAULT_PEAK_TARIFF_WEEKDAYS_ONLY: Final = False
CONF_PEAK_TARIFF_OFFPEAK_FACTOR: Final = "peak_tariff_offpeak_factor"
DEFAULT_PEAK_TARIFF_OFFPEAK_FACTOR: Final = 1.0

# Risk-adjusted pricing on the unpublished horizon (#34). λ = 0 keeps the
# prior's mean pricing; the sigma vector still rides along for display.
CONF_PRICE_RISK_LAMBDA: Final = "price_risk_lambda"
DEFAULT_PRICE_RISK_LAMBDA: Final = 0.0

# Contract-type shadow settlement (#23): the fixed-price column's SEK/kWh.
# 0 means "no fixed contract to compare against".
CONF_CONTRACT_FIXED_PRICE: Final = "contract_fixed_price"
DEFAULT_CONTRACT_FIXED_PRICE: Final = 0.0

# --- Fuse, the live peak guard and outage recovery: v4.0.0 T2 ---------------
#
# All default inert: fuse 0 A means unconfigured (advisor, guard and
# headroom all dormant — a plausible default like 16 A would cap a 20 A
# house); both guards default off, and the peak-guard listener is not even
# registered while its flag is off.
CONF_MAIN_FUSE_A: Final = "main_fuse_amperes"
DEFAULT_MAIN_FUSE_A: Final = 0
CONF_MAIN_FUSE_PHASES: Final = "main_fuse_phases"
DEFAULT_MAIN_FUSE_PHASES: Final = 3
CONF_FUSE_GUARD_ENABLED: Final = "fuse_guard_enabled"
DEFAULT_FUSE_GUARD_ENABLED: Final = False
CONF_PEAK_GUARD_ENABLED: Final = "peak_guard_enabled"
DEFAULT_PEAK_GUARD_ENABLED: Final = False
CONF_PEAK_GUARD_MARGIN_KW: Final = "peak_guard_margin_kw"
DEFAULT_PEAK_GUARD_MARGIN_KW: Final = 0.5
CONF_OUTAGE_RECOVERY_ENABLED: Final = "outage_recovery_enabled"
DEFAULT_OUTAGE_RECOVERY_ENABLED: Final = False

#: Swedish standard main-fuse ladder, for the right-sizing advisor (#3).
FUSE_LADDER_A: Final = (16, 20, 25, 35, 50, 63)
#: How far the guard lowers the ECL displace while suppressing (#7).
PEAK_GUARD_DISPLACE_NUDGE_C: Final = 2.0
#: A coordinator-update gap longer than this reads as a power outage (#22).
OUTAGE_GAP_MINUTES: Final = 90.0
#: How long the staggered-recovery window lasts after an outage.
OUTAGE_RECOVERY_HOURS: Final = 2.0
#: How long hot water queues behind space heating in recovery.
OUTAGE_DHW_DELAY_MINUTES: Final = 45.0


# --- Compressor cycling, item 10 -------------------------------------------
#
# Still zero, and that is now a measured decision rather than an assumption.
#
# Until v3.9.0 chatter was discouraged by a `0.01 * sum(dP^2)` term in the
# objective, priced in no units at all. Removing it was clearly right. Moving
# its job here, by shipping a non-zero default, was tried and rejected:
# sweeping 0.00 / 0.05 / 0.10 / 0.20 SEK per cycle moved the *cycling charge*
# by at most 0.5 SEK while moving the *electricity* cost by up to 2.2 SEK, and
# not monotonically -- 0.10 produced fewer starts than 0.05 on the same
# scenario. At these magnitudes the term does not steer the plan, it perturbs
# which local optimum the solver lands in, and the perturbation is worth more
# than the term. Shipping that as a default would be churn dressed as tuning.
#
# So it stays opt-in. Removing the mispriced term costs about 5% more
# compressor starts across the scenario set (127 -> 133) and saves about 9% of
# the electricity, which is a trade worth taking; anyone who wants the starts
# back has a knob denominated in real currency. `tests/validate.py` reports the
# start count per scenario, which is how that decision gets made from evidence.
CONF_CYCLING_COST: Final = "compressor_cycling_cost"
DEFAULT_CYCLING_COST: Final = 0.0

# --- PV self-consumption, item 9 -------------------------------------------
CONF_PV_ENABLED: Final = "pv_enabled"
CONF_PV_PEAK_KW: Final = "pv_peak_kw"
CONF_PV_EFFICIENCY: Final = "pv_system_efficiency"
CONF_PV_EXPORT_PRICE: Final = "pv_export_price"
CONF_PV_EXPORT_PRICE_ENTITY: Final = "pv_export_price_entity"
CONF_PV_PRODUCTION_ENTITY: Final = "pv_production_entity"

DEFAULT_PV_ENABLED: Final = False
DEFAULT_PV_PEAK_KW: Final = 0.0
DEFAULT_PV_EFFICIENCY: Final = 0.80
DEFAULT_PV_EXPORT_PRICE: Final = 0.0

# --- Away / holiday mode, item 13 ------------------------------------------
CONF_AWAY_ENABLED: Final = "away_enabled"
CONF_AWAY_PRESENCE_ENTITY: Final = "away_presence_entity"
CONF_AWAY_RETURN_ENTITY: Final = "away_return_entity"
CONF_AWAY_TEMPERATURE: Final = "away_temperature"
CONF_AWAY_DHW_MIN_TEMP: Final = "away_dhw_min_temperature"

DEFAULT_AWAY_ENABLED: Final = False
DEFAULT_AWAY_TEMPERATURE: Final = 16.0
DEFAULT_AWAY_DHW_MIN_TEMP: Final = 20.0

# --- Active system identification, item 18 ---------------------------------
CONF_SYSID_ENABLED: Final = "system_identification_enabled"
DEFAULT_SYSID_ENABLED: Final = False

# --- Revealed-preference comfort tuning, item 19 ---------------------------
CONF_COMFORT_LEARNING_ENABLED: Final = "comfort_learning_enabled"
DEFAULT_COMFORT_LEARNING_ENABLED: Final = False

# --- Building presets, item 17 ---------------------------------------------
CONF_BUILDING_PRESET_ENABLED: Final = "building_preset_enabled"
CONF_BUILDING_STRUCTURE: Final = "building_structure"
CONF_BUILDING_ERA: Final = "building_era"
CONF_BUILDING_FOUNDATION: Final = "building_foundation"
CONF_HEATED_AREA: Final = "heated_area_m2"
CONF_UPPER_EMITTER: Final = "upper_floor_emitter"
CONF_LOWER_EMITTER: Final = "lower_floor_emitter"

DEFAULT_BUILDING_PRESET_ENABLED: Final = False
DEFAULT_HEATED_AREA: Final = 140.0

# --- Closed-loop accuracy and energy statistics, items 11 and 15 -----------
ACCURACY_STORE_VERSION: Final = 1
ENERGY_STORE_VERSION: Final = 1


# Service for the card's what-if simulator (item 21).
SERVICE_SIMULATE_PLAN: Final = "simulate_plan"
SERVICE_APPLY_SCHEDULE: Final = "apply_schedule"
# Assign (or clear) one optional sensor from the card's setup diagram. Item
# 32's click-to-assign, built on the card rather than in a custom panel: the
# card is already authenticated and already draws the diagram, and one
# validated service is a far smaller surface than a second frontend with its
# own hand-rolled config-write path.
SERVICE_ASSIGN_ENTITY: Final = "assign_entity"
# Store the layout the user chose in the card's editor (v3.16.0), plus the
# cosmetic box positions. Mirrors assign_entity's discipline: server-side
# validation, an options write, the ordinary reload.
SERVICE_APPLY_TOPOLOGY: Final = "apply_topology"
# Manual plan override: pin *when* the pump runs, safety permitting.
SERVICE_APPLY_MANUAL_PLAN: Final = "apply_manual_plan"
SERVICE_CLEAR_MANUAL_PLAN: Final = "clear_manual_plan"
SERVICE_RESTORE_SNAPSHOT: Final = "restore_learned_snapshot"
#: T6 #52 — attribute the last settled interval's temperature residual.
SERVICE_DIAGNOSE_INTERVAL: Final = "diagnose_interval"
MANUAL_PLAN_STORE_VERSION: Final = 1
# A full solve is seconds of CPU. Dragging a slider must not trigger one per
# pixel, so simulation requests are rate-limited to this interval.
SIMULATE_MIN_INTERVAL_SECONDS: Final = 3.0

# ECL110 / MQTT configuration
CONF_ECL110_COMMAND_TOPIC: Final = "ecl110_command_topic"  # legacy JSON command topic
CONF_ECL110_DISPLACE_SET_TOPIC: Final = "ecl110_displace_set_topic"
CONF_ECL110_STATE_TOPIC: Final = "ecl110_state_topic"
CONF_ECL110_QOS: Final = "ecl110_mqtt_qos"
CONF_ECL110_RETAIN: Final = "ecl110_mqtt_retain"
CONF_ECL110_DISPLACE_MIN: Final = "ecl110_displace_min"
CONF_ECL110_DISPLACE_MAX: Final = "ecl110_displace_max"
CONF_ECL110_PID_TIME_CONSTANT: Final = "ecl110_pid_time_constant_hours"

# Temperature settings
CONF_TARGET_TEMP: Final = "target_temperature"
CONF_MIN_TEMP: Final = "min_temperature"
CONF_MAX_TEMP: Final = "max_temperature"
CONF_COMFORT_TEMP_DAY: Final = "comfort_temp_day"
CONF_COMFORT_TEMP_NIGHT: Final = "comfort_temp_night"
CONF_DAY_START_HOUR: Final = "day_start_hour"
CONF_DAY_END_HOUR: Final = "day_end_hour"

# Thermal model parameters (legacy / general)
CONF_HOUSE_THERMAL_MASS: Final = "house_thermal_mass"  # kWh/°C
CONF_HOUSE_HEAT_LOSS_COEFFICIENT: Final = "house_heat_loss_coefficient"  # kW/°C
CONF_SLAB_THERMAL_MASS: Final = "slab_thermal_mass"  # kWh/°C
CONF_SLAB_HEAT_TRANSFER: Final = "slab_heat_transfer"  # kW/°C
CONF_HEAT_PUMP_COP_NOMINAL: Final = "heat_pump_cop_nominal"
CONF_HEAT_PUMP_MAX_POWER: Final = "heat_pump_max_power"  # kW electrical
CONF_HEAT_PUMP_MIN_POWER: Final = "heat_pump_min_power"  # kW electrical

# Two-zone model parameters
#
# Whether the two-zone model runs was historically inferred from whether any
# zone key exists at all — which an options page can never undo, because the
# initial flow writes the keys into entry.data where options cannot erase
# them. The mode is the explicit override (v4.0.0): "auto" (the default, and
# what every untouched install effectively has) keeps the presence rule
# byte-for-byte; "on"/"off" force the model regardless of which keys exist.
CONF_TWO_ZONE_MODE: Final = "two_zone_mode"
TWO_ZONE_MODE_AUTO: Final = "auto"
TWO_ZONE_MODE_ON: Final = "on"
TWO_ZONE_MODE_OFF: Final = "off"
TWO_ZONE_MODES: Final = (TWO_ZONE_MODE_AUTO, TWO_ZONE_MODE_ON, TWO_ZONE_MODE_OFF)
DEFAULT_TWO_ZONE_MODE: Final = TWO_ZONE_MODE_AUTO
CONF_UPPER_FLOOR_THERMAL_MASS: Final = "upper_floor_thermal_mass"  # kWh/°C
CONF_LOWER_FLOOR_THERMAL_MASS: Final = "lower_floor_thermal_mass"  # kWh/°C
CONF_UPPER_FLOOR_HEAT_LOSS: Final = "upper_floor_heat_loss"  # kW/°C
CONF_LOWER_FLOOR_HEAT_LOSS: Final = "lower_floor_heat_loss"  # kW/°C
CONF_INTER_ZONE_TRANSFER: Final = "inter_zone_heat_transfer"  # kW/°C
CONF_RADIATOR_POWER_FRACTION: Final = "radiator_power_fraction"  # 0-1
CONF_UPPER_FLOOR_AREA_RATIO: Final = "upper_floor_area_ratio"  # 0-1
CONF_BUFFER_TANK_VOLUME: Final = "buffer_tank_volume"  # liters
CONF_BUFFER_TANK_LOSS: Final = "buffer_tank_heat_loss"  # kW/°C

# Solar gain parameters
CONF_WINDOW_AREA: Final = "window_area"  # m²
CONF_SOLAR_ORIENTATION_FACTOR: Final = "solar_orientation_factor"  # 0-1
CONF_SOLAR_HEAT_GAIN_COEFF: Final = "solar_heat_gain_coefficient"  # SHGC 0-1
CONF_SOLAR_UPPER_FRACTION: Final = "solar_upper_fraction"  # fraction going to upper floor

# DHW (Domestic Hot Water) parameters
CONF_DHW_TANK_VOLUME: Final = "dhw_tank_volume"  # liters
CONF_DHW_SETPOINT: Final = "dhw_setpoint"  # °C
CONF_DHW_MIN_TEMP: Final = "dhw_min_temperature"  # °C
CONF_DHW_DAILY_CONSUMPTION: Final = "dhw_daily_consumption"  # liters/day
# How fast the tank cools when nothing is drawn, expressed at a reference
# condition so it stays meaningful regardless of tank size. Self-learned at
# runtime from observed standby decay.
CONF_DHW_COOLING_RATE: Final = "dhw_cooling_rate"  # °C/h at reference conditions
CONF_BUFFER_COOLING_RATE: Final = "buffer_cooling_rate"  # °C/h at reference

# Mixing valve (item 29). Defaults to "none", which keeps the existing
# behaviour exactly: with no valve, whatever the pump makes goes straight to
# the emitters, and that is a correct model rather than a bug.
CONF_MIXING_VALVE_MODE: Final = "mixing_valve_mode"
CONF_MIXING_VALVE_TARGET: Final = "mixing_valve_target"  # °C indoor
CONF_MIXING_VALVE_TARGET_ENTITY: Final = "mixing_valve_target_entity"
# The entity `smart_write` commands: a number, input_number or climate entity
# exposed by the valve's own controller. This is the actuation path the mode
# waited for -- a mode that cannot do what its name says is worse than one
# that is absent, so `smart_write` only became selectable when this landed.
CONF_MIXING_VALVE_WRITE_ENTITY: Final = "mixing_valve_write_entity"
# Do not rewrite the valve target for changes smaller than this. The write
# runs after every optimization cycle, and most cycles the answer is the same
# number -- hammering a device with identical setpoints every 15 minutes
# wears flash on some controllers and floods others' logs.
MIXING_VALVE_WRITE_EPSILON: Final = 0.25  # K
CONF_BUFFER_MAX_TEMP: Final = "buffer_max_temperature"  # °C
DEFAULT_BUFFER_MAX_TEMP: Final = 70.0  # °C
# 0.0 means "not set": the comfort ceiling is used instead, which is the
# recommended setting for a dumb valve anyway.
DEFAULT_MIXING_VALVE_TARGET: Final = 0.0  # °C
CONF_BUFFER_TANK_TEMP_ENTITY: Final = "buffer_tank_temp_entity"
CONF_HOUSE_HEAT_LOSS_SCALE: Final = "house_heat_loss_scale"  # dimensionless
CONF_LOWER_FLOOR_LOSS_RATIO: Final = "lower_floor_loss_ratio"  # dimensionless

# DHW demand windows — the time frames where hot water must be available
CONF_DHW_SCHEDULE_ENABLED: Final = "dhw_schedule_enabled"
CONF_DHW_WINDOWS: Final = "dhw_windows"  # "06:00-08:30, 17:00-22:00"
CONF_DHW_IDLE_MIN_TEMP: Final = "dhw_idle_min_temperature"  # °C outside windows

# DHW anti-legionella cycle
CONF_DHW_LEGIONELLA_ENABLED: Final = "dhw_legionella_enabled"
CONF_DHW_LEGIONELLA_TEMP: Final = "dhw_legionella_temperature"  # °C
CONF_DHW_LEGIONELLA_INTERVAL_DAYS: Final = "dhw_legionella_interval_days"

# --- Hot water, v4.0.0 T3 ---------------------------------------------------
#
# All default inert. The inlet default of 10.0 °C is load-bearing: it is the
# number the two previously hard-coded cold-water temperatures used, and
# every ready target in every existing install sits on it — the T3 identity
# test asserts a fresh model with these defaults plans byte-identically.
# NONE of these keys may join the ``dhw_enabled`` presence trio.
CONF_DHW_INLET_TEMP: Final = "dhw_inlet_temp"  # °C cold-water inlet, annual mean
DEFAULT_DHW_INLET_TEMP: Final = 10.0
#: Peak-to-mean amplitude of the seasonal inlet swing, °C. 0 = constant.
CONF_DHW_INLET_SEASONAL_AMPLITUDE: Final = "dhw_inlet_seasonal_amplitude"
DEFAULT_DHW_INLET_SEASONAL_AMPLITUDE: Final = 0.0
CONF_DHW_INLET_ENTITY: Final = "dhw_inlet_entity"  # live sensor wins over model
#: Fraction of drain heat a greywater recovery unit returns to the inlet.
CONF_GREYWATER_RECOVERY: Final = "greywater_recovery_effectiveness"
DEFAULT_GREYWATER_RECOVERY: Final = 0.0
#: #20 — ready targets from learned per-window draw quantiles.
CONF_DHW_QUANTILE_TARGETS_ENABLED: Final = "dhw_quantile_targets_enabled"
DEFAULT_DHW_QUANTILE_TARGETS_ENABLED: Final = False
#: #24 — credit disinfection achieved by any heat source, hold-verified.
CONF_DHW_FREE_DISINFECTION_ENABLED: Final = "dhw_free_disinfection_enabled"
DEFAULT_DHW_FREE_DISINFECTION_ENABLED: Final = False
#: #47 — let the legionella cycle shop for a cheap day inside its interval.
CONF_DHW_ELASTIC_LEGIONELLA_ENABLED: Final = "dhw_elastic_legionella_enabled"
DEFAULT_DHW_ELASTIC_LEGIONELLA_ENABLED: Final = False
CONF_DHW_LEGIONELLA_MIN_INTERVAL_DAYS: Final = "dhw_legionella_min_interval_days"
DEFAULT_DHW_LEGIONELLA_MIN_INTERVAL_DAYS: Final = 5.0
#: #28 — display only: the shower the tank actually holds.
CONF_SHOWER_FLOW_LPM: Final = "shower_flow_lpm"
DEFAULT_SHOWER_FLOW_LPM: Final = 8.0
#: #6 — pump switches the scheduler may drive, unset = never touched.
CONF_VVC_PUMP_ENTITY: Final = "vvc_pump_entity"
CONF_VVC_LEAD_MINUTES: Final = "vvc_lead_minutes"
DEFAULT_VVC_LEAD_MINUTES: Final = 20
CONF_SPACE_PUMP_ENTITY: Final = "space_circulation_pump_entity"

#: #24 — minutes the tank must HOLD the disinfection temperature before the
#: cycle counts. Momentary blips at temperature kill nothing.
DHW_LEGIONELLA_HOLD_MINUTES: Final = 20.0
#: #20 — events per window before the p90 fully replaces the mean (ramp).
DHW_QUANTILE_MIN_EVENTS: Final = 8
#: #18 — day-type samples at which the blend is half day-type, half pooled.
DHW_DAYTYPE_BLEND_K: Final = 14.0
#: #6 — a zone this close to its comfort floor forces the space pump on.
SPACE_PUMP_FLOOR_MARGIN_C: Final = 0.3

# --- Model & learning, v4.0.0 T4a --------------------------------------------
#
# Detection and learner-freezing ship default-ON: a freeze only stops
# learning, it never changes a plan, so both are plan-neutral guard
# extensions. Only the pieces that could move a plan are gated.
#: #26 — relax the comfort floor while a window is detected open.
CONF_OPEN_WINDOW_RELAX_ENABLED: Final = "open_window_relax_enabled"
DEFAULT_OPEN_WINDOW_RELAX_ENABLED: Final = False
#: #11 — nudge DHW readiness when the immersion element keeps rescuing it.
CONF_IMMERSION_FEEDBACK_ENABLED: Final = "immersion_feedback_enabled"
DEFAULT_IMMERSION_FEEDBACK_ENABLED: Final = False

#: #26 — the ventilation CUSUM: °C of accumulated colder-than-predicted
#: residual beyond the per-sample allowance before "window open" trips.
VENT_CUSUM_THRESHOLD_C: Final = 1.2
VENT_CUSUM_DRIFT_C: Final = 0.08
#: Per-sample cap on what feeds the ventilation CUSUM. Half the threshold,
#: so no single glitched reading can trip the detector alone — at least
#: three consecutive abnormal samples (~1.5 h) are needed, which is the
#: timescale of a window actually standing open.
VENT_CUSUM_CLIP_C: Final = VENT_CUSUM_THRESHOLD_C / 2.0
#: Hours without any residual feed before a tripped ventilation latch is
#: force-released. The feed dries up entirely in mild weather (the
#: heat-loss learner needs indoor−outdoor ≥ 6 °C), and a latch nothing
#: can feed would otherwise freeze every learner indefinitely.
VENT_CUSUM_STARVE_HOURS: Final = 6.0

# T4b — weather inputs (#21 #30). The humidity feed ships ungated: with no
# defrost evidence the derate is 1.0 everywhere, so it is inert by
# construction. The rain/snow split and the roof-snow solar damping move
# real physics, so each is gated.
#: #30 — weight the rain heat-loss multiplier by the liquid fraction of
#: precipitation. Snow does not wet the building envelope.
CONF_PRECIP_TYPE_ENABLED: Final = "precip_type_enabled"
DEFAULT_PRECIP_TYPE_ENABLED: Final = False
#: #30 — damp modelled solar gain for a while after heavy snowfall
#: (snow on roof glazing and low winter panes). Deliberately crude.
CONF_SNOW_ROOF_FACTOR_ENABLED: Final = "snow_roof_factor_enabled"
DEFAULT_SNOW_ROOF_FACTOR_ENABLED: Final = False
#: Open-Meteo's own snowfall convention: cm of snow ≈ 0.7 × mm of water.
SNOW_CM_PER_MM_WATER: Final = 0.7
#: Accumulated snowfall that counts as "heavy" (cm within a day).
SNOW_HEAVY_CM: Final = 2.0
#: Solar-gain multiplier while the roof is assumed snowed over, and how
#: long the assumption holds after the heavy fall.
SNOW_ROOF_DAMPING: Final = 0.5
SNOW_ROOF_DAYS: Final = 2.0

# T4b — the learners (#17 #36 #53 #2). Each ships its learning AND its
# application behind one flag: half-armed states (learning silently, then
# a config change suddenly applying weeks of unreviewed evidence) are
# worse than off.
#: #17 — cap planned electrical power to what the unit has actually
#: delivered per outdoor bucket, through T2's caps_extra channel.
CONF_CAPACITY_CURVE_ENABLED: Final = "capacity_curve_enabled"
DEFAULT_CAPACITY_CURVE_ENABLED: Final = False
#: Samples a 3 °C bucket needs before its envelope caps anything.
CAPACITY_MIN_SAMPLES: Final = 5
#: The cap can never starve the house: at least this fraction of
#: nameplate is always available. The program's worst failure mode is a
#: starved house at −15 °C, not an optimistic plan.
CAPACITY_FLOOR_FRACTION: Final = 0.6
#: Slow forgetting on the envelope so a one-off spike does not pin it.
CAPACITY_FORGET: Final = 0.999
#: #36 — learn a scale on the modelled solar aperture (window_area x
#: SHGC) from sunny-step residuals.
CONF_SOLAR_APERTURE_LEARNING_ENABLED: Final = "solar_aperture_learning_enabled"
DEFAULT_SOLAR_APERTURE_LEARNING_ENABLED: Final = False
SOLAR_APERTURE_MIN: Final = 0.3
SOLAR_APERTURE_MAX: Final = 2.0
#: Irradiance below this carries no aperture information, W/m².
SOLAR_APERTURE_MIN_IRRADIANCE: Final = 150.0
#: EWMA horizon for the regression moments (per accepted sample).
SOLAR_APERTURE_ALPHA: Final = 0.02
#: Accepted sunny samples before the learned scale applies.
SOLAR_APERTURE_MIN_SAMPLES: Final = 30
#: #53 — per-hour internal gains, ridge-regularised toward the constant.
CONF_INTERNAL_GAINS_LEARNING_ENABLED: Final = (
    "internal_gains_learning_enabled"
)
DEFAULT_INTERNAL_GAINS_LEARNING_ENABLED: Final = False
INTERNAL_GAINS_ALPHA: Final = 0.05
#: Pull toward the configured constant per fold — the profile is a
#: perturbation of the prior, not a replacement for it.
INTERNAL_GAINS_RIDGE: Final = 0.02
#: Per-hour ceiling as a multiple of the configured constant.
INTERNAL_GAINS_MAX_FACTOR: Final = 3.0
#: #2 — a standing learned bias on the ECL110 heat curve displace.
CONF_CURVE_LEARNING_ENABLED: Final = "curve_learning_enabled"
DEFAULT_CURVE_LEARNING_ENABLED: Final = False

# T5 — comfort floors (#16 #54). Both move the floor inside the objective,
# so both are gated; the mold guard is double-gated on its entity too.
#: #16 — raise the comfort floor by the model's own expected error at
#: each step's lead time, damped by trust and hard-capped.
CONF_CONFIDENCE_MARGINS_ENABLED: Final = "confidence_margins_enabled"
DEFAULT_CONFIDENCE_MARGINS_ENABLED: Final = False
#: The margin can never exceed this, however bad the history looks (K).
CONFIDENCE_MARGIN_CAP_C: Final = 0.8
#: #54 — keep every cold surface under the mold threshold.
CONF_MOLD_GUARD_ENABLED: Final = "mold_guard_enabled"
DEFAULT_MOLD_GUARD_ENABLED: Final = False
CONF_INDOOR_HUMIDITY_ENTITY: Final = "indoor_humidity_entity"
#: Temperature factor of the worst thermal bridge: surface temperature =
#: T_out + fRsi (T_room − T_out). 0.75 is the Swedish BBR guidance value.
CONF_THERMAL_BRIDGE_FRSI: Final = "thermal_bridge_frsi"
DEFAULT_THERMAL_BRIDGE_FRSI: Final = 0.75
#: Mold growth needs sustained surface RH above roughly this fraction.
MOLD_SURFACE_RH_LIMIT: Final = 0.8

# T6 — insight (#29 #52 #55 #65 #39 #40). Everything here reads the system;
# the only plan-affecting piece is the wear autotune, gated off by default.
#: #55 — what a compressor swap costs. 0 means wear books 0 SEK/start,
#: which keeps the counter pure observation until the user prices it.
CONF_COMPRESSOR_REPLACEMENT_COST: Final = "compressor_replacement_cost"
DEFAULT_COMPRESSOR_REPLACEMENT_COST: Final = 0.0
#: #55 — the manufacturer's rated start count the swap cost spreads over.
CONF_COMPRESSOR_RATED_STARTS: Final = "compressor_rated_starts"
DEFAULT_COMPRESSOR_RATED_STARTS: Final = 100000
#: #55 — feed the realised wear price (cost/rated) into the optimizer's
#: cycling penalty. The one T6 switch that changes plans.
CONF_WEAR_AUTOTUNE_ENABLED: Final = "wear_autotune_enabled"
DEFAULT_WEAR_AUTOTUNE_ENABLED: Final = False
#: #39 — refresh one what-if price tile after each scheduled solve.
#: Off by default: the tile set is three extra solves of real CPU.
CONF_PRICE_TILES_ENABLED: Final = "price_tiles_enabled"
DEFAULT_PRICE_TILES_ENABLED: Final = False
#: #55 — consecutive samples on the far side of the threshold before an
#: edge counts. One noisy meter reading must not book a compressor start.
START_HYSTERESIS_SAMPLES: Final = 2
#: #65 — smoothing for the daily operation-score samples (~3 weeks).
SCORE_ALPHA: Final = 0.05

# T7 — inverter frequency (#61). Observe is the default and actuates
# nothing; control is an explicit per-install opt-in AFTER the user has
# validated their number entity against the real hardware.
CONF_COMPRESSOR_FREQ_ENTITY: Final = "compressor_freq_entity"
#: Optional separate sensor carrying the ACTUAL compressor frequency.
#: Many number entities are setpoint registers that echo the last written
#: value — feedback read from one can never diverge, which makes the
#: watchdog decorative and teaches the map against a frozen setpoint.
CONF_COMPRESSOR_FREQ_SENSOR: Final = "compressor_freq_sensor"
CONF_FREQ_CONTROL_MODE: Final = "freq_control_mode"
DEFAULT_FREQ_CONTROL_MODE: Final = "observe"
#: How far the comfort floor is relaxed while a window is open (gated).
OPEN_WINDOW_RELAX_C: Final = 1.0
#: #11 — measured power above nameplate by this factor reads as the
#: immersion element, not the compressor.
IMMERSION_FACTOR: Final = 1.15
#: #12 — samples a 3 °C bucket needs before its baseline is trusted.
COP_BASELINE_MIN_SAMPLES: Final = 20
#: Weeks-scale EWMA for the long COP baseline.
COP_BASELINE_ALPHA: Final = 0.02
#: #12 — accumulated relative COP shortfall before the repair issue.
COP_HEALTH_THRESHOLD: Final = 0.8
COP_HEALTH_DRIFT: Final = 0.01

# Weather sensitivity parameters
CONF_WIND_SENSITIVITY: Final = "wind_sensitivity_factor"  # fraction per m/s
CONF_RAIN_HEAT_LOSS_MULTIPLIER: Final = "rain_heat_loss_multiplier"  # multiplier

# Optimization settings
CONF_OPTIMIZATION_INTERVAL: Final = "optimization_interval"  # minutes
CONF_PRICE_WEIGHT: Final = "price_weight"
CONF_COMFORT_WEIGHT: Final = "comfort_weight"

# Defaults
DEFAULT_TARGET_TEMP: Final = 21.0
DEFAULT_MIN_TEMP: Final = 19.0
DEFAULT_MAX_TEMP: Final = 23.0
DEFAULT_COMFORT_TEMP_DAY: Final = 21.0
DEFAULT_COMFORT_TEMP_NIGHT: Final = 19.5
DEFAULT_DAY_START_HOUR: Final = 7
DEFAULT_DAY_END_HOUR: Final = 22

DEFAULT_HOUSE_THERMAL_MASS: Final = 10.0  # kWh/°C - typical well-insulated house
DEFAULT_HOUSE_HEAT_LOSS_COEFFICIENT: Final = 0.15  # kW/°C
DEFAULT_SLAB_THERMAL_MASS: Final = 5.0  # kWh/°C - concrete slab
DEFAULT_SLAB_HEAT_TRANSFER: Final = 0.8  # kW/°C - slab to room
DEFAULT_HEAT_PUMP_COP_NOMINAL: Final = 3.5
DEFAULT_HEAT_PUMP_MAX_POWER: Final = 5.0  # kW
DEFAULT_HEAT_PUMP_MIN_POWER: Final = 1.0  # kW

# Two-zone defaults
DEFAULT_UPPER_FLOOR_THERMAL_MASS: Final = 3.0  # kWh/°C - lighter (radiators + air)
DEFAULT_LOWER_FLOOR_THERMAL_MASS: Final = 8.0  # kWh/°C - heavy concrete slab
DEFAULT_UPPER_FLOOR_HEAT_LOSS: Final = 0.08  # kW/°C
DEFAULT_LOWER_FLOOR_HEAT_LOSS: Final = 0.07  # kW/°C
DEFAULT_INTER_ZONE_TRANSFER: Final = 0.5  # kW/°C - open layout heat transfer
DEFAULT_RADIATOR_POWER_FRACTION: Final = 0.4  # 40% to radiators, 60% to floor
DEFAULT_UPPER_FLOOR_AREA_RATIO: Final = 0.5  # equal floors
DEFAULT_BUFFER_TANK_VOLUME: Final = 35.0  # liters
DEFAULT_BUFFER_TANK_LOSS: Final = 0.01  # kW/°C - small tank

# Below this volume the buffer tank is not treated as a store, whatever the
# valve mode: the physics (valve delivery, standing loss, the temperature cap)
# stay modelled, but the terminal credit and the settlement cap ignore it, so
# the optimizer cannot plan around charge it could never meaningfully hold.
# The default 35 L tank is worth ~0.8 kWh over a 20 K swing -- below the
# resolution of a single 15-minute step -- and the honest behaviour at that
# size is to stop pretending (item 27). 100 L over a 30 K usable swing is
# ~3.5 kWh, a couple of hours of winter house load, which is where a store
# starts to be able to move money.
BUFFER_STORE_MIN_VOLUME: Final = 100.0  # liters

# Solar gain defaults
DEFAULT_WINDOW_AREA: Final = 10.0  # m² total glazing area
DEFAULT_SOLAR_ORIENTATION_FACTOR: Final = 0.7  # south-facing bias
DEFAULT_SOLAR_HEAT_GAIN_COEFF: Final = 0.7  # typical double-glazed low-e
DEFAULT_SOLAR_UPPER_FRACTION: Final = 0.4  # 40% upper, 60% lower (open layout, sun hits lower floor)

# DHW defaults
DEFAULT_DHW_TANK_VOLUME: Final = 200.0  # liters
DEFAULT_DHW_SETPOINT: Final = 55.0  # °C - "ready" temperature at window start
DEFAULT_DHW_MIN_TEMP: Final = 45.0  # °C - usable minimum inside demand windows

# How far below the setpoint the usable minimum is allowed to sit. A minimum
# equal to the setpoint leaves no deadband at all: the tank would have to hold
# exactly its target, so the pump would short-cycle against its own hysteresis
# chasing a band of zero width. The card clamps its slider to the ceiling this
# implies, but the ceiling is enforced in ``apply_schedule`` too, because both
# it and ``simulate_plan`` can be called straight from an automation.
DHW_MIN_TEMP_SETPOINT_MARGIN: Final = 5.0  # °C
DEFAULT_DHW_DAILY_CONSUMPTION: Final = 150.0  # liters/day average household

# Standby cooling of the DHW tank, stated at a reference condition: a tank at
# 45 °C surrounded by 20 °C air loses 0.3 °C per hour. The optimizer converts
# this into a UA value (kW/°C) using the tank's thermal mass, and the
# coordinator refines it from measured decay.
DEFAULT_DHW_COOLING_RATE: Final = 0.3  # °C/h
DHW_COOLING_REFERENCE_TANK_TEMP: Final = 45.0  # °C
DHW_COOLING_REFERENCE_AMBIENT_TEMP: Final = 20.0  # °C
DHW_COOLING_REFERENCE_DELTA: Final = (
    DHW_COOLING_REFERENCE_TANK_TEMP - DHW_COOLING_REFERENCE_AMBIENT_TEMP
)
# Plausible bounds for the learned rate — a tank that appears to cool outside
# these is being contaminated by draws or a bad sensor reading.
DHW_COOLING_RATE_MIN: Final = 0.05  # °C/h
DHW_COOLING_RATE_MAX: Final = 3.0  # °C/h

# Standby cooling of the buffer tank, stated the same way as the DHW tank so it
# can be learned by the same estimator. A buffer tank holds very little water,
# so even a modest heat loss moves its temperature quickly: 6 °C/h at 25 °C
# above ambient. That is chosen to reproduce the previous fixed 0.01 kW/°C,
# since UA = rate * C / 25 and a 35 L tank has C = 0.0407 kWh/°C.
DEFAULT_BUFFER_COOLING_RATE: Final = 6.0  # °C/h
BUFFER_COOLING_RATE_MIN: Final = 0.5  # °C/h
BUFFER_COOLING_RATE_MAX: Final = 30.0  # °C/h

# ...and all three of those numbers are for a 35 L tank. They cannot be applied
# unscaled to a larger one.
#
# The UA is derived as `rate * C / 25`, and C scales with volume -- so holding
# the rate fixed makes UA scale with volume too. Physically UA follows the tank's
# *surface area*, which grows as volume^(2/3). Cooling rate is UA/C, so it falls
# as volume^(-1/3): a bigger tank has proportionally less skin to lose heat
# through, which is why large accumulators hold their charge overnight and a
# small buffer does not.
#
# Left unscaled the error is severe and it silently kills the case for storing
# anything. A 750 L tank at the 35 L rate is modelled as losing 43.8 kWh over
# six hours from a 26.1 kWh charge -- 168 % of the charge. The clamp floor is
# worse than the default, because it stops the *learner* from ever finding the
# truth: at 0.5 °C/h a 750 L tank still models 17 W/K against a real ~2 W/K.
# Canonical home for this: the tank-geometry helpers below need it, and
# `thermal_model` imports from here rather than the reverse.
WATER_SPECIFIC_HEAT: Final = 0.00116  # kWh per litre per K


# Bounds on how well or badly a tank can physically be insulated, in W/m2K.
# Scaling the legacy rate geometrically is the right *shape* but keeps its
# magnitude, and that magnitude is not physical: 6 C/h at 35 L works out at
# 9.7 W/K, which for a tank of roughly 0.64 m2 implies no insulation at all.
# Deriving the clamp from surface area and an insulation quality instead means
# the learner can reach what a real accumulator actually does -- around
# 2 W/K for 750 L -- rather than being floored several times above it.
BUFFER_INSULATION_U_BEST: Final = 0.2  # W/m2K, thick modern insulation
BUFFER_INSULATION_U_TYPICAL: Final = 1.0  # W/m2K, an ordinary insulated tank
BUFFER_INSULATION_U_WORST: Final = 8.0  # W/m2K, effectively a bare cylinder


def buffer_tank_surface_area(volume_litres: float) -> float:
    """Outer area of a tank of this volume, m2.

    Assumes an upright cylinder about two and a half times as tall as it is
    wide, which is what accumulators of every size look like. Exactness does not
    matter here; the volume^(2/3) growth does.
    """
    try:
        volume_m3 = max(float(volume_litres), 1e-6) / 1000.0
    except (TypeError, ValueError):
        return 0.0
    diameter = (volume_m3 / 1.963) ** (1.0 / 3.0)  # H = 2.5 D
    return 9.42 * diameter * diameter  # side + both ends


def buffer_cooling_rate_bounds(volume_litres: float) -> tuple[float, float]:
    """Clamp range for the learned cooling rate at a given tank volume, C/h.

    Converted from the insulation bounds above through this tank's own geometry
    and thermal mass, since the learner speaks in C/h while the physics is a UA.
    """
    area = buffer_tank_surface_area(volume_litres)
    capacity = max(float(volume_litres), 1e-6) * WATER_SPECIFIC_HEAT
    if area <= 0.0 or capacity <= 0.0:
        return BUFFER_COOLING_RATE_MIN, BUFFER_COOLING_RATE_MAX
    # rate = UA * reference_delta / C, with UA in kW/K.
    to_rate = DHW_COOLING_REFERENCE_DELTA / capacity / 1000.0
    return (
        BUFFER_INSULATION_U_BEST * area * to_rate,
        BUFFER_INSULATION_U_WORST * area * to_rate,
    )


def default_buffer_cooling_rate(volume_litres: float) -> float:
    """Prior for the cooling rate at a given volume, before anything is learned.

    Derived the same way as the bounds, from an ordinarily-insulated tank. The
    old flat 6 C/h came out at 9.7 W/K on a 35 L tank -- above the bare-cylinder
    ceiling above, i.e. a prior that assumed *worse* than no insulation at all,
    and 30x too lossy by the time it was applied to an accumulator.
    """
    area = buffer_tank_surface_area(volume_litres)
    capacity = max(float(volume_litres), 1e-6) * WATER_SPECIFIC_HEAT
    if area <= 0.0 or capacity <= 0.0:
        return DEFAULT_BUFFER_COOLING_RATE
    return BUFFER_INSULATION_U_TYPICAL * area * DHW_COOLING_REFERENCE_DELTA / capacity / 1000.0

# The house heat loss coefficient the user configures is a nameplate estimate.
# What the optimizer actually needs is how fast *this* house loses heat, so the
# coordinator learns a dimensionless correction factor from the error between
# predicted and observed indoor temperature. 1.0 means the configured value is
# exactly right; the bounds stop a bad sensor or an open window from running
# away with the model.
DEFAULT_HOUSE_HEAT_LOSS_SCALE: Final = 1.0
HOUSE_HEAT_LOSS_SCALE_MIN: Final = 0.3
HOUSE_HEAT_LOSS_SCALE_MAX: Final = 3.0

# How much of the total loss belongs to the lower zone, relative to the
# configured split (item 31).
#
# `house_heat_loss_scale` multiplies *both* zone losses, so it can move the
# total but never the split. Learning both zone losses independently alongside
# it would give three parameters for two degrees of freedom -- they would trade
# off against each other and drift without ever hurting the fit. So the two are
# given separate jobs: the scale owns the level and is fitted from the upper
# zone, which this ratio does not touch; the ratio owns the split and is fitted
# from the lower zone, given the scale. Two parameters, two independent
# measurements, no collinearity.
#
# It stays at 1.0 unless a real lower-floor sensor is configured. Without one the
# lower zone is an estimate derived from the floor return water, and fitting
# against it would be fitting against a fabricated target.
DEFAULT_LOWER_FLOOR_LOSS_RATIO: Final = 1.0
LOWER_FLOOR_LOSS_RATIO_MIN: Final = 0.3
LOWER_FLOOR_LOSS_RATIO_MAX: Final = 3.0

# DHW demand window defaults
DEFAULT_DHW_SCHEDULE_ENABLED: Final = True
DEFAULT_DHW_WINDOWS: Final = "06:00-08:30, 17:00-22:00"
# Outside the demand windows there is no availability requirement. The default
# equals the tank ambient temperature, i.e. "let it coast".
DEFAULT_DHW_IDLE_MIN_TEMP: Final = 20.0  # °C

# DHW anti-legionella defaults
DEFAULT_DHW_LEGIONELLA_ENABLED: Final = True
DEFAULT_DHW_LEGIONELLA_TEMP: Final = 60.0  # °C
DEFAULT_DHW_LEGIONELLA_INTERVAL_DAYS: Final = 7.0

# Weather sensitivity defaults.
#
# Wind: heat loss scales as (1 + sensitivity × wind speed). Only the
# infiltration and convective-film share of the loss responds to wind at all —
# transmission through the insulated envelope does not — so for a reasonably
# tight house the whole-house effect is a few percent per m/s. Measured
# infiltration studies put a 10 m/s wind at roughly +20-40% loss, i.e. a
# sensitivity of 0.02-0.04. The previous default of 0.15 claimed +150% at
# 10 m/s: a physically implausible figure that made every windy forecast
# panic-charge the house, and the passive learner then spent weeks walking the
# overall loss scale back down to compensate. Existing installations keep
# whatever value is stored in their config entry; only new setups see this.
DEFAULT_WIND_SENSITIVITY: Final = 0.03  # 3% heat loss increase per m/s wind
DEFAULT_RAIN_HEAT_LOSS_MULTIPLIER: Final = 1.15  # 15% increase when raining

# ECL110 defaults (manual "Displace" = parallel heat-curve shift in °C)
DEFAULT_ECL110_COMMAND_TOPIC: Final = "ecl110/command"  # legacy JSON write path
DEFAULT_ECL110_DISPLACE_SET_TOPIC: Final = "ecl110/flow_temp_control/displace/set"
DEFAULT_ECL110_STATE_TOPIC: Final = "ecl110/flow_temp_control/displace"
DEFAULT_ECL110_QOS: Final = 1
DEFAULT_ECL110_RETAIN: Final = False
DEFAULT_ECL110_DISPLACE_MIN: Final = -20.0
DEFAULT_ECL110_DISPLACE_MAX: Final = 20.0
DEFAULT_ECL110_PID_TIME_CONSTANT: Final = 1.5  # hours, first-order approximation


# How long a hand-arranged plan stays pinned, measured from the moment it is
# applied. Applying again restarts the clock.
#
# 20 rather than 24 is load-bearing, so do not quietly round it up. The
# optimizer's horizon is 24 h, so a 24-hour override would cover the whole
# horizon at every moment and leave no free step -- re-applying daily would
# switch the optimizer off while appearing to leave it on. At 20 there is always
# a tail of about four hours it still owns. The invariant is *override shorter
# than horizon*, not the number 20.
#
# Both sides obey this one constant: the service uses it as the `expires_at`
# default, and the card publishes it to the chart as the ceiling a slot may be
# dragged to. If they drifted apart, the card would show slots as pinned past
# the point where `channel_pins` frees them, which is the bug this replaced.
MANUAL_PLAN_WINDOW_HOURS: Final = 20
DEFAULT_OPTIMIZATION_INTERVAL: Final = 30  # minutes
DEFAULT_PRICE_WEIGHT: Final = 1.0
DEFAULT_COMFORT_WEIGHT: Final = 5.0

# Update intervals

# Optimization modes
MODE_COMFORT: Final = "comfort"
MODE_ECONOMY: Final = "economy"
#: How much lower the plan may take the house in economy mode, in K. Economy
#: buys savings with comfort, and this is the whole of what it spends: the band
#: widens downward and nothing else about the solve changes.
#:
#: A price-weight multiplier was the obvious alternative and was measured and
#: rejected. It is the same degree of freedom the comfort learner already owns
#: and would be erased by it, it does nothing at all in the two winter profiles
#: where a savings mode is most wanted, and it raised the bill 29 % on the
#: shoulder profile. Widening the band measures -24.6 % on winter_typical and
#: -18.9 % on winter_narrow, and only -4.5 % on flat prices -- the right shape
#: for a mode that promises savings in exchange for comfort.
ECONOMY_MIN_TEMP_WIDENING: Final = 1.5  # K
#: Economy is not a licence to freeze the house. Whatever the configured floor,
#: the widening stops here.
ECONOMY_ABSOLUTE_FLOOR: Final = 15.0  # °C
MODE_OFF: Final = "off"
MODE_BOOST: Final = "boost"
MODE_AUTO: Final = "auto"

#: Every mode the service and the persistence layer accept. Written out inline
#: in the service schema before this, so there was no single place to add one.
OPERATION_MODES: Final = (
    MODE_AUTO,
    MODE_COMFORT,
    MODE_ECONOMY,
    MODE_OFF,
    MODE_BOOST,
)

# Service names
SERVICE_RUN_OPTIMIZATION: Final = "run_optimization"
SERVICE_SET_MODE: Final = "set_mode"
SERVICE_SET_THERMAL_PARAMS: Final = "set_thermal_parameters"

# Attributes
ATTR_DHW_COOLING_RATE: Final = "dhw_cooling_rate"
ATTR_BUFFER_COOLING_RATE: Final = "buffer_cooling_rate"

# The buffer tank key is defined after the staleness table above, so its age
# limit is registered here rather than inline.
INPUT_MAX_AGE_MINUTES[CONF_BUFFER_TANK_TEMP_ENTITY] = 60.0
INPUT_MAX_AGE_MINUTES[CONF_PV_PRODUCTION_ENTITY] = 30.0
# Matches the indoor sensor: it is the same kind of measurement, read on the
# same cycle. A key missing from this table gets no age limit at all, which
# silently disables the staleness watchdog for it.
INPUT_MAX_AGE_MINUTES[CONF_LOWER_FLOOR_TEMP_ENTITY] = 60.0
# A stale valve target would have the model believe the house is being held
# somewhere it is not, and plan charging around it.
INPUT_MAX_AGE_MINUTES[CONF_MIXING_VALVE_TARGET_ENTITY] = 60.0
# A stalled hot sensor on the wood side would look like an indefinite free
# fire, which is the expensive failure direction -- these go stale early.
INPUT_MAX_AGE_MINUTES[CONF_VALVE_OUTLET_TEMP_ENTITY] = 60.0
INPUT_MAX_AGE_MINUTES[CONF_WOOD_TANK_TOP_ENTITY] = 60.0
INPUT_MAX_AGE_MINUTES[CONF_WOOD_TANK_BOTTOM_ENTITY] = 60.0

