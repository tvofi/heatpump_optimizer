"""Minimal stand-in for the binary_sensor platform's entity API."""


class BinarySensorDeviceClass(str):
    PROBLEM = "problem"
    HEAT = "heat"
    PRESENCE = "presence"


class BinarySensorEntity:
    _attr_has_entity_name = False
    _attr_name = None
    _attr_unique_id = None
