"""Minimal stand-in for the binary_sensor platform's entity API."""

from homeassistant.helpers.entity import Entity


class BinarySensorDeviceClass(str):
    PROBLEM = "problem"
    HEAT = "heat"
    PRESENCE = "presence"
    WINDOW = "window"


class BinarySensorEntity(Entity):
    _attr_has_entity_name = False
    _attr_name = None
    _attr_unique_id = None

    @property
    def device_class(self) -> BinarySensorDeviceClass | None:
        """``components/binary_sensor/__init__.py`` BinarySensorEntity.device_class.

        Upstream's cached_property returns ``_attr_device_class`` when the
        attribute exists, then consults ``entity_description``, then
        ``None``; this copy drops the description branch (the stub does not
        model descriptions) and uses a plain property, for the same reason
        SensorEntity's does -- without it the three binary sensors that
        declare a device class read ``None`` through the public property,
        the #947 vacuity.
        """
        if hasattr(self, "_attr_device_class"):
            return self._attr_device_class
        return None
