"""Parsing and evaluation helpers for user-configured DHW demand windows.

A DHW demand window describes a time frame during which domestic hot water must
be available.  Outside of the configured windows there is no availability
requirement, which lets the optimizer let the tank coast and re-heat only when
electricity is cheap.

Windows are configured as a comma (or semicolon) separated list of
``HH:MM-HH:MM`` ranges, for example::

    06:00-08:30, 17:00-22:00

Windows may wrap around midnight (``22:00-06:00``) and are normalized/merged so
that downstream code can rely on a canonical, non-overlapping representation.

**Weekly windows.** A range may carry a day selector prefix, so different days
get different windows (owner request: weekdays vs weekend, or one specific
weekday)::

    weekdays 06:00-08:30, weekend 08:00-09:30
    Mo 05:30-07:00, Tu-Fr 06:00-08:00, Sa,Su 08:00-09:30

A day selector is one of: ``daily`` (the default when absent), ``weekdays``
(Monday–Friday), ``weekend`` (Saturday–Sunday), or a comma/range list of
two-letter day tokens ``Mo Tu We Th Fr Sa Su``. A range without a selector
applies to all seven days, which is exactly the previous behaviour — the flat
spec ``06:00-08:30`` and ``daily 06:00-08:30`` mean the same thing, and an
existing configuration loads unchanged. Later segments for the same day
accumulate (``Mo 06:00-07:00, Mo 18:00-19:00`` is Monday with two windows),
mirroring how the flat grammar treats ``06:00-07:00, 18:00-19:00``.

**One grammar, and it is this one.** The segment separator and the day-list
separator are the same comma, so a spec can only be split by a reader that
knows about day selectors. ``_segments`` is that reader and BOTH parsers use
it, so ``parse_windows`` (the every-day view) and ``parse_weekly_windows``
(the per-day view) accept exactly the same strings and differ only in what
they return. ``format_weekly_windows`` writes in that grammar and nothing
else -- one selector per range, never a bare range trailing a selectored one,
because a bare range means all seven days. Together those give the invariant
this module is expected to hold: anything the renderer emits is read back to
the same schedule by every loader production runs on a stored spec
(``parse_windows``, ``parse_weekly_windows``, ``is_valid_spec``,
``spec_problem``). ``tests/features.py`` enumerates it over all 127 non-empty
day-sets rather than by example (#329, #321).
"""
from __future__ import annotations

import re

# (start_hour, end_hour) as floats in [0, 24); end may be <= start when the
# window wraps past midnight.
Window = tuple[float, float]

_TIME_RE = re.compile(r"^(\d{1,2})(?::(\d{1,2}))?$")

# Full-day window used when the user asks for "always available".
FULL_DAY: Window = (0.0, 24.0)

#: Two-letter day tokens, Monday-first to match ``datetime.weekday()``.
_DAY_TOKENS = ("mo", "tu", "we", "th", "fr", "sa", "su")

_DAY_SELECTOR_RE = re.compile(
    r"^(?P<days>[A-Za-z]{2}(?:\s*(?:-|,)\s*[A-Za-z]{2})*)$"
)


class DHWWindowError(ValueError):
    """Raised when a DHW window specification cannot be parsed."""


def _parse_day_selector(token: str) -> list[int]:
    """A day-selector token into the weekday indices it names.

    ``weekdays``/``weekend``/``daily`` name their obvious sets; otherwise the
    token is one or more two-letter day names joined by ``-`` (a contiguous
    range, wrapping Sa-Mo if asked) or ``,`` (a list). Monday-first indices,
    matching ``datetime.weekday()``.
    """
    t = token.strip().lower()
    if t in ("daily", "everyday", "all"):
        return list(range(7))
    # Case-insensitive tokens: selectors are typed by humans.
    if t == "weekdays":
        return [0, 1, 2, 3, 4]
    if t in ("weekend", "weekends"):
        return [5, 6]
    m = _DAY_SELECTOR_RE.match(t)
    if not m:
        return []
    days: list[int] = []
    t = re.sub(r"\s+", "", t)
    parts = re.split(r"-", t)
    if len(parts) == 2:
        try:
            lo = _DAY_TOKENS.index(parts[0])
            hi = _DAY_TOKENS.index(parts[1])
        except ValueError:
            return []
        span = (hi - lo) % 7 + 1
        days = [(lo + k) % 7 for k in range(span)]
        return sorted(days)
    for part in t.split(","):
        try:
            days.append(_DAY_TOKENS.index(part))
        except ValueError:
            return []
    return sorted(set(days))


