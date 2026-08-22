"""Minimal stand-in for ``homeassistant.util.dt``.

``now``/``utcnow`` are overridable so tests can freeze the clock. The golden
harness needs that: the coordinator publishes time-derived values such as
"hours until the next hot water window", and without a fixed clock every
recorded fixture would differ from every replay by however long the two runs
were apart.
"""
from datetime import datetime, timezone

# When set, both clocks return this instead of the real time.
_FROZEN: datetime | None = None


def freeze(when: datetime | None) -> None:
    """Pin the clock, or pass ``None`` to release it."""
    global _FROZEN
    _FROZEN = when


def now():
    if _FROZEN is not None:
        return _FROZEN
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
    return v
