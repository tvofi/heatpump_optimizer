"""D14 round 9, verifier V2 (independent) for D14-s4-01: the forecast grid's step 0 on DST days.

Metric (one line): v2_grid_off_quarters = quarter-hour instants `now` on a Europe/Stockholm day
(stepped every 15 min in UTC, so every real instant of the day once) at which the REAL
HeatPumpOptimizerCoordinator._forecast_arrays(now) builds a price grid whose step 0 instant
(the step_starts[0] handed to _known_prices_for) differs from coordinator._solve_anchor(now) as an
instant; v2_price0_wrong = the same count keyed on the delivered value: prices[0] returned by
_price_series != the published hourly price covering `now` (prices are distinct per UTC hour).

Count key: the step_starts list production hands _known_prices_for, and the prices array
_price_series returns -- both production outputs, not the harness's own arithmetic.

Null control: the plain days 2026-03-22 and 2026-10-18 -> 0 expected.
Perturbation (--fix): _forecast_arrays recompiled in memory with step_offset taken from
dt_util.as_utc(now) - dt_util.as_utc(midnight) -> expected to_zero on the DST days.

Run (repository root):
  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D14/verify-v2/v2_dst_grid.py [--fix]
Expected: spring 2026-03-29 and autumn 2026-10-25 non-zero (post-transition quarters); plain 0.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: 4-core cloud container, CPython 3.14.0rc2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, inspect, textwrap
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from unittest import mock

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
t_proc0, t_thr0 = time.process_time(), time.thread_time()

from harness import FakeHass, FakeEntry  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
import heatpump_optimizer.coordinator as C  # noqa: E402

TZ = ZoneInfo("Europe/Stockholm")
dt_util.DEFAULT_TIME_ZONE = TZ
FIX = "--fix" in sys.argv

if FIX:
    src = textwrap.dedent(inspect.getsource(C.HeatPumpOptimizerCoordinator._forecast_arrays))
    old = "(now - midnight).total_seconds()"
    assert src.count(old) == 1, "fix target not found"
    src = src.replace(old, "(dt_util.as_utc(now) - dt_util.as_utc(midnight)).total_seconds()")
    ns = {}
    exec(compile(src, C.__file__, "exec"), C.__dict__, ns)
    C.HeatPumpOptimizerCoordinator._forecast_arrays = ns["_forecast_arrays"]

cfg = {"tibber_token": "x", "weather_entity": "weather.home",
       "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor"}
coord = C.HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=cfg))


def run_day(day):
    local_mid = datetime(day.year, day.month, day.day, tzinfo=TZ)
    utc0 = local_mid.astimezone(timezone.utc) - timedelta(hours=1)
    # hourly prices, distinct per UTC hour, as aware local ISO strings (the Tibber shape)
    coord._prices = [
        {"starts_at": (utc0 + timedelta(hours=h)).astimezone(TZ).isoformat(), "total": float(h)}
        for h in range(80)
    ]
    captured = {}
    orig = C.HeatPumpOptimizerCoordinator._known_prices_for

    def spy(self, step_starts):
        captured["s0"] = step_starts[0]
        return orig(self, step_starts)

    off = wrong = n = 0
    end = (datetime(day.year, day.month, day.day, tzinfo=TZ) + timedelta(days=1)).replace(tzinfo=TZ)
    end_utc = datetime(end.year, end.month, end.day, tzinfo=TZ).astimezone(timezone.utc)
    t = local_mid.astimezone(timezone.utc) + timedelta(minutes=7)
    with mock.patch.object(C.HeatPumpOptimizerCoordinator, "_known_prices_for", spy), \
         mock.patch.object(C.HeatPumpOptimizerCoordinator, "_weather_series",
                           side_effect=RuntimeError("stop after prices")):
        while t < end_utc:
            now = t.astimezone(TZ)
            dt_util.freeze(now)
            captured.clear()
            got = {}
            orig_ps = C.HeatPumpOptimizerCoordinator._price_series

            def ps(self, n_steps, midnight, step_offset):
                r = orig_ps(self, n_steps, midnight, step_offset)
                got["p0"] = float(r[0][0])
                return r
            with mock.patch.object(C.HeatPumpOptimizerCoordinator, "_price_series", ps):
                try:
                    coord._forecast_arrays(now)
                except RuntimeError:
                    pass
            n += 1
            anchor = C._solve_anchor(now)
            if captured["s0"].astimezone(timezone.utc) != anchor.astimezone(timezone.utc):
                off += 1
            true_price = float(int((t - utc0).total_seconds() // 3600))
            if got["p0"] != true_price:
                wrong += 1
            t += timedelta(minutes=15)
    return n, off, wrong


days = {"spring": datetime(2026, 3, 29), "autumn": datetime(2026, 10, 25),
        "plain": datetime(2026, 3, 22), "plain_autumn": datetime(2026, 10, 18)}
for name, d in days.items():
    n, off, wrong = run_day(d)
    print(f"RESULT v2_grid_off_quarters[{name}]={off}_of_{n} count")
    print(f"RESULT v2_price0_wrong[{name}]={wrong}_of_{n} count")
dt_util.freeze(None)
pc, tc = time.process_time() - t_proc0, time.thread_time() - t_thr0
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
except Exception:
    sw = "na"
print(f"RESULT swapins={sw}")
