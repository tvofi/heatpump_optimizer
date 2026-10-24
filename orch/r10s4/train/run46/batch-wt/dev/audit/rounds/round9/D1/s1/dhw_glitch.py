"""D1-s1 external-input harness (D1.M6): DhwProfileLearner.async_learn_dynamics fed
a tank-thermometer series with one sensor-fault sample (DS18B20 disconnect -127 C,
power-on 85 C spike, or 1e6), everything else a quiet 55 C tank with a morning draw.

Metric (one line): after DAY+1 simulated days (--day, default 13) (5-min ticks) with ONE glitch sample on
day DAY, the delta vs the glitch-free control of (a) the largest DrawStats occurrence
energy folded, kWh, and (b) the max of the learned hourly profile (intensity ratio), (c) the window's p90
(DrawStats.quantile, the heavy-day target the planner reads).
Count key: the learner's own draw_stats reservoirs and hourly_profile.

Command:  PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python tools/audit/round9/D1/s1/dhw_glitch.py [--guard]
  --day 4   expected (exact, deterministic): control max_event 1.073, p90 1.073;
            glitch -127: max_event 42.218, p90 25.760; glitch 85: 8.747 / 5.677;
            glitch 1e6: 231757.047 / 139054.657 kWh
  --day 13  same max_event; p90 stays 1.073 (the outlier is above the 0.9 index once
            the window has >= 11 occurrences) -- the exposure is the first ~10 days
            and the 40-occurrence reservoir tenure
  --guard   perturbation: samples outside [0, 100] C are skipped before the learner
            (a one-line range check at async_learn_dynamics entry) -> the -127 and
            1e6 rows return to control (direction down); the in-range 85 C spike does
            not move, which is why the property is a physical bound, not a range
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: box B4 cloud container.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio
import logging
import sys
import time
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
logging.disable(logging.CRITICAL)
_p0, _t0 = time.process_time(), time.thread_time()
from harness import FakeHass  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer.dhw_learning import DhwProfileLearner  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402

GUARD = "--guard" in sys.argv
DAY = int(sys.argv[sys.argv.index("--day") + 1]) if "--day" in sys.argv else 13
START = datetime(2026, 1, 5, 0, 0, tzinfo=timezone.utc)


def series(glitch):
    temp = 55.0
    out = []
    for i in range((DAY + 1) * 288):
        t = START + timedelta(minutes=5 * i)
        h = t.hour + t.minute / 60
        if 6.5 <= h < 7.0:
            temp -= 0.8          # a shower: ~8 C over 30 min
        elif 7.0 <= h < 8.0:
            temp = min(55.0, temp + 1.4)  # reheated (heating flag on)
        else:
            temp -= 0.03         # standby
        if h < 0.1:
            temp = 55.0
        v = temp
        if glitch is not None and i == DAY * 288 + 6 * 12 + 36 // 5:  # day DAY, 06:35
            v = glitch
        out.append((t, v, 7.0 <= h < 8.0))
    return out


def run(glitch):
    params = ThermalParameters()
    params.dhw_enabled = True
    heating = {"on": False}
    dl = DhwProfileLearner(FakeHass(), "g", params, frozen=lambda *a: None,
                           heating_active=lambda: heating["on"], external_heat_active=lambda: False)
    for t, v, heat in series(glitch):
        dt_util.freeze(t)
        heating["on"] = heat
        if GUARD and not (0.0 <= v <= 100.0):
            continue
        asyncio.run(dl.async_learn_dynamics(v))
    dt_util.freeze(None)
    dl.draw_stats.fold(t + timedelta(days=1), "", 0.0)  # close the open occurrence
    events = [e for v in dl.draw_stats.reservoirs.values() for e in v]
    p90 = max((dl.draw_stats.quantile(k) or 0.0) for k in dl.draw_stats.reservoirs) if dl.draw_stats.reservoirs else 0.0
    return max(events) if events else 0.0, max(dl.hourly_profile), p90, params.dhw_enabled


ctl = run(None)
print(f"# guard={GUARD} dhw_enabled={ctl[3]}")
print(f"RESULT control_max_event_kwh={ctl[0]:.3f} kWh")
print(f"RESULT control_profile_max={ctl[1]:.3f} ratio")
print(f"RESULT control_window_p90_kwh={ctl[2]:.3f} kWh")
for g in (-127.0, 85.0, 1e6):
    r = run(g)
    tag = str(int(g)) if g > -1e5 else "m"
    print(f"RESULT glitch{tag}_max_event_kwh={r[0]:.3f} kWh")
    print(f"RESULT glitch{tag}_profile_max={r[1]:.3f} ratio")
    print(f"RESULT glitch{tag}_window_p90_kwh={r[2]:.3f} kWh")
p, t = time.process_time() - _p0, time.thread_time() - _t0
print(f"RESULT thread_factor={p / t if t else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
except Exception:
    sw = "na"
print(f"RESULT swapins={sw}")
