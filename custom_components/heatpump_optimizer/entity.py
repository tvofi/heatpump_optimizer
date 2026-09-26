"""The shared entity base for Heat Pump Cost Optimizer (common-modules, Bronze).

Each platform file used to declare its own ``CoordinatorEntity`` base class,
and the five of them re-declared the same two members -- the
``_attr_has_entity_name`` flag and the ``device_info`` property that lands
every entity on the coordinator's device. Those live here once now (issue
#298); each platform's base classes build on ``HeatPumpOptimizerEntity``
instead of re-declaring them. Everything that differs per platform (the
unique-id key, the pinned ``entity_id``, the translation key) stays in the
platform file that owns it. The plain-and-finite publication scrub lives here
too, so it covers all six platforms rather than the sensor platform alone
(#1541).
"""
from __future__ import annotations

import math
from collections.abc import Awaitable, Coroutine
from typing import Any, Callable

import numpy as np

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity


def commanded_power_kw(action: Any) -> float | None:
    """The current plan step's whole electrical ask, space plus DHW, in kW.

    ``action["power"]`` is the SPACE allocation alone, so publishing it as the
    step's power read 0 kW on a step heating only the tank (#1499). Every
    entity that publishes the step's commanded power -- Heat Pump Action's
    ``power_kw``, Recommended Power, the climate's ``recommended_power_kw``
    and Measured Power's ``recommended_power`` -- reads it here, so they
    cannot disagree. None when the action carries no power at all.
    """
    action = action or {}
    space = action.get("power")
    if space is None:
        return None
    return round(float(space) + float(action.get("dhw_power") or 0.0), 2)


