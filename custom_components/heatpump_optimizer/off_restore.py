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
kind: 0) is restored to it, on the entity its current config names; its armed
entry is ``None``. One without (``neutral=None``: the heat curve's persistent
kind) is restored to the reading captured by its first :func:`async_arm`,
before its first write, and its armed entry records that entity beside the
value: ``{"entity_id", "value"}``. The armed set is persisted per entry, so a
restart never re-captures a value the optimizer itself wrote: the baseline
read before the first write survives until the restore that spends it.

**Rule R** (design/R10-GENERIC-HEAT-CURVE-PERSISTENT, C1). A baseline entry is
restored by its own record -- its value to its entity -- whatever the config
now names, so a baseline never lands on an entity it was not read from, and a
key is armed on one entity at a time: an arm naming another entity, or a
neutral kind, first restores the recorded one. A consumer whose config is
cleared is restored through the writer it registered.
:func:`async_rebaseline` is the one way a captured baseline moves (a user's
edit adopted), and each consumer may keep a small persisted mapping of its own
in the same record (:func:`async_consumer_state`), which a restore leaves alone.

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
    ``restored(entry, entity_id, value)``, when given, is told each restore
    write that succeeded, so the consumer's own write record names what the
    entity was last told; the restore never edits that record itself.
    """

    entity_id: str
    write: Callable[[HomeAssistant, str, float], Awaitable[Any]]
    neutral: float | None = None
    baseline_of: Callable[[HomeAssistant, str], float | None] | None = None
    restored: Callable[[Any, str, float], None] | None = None


Factory = Callable[[Any], "Restorer | None"]
Writer = Callable[[HomeAssistant, str, float], Awaitable[Any]]

#: Consumer key -> its factory. Filled at import by each consumer module.
_CONSUMERS: dict[str, Factory] = {}
#: Consumer key -> the write that restores a baseline entry once its factory
#: answers None (rule R: the entity was cleared from the config).
_WRITERS: dict[str, Writer] = {}


def register_consumer(key: str, factory: Factory, write: Writer | None = None) -> None:
    """Make ``key`` restorable: ``factory(config)`` is its restorer, or None unconfigured."""
    _CONSUMERS[key] = factory
    if write is not None:
        _WRITERS[key] = write


@dataclass
class _Held:
    """Per config entry: the persisted armed set, and the restores counted."""

    store: Any
    loaded: bool = False
    #: Consumer key -> None for a neutral consumer, else its baseline entry
    #: ``{"entity_id": str, "value": float}``.
    armed: dict[str, Any] = field(default_factory=dict)
    #: Consumer key -> that consumer's own persisted mapping (C3), saved as ``state``.
    consumers: dict[str, dict[str, Any]] = field(default_factory=dict)
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
            held.armed = {str(k): _entry_of(v) for k, v in armed.items()}
        state = raw.get("state")
        if isinstance(state, Mapping):
            held.consumers = {str(k): dict(v) for k, v in state.items() if isinstance(v, Mapping)}
    return held


def _entry_of(raw: Any) -> Any:
    """One stored armed entry: a baseline mapping, a bare number, or None."""
    if isinstance(raw, Mapping):
        entity_id, value = raw.get("entity_id"), raw.get("value")
        if isinstance(entity_id, str) and isinstance(value, (int, float)):
            return {"entity_id": entity_id, "value": float(value)}
    return float(raw) if isinstance(raw, (int, float)) else None


async def _save(held: _Held) -> None:
    data: dict[str, Any] = {"armed": dict(held.armed)}
    if held.consumers:  # a neutral consumer's record keeps #3299's one key (I4)
        data["state"] = held.consumers
    try:
        await held.store.async_save(data)
    except Exception as err:  # noqa: BLE001 - a store failure never blocks a write
        _LOGGER.debug("Could not save the off-restore store: %s", err)


async def async_arm(hass: HomeAssistant, entry: HeatPumpOptimizerConfigEntry, config: Any, key: str) -> bool:
    """Before a write by consumer ``key``: arm its restore; False refuses the write.

    The first arm captures the baseline of a consumer with no ``neutral`` and
    persists it with its entity; a later arm, in this run or after a restart,
    keeps it. An unreadable baseline refuses the write: what it would restore
    is unknown. A baseline entry for another entity, or under a neutral
    restorer, is restored first (rule R), and a failure refuses the write; a
    neutral entry under a baseline restorer is dropped unwritten, so a neutral
    is never written to a target that has none.
    """
    factory = _CONSUMERS.get(key)
    restorer = factory(config) if factory is not None else None
    if restorer is None:
        return False
    held = await _armed_record(hass, entry)
    if key in held.armed:
        current = held.armed[key]
        if not isinstance(current, dict):
            if current is not None or restorer.neutral is not None:
                return True  # #3299's entry, unchanged
            # A neutral entry under a baseline restorer: replaced below, never written.
        elif restorer.neutral is None and current["entity_id"] == restorer.entity_id:
            return True
        elif not await _restore_baseline(hass, entry, held, key, restorer, "rearm"):
            return False  # latched, still armed: nothing to save
    baseline = None
    if restorer.neutral is None:
        baseline = restorer.baseline_of(hass, restorer.entity_id) if restorer.baseline_of else None
        if log_held(entry, f"off_restore_baseline_{key}", baseline is None,
                    "No baseline readable from %s: not written, nothing to restore it to",
                    restorer.entity_id):
            return False
    held.armed[key] = None if baseline is None else {"entity_id": restorer.entity_id, "value": baseline}
    await _save(held)
    return True


async def _restore_baseline(
    hass: HomeAssistant, entry: HeatPumpOptimizerConfigEntry, held: _Held, key: str,
    restorer: Restorer | None, reason: str,
) -> bool:
    """Rule R: write a baseline entry's value to its own entity; True when sent.

    The writer is the current restorer's, else the one registered for the key.
    A write that raises or answers False is a failure, latched and still armed.
    """
    entity_id, value = held.armed[key]["entity_id"], held.armed[key]["value"]
    write = restorer.write if restorer is not None else _WRITERS.get(key)
    if write is None:
        _LOGGER.warning("No writer left for %s: %s keeps the optimizer's value; set it to %s by hand",
                        key, entity_id, value)
        held.armed.pop(key)
        return False
    try:
        sent = await write(hass, entity_id, value) is not False
        err: Any = "the entity takes no set-point write"
    except Exception as exc:  # noqa: BLE001 - a restore never raises into off or unload
        sent, err = False, exc
    if log_held(entry, f"off_restore_{key}", not sent,
                "Restore of %s to %s on %s failed: %s", entity_id, value, reason, err):
        return False
    if restorer is not None and restorer.restored is not None:
        restorer.restored(entry, entity_id, value)
    held.armed.pop(key)
    _LOGGER.info("Restored %s to %s (%s)", entity_id, value, reason)
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
        if isinstance(baseline, dict):
            sent += await _restore_baseline(hass, entry, held, key, restorer, reason)
            continue
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
        if restorer.restored is not None:
            restorer.restored(entry, restorer.entity_id, value)
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


async def async_armed_entry(hass: HomeAssistant, entry: HeatPumpOptimizerConfigEntry, key: str) -> dict[str, Any] | None:
    """The key's baseline entry ``{"entity_id", "value"}``, or None when it has none."""
    current = (await _armed_record(hass, entry)).armed.get(key)
    return dict(current) if isinstance(current, dict) else None


