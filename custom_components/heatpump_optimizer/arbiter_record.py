"""The pump arbiter's held record, per coordinator, and its store.

What the arbiter wrote (:class:`ArbiterState`), the power-feedback loop's
live run (:class:`FeedbackRun`), and the one persisted mapping a restart
reloads (:func:`persist`, :func:`load`). The record's readers and writers are
``pump_arbiter``'s; this module holds no decision and writes no entity.
"""

from __future__ import annotations

import asyncio
import logging
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any
from weakref import WeakKeyDictionary

from homeassistant.util import dt as dt_util

from . import draw_range, issues, pump_mode
from .const import DOMAIN
from .drift import stored_instant
from .plan_step import PLAN_STEP_MINUTES
from .store import QuarantiningStore, load_mapping

if TYPE_CHECKING:
    from .pump_arbiter import SupplyWiring

_LOGGER = logging.getLogger(__name__)

#: The v6.6.12 stand-down repair, cleared wherever a record from then loads.
ISSUE_MANUAL = "pump_manual_change"
_STORE_VERSION = 1


def log_steps() -> int:
    """One day of plan steps, the decision log's length (width owned by plan_step)."""
    return 24 * 60 // PLAN_STEP_MINUTES


@dataclass
class FeedbackRun:
    """One compressor run under the power-feedback loop; never persisted.

    A restart re-enters the start-hold, which writes today's target. The
    target ``w_c`` is kept unrounded, so a move smaller than the entity's
    step accumulates instead of rounding away.
    """

    start: datetime
    w_c: float
    seen: datetime
    #: (when, measured kW) over :data:`FEEDBACK_WINDOW`.
    samples: deque[tuple[datetime, float]] = field(default_factory=deque)
    running: bool = False
    #: The last value the loop sent that differs from today's target, and
    #: the record it replaced: the bracket ``hold`` reads a clamp cut in.
    sent_c: float | None = None
    prev_c: float | None = None
    #: Where the controller cut a loop write: the target never passes it.
    cut_lo_c: float | None = None
    cut_hi_c: float | None = None
    #: When the compressor stopped under this run (:func:`_kept`).
    stopped: datetime | None = None


@dataclass
class ArbiterState:
    """Per-coordinator record: what was written, and what did not hold."""

    #: slot -> (value written, when); the ownership record, persisted.
    written: dict[str, tuple[Any, datetime]] = field(default_factory=dict)
    #: slot -> the last write a loop move dropped from ``written`` to resend
    #: (:func:`_note_sent`), read while that record is missing, until a
    #: restore or release ends it; persisted with it. A loop run's reset
    #: keeps it. A write lands only once the off restore is armed, which
    #: :func:`_arm_space` no longer refuses, so no write needs to end it.
    dropped: dict[str, Any] = field(default_factory=dict)
    #: slot -> differing readings in a row; slot -> when a value the pump
    #: did not hold is sent again.
    misses: dict[str, int] = field(default_factory=dict)
    retry: dict[str, datetime] = field(default_factory=dict)
    step: dict[str, Any] | None = None
    log: deque[dict[str, Any]] = field(default_factory=lambda: deque(maxlen=log_steps()))
    dhw_since: datetime | None = None
    last_duty: str | None = None
    loaded: bool = False
    unsubs: list[Any] = field(default_factory=list)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    #: (step start, the supply the plan commanded for that step): written by
    #: the cycle's switch write and moved by :func:`supply_tick` (#2492).
    supply: tuple[datetime, bool] | None = None
    #: The step tick's listener and wiring; dropped only at unload, never by duty mode.
    supply_unsub: Callable[[], None] | None = None
    wiring: "SupplyWiring | None" = None
    #: The space set-point's reading when the arbiter last armed a write to
    #: it; ``None`` unknown (a restart, or the power switch read off since).
    #: A later reading that is neither this nor the write is a person's edit.
    space_before: float | None = None
    #: The power-feedback loop's live run, and the inlet-to-target gap at
    #: which a loop-lowered target stopped the compressor (:func:`_feedback`).
    feedback: FeedbackRun | None = None
    stop_gap_k: float | None = None
    #: A supply write ``supply_hold`` held back; the step tick retries it.
    supply_held: bool = False
    #: Until when (UTC) the learners freeze after ``supply_hold`` held a write.
    held_until: datetime | None = None
    #: The last Control pass on a flow set-point (:func:`_pass_record`); never persisted.
    last_pass: draw_range.PassRecord | None = None
    #: The step the action was last cut or refused for, and whether a rate
    #: limit refused its target (:func:`_step_writes`).
    step_cut: datetime | None = None
    step_pending: bool = False
    #: Held around one re-cut and its tail, by cycle and tick alike.
    tail_lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    #: GCHV night register -> its reading before the first write; persisted.
    night_before: dict[str, int] = field(default_factory=dict)
