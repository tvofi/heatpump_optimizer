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
    ) -> RegistryEntry:
        entry = RegistryEntry(
            entity_id=entity_id,
            unique_id=unique_id,
            domain=entity_id.split(".", 1)[0],
            config_entry_id=config_entry_id,
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
