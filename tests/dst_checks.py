"""Quarter-grid and DST-transition checks that need a real timezone.

Run by ``tests/features.py`` in a subprocess with
``HASTUB_TZ=Europe/Stockholm``: the stub's ``DEFAULT_TIME_ZONE`` is read
once at import, so the zone cannot be flipped inside a process that has
already imported ``homeassistant.util.dt``. Everything here exercises paths
where wall-clock time and the plan grid meet — the exact seam the main
suite's identity-timezone stub cannot see.
"""
from __future__ import annotations

import asyncio
import sys
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from zoneinfo import ZoneInfo

from harness import CapturingOptimizer, FakeEntry, FakeHass, FakeState, Results

import numpy as np

from homeassistant.util import dt as dt_util

from heatpump_optimizer import const
from heatpump_optimizer import (
    _handover_stamps,
    _plan_handovers,
    _take_fresh_handover,
)
from heatpump_optimizer.coordinator import (
    FORECAST_STEP_MINUTES,
    HeatPumpOptimizerCoordinator,
    _solve_anchor,
    _utc_step_starts,
)
from heatpump_optimizer.manual_plan import ManualOverride, PIN_ON
from heatpump_optimizer.disinfection import DisinfectionSwitch
from heatpump_optimizer.legionella import LegionellaGuard
from heatpump_optimizer.pump_signals import (
    MODE_SOURCE_EXPIRED,
    MODE_SOURCE_LAST_GOOD,
)
from heatpump_optimizer.optimizer import (
    HeatPumpOptimizer,
    OptimizationConfig,
    _Horizon,
    _utc_step_starts as _opt_utc_step_starts,
)
from heatpump_optimizer.thermal_model import (
    ThermalModel,
    ThermalParameters,
    ThermalState,
)
from heatpump_optimizer.tariff import (
    CapacityTariff,
    PeakTracker,
    _window_slot,
    window_factors,
)

R = Results("DST / quarter-grid (subprocess, HASTUB_TZ)")

STHLM = ZoneInfo("Europe/Stockholm")

R.section("the stub honours HASTUB_TZ")
R.check(
    "dt_util carries the configured zone",
    dt_util.DEFAULT_TIME_ZONE is not None
    and dt_util.now().tzinfo is not None,
)

# ===========================================================================
# The quarter snap, through the coordinator path
# ===========================================================================
R.section("solve anchor snaps to the quarter grid (coordinator path)")

FROZEN = datetime(2026, 8, 26, 12, 7, 33, 123456, tzinfo=STHLM)
dt_util.freeze(FROZEN)

_data = {"tibber_token": "x", "weather_entity": "weather.home"}
coord = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=_data))

anchor = _solve_anchor(dt_util.now())
R.check(
    "12:07:33 floors to 12:00:00 with tz and date intact",
    anchor == datetime(2026, 8, 26, 12, 0, tzinfo=STHLM)
    and anchor.tzinfo is FROZEN.tzinfo,
    f"got {anchor.isoformat()}",
)
R.check(
    "a boundary instant is its own anchor",
    _solve_anchor(datetime(2026, 8, 26, 12, 45, tzinfo=STHLM))
    == datetime(2026, 8, 26, 12, 45, tzinfo=STHLM),
)

# Hourly price entries covering yesterday noon → tomorrow, value = hour of
# day in SEK so a step's price names the hour it was taken from.
coord._prices = [
    {
        "starts_at": (
            datetime(2026, 8, 25, 12, 0, tzinfo=STHLM) + timedelta(hours=i)
        ).isoformat(),
        "total": float(
            (datetime(2026, 8, 25, 12, 0, tzinfo=STHLM) + timedelta(hours=i)).hour
        ),
    }
    for i in range(48)
]

_real_state, _real_opt = coord._solve_snapshot()
coord._solve_snapshot = lambda: (_real_state, CapturingOptimizer(_real_opt))
asyncio.run(coord.async_run_optimization())
result = coord._optimization_result

R.check(
    "optimize() receives the snapped anchor, not the raw 12:07 instant",
    result is not None and result.timestamps[0] == anchor,
    f"got {result.timestamps[0] if result else None}",
)
R.check(
    "every published plan timestamp lands on a :00/:15/:30/:45 boundary",
    result is not None
    and all(
        ts.minute in (0, 15, 30, 45) and ts.second == 0 and ts.microsecond == 0
        for ts in result.timestamps
    ),
)
R.check(
    "step 0's price is the quarter in force at 12:07 — the 12:00 hour's",
    result is not None and result.prices[0] == 12.0,
    f"got {result.prices[0] if result else None}",
)
R.check(
    "the wall-clock action lookup lands on step 0, no pre-horizon clamp",
    coord._current_action.get("power") == 1.0
    and coord._current_action.get("mode") != "idle",
    f"got {coord._current_action}",
)
R.check(
    "filed lead promises mature on quarter boundaries",
    coord._accuracy.lead_pending
    and all(
        t.minute in (0, 15, 30, 45) and t.second == 0
        for t, _lead, _temp in coord._accuracy.lead_pending
    ),
    f"{len(coord._accuracy.lead_pending)} pending",
)

