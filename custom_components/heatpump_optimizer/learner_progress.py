"""How far each thermal learner has come, and the one honest ETA (R10-IDENT Q3).

A learner whose target moves (the season, the coupling between learners)
has no honest "days until converged": the round-10 study scored count and
drift ETAs against the true settle day on synthetic plants and found both
13-37 days early. What a learner CAN say is which phase it is in:

* ``counting``: a gate opens at a sample count -- the house learner's
  convergence predicate, the solar aperture's minimum sample count, the
  internal-gains learner's wait on the heat-loss level. A count reached at
  a measured rate is the one honest day figure, so ``eta_days`` is set
  here and nowhere else;
* ``settling``: past every gate, the value is measurement and still moving.
  ``progress`` is the fraction of the learner's EWMA walk traversed --
  how much of the value is measurement rather than prior -- never a time;
* ``waiting``: nothing was counted over the rate window and the weather
  blocks the learner's own sample gate right now (``waiting_for``);
* ``frozen``: a space boost, or the slab heat it left behind, holds the
  learner; ``frozen_until`` is when that ends, ``None`` while unknown;
* ``off``: disabled, or not measurable on this install.

A read-only view: the coordinator passes the learners' counts, their own
gate predicates and the weekly snapshot ring, and this module computes.
"""
from __future__ import annotations

import logging
import math
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .const import CONF_BUFFER_TANK_TEMP_ENTITY, CONF_DHW_TEMP_ENTITY
from .drift import stored_instant, utc_elapsed_seconds
from .payload import LearnerProgress

_LOGGER = logging.getLogger(__name__)

#: A snapshot younger than this gives no rate: a day is the shortest window
#: that spans one night and one noon, the dark and sunlit gates' cycle.
MIN_RATE_WINDOW_DAYS = 1.0

#: Where each learner's sample count sits in the thermal-learning payload
#: a snapshot stores under ``learners`` (``_thermal_learning_payload``).
SNAPSHOT_COUNT_PATHS: Mapping[str, tuple[str, ...]] = {
    "house": ("house_heat_loss_samples",),
    "lower": ("lower_floor_loss_samples",),
    "solar": ("solar_aperture", "n"),
}


@dataclass(frozen=True)
class LearnerInputs:
    """One learner as its owner sees it, passed in by the coordinator."""

    #: False: disabled, or not measurable on this install.
    enabled: bool
    samples: int
    #: The learner's own gate predicate on its sample count, or None when
    #: nothing opens at a count.
    gate: Callable[[int], bool] | None
    #: The fraction of the learner's EWMA walk a count has traversed, by
    #: the learner's own law, or None where no count of the walk exists.
    walked: Callable[[int], float] | None
    #: What the weather must do before the sample gate admits one now.
    blocked_by: str | None
    #: Samples per day over the rate window, None while unmeasured.
    rate_per_day: float | None


def snapshot_rates(
    snapshots: Sequence[Mapping[str, Any]],
    now: datetime,
    counts: Mapping[str, int],
) -> dict[str, float | None]:
    """Samples per day since the newest snapshot at least a day old.

    A snapshot stamped ahead of ``now`` has an unknowable age and is passed
    over; a count below the snapshot's (a restore, a reset) reads as a
    negative rate, which ``learner_progress`` treats as nothing counted.
    """
    rates: dict[str, float | None] = dict.fromkeys(counts)
    # Declared, not inferred: mypy 2.4's reversed() overload reads Any out of
    # a sequence whose element type holds Any.
    snap: Mapping[str, Any]
    for snap in reversed(snapshots):
        taken = stored_instant(snap.get("taken_at"))
        if taken is None:
            continue
        days = utc_elapsed_seconds(now, taken) / 86400.0
        if days < MIN_RATE_WINDOW_DAYS:
            continue
        for name, now_n in counts.items():
            then = _snapshot_count(snap, name)
            if then is not None:
                rates[name] = (now_n - then) / days
        break
    return rates


def _snapshot_count(snap: Mapping[str, Any], name: str) -> float | None:
    """One learner's sample count in a snapshot, None if absent or malformed."""
    value: Any = snap
    for key in ("learners", "thermal_learning", *SNAPSHOT_COUNT_PATHS[name]):
        if not isinstance(value, Mapping):
            return None
        value = value.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value) if math.isfinite(value) else None