STATES: WeakKeyDictionary[Any, ArbiterState] = WeakKeyDictionary()
OWN_MODES = frozenset((pump_mode.MODE_HEAT, pump_mode.MODE_DHW, pump_mode.MODE_HEAT_DHW))
SLOTS = ("mode", "dhw_setpoint", "space_setpoint", "silent")


#: GCHV night-mode registers 518/519 as hour then minute per register (#1913).
NIGHT_KEYS = {
    "night_start_hour": "start_hour",
    "night_start_minute": "start_minute",
    "night_end_hour": "end_hour",
    "night_end_minute": "end_minute",
}


def state_for(coord: Any) -> ArbiterState:
    held = STATES.get(coord)
    if held is None:
        held = ArbiterState()
        STATES[coord] = held
    return held


def store_of(hass: Any, entry_id: str) -> QuarantiningStore[dict[str, Any]]:
    """The record's store for one config entry."""
    return QuarantiningStore(
        hass,
        _STORE_VERSION,
        f"{DOMAIN}_{entry_id}_pump_duty",
        naive_zone=dt_util.DEFAULT_TIME_ZONE,  # load's zone
    )


async def persist(held: ArbiterState, store: QuarantiningStore[dict[str, Any]]) -> None:
    """Save ``held``'s persisted slots to ``store``; a failure is logged, never raised."""
    payload = {
        "written": {k: [v, at.isoformat()] for k, (v, at) in held.written.items()},
        "dropped": dict(held.dropped),
        "night_before": dict(held.night_before),
    }
    try:
        await store.async_save(payload)
    except Exception as err:  # noqa: BLE001
        _LOGGER.debug("Could not persist the pump duty record: %s", err)


async def load(
    held: ArbiterState, open_store: Callable[[], QuarantiningStore[dict[str, Any]]], hass: Any,
) -> None:
    """Restore the ownership record once, so a restart keeps what it wrote;
    ``open_store`` is called only on that first load."""
    if held.loaded:
        return
    held.loaded = True
    raw = await load_mapping(open_store(), "the pump duty record")
    if raw is None:
        return
    if raw.get("manual"):
        issues.clear_issue(hass, ISSUE_MANUAL)
    written = raw.get("written")
    for slot, pair in written.items() if isinstance(written, dict) else ():
        try:
            value, at = pair[0], stored_instant(pair[1], dt_util.DEFAULT_TIME_ZONE)
        except (TypeError, KeyError, IndexError):
            continue
        if at is not None and writable(slot, value):
            held.written[slot] = (value, at)
    held.dropped = _restored(raw.get("dropped"), (*SLOTS, *NIGHT_KEYS))
    held.night_before = _restored(raw.get("night_before"), NIGHT_KEYS)


def _restored(raw: Any, slots: Any) -> dict[str, Any]:
    """A stored slot map, each entry one the arbiter could have written to a slot of ``slots``."""
    return {k: v for k, v in raw.items() if k in slots and writable(k, v)} if isinstance(raw, dict) else {}


def writable(slot: str, value: Any) -> bool:
    """Whether ``value`` is one the arbiter could have written to ``slot``.

    A restored record is compared and rewritten on every pass, so one of any
    other shape raised there on every cycle (D1-s3-03).
    """
    if slot == "mode":
        return isinstance(value, str) and value in OWN_MODES
    if slot == "silent":
        return value is True or value is False
    if slot in NIGHT_KEYS:
        return isinstance(value, int) and not isinstance(value, bool)
    return slot in SLOTS and isinstance(value, (int, float)) and not isinstance(value, bool)
