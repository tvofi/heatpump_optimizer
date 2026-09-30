"""Minimal stand-in for ``homeassistant.util.dt``.

``now``/``utcnow`` are overridable so tests can freeze the clock. ``utcnow``
is aware in UTC, as upstream's is; ``now`` is aware in ``DEFAULT_TIME_ZONE``
when one is configured and in UTC when none is, as upstream's is. The golden
harness needs that: the coordinator publishes time-derived values such as
"hours until the next hot water window", and without a fixed clock every
recorded fixture would differ from every replay by however long the two runs
were apart.

``as_local`` is the identity by default — the stub predates any timezone
coverage and every fixture was recorded that way. Set ``HASTUB_TZ`` (e.g.
``Europe/Stockholm``) to make it a real conversion, which is what the DST
regression tests do; the default path must stay the identity or every
golden fixture would shift by the runner's UTC offset.
"""
import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# When set, both clocks return this instead of the real time.
_FROZEN: datetime | None = None

# Real timezone behaviour is opt-in per process, mirroring how Home
# Assistant itself carries one configured zone.
DEFAULT_TIME_ZONE = (
    ZoneInfo(os.environ["HASTUB_TZ"]) if os.environ.get("HASTUB_TZ") else None
)


def freeze(when: datetime | None) -> None:
    """Pin the clock, or pass ``None`` to release it.

    The pinned value is normalised on the way out, not stored normalised, so
    a zone set after the freeze still applies: ``now`` returns it in the
    configured zone and ``utcnow`` in UTC, whatever tzinfo it was frozen with
    (round-9 D14-s4-02: a fixed-offset freeze made both clocks return a
    ``+01:00`` datetime upstream never hands out).
    """
    global _FROZEN
    _FROZEN = when


def now():
    # A frozen value is normalised on the way out: an aware one is converted
    # into the configured zone (UTC when none is, upstream's default zone),
    # and a naive one is read as wall time in the zone, the way ``as_local``
    # reads one (round-9 D14-s4-02: a fixed-offset freeze was handed out as
    # a ``+01:00`` datetime upstream never returns).
    #
    # Aware in UTC when no zone is configured, as upstream's is (round-9
    # D1-s1-52: the stub returned a naive datetime there, which inverted the
    # naive-versus-aware verdict of every stored-stamp comparison).
    if _FROZEN is not None:
        if _FROZEN.tzinfo is not None:
            return _FROZEN.astimezone(DEFAULT_TIME_ZONE or timezone.utc)
        return _FROZEN.replace(tzinfo=DEFAULT_TIME_ZONE or timezone.utc)
    return datetime.now(DEFAULT_TIME_ZONE or timezone.utc)


def utcnow():
    if _FROZEN is not None:
        frozen = _FROZEN
        if frozen.tzinfo is None:
            frozen = frozen.replace(tzinfo=DEFAULT_TIME_ZONE or timezone.utc)
        return frozen.astimezone(timezone.utc)
    return datetime.now(timezone.utc)


def as_utc(value: datetime) -> datetime:
    """Upstream ``as_utc`` verbatim: naive is treated as UTC, aware is converted.

    Under the default identity-timezone stub both clocks are naive, and
    ``replace`` preserves the wall difference between two naive stamps --
    the same result their direct subtraction gives -- so routing the age
    seams through here changes nothing in that mode while fixing the
    shared-ZoneInfo subtraction under ``HASTUB_TZ`` (#1299).
    """
    if value.tzinfo == timezone.utc:
        return value
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def parse_datetime(v):
    try:
        return datetime.fromisoformat(v)
    except Exception:
        return None


def as_local(v):
    if DEFAULT_TIME_ZONE is None:
        return v
    if v.tzinfo is None:
        # Home Assistant treats naive datetimes as already-local.
        return v.replace(tzinfo=DEFAULT_TIME_ZONE)
    return v.astimezone(DEFAULT_TIME_ZONE)