# --- override expiry at the snapped anchor: the documented edge ------------------
override = ManualOverride(
    space_slots=[
        (
            datetime(2026, 8, 26, 11, 0, tzinfo=STHLM),
            datetime(2026, 8, 26, 12, 5, tzinfo=STHLM),
        )
    ],
    dhw_slots=None,
    expires_at=datetime(2026, 8, 26, 12, 5, tzinfo=STHLM),
)
coord._manual_override = override
space_pins, dhw_pins = coord._manual_pins(anchor, 8)
R.check(
    "an override expiring 12:05 still pins the [12:00, 12:15) step at 12:07",
    space_pins is not None and space_pins[0] == PIN_ON,
    f"got {space_pins}",
)
R.check(
    "and frees every step starting at or past the expiry",
    space_pins is not None and bool(np.all(np.isnan(space_pins[1:]))),
)
R.check(
    "the not-yet-expired override is kept, not dropped eagerly",
    coord._manual_override is override,
)

dt_util.freeze(None)

# ===========================================================================
# Metering windows across the two Stockholm transitions
# ===========================================================================
R.section("window snap: day-anchored, across both DST transitions")

# Equality proof for every divisor-of-60 config: a full day, both a plain
# day and the two transition days, minute by minute. The old modulo snap is
# reproduced inline as the reference.
def _old_slot(when: datetime, window: int) -> datetime:
    slot = when.replace(second=0, microsecond=0)
    return slot.replace(minute=(slot.minute // window) * window % 60)


_days = (
    datetime(2026, 8, 26, tzinfo=STHLM),   # plain
    datetime(2026, 10, 25, tzinfo=STHLM),  # autumn fold
    datetime(2026, 3, 29, tzinfo=STHLM),   # spring gap
)
_mismatch = []
for window in (15, 30, 60):
    for day in _days:
        # Walk the day by REAL elapsed time (UTC instants converted back to
        # local), not by wall-clock timedelta: only the real walk visits the
        # autumn fold's second 02:xx pass with fold=1 — the form
        # ``dt_util.now()`` actually returns there, and the one place a
        # fold-dropping snap silently merges two metered hours into one
        # window key. The first version of this check walked wall time and
        # stripped ``fold`` before comparing, which is precisely the
        # difference that was load-bearing.
        start_utc = day.astimezone(timezone.utc)
        for m in range(0, 26 * 60, 7):
            when = (start_utc + timedelta(minutes=m, seconds=41)).astimezone(
                STHLM
            )
            if when.date() != day.date():
                continue
            old = _old_slot(when, window)
            new = _window_slot(when, window)
            # The window key is the slot's isoformat — compare exactly that.
            if new.isoformat() != old.isoformat():
                _mismatch.append((window, when, old, new))
R.check(
    "15/30/60-minute snaps match the old keys exactly, fold included",
    not _mismatch,
    f"first: {_mismatch[:1]}",
)

# The autumn day has 25 real hours; a 60-minute tariff must meter 25
# distinct windows, or the repeated hour's burst is diluted across two real
# hours sharing one accumulator.
_fold_day_keys = set()
_start_utc = datetime(2026, 10, 25, tzinfo=STHLM).astimezone(timezone.utc)
for m in range(0, 26 * 60, 5):
    when = (_start_utc + timedelta(minutes=m)).astimezone(STHLM)
    if when.date() != datetime(2026, 10, 25).date():
        continue
    _fold_day_keys.add(_window_slot(when, 60).isoformat())
R.check(
    "the 25-hour autumn day meters 25 distinct 60-minute windows",
    len(_fold_day_keys) == 25,
    f"{len(_fold_day_keys)} distinct keys",
)

_slots_120 = [
    _window_slot(
        datetime(2026, 10, 25, h, 30, tzinfo=STHLM), 120
    )
    for h in range(24)
]
R.check(
    "120-minute windows advance the hour on the fold day (0,0,2,2,4,4,…)",
    [s.hour for s in _slots_120] == [h - h % 2 for h in range(24)]
    and all(s.minute == 0 for s in _slots_120),
    f"got {[s.hour for s in _slots_120]}",
)
R.check(
    "and on the gap day, straight through the missing wall hour",
    [
        _window_slot(datetime(2026, 3, 29, h, 30, tzinfo=STHLM), 120).hour
        for h in (1, 3, 4)
    ]
    == [0, 2, 4],
)

# The realised tracker and the guard's snapshot agree on windows > 60 min.
tariff_120 = CapacityTariff(
    enabled=True, price_per_kw=60.0, window_minutes=120
)
tracker = PeakTracker()
t0 = datetime(2026, 10, 25, 12, 10, tzinfo=STHLM)
tracker.observe(t0, 4.0, tariff_120)
tracker.observe(t0 + timedelta(minutes=80), 8.0, tariff_120)  # 13:30, same window
key, mean, elapsed, factor = tracker.window_snapshot(
    t0 + timedelta(minutes=80), tariff_120
)
R.check(
    "a 12:10 and a 13:30 sample share one 120-minute window",
    mean == 6.0 and key.startswith("2026-10-25T12:00:00"),
    f"key {key}, mean {mean}",
)
R.check(
    "elapsed inside a 120-minute window can exceed an hour",
    abs(elapsed - 90.0) < 1e-9,
    f"elapsed {elapsed}",
)
tracker.observe(t0 + timedelta(minutes=110), 8.0, tariff_120)  # 14:00 next window
R.check(
    "the window closes on the 2-hour boundary, not every wall hour",
    tracker.peaks == [6.0],
    f"peaks {tracker.peaks}",
)

# Factor masks anchor at the true window start: a 13:30 horizon start in a
# 120-minute tariff bills its first window under 12:00, and 12:00 sits
# outside a 13:00-14:00 peak-hours mask.
mask = CapacityTariff(
    enabled=True,
    window_minutes=120,
    # 13:00-14:00 is "peak", everything else half-rate.
    peak_hours=((13.0, 14.0),),
    offpeak_factor=0.5,
)
factors = window_factors(
    mask, datetime(2026, 10, 25, 13, 30, tzinfo=STHLM), 3, 0.25
)
R.check(
    "window_factors samples 12:00/14:00/16:00, not 13:00/15:00/17:00",
    factors is not None and list(factors) == [0.5, 0.5, 0.5],
    f"got {None if factors is None else list(factors)}",
)

# ===========================================================================
# #243: the planning grid walks UTC, not wall-clock timedelta
# ===========================================================================
R.section("planning grid on DST days (#243)")

UTC = timezone.utc
EPOCH = datetime(2026, 1, 1, tzinfo=UTC)


def _price_for(instant: datetime) -> float:
    return float((instant.astimezone(UTC) - EPOCH).total_seconds() // 3600)


def _is_phantom(s: datetime) -> bool:
    back = s.astimezone(UTC).astimezone(STHLM)
    return back.replace(tzinfo=None) != s.replace(tzinfo=None)


def _dst_coord(day: datetime) -> HeatPumpOptimizerCoordinator:
    cfg = {
        "tibber_token": "x",
        "weather_entity": "weather.home",
        "target_temperature": 21.0,
        "min_temperature": 17.0,
        "max_temperature": 23.0,
    }
    built = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=cfg))
    start_utc = (day - timedelta(days=1)).astimezone(UTC)
    entries = []
    wx = []
    for h in range(72):
        t = (start_utc + timedelta(hours=h)).astimezone(STHLM)
        entries.append(
            {"total": _price_for(t), "starts_at": t.isoformat(), "level": "NORMAL"}
        )
        wx.append(
            {
                "datetime": t.isoformat(),
                "temperature": -3.0,
                "wind_speed": 3.0,
                "precipitation": 0.0,
                "humidity": 80.0,
            }
        )
    built._prices = entries
    built._weather_forecast = wx
    built._solar_radiation_forecast = [0.0] * 72
    return built


_DST_DAYS = (
    ("plain", datetime(2026, 8, 26, tzinfo=STHLM)),
    ("spring", datetime(2026, 3, 29, tzinfo=STHLM)),
    ("autumn", datetime(2026, 10, 25, tzinfo=STHLM)),
    ("spring2025", datetime(2025, 3, 30, tzinfo=STHLM)),
    ("autumn2025", datetime(2025, 10, 26, tzinfo=STHLM)),
    ("spring2027", datetime(2027, 3, 28, tzinfo=STHLM)),
    ("autumn2027", datetime(2027, 10, 31, tzinfo=STHLM)),
)

_mis = {}
_n = 96
for _label, _day in _DST_DAYS:
    _now = _day.replace(hour=0, minute=7)
    dt_util.freeze(_now)
    _c = _dst_coord(_day)
    _midnight = _now.replace(hour=0, minute=0, second=0, microsecond=0)
    _priced = _c._price_series(_n, _midnight, 0)
    _arrays = _c._forecast_arrays(_now)
    _labels = _utc_step_starts(_midnight, _n, 0)
    _t0 = _labels[0].astimezone(UTC)
    _real = [_t0 + timedelta(minutes=FORECAST_STEP_MINUTES * i) for i in range(_n)]
    _expected = np.array([_price_for(r) for r in _real])
    _got = np.asarray(_priced[0] if _priced is not None else _arrays.prices)
    _mis[_label] = int(np.sum(_got != _expected))
    dt_util.freeze(None)

R.check(
    "all six transition days align prices to real instants",
    all(_mis[k] == 0 for k in _mis if k != "plain"),
    f"{_mis}",
)
R.check(
    "the plain day stays a zero null",
    _mis["plain"] == 0,
    f"{_mis['plain']}",
)
R.check(
    "_forecast_arrays and _price_series agree on the spring grid",
    _mis["spring"] == 0,
)

_spring = datetime(2026, 3, 29, tzinfo=STHLM)
_autumn = datetime(2026, 10, 25, tzinfo=STHLM)
_spring_ts = _Horizon.timestamps.fget(
    type("_H", (), {"start_time": _spring, "n_steps": _n, "dt": 0.25})()
)
_autumn_ts = _Horizon.timestamps.fget(
    type("_H", (), {"start_time": _autumn, "n_steps": _n, "dt": 0.25})()
)
_plain_ts = _Horizon.timestamps.fget(
    type(
        "_H",
        (),
        {"start_time": datetime(2026, 8, 26, tzinfo=STHLM), "n_steps": _n, "dt": 0.25},
    )()
)
R.check(
    "_Horizon.timestamps invents no spring phantom",
    not any(_is_phantom(t) for t in _spring_ts),
    f"phantoms={[t.isoformat() for t in _spring_ts if _is_phantom(t)]}",
)
R.check(
    "coordinator and optimizer stamp the same spring grid",
    _opt_utc_step_starts(_spring, _n, 0.25) == _utc_step_starts(_spring, _n, 0),
    "the two seams must not disagree by an hour on a transition day",
)
_spring_gaps = [
    (_spring_ts[i + 1].astimezone(UTC) - _spring_ts[i].astimezone(UTC)).total_seconds()
    / 60.0
    for i in range(_n - 1)
]
_autumn_gaps = [
    (_autumn_ts[i + 1].astimezone(UTC) - _autumn_ts[i].astimezone(UTC)).total_seconds()
    / 60.0
    for i in range(_n - 1)
]
R.check(
    "spring and autumn UTC gaps are 15 minutes, plain day too",
    max(_spring_gaps) == 15
    and max(_autumn_gaps) == 15
    and max(
        (
            _plain_ts[i + 1].astimezone(UTC) - _plain_ts[i].astimezone(UTC)
        ).total_seconds()
        / 60.0
        for i in range(_n - 1)
    )
    == 15,
    f"spring {max(_spring_gaps)} autumn {max(_autumn_gaps)}",
)

_params = ThermalParameters.from_config(
    {
        "indoor_temp_entity": "sensor.indoor",
        "outdoor_temp_entity": "sensor.outdoor",
    }
)
_params.dhw_enabled = False
_opt = HeatPumpOptimizer(
    ThermalModel(_params),
    OptimizationConfig(
        horizon_hours=24,
        time_step_minutes=15,
        target_temp=21.0,
        min_temp=17.0,
        max_temp=23.0,
    ),
)
_state = ThermalState(
    room_temperature=21.0,
    slab_temperature=22.0,
    outdoor_temperature=-3.0,
    upper_floor_temperature=21.0,
    lower_floor_temperature=21.0,
    dhw_temperature=50.0,
    buffer_tank_temperature=40.0,
)


def _plan_on(day: datetime):
    now = day.replace(hour=0, minute=7)
    dt_util.freeze(now)
    c = _dst_coord(day)
    arrays = c._forecast_arrays(now)
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    labels = _utc_step_starts(midnight, _n, 0)
    hours = np.array([(s.hour + s.minute / 60.0) for s in labels])
    shaped = np.where(
        (hours >= 0) & (hours < 5),
        0.6,
        np.where((hours >= 16) & (hours < 20), 2.8, 1.1),
    )
    res = _opt.optimize(
        _state,
        shaped,
        np.asarray(arrays.outdoor_temps),
        np.asarray(arrays.wind_speeds),
        np.asarray(arrays.precipitation),
        np.asarray(arrays.solar_radiation),
        _solve_anchor(now),
    )
    dt_util.freeze(None)
    return res


_spring_plan = _plan_on(_spring)
_autumn_plan = _plan_on(_autumn)
_spring_ph = [i for i, t in enumerate(_spring_plan.timestamps) if _is_phantom(t)]
_spring_kwh = (
    float(np.sum(np.asarray(_spring_plan.power_schedule)[_spring_ph]) * 0.25)
    if _spring_ph
    else 0.0
)
_autumn_utc = [t.astimezone(UTC) for t in _autumn_plan.timestamps]
_autumn_plan_gaps = [
    (_autumn_utc[i + 1] - _autumn_utc[i]).total_seconds() / 60.0
    for i in range(len(_autumn_utc) - 1)
]
R.check(
    "spring plan books no energy on a phantom step",
    _spring_kwh == 0.0 and not _spring_ph,
    f"phantom_kwh={_spring_kwh} steps={_spring_ph}",
)
R.check(
    "autumn plan max gap is one 15-minute step",
    max(_autumn_plan_gaps) == 15,
    f"max_gap_min={max(_autumn_plan_gaps)}",
)

# ===========================================================================
# #777: the billing mask walked the wall clock while the plan walks UTC
# ===========================================================================
R.section("window_factors across a transition INSIDE the horizon (#777)")

# The 120-minute case above starts at 13:30 on the fold day -- ten hours PAST
# the 03:00 transition -- so not one of its windows crosses one, which is why
# it could never have seen #777. These start the evening BEFORE, over the real
# 24 h default horizon, so the transition falls inside the horizon and every
# window after it is labelled by the walk under test.
_M777 = dict(
    enabled=True,
    price_per_kw=60.0,
    peak_hours=((7.0, 20.0),),
    offpeak_factor=0.0,
)
_DAYS777 = (
    ("autumn", datetime(2026, 10, 24, 21, 0, tzinfo=STHLM)),
    ("spring", datetime(2026, 3, 28, 21, 0, tzinfo=STHLM)),
    ("control", datetime(2026, 10, 17, 21, 0, tzinfo=STHLM)),
)


def _metered_factors(tariff: CapacityTariff, start: datetime, n: int) -> list[float]:
    """The factor PRODUCTION assigns each window, over real UTC-walked instants.

    Nothing here re-implements the mask: the instants come from the
    optimizer's own step clock (``_utc_step_starts``) and the factor is read
    back off ``PeakTracker`` after ``observe`` has attributed the window. That
    is exactly the quantity ``window_factors``' docstring promises the plan's
    cost term can never disagree with, so it is what the check compares to.
    """
    tracker = PeakTracker()
    slot0 = _window_slot(start, tariff.window_minutes)
    seen = []
    for when in _opt_utc_step_starts(slot0, n, tariff.window_minutes / 60.0):
        tracker.observe(when, 1.0, tariff)
        seen.append(tracker._window_factor)
    return seen


_f777 = {}
for _label, _start in _DAYS777:
    for _wm in (60, 15):
        _t777 = CapacityTariff(window_minutes=_wm, **_M777)
        _n777 = int(round(24 * 60 / _wm))
        _planned = window_factors(_t777, _start, _n777, _wm / 60.0)
        _metered = _metered_factors(_t777, _start, _n777)
        _f777[(_label, _wm)] = {
            "produced": _planned is not None,
            "bad": []
            if _planned is None
            else [i for i in range(_n777) if _planned[i] != _metered[i]],
            "rates": sorted(set(_metered)),
        }


def _agree777(label: str) -> bool:
    # `produced` guards the vacuous pass: a None return compares an empty
    # mismatch list against itself and would look like agreement.
    return all(
        _f777[(label, wm)]["produced"] and not _f777[(label, wm)]["bad"]
        for wm in (60, 15)
    )


def _detail777(label: str) -> str:
    return "; ".join(
        "%dmin produced=%s mismatched=%s"
        % (wm, _f777[(label, wm)]["produced"], _f777[(label, wm)]["bad"])
        for wm in (60, 15)
    )


# The guard against this case silently sliding off the transition again --
# the exact way the 13:30 case above stopped covering anything.
_offsets777 = {
    label: len({s.utcoffset() for s in _opt_utc_step_starts(start, 24, 1.0)})
    for label, start in _DAYS777
}
R.check(
    "the transition really is inside the autumn and spring horizons",
    _offsets777["autumn"] == 2
    and _offsets777["spring"] == 2
    and _offsets777["control"] == 1,
    "distinct UTC offsets per 24 h horizon: %s" % (_offsets777,),
)
R.check(
    "autumn fold: every window bills under the hour the meter keys it at",
    _agree777("autumn"),
    _detail777("autumn"),
)
R.check(
    "spring gap: every window bills under the hour the meter keys it at",
    _agree777("spring"),
    _detail777("spring"),
)
R.check(
    "NULL CONTROL: the ordinary Saturday a week earlier never disagreed",
    _agree777("control"),
    _detail777("control"),
)
R.check(
    "and the comparison is not vacuous — both rates occur in every cell",
    all(cell["rates"] == [0.0, 1.0] for cell in _f777.values()),
    "; ".join(
        "%s/%dmin rates=%s" % (label, wm, _f777[(label, wm)]["rates"])
        for (label, wm) in _f777
    ),
)

# ===========================================================================
# #1299 (round-5 D1-08): the age seams subtract wall clocks across DST
# ===========================================================================
R.section("age seams across the DST transitions (#1299)")

# Every seam below subtracts two datetimes that carry Home Assistant's
# single process-wide ZoneInfo instance, and CPython resolves subtraction
# of two aware datetimes that SHARE one tzinfo object as naive wall-clock
# subtraction -- so an age spanning a transition is off by the offset
# delta (1 h here). A true 2 h fold-night outage therefore reads 60 min
# old, under the 90-minute stale floor, and a dead plan keeps actuating;
# the spring gap over-reads by the same hour; a backward clock step
# publishes negative weather staleness. The null control throughout is
# the same true 2 h on a plain night, where wall and true elapsed agree.
FOLD_NIGHT = (
    datetime(2026, 10, 25, 1, 30, tzinfo=STHLM),  # CEST, pre-fold
    datetime(2026, 10, 25, 2, 30, tzinfo=STHLM, fold=1),  # CET, post-fold
)
GAP_NIGHT = (
    datetime(2027, 3, 28, 1, 30, tzinfo=STHLM),  # CET, pre-gap
    datetime(2027, 3, 28, 4, 30, tzinfo=STHLM),  # CEST, post-gap
)
PLAIN_NIGHT = (
    datetime(2026, 10, 24, 1, 30, tzinfo=STHLM),
    datetime(2026, 10, 24, 3, 30, tzinfo=STHLM),
)


def _age_coord(extra=None):
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("5.0"))
    config = {
        const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
        const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
        const.CONF_DHW_TANK_VOLUME: 180.0,
    }
    config.update(extra or {})
    return HeatPumpOptimizerCoordinator(hass, FakeEntry(data=config))


