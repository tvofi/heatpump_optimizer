"""Minimal stand-in for ``homeassistant.helpers.translation``."""


async def async_get_translations(hass, language, category, integrations=None):
    return {}
