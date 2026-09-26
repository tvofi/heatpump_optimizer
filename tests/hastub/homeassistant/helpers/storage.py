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

A load decodes the way upstream's does, with ``orjson.loads`` semantics for
numbers: a bare ``NaN``/``Infinity`` token or a number that overflows a double
is a decode error, and an integer outside orjson's i64/u64 range is a float.
A document that fails to decode is moved aside and loads as ``None``, as
upstream's ``_async_load_data`` renames a corrupt file and returns ``None``
(round-9 D1-s1-51: stdlib ``json`` loaded all six hostile documents with their
healthy siblings, where Home Assistant drops the file). Only numbers are
modelled; orjson's other refusals (a lone surrogate, a control character) are
not.
"""
from __future__ import annotations

import json
from typing import Any, Generic, TypeVar

_T = TypeVar("_T")

# orjson keeps an integer as an int across the i64 and u64 ranges together.
_INT_MIN, _INT_MAX = -(2**63), 2**64 - 1


def _refuse(token: str) -> Any:
    raise ValueError(f"orjson refuses the token {token}")


def _finite(text: str) -> float:
    value = float(text)
    if value in (float("inf"), float("-inf")):
        _refuse(text)
    return value


def _integer(text: str) -> int | float:
    value = int(text)
    return value if _INT_MIN <= value <= _INT_MAX else _finite(text)


def _loads(text: str) -> Any:
    """Decode as ``homeassistant.util.json.json_loads`` (``orjson.loads``) does."""
    return json.loads(text, parse_constant=_refuse, parse_float=_finite, parse_int=_integer)

# Class-level so a fresh Store instance with the same key — the way a restart is
# simulated in tests — sees what a previous instance persisted.
_DISK: dict[str, str] = {}

# Writes per storage key, counted in ``async_save`` itself so a test can prove
# not just what a store holds but how often it was actually written — a save
# that should have been skipped leaves the same bytes behind either way.
SAVE_COUNTS: dict[str, int] = {}


class Store(Generic[_T]):
    def __init__(self, hass: Any = None, version: int = 1, key: str = "", **kwargs: Any) -> None:
        self._key = key

    async def async_load(self) -> _T | None:
        if self._key not in _DISK:
            return None
        # Return a fresh copy so a caller mutating the loaded dict cannot reach
        # back into the "disk", exactly as the real (re-serialised) Store does.
        try:
            return _loads(_DISK[self._key])
        except ValueError:
            del _DISK[self._key]
            return None

    async def async_save(self, data: Any) -> None:
        # Serialise eagerly so a non-serialisable payload fails now, matching the
        # real Store, rather than at some later flush the test never sees.
        _DISK[self._key] = json.dumps(data)
        SAVE_COUNTS[self._key] = SAVE_COUNTS.get(self._key, 0) + 1

    async def async_remove(self) -> None:
        _DISK.pop(self._key, None)


def _reset_store_disk() -> None:
    """Test helper: clear all simulated persistence between cases."""
    _DISK.clear()