def _seam_ages(night):
    """The published plan age / staleness / weather hours over a TRUE 2 h."""
    coord = _age_coord()
    start, end = night
    try:
        dt_util.freeze(start)
        coord._last_optimization = dt_util.now()
        coord._weather_fetch_failed("simulated outage")
        dt_util.freeze(end)
        plan_age = coord._plan_age_minutes()
        plan_stale = coord._plan_is_stale()
        weather_hours = coord.weather_stale_hours()
    finally:
        dt_util.freeze(None)
    true_minutes = (
        end.astimezone(timezone.utc) - start.astimezone(timezone.utc)
    ).total_seconds() / 60.0
    return plan_age, plan_stale, weather_hours, true_minutes


_fa, _fs, _fw, _ft = _seam_ages(FOLD_NIGHT)
R.check(
    "a 2 h fold-night outage reads its true age, not the wall clock's",
    _fa == _ft,
    f"published {_fa} min, true {_ft}",
)
R.check(
    "and crosses the 90-minute stale floor a 2 h outage must cross",
    _fs is True,
    f"stale flag {_fs} at published {_fa} min",
)
R.check(
    "weather staleness across the fold is the true 2 h",
    _fw == 2.0,
    f"published {_fw} h",
)
_ga, _gs, _gw, _gt = _seam_ages(GAP_NIGHT)
R.check(
    "spring gap: the plan age is the true 2 h, not 3 h of wall clock",
    _ga == _gt,
    f"published {_ga} min, true {_gt}",
)
R.check(
    "spring gap: weather staleness is the true 2 h",
    _gw == 2.0,
    f"published {_gw} h",
)
_pa, _ps, _pw, _pt = _seam_ages(PLAIN_NIGHT)
R.check(
    "NULL CONTROL: the plain night's ages were always true",
    _pa == _pt and _pw == 2.0,
    f"age {_pa} min (true {_pt}), weather {_pw} h",
)

