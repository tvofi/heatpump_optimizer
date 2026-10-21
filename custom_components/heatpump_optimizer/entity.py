"""The shared entity base for Heat Pump Cost Optimizer (common-modules, Bronze).

Each platform file used to declare its own ``CoordinatorEntity`` base class,
and the five of them re-declared the same two members -- the
``_attr_has_entity_name`` flag and the ``device_info`` property that lands
every entity on the coordinator's device. Those live here once now (issue
#298); each platform's base classes build on ``HeatPumpOptimizerEntity``
instead of re-declaring them. The rule that derives an entity's three ids
lives here too (#1742), and the platform file keeps only the values it feeds
that rule: the unique-id key, the translation key and the platform. The
plain-and-finite publication scrub lives here as well, so it covers all six
platforms rather than the sensor platform alone (#1541).

Nothing here imports from the package, so the core never imports the surface
layer; the coordinator is read through its public names only (#1739).
"""
from __future__ import annotations

import math
from collections.abc import Awaitable, Coroutine
from typing import TYPE_CHECKING, Any, Callable

import numpy as np

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .payload import Payload

if TYPE_CHECKING:  # coordinator imports this module
    from .coordinator import HeatPumpOptimizerCoordinator


def commanded_power_kw(action: Any) -> float | None:
    """The current plan step's whole electrical ask, space plus DHW, in kW.

    ``action["power"]`` is the SPACE allocation alone, so publishing it as the
    step's power read 0 kW on a step heating only the tank (#1499). Every
    entity that publishes the step's commanded power -- Heat Pump Action's
    ``power_kw``, Recommended Power, the climate's ``recommended_power_kw``
    and Measured Power's ``recommended_power`` -- reads it here, so they
    cannot disagree. None when the action carries no power at all.

    Zero when the SAME action declares the pump off (``heat_pump_on`` is
    False): an ask the pump is not switched on for is not a draw, and four
    entities publishing 0.4 kW beside a state of "off" is the contradiction a
    user reads as a broken sensor (R9 D8-s1-03, #1644 P2). The gate is here
    rather than in the plan's on decision because the two are different facts:
    the plan decides what the pump must do (``planned_draw_runs``), this
    reports what the step asks of a pump it has already declared off. Only an
    explicit False gates -- an action that carries no ``heat_pump_on`` at all
    is a caller's partial dict, not a declaration, and publishes its ask.
    """
    action = action or {}
    space = action.get("power")
    if space is None:
        return None
    if action.get("heat_pump_on") is False:
        return 0.0
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


class HeatPumpOptimizerEntity(CoordinatorEntity["HeatPumpOptimizerCoordinator"]):
    """What every Heat Pump Optimizer entity has in common.

    Display names come from the translation files (``strings.json`` /
    ``translations/*.json``) via ``translation_key``, so the UI follows the
    Home Assistant language while ``unique_id`` — and therefore history and
    statistics — never moves.
    """

    _attr_has_entity_name = True

    #: The platform the pinned ``entity_id`` is registered under.
    _platform_domain: str = ""

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

    def _pin_identity(
        self,
        entry: Any,
        key: str,
        translation_key: str | None = None,
        object_id: str | None = None,
    ) -> None:
        """Pin the unique id, the translation key and today's object id.

        ``unique_id`` is what the registry, history and statistics key on, so
        ``key`` is the stable one and never follows a rename. A translation
        key left out is the class's own ``_attr_translation_key``.

        Assigning ``entity_id`` before the entity is added is Home Assistant's
        integration-suggested-object-id mechanism: it is used verbatim at first
        registration and ignored for entities that already exist. Without it,
        a Home Assistant running in a language with native entity ids (Swedish
        is one) would derive *translated* object ids from the translation-keyed
        name, breaking the dashboard card's id-suffix contract on fresh
        installs. The object id is ``heat_pump_optimizer_`` plus the
        translation key; ``object_id`` replaces it only for the climate entity,
        whose id predates the scheme.
        """
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        if translation_key is not None:
            self._attr_translation_key = translation_key
        if object_id is None:
            object_id = f"heat_pump_optimizer_{self._attr_translation_key}"
        self.entity_id = f"{self._platform_domain}.{object_id}"

    def _data(self) -> Payload:
        """The coordinator's published payload, empty before the first refresh."""
        return self.coordinator.data or Payload()


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

    The configured flag via ``thermal_params``, because the registry asks
    before the first refresh; the payload's copy where a test double has
    only that. The boost overlay asks here too (#1527), so a no-DHW install
    cannot be handed hot-water power by a switch it should never have used.
    """
    params = getattr(coordinator, "thermal_params", None)
    if params is not None:
        return bool(params.dhw_enabled)
    return bool((getattr(coordinator, "data", None) or {}).get("dhw_enabled"))


def input_configured(coordinator: Any, slot: str) -> bool:
    """Whether the user configured this input slot. Read from the config,
    because the registry asks before the first refresh builds a payload."""
    config = getattr(coordinator, "effective_config", None) or {}
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
