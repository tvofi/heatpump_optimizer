"""The store-load boundary: a ``Store`` whose loads cannot hand back a non-finite number.

Learned/live state is reconstituted by ~11 independent ``Store`` reads feeding
~18 hand-written loader seams, each over a ``float()`` coercion guarded by
``(TypeError, ValueError, OverflowError)``. That guard is blind to non-finite by
construction of the Python float type: ``float('nan')`` raises nothing, and
``np.clip`` propagates NaN onto the live model while *clamping* +-inf rather
than refusing it. So finiteness was enforced **per demonstrated field** — a
guard sat on the seam a harness happened to show, while its sibling in the same
store dict stayed open. The fifth seam of #1296/#1345 (``apply_cooling_rate``,
70 lines below the guarded ``normalize_profile`` in the same file) and its
sibling (``DefrostDerate.from_dict``'s ``duty`` grid) are the round-6 instances.

This module closes the class by construction instead of one more guard: every
store is a ``QuarantiningStore``, whose ``async_load`` scrubs poisoned numeric
leaves (non-finite, or of a magnitude no writer produces) to ``None`` — the
loaders' own absent-data default — so a poisoned leaf is quarantined at the
one persistence boundary and no per-seam guard can be forgotten, because no
seam decides finiteness or magnitude any more.

The rule that a store must be this type is enforced, not remembered: the
standing sweep ``tests/finite_boundary.py`` derives the boundary set from the
tree (every ``QuarantiningStore(...)`` construction, and zero raw ``Store(...)``
constructions outside it) and drives a non-finite leaf through each boundary.
"""
from __future__ import annotations

import asyncio
import logging
import math
from collections.abc import Mapping, Sequence
from datetime import datetime, timedelta, timezone, tzinfo
from typing import Any, TypeVar, cast

from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

_LOGGER = logging.getLogger(__name__)

#: Home Assistant's ``Store`` bounds its payload to a JSON-shaped container
#: (a mapping or a sequence). The boundary never widens that; it scrubs leaves.
_StorePayload = TypeVar("_StorePayload", bound=Mapping[str, Any] | Sequence[Any])


#: No writer stores a number this large (an epoch in ms is 1.8e12), so one that
#: is -- ``2**64``, ``1e300``, a key of that size -- is a corrupt leaf, and is
#: quarantined here exactly as a non-finite one is (round-9 class P1).
ABSURD = 1e15


def _poisoned(value: Any) -> bool:
    """A leaf no writer produces: non-finite, or of magnitude ``ABSURD`` or more.

    A ``str`` counts by what ``float()`` makes of it (``"NaN"``, ``"Infinity"``,
    ``"1e300"`` …): those are the spellings a loader's coercion turns into a
    poisoned number without raising, which its ``(TypeError, ValueError)``
    guard cannot see. ``bool`` is an ``int`` to Python and never poisoned.
    """
    if isinstance(value, bool):
        return False
    if isinstance(value, str):
        try:
            value = float(value)
        except (TypeError, ValueError, OverflowError):
            return False
    if isinstance(value, int):
        return abs(value) >= ABSURD
    if isinstance(value, float):
        return not math.isfinite(value) or abs(value) >= ABSURD
    return False


def _sanitize(value: Any) -> Any:
    """Recursively scrub poisoned numeric leaves (``_poisoned``) to ``None``.

    A dict entry whose key is poisoned is dropped. Anything else -- a finite
    number below ``ABSURD``, a non-numeric string the loader will refuse on its
    own -- passes through untouched, so the boundary never rewrites a healthy
    payload.
    """
    if isinstance(value, dict):
        return {k: _sanitize(v) for k, v in value.items() if not _poisoned(k)}
    if isinstance(value, list):
        return [_sanitize(child) for child in value]
    if isinstance(value, tuple):
        return tuple(_sanitize(child) for child in value)
    return None if _poisoned(value) else value


