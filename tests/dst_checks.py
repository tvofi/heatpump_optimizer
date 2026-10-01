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
    FORECAST_STEP,
    FORECAST_STEP_MINUTES,
    HeatPumpOptimizerCoordinator,
    _solve_anchor,
    _utc_step_starts,
)
from heatpump_optimizer.manual_plan import ManualOverride, PIN_OFF, PIN_ON
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
    _labels = _utc_step_starts(_midnight, _n, FORECAST_STEP)
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
# #1741: one clock. The coordinator's bridge to the optimizer's horizon
# (_horizon_step_starts) and _Horizon.timestamps both call the one
# optimizer._utc_step_starts with the configured step, so they agree on both
# transition days by construction, not because the config surface only offers
# whole-minute steps. A 7.5-minute step is the control the old two-clock pair
# failed: its minute-rounding bridge walked 8-minute steps.
_clk_fake = type("_C", (), {"_opt_config": type("_O", (), {"dt_hours": 0.25})()})()
_clk_odd = type("_C", (), {"_opt_config": type("_O", (), {"dt_hours": 0.125})()})()
R.check(
    "one horizon clock: the coordinator's import IS the optimizer's",
    _utc_step_starts is _opt_utc_step_starts,
)
for _clk_label, _clk_day, _clk_ts in (
    ("spring", _spring, _spring_ts), ("autumn", _autumn, _autumn_ts),
):
    R.check(
        f"coordinator and optimizer stamp the same {_clk_label} grid",
        HeatPumpOptimizerCoordinator._horizon_step_starts(_clk_fake, _clk_day, _n)
        == list(_clk_ts),
        "the two seams must not disagree by an hour on a transition day",
    )
    _clk_odd_ts = _Horizon.timestamps.fget(
        type("_H", (), {"start_time": _clk_day, "n_steps": _n, "dt": 0.125})()
    )
    R.check(
        f"and on a step that is not a whole number of minutes ({_clk_label})",
        HeatPumpOptimizerCoordinator._horizon_step_starts(_clk_odd, _clk_day, _n)
        == list(_clk_odd_ts),
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
    labels = _utc_step_starts(midnight, _n, FORECAST_STEP)
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
    for when in _opt_utc_step_starts(slot0, n, timedelta(minutes=tariff.window_minutes)):
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
    label: len({s.utcoffset() for s in _opt_utc_step_starts(start, 24, timedelta(hours=1))})
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

# ===========================================================================
# Round 9 F1.1: the grid after the transition, naive stored stamps, and the
# DST tracer over replayed transition days
# ===========================================================================
R.section("the forecast grid after the transition (round-9 D14-s4-01)")

# The #243 grid checks above solve at 00:07, before either transition, so
# ``step_offset`` is 0 and the seam that measures it is never exercised.
# After the transition, ``now - midnight`` read as wall clock is an hour off
# the true elapsed time (spring 12:07 is 11 h 07 min after a CET midnight),
# so the grid walked from midnight in UTC starts four quarters off ``now``.
_post = {}
for _label, _day in _DST_DAYS:
    _now = _day.replace(hour=12, minute=7)
    dt_util.freeze(_now)
    try:
        _prices = list(_dst_coord(_day)._forecast_arrays(_now).prices)
    finally:
        dt_util.freeze(None)
    _q0 = _now.replace(minute=0).astimezone(UTC)
    _want = [
        _price_for(_q0 + timedelta(minutes=FORECAST_STEP_MINUTES * i))
        for i in range(len(_prices))
    ]
    _post[_label] = sum(1 for g, w in zip(_prices, _want) if g != w)
R.check(
    "at noon on every transition day the grid starts at now's own quarter",
    all(_post[k] == 0 for k in _post if k != "plain") and len(_prices) > 0,
    f"{_post}",
)
R.check(
    "NULL CONTROL: the plain day's noon grid was always aligned",
    _post["plain"] == 0,
    f"{_post['plain']}",
)

R.section("naive stored stamps under the aware clock (round-9 D3-s1-91)")

# The main suite's identity-zone stub hands out a naive clock, where the
# tzinfo guards in ``_detect_outage`` and ``_immersion_dhw_margin`` never
# fire: deleting either left every check green. Here the clock is aware, a
# naive stored stamp is the user's wall time in the configured zone, and
# each guard decides the answer.
_AUG_NOON = datetime(2026, 8, 26, 12, 0, tzinfo=STHLM)


def _outage_after(minutes: float):
    coord = _age_coord({const.CONF_OUTAGE_RECOVERY_ENABLED: True})
    stamp = (_AUG_NOON - timedelta(minutes=minutes)).replace(tzinfo=None)
    dt_util.freeze(_AUG_NOON)
    try:
        coord._detect_outage(stamp.isoformat())
        return coord._outage_recovery_until
    except TypeError as err:
        return err
    finally:
        dt_util.freeze(None)


# 60 min past the gap floor as local wall time, but 60 min short of it if
# the stamp were read as UTC (Stockholm is UTC+2 in August).
_long = _outage_after(const.OUTAGE_GAP_MINUTES + 60.0)
_short = _outage_after(10.0)
R.check(
    "a naive last tick past the gap floor opens the outage window",
    isinstance(_long, datetime)
    and _long.astimezone(UTC)
    == _AUG_NOON.astimezone(UTC) + timedelta(hours=const.OUTAGE_RECOVERY_HOURS),
    f"recovery until {_long!r}",
)
R.check(
    "NULL CONTROL: a naive last tick 10 min ago opens nothing",
    _short is None,
    f"recovery until {_short!r}",
)

_ic = _age_coord({const.CONF_IMMERSION_FEEDBACK_ENABLED: True})
_ic._immersion_events = [
    (_AUG_NOON - timedelta(days=d)).replace(tzinfo=None).isoformat()
    for d in (1, 2, 3)
]
try:
    _margin = _ic._immersion_dhw_margin(_AUG_NOON)
except TypeError as err:
    _margin = err
R.check(
    "three naive immersion events inside 14 days ask for the readiness margin",
    _margin == 2.0,
    f"margin {_margin!r}",
)

# ``utc_elapsed_seconds`` reads a naive stamp as UTC, as Home Assistant's
# ``as_utc`` does. Under a UTC process zone ``astimezone`` does that anyway,
# so only a non-UTC process zone shows whether the naive-is-UTC line decides.
import os as _os  # noqa: E402
import time as _time  # noqa: E402

from heatpump_optimizer.accuracy import utc_elapsed_seconds  # noqa: E402

_saved_tz = _os.environ.get("TZ")
_os.environ["TZ"] = "Europe/Stockholm"
_time.tzset()
try:
    _zone_took = _time.localtime(1787270400).tm_gmtoff == 7200  # 2026-08-21
    _naive_gap = utc_elapsed_seconds(
        datetime(2026, 8, 26, 12, 0, tzinfo=UTC), datetime(2026, 8, 26, 12, 0)
    )
finally:
    if _saved_tz is None:
        _os.environ.pop("TZ", None)
    else:
        _os.environ["TZ"] = _saved_tz
    _time.tzset()
R.check(
    "a naive stamp is UTC to utc_elapsed_seconds under a non-UTC process zone",
    _zone_took and _naive_gap == 0.0,
    f"zone took {_zone_took}, gap {_naive_gap} s",
)

R.section("the UTC helpers themselves across both transitions (round-9 P7)")

# The tracer below judges arithmetic on zoned stamps. Once a helper has
# relabelled a stamp as UTC there is no zoned operation left to judge, so an
# error inside ``utc_elapsed_seconds`` or ``utc_shift`` is invisible to it
# (fix review of #1722: ``replace(tzinfo=UTC)`` for ``astimezone(UTC)`` put
# the P7 bug back with every check green). These pin the helpers directly.
from heatpump_optimizer.accuracy import utc_shift  # noqa: E402


_aut_a = datetime(2026, 10, 25, 1, 30, tzinfo=STHLM)  # 23:30Z, CEST
_aut_b = datetime(2026, 10, 25, 3, 30, tzinfo=STHLM)  # 02:30Z, CET
_spr_a = datetime(2026, 3, 29, 1, 30, tzinfo=STHLM)  # 00:30Z, CET
_spr_b = datetime(2026, 3, 29, 3, 30, tzinfo=STHLM)  # 01:30Z, CEST
_pln_a = datetime(2026, 10, 18, 1, 30, tzinfo=STHLM)
_pln_b = datetime(2026, 10, 18, 3, 30, tzinfo=STHLM)
_gaps_h = {
    "autumn": utc_elapsed_seconds(_aut_b, _aut_a) / 3600.0,
    "spring": utc_elapsed_seconds(_spr_b, _spr_a) / 3600.0,
    "plain": utc_elapsed_seconds(_pln_b, _pln_a) / 3600.0,
}
R.check(
    "utc_elapsed_seconds reads 01:30 to 03:30 as 3 h on the autumn day and 1 h on the spring day",
    _gaps_h["autumn"] == 3.0 and _gaps_h["spring"] == 1.0,
    f"{_gaps_h}",
)
R.check(
    "NULL CONTROL: on a plain day 01:30 to 03:30 is 2 h",
    _gaps_h["plain"] == 2.0,
    f"{_gaps_h['plain']}",
)
_shift_aut = utc_shift(_aut_a, timedelta(hours=2))
_shift_spr = utc_shift(_spr_a, timedelta(hours=1))
R.check(
    "utc_shift of 01:30 by 2 h lands on 02:30+01:00 (autumn) and by 1 h on 03:30+02:00 (spring)",
    (_shift_aut.hour, _shift_aut.minute, _shift_aut.utcoffset()) == (2, 30, timedelta(hours=1))
    and _shift_aut.astimezone(UTC) == datetime(2026, 10, 25, 1, 30, tzinfo=UTC)
    and (_shift_spr.hour, _shift_spr.minute, _shift_spr.utcoffset()) == (3, 30, timedelta(hours=2))
    and _shift_spr.astimezone(UTC) == datetime(2026, 3, 29, 1, 30, tzinfo=UTC)
    and _shift_aut.tzinfo is STHLM,
    f"autumn {_shift_aut.isoformat()} spring {_shift_spr.isoformat()}",
)

# ``_detect_outage``'s two windows across the autumn fold: 02:30 CEST (the
# first reading) plus 2 h recovery and 45 min DHW delay both land after the
# clocks go back, where a wall-clock ``+`` puts each an hour late.
_OUT_NOW = datetime(2026, 10, 25, 2, 30, tzinfo=STHLM)  # fold 0: 00:30Z


def _outage_windows():
    coord = _age_coord({const.CONF_OUTAGE_RECOVERY_ENABLED: True})
    last = (_OUT_NOW.astimezone(UTC)
            - timedelta(minutes=const.OUTAGE_GAP_MINUTES + 60.0)).astimezone(STHLM)
    dt_util.freeze(_OUT_NOW)
    try:
        coord._detect_outage(last.isoformat())
    finally:
        dt_util.freeze(None)
    return coord._outage_recovery_until, coord._outage_dhw_until


_rec_until, _dhw_until = _outage_windows()
_now_utc = _OUT_NOW.astimezone(UTC)
R.check(
    "an outage across the autumn fold opens both windows at their true instants",
    isinstance(_rec_until, datetime) and isinstance(_dhw_until, datetime)
    and _rec_until.astimezone(UTC) == _now_utc + timedelta(hours=const.OUTAGE_RECOVERY_HOURS)
    and _dhw_until.astimezone(UTC) == _now_utc + timedelta(minutes=const.OUTAGE_DHW_DELAY_MINUTES),
    f"now {_now_utc.isoformat()} recovery {_rec_until!r} dhw {_dhw_until!r}",
)

R.section("the DST tracer over replayed transition days (round-9 P7 barrier)")

# The class barrier for P7 (#1665): the committed replay day, shifted onto
# two transition days and a plain one, runs through ``replay.run_fixture``
# -- the real ``_async_update_data`` and every published entity -- with the
# clock Home Assistant hands out wrapped so every datetime it returns is
# traced. A subtraction of two stamps sharing the zone, or a ``+ timedelta``
# on one, whose result differs from the true (UTC) arithmetic is a wall-clock
# seam, keyed on (file, function). The static enumerator cannot see a site
# whose operands it does not name (``result.timestamps``); this reads what
# production computed. ``tariff._window_slot`` is exempt by definition: it
# labels a wall-clock tariff window, where the wall reading is the answer.
# The fixture's stamps are read in the zone (``replay._ts`` patched), the
# recorder export's own reading, so the lane's step walk is measured too:
# stepping a zoned clock by wall time drops the autumn day's repeated hour
# (round-9 D14-s4-02, G3-V2).
import json  # noqa: E402
import logging as _logging  # noqa: E402
import re  # noqa: E402
import tempfile  # noqa: E402
from pathlib import Path  # noqa: E402

import replay  # noqa: E402
from heatpump_optimizer import coordinator as cm  # noqa: E402

_PKG = "/custom_components/heatpump_optimizer/"
_WALL_SEAMS: dict[tuple[str, str], int] = {}
_QUIET = [0]
_EXEMPT = {("tariff.py", "_window_slot")}


def _seam(err_s: float) -> None:
    if _QUIET[0] or abs(err_s) < 1e-6:
        return
    frame = sys._getframe(2)
    while frame is not None and frame.f_code.co_filename == __file__:
        frame = frame.f_back
    if frame is not None and _PKG in frame.f_code.co_filename.replace("\\", "/"):
        key = (Path(frame.f_code.co_filename).name, frame.f_code.co_name)
        _WALL_SEAMS[key] = _WALL_SEAMS.get(key, 0) + 1


def _judge_add(a: datetime, delta: timedelta, res: datetime) -> None:
    if isinstance(a.tzinfo, ZoneInfo):
        _seam(datetime.timestamp(res) - datetime.timestamp(a) - delta.total_seconds())


class _Traced(datetime):
    """A clock value whose arithmetic reports itself against the UTC truth."""

    def __sub__(self, other):
        res = datetime.__sub__(self, other)
        if isinstance(other, datetime) and res is not NotImplemented:
            if self.tzinfo is other.tzinfo and isinstance(self.tzinfo, ZoneInfo):
                true = datetime.timestamp(self) - datetime.timestamp(other)
                _seam(res.total_seconds() - true)
        elif isinstance(other, timedelta) and res is not NotImplemented:
            _judge_add(self, -other, res)
        return res

    def __rsub__(self, other):
        if not isinstance(other, datetime):
            return NotImplemented
        res = datetime.__sub__(other, self)
        if other.tzinfo is self.tzinfo and isinstance(self.tzinfo, ZoneInfo):
            true = datetime.timestamp(other) - datetime.timestamp(self)
            _seam(res.total_seconds() - true)
        return res

    def __add__(self, other):
        res = datetime.__add__(self, other)
        if isinstance(other, timedelta) and res is not NotImplemented:
            _judge_add(self, other, res)
        return res

    __radd__ = __add__

    def astimezone(self, tz=None):
        # ZoneInfo.fromutc adds its offset on the subclass: the conversion
        # itself, not production arithmetic.
        _QUIET[0] += 1
        try:
            return datetime.astimezone(self, tz)
        finally:
            _QUIET[0] -= 1


def _traced(value):
    if isinstance(value, datetime) and not isinstance(value, _Traced):
        return _Traced(
            value.year, value.month, value.day, value.hour, value.minute,
            value.second, value.microsecond, value.tzinfo, fold=value.fold,
        )
    return value


_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?[+-]\d{2}:\d{2}$")


def _shifted(node, delta: timedelta):
    """The committed day moved by one absolute delta, re-rendered in the zone."""
    if isinstance(node, str) and _ISO.match(node):
        moved = datetime.fromisoformat(node) + delta
        zone = UTC if moved.utcoffset() == timedelta(0) else STHLM
        return moved.astimezone(zone).isoformat()
    if isinstance(node, list):
        return [_shifted(x, delta) for x in node]
    if isinstance(node, dict):
        return {k: _shifted(v, delta) for k, v in node.items()}
    return node


_REPLAY_SRC = json.loads(Path("tests/replay/synthetic-dhw-only.json").read_text())
_REPLAY_DAY0 = datetime.fromisoformat(_REPLAY_SRC["window"]["start"])
_TRACE_HOURS = 5  # both transitions fall inside 00:00-05:00 true time
_TRACE_DAYS = (
    ("spring", datetime(2026, 3, 29, tzinfo=STHLM)),
    ("autumn", datetime(2026, 10, 25, tzinfo=STHLM)),
    ("plain", datetime(2026, 10, 18, tzinfo=STHLM)),
)
_saved_clock = {
    n: getattr(dt_util, n)
    for n in ("now", "utcnow", "as_local", "as_utc", "parse_datetime")
}
_saved_ts = replay._ts
# The lane's forecast walk and recorded price walk, captured per day: the
# cycle count alone does not see either walk or the price labels.
import harness  # noqa: E402

_saved_call = harness.FakeServices.async_call
_saved_update = cm.HeatPumpOptimizerCoordinator._async_update_data
_walks: dict[str, dict[str, list]] = {}
_walk_label = [""]


async def _capturing_call(self, domain, service, data=None, **kwargs):
    res = await _saved_call(self, domain, service, data, **kwargs)
    if (domain, service) == ("weather", "get_forecasts") and res:
        for body in res.values():
            _walks[_walk_label[0]]["forecasts"].append(
                [row["datetime"] for row in body.get("forecast", [])])
    return res


async def _capturing_update(self):
    fetch = self.__dict__.get("_fetch_tibber_prices")
    if fetch is not None and not getattr(fetch, "_captures", False):
        async def captured():
            await fetch()
            _walks[_walk_label[0]]["prices"] = [row["starts_at"] for row in self._prices]
        captured._captures = True
        self._fetch_tibber_prices = captured
    return await _saved_update(self)


def _traced_replay(
    options: dict | None = None,
    *,
    before_cycle=None,
    solve_fails: range = range(0),
    on_day=None,
) -> dict[str, tuple[int, int, list]]:
    """The three days through the traced clock: (cycles, failed, seams) each.

    ``options`` is laid over the fixture's entry options (a configured seam is
    reached only when its option is on); ``before_cycle(coordinator, day, n)``
    is awaited ahead of cycle ``n`` (a manual plan applied by the real
    service); ``solve_fails`` names the cycles whose solve raises, so the plan
    keeps its earlier stamps and the next cycles read them across the
    transition. A seam is keyed by (file, function), as the tracer reports it.
    """
    out: dict[str, tuple[int, int, list]] = {}
    cycle_no = [0]
    saved_update = cm.HeatPumpOptimizerCoordinator._async_update_data
    saved_process = cm._await_process

    async def counting_update(self):
        n = cycle_no[0]
        cycle_no[0] += 1
        if before_cycle is not None:
            await before_cycle(self, _day_now[0], n)
        return await saved_update(self)

    async def failing_process(*args, **kwargs):
        if cycle_no[0] - 1 in solve_fails:
            raise RuntimeError("the solve failed (the straddle arm)")
        return await saved_process(*args, **kwargs)

    _day_now = [None]
    with tempfile.TemporaryDirectory() as tmp:
        try:
            for n, f in _saved_clock.items():
                setattr(dt_util, n, (lambda f: lambda *a, **k: _traced(f(*a, **k)))(f))
            replay._ts = lambda raw: (
                datetime.fromisoformat(raw).astimezone(STHLM) if raw else None
            )
            cm.HeatPumpOptimizerCoordinator._async_update_data = counting_update
            if solve_fails:
                cm._await_process = failing_process
                _logging.disable(_logging.CRITICAL)  # the failed solves' tracebacks are the arm's input
            for label, day in _TRACE_DAYS:
                if on_day is not None:
                    on_day(label)
                cycle_no[0] = 0
                _day_now[0] = day
                fx = _shifted(_REPLAY_SRC, day.astimezone(UTC) - _REPLAY_DAY0.astimezone(UTC))
                fx["entry"]["options"].update(options or {})
                end = day.astimezone(UTC) + timedelta(hours=_TRACE_HOURS)
                fx["window"] = {
                    "start": day.isoformat(),
                    "end": end.astimezone(STHLM).isoformat(),
                }
                path = Path(tmp) / f"dst-{label}.json"
                path.write_text(json.dumps(fx))
                before = dict(_WALL_SEAMS)
                run = replay.run_fixture(path, 30)
                out[label] = (
                    run["cycles"],
                    run["counts"]["cycle"],
                    sorted(
                        k for k, v in _WALL_SEAMS.items()
                        if v != before.get(k, 0) and k not in _EXEMPT
                    ),
                )
        finally:
            _logging.disable(_logging.NOTSET)
            cm.HeatPumpOptimizerCoordinator._async_update_data = saved_update
            cm._await_process = saved_process
            replay._ts = _saved_ts
            for n, f in _saved_clock.items():
                setattr(dt_util, n, f)
    return out


try:
    harness.FakeServices.async_call = _capturing_call
    cm.HeatPumpOptimizerCoordinator._async_update_data = _capturing_update
    _traced_days = _traced_replay(on_day=lambda label: (
        _walk_label.__setitem__(0, label),
        _walks.__setitem__(label, {"forecasts": [], "prices": []}),
    ))
finally:
    harness.FakeServices.async_call = _saved_call
    cm.HeatPumpOptimizerCoordinator._async_update_data = _saved_update

# The committed day prices from a price entity, so the lane's own recorded
# price walk (the Tibber path) never runs above. One hour of the same days
# with the Tibber source and the price entity as the recorded series reaches
# it, untraced: this pins the walk and its labels, not production.
with tempfile.TemporaryDirectory() as _tmp:
    try:
        harness.FakeServices.async_call = _capturing_call
        cm.HeatPumpOptimizerCoordinator._async_update_data = _capturing_update
        replay._ts = lambda raw: (
            datetime.fromisoformat(raw).astimezone(STHLM) if raw else None
        )
        for _label, _day in _TRACE_DAYS:
            _walk_label[0] = _label
            _fx = _shifted(_REPLAY_SRC, _day.astimezone(UTC) - _REPLAY_DAY0.astimezone(UTC))
            _fx["entry"]["data"]["price_source"] = const.PRICE_SOURCE_TIBBER
            _fx["price_series_entity"] = _fx["entry"]["data"]["price_entity"]
            _fx["window"] = {
                "start": _day.isoformat(),
                "end": (_day.astimezone(UTC) + timedelta(hours=1)).astimezone(STHLM).isoformat(),
            }
            _path = Path(_tmp) / f"walk-{_label}.json"
            _path.write_text(json.dumps(_fx))
            replay.run_fixture(_path, 30)
    finally:
        harness.FakeServices.async_call = _saved_call
        cm.HeatPumpOptimizerCoordinator._async_update_data = _saved_update
        replay._ts = _saved_ts

_want_cycles = _TRACE_HOURS * 2
R.check(
    "the replay lane steps a zoned clock in UTC: every day runs its true cycles",
    all(v[0] == _want_cycles and v[1] == 0 for v in _traced_days.values()),
    f"(cycles, cycle failures) per day "
    f"{ {k: v[:2] for k, v in _traced_days.items()} }, want {_want_cycles}",
)


def _walk_steps(stamps: list) -> set:
    """The distinct true steps, in seconds, between consecutive stamps."""
    ts = [datetime.fromisoformat(x).timestamp() for x in stamps]
    return {b - a for a, b in zip(ts, ts[1:])}


def _labels_in_zone(stamps: list) -> bool:
    return all(
        datetime.fromisoformat(x).utcoffset()
        == datetime.fromisoformat(x).astimezone(STHLM).utcoffset()
        for x in stamps
    )


_walk_facts = {
    k: (
        len(v["forecasts"]),
        set().union(*(_walk_steps(f) for f in v["forecasts"])) if v["forecasts"] else set(),
        len(v["prices"]),
        _walk_steps(v["prices"]),
        _labels_in_zone(v["prices"]),
    )
    for k, v in _walks.items()
}
R.check(
    "the replay lane's forecast walk steps one true hour, across both transitions",
    all(f[0] > 0 and f[1] == {3600.0} for f in _walk_facts.values()),
    f"(forecast calls, steps) {({k: f[:2] for k, f in _walk_facts.items()})}",
)
R.check(
    "the replay lane's price walk labels every true quarter of the day in the zone",
    _walk_facts["spring"][2:] == (92, {900.0}, True)
    and _walk_facts["autumn"][2:] == (100, {900.0}, True)
    and _walk_facts["plain"][2:] == (96, {900.0}, True),
    f"(quarters, steps, labels in zone) {({k: f[2:] for k, f in _walk_facts.items()})}",
)
R.check(
    "no production seam does wall-clock arithmetic across either transition",
    not _traced_days["spring"][2] and not _traced_days["autumn"][2],
    f"spring {_traced_days['spring'][2]} autumn {_traced_days['autumn'][2]}",
)
R.check(
    "NULL CONTROL: the plain day reads no seam, and the tracer did run",
    not _traced_days["plain"][2]
    and _WALL_SEAMS.get(("tariff.py", "_window_slot"), 0) > 0,
    f"plain {_traced_days['plain'][2]}, exempt label hits "
    f"{_WALL_SEAMS.get(('tariff.py', '_window_slot'), 0)}",
)


# ---------------------------------------------------------------------------
# The two arms the first tracer lacked (#1756). The run above replays one
# configuration with every solve succeeding, so it is blind in two ways its
# own barrier text did not name (RCA-BULK-1 section 1): a seam reached only
# through an option, and a seam that executes but whose operands never
# straddle the transition. Each arm answers one.
# ---------------------------------------------------------------------------
R.section("the manual override lasts its stated length in true time (#1756, D9)")

# ``now + timedelta(hours=20)`` on a zoned stamp adds wall clock: applied the
# evening before the autumn fold the override lasted 21 true hours, and the
# spring gap cut it to 19. The same sum clamps a far ``expires_at`` in
# ``build_override`` and ends each step in ``channel_pins``.
from harness import FakeServiceCall  # noqa: E402
from heatpump_optimizer import services as _services  # noqa: E402
from heatpump_optimizer.accuracy import utc_elapsed_seconds as _elapsed_s  # noqa: E402
from homeassistant.config_entries import ConfigEntryState  # noqa: E402
from heatpump_optimizer.manual_plan import build_override  # noqa: E402

_override_hours = {}
for _label, _evening in (
    ("autumn", datetime(2026, 10, 24, 23, 0, tzinfo=STHLM)),
    ("spring", datetime(2026, 3, 28, 23, 0, tzinfo=STHLM)),
    ("plain", datetime(2026, 10, 17, 23, 0, tzinfo=STHLM)),
):
    _hass = FakeHass()
    _entry = FakeEntry(data={}, entry_id=f"override-{_label}")
    _coord = HeatPumpOptimizerCoordinator(_hass, _entry)

    async def _no_refresh(*_a, **_k):
        return None

    _coord.async_request_refresh = _no_refresh
    _entry.state = ConfigEntryState.LOADED
    _entry.runtime_data = _coord
    _hass.config_entries.entries.append(_entry)
    dt_util.freeze(_evening)
    try:
        asyncio.run(
            _services.handle_apply_manual_plan(
                _hass,
                FakeServiceCall("heatpump_optimizer", "apply_manual_plan", {"dhw_slots": []}),
            )
        )
        _far = build_override(
            dhw_slots=[], space_slots=None, now=_evening,
            expires_at=_evening + timedelta(hours=48),
        )
    finally:
        dt_util.freeze(None)
    _override_hours[_label] = (
        _elapsed_s(_coord._manual_override.expires_at, _evening) / 3600.0,
        _elapsed_s(_far.expires_at, _evening) / 3600.0,
    )
R.check(
    "a default override applied the evening before either transition lasts 20 true hours",
    all(v[0] == const.MANUAL_PLAN_WINDOW_HOURS for v in _override_hours.values()),
    f"(default, clamped far expiry) hours {_override_hours}",
)
R.check(
    "a far expires_at is clamped to the same 20 true hours",
    all(v[1] == const.MANUAL_PLAN_WINDOW_HOURS for v in _override_hours.values()),
    f"{_override_hours}",
)
R.check(
    "NULL CONTROL: on a plain day the 20 hours were always right",
    _override_hours["plain"] == (20.0, 20.0),
    f"{_override_hours['plain']}",
)

# ``channel_pins`` judges a step by overlap with ``[ref, ref + step)``. The
# step 02:45 CEST on the autumn day ends at 02:00 CET, a true quarter hour
# later; wall-added it ends at 03:00 CET, an hour and a quarter later, and a
# slot starting at 02:30 CET (30 true minutes after the step ended) then
# overlaps it and pins it on.
_pin_step = datetime(2026, 10, 25, 2, 45, tzinfo=STHLM)  # fold 0: 00:45Z
_pin_far = datetime(2026, 10, 25, 2, 30, fold=1, tzinfo=STHLM)  # 01:30Z
_pin_near = datetime(2026, 10, 25, 2, 50, tzinfo=STHLM)  # 00:50Z, inside the step


def _pin_for(slot_start: datetime):
    override = ManualOverride(
        space_slots=None,
        dhw_slots=[(slot_start, slot_start + timedelta(hours=1))],
        expires_at=datetime(2026, 10, 26, 2, 0, tzinfo=STHLM),
    )
    return override.channel_pins("dhw", [_pin_step], timedelta(minutes=15))


R.check(
    "a step ending at the autumn fold stays off for a slot that starts 30 true minutes after it",
    _pin_for(_pin_far) == [PIN_OFF],
    f"pins {_pin_for(_pin_far)}",
)
R.check(
    "NULL CONTROL: a slot that starts inside the step still pins it on",
    _pin_for(_pin_near) == [PIN_ON],
    f"pins {_pin_for(_pin_near)}",
)

R.section("the DST tracer: config arm and straddle arm (#1756)")

_CAPACITY_MASK = {
    const.CONF_PEAK_TARIFF_ENABLED: True,
    const.CONF_PEAK_TARIFF_HOURS: "07:00-19:00",
    const.CONF_PEAK_TARIFF_OFFPEAK_FACTOR: 0.5,
}
_MANUAL_PLAN_AT = 1  # cycle ahead of both transitions (00:30 true time)


async def _apply_plan_before_fold(coord, day, n):
    """The apply service, as the card calls it, once, ahead of the fold."""
    if n != _MANUAL_PLAN_AT:
        return

    async def no_refresh(*_a, **_k):
        return None

    coord.async_request_refresh = no_refresh
    coord.entry.state = ConfigEntryState.LOADED
    coord.entry.runtime_data = coord
    coord.hass.config_entries.entries.append(coord.entry)
    start = (day.astimezone(UTC) + timedelta(hours=1)).astimezone(STHLM)
    end = (day.astimezone(UTC) + timedelta(hours=6)).astimezone(STHLM)
    await _services.handle_apply_manual_plan(
        coord.hass,
        FakeServiceCall(
            "heatpump_optimizer", "apply_manual_plan",
            {"dhw_slots": [{"start": start.isoformat(), "end": end.isoformat()}]},
        ),
    )


_arm_runs = {
    f"tariff {w} min": _traced_replay(
        {**_CAPACITY_MASK, const.CONF_PEAK_TARIFF_WINDOW: w},
        before_cycle=_apply_plan_before_fold,
    )
    for w in (15, 60)
}
_arm_runs["straddle"] = _traced_replay(solve_fails=range(3, 7))


def _arm_seams(run: dict, days=("spring", "autumn")) -> dict:
    return {k: v[2] for k, v in run.items() if k in days and v[2]}


R.check(
    "every arm runs its true cycles on every day, none failing outright",
    all(
        v[0] == _want_cycles and v[1] == 0
        for run in _arm_runs.values() for v in run.values()
    ),
    f"(cycles, failed) { {a: {k: v[:2] for k, v in r.items()} for a, r in _arm_runs.items()} }",
)
for _arm, _run in _arm_runs.items():
    R.check(
        f"arm [{_arm}]: no production seam does wall-clock arithmetic across either transition",
        not _arm_seams(_run),
        f"{_arm_seams(_run)}",
    )
    R.check(
        f"NULL CONTROL arm [{_arm}]: the plain day reads no seam",
        not _run["plain"][2],
        f"{_run['plain'][2]}",
    )

R.section("rate limiters, retry stamps and manual-plan compares across the fold (round-9 F10.1d)")

# Every site below subtracted or compared two stamps that share the one
# ZoneInfo object, which CPython reads as wall clock. LAST/NOW are 02:55 on
# the autumn fold day, a true hour apart and a wall zero apart.
_FOLD_LAST = datetime(2026, 10, 25, 2, 55, tzinfo=STHLM)  # 00:55Z
_FOLD_NOW = datetime(2026, 10, 25, 2, 55, tzinfo=STHLM, fold=1)  # 01:55Z
_FOLD_NOW_10M = datetime(2026, 10, 25, 2, 5, tzinfo=STHLM, fold=1)  # 01:05Z
_FOLD_LAST_S = _FOLD_LAST.astimezone(UTC)
_PLAIN_LAST = datetime(2026, 10, 24, 2, 55, tzinfo=STHLM)
_PLAIN_NOW = datetime(2026, 10, 24, 3, 55, tzinfo=STHLM)


def _fold_coord(hass=None, **cfg):
    base = {
        "tibber_token": "x",
        "weather_entity": "weather.home",
        "indoor_temp_entity": "sensor.indoor",
        "outdoor_temp_entity": "sensor.outdoor",
    }
    return HeatPumpOptimizerCoordinator(hass or FakeHass(), FakeEntry(data={**base, **cfg}))


from heatpump_optimizer import power_guard as _power_guard  # noqa: E402
from heatpump_optimizer import pump_arbiter as _arbiter  # noqa: E402
from heatpump_optimizer.freq_control import FREQ_MIN_SAMPLES  # noqa: E402
from heatpump_optimizer.manual_plan import build_override  # noqa: E402

for _label, _l, _n in (
    ("the fold hour", _FOLD_LAST, _FOLD_NOW),
    ("NULL CONTROL: a plain hour", _PLAIN_LAST, _PLAIN_NOW),
):
    _guard = _power_guard.GuardState()
    _guard._last_event = _l
    R.check(f"{_label}: a meter event a true hour on is not throttled", not _guard.throttled(_n), "")

_arb_held = _arbiter.ArbiterState()
_real_setpoint_check = _arbiter.setpoint_check
_arbiter.setpoint_check = SimpleNamespace(create_issue=lambda *a, **k: None)
_arbiter._not_held(SimpleNamespace(hass=None), _arb_held, "mode", "x", _FOLD_LAST)
_arbiter.setpoint_check = _real_setpoint_check
_retry_min = (_arb_held.retry["mode"].astimezone(UTC) - _FOLD_LAST_S).total_seconds() / 60.0
R.check(
    "a pump write retry set on the fold night waits a true 5 minutes",
    _retry_min == _arbiter.RETRY_MINUTES,
    f"{_retry_min} min",
)
R.check(
    "and is due once those 5 true minutes have passed, not an hour of wall clock later",
    utc_elapsed_seconds(_FOLD_NOW, _arb_held.retry["mode"]) >= 0,
    "",
)

# The arbiter's two other seams: the echo grace in ``hold`` and the retry gate
# in ``_write``. A write at 02:59 CEST read back at 02:00 CET is a true 60 s,
# past the 20 s grace, though the wall difference is -3540 s; a retry stamped
# 5 true minutes after a 02:58 CEST failure is labelled 02:03 CET, which the
# wall clock has already passed.
_arb_hass = FakeHass()
_arb_hass.states.set("number.dhw", FakeState("55"))


class _ArbCoord:  # weak-referenceable, as the arbiter's WeakKeyDictionary needs
    hass = _arb_hass
    _config = {const.CONF_DHW_SETPOINT_ENTITY: "number.dhw"}


_arb_coord = _ArbCoord()
_echo_at = datetime(2026, 10, 25, 2, 59, tzinfo=STHLM)
_echo_now = datetime(2026, 10, 25, 2, 0, tzinfo=STHLM, fold=1)
_echo_held = _arbiter.state_for(_arb_coord)
_echo_held.written["dhw_setpoint"] = (60.0, _echo_at)
_arbiter.hold(_arb_coord, _echo_now)
R.check(
    "a pump write read back a true 60 s later across the fold is past its 20 s echo grace",
    _echo_held.misses.get("dhw_setpoint") == 1,
    f"misses {dict(_echo_held.misses)}",
)
_echo_held.written.clear()
_echo_held.misses.clear()
_echo_held.written["dhw_setpoint"] = (60.0, _PLAIN_LAST)
_arbiter.hold(_arb_coord, _PLAIN_NOW)
R.check(
    "NULL CONTROL: a plain-hour write read back an hour later is past its grace",
    _echo_held.misses.get("dhw_setpoint") == 1,
    f"misses {dict(_echo_held.misses)}",
)
_gate_failed_at = datetime(2026, 10, 25, 2, 58, tzinfo=STHLM)
_echo_held.retry["dhw_setpoint"] = utc_shift(_gate_failed_at, timedelta(minutes=_arbiter.RETRY_MINUTES))
_echo_held.written.clear()
try:
    asyncio.run(_arbiter._write(_arb_coord, "dhw_setpoint", 60.0, _gate_failed_at))
except Exception:  # noqa: BLE001 - the write path past the gate is not under test
    pass
R.check(
    "a pump write retry stamped 5 true minutes after a 02:58 CEST failure still holds at 02:58 CEST",
    "dhw_setpoint" not in _echo_held.written and not _arb_hass.services.calls,
    f"written {dict(_echo_held.written)}, calls {len(_arb_hass.services.calls)}",
)
_spring_guard = _power_guard.GuardState()
_spring_guard._last_event = datetime(2026, 3, 29, 1, 59, 58, tzinfo=STHLM)
R.check(
    "spring gap: a meter event a true 5 s after the last is throttled, not 62 minutes of wall clock on",
    _spring_guard.throttled(datetime(2026, 3, 29, 3, 0, 3, tzinfo=STHLM)),
    "",
)

dt_util.freeze(_FOLD_NOW)
_c = _fold_coord(**{const.CONF_SNOW_ROOF_FACTOR_ENABLED: True})
# The heavy-snow hold: 2.5 true days after the last heavy fall it has lapsed
# (SNOW_ROOF_DAYS is 2), though the wall clock reads 1 day 23 h 30 min.
_c._last_heavy_snow = datetime(2026, 10, 23, 2, 55, tzinfo=STHLM)
_c._snow_accum_last = None
_hold_now = datetime(2026, 10, 25, 2, 25, tzinfo=STHLM, fold=1)
R.check(
    "the roof-snow hold has lapsed 2 days 30 true minutes after the last heavy fall",
    _c._update_snow_memory(_hold_now, np.zeros(4)) is False,
    "",
)
_c._last_heavy_snow = datetime(2026, 10, 23, 2, 55, tzinfo=STHLM)
R.check(
    "NULL CONTROL: the same hold is still on a true 1 day 23 h 30 min after",
    _c._update_snow_memory(datetime(2026, 10, 25, 2, 25, tzinfo=STHLM), np.zeros(4)) is True,
    "",
)
_c = _fold_coord(**{const.CONF_SNOW_ROOF_FACTOR_ENABLED: True})
_c._snow_accum_last, _c._snow_accum_cm = _FOLD_LAST, 10.0
_c._update_snow_memory(_FOLD_NOW, np.zeros(4))
R.check(
    "snow memory decays over the true hour of the fold, not the wall zero",
    abs(_c._snow_accum_cm - 10.0 * np.exp(-1 / 24)) < 1e-9,
    f"{_c._snow_accum_cm}",
)

_c = _fold_coord()
_c._last_simulation = _FOLD_LAST
_sim = asyncio.run(_c.async_simulate({}, limited=True))
R.check(
    "the what-if limiter lets a call a true hour after the last one through",
    _sim.get("rate_limited") is False,
    f"{_sim}",
)

dt_util.freeze(_FOLD_NOW_10M)
_c = _fold_coord(
    peak_guard_enabled=True,
    house_power_entity="sensor.house_power",
    main_fuse_amperes=16.0,
    main_fuse_phases=1,
    **{const.CONF_PEAK_TARIFF_ENABLED: True},
)
_seen: list = []
_c._peak_tracker.observe = lambda *a, **k: _seen.append(k.get("dt_hours"))
_c._guard_last_fold = _FOLD_LAST
_c._on_power_event(SimpleNamespace(data={"new_state": FakeState("6500", unit="W")}))
R.check(
    "the meter fold weighs a sample by its true 10 minutes across the fold",
    len(_seen) == 1 and _seen[0] is not None and abs(_seen[0] - 1 / 6) < 1e-9,
    f"{_seen}",
)

dt_util.freeze(_FOLD_NOW)
_hass = FakeHass()
_hass.states.set("number.freq", FakeState("45", attributes={"min": 20.0, "max": 120.0}))
_c = _fold_coord(_hass, compressor_freq_entity="number.freq", freq_control_mode="control")
_c._measured_power = 2.0
_c._current_action = {"power": 1.5, "dhw_power": 0.5}
for _ in range(FREQ_MIN_SAMPLES + 1):
    _c._freq_map.observe(45.0, 2.0, 20.0, 120.0)
_c._freq_last_write = _FOLD_LAST
asyncio.run(_c._command_frequency())
R.check(
    "a compressor frequency write a true hour after the last one is not rate-limited",
    len(_hass.services.calls) == 1,
    f"{len(_hass.services.calls)} writes",
)

_mp_now = datetime(2026, 10, 24, 6, 30, tzinfo=STHLM)
_mp_exp = datetime(2026, 10, 25, 2, 15, tzinfo=STHLM, fold=1)  # 45 true min past the cap
_built = build_override(dhw_slots=[], space_slots=[], expires_at=_mp_exp, now=_mp_now)
R.check(
    "a far expiry applied the morning before the fold clamps to 20 true hours",
    (_built.expires_at.timestamp() - _mp_now.timestamp()) / 3600.0 == 20.0,
    f"{(_built.expires_at.timestamp() - _mp_now.timestamp()) / 3600.0} h",
)
_mp_over = ManualOverride(
    space_slots=[], dhw_slots=[],
    expires_at=datetime(2026, 10, 25, 2, 30, tzinfo=STHLM, fold=1), created_at=_mp_now,
)
R.check(
    "an override expiring 02:30 CET is still running at 02:45 CEST, a true 45 minutes before",
    not _mp_over.is_expired(datetime(2026, 10, 25, 2, 45, tzinfo=STHLM)),
    "",
)
try:
    build_override(
        dhw_slots=[], space_slots=[],
        expires_at=datetime(2026, 10, 25, 2, 30, tzinfo=STHLM, fold=1),
        now=datetime(2026, 10, 25, 2, 45, tzinfo=STHLM),
    )
    _past_refused = False
except Exception as _exc:  # ManualPlanError
    _past_refused = "not in the future" in str(_exc)
R.check(
    "an expiry 02:30 CET is in the future of 02:45 CEST, so it is accepted",
    not _past_refused,
    "",
)
_plain = build_override(
    dhw_slots=[], space_slots=[],
    expires_at=datetime(2026, 10, 24, 2, 15, tzinfo=STHLM) + timedelta(days=3),
    now=datetime(2026, 10, 20, 6, 30, tzinfo=STHLM),
)
R.check(
    "NULL CONTROL: on a plain day the same far expiry was always 20 hours",
    (_plain.expires_at.timestamp() - datetime(2026, 10, 20, 6, 30, tzinfo=STHLM).timestamp()) / 3600.0 == 20.0,
    "",
)


sys.exit(R.close("DST / QUARTER-GRID CHECKS"))
