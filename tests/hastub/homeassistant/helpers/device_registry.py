"""Minimal stand-in for ``homeassistant.helpers.device_registry``.

Real Home Assistant defines ``DeviceInfo`` here (``homeassistant.helpers.
entity`` re-exports it) and ``DeviceEntryType``, the enum a DeviceInfo's
``entry_type`` field takes -- a StrEnum with the single member ``SERVICE``
in the hacs.json floor 2024.6.0. The production import that needs it is the
coordinator's ``device_info`` property (#305).
"""


class DeviceEntryType(str):
    """Mirrors ``homeassistant.helpers.device_registry.DeviceEntryType``."""

    SERVICE = "service"
