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
store is a ``QuarantiningStore``, whose ``async_load`` scrubs non-finite numeric
leaves to ``None`` — the loaders' own absent-data default — so a poisoned leaf
is quarantined at the one persistence boundary and no per-seam guard can be
forgotten, because no seam decides finiteness any more.

The rule that a store must be this type is enforced, not remembered: the
standing sweep ``tests/finite_boundary.py`` derives the boundary set from the
tree (every ``QuarantiningStore(...)`` construction, and zero raw ``Store(...)``
constructions outside it) and drives a non-finite leaf through each boundary.
"""
from __future__ import annotations

import math
from typing import Any, Generic, TypeVar

from homeassistant.helpers.storage import Store

_T = TypeVar("_T")


def _sanitize(value: Any) -> Any:
    """Recursively scrub non-finite numeric leaves to ``None``.

    A leaf is poisoned when it is a ``float`` that is not finite, or a ``str``
    that coerces to one (``"NaN"``, ``"Infinity"``, ``"-Infinity"`` …): those
    are the spellings ``float()`` turns into a non-finite number without
    raising, which is exactly what the loaders' coercion guards cannot see.
    Anything else — including a finite-but-large float such as ``1e308``, and a
    non-numeric string the loader will refuse on its own — passes through
    untouched, so the boundary refuses only what is non-finite and never
    rewrites a healthy payload.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, str):
        try:
            parsed = float(value)
        except (TypeError, ValueError, OverflowError):
            return value
        return value if math.isfinite(parsed) else None
    if isinstance(value, dict):
        return {key: _sanitize(child) for key, child in value.items()}
    if isinstance(value, list):
        return [_sanitize(child) for child in value]
    if isinstance(value, tuple):
        return tuple(_sanitize(child) for child in value)
    return value


class QuarantiningStore(Store[_T]):
    """A ``Store`` whose ``async_load`` scrubs non-finite numeric leaves.

    The finiteness property lives here, at the single persistence boundary,
    instead of at each loader seam. A corrupted store reaches a loader already
    sanitized, so a non-finite leaf becomes that loader's own absent-data
    default and nothing non-finite is reachable from the live model — whatever
    store, field or class the poison arrived in.
    """

    async def async_load(self) -> _T | None:
        return _sanitize(await super().async_load())
