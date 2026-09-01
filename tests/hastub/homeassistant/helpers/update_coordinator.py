"""Minimal stand-in for ``homeassistant.helpers.update_coordinator``."""


class DataUpdateCoordinator:
    def __init__(self, *args, **kwargs):
        self.hass = args[0] if args else kwargs.get("hass")
        self.data = None
        self.refresh_requests = 0
        self.last_update_success = True
        # Real HA's async_shutdown stops the refresh debouncer and any
        # in-flight refresh (config-entry-unloading, Silver). The stub does
        # none of that machinery but records the call, so an override that
        # forgets `super().async_shutdown()` is visible to a test.
        self.base_shutdown_called = False

    async def async_request_refresh(self):
        # Counted rather than executed: a test that exercises a setter should
        # not be dragged into a full optimization run as a side effect.
        self.refresh_requests += 1

    async def async_refresh(self):
        await self.async_request_refresh()

    async def async_config_entry_first_refresh(self):
        # Counted like the other refreshes: entry-lifecycle tests need setup
        # to complete, not to run a full optimization as a side effect.
        await self.async_request_refresh()

    async def async_shutdown(self) -> None:
        self.base_shutdown_called = True

    def async_update_listeners(self):
        return None


class UpdateFailed(Exception):
    pass


class CoordinatorEntity:
    """Just enough of the real thing to construct an entity in a test."""

    def __init__(self, coordinator, context=None):
        self.coordinator = coordinator

    @property
    def available(self) -> bool:
        """Mirror the real base class: unavailable after a failed refresh.

        Entities that override ``available`` are expected to AND their own
        condition with ``super().available``; a stub without this property
        made that conjunction untestable.
        """
        return bool(getattr(self.coordinator, "last_update_success", True))
