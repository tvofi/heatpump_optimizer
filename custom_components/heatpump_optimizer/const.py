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
CONF_HEAT_PUMP_ENTITY: Final = "heat_pump_entity"
CONF_HEAT_PUMP_SWITCH_ENTITY: Final = "heat_pump_switch_entity"

# Two-zone sensor configuration
CONF_SOLAR_RADIATION_ENTITY: Final = "solar_radiation_entity"
CONF_FLOOR_RETURN_TEMP_ENTITY: Final = "floor_return_temp_entity"

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

ATTR_STALE_INPUTS: Final = "stale_inputs"
ATTR_INPUT_AGES: Final = "input_ages_minutes"
ATTR_LEARNERS_FROZEN: Final = "learners_frozen"

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

ATTR_EXTERNAL_HEAT_ACTIVE: Final = "external_heat_active"
ATTR_EXTERNAL_HEAT_CONFIDENCE: Final = "external_heat_confidence"
ATTR_EXTERNAL_HEAT_EVIDENCE: Final = "external_heat_evidence"

# --- Unknown price horizon (item 7) ----------------------------------------
#
# Prices past the published horizon used to be a flat repeat of the last known
# value. A flat tail has no trough, so the optimizer could not see a cheap
# period ahead worth waiting for and systematically under-deferred load.
CONF_PRICE_PRIOR_ENABLED: Final = "price_prior_enabled"
DEFAULT_PRICE_PRIOR_ENABLED: Final = True
PRICE_MODEL_STORE_VERSION: Final = 1

ATTR_PRICE_KNOWN_STEPS: Final = "price_known_steps"
ATTR_PRICE_PRIOR_DAYS: Final = "price_prior_days"

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

ATTR_PEAK_BILLED_KW: Final = "billed_peak_kw"
ATTR_PEAK_THRESHOLD_KW: Final = "peak_threshold_kw"
ATTR_PEAK_PROJECTED_KW: Final = "projected_peak_kw"

# --- Compressor cycling, item 10 -------------------------------------------
#
# Defaults to zero so the shipped behaviour is unchanged until a user decides
# their compressor's start cost is worth paying for. ``tests/validate.py``
# reports the start count per scenario, which is how that decision gets made
# from evidence rather than from assumption.
CONF_CYCLING_COST: Final = "compressor_cycling_cost"
DEFAULT_CYCLING_COST: Final = 0.0
ATTR_COMPRESSOR_STARTS: Final = "compressor_starts"

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
ATTR_COMFORT_WEIGHT_LEARNED: Final = "comfort_weight_learned"

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

ATTR_TEMPERATURE_MAE: Final = "temperature_mae"
ATTR_COST_ERROR_PERCENT: Final = "cost_error_percent"

# Service for the card's what-if simulator (item 21).
SERVICE_SIMULATE_PLAN: Final = "simulate_plan"
SERVICE_APPLY_SCHEDULE: Final = "apply_schedule"
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
CONF_BUFFER_TANK_TEMP_ENTITY: Final = "buffer_tank_temp_entity"
CONF_HOUSE_HEAT_LOSS_SCALE: Final = "house_heat_loss_scale"  # dimensionless

# DHW demand windows — the time frames where hot water must be available
CONF_DHW_SCHEDULE_ENABLED: Final = "dhw_schedule_enabled"
CONF_DHW_WINDOWS: Final = "dhw_windows"  # "06:00-08:30, 17:00-22:00"
CONF_DHW_IDLE_MIN_TEMP: Final = "dhw_idle_min_temperature"  # °C outside windows

# DHW anti-legionella cycle
CONF_DHW_LEGIONELLA_ENABLED: Final = "dhw_legionella_enabled"
CONF_DHW_LEGIONELLA_TEMP: Final = "dhw_legionella_temperature"  # °C
CONF_DHW_LEGIONELLA_INTERVAL_DAYS: Final = "dhw_legionella_interval_days"

# Weather sensitivity parameters
CONF_WIND_SENSITIVITY: Final = "wind_sensitivity_factor"  # fraction per m/s
CONF_RAIN_HEAT_LOSS_MULTIPLIER: Final = "rain_heat_loss_multiplier"  # multiplier

