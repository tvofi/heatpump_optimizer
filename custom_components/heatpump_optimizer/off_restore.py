"""The one owner of the off and unload restore (R10-GENERIC-HEAT-CURVE).

Owner ruling (tvofi, #201, 2026-11-07): turning the optimizer off restores the
baseline. A consumer is a writer of one entity that owes that entity a value
when the optimizer lets go of it: on ``MODE_OFF``, on ``async_unload_entry``,
and once more for a write left armed by a crash, at the first of either after
the restart. This module is that seam's one owner; a consumer registers a
factory at import (:func:`register_consumer`) and calls :func:`async_arm`
before each write, and the coordinator and ``__init__`` call
:func:`async_restore` and :func:`async_forget`. Everything is keyed on the
config entry, never the coordinator, so a consumer needs no coordinator to
reach it and a restart's new coordinator finds the same persisted record. A second consumer -- the pump
arbiter's space set-point (R10-ARBITER-OFF-RESTORE) -- registers its own
factory and edits nothing here.

**Baseline.** A consumer with a fixed ``neutral`` (the heat curve's offset
kind: 0) is restored to it. One without is restored to the reading captured by
its first :func:`async_arm`, before its first write. The armed set and each
captured baseline are persisted per entry, so a restart never re-captures a
value the optimizer itself wrote: the baseline read before the first write
survives until the restore that spends it.

**Restore.** One write per armed consumer, bypassing the consumer's own write
policy (its latch, its rate guard), and counted. A failure is latched and
keeps the consumer armed, so the next off or unload tries again; it never
raises into the caller. Home Assistant stopping changes nothing: the target
integration may already be gone, which is a failure like any other.
"""
from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any
from weakref import WeakKeyDictionary

from homeassistant.core import HomeAssistant

from .const import DOMAIN, MODE_OFF
from .log_latch import log_held
from .store import QuarantiningStore, load_mapping

if TYPE_CHECKING:
    from .coordinator import HeatPumpOptimizerConfigEntry

_LOGGER = logging.getLogger(__name__)

OFF_RESTORE_STORE_VERSION = 1


@dataclass(frozen=True)
class Restorer:
    """What one consumer restores, built from the entry's config by its factory.

    ``write(hass, entity_id, value)`` sends ``value`` in the entity's own
    unit. ``neutral`` is the fixed restore value; ``None`` restores the
    baseline ``baseline_of(hass, entity_id)`` returned at the first arm.
    """

    entity_id: str
    write: Callable[[HomeAssistant, str, float], Awaitable[Any]]
    neutral: float | None = None
    baseline_of: Callable[[HomeAssistant, str], float | None] | None = None


Factory = Callable[[Any], "Restorer | None"]

#: Consumer key -> its factory. Filled at import by each consumer module.
_CONSUMERS: dict[str, Factory] = {}


def register_consumer(key: str, factory: Factory) -> None:
    """Make ``key`` restorable: ``factory(config)`` is its restorer, or None unconfigured."""
    _CONSUMERS[key] = factory


@dataclass
class _Held:
    """Per config entry: the persisted armed set, and the restores counted."""

    store: Any
    loaded: bool = False
    #: Consumer key -> captured baseline (None for a neutral consumer).
    armed: dict[str, float | None] = field(default_factory=dict)
    restores: int = 0
    last_restore: str | None = None


_RECORDS: WeakKeyDictionary[HeatPumpOptimizerConfigEntry, _Held] = WeakKeyDictionary()


def _store(hass: HomeAssistant, entry_id: str) -> QuarantiningStore[dict[str, Any]]:
    return QuarantiningStore(hass, OFF_RESTORE_STORE_VERSION, f"{DOMAIN}_{entry_id}_off_restore")


async def _armed_record(hass: HomeAssistant, entry: HeatPumpOptimizerConfigEntry) -> _Held:
    held = _RECORDS.get(entry)
    if held is None:
        held = _RECORDS[entry] = _Held(_store(hass, entry.entry_id))
    if not held.loaded:
        held.loaded = True
        raw = await load_mapping(held.store, "off-restore store") or {}
        armed = raw.get("armed")
        if isinstance(armed, Mapping):
            held.armed = {
                str(k): (float(v) if isinstance(v, (int, float)) else None)
                for k, v in armed.items()
            }
    return held


