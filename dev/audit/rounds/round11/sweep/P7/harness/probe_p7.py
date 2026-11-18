"""Class P7 probes, round 11. Each probe exits 1 when its seam answers a DST
day with wall-clock (calendar) arithmetic instead of true elapsed time, 0 when
it agrees with the UTC reference.

Run: HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub:custom_components python3 probe_p7.py <probe> [--day spring|autumn|plain]
Probes:
  month_hours            ledger.month_hours of the month vs its real hours (D2-s3-07's site)
  hours_until_next_window dhw_schedule.hours_until_next_window at 01:30 local, a window opening 03:00/04:00
  simulate_trajectory     ThermalModel.simulate_trajectory's per-step hour of day vs optimizer._step_clock
  simulate_trajectory_batch       same, the batch kernel
  simulate_trajectory_with_dhw    same, the DHW kernel (draw-rate hours and gains hours)
--day plain is the null control: every probe exits 0 on a day with no transition.
"""
import argparse, sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("probe")
ap.add_argument("--day", default="spring", choices=["spring", "autumn", "plain"])
A = ap.parse_args()
Z = ZoneInfo("Europe/Stockholm")
DAY = {"spring": (2026, 3, 29), "autumn": (2026, 10, 25), "plain": (2026, 5, 10)}[A.day]


def real_hours_until(local_from, wall_target_hour):
    y, m, d = DAY
    tgt = datetime(y, m, d, int(wall_target_hour), int(round((wall_target_hour % 1) * 60)), tzinfo=Z)
    return (tgt.astimezone(timezone.utc) - local_from.astimezone(timezone.utc)).total_seconds() / 3600.0


def out(name, got, want, tol=1e-6):
    bad = abs(got - want) > tol
    print(f"PROBE {name} day={A.day} got={got:.6f} want={want:.6f} -> {'FAIL' if bad else 'ok'}")
    sys.exit(1 if bad else 0)


if A.probe == "month_hours":
    from heatpump_optimizer import ledger
    y, m, _ = DAY
    a = datetime(y, m, 1, tzinfo=Z)
    b = datetime(y + (m == 12), m % 12 + 1, 1, tzinfo=Z)
    real = (b.astimezone(timezone.utc) - a.astimezone(timezone.utc)).total_seconds() / 3600.0
    out("ledger.month_hours", ledger.month_hours(datetime(y, m, 15, 12, tzinfo=Z)), real)

if A.probe == "hours_until_next_window":
    from heatpump_optimizer.dhw_schedule import hours_until_next_window
    y, m, d = DAY
    now = datetime(y, m, d, 1, 30, tzinfo=Z)   # before the transition in either direction
    win_start = 4.0                             # a window opening at 04:00 wall, after it
    got = hours_until_next_window(now.hour + now.minute / 60.0, [(win_start, 6.0)])
    out("dhw_schedule.hours_until_next_window", got, real_hours_until(now, win_start))

if A.probe.startswith("simulate_trajectory"):
    from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState, WeatherSeries
    from heatpump_optimizer.optimizer import _step_clock
    y, m, d = DAY
    start = datetime(y, m, d, 0, 0, tzinfo=Z)
    n, dt = 24, 0.25                                     # 6 h from local midnight: spans 02:00-03:00
    _, step_hours = _step_clock(start, n, dt)
    true_hours = np.asarray(step_hours, float) % 24.0
    seen = []
    p = ThermalParameters()
    p.internal_gains_profile = [0.1 * h for h in range(24)]
    orig_g, orig_r = ThermalModel.internal_gains_at, ThermalModel.dhw_draw_rates

    def gains_at(self, hour_of_day):
        seen.append(("gains", float(hour_of_day)))
        return orig_g(self, hour_of_day)

    def draw_rates(self, hours):
        seen.extend(("draw", float(h)) for h in np.asarray(hours, float))
        return orig_r(self, hours)
    ThermalModel.internal_gains_at, ThermalModel.dhw_draw_rates = gains_at, draw_rates
    model = ThermalModel(p)
    w = WeatherSeries(outdoor_temps=np.full(n, 0.0))
    power = np.full(n, 2.0)
    sh = float(step_hours[0])
    if A.probe == "simulate_trajectory":
        model.simulate_trajectory(ThermalState(), power, w, dt_hours=dt, start_hour=sh)
    elif A.probe == "simulate_trajectory_batch":
        model.simulate_trajectory_batch(ThermalState(), power[None, :], w, dt_hours=dt, start_hour=sh)
    else:
        model.simulate_trajectory_with_dhw(ThermalState(), power, np.zeros(n), w, start_hour=sh, dt_hours=dt)
    if not seen:
        print(f"PROBE {A.probe} day={A.day} no hour reached the spies -> UNREACHED"); sys.exit(2)
    # the hour each recorded call answers for, step by step, against the true local hour
    by_kind = {}
    for k, h in seen:
        by_kind.setdefault(k, []).append(h)
    worst = 0.0
    for k, hs in by_kind.items():
        hs = np.asarray(hs[:n])
        worst = max(worst, float(np.max(np.abs(((hs - true_hours[: hs.size]) + 12) % 24 - 12))))
    out(f"thermal_model.ThermalModel.{A.probe} (max |hour - true hour|, kinds {sorted(by_kind)})", worst, 0.0)