# Optimization settings
CONF_OPTIMIZATION_HORIZON: Final = "optimization_horizon"  # hours
CONF_OPTIMIZATION_INTERVAL: Final = "optimization_interval"  # minutes
CONF_TIME_STEP: Final = "time_step"  # minutes
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

# Solar gain defaults
DEFAULT_WINDOW_AREA: Final = 10.0  # m² total glazing area
DEFAULT_SOLAR_ORIENTATION_FACTOR: Final = 0.7  # south-facing bias
DEFAULT_SOLAR_HEAT_GAIN_COEFF: Final = 0.7  # typical double-glazed low-e
DEFAULT_SOLAR_UPPER_FRACTION: Final = 0.4  # 40% upper, 60% lower (open layout, sun hits lower floor)

# DHW defaults
DEFAULT_DHW_TANK_VOLUME: Final = 200.0  # liters
DEFAULT_DHW_SETPOINT: Final = 55.0  # °C - "ready" temperature at window start
DEFAULT_DHW_MIN_TEMP: Final = 45.0  # °C - usable minimum inside demand windows
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

# The house heat loss coefficient the user configures is a nameplate estimate.
# What the optimizer actually needs is how fast *this* house loses heat, so the
# coordinator learns a dimensionless correction factor from the error between
# predicted and observed indoor temperature. 1.0 means the configured value is
# exactly right; the bounds stop a bad sensor or an open window from running
# away with the model.
DEFAULT_HOUSE_HEAT_LOSS_SCALE: Final = 1.0
HOUSE_HEAT_LOSS_SCALE_MIN: Final = 0.3
HOUSE_HEAT_LOSS_SCALE_MAX: Final = 3.0

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

# Weather sensitivity defaults
DEFAULT_WIND_SENSITIVITY: Final = 0.15  # 15% heat loss increase per m/s wind
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

DEFAULT_OPTIMIZATION_HORIZON: Final = 24  # hours
DEFAULT_OPTIMIZATION_INTERVAL: Final = 30  # minutes
DEFAULT_TIME_STEP: Final = 15  # minutes
DEFAULT_PRICE_WEIGHT: Final = 1.0
DEFAULT_COMFORT_WEIGHT: Final = 5.0

# Update intervals
UPDATE_INTERVAL_PRICES: Final = timedelta(minutes=15)
UPDATE_INTERVAL_WEATHER: Final = timedelta(minutes=30)
UPDATE_INTERVAL_OPTIMIZATION: Final = timedelta(minutes=30)

# Optimization modes
MODE_COMFORT: Final = "comfort"
MODE_ECONOMY: Final = "economy"
MODE_OFF: Final = "off"
MODE_BOOST: Final = "boost"
MODE_AUTO: Final = "auto"

# Service names
SERVICE_RUN_OPTIMIZATION: Final = "run_optimization"
SERVICE_SET_MODE: Final = "set_mode"
SERVICE_SET_THERMAL_PARAMS: Final = "set_thermal_parameters"

# Attributes
ATTR_NEXT_OPTIMIZATION: Final = "next_optimization"
ATTR_LAST_OPTIMIZATION: Final = "last_optimization"
ATTR_CURRENT_SCHEDULE: Final = "current_schedule"
ATTR_PREDICTED_SAVINGS: Final = "predicted_savings"
ATTR_PREDICTED_COST: Final = "predicted_cost"
ATTR_BASELINE_COST: Final = "baseline_cost"
ATTR_OPTIMIZATION_STATUS: Final = "optimization_status"
ATTR_CURRENT_PRICE: Final = "current_price"
ATTR_AVG_PRICE_24H: Final = "average_price_24h"
ATTR_INDOOR_TEMP: Final = "indoor_temperature"
ATTR_OUTDOOR_TEMP: Final = "outdoor_temperature"
ATTR_HEAT_PUMP_STATE: Final = "heat_pump_state"
ATTR_HEAT_PUMP_SETPOINT: Final = "heat_pump_setpoint"
ATTR_COP_CURRENT: Final = "current_cop"
ATTR_HEAT_PUMP_ON: Final = "heat_pump_on"
ATTR_ECL110_DISPLACE: Final = "ecl110_displace"
ATTR_ECL110_EFFECTIVE_DISPLACE: Final = "ecl110_effective_displace"
ATTR_ECL110_COMMAND_PAYLOAD: Final = "ecl110_command_payload"