async def _save(held: _Held) -> None:
    try:
        await held.store.async_save({"armed": dict(held.armed)})
    except Exception as err:  # noqa: BLE001 - a store failure never blocks a write
        _LOGGER.debug("Could not save the off-restore store: %s", err)


async def async_arm(hass: HomeAssistant, entry: HeatPumpOptimizerConfigEntry, config: Any, key: str) -> bool:
    """Before a write by consumer ``key``: arm its restore; False refuses the write.

    The first arm captures the baseline of a consumer with no ``neutral`` and
    persists it; a later arm, in this run or after a restart, keeps it. An
    unreadable baseline refuses the write: what it would restore is unknown.
    """
    factory = _CONSUMERS.get(key)
    restorer = factory(config) if factory is not None else None
    if restorer is None:
        return False
    held = await _armed_record(hass, entry)
    if key in held.armed:
        return True
    baseline = None
    if restorer.neutral is None:
        baseline = restorer.baseline_of(hass, restorer.entity_id) if restorer.baseline_of else None
        if log_held(entry, f"off_restore_baseline_{key}", baseline is None,
                    "No baseline readable from %s: not written, nothing to restore it to",
                    restorer.entity_id):
            return False
    held.armed[key] = baseline
    await _save(held)
    return True


async def async_restore(hass: HomeAssistant, entry: HeatPumpOptimizerConfigEntry, config: Any, reason: str) -> int:
    """Restore every armed consumer; the number of restore writes sent.

    Called on the transition into ``MODE_OFF`` and from ``async_unload_entry``.
    A consumer no longer configured is disarmed unwritten: its entity is no
    longer the optimizer's to write.
    """
    held = await _armed_record(hass, entry)
    sent = 0
    for key, baseline in list(held.armed.items()):
        factory = _CONSUMERS.get(key)
        restorer = factory(config) if factory is not None else None
        value = None if restorer is None else (
            restorer.neutral if restorer.neutral is not None else baseline)
        if restorer is None or value is None:
            held.armed.pop(key)
            continue
        try:
            await restorer.write(hass, restorer.entity_id, value)
        except Exception as err:  # noqa: BLE001 - a restore never raises into off or unload
            log_held(entry, f"off_restore_{key}", True,
                     "Restore of %s to %s on %s failed: %s", restorer.entity_id, value, reason, err)
            continue
        log_held(entry, f"off_restore_{key}", False)
        held.armed.pop(key)
        sent += 1
        _LOGGER.info("Restored %s to %s (%s)", restorer.entity_id, value, reason)
    held.restores += sent
    held.last_restore = reason if sent else held.last_restore
    await _save(held)
    return sent


async def async_mode_change(
    hass: HomeAssistant, entry: HeatPumpOptimizerConfigEntry, config: Any, old: str, new: str
) -> int:
    """The off rule's mode half (tvofi, 2026-11-07): entering ``MODE_OFF`` restores.

    Called by ``async_set_mode`` before the mode is set; staying off, or any
    other change, writes nothing.
    """
    if new != MODE_OFF or old == MODE_OFF:
        return 0
    return await async_restore(hass, entry, config, "mode_off")


async def async_forget(hass: HomeAssistant, entry_id: str) -> None:
    """``async_remove_entry``: drop the entry's persisted armed set.

    The unload before it restored what it could; nothing is written here, so
    the restore keeps one owner (the design note's O4).
    """
    try:
        await _store(hass, entry_id).async_remove()
    except Exception as err:  # noqa: BLE001
        _LOGGER.debug("Could not remove the off-restore store: %s", err)


def diagnostics(entry: HeatPumpOptimizerConfigEntry) -> dict[str, Any]:
    """The armed consumers and the restores counted for ``entry``."""
    held = _RECORDS.get(entry)
    if held is None:
        return {"armed": [], "restores": 0, "last_restore": None}
    return {"armed": sorted(held.armed), "restores": held.restores,
            "last_restore": held.last_restore}
