"""The room-separability sensor, split from sensor.py (scratch payment probe)."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorStateClass

from . import room_history, room_record
from .sensor import HeatPumpOptimizerSensorBase, HeatPumpOptimizerCoordinator, HeatPumpOptimizerConfigEntry


class RoomSeparabilitySensor(HeatPumpOptimizerSensorBase):
    """How many rooms the room history can model apart (#3616, phase 3a).

    The state counts the rooms whose verdict is ``separable``; the attributes
    carry each room's verdict and the house line (``room_history.identifiability_report``).
    Unknown until the history is loaded on the first cycle.
    """

    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: HeatPumpOptimizerCoordinator, entry: HeatPumpOptimizerConfigEntry) -> None:
        super().__init__(coordinator, entry, "room_separability", "room_separability")

    @property
    def native_value(self) -> int | None:
        return room_history.separable_count(room_record.report_of(self.coordinator))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        view = room_record.report_of(self.coordinator) or {}
        return {"rooms": view.get("rooms"), "house": view.get("house"), "rows": view.get("rows")}
