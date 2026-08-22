"""Minimal stand-in for the sensor platform's entity API."""


class SensorDeviceClass(str):
    TEMPERATURE = "temperature"
    POWER = "power"
    ENERGY = "energy"
    MONETARY = "monetary"
    IRRADIANCE = "irradiance"
    BATTERY = "battery"
    TIMESTAMP = "timestamp"


class SensorStateClass(str):
    MEASUREMENT = "measurement"
    TOTAL = "total"
    TOTAL_INCREASING = "total_increasing"


class SensorEntity:
    _attr_has_entity_name = False
    _attr_name = None
    _attr_unique_id = None
