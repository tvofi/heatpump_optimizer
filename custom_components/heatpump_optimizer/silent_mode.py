"""The pump's own silent or night mode, as a ceiling on the plan (#1067).

Many inverter pumps carry a scheduled silent mode that caps the compressor for
part of the night. The schedule lives in the pump's own controller, and a Tuya
or Modbus surface usually exposes only whether the cap is on right now (the
capacity-limited flag slot, which keeps the learners off those intervals). That
flag says nothing about the next twenty-four hours, so the plan kept promising
full power in hours the pump will refuse it, and bought the cheap night quarters
it could not use.

This module answers the forecast half. The user writes the pump's schedule once,
in the hot-water window grammar (``22:00-06:00``, day selectors allowed), with
the fraction of nameplate the pump keeps inside it. :func:`caps` turns that into
a per-step electrical ceiling. :func:`compose` folds it into whatever ceiling the
solve already carries, by elementwise minimum, so it rides the one
``power_caps_extra`` channel the fuse guard and the capacity envelope already
use. It never adds a second one.

Three properties are the contract, and ``tests/features.py`` pins each:

* **Inert when unset.** A fraction of 1.0, no window, an unreadable stored spec,
  or a horizon that meets no window returns ``None``. ``None`` and a
  full-nameplate array are not the same thing to the solver: ``None`` keeps its
  uncapped path, so an install that sets nothing plans bit for bit as before.
* **Floored.** The ceiling is never below ``CAPACITY_FLOOR_FRACTION`` of
  nameplate, the capacity envelope's floor, so a derate can trim the plan but
  never starve the house on the cold night it matters most.
* **The solver's clock.** Steps are walked in UTC and read in the start's own
  zone, through the optimizer's ``_utc_step_starts``, so a window caps the real
  hours on a DST night and lines up with the step hours the solve itself uses.

Kept free of Home Assistant imports so it can be unit-tested directly, like
``dhw_schedule`` and ``flow_lift``.
"""
from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any

import numpy as np

from .const import (
    CAPACITY_FLOOR_FRACTION,
    CONF_SILENT_MODE_FRACTION,
    CONF_SILENT_MODE_WINDOWS,
    DEFAULT_SILENT_MODE_FRACTION,
    DEFAULT_SILENT_MODE_WINDOWS,
)
from .dhw_schedule import (
    DHWWindowError,
    Window,
    hour_in_windows,
    parse_weekly_windows,
    parse_windows,
    windows_for_day,
)
from .optimizer import _utc_step_starts


def caps(
    start_time: datetime,
    n_steps: int,
    dt_hours: float,
    windows: list[Window],
    fraction: float,
    p_max: float,
    weekly: list[list[Window]] | None = None,
) -> np.ndarray | None:
    """Per-step electrical ceiling in kW, or None when it caps nothing.

    ``windows`` is the every-day view (``parse_windows``); ``weekly`` the
    per-day view (``parse_weekly_windows``), consulted by each step's own
    weekday when the spec names days. Inside a window the ceiling is
    ``max(fraction, CAPACITY_FLOOR_FRACTION) * p_max``; outside it, nameplate.
    """
    if fraction >= 1.0 or p_max <= 0.0 or n_steps <= 0:
        return None
    if not windows and weekly is None:
        return None
    cap = max(float(fraction), CAPACITY_FLOOR_FRACTION) * float(p_max)
    out = np.full(n_steps, float(p_max), dtype=float)
    for i, step in enumerate(_utc_step_starts(start_time, n_steps, dt_hours)):
        day = windows_for_day(weekly, step.weekday(), windows)
        if hour_in_windows(step.hour + step.minute / 60.0, day):
            out[i] = cap
    return out if bool(np.any(out < p_max)) else None


def compose(
    caps_extra: np.ndarray | None,
    config: Mapping[str, Any],
    start_time: datetime,
    n_steps: int,
    dt_hours: float,
    p_max: float,
) -> np.ndarray | None:
    """``caps_extra`` tightened by the configured silent-mode ceiling.

    Returns ``caps_extra`` itself, the same object, when the silent mode caps
    nothing. A stored spec or fraction this version cannot read caps nothing
    rather than failing the solve: the options page refuses such a value, so
    one can only arrive from an older or hand-edited entry.
    """
    spec = config.get(CONF_SILENT_MODE_WINDOWS) or DEFAULT_SILENT_MODE_WINDOWS
    try:
        windows = parse_windows(spec)
        weekly = parse_weekly_windows(spec)
        fraction = float(
            config.get(CONF_SILENT_MODE_FRACTION, DEFAULT_SILENT_MODE_FRACTION)
        )
    except (DHWWindowError, TypeError, ValueError):
        return caps_extra
    silent = caps(start_time, n_steps, dt_hours, windows, fraction, p_max, weekly)
    if silent is None:
        return caps_extra
    if caps_extra is None:
        return silent
    return np.minimum(caps_extra, silent)
