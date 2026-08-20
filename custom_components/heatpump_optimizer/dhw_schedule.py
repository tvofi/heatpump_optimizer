"""Parsing and evaluation helpers for user-configured DHW demand windows.

A DHW demand window describes a time frame during which domestic hot water must
be available.  Outside of the configured windows there is no availability
requirement, which lets the optimizer let the tank coast and re-heat only when
electricity is cheap.

Windows are configured as a comma separated list of ``HH:MM-HH:MM`` ranges, for
example::

    06:00-08:30, 17:00-22:00

Windows may wrap around midnight (``22:00-06:00``) and are normalized/merged so
that downstream code can rely on a canonical, non-overlapping representation.
"""
from __future__ import annotations

import re

# (start_hour, end_hour) as floats in [0, 24); end may be <= start when the
# window wraps past midnight.
Window = tuple[float, float]

_TIME_RE = re.compile(r"^(\d{1,2})(?::(\d{1,2}))?$")

# Full-day window used when the user asks for "always available".
FULL_DAY: Window = (0.0, 24.0)


class DHWWindowError(ValueError):
    """Raised when a DHW window specification cannot be parsed."""


def _parse_time(token: str) -> float:
    """Parse ``HH`` or ``HH:MM`` into a float hour in [0, 24]."""
    token = token.strip()
    match = _TIME_RE.match(token)
    if not match:
        raise DHWWindowError(f"Invalid time '{token}' (expected HH:MM)")
    hour = int(match.group(1))
    minute = int(match.group(2) or 0)
    if minute >= 60:
        raise DHWWindowError(f"Invalid minute in '{token}'")
    if hour == 24 and minute == 0:
        return 24.0
    if hour > 23:
        raise DHWWindowError(f"Invalid hour in '{token}'")
    return hour + minute / 60.0


def parse_windows(spec: str | list | tuple | None) -> list[Window]:
    """Parse a DHW window specification into normalized windows.

    Returns an empty list when the specification is empty, which callers should
    interpret as "no DHW demand windows configured".

    Raises:
        DHWWindowError: if the specification is malformed.
    """
    if spec is None:
        return []

    if isinstance(spec, (list, tuple)):
        parts: list[str] = []
        for item in spec:
            if isinstance(item, (list, tuple)) and len(item) == 2:
                parts.append(f"{item[0]}-{item[1]}")
            else:
                parts.append(str(item))
        raw = ",".join(parts)
    else:
        raw = str(spec)

    raw = raw.replace(";", ",").replace("\n", ",").strip()
    if not raw:
        return []

    windows: list[Window] = []
    for chunk in raw.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        # Accept both "-" and en-dash as range separators.
        chunk = chunk.replace("\u2013", "-").replace("\u2014", "-")
        if "-" not in chunk:
            raise DHWWindowError(
                f"Invalid window '{chunk}' (expected HH:MM-HH:MM)"
            )
        start_token, _, end_token = chunk.partition("-")
        start = _parse_time(start_token)
        end = _parse_time(end_token)
        if start == end:
            # A zero-length window is meaningless; treat "00:00-00:00" as a
            # full day since that is the most likely intent.
            if start == 0.0:
                windows.append(FULL_DAY)
                continue
            raise DHWWindowError(
                f"Invalid window '{chunk}' (start and end are identical)"
            )
        windows.append((start, end))

    return _normalize(windows)


def _split_wrapping(windows: list[Window]) -> list[Window]:
    """Split midnight-wrapping windows into non-wrapping segments."""
    flat: list[Window] = []
    for start, end in windows:
        if end > start:
            flat.append((start, min(end, 24.0)))
        else:
            flat.append((start, 24.0))
            flat.append((0.0, end))
    return [(s, e) for s, e in flat if e > s]


def _normalize(windows: list[Window]) -> list[Window]:
    """Split wrapping windows, then sort and merge overlapping ranges."""
    flat = sorted(_split_wrapping(windows))
    if not flat:
        return []

    merged: list[Window] = [flat[0]]
    for start, end in flat[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end:
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))

    if len(merged) == 1 and merged[0][0] <= 0.0 and merged[0][1] >= 24.0:
        return [FULL_DAY]
    return merged


def format_windows(windows: list[Window]) -> str:
    """Render normalized windows back into the configuration string form."""

    def fmt(value: float) -> str:
        total_minutes = int(round(value * 60))
        # A window ending at the end of the day reads better as 24:00 than 00:00.
        if total_minutes != 24 * 60:
            total_minutes %= 24 * 60
        return f"{total_minutes // 60:02d}:{total_minutes % 60:02d}"

    return ", ".join(f"{fmt(s)}-{fmt(e)}" for s, e in windows)


def hour_in_windows(hour: float, windows: list[Window]) -> bool:
    """Return True when the given hour-of-day falls inside any window."""
    if not windows:
        return False
    h = hour % 24.0
    for start, end in windows:
        if start <= h < end:
            return True
        # Guard the 24:00 boundary of a full-day window.
        if end >= 24.0 and h >= start:
            return True
    return False


def overlap_fraction(
    hour_start: float, hour_end: float, windows: list[Window]
) -> float:
    """Fraction of the interval [hour_start, hour_end) covered by the windows.

    The interval is interpreted on a 24-hour clock and may wrap.
    """
    if not windows:
        return 0.0
    length = hour_end - hour_start
    if length <= 0:
        return 0.0

    covered = 0.0
    # Walk the interval in 24h-normalized segments so wrapping works.
    segments: list[tuple[float, float]] = []
    start = hour_start % 24.0
    remaining = min(length, 24.0)
    while remaining > 1e-9:
        seg_end = min(start + remaining, 24.0)
        segments.append((start, seg_end))
        remaining -= seg_end - start
        start = 0.0

    for seg_start, seg_end in segments:
        for win_start, win_end in windows:
            covered += max(
                0.0, min(seg_end, win_end) - max(seg_start, win_start)
            )

    return max(0.0, min(1.0, covered / length))


def hours_until_next_window(hour: float, windows: list[Window]) -> float | None:
    """Hours from ``hour`` until the next window starts (0.0 when inside one).

    Returns None when no windows are configured.
    """
    if not windows:
        return None
    if hour_in_windows(hour, windows):
        return 0.0
    h = hour % 24.0
    best: float | None = None
    for start, _ in windows:
        delta = (start - h) % 24.0
        if best is None or delta < best:
            best = delta
    return best


def window_bounds_for(hour: float, windows: list[Window]) -> Window | None:
    """Return the window containing ``hour``, if any."""
    if not windows:
        return None
    h = hour % 24.0
    for start, end in windows:
        if start <= h < end or (end >= 24.0 and h >= start):
            return (start, end)
    return None


def is_valid_spec(spec: str) -> bool:
    """Return True when the specification parses successfully."""
    try:
        parse_windows(spec)
    except DHWWindowError:
        return False
    return True
