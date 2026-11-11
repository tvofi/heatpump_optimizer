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


class DeviceEntry:
    """A subset of ``homeassistant.helpers.device_registry.DeviceEntry``.

    The fields the options flow's device pre-fill reads (#1067 W1067-G7b),
    plus the identity upstream keys a device by. Upstream's is a frozen
    attrs class with two dozen more fields (connections, area_id, hw/sw
    version, via_device_id, labels); none is read here and none is modelled.
    """

    def __init__(
        self,
        id: str,
        *,
        name: str | None = None,
        name_by_user: str | None = None,
        manufacturer: str | None = None,
        model: str | None = None,
        identifiers: set | None = None,
        config_entries: set | None = None,
        entry_type: DeviceEntryType | None = None,
        disabled_by: str | None = None,
    ) -> None:
        self.id = id
        self.name = name
        self.name_by_user = name_by_user
        self.manufacturer = manufacturer
        self.model = model
        self.identifiers = identifiers or set()
        self.config_entries = config_entries or set()
        self.entry_type = entry_type
        self.disabled_by = disabled_by


class DeviceRegistry:
    """A dict of devices with upstream's ``async_get``.

    Upstream's creation path (``async_get_or_create``, its identifier and
    connection merging, and the update/removal events) is not mimicked;
    tests seed entries with the test-facing ``add``.
    """

    def __init__(self) -> None:
        self.devices: dict[str, DeviceEntry] = {}

    def add(self, device_id: str, **fields) -> DeviceEntry:
        entry = DeviceEntry(device_id, **fields)
        self.devices[device_id] = entry
        return entry

    def async_get(self, device_id: str) -> DeviceEntry | None:
        return self.devices.get(device_id)


_REGISTRY_KEY = "_stub_device_registry"


def async_get(hass) -> DeviceRegistry:
    """One registry per hass, as the entity-registry stub does."""
    registry = hass.data.get(_REGISTRY_KEY)
    if registry is None:
        registry = DeviceRegistry()
        hass.data[_REGISTRY_KEY] = registry
    return registry