def _bound_instants(
    value: Any, bound: datetime, where: str, naive_zone: tzinfo | None = timezone.utc
) -> Any:
    """Bound every stored instant to ``bound``: none may lie beyond it.

    A stored instant was stamped by the clock that ran when it was written. A
    clock that ran ahead then (no RTC, NTP not yet synced) leaves a stamp the
    corrected clock has not reached, and every ``now - stamp`` window the
    stamp opens then holds for the clock's whole error -- a cooldown, a grace
    period, a disinfection timer, one sibling at a time (round 9). Bounded
    here, once, so no loader and no later parse of the string decides it.
    A leaf is an instant when it is a date *and* a time; a date-only day key
    is not one. A naive leaf is read in ``naive_zone``, the zone its loader
    reads it in, and bounded as a naive wall time there (``None``: the naive
    clock's own wall time). Only a leaf beyond the bound is rewritten, so a
    healthy payload comes back unchanged.
    """
    if isinstance(value, str) and len(value) >= 16 and value[10:11] in ("T", " "):
        try:
            when = datetime.fromisoformat(value)
        except ValueError:
            return value
        naive = when.tzinfo is None
        when = when.replace(tzinfo=naive_zone or bound.tzinfo) if naive else when
        if when <= bound:
            return value
        clamped = bound.astimezone(when.tzinfo)
        clamped = clamped.replace(tzinfo=None) if naive else clamped
        _LOGGER.warning(
            "%s: stored instant %s is ahead of the clock; bounded to %s",
            where, value, clamped,
        )
        return clamped.isoformat()
    if isinstance(value, dict):
        return {k: _bound_instants(v, bound, where, naive_zone) for k, v in value.items()}
    if isinstance(value, list):
        return [_bound_instants(child, bound, where, naive_zone) for child in value]
    return value


class QuarantiningStore(Store[_StorePayload]):
    """A ``Store`` whose ``async_load`` scrubs poisoned numeric leaves.

    The finiteness and magnitude properties live here, at the single
    persistence boundary, instead of at each loader seam. A corrupted store
    reaches a loader already sanitized, so a poisoned leaf becomes that
    loader's own absent-data default and nothing poisoned is reachable from
    the live model — whatever store, field or class the poison arrived in.
    """

    #: The read in flight, kept until the next one.
    _reading: asyncio.Future[None] | None = None

    def __init__(
        self,
        *args: Any,
        lead: timedelta | None = timedelta(0),
        naive_zone: tzinfo | None = timezone.utc,
        **kwargs: Any,
    ) -> None:
        """``lead``: how far ahead of the clock a stored instant may lie.

        Zero for a store of things that happened; the longest legitimate lead
        for one holding expiries (a boost's maximum); ``None`` only for a
        store of user-set instants no system bound governs. ``naive_zone``:
        the zone the store's loader reads a naive instant in, the one it
        passes ``drift.stored_instant`` -- Home Assistant's where the loader
        reads it so, or the bound is off by the zone's offset either way.
        """
        super().__init__(*args, **kwargs)
        self._lead = lead
        self._naive_zone = naive_zone

    async def async_load(self) -> _StorePayload | None:
        self._reading = reading = asyncio.get_running_loop().create_future()
        try:
            data = _sanitize(await super().async_load())
            if self._lead is not None:
                bound = dt_util.as_utc(dt_util.now()) + self._lead
                where = str(getattr(self, "key", None) or getattr(self, "_key", "store"))
                data = _bound_instants(data, bound, where, self._naive_zone)
            return cast(_StorePayload | None, data)
        finally:
            reading.set_result(None)

    async def async_save(self, data: Any) -> None:
        """Save, once this store's read in flight, if any, has landed.

        A save of a whole payload built from memory that runs before the
        startup read lands replaces the persisted state with the fresh
        defaults that read is about to install (round 9, D1-s2-52: five
        coordinator writers lost persisted learned state this way; R6's
        mode setter hit it before them). Waiting here, in the store itself,
        is the property rather than a per-writer discipline: no save this
        type can express clobbers its own pending read.
        """
        await self.async_wait_for_read()
        await super().async_save(data)

    async def async_wait_for_read(self) -> None:
        """Return once the read in flight, if any, has landed.

        A writer that saves its whole payload from memory waits here first: a
        write before a startup read lands replaces the stored state with the
        fresh defaults that read is about to overwrite (R6, round 9: a mode set
        during startup zeroed the comfort learner). Shielded, so a cancelled
        writer does not cancel the future another writer awaits.
        """
        if self._reading is not None:
            await asyncio.shield(self._reading)
