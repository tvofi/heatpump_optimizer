"""Minimal stand-in for the climate platform's entity API."""


class ClimateEntityFeature(int):
    TARGET_TEMPERATURE = 1
    PRESET_MODE = 16
    TURN_ON = 256
    TURN_OFF = 128


class HVACMode(str):
    OFF = "off"
    HEAT = "heat"
    AUTO = "auto"


class HVACAction(str):
    OFF = "off"
    IDLE = "idle"
    HEATING = "heating"


class ClimateEntity:
    _attr_has_entity_name = False
    _attr_name = None
    _attr_unique_id = None
