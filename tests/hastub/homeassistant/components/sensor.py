"""Minimal stand-in for the sensor platform's entity API."""


class SensorDeviceClass(str):
    TEMPERATURE = "temperature"
    POWER = "power"
    ENERGY = "energy"
    MONETARY = "monetary"
    IRRADIANCE = "irradiance"
    BATTERY = "battery"
    TIMESTAMP = "timestamp"
    FREQUENCY = "frequency"
    VOLUME_STORAGE = "volume_storage"
    ENERGY_STORAGE = "energy_storage"


class SensorStateClass(str):
    MEASUREMENT = "measurement"
    TOTAL = "total"
    TOTAL_INCREASING = "total_increasing"


#: Mirrors ``homeassistant.components.sensor.const.DEVICE_CLASS_STATE_CLASSES``
#: for the device classes this stub declares, copied from the installed Home
#: Assistant rather than reasoned out here. Home Assistant checks this pair
#: on every state write and logs "state class ... which is impossible
#: considering device class" -- a warning in the user's log, and one the core
#: intends to turn into an exception. Note what it does NOT say: the check
#: only fires when a state class is *set*, so a device class with no state
#: class is never a violation.
DEVICE_CLASS_STATE_CLASSES = {
    SensorDeviceClass.TEMPERATURE: {SensorStateClass.MEASUREMENT},
    SensorDeviceClass.POWER: {SensorStateClass.MEASUREMENT},
    SensorDeviceClass.ENERGY: {
        SensorStateClass.TOTAL,
        SensorStateClass.TOTAL_INCREASING,
    },
    SensorDeviceClass.MONETARY: {SensorStateClass.TOTAL},
    SensorDeviceClass.IRRADIANCE: {SensorStateClass.MEASUREMENT},
    SensorDeviceClass.BATTERY: {SensorStateClass.MEASUREMENT},
    SensorDeviceClass.TIMESTAMP: set(),
    SensorDeviceClass.FREQUENCY: {SensorStateClass.MEASUREMENT},
    SensorDeviceClass.VOLUME_STORAGE: {SensorStateClass.MEASUREMENT},
    SensorDeviceClass.ENERGY_STORAGE: {SensorStateClass.MEASUREMENT},
}


class SensorEntity:
    _attr_has_entity_name = False
    _attr_name = None
    _attr_unique_id = None
