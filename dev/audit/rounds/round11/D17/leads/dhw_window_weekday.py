"""D17-s3-51: the published 'in a hot-water window' flag ignores a day-selector schedule.

Metric: over the week's 7 x 48 half-hour cells, the number of cells where the
coordinator's real HeatPumpOptimizerCoordinator._dhw_in_demand_window() (the
payload's dhw_in_demand_window) differs from the window in force that weekday,
dhw_schedule.windows_for_day(params.dhw_weekly_windows, weekday, params.dhw_windows)
-- the resolution the optimizer's own weekday arrays use. No solve has run, so
_dhw_effective_windows falls back to params.dhw_demand_windows (the flat union).
Count key: the bool _dhw_in_demand_window returns.
Spec: 'weekdays 06:00-08:30, weekend 08:00-09:30' (the raiser's example).
Null control: a flat spec '06:00-08:30' with no day names -> 0 cells.
Run:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D17/leads/dhw_window_weekday.py [--perturb]
  --perturb swaps _dhw_effective_windows in memory for one resolving today's
  weekday through windows_for_day; cells_wrong must go to 0.
Expected: cells_wrong=18 (exact: 08:30-09:30 on five weekdays = 10 cells, plus
06:00-08:00 on Saturday and Sunday = 8 cells), null_cells_wrong=0.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (planted finder export
audit-r11-leads-px), machine: owner's macOS box (B8).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
from datetime import datetime, timedelta, timezone
from unittest import mock

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
from harness import FakeHass, FakeEntry  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import coordinator as coord_mod  # noqa: E402
from heatpump_optimizer.dhw_schedule import windows_for_day, hour_in_windows  # noqa: E402

c0, t0 = time.process_time(), time.thread_time()
PERTURB = "--perturb" in sys.argv
MONDAY = datetime(2026, 1, 12, tzinfo=timezone.utc)  # a Monday


def build(spec):
    cfg = {"tibber_token": "x", "weather_entity": "weather.home",
           "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
           "dhw_enabled": True, "dhw_schedule_enabled": True, "dhw_windows": spec}
    return coord_mod.HeatPumpOptimizerCoordinator(FakeHass({}), FakeEntry(data=cfg))


def run(spec, label):
    c = build(spec)
    params = getattr(c, "_ctx", c)._thermal_params
    if PERTURB:
        def _eff(self=c):
            wd = dt_util.now().weekday()
            return windows_for_day(params.dhw_weekly_windows, wd, list(params.dhw_windows))
        c._dhw_effective_windows = _eff
    wrong = 0
    for day in range(7):
        per_day = 0
        for half in range(48):
            t = MONDAY + timedelta(days=day, minutes=30 * half)
            with mock.patch.object(dt_util, "now", lambda t=t: t):
                published = c._dhw_in_demand_window()
            truth = hour_in_windows(t.hour + t.minute / 60.0,
                                    windows_for_day(params.dhw_weekly_windows, day,
                                                    list(params.dhw_windows)))
            per_day += published != truth
        if per_day:
            print(f"{label} weekday {day}: {per_day} half-hours wrong")
        wrong += per_day
    sat7 = MONDAY + timedelta(days=5, hours=7)
    with mock.patch.object(dt_util, "now", lambda: sat7):
        print(f"{label} Saturday 07:00: in_window={c._dhw_in_demand_window()} "
              f"next_in_h={c._dhw_next_window_in_hours()}")
    return wrong


wrong = run("weekdays 06:00-08:30, weekend 08:00-09:30", "weekly")
null = run("06:00-08:30", "flat")
print(f"RESULT cells=336 count")
print(f"RESULT cells_wrong={wrong} count")
print(f"RESULT null_cells_wrong={null} count")
cpu, th = time.process_time() - c0, time.thread_time() - t0
print(f"RESULT thread_factor={cpu / th if th else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    import resource
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap}")
except Exception:
    print("RESULT swapins=0")