# A backward clock step (NTP step, or the fold itself seen from the far
# side) puts ``now`` before the latch: staleness must clamp at 0, never
# publish a negative age. The plan-age seam already clamps; this is the
# weather seam's own arm.
_JMP = datetime(2026, 10, 24, 12, 0, tzinfo=timezone.utc)
_jc = _age_coord()
try:
    dt_util.freeze(_JMP)
    _jc._last_optimization = dt_util.now()
    _jc._weather_fetch_failed("simulated outage")
    dt_util.freeze(_JMP - timedelta(hours=2))
    _jw = _jc.weather_stale_hours()
    _ja = _jc._plan_age_minutes()
finally:
    dt_util.freeze(None)
R.check(
    "a backward clock step publishes 0 h staleness, not a negative age",
    _jw == 0.0,
    f"weather_stale_hours={_jw}",
)
R.check(
    "the plan age stays clamped at 0 after the same step",
    _ja == 0.0,
    f"plan age {_ja}",
)

# --- the siblings the sweep found carrying the identical shape ------------
# ``_take_fresh_handover`` stamps with ``dt_util.now()`` at unload and
# subtracts ``dt_util.now()`` at setup: across a fold the handover reads
# half its true age, and a 2 h-old plan is reborn as fresh against a
# 60-minute window. The plain-night arm is the null control.
_taken = {}
for _label, _night in (("fold", FOLD_NIGHT), ("plain", PLAIN_NIGHT)):
    _h = FakeHass()
    _plan_handovers(_h)["e1"] = {"plan": True}
    try:
        dt_util.freeze(_night[0])
        _handover_stamps(_h)["e1"] = dt_util.now()
        dt_util.freeze(_night[1])
        _taken[_label] = _take_fresh_handover(_h, "e1", 60.0)
    finally:
        dt_util.freeze(None)
