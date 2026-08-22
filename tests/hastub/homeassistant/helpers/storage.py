"""Honest in-memory stand-in for ``homeassistant.helpers.storage.Store``.

The real Store persists a JSON document per storage key and hands the same data
back on a later ``async_load``. Tests here need that round-trip to be real —
otherwise a persistence bug (an override that should survive a restart, or an
expired one that should be discarded) would pass against a no-op stub.

Two rules are enforced deliberately, because a lenient stub hides real bugs:

* Data is keyed by the Store's storage key and shared across Store instances
  with the same key, so a *new* Store (a simulated restart) loads what an
  earlier one saved.
* Everything saved is round-tripped through ``json`` immediately, so a value
  the real Store could not serialise raises here too instead of silently
  working only in tests.
"""
from __future__ import annotations

import json
from typing import Any

# Class-level so a fresh Store instance with the same key — the way a restart is
# simulated in tests — sees what a previous instance persisted.
_DISK: dict[str, str] = {}


class Store:
    def __init__(self, hass: Any = None, version: int = 1, key: str = "", **kwargs: Any) -> None:
        self._key = key

    async def async_load(self) -> Any:
        if self._key not in _DISK:
            return None
        # Return a fresh copy so a caller mutating the loaded dict cannot reach
        # back into the "disk", exactly as the real (re-serialised) Store does.
        return json.loads(_DISK[self._key])

    async def async_save(self, data: Any) -> None:
        # Serialise eagerly so a non-serialisable payload fails now, matching the
        # real Store, rather than at some later flush the test never sees.
        _DISK[self._key] = json.dumps(data)

    async def async_remove(self) -> None:
        _DISK.pop(self._key, None)


def _reset_store_disk() -> None:
    """Test helper: clear all simulated persistence between cases."""
    _DISK.clear()
