"""Minimal stand-in for ``homeassistant.const``.

Only the members the integration actually imports are defined. Kept
deliberately small: a fuller stub would drift from the real thing without
anybody noticing, and the point here is to let the integration import without
a Home Assistant install, not to reimplement it.
"""


class Platform(str):
    SENSOR = "sensor"
    BINARY_SENSOR = "binary_sensor"
    BUTTON = "button"
    CLIMATE = "climate"
    SWITCH = "switch"
    DIAGNOSTICS = "diagnostics"


CONF_NAME = "name"


class UnitOfSpeed:
    METERS_PER_SECOND = "m/s"
    KILOMETERS_PER_HOUR = "km/h"
    MILES_PER_HOUR = "mph"
    KNOTS = "kn"
    FEET_PER_SECOND = "ft/s"
    BEAUFORT = "Beaufort"


class UnitOfPower:
    WATT = "W"
    KILO_WATT = "kW"


class UnitOfEnergy:
    WATT_HOUR = "Wh"
    KILO_WATT_HOUR = "kWh"


class UnitOfTemperature:
    CELSIUS = "°C"
    FAHRENHEIT = "°F"


class UnitOfVolume:
    LITERS = "L"


PERCENTAGE = "%"
ATTR_TEMPERATURE = "temperature"
