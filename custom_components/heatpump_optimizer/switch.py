"""Switch entities for Heat Pump Cost Optimizer.

Six switches, all plain toggles over coordinator state. Each reads the live
state rather than the published payload, and publishes it as soon as the
action has changed it, before the refresh that runs the solve (30 to 70 s on
a Pi): Home Assistant's toggle falls back to the old state after about two
seconds without a state change, so a switch turned off flipped back on in
front of the user (v6.6.12).

* "Optimizer Active" — the master on/off switch for the optimizer. When off,
  the heat pump is left in its default state; when on, the optimizer actively
  controls the heat pump.
* "Away" — the plan page's away override.
* "DHW Boost" and "Boost Space Heating" — two-hour maximum boosts of the hot
  water and the space heating, released when their window ends.
* "Block DHW" and "Block Space Heating" — the opposite, for the same two
  hours. A safety floor releases a block and the switch says why.
"""
from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from . import boost
from .const import MODE_AUTO, MODE_OFF
from .coordinator import HeatPumpOptimizerConfigEntry, HeatPumpOptimizerCoordinator
from .entity import DHWEntityMixin
from .entity import HeatPumpOptimizerEntity, publish_then_refresh

# Turning the optimizer on or off lands on the coordinator, which commands
# one heat pump; two toggles racing is two commands to one machine, so
# actions on this platform run one at a time (parallel-updates, Silver).
PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HeatPumpOptimizerConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Heat Pump Optimizer switch from a config entry."""
    coordinator = entry.runtime_data
    async_add_entities(
        [
            OptimizerEnableSwitch(coordinator, entry),
            AwaySwitch(coordinator, entry),
            BoostDhwSwitch(coordinator, entry),
            BoostSpaceSwitch(coordinator, entry),
            BlockDhwSwitch(coordinator, entry),
            BlockSpaceSwitch(coordinator, entry),
        ]
    )


class OptimizerEnableSwitch(HeatPumpOptimizerEntity, SwitchEntity):
    """Switch to enable/disable the optimizer."""

    _attr_translation_key = "optimizer_active"
    _platform_domain = "switch"
    def __init__(
        self,
        coordinator: HeatPumpOptimizerCoordinator,
        entry: HeatPumpOptimizerConfigEntry,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._pin_identity(entry, "optimizer_switch")

    @property
    def is_on(self) -> bool:
        """Return true if the optimizer is active."""
        return bool(self.coordinator.mode != MODE_OFF)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes.

        ``mode`` reads the live ``coordinator.mode``, the same source
        ``is_on`` above reads, not the published payload's copy: the payload
        only catches up once the refresh a mode change asks for has run its
        solve, so the switch's own state and its ``mode`` attribute used to
        disagree for that window (D8-s2-03).
        """
        if self.coordinator.data:
            return {
                "mode": self.coordinator.mode,
                "optimization_status": self.coordinator.data.get("optimization_status"),
            }
        return {}

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the optimizer.

        Only from *off*. Turning on a switch that is already on used to force
        `auto`, which silently threw away a live economy or comfort selection --
        easy to trigger from a dashboard toggle or a scene.
        """
        if self.coordinator.mode != MODE_OFF:
            self.async_write_ha_state()
            return
        await self.coordinator.async_set_mode(MODE_AUTO, refresh=False)
        publish_then_refresh(self)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the optimizer."""
        await self.coordinator.async_set_mode(MODE_OFF, refresh=False)
        publish_then_refresh(self)


class AwaySwitch(HeatPumpOptimizerEntity, SwitchEntity):
    """Plan-page away override on/off. ``is_on`` is the override, not resolve()."""

    _attr_translation_key = "away"
    _platform_domain = "switch"

    def __init__(
        self,
        coordinator: HeatPumpOptimizerCoordinator,
        entry: HeatPumpOptimizerConfigEntry,
    ) -> None:
        super().__init__(coordinator)
        self._pin_identity(entry, "away")

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.away_state.override_active)

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_away(active=True, refresh=False)
        publish_then_refresh(self)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_away(active=False, refresh=False)
        publish_then_refresh(self)


class TimedDutySwitch(HeatPumpOptimizerEntity, SwitchEntity):
    """A two-hour boost or block of one duty. The four switches share this.

    Subclasses set the channel, the polarity and the registry key. Hot-water
    switches also mix in ``DHWEntityMixin``. State stays in ``boost``'s weak
    map; the coordinator grows no attribute.
    """

    _platform_domain = "switch"
    _channel = ""
    _block = False
    _unique_key = ""

    def __init__(
        self,
        coordinator: HeatPumpOptimizerCoordinator,
        entry: HeatPumpOptimizerConfigEntry,
    ) -> None:
        super().__init__(coordinator)
        self._pin_identity(entry, self._unique_key)

    @property
    def is_on(self) -> bool:
        held = boost.held_for(self.coordinator)
        now = dt_util.now()
        if self._block:
            return held.block_active(self._channel, now)
        return held.active(self._channel, now)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        if not self._block:
            return None
        why = boost.block_release_reason(self.coordinator, self._channel)
        if why is None:
            return None
        return {"block_release": why}

    async def _press(self, active: bool) -> None:
        if self._block:
            await boost.set_block(
                self.coordinator, self._channel, active, refresh=False
            )
        else:
            await boost.set_channel(
                self.coordinator, self._channel, active, refresh=False
            )
        publish_then_refresh(self)

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._press(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._press(False)


class BoostDhwSwitch(DHWEntityMixin, TimedDutySwitch):
    """Two-hour maximum hot-water heat; gated like every hot-water entity (#1527).

    The unique id keeps the pre-#1334 key: an existing install's registry
    entry (and its history) is identified by this string, so the rename
    moves the suggested object id for NEW installs only, exactly as #1227
    and #1333 moved the sensors'.
    """

    _attr_translation_key = "dhw_boost"
    _channel = "dhw"
    _unique_key = "boost_dhw"


class BoostSpaceSwitch(TimedDutySwitch):
    """Two-hour maximum space heat."""

    _attr_translation_key = "boost_space"
    _channel = "space"
    _unique_key = "boost_space"


class BlockDhwSwitch(DHWEntityMixin, TimedDutySwitch):
    """Two-hour hot-water block; gated like every hot-water entity."""

    _attr_translation_key = "block_dhw"
    _channel = "dhw"
    _block = True
    _unique_key = "block_dhw"


class BlockSpaceSwitch(TimedDutySwitch):
    """Two-hour space-heat block."""

    _attr_translation_key = "block_space"
    _channel = "space"
    _block = True
    _unique_key = "block_space"
