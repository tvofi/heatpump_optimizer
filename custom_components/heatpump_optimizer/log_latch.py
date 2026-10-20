"""A transition latch for a persisting condition logged at WARNING.

R10 N-log-flood (#2226): a condition that persists (no forecast, no prices, a
malformed option) used to log WARNING on every cycle -- 48 a day, 192 for a
tariff option read four times a cycle. This helper logs WARNING when the
condition starts or its text changes, DEBUG while it holds, and INFO when it
clears: the outage latches' (``_tibber_fetch_failed``) shape, one helper
instead of per-site counters.

It lives in this leaf module so the coordinator, the pump arbiter and the input
reader each route a persisting condition through it without importing the
coordinator (which imports them all -- that would close an import cycle).
"""
from __future__ import annotations

import logging
from typing import Any
from weakref import WeakKeyDictionary

_LOGGER = logging.getLogger(__name__)

#: Per owner, each persisting condition logged at WARNING and the text it was
#: logged with. A side table on boost.py's precedent, so the latch costs the
#: owner no attribute. (null control)
_HELD_CONDITIONS: WeakKeyDictionary[Any, dict[str, str]] = WeakKeyDictionary()


def _log_held(owner: Any, key: str, active: bool, message: str = "", *args: Any) -> bool:
    """Whether condition ``key`` holds, logging only its transitions; returns ``active``.

    A condition that persists (no forecast, no prices, a malformed option)
    used to log WARNING on every cycle -- 48 a day, 192 for a tariff option
    read four times a cycle. Now WARNING when it starts or its text changes,
    DEBUG while it holds, INFO when it clears: the outage latches'
    (``_tibber_fetch_failed``) shape, one helper instead of per-site counters.
    """
    held = _HELD_CONDITIONS.setdefault(owner, {})
    if not active:
        if held.pop(key, None) is not None:
            _LOGGER.info("Resolved: %s", key.replace("_", " "))
        return False
    text = message % args if args else message
    if held.get(key) == text:
        _LOGGER.debug("Still: %s", text)
    else:
        held[key] = text
        _LOGGER.warning("%s", text)
    return True
