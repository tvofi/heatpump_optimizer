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
    ENUM = "enum"


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
    SensorDeviceClass.ENUM: set(),
}

#: ``sensor/const.py`` NON_NUMERIC_DEVICE_CLASSES, minus the classes this stub
#: does not declare. Home Assistant refuses a unit of measurement on these.
NON_NUMERIC_DEVICE_CLASSES = {
    SensorDeviceClass.ENUM,
    SensorDeviceClass.TIMESTAMP,
}


class SensorEntity:
    _attr_has_entity_name = False
    _attr_name = None
    _attr_unique_id = None

    @property
    def options(self) -> list[str] | None:
        """``sensor/__init__.py`` SensorEntity.options."""
        return getattr(self, "_attr_options", None)

    @property
    def state(self):
        """The ENUM half of ``sensor/__init__.py`` SensorEntity.state.

        Transcribed from Home Assistant 2025.2.0 -- the floor `hacs.json`
        declares -- rather than reasoned out here, because a stub that is
        merely plausible is how #536 and #543 shipped: a test pins the stub
        and the production path is never exercised as an installation runs
        it. Only the enum and unit branches are mirrored; the numeric
        conversion path is not, so this returns ``native_value`` unchanged
        for every sensor that declares no options.

        The three refusals, in upstream's order and with upstream's meaning:
        a non-numeric device class may carry no unit; ``None`` short-circuits
        BEFORE the options check, so an unavailable enum sensor is
        ``STATE_UNKNOWN`` rather than an error; and a value outside the
        declared options raises. That last one is the whole reason this
        exists -- upstream raises ``ValueError`` on EVERY state write, so an
        option list that misses a reachable state takes the entity down on a
        real install and nowhere else.
        """
        value = self.native_value
        device_class = getattr(self, "_attr_device_class", None)
        if (
            device_class in NON_NUMERIC_DEVICE_CLASSES
            and self.native_unit_of_measurement
        ):
            raise ValueError(
                f"Sensor {type(self).__name__} has a unit of measurement and "
                "thus indicating it has a numeric value; however, it has the "
                f"non-numeric device class: {device_class}"
            )
        if value is None:
            return None
        options = self.options
        if options is not None or device_class is SensorDeviceClass.ENUM:
            if device_class is not SensorDeviceClass.ENUM:
                reason = "is missing the enum device class"
                if device_class is not None:
                    reason = f"has device class '{device_class}' instead of 'enum'"
                raise ValueError(
                    f"Sensor {type(self).__name__} is providing enum options, "
                    f"but {reason}"
                )
            if options and value not in options:
                raise ValueError(
                    f"Sensor {type(self).__name__} provides state value "
                    f"'{value}', which is not in the list of options provided"
                )
        return value

    @property
    def native_unit_of_measurement(self):
        return getattr(self, "_attr_native_unit_of_measurement", None)
