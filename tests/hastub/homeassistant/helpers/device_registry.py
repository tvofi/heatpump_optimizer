"""Minimal stand-in for ``homeassistant.helpers.device_registry``.

Real Home Assistant defines ``DeviceInfo`` here (``homeassistant.helpers.
entity`` re-exports it) and ``DeviceEntryType``, the enum a DeviceInfo's
``entry_type`` field takes -- a StrEnum with the single member ``SERVICE``
since 2024.6.0, so it is present at the hacs.json floor. The production
import that needs it is the coordinator's ``device_info`` property (#305).
"""


class DeviceEntryType(str):
    """Mirrors ``homeassistant.helpers.device_registry.DeviceEntryType``."""

    SERVICE = "service"
