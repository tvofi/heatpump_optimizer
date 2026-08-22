"""Minimal stand-in for ``homeassistant.helpers.update_coordinator``."""


class DataUpdateCoordinator:
    def __init__(self, *args, **kwargs):
        self.hass = args[0] if args else kwargs.get("hass")
        self.data = None


class UpdateFailed(Exception):
    pass


class CoordinatorEntity:
    """Just enough of the real thing to construct an entity in a test."""

    def __init__(self, coordinator, context=None):
        self.coordinator = coordinator
