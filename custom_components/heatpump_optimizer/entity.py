"""The shared entity base for Heat Pump Cost Optimizer (common-modules, Bronze).

Each platform file used to declare its own ``CoordinatorEntity`` base class,
and the five of them re-declared the same two members -- the
``_attr_has_entity_name`` flag and the ``device_info`` property that lands
every entity on the coordinator's device. Those live here once now (issue
#298); each platform's base classes build on ``HeatPumpOptimizerEntity``
instead of re-declaring them. Everything that differs per platform (the
unique-id key, the pinned ``entity_id``, the translation key) stays in the
platform file that owns it.
"""
from __future__ import annotations

from typing import Any

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity


class HeatPumpOptimizerEntity(CoordinatorEntity):
    """What every Heat Pump Optimizer entity has in common.

    Display names come from the translation files (``strings.json`` /
    ``translations/*.json``) via ``translation_key``, so the UI follows the
    Home Assistant language while ``unique_id`` — and therefore history and
    statistics — never moves.
    """

    _attr_has_entity_name = True

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        info: DeviceInfo = self.coordinator.device_info
        return info


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
        config = getattr(self.coordinator, "_config", None) or {}
        return bool(config.get(self._dhw_probe_slot))

    @property
    def available(self) -> bool:
        return bool(
            super().available
            and self.coordinator.data
            and has_hot_water(self.coordinator)
        )
