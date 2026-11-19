"""D17-s1 owed cell: the comfort page's weekend and holiday fields (PR 3013).

Metric: the comfort target the live solve reads for a given local hour and date,
captured by wrapping heatpump_optimizer.optimizer:OptimizationConfig.get_comfort_temp
during one full `_async_update_data` cycle on a coordinator rebuilt (a restart) from
an entry saved through the real comfort options page. Count key: the target value the
solve itself was handed (the production seam's return value), per (date, hour).
Each arm's expected target comes from strings.json's description of the field:
  weekend day/night "Preferred temperature during weekend waking hours / nights.
  Defaults to the weekday ... value."; start/end hour "when weekend daytime/night-time
  temperature takes over"; holiday "on days the holiday calendar is on ...
  Away setback still wins if away is active."

Command:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D17/s1/h_owed.py
Expected: RESULT owed_checks=18, RESULT owed_fail=1 (the kept-weekend check, D17-s1-02) (exact);
          under --perturb-weekend owed_fail=8
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B13
Perturbation: --perturb-weekend wraps OptimizationConfig.get_comfort_temp to hand it
the Friday before any weekend date (the weekend branch never taken):
every weekend-arm check fails, owed_fail goes up.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio  # noqa: E402
import sys  # noqa: E402
from datetime import datetime, timedelta, timezone  # noqa: E402
from unittest import mock  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig  # noqa: E402
from heatpump_optimizer import optimizer as omod  # noqa: E402

SAT = datetime(2026, 1, 17, 6, 0, tzinfo=timezone.utc)   # solve starts Saturday 06:00 UTC (24 h horizon)
THU = datetime(2026, 1, 15, 6, 0, tzinfo=timezone.utc)
PERTURB = "--perturb-weekend" in sys.argv
CHECKS, FAILS = [], []


def capture(entry, now, states=None):
    """{(date, hour): target} the solve read, from a fresh coordinator over ``entry``."""
    seen = {}
    real = omod.OptimizationConfig.get_comfort_temp

    def spy(self, hour, when=None):
        if PERTURB and when is not None and when.weekday() >= 5:
            when = when - timedelta(days=when.weekday() - 4)
        v = real(self, hour, when)
        if when is not None:
            seen[(when.date().isoformat(), int(hour))] = v
        return v

    with mock.patch.object(omod.OptimizationConfig, "get_comfort_temp", spy):
        hass, coord = rig.build_coord(entry, states=states, now=now)
        rig.run_cycles(coord, 1)
    return seen


def save(answers, options=None):
    """Submit the comfort page with ``answers`` over its own defaults."""
    async def go():
        flow, entry, hass = rig.new_flow(options=options)
        form = await flow.async_step_comfort(None)
        a = rig.schema_defaults(form)
        for f, v in answers.items():
            a.setdefault(rig.field_section(form, f), {})[f] = v
        res = await rig.submit(flow, "comfort", a)
        assert not res.get("errors"), (answers, res.get("errors"))
        return res, entry
    return asyncio.run(go())


def check(name, got, want):
    ok = got == want
    CHECKS.append(name)
    if not ok:
        FAILS.append(name)
    print(f"ROW {name} {'PASS' if ok else 'FAIL'} got={got} doc={want}", flush=True)


def main():
    sat, thu = "2026-01-17", "2026-01-15"
    # null control
    _, e0 = save({})
    t0 = capture(e0, SAT)
    check("null: saturday 12h follows weekday day 21.0", t0.get((sat, 12)), 21.0)
    # weekend day value
    _, e = save({"comfort_temp_day_weekend": 22.5})
    t, w = capture(e, SAT), capture(e, THU)
    check("comfort_temp_day_weekend=22.5: saturday 12h", t.get((sat, 12)), 22.5)
    check("comfort_temp_day_weekend=22.5: thursday 12h unchanged", w.get((thu, 12)), 21.0)
    # weekend night
    _, e = save({"comfort_temp_night_weekend": 20.5})
    t, w = capture(e, SAT), capture(e, THU)
    check("comfort_temp_night_weekend=20.5: saturday 23h", t.get((sat, 23)), 20.5)
    check("comfort_temp_night_weekend=20.5: thursday 23h unchanged", w.get((thu, 23)), 19.5)
    # weekend start / end hour
    _, e = save({"day_start_hour_weekend": 10})
    t, w = capture(e, SAT), capture(e, THU)
    check("day_start_hour_weekend=10: saturday 8h is night", t.get((sat, 8)), 19.5)
    check("day_start_hour_weekend=10: saturday 10h is day", t.get((sat, 10)), 21.0)
    check("day_start_hour_weekend=10: thursday 8h stays day", w.get((thu, 8)), 21.0)
    _, e = save({"day_end_hour_weekend": 20})
    t = capture(e, SAT)
    check("day_end_hour_weekend=20: saturday 21h is night", t.get((sat, 21)), 19.5)
    # 'Defaults to the weekday daytime value': weekday edited, weekend section left as shown
    _, e = save({"comfort_temp_day": 22.5})
    t = capture(e, SAT)
    check("weekday day=22.5, weekend untouched: saturday 12h follows", t.get((sat, 12)), 22.5)
    # a value the user keeps as shown while changing the weekday value
    _, e1 = save({"comfort_temp_day": 22.5})                     # weekend now shows 22.5
    _, e2 = save({"comfort_temp_day": 21.0, "comfort_temp_day_weekend": 22.5}, options=dict(e1.options))
    t = capture(e2, SAT)
    check("weekend kept at its shown 22.5 while weekday set to 21.0: saturday 12h",
          t.get((sat, 12)), 22.5)
    print("stored after that save:", {k: v for k, v in e2.options.items() if "comfort" in k})
    # holiday
    hol = {"holiday_calendar_entity": "calendar.hol"}
    _, e = save({"holiday_comfort_temp_day": 22.5, "holiday_comfort_temp_night": 20.5,
                 "holiday_day_start_hour": 9, "holiday_day_end_hour": 18}, options=hol)
    on = capture(e, THU, {"calendar.hol": "on"})
    off = capture(e, THU, {"calendar.hol": "off"})
    check("holiday_comfort_temp_day=22.5, calendar on: thursday 12h", on.get((thu, 12)), 22.5)
    check("holiday_comfort_temp_night=20.5, calendar on: thursday 20h", on.get((thu, 20)), 20.5)
    check("holiday_day_start_hour=9, calendar on: thursday 8h is night", on.get((thu, 8)), 20.5)
    check("holiday_day_end_hour=18, calendar on: thursday 18h is night", on.get((thu, 18)), 20.5)
    check("holiday fields, calendar off: thursday 12h weekday", off.get((thu, 12)), 21.0)
    # 'Away setback still wins if away is active'
    async def away_save():
        flow, entry, hass = rig.new_flow(options={**dict(e.options)})
        form = await flow.async_step_away(None)
        a = rig.schema_defaults(form)
        a.update({"away_presence_entity": "person.me", "holiday_calendar_entity": "calendar.hol",
                  "away_temperature": 12.0})
        await rig.submit(flow, "away", a)
        return entry
    ea = asyncio.run(away_save())
    hass, coord = rig.build_coord(ea, states={"calendar.hol": "on", "person.me": "not_home"}, now=THU)
    d = rig.run_cycles(coord, 1)
    check("holiday on + away active: away target wins", d.get("away_target_temperature"), 12.0)
    check("holiday on + away active: the setpoint written is the away temperature",
          (d.get("current_action") or {}).get("setpoint"), 12.0)
    print(f"RESULT owed_checks={len(CHECKS)}")
    print(f"RESULT owed_fail={len(FAILS)}")
    for f in FAILS:
        print("FAIL", f)
    print(f"RESULT thread_factor={rig.thread_factor()}")
    print(f"RESULT load1={rig.load1()}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