R.check(
    "a fold-night handover 2 h old is refused against a 60-min window",
    _taken["fold"] is None,
    f"got {_taken['fold']}",
)
R.check(
    "NULL CONTROL: the plain-night 2 h handover is refused identically",
    _taken["plain"] is None,
    f"got {_taken['plain']}",
)

# ``LegionellaGuard.hours_since`` publishes the age of the last cycle;
# the live latch is ``dt_util.now()`` on both sides of the subtraction.
_lg = LegionellaGuard(
    FakeHass(),
    "dst",
    ThermalParameters.from_config({}),
    {},
    action=lambda: {},
    disinfect=DisinfectionSwitch({}, None, None),
    dhw_blocked=lambda: False,
)
try:
    dt_util.freeze(FOLD_NIGHT[0])
    _lg.last_cycle = dt_util.now()
    dt_util.freeze(FOLD_NIGHT[1])
    _lh = _lg.hours_since()
finally:
    dt_util.freeze(None)
R.check(
    "legionella hours_since reads true elapsed across the fold",
    _lh == 2.0,
    f"published {_lh} h",
)


# The plan-step walk in ``_async_drive_pumps`` derives the pump's step
# index from ``now - timestamps[0]`` -- the same shared-ZoneInfo shape.
# The schedule is ON exactly for the steps the fold's 1 h wall error
# lands on (steps 4-7 of the quarter grid): the naive walk stops there
# while the true 2 h walk has left them, so at the bug the pump is
# commanded ON by an hour-old step. Warm zones and a mild outdoor keep
# every comfort rail out of the decision, so the command follows the plan.
async def _pump_command(night):
    coord = _age_coord({const.CONF_SPACE_PUMP_ENTITY: "switch.space"})
    schedule = [1.0 if 4 <= i < 8 else 0.0 for i in range(96)]
    try:
        dt_util.freeze(night[0])
        coord._optimization_result = SimpleNamespace(
            timestamps=[dt_util.now()], power_schedule=schedule
        )
        dt_util.freeze(night[1])
        await coord._async_drive_pumps()
    finally:
        dt_util.freeze(None)
    return [
        (service, data.get("entity_id"))
        for domain, service, data in coord.hass.services.calls
        if domain == "homeassistant"
    ]


