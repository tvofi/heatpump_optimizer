"""Shared scaffolding for the unit-style tests.

The existing suite is made of end-to-end scripts that assert on outcomes. That
catches an optimizer that gets obviously worse, but it cannot catch a detector
that never fires, a watchdog that lets a flatline through, or a tariff model
that charges the whole month's fee once per hour. Those need the modules driven
directly, which is what these helpers are for.

Deliberately not pytest: the rest of the suite is plain scripts so it can run
against a real Home Assistant environment without extra tooling, and mixing two
runners in one directory would be worse than a small amount of duplication.
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

UTC = timezone.utc


class Results:
    """A tiny pass/fail recorder shared by the test scripts."""

    def __init__(self, title: str) -> None:
        self.title = title
        self.failures = 0
        self.checks = 0
        print(f"\n=== {title} ===")

    def section(self, name: str) -> None:
        print(f"\n-- {name}")

    def check(self, name: str, condition: bool, detail: str = "") -> bool:
        self.checks += 1
        if condition:
            print(f"  ok   {name}")
        else:
            self.failures += 1
            suffix = f"  [{detail}]" if detail else ""
            print(f"  FAIL {name}{suffix}")
        return bool(condition)

    def close(self, label: str) -> int:
        if self.failures:
            print(f"\n{self.failures} of {self.checks} {label} FAILED")
            return 1
        print(f"\nALL {self.checks} {label} PASSED")
        return 0


class FakeState:
    """Stand-in for a Home Assistant state object."""

    def __init__(
        self,
        state,
        *,
        last_updated: datetime | None = None,
        last_reported: datetime | None = None,
        unit: str | None = None,
        attributes: dict | None = None,
    ) -> None:
        self.state = state
        self.last_updated = last_updated or datetime.now(UTC)
        self.last_changed = self.last_updated
        # Home Assistant sets this on every state WRITE, including one that
        # rewrites an unchanged value, which is why InputReader prefers it.
        # The stub had no such attribute at all, so every freshness test in
        # the suite was silently exercising the last_updated fallback and the
        # mechanism v5.2.0's cloud-gap argument rests on was never run.
        # Defaults to last_updated (an entity that has only ever changed),
        # and a test that wants a re-reporting sensor sets it explicitly.
        self.last_reported = last_reported or self.last_updated
        self.attributes = dict(attributes or {})
        if unit is not None:
            self.attributes["unit_of_measurement"] = unit


class FakeStates:
    def __init__(self, mapping: dict | None = None) -> None:
        self._states = dict(mapping or {})

    def get(self, entity_id):
        return self._states.get(entity_id)

    def set(self, entity_id, state):
        self._states[entity_id] = state

    def keys(self):
        return self._states.keys()


class FakeHass:
    """The slice of ``hass`` the integration actually touches in these tests."""

    def __init__(self, states: dict | None = None) -> None:
        self.states = FakeStates(states)
        self.data = {}
        self.services = FakeServices()
        self.config = FakeConfig()
        self.config_entries = FakeConfigEntries()
        self.http = FakeHttp()
        self._tasks = []

    def async_create_task(self, coro):
        # Nothing here awaits the setup tasks, and leaving the coroutine
        # un-awaited emits a warning that looks like a test failure.
        coro.close()
        return None

    async def async_add_executor_job(self, func, *args):
        return func(*args)


class FakeServiceCall:
    """The slice of ``ServiceCall`` the integration's handlers read."""

    def __init__(self, domain, service, data) -> None:
        self.domain = domain
        self.service = service
        self.data = dict(data or {})