# Two-zone attributes
ATTR_UPPER_FLOOR_TEMP: Final = "upper_floor_temperature"
ATTR_LOWER_FLOOR_TEMP: Final = "lower_floor_temperature"
ATTR_UPPER_FLOOR_SETPOINT: Final = "upper_floor_setpoint"
ATTR_LOWER_FLOOR_SETPOINT: Final = "lower_floor_setpoint"
ATTR_SLAB_TEMP: Final = "slab_temperature"
ATTR_BUFFER_TANK_TEMP: Final = "buffer_tank_temperature"
ATTR_SOLAR_GAIN: Final = "solar_heat_gain"
ATTR_SOLAR_RADIATION: Final = "solar_radiation"
ATTR_FLOOR_RETURN_TEMP: Final = "floor_return_temperature"

# DHW attributes
ATTR_DHW_TEMP: Final = "dhw_temperature"
ATTR_DHW_SETPOINT: Final = "dhw_setpoint"
ATTR_DHW_HEATING_ACTIVE: Final = "dhw_heating_active"
ATTR_DHW_HEATING_SCHEDULE: Final = "dhw_heating_schedule"
ATTR_DHW_HEATING_COST: Final = "dhw_heating_cost"
ATTR_DHW_WINDOWS: Final = "dhw_windows"
ATTR_DHW_IN_DEMAND_WINDOW: Final = "dhw_in_demand_window"
ATTR_DHW_NEXT_WINDOW_IN_HOURS: Final = "dhw_next_window_in_hours"
ATTR_DHW_REQUIRED_TEMP: Final = "dhw_required_temperature"
ATTR_DHW_LEGIONELLA_DUE_IN_HOURS: Final = "dhw_legionella_due_in_hours"
ATTR_DHW_COOLING_RATE: Final = "dhw_cooling_rate"
ATTR_DHW_COOLING_RATE_LEARNED: Final = "dhw_cooling_rate_learned"
ATTR_DHW_COOLING_SAMPLES: Final = "dhw_cooling_samples"
ATTR_DHW_HOLD_HOURS: Final = "dhw_hold_hours"
ATTR_DHW_PREHEAT_HOURS: Final = "dhw_preheat_hours"
ATTR_BUFFER_COOLING_RATE: Final = "buffer_cooling_rate"
ATTR_BUFFER_COOLING_RATE_LEARNED: Final = "buffer_cooling_rate_learned"
ATTR_BUFFER_COOLING_SAMPLES: Final = "buffer_cooling_samples"
ATTR_HOUSE_HEAT_LOSS_SCALE: Final = "house_heat_loss_scale"
ATTR_HOUSE_HEAT_LOSS_LEARNED: Final = "house_heat_loss_learned"
ATTR_HOUSE_HEAT_LOSS_SAMPLES: Final = "house_heat_loss_samples"
ATTR_HOUSE_HEAT_LOSS_EFFECTIVE: Final = "house_heat_loss_effective"

# Wind chill factor (additional heat loss per m/s wind) — legacy, now configurable
WIND_CHILL_FACTOR: Final = 0.005  # kW/°C per m/s
# Rain cooling factor — legacy, now configurable
RAIN_COOLING_FACTOR: Final = 0.01  # kW/°C per mm/h

# The buffer tank key is defined after the staleness table above, so its age
# limit is registered here rather than inline.
INPUT_MAX_AGE_MINUTES[CONF_BUFFER_TANK_TEMP_ENTITY] = 60.0
INPUT_MAX_AGE_MINUTES[CONF_PV_PRODUCTION_ENTITY] = 30.0

# Attributes for the measured power / COP feature
ATTR_MEASURED_POWER: Final = "measured_power"
ATTR_MEASURED_POWER_AVAILABLE: Final = "measured_power_available"
ATTR_COP_SCALE: Final = "cop_scale"
ATTR_COP_SAMPLES: Final = "cop_samples"
ATTR_COP_MEASURED: Final = "measured_cop"