"""Minimal stand-in for ``homeassistant.util.dt``.

``now``/``utcnow`` are overridable so tests can freeze the clock. Both are
aware, as upstream's are: ``now`` in ``DEFAULT_TIME_ZONE`` (UTC when none is
configured, upstream's own default), ``utcnow`` in UTC. The golden
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
    # Aware always, as upstream: ``datetime.now(time_zone or
    # DEFAULT_TIME_ZONE)``, whose default zone is UTC (round-9 D1-s1-52: a
    # naive default inverted every naive-vs-aware verdict). A naive freeze is
    # read as wall time in the zone, the way ``as_local`` reads one.
    zone = DEFAULT_TIME_ZONE or timezone.utc
    if _FROZEN is not None:
        if _FROZEN.tzinfo is None:
            return _FROZEN.replace(tzinfo=zone)
        return _FROZEN.astimezone(zone)
    return datetime.now(zone)


def utcnow():
    if _FROZEN is not None:
        return now().astimezone(timezone.utc)
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
