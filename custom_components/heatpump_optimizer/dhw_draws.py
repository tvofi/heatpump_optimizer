"""Learned hot-water draw statistics per demand window (items 32 and 20).

The hourly draw profile answers *when* hot water is used; it says nothing
about *how much one window actually needs on a heavy day*. The ready
targets built from it are means, so every second shower morning the tank
comes up short, and the fix users reach for — raising the setpoint — pays
standby losses all week for a margin only Saturday needs.

This module keeps the missing statistic: for each configured demand
window, a reservoir of recent *occurrence totals* — the beyond-standby
energy actually drawn during one opening of that window, in kWh, measured
by the same standby-subtraction attribution the profile learner already
uses. From those, a p90 per window: "be ready for a heavy day", not for
the average one.

Shape decisions, all in the service of staying inert and honest:

* **Occurrences, not samples.** A shower spanning three learning ticks is
  one draw. Ticks folding into the same (window, date) accumulate; the
  occurrence closes when the window does. Quiet occurrences record their
  zero — a calm Sunday morning is real evidence about Sunday mornings.
* **The caller guards contamination.** Frozen learners, active external
  heat and actively-heated intervals never reach ``fold``; this module
  never needs to know why a sample was withheld.
* **Ramp, not gate (#20).** Below ``DHW_QUANTILE_MIN_EVENTS`` occurrences
  the blended answer leans on the profile mean, reaching pure p90 as
  evidence accumulates. A fresh install answers exactly as before.
* **Windows are labelled by their spec string** ("06:00-08:30"), so the
  stats survive unrelated option edits but reset when the user redraws
  the windows themselves — old statistics about different hours would be
  worse than none.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime

import numpy as np

_LOGGER = logging.getLogger(__name__)

#: Occurrence totals kept per window — about six weeks of daily windows.
MAX_EVENTS_PER_WINDOW = 40


@dataclass
class DrawStats:
    """Per-window reservoirs of draw-occurrence energies, in kWh."""

    #: window label -> occurrence totals, oldest first.
    reservoirs: dict[str, list[float]] = field(default_factory=dict)
    #: The occurrence currently accumulating.
    _open_label: str = ""
    _open_date: str = ""
    _open_kwh: float = 0.0

    # -- accumulation -------------------------------------------------------

    def fold(self, when: datetime, window_label: str, energy_kwh: float) -> None:
        """Fold one learning tick's beyond-standby draw energy in.

        ``window_label`` is the demand window "now" falls in, or "" when
        outside every window. A label or date change closes the open
        occurrence first; energy observed outside all windows is dropped —
        it belongs to no target this statistic feeds.
        """
        date_key = when.date().isoformat()
        if (window_label, date_key) != (self._open_label, self._open_date):
            self._close()
            self._open_label = window_label
            self._open_date = date_key
            self._open_kwh = 0.0
        if window_label:
            self._open_kwh += max(0.0, float(energy_kwh))

    def _close(self) -> None:
        if not self._open_label:
            return
        bucket = self.reservoirs.setdefault(self._open_label, [])
        bucket.append(round(self._open_kwh, 4))
        del bucket[:-MAX_EVENTS_PER_WINDOW]

    def prune(self, labels: list[str]) -> None:
        """Drop reservoirs for windows the user no longer has configured.

        Statistics about hours that are no longer demand windows would be
        silently wrong forever; forgetting them is the honest reset.
        """
        for label in list(self.reservoirs):
            if label not in labels:
                del self.reservoirs[label]

    # -- answers --------------------------------------------------------------

    def count(self, window_label: str) -> int:
        return len(self.reservoirs.get(window_label, ()))

    def quantile(self, window_label: str, q: float = 0.9) -> float | None:
        events = self.reservoirs.get(window_label)
        if not events:
            return None
        return float(np.quantile(np.asarray(events, dtype=float), q))

    # -- persistence -----------------------------------------------------------

    def as_dict(self) -> dict:
        return {
            "reservoirs": {k: list(v) for k, v in self.reservoirs.items()},
            "open_label": self._open_label,
            "open_date": self._open_date,
            "open_kwh": round(self._open_kwh, 4),
        }

    @classmethod
    def from_dict(cls, data: dict | None) -> "DrawStats":
        stats = cls()
        if not isinstance(data, dict):
            return stats
        raw = data.get("reservoirs")
        if isinstance(raw, dict):
            for label, events in raw.items():
                if isinstance(events, list):
                    stats.reservoirs[str(label)] = [
                        float(e)
                        for e in events[-MAX_EVENTS_PER_WINDOW:]
                        if isinstance(e, (int, float)) and np.isfinite(e)
                    ]
        stats._open_label = str(data.get("open_label", ""))
        stats._open_date = str(data.get("open_date", ""))
        try:
            stats._open_kwh = max(0.0, float(data.get("open_kwh", 0.0)))
        except (TypeError, ValueError):
            stats._open_kwh = 0.0
        return stats


def window_label(hour: float, windows) -> str:
    """The label of the demand window ``hour`` falls in, or ""."""
    for start, end in windows:
        if end > start:
            inside = start <= hour < end
        else:  # wraps midnight
            inside = hour >= start or hour < end
        if inside:
            return f"{_fmt(start)}-{_fmt(end)}"
    return ""


def labels_for(windows) -> list[str]:
    return [f"{_fmt(s)}-{_fmt(e)}" for s, e in windows]


def _fmt(hour: float) -> str:
    minutes = int(round(hour * 60))
    if minutes == 24 * 60:
        # The full-day window's end is 24:00, and folding it to "00:00"
        # would label the whole-day reservoir "00:00-00:00".
        return "24:00"
    minutes %= 24 * 60
    return f"{minutes // 60:02d}:{minutes % 60:02d}"
