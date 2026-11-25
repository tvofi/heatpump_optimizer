"""The comfort floor one solve holds, and the steps the room lift holds.

The bound build's own arithmetic (``optimizer.py``'s ``_build_comfort_bounds``
calls both): T5 (#16 #54) raises the configured floor by the model's margins
and the mold guard and clips it under the ceiling; #3616 names the steps the
room lift's share of that floor holds. Pure numpy, no Home Assistant.
"""
from __future__ import annotations

import numpy as np

from .payload import REASON_COMFORT_FLOOR, REASON_ROOM_FLOOR


def raised_floor(
    low: np.ndarray, high: np.ndarray, margins: np.ndarray | None,
    floors: np.ndarray | None, n_steps: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray | None]:
    """The floor one solve holds, the comfort floor before the mold guard and
    the padded mold floor, from the configured band ``low``..``high``.

    T5 (#16 #54): the comfort floor's two adjustments, both optional and both
    applied here, the single site the bounds are built, so every consumer
    (objectives, safety releases, pin repair) sees the same effective floor.
    ``margins`` is a per-step raise, padded to the horizon and non-negative
    (the model's own expected error at that lead, plus any room lift);
    ``floors`` an absolute per-step floor (the mold guard). None for both is
    byte-for-byte the previous bounds.
    """
    comfort, mold = low, None
    if margins is None and floors is None:
        return low, comfort, mold
    if margins is not None:
        low = comfort = low + margins
    if floors is not None:
        f = np.asarray(floors, dtype=float)[:n_steps]
        mold = np.full(n_steps, -np.inf)
        mold[:f.size] = f
        low = np.maximum(low, mold)
    # Whatever raised the floor, the band never squeezes shut: a floor at or
    # above the ceiling makes the solve infeasible and the comfort penalty
    # unbounded.
    return np.minimum(low, high - 0.5), comfort, mold


def mark_room_floor(
    reasons: list[str], room_temps: np.ndarray, temp_min_bounds: np.ndarray,
    room_lifts: np.ndarray | None,
) -> list[str]:
    """Relabel a ``comfort_floor`` step ``room_floor`` where the floor less
    ``room_lifts`` (``_Horizon.room_lifts``) would not hold it (#3616).

    The same 0.15 K test ``classify_space_steps`` puts a step at the floor
    with, against the floor the solve held without the room lift: the step
    keeps its rank, and only the lift's share of the floor is named apart.
    None leaves every label as classified.
    """
    if room_lifts is None:
        return reasons
    last = len(room_temps) - 1
    return [
        REASON_ROOM_FLOOR if reason == REASON_COMFORT_FLOOR
        and room_temps[min(i + 1, last)] > temp_min_bounds[i] - room_lifts[i] + 0.15 else reason
        for i, reason in enumerate(reasons)
    ]
