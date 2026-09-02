"""Minimal stand-in for ``homeassistant.const``.

Only the members the integration actually imports are defined. Kept
deliberately small: a fuller stub would drift from the real thing without
anybody noticing, and the point here is to let the integration import without
a Home Assistant install, not to reimplement it.
"""


class Platform(str):
    """The subset of Home Assistant's Platform enum this integration uses.

    Every name here MUST exist in the real enum. A member invented for the
    stub's convenience makes the suite pass on code that cannot import in
    Home Assistant: ``DIAGNOSTICS`` was added here in v6.3.1 and every gate
    stayed green while the integration failed to load with
    ``AttributeError: type object 'Platform' has no attribute 'DIAGNOSTICS'``.
    tests/entities.py now pins this class against the real roster.
    """

    SENSOR = "sensor"
    BINARY_SENSOR = "binary_sensor"
    BUTTON = "button"
    CLIMATE = "climate"
    SWITCH = "switch"


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
