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
from zoneinfo import ZoneInfo

from harness import FakeEntry, FakeHass, Results

import numpy as np

from homeassistant.util import dt as dt_util

from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
from heatpump_optimizer.manual_plan import ManualOverride, PIN_ON
from heatpump_optimizer.optimizer import OptimizationResult
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

anchor = coord._solve_anchor(dt_util.now())
R.check(
    "12:07:33 floors to 12:00:00 with tz and date intact",
    anchor == datetime(2026, 8, 26, 12, 0, tzinfo=STHLM)
    and anchor.tzinfo is FROZEN.tzinfo,
    f"got {anchor.isoformat()}",
)
R.check(
    "a boundary instant is its own anchor",
    coord._solve_anchor(datetime(2026, 8, 26, 12, 45, tzinfo=STHLM))
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

captured: dict[str, object] = {}
_real_state, _real_opt = coord._solve_snapshot()


class CapturingOptimizer:
    """Records optimize()'s anchor; timestamps built exactly as _Horizon's."""

    def __init__(self, inner):
        self._inner = inner

    def optimize(
        self, state, prices, outdoor, wind, precip, solar, start_time,
        *args, **kwargs
    ):
        captured["start_time"] = start_time
        n = len(prices)
        return OptimizationResult(
            power_schedule=[1.0] * n,
            room_temp_trajectory=[21.0] * (n + 1),
            slab_temp_trajectory=[22.0] * (n + 1),
            timestamps=[start_time + timedelta(hours=0.25 * i) for i in range(n)],
            prices=[float(p) for p in prices],
            predicted_cost=1.0,
            baseline_cost=1.0,
            predicted_savings=0.0,
            savings_percentage=0.0,
            optimal_setpoints=[21.0] * n,
            status="ok",
        )

    def get_current_action(self, result, now):
        return self._inner.get_current_action(result, now)


coord._solve_snapshot = lambda: (_real_state, CapturingOptimizer(_real_opt))
asyncio.run(coord.async_run_optimization())
result = coord._optimization_result

R.check(
    "optimize() receives the snapped anchor, not the raw 12:07 instant",
    captured.get("start_time") == anchor,
    f"got {captured.get('start_time')}",
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

sys.exit(R.close("DST / QUARTER-GRID CHECKS"))