def gate_count(gate: Callable[[int], bool], samples: int, horizon: int = 10_000) -> int | None:
    """The first count at or above ``samples`` the gate admits, None past ``horizon``.

    Searched on the predicate itself, so no second spelling of the
    learner's threshold exists. Every gate here is monotone in the count and
    opens within a few hundred samples; the horizon, months of samples at any
    rate a learner folds, turns a gate that never opens into "no gate" rather
    than an endless search. A negative count is the gate's own to clamp.
    """
    return next((n for n in range(samples, samples + horizon) if gate(n)), None)


#: The freeze the learners obey: ``(reason, end)`` -- ``_learning_frozen``'s
#: answer and when it ends, ``None`` where the reason has no known end.
Freeze = tuple[str, datetime | None]


def pauses(reason: str | None) -> bool:
    """Whether a ``_learning_frozen`` reason shows the learner as ``frozen``.

    The census of every reason ``_learning_frozen`` and ``_tail_freeze`` can
    return. Shown, the reason in ``waiting_for``: the boost (``boost_space``,
    with an end where one is known), an open window (``ventilation``) and an
    unusable reading (``<problem>:<entity key>``, but not ``not_configured:``) -- each holds the learner
    until something changes, and a count that stands still hides it. Kept as
    the count: the early cut-off (one interval, gone next cycle), the
    unmetered-power freeze and an unread room (a property of the install that
    never ends, so a pause would promise a resume), and the plant states the
    heat pump itself signals (external heat, defrost, fault), which come and
    go within cycles. The reason is ``learner_freeze_reason``, the last one a
    learner recorded this cycle: the hot-water and buffer learners record
    their own probe's problem there, which holds neither fabric learner, so
    a reading on one of their probes keeps the count too.
    """
    if reason is None:
        return False
    if reason in ("boost_space", "ventilation"):
        return True
    problem, _, key = reason.partition(":")
    return bool(key) and problem != "not_configured" and key not in _OTHER_PROBES


#: The probes only the hot-water and buffer learners freeze on.
_OTHER_PROBES = frozenset((CONF_DHW_TEMP_ENTITY, CONF_BUFFER_TANK_TEMP_ENTITY))


def log_skip(clean: bool, what: str, why: str, *args: object) -> bool:
    """At DEBUG: why ``what`` took no sample this cycle; returns ``clean`` unchanged.

    The learners refuse far more often than they fold, and a count that
    stands still says nothing about which gate held it. ``why`` is a
    ``%``-format and ``args`` its values, left to the logger so that nothing
    is formatted with DEBUG off.
    """
    _LOGGER.debug("No %s sample this cycle: " + why + "%s", what, *args, "" if clean else " (the open counter span is spoiled)")
    return clean


def learner_progress(learner: LearnerInputs, frozen: Freeze | None = None) -> LearnerProgress:
    """The phase, progress, wait and (counting only) ETA of one learner.

    ``frozen``: the answer the learners obey, ``None`` when nothing holds
    them. Ranked above the weather wait, below off: a frozen learner takes
    nothing whatever the weather does.
    """
    if not learner.enabled:
        return _status("off", None, None, None, learner.samples, None)
    n = learner.samples
    # A rate of zero or below (a restore, a reset) is nothing counted.
    rate = learner.rate_per_day if (learner.rate_per_day or 0.0) > 0.0 else None
    needed = gate_count(learner.gate, n) if learner.gate is not None else None
    progress: float | None
    eta: float | None = None
    if needed is not None and needed > n:
        phase, progress = "counting", n / needed
        if rate is not None:
            eta = (needed - n) / rate
    else:
        phase = "settling"
        progress = learner.walked(n) if learner.walked is not None else None
    if frozen is not None and pauses(frozen[0]):
        until = frozen[1].isoformat() if frozen[1] is not None else None
        return _status("frozen", progress, frozen[0], None, n, needed, until)
    if learner.blocked_by is not None and rate is None:
        return _status("waiting", progress, learner.blocked_by, None, n, needed)
    return _status(phase, progress, None, eta, n, needed)


def _status(
    phase: str,
    progress: float | None,
    waiting_for: str | None,
    eta_days: float | None,
    samples: int,
    samples_needed: int | None,
    frozen_until: str | None = None,
) -> LearnerProgress:
    status: LearnerProgress = {
        "phase": phase,
        "progress": round(progress, 3) if progress is not None else None,
        "waiting_for": waiting_for,
        "eta_days": round(eta_days, 1) if eta_days is not None else None,
        "samples": int(samples),
        "samples_needed": samples_needed,
    }
    if phase == "frozen":
        status["frozen_until"] = frozen_until
    return status