class FakeServices:
    """Honest registration state, not a no-op.

    A stub that swallows ``async_register`` cannot catch a service that is
    registered but never removed — which is exactly the class of leak the
    lifecycle tests exist for — so the registry is real: registration stores
    the handler, removal deletes it, and ``async_services`` reports what is
    actually there. ``async_call`` dispatches through the stored schema to
    the stored handler, the way Home Assistant does, so a service test
    exercises the handler body rather than a recording stub.
    """

    def __init__(self) -> None:
        self.calls = []
        self._registry: dict[str, dict] = {}
        self._schemas: dict[tuple, object] = {}

    async def async_call(self, domain, service, data=None, **kwargs):
        self.calls.append((domain, service, data))
        handler = self._registry.get(domain, {}).get(service)
        if handler is None:
            return None
        schema = self._schemas.get((domain, service))
        payload = schema(dict(data or {})) if schema is not None else dict(data or {})
        return await handler(FakeServiceCall(domain, service, payload))

    def async_register(self, domain, service, handler, schema=None, **kwargs):
        self._registry.setdefault(domain, {})[service] = handler
        self._schemas[(domain, service)] = schema

    def async_remove(self, domain, service):
        self._registry.get(domain, {}).pop(service, None)
        self._schemas.pop((domain, service), None)

    def async_services(self) -> dict:
        return self._registry


class FakeConfigEntries:
    """Platform forwarding is not what these tests exercise; it just has to
    report success so the entry-level setup/unload paths can run whole. The
    entry roster is real so service handlers that resolve their targets via
    ``async_entries`` find the entry the test set up."""

    def __init__(self) -> None:
        self.entries = []
        self.reloaded = []

    def async_entries(self, domain=None):
        return list(self.entries)

    async def async_reload(self, entry_id):
        self.reloaded.append(entry_id)
        return True

    async def async_forward_entry_setups(self, entry, platforms):
        return None

    async def async_unload_platforms(self, entry, platforms):
        return True

    def async_update_entry(self, entry, **kwargs):
        for key, value in kwargs.items():
            setattr(entry, key, value)


class FakeHttp:
    def register_static_path(self, *args, **kwargs):
        return None


class FakeConfig:
    latitude = 59.33
    longitude = 18.07
    language = "en"
    # What a Swedish install has configured; also what the golden coordinator
    # fixtures pin as the published currency leaf.
    currency = "SEK"


class FakeCoordinator:
    """A coordinator stand-in for exercising the entity classes.

    The entities are thin readers over ``coordinator.data``, so testing them
    against a dict is both sufficient and much less brittle than constructing a
    real coordinator, which is precisely the fixture fragility the backlog
    warned about.
    """

    def __init__(self, data: dict | None = None, **extra) -> None:
        self.data = data
        self.device_info = {"identifiers": {("heatpump_optimizer", "test")}}
        self.optimization_running = False
        self.system_identification_active = False
        # Mirrors DataUpdateCoordinator: True until a refresh fails. Lets
        # entity tests flip it and watch ``super().available`` conjunctions.
        self.last_update_success = True
        self.pressed = []
        # What the real coordinator resolves from hass.config at construction.
        self.currency = "SEK"
        # What the climate thermostat card shows as the user's target.
        self.target_temperature = 21.0
        self.mode_calls: list[str] = []
        for key, value in extra.items():
            setattr(self, key, value)

    async def async_set_mode(self, mode):
        self.mode_calls.append(mode)

    async def async_set_target_temperature(self, temp):
        self.target_temperature = float(temp)

    def record_setpoint_override(self, temp):
        self.pressed.append(f"override:{temp}")

    async def async_publish_current_action(self, reason=None):
        self.pressed.append(f"publish:{reason}")

    def describe_setup(self) -> dict:
        """The topology the plan sensors publish for the card's setup page."""
        return {"two_zone": False, "dhw": False, "slots": []}

    async def async_force_optimization(self):
        self.pressed.append("force_optimization")

    async def async_arm_system_identification(self):
        self.pressed.append("system_identification")

    async def async_reset_comfort_weight(self):
        self.pressed.append("reset_comfort_weight")


class FakeEntry:
    def __init__(self, data: dict | None = None, options: dict | None = None) -> None:
        self.data = dict(data or {})
        self.options = dict(options or {})
        self.entry_id = "test_entry"
        self.version = 1
        self._on_unload = []

    def add_update_listener(self, listener):
        return lambda: None

    def async_on_unload(self, func):
        self._on_unload.append(func)


def minutes_ago(minutes: float, now: datetime | None = None) -> datetime:
    return (now or datetime.now(UTC)) - timedelta(minutes=minutes)
