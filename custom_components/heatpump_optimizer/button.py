"""Button entities for Heat Pump Cost Optimizer.

Four momentary actions with no lasting state, which is exactly what a
``ButtonEntity`` is for. A switch would have to bounce itself back off, and
until it did, the UI would imply a state that does not exist:

* "Optimize Now" — run an optimization without waiting for the next interval,
* "Learning Run System Identification" — arm the commissioning step test,
* "Learning Reset Comfort Weight" — undo the revealed-preference comfort
  tuning,
* "Prediction Accuracy Diagnose Last Interval" — attribute the last
  interval's temperature residual.

The runs take real time — an optimization fetches prices and weather and then
solves — so they report ``available`` as False while busy, giving the user
feedback that the press landed rather than inviting a second one.
"""
from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import HeatPumpOptimizerConfigEntry, HeatPumpOptimizerCoordinator
from .entity import HeatPumpOptimizerEntity, off_the_action

_LOGGER = logging.getLogger(__name__)

# The coordinator is the serialization point, not this semaphore: the solve
# guards itself on ``_optimization_running`` and every other press's setter
# is a single write. The optimize-now press must await its solve to answer
# the tap (#1644, D10-s1-02), and under a held slot that wait queues the
# other buttons' presses behind it -- the v6.6.12 bug-5 shape, where a
# restart cancelled a queued reset before its setter ran. Declared 0
# (parallel-updates, Silver): no press ever queues behind another.
PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HeatPumpOptimizerConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Heat Pump Optimizer buttons from a config entry."""
    coordinator = entry.runtime_data
    async_add_entities(
        [
            ForceOptimizationButton(coordinator, entry),
            SystemIdentificationButton(coordinator, entry),
            ResetComfortWeightButton(coordinator, entry),
            DiagnoseIntervalButton(coordinator, entry),
        ]
    )


class _OptimizerButtonBase(HeatPumpOptimizerEntity, ButtonEntity):
    """Shared plumbing so the buttons land on the existing device."""

    def __init__(
        self,
        coordinator: HeatPumpOptimizerCoordinator,
        entry: HeatPumpOptimizerConfigEntry,
        key: str,
        translation_key: str,
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._key = key
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_translation_key = translation_key
        # Pin today's English object id for new installs (the integration
        # suggested-object-id mechanism); see the sensor base class.
        self.entity_id = f"button.heat_pump_optimizer_{translation_key}"


class ForceOptimizationButton(_OptimizerButtonBase):
    """Run the optimization now, without waiting for the next interval."""

    def __init__(
        self, coordinator: HeatPumpOptimizerCoordinator, entry: HeatPumpOptimizerConfigEntry
    ) -> None:
        super().__init__(coordinator, entry, "force_optimization", "optimize_now")

    @property
    def available(self) -> bool:
        """Unavailable while a run is in flight, so repeated taps do nothing."""
        return bool(super().available and not self.coordinator.optimization_running)

    async def async_press(self) -> None:
        """Force an optimization run, raising when it did not run.

        The press answers a tap with the same refusal the
        ``run_optimization`` action raises (#1644, D10-s1-02): reporting
        success behind a dead price feed is the silent failure the action
        was fixed out of (#294). The solve is awaited here -- the platform
        takes no parallel-updates slot, so nothing queues behind it -- and
        the fetch-and-actuate cycle still runs off the press, as before
        (#1641).
        """
        _LOGGER.info("Optimization run requested from the dashboard")
        reason = await self.coordinator.async_run_optimization()
        off_the_action(self, self.coordinator.async_request_refresh())
        if reason == "no_prices":
            # The action's own wording, on the action's own translation
            # keys: services.py owns them and this is its sibling surface.
            raise HomeAssistantError(
                f"The optimization did not run for {self._entry.entry_id}: "
                "fewer than four electricity price steps were available",
                translation_domain=DOMAIN,
                translation_key="run_optimization_no_prices",
                translation_placeholders={"entry_ids": self._entry.entry_id},
            )
        if reason is not None:
            raise HomeAssistantError(
                f"The optimization did not run for {self._entry.entry_id}: "
                "the solve failed; the error is in the integration's log",
                translation_domain=DOMAIN,
                translation_key="run_optimization_solve_failed",
                translation_placeholders={"entry_ids": self._entry.entry_id},
            )


class SystemIdentificationButton(_OptimizerButtonBase):
    """Arm the commissioning step test (item 18).

    Pressing does not start an experiment immediately: it arms one, and the
    coordinator runs it at the next moment the gating conditions hold (mild
    weather, cheap electricity, night). Running it on demand regardless of
    conditions would be both expensive and uncomfortable.
    """

    _attr_entity_category = None

    def __init__(
        self, coordinator: HeatPumpOptimizerCoordinator, entry: HeatPumpOptimizerConfigEntry
    ) -> None:
        super().__init__(
            coordinator, entry, "system_identification", "learning_run_system_identification"
        )

    @property
    def available(self) -> bool:
        return bool(
            super().available and not self.coordinator.system_identification_active
        )

    async def async_press(self) -> None:
        off_the_action(self, self.coordinator.async_arm_system_identification())


class ResetComfortWeightButton(_OptimizerButtonBase):
    """Undo the revealed-preference comfort tuning (item 19).

    A self-adjusting objective the user cannot reset would be alarming, so the
    learned value is always both visible and revertible.
    """

    def __init__(
        self, coordinator: HeatPumpOptimizerCoordinator, entry: HeatPumpOptimizerConfigEntry
    ) -> None:
        super().__init__(
            coordinator, entry, "reset_comfort_weight", "learning_reset_comfort_weight"
        )

    async def async_press(self) -> None:
        await self.coordinator.async_reset_comfort_weight()
        off_the_action(self, self.coordinator.async_request_refresh())


class DiagnoseIntervalButton(_OptimizerButtonBase):
    """Attribute the last interval's temperature residual (T6 #52).

    One press, one attribution: the coordinator re-runs the interval that
    just settled, swapping realised inputs into the plan's assumptions one
    at a time, and publishes what each swap explains on the Prediction
    Accuracy sensor. A button rather than an automatic per-interval run,
    because the answer is for a person mid-investigation — computed
    unasked it would be noise, and noise about the model's errors is the
    fastest way to teach people to ignore them.
    """

    _attr_entity_category = None

    def __init__(
        self, coordinator: HeatPumpOptimizerCoordinator, entry: HeatPumpOptimizerConfigEntry
    ) -> None:
        super().__init__(
            coordinator, entry, "diagnose_interval", "diagnose_last_interval"
        )

    async def async_press(self) -> None:
        off_the_action(self, self.coordinator.async_diagnose_interval())
