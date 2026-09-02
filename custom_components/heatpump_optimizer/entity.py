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
        return self.coordinator.device_info
