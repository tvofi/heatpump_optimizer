"""Minimal stand-in for the switch platform's entity API."""

from homeassistant.helpers.entity import Entity


class SwitchEntity(Entity):
    _attr_has_entity_name = False
    _attr_name = None
    _attr_unique_id = None
