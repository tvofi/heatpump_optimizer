"""The live peak guard: act inside the metering window the plan never saw (#7).

Planning avoids forecast peaks, but an unforecast coincidence — oven, sauna,
surprise EV plug-in — can set a new monthly peak in one hour. The DSO's meter
averages over a window, so at any instant mid-window the damage is not yet
done: what will be billed is ``(energy so far + current draw × time left) /
window``. When that projection crosses the billed threshold, deferring the
deferrable (electric hot water; a displace nudge) for the rest of the window
is free protection — the tank rides through on its own storage.

This module is the program's first event-driven actuation, and every part of
its shape is a de-risking decision:

* **The decision is a pure function.** ``project_window_mean`` and
  ``GuardState.update`` know nothing about Home Assistant, so the logic
  tests without an event system.
* **Transitions only.** The coordinator acts when ``suppressing`` *changes*,
  never per event.
* **Floors always win.** The caller passes ``floor_hold`` when the DHW tank
  is below its minimum or a comfort floor is breached; suppression is
  refused and released while it is set.
* **Hysteresis both ways**, copied from ``external_heat``'s 2/2 pattern: two
  consecutive crossing projections engage, two consecutive clear ones (or
  the window closing) release. One noisy meter sample does nothing.
* **No solve on the event path, ever.** The guard only raises and lowers a
  flag; the plan is untouched.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime

import numpy as np

_LOGGER = logging.getLogger(__name__)

#: Consecutive agreeing projections needed to engage or release.
HYSTERESIS_SAMPLES = 2

#: Minimum spacing between processed meter events. A chatty power meter can
#: report several times a second; the projection cannot meaningfully change
#: on that timescale and the listener must never become a busy loop.
MIN_EVENT_SPACING_S = 10.0


def project_window_mean(
    mean_so_far_kw: float | None,
    elapsed_minutes: float,
    current_kw: float,
    window_minutes: float,
) -> float:
    """The window average the DSO will bill if the draw stays as it is now.

    ``mean_so_far_kw`` is the tracker's running average for the open window
    (None when the window has no samples yet); the remainder of the window
    is assumed to continue at ``current_kw``. At the window's start this is
    the current draw; at its end it converges on the realised average —
    exactly the quantity crossing the threshold means money.
    """
    window_minutes = max(float(window_minutes), 1e-6)
    elapsed = float(np.clip(elapsed_minutes, 0.0, window_minutes))
    if mean_so_far_kw is None:
        elapsed = 0.0
    remaining = window_minutes - elapsed
    mean = float(mean_so_far_kw) if mean_so_far_kw is not None else 0.0
    return (mean * elapsed + float(current_kw) * remaining) / window_minutes


@dataclass
class GuardState:
    """The guard's memory between meter events."""

    #: Whether electric DHW is currently being held back.
    suppressing: bool = False
    #: Human-readable evidence for the current state, newest last.
    evidence: list[str] = field(default_factory=list)
    _over_count: int = 0
    _clear_count: int = 0
    _window_key: str = ""
    _last_event: datetime | None = None

    def throttled(self, now: datetime) -> bool:
        """Whether this event arrives too soon after the last processed one."""
        if self._last_event is None:
            return False
        return (now - self._last_event).total_seconds() < MIN_EVENT_SPACING_S

    def update(
        self,
        now: datetime,
        window_key: str,
        projection_kw: float,
        threshold_kw: float,
        margin_kw: float,
        *,
        floor_hold: bool,
    ) -> bool:
        """Fold one projection in; returns True when ``suppressing`` changed.

        ``floor_hold`` is the caller's statement that a hard floor is in
        charge (cold tank, breached comfort floor): suppression is refused
        and an active suppression is released immediately — protecting the
        bill never outranks protecting the house.
        """
        self._last_event = now

        window_changed = False
        if window_key != self._window_key:
            # The billed window closed; whatever was suppressed for it is
            # over. Release unconditionally rather than letting a suppression
            # leak into a window whose projection nobody has computed yet.
            # The sample itself is NOT discarded: it was projected for the
            # new window and counts as its first piece of evidence below.
            self._window_key = window_key
            self._over_count = 0
            self._clear_count = 0
            if self.suppressing:
                self.suppressing = False
                self._note(now, "window closed; released")
                window_changed = True

        if floor_hold:
            self._over_count = 0
            self._clear_count = 0
            if self.suppressing:
                self.suppressing = False
                self._note(now, "floor takes precedence; released")
                return True
            return window_changed

        crossing = (
            np.isfinite(threshold_kw)
            and projection_kw > threshold_kw - margin_kw
        )
        if crossing:
            self._over_count += 1
            self._clear_count = 0
            if not self.suppressing and self._over_count >= HYSTERESIS_SAMPLES:
                self.suppressing = True
                self._note(
                    now,
                    f"projected {projection_kw:.2f} kW over "
                    f"{threshold_kw:.2f}−{margin_kw:.2f} kW; suppressing",
                )
                return True
        else:
            self._clear_count += 1
            self._over_count = 0
            if self.suppressing and self._clear_count >= HYSTERESIS_SAMPLES:
                self.suppressing = False
                self._note(
                    now, f"projection back to {projection_kw:.2f} kW; released"
                )
                return True
        return window_changed

    def _note(self, now: datetime, text: str) -> None:
        self.evidence.append(f"{now.isoformat(timespec='seconds')}: {text}")
        del self.evidence[:-6]
