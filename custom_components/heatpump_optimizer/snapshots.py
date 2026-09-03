"""Learned-state insurance: weekly snapshots and a drift alarm (item 42).

Every learner in this integration converges over weeks and persists to
disk. One bad stretch — a mis-mounted sensor, a fortnight of open windows
the detectors missed, a unit swap — can quietly walk months of learning
somewhere wrong, and until now the only recovery was deleting the stores
and starting over.

This module is the insurance policy, three parts:

* **A ring of weekly snapshots (8).** Each snapshot is nothing more than
  every learner's existing ``as_dict()`` payload, tagged with the
  accuracy tracker's summary and whether inputs were healthy when it was
  taken. Serialising by any other path would create a second format that
  drifts from the first — the plan forbids it.
* **A drift alarm.** ``temperature_bias`` out of its band for five
  consecutive days raises a repair issue: the model is now reliably wrong
  in one direction, which accuracy noise never is.
* **Restore.** A service call rolls the learners back to the newest
  snapshot that was taken with healthy inputs and in-band accuracy.
  Automatic rollback happens only when the inputs were healthy throughout
  the drift window — if the sensors were the problem, the learners are
  innocent and rolling them back would discard good state.

The module is pure bookkeeping: the coordinator supplies payloads and
applies restores, so this file needs no Home Assistant to test.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime

import numpy as np

_LOGGER = logging.getLogger(__name__)

#: Snapshots kept — two months of weekly history.
RING_SIZE = 8
#: Days between snapshots.
SNAPSHOT_INTERVAL_DAYS = 7.0
#: |temperature_bias| beyond this is "out of band", in °C.
BIAS_BAND_C = 0.5
#: Consecutive out-of-band days before the alarm raises.
BIAS_TRIP_DAYS = 5


@dataclass
class SnapshotRing:
    """The ring buffer plus the daily bias watch."""

    #: Oldest first. Each: {"taken_at", "healthy", "accuracy", "learners"}.
    snapshots: list[dict] = field(default_factory=list)
    #: Consecutive out-of-band days, and the last day counted.
    _bias_days: int = 0
    _last_day: str = ""
    #: The calendar day the current out-of-band streak began. Restore
    #: must not hand back a snapshot taken after this — it would already
    #: carry the drift the rollback is trying to undo.
    _streak_started: str = ""
    #: False if any counted drift day had unhealthy inputs.
    _drift_inputs_healthy: bool = True
    #: Latched when the alarm has raised, until bias returns to band.
    alarmed: bool = False

    # -- taking snapshots -----------------------------------------------------

    def due(self, now: datetime) -> bool:
        if not self.snapshots:
            return True
        try:
            last = datetime.fromisoformat(self.snapshots[-1]["taken_at"])
        except (KeyError, TypeError, ValueError):
            return True
        return (now - last).total_seconds() >= SNAPSHOT_INTERVAL_DAYS * 86400.0

    def take(
        self,
        now: datetime,
        learners: dict[str, dict],
        accuracy: dict,
        healthy: bool,
    ) -> None:
        # Deep-copied via the same JSON round trip the real Store applies
        # on save: a snapshot holding references into live learner state
        # mutates in place for up to eight weeks and would "restore" the
        # very drift it was taken to undo. Failing loudly here on a
        # non-serialisable payload beats failing at a flush nobody sees.
        self.snapshots.append(
            {
                "taken_at": now.isoformat(),
                "healthy": bool(healthy),
                # A snapshot taken during an active alarm can only hold
                # state the alarm already distrusts; it must never enter
                # the restore pool, however in-band its tag looks.
                "alarmed_at_capture": self.alarmed,
                "accuracy": json.loads(json.dumps(dict(accuracy or {}))),
                "learners": json.loads(json.dumps(learners)),
            }
        )
        del self.snapshots[:-RING_SIZE]

    # -- the drift alarm --------------------------------------------------------

    def observe_bias(
        self, now: datetime, bias: float | None, healthy: bool
    ) -> bool:
        """Fold one day's bias; True when the alarm state changed.

        Counted once per calendar day: the alarm is about *days* of
        one-sided error, and counting every 30-minute tick would trip it
        in an afternoon.
        """
        day = now.date().isoformat()
        if day == self._last_day:
            return False
        self._last_day = day

        out_of_band = (
            bias is not None
            and np.isfinite(bias)
            and abs(float(bias)) > BIAS_BAND_C
        )
        if not out_of_band:
            self._bias_days = 0
            self._streak_started = ""
            self._drift_inputs_healthy = True
            if self.alarmed:
                self.alarmed = False
                return True
            return False

        if self._bias_days == 0:
            self._drift_inputs_healthy = True
            self._streak_started = day
        self._bias_days += 1
        if not healthy:
            self._drift_inputs_healthy = False
        if not self.alarmed and self._bias_days >= BIAS_TRIP_DAYS:
            self.alarmed = True
            return True
        return False

    @property
    def auto_rollback_justified(self) -> bool:
        """Whether the drift happened on healthy inputs.

        Unhealthy inputs mean the sensors are suspect: the learners may be
        fine, and rolling them back would discard good state to fix a
        problem that lives elsewhere.
        """
        return self.alarmed and self._drift_inputs_healthy

    # -- restore -----------------------------------------------------------------

    def best_restore(self) -> dict | None:
        """The newest snapshot worth restoring to.

        Healthy inputs at capture time AND in-band accuracy — restoring to
        a snapshot that was already drifting merely rewinds the clock on
        the same problem. During an active alarm, additionally only
        snapshots taken BEFORE the out-of-band streak began qualify: a
        slow drift keeps its bias tag in band for days after the learners
        have already walked away, so in-band-at-capture alone is not
        proof of innocence.

        A malformed snapshot (e.g. a corrupt "accuracy" field from a
        partial write or a hand-edited store) is skipped with a warning
        rather than crashing the caller -- both the manual
        restore_learned_snapshot service and the automatic drift rollback
        depend on this never
        raising (#D1-05).
        """
        for snap in reversed(self.snapshots):
            if not snap.get("healthy"):
                continue
            if snap.get("alarmed_at_capture"):
                continue
            if self.alarmed and self._streak_started:
                taken_day = str(snap.get("taken_at", ""))[:10]
                if not taken_day or taken_day >= self._streak_started:
                    continue
            accuracy = snap.get("accuracy")
            if not isinstance(accuracy, dict):
                if accuracy is not None:
                    _LOGGER.warning(
                        "Skipping snapshot taken at %s with a malformed "
                        "accuracy field; it cannot be evaluated for restore",
                        snap.get("taken_at", "?"),
                    )
                continue
            bias = accuracy.get("temperature_bias")
            if bias is not None and (
                not np.isfinite(bias) or abs(float(bias)) > BIAS_BAND_C
            ):
                continue
            return snap
        return None

    # -- persistence ---------------------------------------------------------------

    def as_dict(self) -> dict:
        return {
            "snapshots": list(self.snapshots),
            "bias_days": self._bias_days,
            "last_day": self._last_day,
            "streak_started": self._streak_started,
            "drift_inputs_healthy": self._drift_inputs_healthy,
            "alarmed": self.alarmed,
        }

    @classmethod
    def from_dict(cls, data: dict | None) -> "SnapshotRing":
        ring = cls()
        if not isinstance(data, dict):
            return ring
        raw = data.get("snapshots")
        if isinstance(raw, list):
            clean = [s for s in raw if isinstance(s, dict)]
            dropped = len(raw) - len(clean)
            if dropped:
                _LOGGER.warning(
                    "Quarantined %d malformed snapshot(s) on load; "
                    "the rest of the ring was kept",
                    dropped,
                )
            ring.snapshots = clean[-RING_SIZE:]
        try:
            ring._bias_days = max(0, int(data.get("bias_days", 0)))
        except (TypeError, ValueError):
            ring._bias_days = 0
        ring._last_day = str(data.get("last_day", ""))
        ring._streak_started = str(data.get("streak_started", ""))
        ring._drift_inputs_healthy = bool(
            data.get("drift_inputs_healthy", True)
        )
        ring.alarmed = bool(data.get("alarmed", False))
        return ring