def _format_day_selector(days: list[int]) -> str:
    """Render a weekday set back as a selector token, or "" for all seven."""
    if len(days) == 7:
        return "daily"
    ordered = sorted(set(days))
    if ordered == [0, 1, 2, 3, 4]:
        return "weekdays"
    if ordered == [5, 6]:
        return "weekend"
    # Contiguous runs (possibly wrapping) render as ranges; anything else
    # as a comma list. Ranges keep the rendered spec short, which is the
    # point of rendering back at all.
    for lo in ordered:
        span = len(ordered)
        run = [(lo + k) % 7 for k in range(span)]
        if sorted(run) == ordered:
            hi = run[-1]
            if span >= 3:
                return f"{_DAY_TOKENS[lo].capitalize()}-{_DAY_TOKENS[hi].capitalize()}"
            break
    return ",".join(_DAY_TOKENS[d].capitalize() for d in ordered)


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
    return _normalize(_raw_windows(spec))


def _spec_text(spec: str | list | tuple) -> str:
    """A spec of any accepted shape as one normalised string.

    Lists and tuples are joined with the same comma the string form uses, and
    the alternative separators (``;``, newline) become that comma too. Shared
    by both parsers so neither can be looking at a different string.
    """
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
    return raw.replace(";", ",").replace("\n", ",").strip()


def _segments(raw: str) -> list[str]:
    """The spec's segments: commas split them, except inside a day selector.

    The comma is both the segment separator and, inside a day selector
    (``Sa,Su 08:00-09:30``), the day-list separator. A chunk with no digits
    that parses as day names is therefore a CONTINUATION of the next chunk's
    selector, not a segment of its own: reassemble before parsing.

    THE one segmenter, for both parsers (#329/#321). It used to live only in
    ``parse_weekly_windows`` while ``_raw_windows`` split on every comma, so
    the two grammars disagreed on exactly the comma-list selectors
    ``_format_day_selector`` prefers -- 90 of the 127 non-empty day-sets. The
    renderer emitted what its own first loader rejected, and a canonicalised
    weekly schedule came back as a WARNING and no schedule at all.
    """
    segments: list[str] = []
    pending_selector = ""
    for chunk in raw.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if not re.search(r"\d", chunk) and _parse_day_selector(chunk):
            pending_selector = (
                f"{pending_selector},{chunk}" if pending_selector else chunk
            )
            continue
        if pending_selector:
            chunk = f"{pending_selector},{chunk}"
            pending_selector = ""
        segments.append(chunk)
    if pending_selector:
        # A selector with no range after it: "weekdays" alone names days
        # and gives them no times, which is almost certainly a truncated
        # edit rather than intent. Refuse it with the text the user typed.
        raise DHWWindowError(
            f"Day selector '{pending_selector}' has no time window "
            f"(expected e.g. 'weekdays 06:00-08:30')"
        )
    return segments


def _raw_windows(spec: str | list | tuple | None) -> list[Window]:
    """The windows exactly as written, one per range, before normalisation.

    ``spec_problem`` judges each range on its own: normalisation merges an
    overlapping one-minute range into its neighbour, and a range that has
    been merged away can no longer be refused.
    """
    if spec is None:
        return []

    raw = _spec_text(spec)
    if not raw:
        return []

    windows: list[Window] = []
    for chunk in _segments(raw):
        windows.extend(_parse_one_range(chunk))
    return windows


def _parse_one_range(chunk: str) -> list[Window]:
    """One ``[days ]HH:MM-HH:MM`` range into its window list.

    The day selector is accepted and IGNORED here -- ``parse_windows`` is the
    every-day view, and a day-prefixed spec means "these times, on those
    days"; the every-day view keeps the times so nothing downstream breaks
    on a weekly spec it has not been taught about. The weekly structure is
    ``parse_weekly_windows``'s job.
    """
    chunk = chunk.strip()
    # Accept both "-" and en/em-dash as range separators.
    chunk = chunk.replace("\u2013", "-").replace("\u2014", "-")
    # A leading day selector ("weekdays 06:00-08:30") ends at the first
    # digit: selectors are letters/commas/dashes only.
    m = re.match(r"^([A-Za-z][A-Za-z,\s-]*?)\s+(?=\d)", chunk)
    if m and _parse_day_selector(m.group(1)):
        chunk = chunk[m.end():]
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
            return [FULL_DAY]
        raise DHWWindowError(
            f"Invalid window '{chunk}' (start and end are identical)"
        )
    return [(start, end)]


