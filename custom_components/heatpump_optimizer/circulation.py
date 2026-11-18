"""The circulation pumps' one owner: the write, the record of it, the restore (ADR-004).

The hot-water circulation pump follows the user's hot-water windows and the
space circulation pump the plan (``pump_schedule`` decides both; the
coordinator hands the decision here). Each is commanded once per state
change, and an off write arms :mod:`off_restore` first, so the pump is
switched back on when the optimizer lets go: on Off, on unload, and for the
space pump, whose command is cut from the plan, on a stale plan too. A
restore that lands empties the record, so the first command after it is sent
whatever was last sent.

The record is kept per config entry, as :mod:`off_restore` keys everything,
so the restore reaches it with no coordinator.
"""
from __future__ import annotations

import logging
from typing import Any
from weakref import WeakKeyDictionary

from homeassistant.core import HomeAssistant

from . import off_restore
from .entry_config import EntryConfig

_LOGGER = logging.getLogger(__name__)

#: The off-restore keys, which are also the pumps' names here.
SPACE = "circulation_space"
DHW = "circulation_dhw"
_ENTITY_OF = {SPACE: lambda c: c.space_circulation_pump_entity, DHW: lambda c: c.vvc_pump_entity}

#: Config entry -> entity -> the state last commanded; a failed command is not recorded.
_COMMANDED: WeakKeyDictionary[Any, dict[str, bool]] = WeakKeyDictionary()


def commanded(entry: Any) -> dict[str, bool]:
    """The entry's record: what each pump was last told, empty before any command."""
    return _COMMANDED.setdefault(entry, {})


async def _send(hass: HomeAssistant, entity_id: str, on: float) -> None:
    await hass.services.async_call(
        "homeassistant", "turn_on" if on else "turn_off", {"entity_id": entity_id}
    )


async def command(hass: HomeAssistant, entry: Any, config: Any, pump: str, on: bool, reason: str) -> None:
    """Switch ``pump`` (:data:`SPACE` or :data:`DHW`) where ``on`` is a change; never raises.

    Recorded only after the call succeeded: a command that failed (entity
    briefly unavailable) is sent again on the next cycle, not remembered as
    done. An off write the restore cannot be armed for is not sent.
    """
    entity_id = _ENTITY_OF[pump](EntryConfig.from_mapping(config))
    record = commanded(entry)
    if not entity_id or record.get(entity_id) == on:
        return
    try:
        if not on and not await off_restore.async_arm(hass, entry, config, pump):
            return
        await _send(hass, entity_id, on)
    except Exception as err:  # noqa: BLE001 - a pump must never kill the cycle
        _LOGGER.warning("Could not command pump %s: %s", entity_id, err)
        return
    _LOGGER.info("Pump %s → %s: %s", entity_id, "turn_on" if on else "turn_off", reason)
    record[entity_id] = on


def _restored(entry: Any, entity_id: str, _value: float) -> None:
    """The restore switched the pump on: the record of it goes."""
    commanded(entry).pop(entity_id, None)


def _register(pump: str, stale: bool) -> None:
    def restorer(config: Any) -> off_restore.Restorer | None:
        entity_id = _ENTITY_OF[pump](EntryConfig.from_mapping(config))
        return off_restore.Restorer(str(entity_id), _send, neutral=1.0, restored=_restored) if entity_id else None

    off_restore.register_consumer(pump, restorer, stale=stale)


_register(SPACE, stale=True)
_register(DHW, stale=False)
