"""Minimal stand-in for the datetime platform's entity API."""

from homeassistant.helpers.entity import Entity


class DateTimeEntity(Entity):
    _attr_has_entity_name = False
    _attr_name = None
    _attr_unique_id = None
