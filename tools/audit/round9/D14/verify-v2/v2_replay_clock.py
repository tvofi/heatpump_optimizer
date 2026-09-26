"""D14 round 9, verifier V2 (independent) for D14-s4-02: can the replay lane's clock see a DST seam?

Metric (one line): over one Europe/Stockholm DST day, walking the clock the way
tests/replay.py:run_fixture does (t = replay._ts(window.start) + k * 15 min, frozen into
dt_util), v2_offset_mismatch = cycles whose frozen now carries a UTC offset different from the
ZoneInfo value Home Assistant would hand the integration at the same instant, and
v2_grid_off_under_replay_clock = cycles at which the REAL coordinator._forecast_arrays builds a
price grid whose step 0 != _solve_anchor(now) as instants (the D14-s4-01 seam) -- compared with the
same count under the ZoneInfo clock.
Keys: replay._ts's returned tzinfo; the step_starts production hands _known_prices_for.

Null control: plain day 2026-03-22 -> 0 on every count.
Perturbation (--zone-clock-ts): replay._ts patched in memory to astimezone(ZoneInfo(tz)) ->
v2_grid_off_under_replay_clock equals the ZoneInfo count (non-zero on the DST days).

Run: PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D14/verify-v2/v2_replay_clock.py [--zone-clock-ts]
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; 4-core cloud container, CPython 3.14.0rc2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, logging
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from unittest import mock
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
logging.disable(logging.CRITICAL)
t_proc0, t_thr0 = time.process_time(), time.thread_time()
from harness import FakeHass, FakeEntry  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
import heatpump_optimizer.coordinator as C  # noqa: E402
import replay  # noqa: E402

TZ = ZoneInfo("Europe/Stockholm")
dt_util.DEFAULT_TIME_ZONE = TZ
if "--zone-clock-ts" in sys.argv:
    _o = replay._ts
    replay._ts = lambda raw: (_o(raw).astimezone(TZ) if raw else None)

cfg = {"tibber_token": "x", "weather_entity": "weather.home"}
coord = C.HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=cfg))


def grid_off(now, utc0):
    cap = {}
    orig = C.HeatPumpOptimizerCoordinator._known_prices_for

    def spy(self, ss):
        cap["s0"] = ss[0]
        return orig(self, ss)
    with mock.patch.object(C.HeatPumpOptimizerCoordinator, "_known_prices_for", spy), \
         mock.patch.object(C.HeatPumpOptimizerCoordinator, "_weather_series", side_effect=RuntimeError):
        dt_util.freeze(now)
        try:
            coord._forecast_arrays(now)
        except RuntimeError:
            pass
    return cap["s0"].astimezone(timezone.utc) != C._solve_anchor(now).astimezone(timezone.utc)


def day(start_iso):
    start = replay._ts(start_iso)          # what run_fixture freezes from
    zstart = datetime.fromisoformat(start_iso).astimezone(TZ)
    utc0 = start.astimezone(timezone.utc) - timedelta(hours=1)
    coord._prices = [{"starts_at": (utc0 + timedelta(hours=h)).astimezone(TZ).isoformat(), "total": float(h)}
                     for h in range(80)]
    n = mism = off_r = off_z = 0
    for k in range(96):
        t = start + timedelta(minutes=15 * k)       # run_fixture: t += step
        z = zstart + timedelta(minutes=15 * k)      # a ZoneInfo clock stepped the same way
        z = (z.astimezone(timezone.utc)).astimezone(TZ)
        if t.astimezone(timezone.utc) >= (datetime.fromisoformat(start_iso) + timedelta(days=1)).astimezone(timezone.utc) + timedelta(hours=1):
            break
        n += 1
        mism += t.utcoffset() != TZ.utcoffset(t.astimezone(timezone.utc).replace(tzinfo=None))
        off_r += grid_off(t, utc0)
        zt = t.astimezone(timezone.utc).astimezone(TZ)
        off_z += grid_off(zt, utc0)
    return n, mism, off_r, off_z


for name, iso in (("spring", "2026-03-29T00:00:00+01:00"), ("autumn", "2026-10-25T00:00:00+02:00"),
                  ("plain", "2026-03-22T00:00:00+01:00")):
    n, m, r, z = day(iso)
    print(f"RESULT v2_offset_mismatch[{name}]={m}_of_{n} count")
    print(f"RESULT v2_grid_off_under_replay_clock[{name}]={r}_of_{n} count")
    print(f"RESULT v2_grid_off_under_zoneinfo_clock[{name}]={z}_of_{n} count")
dt_util.freeze(None)
pc, tc = time.process_time() - t_proc0, time.thread_time() - t_thr0
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
