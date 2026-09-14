"""Stand-in for ``homeassistant.helpers.update_coordinator``.

D1-INST (#924): these entry points used to be counters that never ran
``_async_update_data``, so no gate-suite lane ever exercised the base class's
reaction chain -- ``UpdateFailed -> last_update_success False -> entities
unavailable``, the debouncer, the listener fan-out. They now run the chain as
upstream 2025.2.0 does, and ``tests/ha_contract.py`` pins each observable
against both this stub and the real package (nightly lane).

What is deliberately still absent (the inventory entry in ha_contract.py is
the authority): the loop-driven interval scheduler -- the fakes carry no
``hass.loop`` and no test may grow a background poller mid-run --
``update_method``/``setup_method``, the manual-push setters, and the
wrong-state warning ``async_config_entry_first_refresh`` logs upstream (at
the 2025.2.0 floor it warns and continues, so skipping it changes nothing).
"""

import asyncio

from homeassistant.exceptions import ConfigEntryNotReady

REQUEST_REFRESH_DEFAULT_COOLDOWN = 10


class Debouncer:
    """Inline stand-in for ``homeassistant.helpers.debounce.Debouncer``.

    Upstream's (cooldown=10, immediate=True) semantics: the first call runs
    the function then arms the cooldown; calls inside the cooldown coalesce
    into one trailing run at its end. The execute lock is a flag rather than
    an ``asyncio.Lock`` because the suite drives one coordinator across many
    ``asyncio.run`` scopes and a Lock binds itself to its first loop. The
    trailing run rides ``hass.async_create_task`` where the hass has one,
    which under the shared fakes closes it -- a fake that never runs tasks
    cannot run the trailing refresh either, and that divergence is the
    environment's, recorded here rather than papered over.
    """

    def __init__(self, hass, logger, *, cooldown, immediate, function=None):
        self.hass = hass
        self.logger = logger
        self.cooldown = cooldown
        self.immediate = immediate
        self._function = function
        self._timer_task = None
        self._execute_at_end_of_timer = False
        self._executing = False
        self._shutdown_requested = False

    def _schedule_or_call_now(self) -> bool:
        """Whether the function should run now, upstream's decision tree."""
        if self._shutdown_requested:
            return False
        if self._timer_task is not None:
            self._execute_at_end_of_timer = True
            return False
        if self._executing:
            return False
        if not self.immediate:
            self._execute_at_end_of_timer = True
            self._schedule_timer()
            return False
        return True

    async def async_call(self) -> None:
        if not self._schedule_or_call_now():
            return
        self._executing = True
        try:
            if self._timer_task is not None:
                return
            result = self._function()
            if asyncio.iscoroutine(result):
                await result
        finally:
            self._executing = False
            self._schedule_timer()

    async def _handle_timer_finish(self) -> None:
        self._execute_at_end_of_timer = False
        if self._executing:
            return
        self._executing = True
        try:
            if self._timer_task is not None:
                return
            result = self._function()
            if asyncio.iscoroutine(result):
                await result
        finally:
            self._executing = False
            self._schedule_timer()

    def _on_debounce(self) -> None:
        self._timer_task = None
        if not self._execute_at_end_of_timer:
            return
        self._execute_at_end_of_timer = False
        create = getattr(self.hass, "async_create_task", None)
        if create is None:
            return
        create(self._handle_timer_finish())

    def async_cancel(self) -> None:
        if self._timer_task is not None:
            self._timer_task.cancel()
            self._timer_task = None
        self._execute_at_end_of_timer = False

    def async_shutdown(self) -> None:
        self._shutdown_requested = True
        self.async_cancel()
        self._function = None

    def _schedule_timer(self) -> None:
        if self._shutdown_requested:
            return
        loop = getattr(self.hass, "loop", None)
        if loop is None:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                return
        self._timer_task = loop.call_later(self.cooldown, self._on_debounce)


class DataUpdateCoordinator:
    def __init__(self, hass, logger=None, *, name=None, update_interval=None,
                 config_entry=None, **_ignored):
        self.hass = hass
        self.logger = logger
        self.name = name
        self.config_entry = config_entry
        self.data = None
        # Stub telemetry: how many debounced refreshes were REQUESTED. The
        # audit instruments read it; it counts requests, never cycles.
        self.refresh_requests = 0
        self.last_update_success = True
        self.last_exception = None
        self._listeners = {}
        self._last_listener_id = 0
        self._shutdown_requested = False
        # Real HA's async_shutdown stops the refresh debouncer and any
        # in-flight refresh (config-entry-unloading, Silver). Kept from the
        # counter era: the call is recorded so an override that forgets
        # `super().async_shutdown()` is visible to a test.
        self.base_shutdown_called = False
        self._debounced_refresh = Debouncer(
            hass,
            logger,
            cooldown=REQUEST_REFRESH_DEFAULT_COOLDOWN,
            immediate=True,
            function=self.async_refresh,
        )
        # Upstream registers shutdown on the entry it was built for; the
        # entry manager runs it when the entry goes away.
        on_unload = getattr(config_entry, "async_on_unload", None) \
            if config_entry is not None else None
        if on_unload is not None:
            on_unload(self.async_shutdown)

    def _log(self, level, message, *args) -> None:
        target = getattr(self.logger, level, None)
        if callable(target):
            target(message, *args)

    async def _async_update_data(self):
        raise NotImplementedError("Update method not implemented")

    async def _async_refresh(self, *, log_failures=True) -> None:
        """Upstream's reaction chain, minus the scheduler arms."""
        self._debounced_refresh.async_cancel()
        if self._shutdown_requested:
            return
        previous_update_success = self.last_update_success
        previous_data = self.data
        try:
            self.data = await self._async_update_data()
        except (UpdateFailed, TimeoutError) as err:
            self.last_exception = err
            if self.last_update_success:
                if log_failures:
                    self._log(
                        "error", "Error fetching %s data: %s", self.name, err
                    )
                self.last_update_success = False
        except Exception as err:  # noqa: BLE001 - upstream latches, never raises
            self.last_exception = err
            self.last_update_success = False
            self._log(
                "error", "Unexpected error fetching %s data: %s", self.name, err
            )
        else:
            if not self.last_update_success:
                self.last_update_success = True
                self._log("info", "Fetching %s data recovered", self.name)
        if not self.last_update_success and not previous_update_success:
            return
        if (
            self.last_update_success != previous_update_success
            or previous_data != self.data
        ):
            self.async_update_listeners()

    async def async_refresh(self) -> None:
        await self._async_refresh(log_failures=True)

    async def async_config_entry_first_refresh(self) -> None:
        await self._async_refresh(log_failures=False)
        if self.last_update_success:
            return
        ex = ConfigEntryNotReady()
        ex.__cause__ = self.last_exception
        raise ex

    async def async_request_refresh(self) -> None:
        self.refresh_requests += 1
        await self._debounced_refresh.async_call()

    async def async_shutdown(self) -> None:
        self.base_shutdown_called = True
        self._shutdown_requested = True
        self._debounced_refresh.async_shutdown()

    def async_add_listener(self, update_callback, context=None):
        """Register a listener; the return value removes it again."""
        self._last_listener_id += 1
        listener_id = self._last_listener_id
        self._listeners[listener_id] = (update_callback, context)

        def _remove_listener():
            self._listeners.pop(listener_id, None)

        return _remove_listener

    def async_update_listeners(self):
        for update_callback, _context in list(self._listeners.values()):
            update_callback()


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