async def async_rebaseline(
    hass: HomeAssistant, entry: HeatPumpOptimizerConfigEntry, key: str, entity_id: str, value: float
) -> bool:
    """C2: move the key's baseline to ``value`` while it is armed on ``entity_id``.

    The only way a captured baseline moves (a user's edit, adopted); False,
    and nothing saved, when the key is not armed on that entity.
    """
    held = await _armed_record(hass, entry)
    current = held.armed.get(key)
    if not isinstance(current, dict) or current["entity_id"] != entity_id:
        return False
    held.armed[key] = {"entity_id": entity_id, "value": float(value)}
    await _save(held)
    return True


async def async_consumer_state(hass: HomeAssistant, entry: HeatPumpOptimizerConfigEntry, key: str) -> dict[str, Any]:
    """C3: the consumer's own persisted mapping, mutable; a restore leaves it.

    Saved by :func:`async_save_state`, and by the restore that follows a
    ``restored`` callback; never read here.
    """
    await _armed_record(hass, entry)
    return consumer_state(entry, key)


def consumer_state(entry: HeatPumpOptimizerConfigEntry, key: str) -> dict[str, Any]:
    """C3 for a caller inside a restore (``restored``), whose record is loaded; else empty."""
    held = _RECORDS.get(entry)
    return {} if held is None else held.consumers.setdefault(key, {})


async def async_save_state(hass: HomeAssistant, entry: HeatPumpOptimizerConfigEntry) -> None:
    """C3: persist the record, consumer state included."""
    await _save(await _armed_record(hass, entry))


async def async_forget(hass: HomeAssistant, entry_id: str) -> None:
    """``async_remove_entry``: drop the entry's persisted record.

    The unload before it restored what it could; nothing is written here, so
    the restore keeps one owner (the design note's O4). A baseline entry still
    armed -- its unload restore failed -- is named once, with the value to set
    by hand (C4).
    """
    store = _store(hass, entry_id)
    raw = await load_mapping(store, "off-restore store") or {}
    armed = raw.get("armed")
    for key, current in (armed.items() if isinstance(armed, Mapping) else ()):
        current = _entry_of(current)
        if isinstance(current, dict):
            _LOGGER.warning("Removed with %s still displaced by %s: set it to %s by hand",
                            current["entity_id"], key, current["value"])
    try:
        await store.async_remove()
    except Exception as err:  # noqa: BLE001
        _LOGGER.debug("Could not remove the off-restore store: %s", err)


def diagnostics(entry: HeatPumpOptimizerConfigEntry) -> dict[str, Any]:
    """The armed consumers and the restores counted for ``entry``."""
    held = _RECORDS.get(entry)
    if held is None:
        return {"armed": [], "restores": 0, "last_restore": None}
    return {"armed": sorted(held.armed), "restores": held.restores,
            "last_restore": held.last_restore}
