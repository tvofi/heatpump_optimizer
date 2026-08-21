"""Constants for Heat Pump Cost Optimizer."""
from __future__ import annotations

from datetime import timedelta
from typing import Final

DOMAIN: Final = "heatpump_optimizer"
PLATFORMS: Final = ["sensor", "climate", "switch"]

# Schema version of the config entry. Bump when stored keys change in a way
# that needs migrating, and handle it in ``async_migrate_entry``.
CONFIG_ENTRY_VERSION: Final = 6

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