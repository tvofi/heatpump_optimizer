"""Minimal stand-in for ``homeassistant.helpers.update_coordinator``."""


class DataUpdateCoordinator:
    def __init__(self, *args, **kwargs):
        self.hass = args[0] if args else kwargs.get("hass")
        self.data = None
        self.refresh_requests = 0

    async def async_request_refresh(self):
        # Counted rather than executed: a test that exercises a setter should
        # not be dragged into a full optimization run as a side effect.
        self.refresh_requests += 1

    async def async_refresh(self):
        await self.async_request_refresh()

    def async_update_listeners(self):
        return None


class UpdateFailed(Exception):
    pass


class CoordinatorEntity:
    """Just enough of the real thing to construct an entity in a test."""

    def __init__(self, coordinator, context=None):
        self.coordinator = coordinator
