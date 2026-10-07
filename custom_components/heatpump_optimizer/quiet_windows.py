"""The user's quiet windows: silent and off, on the plan (#1910).

Distinct from :mod:`silent_mode`, which models the pump's OWN night-mode
schedule -- a fact about the hardware the plan must respect. These windows
are the user's wish about noise: rows that say "run silently here" (the
compressor capped, the plan buying the hours the cap makes cheap) and rows
that say "plan nothing here" (no space heating and no hot-water slots in the
window, tvofi's decision D1 of 2026-09-30: an Off window means solely that,
with nothing extra written -- those steps are ordinary idle steps).

Two option keys, one spec per action, both in the unchanged
``dhw_schedule`` grammar; the fraction a silent row keeps is the existing
``silent_mode_power_fraction``. Four properties are the contract, and
``tests/features.py`` pins each:

* **Inert when unset.** No rows, an unreadable stored spec, or the whole
  horizon meeting no window returns ``None`` everywhere, and ``compose``
  hands the caller's ceiling back as the same object. An install that sets
  nothing plans bit for bit as before, and every value-bearing golden stays
  byte-identical.
* **Floored where silent, zero where off.** A silent step caps electrical
  power at ``max(fraction, CAPACITY_FLOOR_FRACTION) * p_max`` -- the same
  floor as the pump's own schedule and the capacity envelope, so a derate
  can trim the plan but never starve the house. An off step is a deliberate
  zero and is NOT floored: the plan pre-heats before it and the soft comfort
  penalty prices any shortfall through the published breach figures.
* **The solver's clock.** Steps are walked in UTC through the optimizer's
  ``_utc_step_starts`` and read in the step's own zone, so a window binds
  the real hours on a DST night.
* **Enforced only where enforceable.** Nothing while the optimizer is off
  (D2: switching it off inside a window undoes nothing). A silent row needs
  a control the optimizer can hold, which today is the capacity-limited slot
  being a ``switch`` -- decided from the entity ID's domain alone, so a
  switch that has not reported yet (state ``unknown``; many Tuya forks
  transmit on change only) is still a usable control: unknown is not off.
  Where a silent row cannot be enforced the plan is not capped for it and
  ``compose`` says so, so the card and one repair issue can say it too.

Where the capacity figure comes from (tvofi, 2026-10-04): a measured figure
is preferred over the configured fraction -- a heat-pump power entity (W or
kW) supplies the in-window ceiling directly, else a compressor-frequency
reading scales nameplate by ``hz / hz_max`` -- and the configured fraction
is used exactly as configured otherwise, including 1.0 meaning "rows shown,
nothing capped".

Kept free of Home Assistant imports so it can be unit-tested directly, like
``dhw_schedule`` and ``silent_mode``; hass state arrives as a ``get_state``
callable.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta, time
from typing import Any, Final

import numpy as np

from . import freq_control
from .const import (
    CAPACITY_FLOOR_FRACTION,
    CONF_COMPRESSOR_FREQ_ENTITY,
    CONF_COMPRESSOR_FREQ_MAX_HZ,
    CONF_COMPRESSOR_FREQ_MIN_HZ,
    CONF_COMPRESSOR_FREQ_SENSOR,
    CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY,
    CONF_POWER_ENTITY,
    CONF_QUIET_OFF_WINDOWS,
    CONF_QUIET_SILENT_WINDOWS,
    CONF_SILENT_MODE_FRACTION,
    DEFAULT_COMPRESSOR_FREQ_MAX_HZ,
    DEFAULT_COMPRESSOR_FREQ_MIN_HZ,
    DEFAULT_SILENT_MODE_FRACTION,
)
from .dhw_schedule import (
    DHWWindowError,
    Window,
    hour_in_windows,
    parse_weekly_windows,
    parse_windows,
    windows_for_day,
)
from .inputs import normalize_power_kw
from .modbus_prefill import night_mode_write_ids, package_prefix
from .optimizer import _utc_step_starts

#: The per-step action codes, as one int8 array element per step.
ACTION_NONE: Final = 0
ACTION_SILENT: Final = 1
ACTION_OFF: Final = 2

_DAY_NAMES: Final = (
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
    "Saturday", "Sunday",
)


@dataclass(frozen=True)
class QuietCompose:
    """What quiet windows did to one solve's limits.

    ``caps`` is the electrical ceiling after the silent windows folded in
    (``None`` and the caller's own object unchanged when they cap nothing);
    off steps are NOT expressed here -- a zero entry would collapse the
    DHW planner's horizon-minimum run cap, so off rides ``off_steps`` and
    the space-heating caps array instead. ``actions`` is the resolved
    per-step action array for publication; ``silent_dropped`` says silent
    rows existed and were not enforceable, which is the card's "not
    enforced" marker and the repair issue's trigger.
    """

    caps: np.ndarray | None
    off_steps: np.ndarray | None
    actions: np.ndarray | None
    silent_dropped: bool


def step_actions(
    start_time: datetime,
    n_steps: int,
    dt_hours: float,
    silent_spec: str | None,
    off_spec: str | None,
) -> np.ndarray | None:
    """The per-step action array (``ACTION_*`` codes), or ``None``.

    ``None`` when neither spec names a window the horizon reaches, so the
    solve's limits stay free of an array nobody reads. A step inside both
    specs resolves to off -- the specs may not overlap (``overlap_problem``
    refuses it at save), so this can only arrive from a hand-edited store,
    and refusing to plan in the window is the safe reading.
    """
    if n_steps <= 0:
        return None
    parsed = _parse_spec_pair(silent_spec, off_spec)
    if parsed is None:
        return None
    (s_win, s_weekly), (o_win, o_weekly) = parsed
    out = np.full(n_steps, ACTION_NONE, dtype=np.int8)
    for i, step in enumerate(
        _utc_step_starts(start_time, n_steps, timedelta(hours=dt_hours))
    ):
        hour = step.hour + step.minute / 60.0
        day = step.weekday()
        if hour_in_windows(hour, windows_for_day(o_weekly, day, o_win)):
            out[i] = ACTION_OFF
        elif hour_in_windows(
            hour, windows_for_day(s_weekly, day, s_win)
        ):
            out[i] = ACTION_SILENT
    return out if bool(np.any(out)) else None


def silent_control_usable(entity_id: Any) -> bool:
    """Whether the optimizer can hold a silent window through ``entity_id``.

    True exactly when the configured capacity-limited slot is a ``switch``:
    the Tuya night/mute switches. A ``binary_sensor`` (GCHV's read-only
    flag) cannot be written, so those installs fall to SW-4's schedule
    registers. Decided from the entity ID's domain and NEVER from the
    state: a switch that has not reported yet reads ``unknown`` -- unknown
    is not off -- and the gate must not drop the window for a silence that
    is only the device transmitting on change.
    """
    if not isinstance(entity_id, str) or "." not in entity_id:
        return False
    return entity_id.split(".", 1)[0].strip().lower() == "switch"


def gchv_schedule_ready(
    config: Mapping[str, Any], get_state: Callable[[str], Any] | None
) -> bool:
    """Whether the GCHV night-mode numbers can hold a silent window.

    The capacity-limited slot must be register 68's flag (so the prefix
    resolves) and all four hour/minute numbers must be present. The flag's
    on/off state is not a control -- the package has no silent on/off
    register -- and is not consulted.
    """
    if get_state is None:
        return False
    prefix = package_prefix(config.get(CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY))
    if not prefix:
        return False
    return all(get_state(eid) is not None for eid in night_mode_write_ids(prefix).values())


def gchv_fits_pump(spec: str | None) -> bool:
    """Whether ``spec`` is one daily window the same every day.

    Registers 518/519 hold one start/end pair for every day. Two windows
    on one day, or days that differ, cannot be stored; the next window is
    still written and the rest are marked not enforced (#1913).
    """
    days = _gchv_days(spec)
    if days is None or any(len(day) != 1 for day in days):
        return False
    first = days[0][0]
    return all(day[0] == first for day in days)


def next_gchv_window(
    now: datetime, spec: str | None
) -> tuple[float, float] | None:
    """The next GCHV window's start/end hours (wraps as start > end).

    A wrapping 22:00-06:00 is one window, even though the DHW grammar
    splits it at midnight. A window that has already started and not yet
    ended is the next one -- the pump should already be holding it.
    """
    days = _gchv_days(spec)
    if days is None:
        return None
    tz = now.tzinfo
    yesterday = now.date() - timedelta(days=1)
    for start, end in days[yesterday.weekday()]:
        if start < end:
            continue
        begin = _gchv_at(yesterday, start, tz)
        finish = _gchv_at(now.date(), end, tz)
        if now < finish:
            if now >= begin:
                return (start, end)
    for offset in range(8):
        day = now.date() + timedelta(days=offset)
        for start, end in days[day.weekday()]:
            begin = _gchv_at(day, start, tz)
            finish = (
                _gchv_at(day, end, tz) if start < end
                else _gchv_at(day + timedelta(days=1), end, tz)
            )
            if now < finish:
                return (start, end)
    return None


def silent_unenforceable(
    config: Mapping[str, Any], get_state: Callable[[str], Any] | None = None
) -> bool:
    """True when silent rows are configured and cannot be fully held.

    A switch control is fully holdable from its entity-id domain alone.
    A GCHV schedule is fully holdable only when the four numbers resolve
    and the spec is one daily window the same every day.
    """
    spec = config.get(CONF_QUIET_SILENT_WINDOWS)
    if not spec:
        return False
    if silent_control_usable(config.get(CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY)):
        return False
    return not (gchv_schedule_ready(config, get_state) and gchv_fits_pump(spec))


def _gchv_days(spec: str | None) -> list[list[tuple[float, float]]] | None:
    """Per weekday, GCHV windows with midnight wraps merged back together."""
    parsed = _parse_spec_pair(spec, None)
    if parsed is None:
        return None
    (win, weekly), _unused = parsed
    return [_gchv_merge(windows_for_day(weekly, day, win)) for day in range(7)]


def _gchv_merge(segments: list[Window]) -> list[tuple[float, float]]:
    """Rejoin a midnight wrap the DHW normaliser split into two segments."""
    if not segments:
        return []
    segs = list(segments)
    wrap: tuple[float, float] | None = None
    if len(segs) >= 2 and segs[0][0] <= 0.0 and segs[-1][1] >= 24.0:
        wrap = (segs[-1][0], segs[0][1])
        segs = segs[1:-1]
    out = list(segs)
    if wrap is not None:
        out.append(wrap)
    return out


def _gchv_at(day: Any, hour: float, tz: Any) -> datetime:
    """``day`` at ``hour`` (hours past midnight) in ``tz``."""
    minutes = int(round(hour * 60.0)) % (24 * 60)
    return datetime.combine(day, time(minutes // 60, minutes % 60), tzinfo=tz)


def _silent_plan_spec(
    config: Mapping[str, Any],
    get_state: Callable[[str], Any] | None,
    start_time: datetime,
    silent_spec: Any,
) -> tuple[str | None, bool]:
    """The silent spec the plan should cap, and whether any row is dropped.

    A GCHV install that needs more than one daily window still caps the
    next window (what the pump will hold) and marks the rest not enforced.
    """
    if not silent_spec:
        return None, False
    spec = str(silent_spec)
    if silent_control_usable(config.get(CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY)):
        return spec, False
    if not gchv_schedule_ready(config, get_state):
        return None, True
    if gchv_fits_pump(spec):
        return spec, False
    nxt = next_gchv_window(start_time, spec)
    if nxt is None:
        return None, True
    return f"{_fmt(nxt[0])}-{_fmt(nxt[1])}", True


def _power_entity_kw(
    power_id: str, get_state: Callable[[str], Any]
) -> float | None:
    """A heat-pump power entity's reading in kW, or ``None``.

    The entity's own declared unit converts to kW through the same
    normaliser every other power read uses; an unrecognised unit is no
    reading rather than a guess, because a wrongly scaled ceiling is worse
    than none.
    """
    state = get_state(power_id)
    if state is None:
        return None
    try:
        value = float(state.state)
    except (TypeError, ValueError):
        return None
    if value <= 0.0:
        return None
    kw = normalize_power_kw(
        value, (state.attributes or {}).get("unit_of_measurement")
    )
    return kw if kw is not None and kw > 0.0 else None


def measured_ceiling_kw(
    config: Mapping[str, Any],
    get_state: Callable[[str], Any] | None,
    p_max: float,
) -> float | None:
    """The measured in-window ceiling in kW, or ``None`` when unmetered.

    Preference order (tvofi, 2026-10-04): a heat-pump power entity first,
    then a compressor-frequency reading scaled by ``hz / hz_max`` over the
    range the frequency configuration carries. The figure is read once, on
    the loop, when the solve's inputs are assembled; it is the install's
    answer to "what does silent cost", not a time series.
    """
    if get_state is None or p_max <= 0.0:
        return None
    power_id = config.get(CONF_POWER_ENTITY)
    if isinstance(power_id, str) and power_id:
        kw = _power_entity_kw(power_id, get_state)
        if kw is not None:
            return kw
    hz, _, hz_max, _ = freq_control.resolve_reading(
        config.get(CONF_COMPRESSOR_FREQ_ENTITY),
        config.get(CONF_COMPRESSOR_FREQ_SENSOR),
        get_state,
        float(config.get(CONF_COMPRESSOR_FREQ_MIN_HZ)
              or DEFAULT_COMPRESSOR_FREQ_MIN_HZ),
        float(config.get(CONF_COMPRESSOR_FREQ_MAX_HZ)
              or DEFAULT_COMPRESSOR_FREQ_MAX_HZ),
    )
    if hz is not None and hz > 0.0 and hz_max > 0.0:
        return hz / hz_max * float(p_max)
    return None


def silent_cap_kw(
    config: Mapping[str, Any],
    get_state: Callable[[str], Any] | None,
    p_max: float,
) -> float | None:
    """The in-window electrical ceiling a silent step carries, in kW.

    A measured figure when the install exposes one, clipped into the same
    floor the configured fraction answers to -- the floor is the capacity
    envelope's, not the fraction's, so it holds for both. Otherwise the
    configured ``silent_mode_power_fraction`` exactly as configured:
    ``None`` at 1.0, which keeps an unconfigured fraction from capping
    anything while the rows still show (and the card still says the
    fraction is unset).
    """
    if p_max <= 0.0:
        return None
    measured = measured_ceiling_kw(config, get_state, p_max)
    if measured is not None:
        return min(
            max(float(measured), CAPACITY_FLOOR_FRACTION * float(p_max)),
            float(p_max),
        )
    try:
        fraction = float(
            config.get(CONF_SILENT_MODE_FRACTION, DEFAULT_SILENT_MODE_FRACTION)
        )
    except (TypeError, ValueError):
        return None
    if fraction >= 1.0:
        return None
    return max(fraction, CAPACITY_FLOOR_FRACTION) * float(p_max)


def compose(
    caps_extra: np.ndarray | None,
    config: Mapping[str, Any],
    get_state: Callable[[str], Any] | None,
    start_time: datetime,
    n_steps: int,
    dt_hours: float,
    p_max: float,
    *,
    optimizer_active: bool = True,
) -> QuietCompose:
    """The caller's ceiling tightened by the configured quiet windows.

    Silent steps fold into ``caps_extra`` by elementwise minimum -- the one
    ``power_caps_extra`` channel the fuse guard, the capacity envelope and
    the pump's own schedule already share -- and off steps come back as the
    ``off_steps`` mask for the solver's space caps and the DHW planner's
    forced-off door. Unset, unreadable, unreachable or unenforceable caps
    nothing: the caller's array comes back as the same object, which is
    the null control an install that sets nothing depends on.
    """
    silent_spec = config.get(CONF_QUIET_SILENT_WINDOWS)
    off_spec = config.get(CONF_QUIET_OFF_WINDOWS)
    if not silent_spec and not off_spec:
        return QuietCompose(caps_extra, None, None, False)
    if not optimizer_active:
        # D2 (tvofi, 2026-09-30): quiet windows write nothing and plan
        # nothing while the optimizer is off; the pump stays where it was
        # left. The rows are still configured, hence the dropped marker.
        return QuietCompose(caps_extra, None, None, bool(silent_spec))
    planned, silent_dropped = _silent_plan_spec(
        config, get_state, start_time, silent_spec
    )
    actions = step_actions(
        start_time, n_steps, dt_hours, planned, off_spec,
    )
    if actions is None:
        return QuietCompose(caps_extra, None, None, silent_dropped)
    off_steps = actions == ACTION_OFF
    caps = caps_extra
    silent_steps = actions == ACTION_SILENT
    if bool(np.any(silent_steps)):
        cap = silent_cap_kw(config, get_state, p_max)
        if cap is not None and cap < float(p_max):
            own = np.full(n_steps, float(p_max), dtype=float)
            own[silent_steps] = float(cap)
            caps = own if caps_extra is None else np.minimum(caps_extra, own)
    return QuietCompose(
        caps,
        off_steps if bool(np.any(off_steps)) else None,
        actions,
        silent_dropped,
    )


def compose_with_silent(
    caps_extra: np.ndarray | None,
    config: Mapping[str, Any],
    get_state: Callable[[str], Any] | None,
    start_time: datetime,
    n_steps: int,
    dt_hours: float,
    p_max: float,
    *,
    optimizer_active: bool = True,
) -> QuietCompose:
    """The pump's silent-mode schedule, then the user's quiet windows.

    Silent rows of either source cap through ``power_caps_extra``. Off rows
    come back as ``off_steps``. Nothing is planned for a window while the
    optimizer is off, and a silent quiet-window row needs a control that
    can be held. Hass state is read here, on the loop (#1067, #1910).
    """
    from . import silent_mode

    caps = silent_mode.compose(
        caps_extra, config, start_time, n_steps, dt_hours, p_max,
    )
    return compose(
        caps, config, get_state, start_time, n_steps, dt_hours, p_max,
        optimizer_active=optimizer_active,
    )


def configured_specs(config: Mapping[str, Any]) -> dict[str, str]:
    """The quiet-window specs as configured, one per action (#1910).

    The card's editor edits the configuration, so it needs the configuration
    -- in the shared grammar, empty string for "no rows" -- not the plan's
    reading of it. The specs are stored canonical by the services that write
    them, so they are handed back as stored. A silent spec with no control
    that can hold it carries the not-enforced marker, decided from the
    entity ID's domain and never the state, so a switch that has not
    reported yet (state ``unknown``) is not dropped: unknown is not off.
    """
    out: dict[str, str] = {
        "quiet_silent_windows_spec": str(
            config.get(CONF_QUIET_SILENT_WINDOWS) or ""
        ),
        "quiet_off_windows_spec": str(config.get(CONF_QUIET_OFF_WINDOWS) or ""),
    }
    if out["quiet_silent_windows_spec"] and not silent_control_usable(
        config.get(CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY)
    ):
        out["quiet_silent_not_enforced"] = "true"
    return out


def overridden_config(
    config: Mapping[str, Any], overrides: Mapping[str, Any]
) -> Mapping[str, Any]:
    """``config`` with the quiet what-if override keys folded in (#1910).

    A what-if that changes the rows must be priced under the caps they
    imply, so the simulator composes against this rather than the stored
    configuration. Unrelated keys pass straight through to whoever else
    reads ``overrides``.
    """
    out = config
    for key in (CONF_QUIET_SILENT_WINDOWS, CONF_QUIET_OFF_WINDOWS):
        if key in overrides:
            out = {**out, key: overrides[key]}
    # The fraction folds only when the call moved it off its default, which
    # is also exactly when folding changes anything: absent and an explicit
    # 1.0 are the same setting.
    fraction = overrides.get(
        CONF_SILENT_MODE_FRACTION, DEFAULT_SILENT_MODE_FRACTION
    )
    if fraction != DEFAULT_SILENT_MODE_FRACTION:
        out = {**out, CONF_SILENT_MODE_FRACTION: fraction}
    return out


def apply_config_keys(config: dict[str, Any], params: Mapping[str, Any]) -> None:
    """Fold a parameter write's quiet keys into the live config (#1910).

    The specs and the silent fraction are configuration, not physics, so
    ``set_thermal_parameters`` routes them here: into the config mapping
    the next solve composes from, with the persistence itself done by the
    options write the caller already makes.
    """
    for key in (CONF_QUIET_SILENT_WINDOWS, CONF_QUIET_OFF_WINDOWS):
        if key in params:
            config[key] = params[key]
    fraction = params.get(
        CONF_SILENT_MODE_FRACTION, DEFAULT_SILENT_MODE_FRACTION
    )
    if fraction != DEFAULT_SILENT_MODE_FRACTION:
        config.update({CONF_SILENT_MODE_FRACTION: fraction})


def _parse_spec_pair(
    silent_spec: str | None, off_spec: str | None
) -> tuple[
    tuple[list[Window], list[list[Window]] | None],
    tuple[list[Window], list[list[Window]] | None],
] | None:
    """Both specs parsed, or ``None`` when neither carries a window.

    An unreadable stored spec caps nothing rather than failing the solve,
    the same stance ``silent_mode.compose`` takes: the options page and the
    services refuse such a value, so one can only arrive from an older or
    hand-edited entry.
    """
    out: list[tuple[list[Window], list[list[Window]] | None]] = []
    for spec in (silent_spec, off_spec):
        if not spec:
            out.append(([], None))
            continue
        try:
            out.append((parse_windows(spec), parse_weekly_windows(spec)))
        except (DHWWindowError, TypeError, ValueError):
            return None
    if not out[0][0] and out[0][1] is None and not out[1][0] and out[1][1] is None:
        return None
    return out[0], out[1]


def overlap_problem(
    silent_spec: str | None,
    off_spec: str | None,
    dhw_spec: str | None,
) -> str | None:
    """The first cross-spec overlap the save must refuse, or ``None``.

    The plan's section 2.1 rules: an off window may not overlap a hot-water
    window on the same day (hot water must be available exactly when the
    user asked for it); a silent window may not overlap an off window on
    the same day (one step cannot be both); a silent window MAY overlap a
    hot-water one -- the tank just charges slower. Judged per weekday over
    the specs' own weekly structure, the same resolution
    ``step_actions`` plans by, so what is refused is exactly what could
    otherwise conflict in the plan.
    """
    parsed = _parse_spec_pair(silent_spec, off_spec)
    if parsed is None:
        return None
    (s_win, s_weekly), (o_win, o_weekly) = parsed
    dhw_win: list[Window] = []
    dhw_weekly: list[list[Window]] | None = None
    if dhw_spec:
        try:
            dhw_win = parse_windows(dhw_spec)
            dhw_weekly = parse_weekly_windows(dhw_spec)
        except (DHWWindowError, TypeError, ValueError):
            dhw_win, dhw_weekly = [], None
    for day in range(7):
        off_day = windows_for_day(o_weekly, day, o_win)
        if off_day:
            for window in off_day:
                for other in windows_for_day(dhw_weekly, day, dhw_win):
                    if _overlaps(window, other):
                        return (
                            f"off window {_fmt(window[0])}-{_fmt(window[1])} overlaps "
                            f"the hot-water window {_fmt(other[0])}-"
                            f"{_fmt(other[1])} on {_DAY_NAMES[day]}"
                        )
                for other in windows_for_day(s_weekly, day, s_win):
                    if _overlaps(window, other):
                        return (
                            f"off window {_fmt(window[0])}-{_fmt(window[1])} overlaps "
                            f"the silent window {_fmt(other[0])}-"
                            f"{_fmt(other[1])} on {_DAY_NAMES[day]}"
                        )
    return None


def _overlaps(a: Window, b: Window) -> bool:
    """Whether two windows on the same day share any time.

    Both sides come from ``windows_for_day``, whose lists are normalised
    (midnight-wrapping ranges already split), so both are same-day
    intervals and a plain open-interval test is exact.
    """
    return bool(a[0] < b[1] and b[0] < a[1])


def _fmt(hour: float) -> str:
    """An hour-of-day as ``HH:MM``, the grammar's own form."""
    minutes = int(round(hour * 60.0)) % (24 * 60)
    return f"{minutes // 60:02d}:{minutes % 60:02d}"