_pf = asyncio.run(_pump_command(FOLD_NIGHT))
_pp = asyncio.run(_pump_command(PLAIN_NIGHT))
R.check(
    "the pump walks the plan by TRUE elapsed steps across the fold",
    _pf == _pp,
    f"fold {_pf} vs plain {_pp}",
)
R.check(
    "and that agreement is the OFF the true index commands",
    _pp == [("turn_off", "switch.space")],
    f"plain-night command {_pp}",
)

# The mode entity's last-good fallback is bounded by the age of the last
# live reading (MODE_LAST_GOOD_MAX_AGE_MINUTES = 180): the seam at
# coordinator.py's ``_pump_mode_last_good_at`` stamps ``dt_util.now()`` on
# a live read and ages it with the same shared-ZoneInfo subtraction. The
# fold reads a true-200-minute-old mode as 140 minutes -- inside the 180
# bound -- so a mode that stopped acting three and a half hours ago keeps
# suppressing channels it can no longer serve. Same shape as the plan-age
# seam, one whole method up.
MODE_STAMP_NIGHT = (
    datetime(2026, 10, 25, 0, 30, tzinfo=STHLM),  # CEST, pre-fold
    datetime(2026, 10, 25, 2, 50, tzinfo=STHLM, fold=1),  # CET, post-fold
)
MODE_PLAIN_NIGHT = (
    datetime(2026, 10, 24, 0, 30, tzinfo=STHLM),
    datetime(2026, 10, 24, 3, 50, tzinfo=STHLM),  # same TRUE 200 min
)


