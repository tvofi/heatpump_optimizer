"""Minimal stand-in for ``homeassistant.helpers.entity_registry``.

Just enough of the real API for the integration's retired-entity cleanup to
run and be tested: a per-hass registry holding entries addressable by
entity_id, with the three functions the integration calls. Tests pre-seed
entries with ``EntityRegistry.add``; the real API's richer creation path is
deliberately not mimicked.
"""
from __future__ import annotations

from dataclasses import dataclass

_REGISTRY_KEY = "_stub_entity_registry"


@dataclass
class RegistryEntry:
    entity_id: str
    unique_id: str
    domain: str
    config_entry_id: str | None = None
    # The device pre-fill's fields (#1067 W1067-G7b). Upstream carries the
    # integration that created the entry in ``platform`` and the device it
    # belongs to in ``device_id``; ``device_class`` is the user's override
    # and ``original_device_class`` the integration's, and
    # ``unit_of_measurement`` is likewise the override of a unit the state
    # carries. All default to None here, so the retired-entity cleanup's
    # own entries are unchanged.
    device_id: str | None = None
    platform: str | None = None
    original_name: str | None = None
    translation_key: str | None = None
    device_class: str | None = None
    original_device_class: str | None = None
    unit_of_measurement: str | None = None


class EntityRegistry:
    def __init__(self) -> None:
        self.entities: dict[str, RegistryEntry] = {}
        self.removed: list[str] = []

    def add(
        self,
        entity_id: str,
        *,
        unique_id: str,
        config_entry_id: str | None = None,
        **fields,
    ) -> RegistryEntry:
        entry = RegistryEntry(
            entity_id=entity_id,
            unique_id=unique_id,
            domain=entity_id.split(".", 1)[0],
            config_entry_id=config_entry_id,
            **fields,
        )
        self.entities[entity_id] = entry
        return entry

    def async_remove(self, entity_id: str) -> None:
        self.entities.pop(entity_id, None)
        self.removed.append(entity_id)


def async_get(hass) -> EntityRegistry:
    registry = hass.data.get(_REGISTRY_KEY)
    if registry is None:
        registry = EntityRegistry()
        hass.data[_REGISTRY_KEY] = registry
    return registry


def async_entries_for_config_entry(
    registry: EntityRegistry, config_entry_id: str
) -> list[RegistryEntry]:
    return [
        entry
        for entry in registry.entities.values()
        if entry.config_entry_id == config_entry_id
    ]


def async_entries_for_device(
    registry: EntityRegistry, device_id: str, include_disabled_entities: bool = False
) -> list[RegistryEntry]:
    """Every entry belonging to one device.

    Upstream reads an index built at registry load and, by default, hides
    disabled entries; the stub models no ``disabled_by``, so the flag is
    accepted and every entry of the device is returned.
    """
    return [
        entry
        for entry in registry.entities.values()
        if entry.device_id == device_id
    ]
