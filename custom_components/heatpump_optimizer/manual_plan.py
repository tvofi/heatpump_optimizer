"""Manual plan override: pinning *when* the heat pump actually runs.

The optimizer decides both *whether* to run each channel and *how hard*. The
apply_schedule service only ever changed the comfort/demand envelope and let
the optimizer keep re-deciding inside it, which is the opposite of what a user
who has hand-arranged their day wants: they want the chosen slots to stick.

This module is the data model behind that. It parses the slot lists a user (or
the dashboard card) supplies, decides for any horizon step whether that step is
pinned on, pinned off, or left free, and round-trips to a plain dict for
persistence. It is deliberately free of any Home Assistant import so it can be
unit-tested on its own and so the awkward parts — the omitted-vs-empty
distinction and the expiry boundary — are exercised without a running hass.

Three things carry subtle intent and are worth stating once here:

* A channel given as ``None`` means "leave this fully automatic"; a channel
  given as an explicit empty list means "off for the whole override period".
  Those are different instructions and are kept different all the way through.
* The override controls timing only. Whether a pinned-on step runs *hard* is
  still the optimizer's call, and whether a pinned-off step is *released* for
  safety is decided later against the solved trajectory — not here.
* Everything past ``expires_at`` is automatic again, so a plan applied in the
  evening cannot quietly keep forcing the pump the next afternoon.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

# Pin encoding shared with the optimizer's bounds construction. The optimizer
# reads a per-step float array as: NaN -> free to be chosen, 0 -> forced off,
# 1 -> forced on. Floats (rather than an enum) so a whole channel is a single
# numpy-friendly array the solver bounds can be built from directly.
PIN_FREE = float("nan")
PIN_OFF = 0.0
PIN_ON = 1.0

#: The two channels a manual plan can pin, in the order the response reports.
CHANNEL_SPACE = "space"
CHANNEL_DHW = "dhw"

Slot = tuple[datetime, datetime]


class ManualPlanError(ValueError):
    """A manual plan could not be parsed or is internally inconsistent.

    A plain ``ValueError`` subclass on purpose: this module stays Home
    Assistant-free, so the service layer is what turns this into the
    ``ServiceValidationError`` the user actually sees.
    """


def _coerce_awareness(value: datetime, reference: datetime) -> datetime:
    """Return ``value`` made comparable with ``reference``.

    Home Assistant hands out timezone-aware local times, but slots may arrive
    as either aware ISO strings or, in tests, naive datetimes. Comparing across
    the two raises ``TypeError``, so both are brought onto the reference's
    footing rather than left to blow up deep inside an ordering check.
    """
    if reference.tzinfo is None:
        if value.tzinfo is not None:
            # Express the instant in local wall time, then drop the offset to
            # match a naive reference.
            return value.astimezone().replace(tzinfo=None)
        return value
    if value.tzinfo is None:
        return value.replace(tzinfo=reference.tzinfo)
    return value


def _parse_dt(value: Any, reference: datetime) -> datetime:
    """Parse one ISO 8601 datetime, raising ManualPlanError on anything else."""
    if isinstance(value, datetime):
        return _coerce_awareness(value, reference)
    if not isinstance(value, str):
        raise ManualPlanError(f"expected an ISO 8601 datetime, got {value!r}")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as err:
        raise ManualPlanError(f"could not parse datetime {value!r}: {err}") from err
    return _coerce_awareness(parsed, reference)


def parse_channel(raw: Any, reference: datetime) -> list[Slot] | None:
    """Parse and validate one channel's slots.

    ``None`` is returned unchanged to preserve "leave automatic"; an empty list
    stays an empty list to preserve "off for the whole period". Everything else
    must be a list of ``{"start": ..., "end": ...}`` objects with parseable
    datetimes, each ``end`` strictly after its ``start``, and no two slots
    overlapping. The returned slots are sorted by start time so downstream code
    never has to re-sort.
    """
    if raw is None:
        return None
    if not isinstance(raw, (list, tuple)):
        raise ManualPlanError(
            "slots must be a list of {start, end} objects or omitted entirely"
        )

    slots: list[Slot] = []
    for item in raw:
        if not isinstance(item, dict) or "start" not in item or "end" not in item:
            raise ManualPlanError(
                f"each slot must be an object with 'start' and 'end', got {item!r}"
            )
        start = _parse_dt(item["start"], reference)
        end = _parse_dt(item["end"], reference)
        if end <= start:
            raise ManualPlanError(
                f"slot end {item['end']!r} is not after its start {item['start']!r}"
            )
        slots.append((start, end))

    slots.sort(key=lambda s: s[0])
    for (prev_start, prev_end), (next_start, _next_end) in zip(slots, slots[1:]):
        if next_start < prev_end:
            raise ManualPlanError(
                "slots overlap: "
                f"{prev_start.isoformat()}–{prev_end.isoformat()} and "
                f"{next_start.isoformat()} onwards"
            )
    return slots


def _slots_to_payload(slots: list[Slot] | None) -> list[dict[str, str]] | None:
    if slots is None:
        return None
    return [{"start": s.isoformat(), "end": e.isoformat()} for s, e in slots]


@dataclass
class ManualOverride:
    """A hand-arranged plan in force until ``expires_at``.

    ``space_slots`` / ``dhw_slots`` follow the omitted-vs-empty rule: ``None``
    leaves the channel automatic, ``[]`` forces it off for the whole period.
    ``released_*`` are populated after a solve to record which forced-off steps
    safety had to override, purely so the UI can show it; they are never
    persisted because they are re-derived on every solve.
    """

    space_slots: list[Slot] | None
    dhw_slots: list[Slot] | None
    expires_at: datetime
    created_at: datetime | None = None
    #: Per-channel step indices whose "off" pin was released for safety, with
    #: the reason. Transient: set by the coordinator after each solve.
    released_space: list[dict[str, Any]] = field(default_factory=list)
    released_dhw: list[dict[str, Any]] = field(default_factory=list)

    def slots_for(self, channel: str) -> list[Slot] | None:
        return self.space_slots if channel == CHANNEL_SPACE else self.dhw_slots

    def is_expired(self, now: datetime) -> bool:
        """Whether the override no longer applies as of ``now``."""
        return _coerce_awareness(now, self.expires_at) >= self.expires_at

    def channel_pins(
        self, channel: str, step_starts: list[datetime]
    ) -> list[float] | None:
        """Per-step pin values for one channel, or ``None`` when automatic.

        A step is pinned on when its start instant falls inside one of the
        channel's slots, pinned off when it does not, and left free once it is
        at or beyond the expiry — so the override reaches exactly as far into
        the horizon as it was asked to and no further.
        """
        slots = self.slots_for(channel)
        if slots is None:
            return None
        pins: list[float] = []
        for ts in step_starts:
            ref = _coerce_awareness(ts, self.expires_at)
            if ref >= self.expires_at:
                pins.append(PIN_FREE)
                continue
            in_slot = any(start <= ref < end for start, end in slots)
            pins.append(PIN_ON if in_slot else PIN_OFF)
        return pins

    def pinned_step_count(self, channel: str, step_starts: list[datetime]) -> int:
        """How many horizon steps this channel forces on."""
        pins = self.channel_pins(channel, step_starts)
        if pins is None:
            return 0
        return sum(1 for p in pins if p == PIN_ON)

    def normalized_slots(self, channel: str) -> list[dict[str, str]] | None:
        return _slots_to_payload(self.slots_for(channel))

    def to_dict(self) -> dict[str, Any]:
        """Serialise for persistence. Released steps are intentionally left out."""
        return {
            "space_slots": _slots_to_payload(self.space_slots),
            "dhw_slots": _slots_to_payload(self.dhw_slots),
            "expires_at": self.expires_at.isoformat(),
            "created_at": (
                self.created_at.isoformat() if self.created_at is not None else None
            ),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ManualOverride":
        """Rebuild from :meth:`to_dict`, raising ManualPlanError on bad data.

        The expiry parses without a reference clock; the slots are then parsed
        against that expiry so their awareness matches, which is all that a
        later ``is_expired`` / ``channel_pins`` comparison needs.
        """
        raw_expiry = data.get("expires_at")
        if not isinstance(raw_expiry, str):
            raise ManualPlanError("stored override has no expiry")
        try:
            expires_at = datetime.fromisoformat(raw_expiry)
        except ValueError as err:
            raise ManualPlanError(f"bad stored expiry {raw_expiry!r}") from err

        space_slots = parse_channel(data.get("space_slots"), expires_at)
        dhw_slots = parse_channel(data.get("dhw_slots"), expires_at)
        created_at = None
        raw_created = data.get("created_at")
        if isinstance(raw_created, str):
            try:
                created_at = datetime.fromisoformat(raw_created)
            except ValueError:
                created_at = None
        return cls(
            space_slots=space_slots,
            dhw_slots=dhw_slots,
            expires_at=expires_at,
            created_at=created_at,
        )


def build_override(
    *,
    dhw_slots: Any,
    space_slots: Any,
    expires_at: datetime,
    now: datetime,
) -> ManualOverride:
    """Validate raw service input into a :class:`ManualOverride`.

    Raises :class:`ManualPlanError` for any bad slot, an expiry in the past, or
    an expiry that will not outlast the moment it is applied — so a rejected
    call never reaches the point of replacing whatever override is in force.
    """
    # Coerce once, towards `now`, and keep the coerced value. Coercing each
    # operand towards the other gives them *opposite* awareness when only one
    # side is naive, and comparing those raises TypeError -- which is not a
    # ManualPlanError, so it escapes the service handler as an opaque crash.
    # A tz-less `expires_at` is exactly what the service UI's free-text field
    # produces, so this is the ordinary case, not a corner one.
    expires_ref = _coerce_awareness(expires_at, now)
    if expires_ref <= now:
        raise ManualPlanError(
            f"expires_at {expires_at.isoformat()} is not in the future"
        )
    space = parse_channel(space_slots, now)
    dhw = parse_channel(dhw_slots, now)
    return ManualOverride(
        space_slots=space,
        dhw_slots=dhw,
        # The coerced expiry, so it can be compared with the slots -- which were
        # parsed against `now` -- without raising on every coordinator refresh.
        expires_at=expires_ref,
        created_at=now,
    )
