import sys

sys.path.insert(
    0, "/tmp/claude-0/-home-user/67fb38f0-9f88-5c6b-9d2e-78b6cb07f57d/scratchpad"
)
from _common import (
    S,
    show,
    datetime,
    dt_util,
    coord,
    true_s,
)
from heatpump_optimizer import boost, away
from heatpump_optimizer.const import CONF_OUTAGE_RECOVERY_ENABLED


def mk():
    c = coord(**{CONF_OUTAGE_RECOVERY_ENABLED: True})
    c._thermal_params.dhw_enabled = (
        False  # so _outage_dhw_hold is decided by the stamp alone
    )
    return c


def detect(c, at):
    dt_util.freeze(at)
    try:
        c._detect_outage("2020-01-01T00:00:00+00:00")
    finally:
        dt_util.freeze(None)
    return c


# --- coordinator.py:8543 recovery window = 2 h
# set 01:30 CEST (23:30Z) -> until 01:30Z (02:30 CET fold1). At 02:45 CEST fold0 (00:45Z) true 1h15 into the window.
c = detect(mk(), datetime(2026, 10, 25, 1, 30, tzinfo=S))
t = datetime(2026, 10, 25, 2, 45, tzinfo=S)
print(
    "   until",
    c._outage_recovery_until,
    "true remaining h",
    true_s(c._outage_recovery_until, t) / 3600,
)
show(
    "coordinator.py:8543 recovery still active at true 45min before end",
    c._outage_recovery_active(t),
    True,
)
# until 02:50 CEST fold0 (00:50Z); set 00:50 CEST?? use 2h window: set 00:50Z-2h => 22:50Z = 00:50 CEST
c = detect(mk(), datetime(2026, 10, 25, 0, 50, tzinfo=S))
t = datetime(
    2026, 10, 25, 2, 20, tzinfo=S, fold=1
)  # 01:20Z, true 30 min after until=00:50Z? (until=02:50Z-?)
print(
    "   until",
    c._outage_recovery_until,
    "true",
    true_s(t, c._outage_recovery_until) / 60,
    "min after until",
)
show(
    "coordinator.py:8543 recovery expired when true now is after until",
    c._outage_recovery_active(t),
    true_s(t, c._outage_recovery_until) < 0,
)

# --- coordinator.py:8554 DHW queue = 45 min
c = detect(
    mk(), datetime(2026, 10, 25, 2, 20, tzinfo=S)
)  # 00:20Z -> until 01:05Z (02:05 CET fold1)
t = datetime(2026, 10, 25, 2, 30, tzinfo=S)  # 00:30Z: true 35 min before until
print(
    "   until",
    c._outage_dhw_until,
    "true remaining min",
    true_s(c._outage_dhw_until, t) / 60,
)
show(
    "coordinator.py:8554 DHW hold still on at true 35min before end",
    c._outage_dhw_hold(t),
    True,
)
c = detect(
    mk(), datetime(2026, 10, 25, 2, 5, tzinfo=S)
)  # 00:05Z -> until 00:50Z (02:50 CEST fold0)
t = datetime(2026, 10, 25, 2, 20, tzinfo=S, fold=1)  # 01:20Z: true 30 min after until
print(
    "   until",
    c._outage_dhw_until,
    "true now-until min",
    true_s(t, c._outage_dhw_until) / 60,
)
show(
    "coordinator.py:8554 DHW hold off at true 30min after end",
    c._outage_dhw_hold(t),
    False,
)

# --- boost.py:65-75, 81
print("--- boost")
held = boost.BoostState()
for lbl, setat, check, exp in (
    (
        "set 01:30 CEST (fold night), true +2h",
        datetime(2026, 10, 25, 1, 30, tzinfo=S),
        None,
        2.0,
    ),
    (
        "set 02:30 CEST fold0, true +2h",
        datetime(2026, 10, 25, 2, 30, tzinfo=S),
        None,
        2.0,
    ),
    (
        "set 01:30 CET before spring gap, true +2h",
        datetime(2026, 3, 29, 1, 30, tzinfo=S),
        None,
        2.0,
    ),
):
    held = boost.BoostState()
    held.set(boost.CHANNEL_DHW, True, setat)
    got = true_s(held.until[boost.CHANNEL_DHW], setat) / 3600.0
    show(f"boost.py:81 set() lasts true hours [{lbl}]", got, exp)