def parse_weekly_windows(
    spec: str | list | tuple | None,
) -> list[list[Window]] | None:
    """Parse a possibly day-aware window spec into seven day window lists.

    Returns ``None`` when the spec is the plain every-day form (no day
    selectors) -- the caller keeps using ``parse_windows`` and today's
    behaviour is exactly yesterday's. Otherwise returns a Monday-first list
    of seven window lists; a day with no segment gets an empty list, which
    downstream reads as "no requirement that day".

    Raises ``DHWWindowError`` with the offending segment named, so the
    config flow can put the error on the field a user is staring at.
    """
    if spec is None:
        return None
    raw = _spec_text(spec)
    if not raw:
        return None

    weekly: list[list[Window]] | None = None
    for chunk in _segments(raw):
        chunk = chunk.replace("\u2013", "-").replace("\u2014", "-")
        days = list(range(7))
        m = re.match(r"^([A-Za-z][A-Za-z,\s-]*?)\s+(?=\d)", chunk)
        if m:
            selected = _parse_day_selector(m.group(1))
            if selected:
                days = selected
                chunk = chunk[m.end():]
            # An unparsable leading token is not a selector and will fail
            # as a time below, with the user's own text in the message.
        wins = _parse_one_range(chunk)
        if days != list(range(7)):
            if weekly is None:
                weekly = [[] for _ in range(7)]
            for d in days:
                weekly[d].extend(wins)
        elif weekly is not None:
            # A dayless segment in a weekly spec applies to every day:
            # "weekdays 06-07, 17-22" gives weekdays both, all days the
            # second -- the same reading the flat grammar gives.
            for day in weekly:
                day.extend(wins)
    if weekly is None:
        return None
    return [_normalize(day) for day in weekly]


def format_weekly_windows(weekly: list[list[Window]]) -> str:
    """Render a seven-day window structure back into the spec grammar.

    Days with identical window sets render once under a combined selector,
    so the common weekday/weekend pair stays the two-segment string the
    user typed; the rendering is canonical, not echo.
    """
    by_windows: dict[tuple[Window, ...], list[int]] = {}
    for d, day in enumerate(weekly):
        by_windows.setdefault(tuple(day), []).append(d)
    # Empty days render as their own group only when some day is non-empty;
    # an all-empty schedule renders as the empty string.
    segments: list[str] = []
    for wins, days in sorted(
        by_windows.items(), key=lambda kv: (not kv[0], kv[1][0])
    ):
        if not wins:
            continue
        selector = _format_day_selector(days)
        if selector == "daily":
            segments.append(format_windows(list(wins)))
            continue
        # One selector per RANGE, not one per group. The grammar reads a
        # range with no selector as applying to all seven days, so a group's
        # second and later ranges must not be left bare: "Mo 06:00-08:30,
        # 17:00-22:00" handed every other day Monday's evening window on the
        # way back in (#329). Repeating the selector is exactly equivalent --
        # later segments for the same day accumulate -- and it is the only
        # form of a multi-range group that survives its own parser.
        segments.extend(f"{selector} {format_windows([w])}" for w in wins)
    return ", ".join(segments)


def windows_for_day(
    weekly: list[list[Window]] | None, weekday: int, fallback: list[Window]
) -> list[Window]:
    """The window list in force on one weekday.

    ``fallback`` is the flat/every-day set from ``parse_windows``, used when
    no weekly structure exists; it is also what a ``None`` weekday (a caller
    with an hour but no date) gets, so hour-only consumers are untouched by
    the whole feature.
    """
    if weekly is None or weekday is None:
        return fallback
    return weekly[max(0, min(6, int(weekday)))]


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


def is_valid_spec(spec: str) -> bool:
    """Return True when the specification parses successfully."""
    try:
        parse_windows(spec)
    except DHWWindowError:
        return False
    return True


#: The shortest window the config flow accepts, in minutes: one planning
#: step. The optimizer plans on a 15-minute grid and tests window membership
#: at each step's start (``hour_in_windows``), so a window shorter than a
#: step can sit between two starts and bind nothing at all -- "06:05-06:06"
#: was accepted and then changed no plan (audit D4-08, #171). Kept equal to
#: ``OptimizationConfig.time_step_minutes``; tests/entities.py pins the two
#: together, since this module cannot import the optimizer.
MIN_WINDOW_MINUTES = 15

#: The config flow's error keys, translated in strings.json under both
#: flows' ``error`` sections. Named here, next to the verdict that returns
#: them, the way ``comfort_band`` names its codes.
ERROR_INVALID = "invalid_dhw_windows"
ERROR_TOO_SHORT = "dhw_window_too_short"


def window_minutes(window: Window) -> float:
    """A window's length in minutes, measured through midnight when it wraps."""
    start, end = window
    hours = end - start if end > start else end + 24.0 - start
    # The grammar is minute-resolution; rounding keeps "06:05-06:20" at
    # exactly 15 rather than at whatever the float subtraction landed on.
    return float(round(hours * 60.0))


def spec_problem(spec: str) -> str | None:
    """The config flow's verdict on a window spec: an error key, or None.

    Stricter than ``parse_windows`` on purpose, and separate from it: the
    parser must stay permissive so a stored spec keeps loading whatever this
    version thinks of it, while the form is where the typo happens and where
    it can still be corrected.
    """
    try:
        windows = _raw_windows(spec)
    except DHWWindowError:
        return ERROR_INVALID
    if any(window_minutes(w) < MIN_WINDOW_MINUTES for w in windows):
        return ERROR_TOO_SHORT
    return None
