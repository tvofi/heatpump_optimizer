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
        unit: str | None = None,
        attributes: dict | None = None,
    ) -> None:
        self.state = state
        self.last_updated = last_updated or datetime.now(UTC)
        self.last_changed = self.last_updated
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
        self._tasks = []

    def async_create_task(self, coro):
        # Nothing here awaits the setup tasks, and leaving the coroutine
        # un-awaited emits a warning that looks like a test failure.
        coro.close()
        return None

    async def async_add_executor_job(self, func, *args):
        return func(*args)


class FakeServices:
    def __init__(self) -> None:
        self.calls = []

    async def async_call(self, domain, service, data=None, **kwargs):
        self.calls.append((domain, service, data))
        return None

    def async_register(self, *args, **kwargs):
        return None

    def async_remove(self, *args, **kwargs):
        return None


class FakeConfig:
    latitude = 59.33
    longitude = 18.07
    language = "en"


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
        self.pressed = []
        for key, value in extra.items():
            setattr(self, key, value)

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


def minutes_ago(minutes: float, now: datetime | None = None) -> datetime:
    return (now or datetime.now(UTC)) - timedelta(minutes=minutes)
