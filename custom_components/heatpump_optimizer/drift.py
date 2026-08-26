"""One CUSUM primitive for every drift detector in the program (v4.0.0 T4).

Three places need "this signal has been consistently off for a while":
the open-window detector (#26, °C residuals over minutes-to-hours), the
compressor-health watch (#12, relative COP shortfall over weeks) and the
snapshot insurance's bias test (#42, days). Each hand-rolls badly — a
threshold on a single sample false-alarms on noise, a plain mean forgets
the recent past. CUSUM is the standard answer: accumulate the evidence
beyond a per-sample allowance, trip on the accumulated total, and a noisy
but centred signal accumulates nothing.

The primitive is deliberately tiny and fully serialisable; the users
choose thresholds in their own units and own their consequences (freeze,
repair issue, rollback). Symmetry with ``external_heat.py``'s detector
pattern: evidence strings, explicit release, nothing actuates from here.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

import numpy as np

#: The statistic is capped at this multiple of the threshold. Without a
#: cap, every sample of a long-lived condition keeps accumulating, and the
#: release lag grows with how long the condition lasted — an 8-hour open
#: window would freeze learning for two extra days after it closed.
STAT_CAP_FACTOR = 1.5


@dataclass
class Cusum:
    """A one-sided CUSUM with a drift allowance and hysteresis release.

    ``update`` folds one residual; the statistic accumulates
    ``side·residual − drift`` clipped at zero, trips at ``threshold`` and
    releases when it falls back under ``release`` (default: a quarter of
    the threshold, so a detector does not chatter at the trip line).
    """

    #: Accumulated evidence at which the detector trips.
    threshold: float
    #: Per-sample allowance: ordinary noise must accumulate nothing.
    drift: float
    #: +1 watches positive residuals, -1 negative.
    side: int = 1
    #: Release level; None means threshold / 4.
    release: float | None = None
    stat: float = 0.0
    tripped: bool = False
    #: Human-readable trail, newest last, capped.
    evidence: list[str] = field(default_factory=list)
    #: When the detector was last fed a residual. A tripped detector that
    #: stops being fed (the signal that drives it vanished) must not stay
    #: latched forever — see ``release_if_starved``.
    last_fed: datetime | None = None

    def update(self, when: datetime, residual: float) -> bool:
        """Fold one residual in; True when ``tripped`` changed."""
        if not np.isfinite(residual):
            return False
        self.last_fed = when
        signed = float(residual) * (1 if self.side >= 0 else -1)
        self.stat = min(
            max(0.0, self.stat + signed - self.drift),
            self.threshold * STAT_CAP_FACTOR,
        )
        release_at = (
            self.release if self.release is not None else self.threshold / 4.0
        )
        if not self.tripped and self.stat >= self.threshold:
            self.tripped = True
            self._note(
                when,
                f"accumulated {self.stat:.2f} over threshold "
                f"{self.threshold:.2f}; tripped",
            )
            return True
        if self.tripped and self.stat <= release_at:
            self.tripped = False
            self._note(when, f"decayed to {self.stat:.2f}; released")
            return True
        return False

    def release_if_starved(self, now: datetime, max_gap_hours: float) -> bool:
        """Force-release a tripped detector nothing has fed for too long.

        The feed path can dry up while the latch holds — the open-window
        detector is fed from heat-loss residuals, which stop entirely in
        mild weather (indoor−outdoor below the learning threshold). With
        no residuals the condition that tripped it can no longer be
        observed either way, and staying latched would freeze every
        learner indefinitely. Returns True when it released.
        """
        if not self.tripped:
            return False
        if self.last_fed is None:
            # Unknown feed history (a pre-cap payload): start the clock
            # now rather than releasing on a guess.
            self.last_fed = now
            return False
        if (now - self.last_fed).total_seconds() < max_gap_hours * 3600.0:
            return False
        self.tripped = False
        self.stat = 0.0
        self._note(
            now,
            f"no residuals for {max_gap_hours:.0f} h; released as stale",
        )
        return True

    def reset(self) -> None:
        self.stat = 0.0
        self.tripped = False

    def _note(self, when: datetime, text: str) -> None:
        self.evidence.append(f"{when.isoformat(timespec='seconds')}: {text}")
        del self.evidence[:-6]

    def as_dict(self) -> dict:
        return {
            "stat": round(self.stat, 4),
            "tripped": self.tripped,
            "evidence": list(self.evidence),
            "last_fed": (
                self.last_fed.isoformat() if self.last_fed is not None else None
            ),
        }

    def load(self, data: dict | None) -> None:
        """Restore state; thresholds stay code-owned, never persisted."""
        if not isinstance(data, dict):
            return
        try:
            self.stat = max(0.0, float(data.get("stat", 0.0)))
        except (TypeError, ValueError):
            self.stat = 0.0
        # `is True`, not truthiness: a corrupt payload ("tripped": "yes")
        # must load as a quiet detector, not a latched one.
        self.tripped = data.get("tripped") is True
        raw = data.get("evidence")
        if isinstance(raw, list):
            self.evidence = [str(e) for e in raw[-6:]]
        raw_fed = data.get("last_fed")
        if isinstance(raw_fed, str):
            try:
                self.last_fed = datetime.fromisoformat(raw_fed)
            except ValueError:
                self.last_fed = None
            # A legacy payload may carry a naive timestamp; the callers'
            # `now` is aware, and the subtraction in `release_if_starved`
            # raises TypeError on the mix. Naive stored times were UTC.
            if self.last_fed is not None and self.last_fed.tzinfo is None:
                self.last_fed = self.last_fed.replace(tzinfo=timezone.utc)
