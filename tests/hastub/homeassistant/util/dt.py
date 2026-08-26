"""Minimal stand-in for ``homeassistant.util.dt``.

``now``/``utcnow`` are overridable so tests can freeze the clock. The golden
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
    """Pin the clock, or pass ``None`` to release it."""
    global _FROZEN
    _FROZEN = when


def now():
    if _FROZEN is not None:
        return _FROZEN
    if DEFAULT_TIME_ZONE is not None:
        return datetime.now(DEFAULT_TIME_ZONE)
    return datetime.now()


def utcnow():
    if _FROZEN is not None:
        return (
            _FROZEN
            if _FROZEN.tzinfo is not None
            else _FROZEN.replace(tzinfo=timezone.utc)
        )
    return datetime.now(timezone.utc)


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