async def _mode_source_after_outage(night):
    """mode_source once the entity is stale, one outage-spanning window."""
    coord = _age_coord({const.CONF_HEAT_PUMP_MODE_ENTITY: "sensor.mode"})
    start, end = night
    try:
        dt_util.freeze(start)
        # "heating" alone is status-ambiguous for a plain sensor
        # (pump_mode._STATUS_AMBIGUOUS); a multi-duty spelling is accepted
        # from any domain, so this is a LIVE read.
        coord.hass.states.set(
            "sensor.mode",
            FakeState("heating + hot water", last_updated=dt_util.now()),
        )
        await coord._update_current_state()
        stamped = coord._pump_mode_last_good_at
        # The entity now goes quiet: its state never updates again, so at
        # ``end`` it is stale -- unreadable, which is exactly the state the
        # last-good fallback exists for.
        dt_util.freeze(end)
        await coord._update_current_state()
        source = coord._pump_signals.mode_source
    finally:
        dt_util.freeze(None)
    return stamped, source


_ms, _mf = asyncio.run(_mode_source_after_outage(MODE_STAMP_NIGHT))
_mp, _mpf = asyncio.run(_mode_source_after_outage(MODE_PLAIN_NIGHT))
R.check(
    "the fold-night outage stamped its last-good at the pre-fold instant",
    _ms is not None and _ms.utcoffset() == MODE_STAMP_NIGHT[0].utcoffset(),
    f"stamped {_ms}",
)
R.check(
    "a mode unreadable for a TRUE 3 h 20 min is expired, not held good",
    _mf == MODE_SOURCE_EXPIRED,
    f"fold-night mode_source={_mf!r}",
)
R.check(
    "NULL CONTROL: the plain night expires the same-age mode identically",
    _mpf == MODE_SOURCE_EXPIRED and _mp is not None,
    f"plain-night mode_source={_mpf!r}",
)

