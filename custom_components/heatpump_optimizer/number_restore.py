"""The off restore of the two numbers the cycle writes (ADR-004).

The compressor frequency (``freq_control.FrequencyWatchdog``) and the mixing
valve's target (``mixing_valve.ValveTarget``) are each restored to the
reading captured before the first write, on Off, on unload and on a stale
plan. A restore that lands empties its owner's record, so the first command
after it is sent whatever was last sent.

The owners are kept per config entry, as :mod:`off_restore` keys everything,
so the restore reaches them with no coordinator.
"""
from __future__ import annotations

from typing import Any
from weakref import WeakKeyDictionary

from homeassistant.core import HomeAssistant

from . import mixing_valve, off_restore
from .entry_config import EntryConfig
from .freq_control import FrequencyWatchdog
from .inputs import number_reading, read_setpoint, write_setpoint, write_setpoint_c

#: The off-restore keys of the two numbers.
FREQUENCY_RESTORE = "compressor_frequency"
VALVE_RESTORE = "mixing_valve_target"


def _register_number_restore(key: str, entity_of: Any, restored: Any, write: Any, reading: Any) -> None:
    """Register the entity ``entity_of(config)`` under ``key``; ``restored`` empties its owner's record."""
    def restorer(config: Any) -> off_restore.Restorer | None:
        entity_id = entity_of(EntryConfig.from_mapping(config))
        return off_restore.Restorer(
            str(entity_id), write, baseline_of=reading, restored=restored, write_unread=True) if entity_id else None

    off_restore.register_consumer(key, restorer, write, stale=True)


#: Config entry -> the two numbers' write owners, set by the entry's
#: coordinator (:func:`bind`).
_NUMBER_OWNERS: WeakKeyDictionary[Any, tuple[FrequencyWatchdog, mixing_valve.ValveTarget]] = WeakKeyDictionary()


def bind(entry: Any, frequency: FrequencyWatchdog, valve: mixing_valve.ValveTarget) -> None:
    """Hand the entry's two write owners to their restores."""
    _NUMBER_OWNERS[entry] = (frequency, valve)


def _frequency_restored(entry: Any, _entity_id: str, _value: float) -> None:
    if (owners := _NUMBER_OWNERS.get(entry)) is not None:
        owners[0].stand_easy()


def _valve_restored(entry: Any, _entity_id: str, _value: float) -> None:
    if (owners := _NUMBER_OWNERS.get(entry)) is not None:
        owners[1].handed_back()


def _number_reading(hass: HomeAssistant, entity_id: str) -> float | None:
    """The entity's state as a number in its own unit, or ``None`` (``inputs.number_reading``)."""
    value: float | None = getattr(number_reading(hass, entity_id), "value", None)
    return value


_register_number_restore(FREQUENCY_RESTORE, lambda c: c.compressor_freq_entity, _frequency_restored, write_setpoint, _number_reading)
_register_number_restore(VALVE_RESTORE, lambda c: c.mixing_valve_write_entity, _valve_restored, write_setpoint_c, read_setpoint)
