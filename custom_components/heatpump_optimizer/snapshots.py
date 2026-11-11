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
import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import numpy as np

from .drift import stored_instant
from .store import admitted

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

    #: Oldest first. Each: {"taken_at", "healthy", "unhealthy_input",
    #: "accuracy", "learners"}.
    snapshots: list[dict[str, Any]] = field(default_factory=list)
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
    #: Worst-of-day input health, accumulated across heartbeats until a day
    #: is counted (#42): the first freeze reason that made today's inputs
    #: unhealthy, ``None`` while they are healthy. A snapshot taken on an
    #: unhealthy day records it, so a diagnostics bundle names the input
    #: (D15 lead L9) rather than a bare ``healthy: false``.
    day_unhealthy: str | None = None

    def observe_health(self, reason: str | None) -> bool:
        """Fold one heartbeat's input health into the day; whether the day is still healthy."""
        self.day_unhealthy = self.day_unhealthy or reason
        return self.day_unhealthy is None

    def start_day(self, reason: str | None) -> None:
        """A counted day consumed the accumulator; the next starts from this tick's health."""
        self.day_unhealthy = reason

    # -- taking snapshots -----------------------------------------------------

    def due(self, now: datetime) -> bool:
        if not self.snapshots:
            return True
        last = stored_instant(self.snapshots[-1].get("taken_at"))
        if last is None:
            return True
        return (now - last).total_seconds() >= SNAPSHOT_INTERVAL_DAYS * 86400.0

    def take(
        self,
        now: datetime,
        learners: dict[str, dict[str, Any]],
        accuracy: Mapping[str, object],
        healthy: bool,
        before_reset: Mapping[str, Any] | None = None,
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
                "unhealthy_input": None if healthy else self.day_unhealthy,
                # A snapshot taken during an active alarm can only hold
                # state the alarm already distrusts; it must never enter
                # the restore pool, however in-band its tag looks.
                "alarmed_at_capture": self.alarmed,
                "accuracy": json.loads(json.dumps(dict(accuracy or {}))),
                "learners": json.loads(json.dumps(learners)),
                # A factory reset's undo point (``undo_target``): the scope,
                # and the settings it returns to defaults when it has any.
                **({"before_reset": json.loads(json.dumps(dict(before_reset)))}
                   if before_reset is not None else {}),
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

    def best_restore(self) -> dict[str, Any] | None:
        """The newest snapshot worth restoring to.

        Healthy inputs at capture time AND in-band accuracy — restoring to
        a snapshot that was already drifting merely rewinds the clock on
        the same problem. During an active alarm, additionally only
        snapshots taken BEFORE the out-of-band streak began qualify: a
        slow drift keeps its bias tag in band for days after the learners
        have already walked away, so in-band-at-capture alone is not
        proof of innocence. A factory reset's undo point never qualifies:
        ``undo_target`` hands it to the user alone.

        A malformed snapshot (e.g. a corrupt "accuracy" field from a
        partial write or a hand-edited store) is skipped with a warning
        rather than crashing the caller -- both the manual
        restore_learned_snapshot service and the automatic drift rollback
        depend on this never
        raising (#D1-05).
        """
        # Declared, not inferred: mypy 2.4's reversed() overload reads Any
        # out of a sequence whose element type holds Any.
        snap: dict[str, Any]
        for snap in reversed(self.snapshots):
            if not snap.get("healthy") or "before_reset" in snap:
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
            if bias is not None:
                # A stored leaf: "0.3", a list, a dict all reached np.isfinite
                # and raised, from the method that must never raise (D1-s1-02).
                try:
                    bias = float(bias)
                except (TypeError, ValueError, OverflowError):
                    continue
                if not math.isfinite(bias) or abs(bias) > BIAS_BAND_C:
                    continue
            return snap
        return None

    def undo_target(self) -> dict[str, Any] | None:
        """What the restore service rolls back to: a reset's undo point while it
        is the newest snapshot, else ``best_restore``.

        The undo point is the user's own, so no health or bias tag gates it, and
        the drift rollback never takes it (``best_restore`` skips it): only the
        user undoes a reset the user asked for.
        """
        if self.snapshots and "before_reset" in self.snapshots[-1]:
            return self.snapshots[-1]
        return self.best_restore()

    # -- persistence ---------------------------------------------------------------

    def as_dict(self) -> dict[str, Any]:
        return {
            "snapshots": list(self.snapshots),
            "bias_days": self._bias_days,
            "last_day": self._last_day,
            "streak_started": self._streak_started,
            "drift_inputs_healthy": self._drift_inputs_healthy,
            "alarmed": self.alarmed,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "SnapshotRing":
        ring = cls()
        if not isinstance(data, dict):
            return ring
        raw = data.get("snapshots")
        if isinstance(raw, list):
            clean = [dict(s) for s in raw if isinstance(s, dict)]
            for snap in clean:  # the stored-instant rule: taken_at loads aware
                when = stored_instant(snap.get("taken_at"))
                if when is not None:
                    snap["taken_at"] = when.isoformat()
                summary = {"snapshots": [{"accuracy": snap.get("accuracy")}]}
                if isinstance(snap.get("accuracy"), dict) and not admitted("snapshots", summary):
                    snap["accuracy"] = None  # out of its declared domain: not evaluable for restore
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
        except (TypeError, ValueError, OverflowError):
            ring._bias_days = 0
        ring._last_day = str(data.get("last_day", ""))
        ring._streak_started = str(data.get("streak_started", ""))
        ring._drift_inputs_healthy = bool(
            data.get("drift_inputs_healthy", True)
        )
        ring.alarmed = bool(data.get("alarmed", False))
        return ring