# active(): until 02:50 fold0 (00:50Z); now 02:20 fold1 (01:20Z) -> true 30 min past; must be inactive
held = boost.BoostState()
held.until[boost.CHANNEL_DHW] = datetime(2026, 10, 25, 2, 50, tzinfo=S)
now = datetime(2026, 10, 25, 2, 20, tzinfo=S, fold=1)
show(
    "boost.py:66 active() false once true 30min past end",
    held.active(boost.CHANNEL_DHW, now),
    False,
)
# until 02:30 fold1 (01:30Z); now 02:45 fold0 (00:45Z) -> 45 min still to run; must be active
held = boost.BoostState()
held.until[boost.CHANNEL_DHW] = datetime(2026, 10, 25, 2, 30, tzinfo=S, fold=1)
now = datetime(2026, 10, 25, 2, 45, tzinfo=S)
show(
    "boost.py:66 active() true with true 45min left",
    held.active(boost.CHANNEL_DHW, now),
    True,
)
held.expire(now)
show(
    "boost.py:70 expire() keeps it with true 45min left",
    boost.CHANNEL_DHW in held.until,
    True,
)
# expire clamp: until label far ahead is clamped to now+2h wall
held = boost.BoostState()
held.until[boost.CHANNEL_DHW] = datetime(
    2026, 10, 25, 4, 45, tzinfo=S
)  # 03:45Z: 3h00 true after now
now = datetime(2026, 10, 25, 2, 45, tzinfo=S)  # 00:45Z
held.expire(now)
got = true_s(held.until[boost.CHANNEL_DHW], now) / 3600.0
show("boost.py:72/75 expire() clamp to true 2h ahead", got, 2.0)

# --- away.py:249 expire_override and :469 _apply_return
print("--- away")
# naive-typed (zone = DEFAULT_TIME_ZONE ZoneInfo, as _parse_return_time makes it) vs now
ret = away._parse_return_time("2026-10-25T02:30:00")
print(
    "   typed return tz is the shared ZoneInfo:",
    ret.tzinfo is dt_util.DEFAULT_TIME_ZONE,
    "fold",
    ret.fold,
)
now_f1 = datetime(
    2026, 10, 25, 2, 45, tzinfo=S, fold=1
)  # 01:45Z; ret(fold0)=02:30 CEST=00:30Z -> true passed
show(
    "away.py:249 typed return 02:30(fold0) expired at 02:45 fold1",
    away.expire_override(True, ret, now_f1)[0],
    False,
)
# the form it takes after the production round trip: isoformat -> _parse_return_time
rt = away._parse_return_time(ret.isoformat())
print(
    "   round-tripped return",
    rt.isoformat(),
    "tz is shared ZoneInfo:",
    rt.tzinfo is dt_util.DEFAULT_TIME_ZONE,
    type(rt.tzinfo).__name__,
)
now_x = datetime(
    2026, 10, 25, 2, 15, tzinfo=S, fold=1
)  # 01:15Z; rt = 00:30Z -> true passed 45 min
show(
    "away.py:249 round-tripped (offset-bearing) return 02:30+02:00 expired at 02:15 fold1",
    away.expire_override(True, rt, now_x)[0],
    False,
)

# :469 hours_left through the real resolve() with a presence calendar attribute end_time (naive local string)
from heatpump_optimizer.thermal_model import (
    ThermalModel,
    ThermalParameters,
    ThermalState,
)

cfg = (
    away.AwayConfig(presence_entity="calendar.holiday")
    if hasattr(away, "AwayConfig")
    else None
)
model = ThermalModel(ThermalParameters.from_config({}))
ts = ThermalState(room_temperature=21.0, outdoor_temperature=0.0)
for lbl, now, endtxt in (
    (
        "fold: now 00:45 CEST, end 02:15 (typed, fold0 = 00:15Z+... )",
        datetime(2026, 10, 25, 0, 45, tzinfo=S),
        "2026-10-25 03:45:00",
    ),
    (
        "spring: now 01:00 CET, end 04:00 CEST",
        datetime(2026, 3, 29, 1, 0, tzinfo=S),
        "2026-03-29 04:00:00",
    ),
):
    st = away.resolve(
        away.AwayConfig(presence_entity="calendar.holiday"),
        now=now,
        presence_raw="on",
        presence_attributes={"end_time": endtxt},
        return_raw=None,
        comfort_temp=21.0,
        model=model,
        thermal_state=ts,
        outdoor_temp=0.0,
    )
    ret = away._parse_return_time(endtxt)
    exp = true_s(ret, now) / 3600.0
    show(f"away.py:469 hours_until_return [{lbl}]", st.hours_until_return, exp)

# --- away.py:249 through the PRODUCTION path (typed return via async_set_away, then _resolve_away on the fold)
import asyncio
print("--- away production path")
ret_typed = away._parse_return_time("2026-10-25T02:30:00")
now_pre = datetime(2026, 10, 25, 1, 0, tzinfo=S)
now_fold = datetime(2026, 10, 25, 2, 15, tzinfo=S, fold=1)  # 01:15Z; return 02:30 fold0 = 00:30Z -> already passed
# function-level (ZoneInfo stamp, the shape _parse_return_time returns for typed text): MISFIRES
show("away.py:249 expire_override with the ZoneInfo stamp (function level)", away.expire_override(True, ret_typed, now_fold)[0], False)
c = coord()
dt_util.freeze(now_pre)
asyncio.run(c.async_set_away(True, "2026-10-25T02:30:00", refresh=False))
print("   stored override_return_iso:", c._away_state.override_return_iso)
dt_util.freeze(now_fold)
try:
    c._spawn = lambda coro: coro.close()
    c._resolve_away()
finally:
    dt_util.freeze(None)
show("away.py:249 production path (_resolve_away) override expired once true return passed", c._away_state.override_active, False)