# The defrost duty window accumulates seconds through ``_elapsed``, the
# same shared-ZoneInfo subtraction with both stamps from ``dt_util.now()``:
# across the fold a true-2 h defrost settles as one hour of duty.
from heatpump_optimizer.defrost import DefrostWindow

_dw_fold = DefrostWindow()
_dw_plain = DefrostWindow()
try:
    dt_util.freeze(FOLD_NIGHT[0])
    _dw_fold.observe(dt_util.now(), True)
    dt_util.freeze(FOLD_NIGHT[1])
    _fold_seconds = _dw_fold.peek(dt_util.now()).seconds

    dt_util.freeze(PLAIN_NIGHT[0])
    _dw_plain.observe(dt_util.now(), True)
    dt_util.freeze(PLAIN_NIGHT[1])
    _plain_seconds = _dw_plain.peek(dt_util.now()).seconds
finally:
    dt_util.freeze(None)
R.check(
    "a defrost running the fold's true 2 h books 7200 s of duty",
    _fold_seconds == 7200.0,
    f"fold {_fold_seconds} s",
)
R.check(
    "NULL CONTROL: the plain night books the same 7200 s",
    _plain_seconds == 7200.0,
    f"plain {_plain_seconds} s",
)
R.check(
    "and a mixed naive/aware pair is still declined, not guessed",
    _dw_fold._elapsed(
        datetime(2026, 10, 25, 2, 30),  # naive
        datetime(2026, 10, 25, 2, 30, tzinfo=STHLM),
    )
    is None,
    "the unknown-length contract survives the normalisation",
)

sys.exit(R.close("DST / QUARTER-GRID CHECKS"))