def _finite(value: Any) -> Any:
    """Plain, finite Python for everything an entity publishes, recursively.

    ``inf`` and ``nan`` are not JSON. orjson -- the serializer Home Assistant
    uses for the websocket and the recorder -- writes them as ``null``, so the
    frontend and the database already see "unknown" while a Jinja template
    reading the same attribute in-process sees Python's ``inf`` and compares
    ``> 100`` as true. One published number, two different meanings depending
    on who reads it.

    The values are not accidents. ``PeakTracker.threshold_kw`` returns ``inf``
    on purpose, as a sentinel meaning "the capacity term has no reference yet,
    do not let it distort the plan" -- which is a decision variable, and
    ``None`` ("unknown") is what it means once it becomes a published
    attribute. It is +inf on the 1st of every month, for every install with a
    capacity tariff.

    Applied at the publication boundary rather than at the two sites that
    produce it today, because the interesting case is the one nobody
    predicted: the next attribute that divides by a zero sample count is
    covered without anyone remembering to ask. It was a sensor-only scrub
    until #1541 found climate, switch and binary-sensor attributes publishing
    the raw value; the entity base installs it on every platform now.

    The same boundary plains numpy (#173). The optimizer hands the
    coordinator numpy scalars -- the solar-gain trajectory is one
    ``numpy.float64`` per step -- and the coordinator converts the fields
    it remembers to (``predictive_info`` goes through ``_plain_types``) and
    forgets the rest (``schedule`` did not). Converting here, once, covers
    every entity, and the order matters: ``np.float64`` *subclasses*
    ``float``, so it has to be unwrapped before the finite test or it walks
    through that test unchanged.
    """
    if isinstance(value, np.ndarray):
        return _finite(value.tolist())
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, dict):
        return {key: _finite(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_finite(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_finite(item) for item in value)
    return value


class HeatPumpOptimizerEntity(CoordinatorEntity):
    """What every Heat Pump Optimizer entity has in common.

    Display names come from the translation files (``strings.json`` /
    ``translations/*.json``) via ``translation_key``, so the UI follows the
    Home Assistant language while ``unique_id`` — and therefore history and
    statistics — never moves.
    """

    _attr_has_entity_name = True

    #: The properties Home Assistant reads to build a state write, on every
    #: platform this integration has. Every number it publishes leaves through
    #: one of them, which is why the plain-and-finite scrub is installed here
    #: rather than repeated per entity -- and why an entity added next year
    #: gets it without anyone remembering to ask for it.
    _PUBLISHED = (
        "native_value",
        "extra_state_attributes",
        "current_temperature",
        "target_temperature",
    )

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Wrap every subclass's published properties in the finite scrub."""
        super().__init_subclass__(**kwargs)
        for name in HeatPumpOptimizerEntity._PUBLISHED:
            prop = cls.__dict__.get(name)
            if not isinstance(prop, property) or prop.fget is None:
                continue
            if getattr(prop.fget, "_finite_scrubbed", False):
                continue

            def scrubbed(
                self: HeatPumpOptimizerEntity,
                _fget: Callable[[Any], Any] = prop.fget,
            ) -> Any:
                return _finite(_fget(self))

            scrubbed.__name__ = name
            scrubbed.__doc__ = prop.fget.__doc__
            setattr(scrubbed, "_finite_scrubbed", True)
            setattr(cls, name, property(scrubbed, prop.fset, prop.fdel))

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        info: DeviceInfo = self.coordinator.device_info
        return info


def publish_then_refresh(
    entity: Any, then: Callable[[], Awaitable[None]] | None = None
) -> None:
    """Publish an action's result, then ask for the refresh off the action.

    The payload changes only when that refresh has run its solve, 30 to 70 s
    on a Pi, and outside the debouncer's cooldown the refresh runs the solve
    inline: awaited in the action, the state write -- and, under
    PARALLEL_UPDATES, the next action -- waited for it, so a toggle fell back
    to its old state in the frontend (v6.6.12). As an entry background task
    the refresh starts at once and is cancelled at unload; ``then`` runs
    after it, where the action used to run it. The coordinator logs a failed
    refresh itself, and Home Assistant logs anything a task raises.
    """
    entity.async_write_ha_state()

    async def _refresh() -> None:
        await entity.coordinator.async_request_refresh()
        if then is not None:
            await then()

    off_the_action(entity, _refresh())


def off_the_action(entity: Any, work: Coroutine[Any, Any, Any]) -> None:
    """Run an action's slow part as an entry background task, so it returns.

    A button has published already (upstream writes the press time before
    ``async_press``), but under the button platform's PARALLEL_UPDATES a press
    awaiting a solve held the slot, and a reset pressed behind it was cancelled
    at a restart before its setter ran (RC2, round 9).
    """
    entity._entry.async_create_background_task(
        entity.hass, work, name="heatpump_optimizer_action_refresh"
    )


def has_hot_water(coordinator: Any) -> bool:
    """Whether this install has hot water: the one answer every reader takes.

    The configured flag via ``_thermal_params``, because the registry asks
    before the first refresh; the payload's copy where a test double has
    only that. The boost overlay asks here too (#1527), so a no-DHW install
    cannot be handed hot-water power by a switch it should never have used.
    """
    params = getattr(coordinator, "_thermal_params", None)
    if params is not None:
        return bool(params.dhw_enabled)
    return bool((getattr(coordinator, "data", None) or {}).get("dhw_enabled"))


def input_configured(coordinator: Any, slot: str) -> bool:
    """Whether the user configured this input slot. Read from the config,
    because the registry asks before the first refresh builds a payload."""
    config = getattr(coordinator, "_config", None) or {}
    return bool(config.get(slot))


class ConfiguredInputMixin(HeatPumpOptimizerEntity):
    """An entity that reads an optional input, gated on that input existing.

    Available, and enabled by default, exactly where one of its config
    slots is configured. Four probe temperatures (#1542's shape) and the two
    ECL110 readouts (#1527's) kept a static default-off, or no gate at all,
    beside inputs the user had configured; ``tests/entities.py`` enumerates
    every entity whose default should follow a configured input.
    """

    #: Config slots this entity reads; any one configured lights it.
    _input_slots: tuple[str, ...] = ()

    @property
    def entity_registry_enabled_default(self) -> bool:
        return any(input_configured(self.coordinator, s) for s in self._input_slots)

    @property
    def available(self) -> bool:
        return bool(super().available and self.entity_registry_enabled_default)


class DHWEntityMixin(HeatPumpOptimizerEntity):
    """A hot-water entity, gated on the install actually having hot water.

    Every entity whose subject is hot water takes its availability and its
    registry default from here, on every platform, so a new one inherits the
    gate by construction; ``tests/entities.py`` enumerates them and names
    the exceptions. Two DHW Energy-dashboard meters stuck at 0.0 on a
    no-DHW install, a sixth sensor outside the gate (#1461), and a boost
    switch that injected hot-water power on a plant with no tank (#1527)
    were each this gate missing from one sibling.

    The default is on exactly where there is hot water (#1398), and where
    the entity also needs an optional probe, only once that probe is
    configured (#1542): a tank thermometer the user wired up is not hidden.
    """

    #: The config slot of an optional probe this entity reads beside hot
    #: water, such as the tank thermometer. Empty: hot water alone gates it.
    _dhw_probe_slot: str = ""

    @property
    def entity_registry_enabled_default(self) -> bool:
        """On where the install has hot water and any probe it needs."""
        if not has_hot_water(self.coordinator):
            return False
        if not self._dhw_probe_slot:
            return True
        return input_configured(self.coordinator, self._dhw_probe_slot)

    @property
    def available(self) -> bool:
        return bool(
            super().available
            and self.coordinator.data
            and has_hot_water(self.coordinator)
        )
