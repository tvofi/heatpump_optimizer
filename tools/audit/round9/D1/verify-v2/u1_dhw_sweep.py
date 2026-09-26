"""V2 (independent) harness for D1-s1-03.

Metric (one line): over a 30-day run of 5-min tank samples (one 45 L-class
shower per morning), with ONE -127 C sample on glitch day G, the number of
day-ends at which the production DrawStats.quantile(0.9) of the draw window
exceeds the glitch-free control's by more than 10 %, per G in {0,2,4,6,8,10,12,20};
plus the day-end count at which the largest stored occurrence exceeds
the tank's physical ceiling (thermal mass x (100 - 0) C).
Count key: the learner's own draw_stats reservoirs after production
async_learn_dynamics; control is the same series without the glitch.
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/verify-v2/u1_dhw_sweep.py [--guard]
Expected: inflated_days > 0 only for G <= ~9 (window < 11 occurrences), 0 for G >= 10;
  impossible_days = 30 - G for every G (+-1). --guard ([0,100] C skip at entry): all 0.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: cloud box G1-V2, 4 vCPU Linux, CPython 3.14.0rc2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, sys, time
from datetime import datetime, timedelta, timezone
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
_p0, _t0 = time.process_time(), time.thread_time()
import logging; logging.disable(logging.CRITICAL)
from harness import FakeHass  # noqa
from homeassistant.util import dt as dt_util  # noqa
from heatpump_optimizer.dhw_learning import DhwProfileLearner  # noqa
from heatpump_optimizer.thermal_model import ThermalParameters  # noqa

GUARD = "--guard" in sys.argv
DAYS = 30
START = datetime(2026, 2, 2, 0, 0, tzinfo=timezone.utc)
GS = [0, 2, 4, 6, 8, 10, 12, 20]


async def run(g_day):
    params = ThermalParameters(); params.dhw_enabled = True
    heat = {"on": False}
    dl = DhwProfileLearner(FakeHass(), "u1", params, frozen=lambda *a: None,
                           heating_active=lambda: heat["on"], external_heat_active=lambda: False)
    ceiling = params.dhw_tank_thermal_mass * 100.0
    temp = 52.0
    p90s, maxes = [], []
    for i in range(DAYS * 288):
        t = START + timedelta(minutes=5 * i)
        h = t.hour + t.minute / 60
        if 18.0 <= h < 18.5:
            temp -= 0.6
        elif 18.5 <= h < 19.5:
            temp = min(52.0, temp + 1.2)
        else:
            temp -= 0.025
        if h < 0.05:
            temp = 52.0
        v = temp
        if g_day is not None and i == g_day * 288 + 18 * 12 + 2:
            v = -127.0
        heat["on"] = 18.5 <= h < 19.5
        dt_util.freeze(t)
        if not (GUARD and not (0.0 <= v <= 100.0)):
            await dl.async_learn_dynamics(v)
        if i % 288 == 287:
            r = dl.draw_stats.reservoirs
            p90s.append(max((dl.draw_stats.quantile(k) or 0.0) for k in r) if r else 0.0)
            ev = [e for v2 in r.values() for e in v2]
            maxes.append(max(ev) if ev else 0.0)
    dt_util.freeze(None)
    return p90s, maxes, ceiling


async def main():
    c_p90, _, ceiling = await run(None)
    tot_infl = 0
    for g in GS:
        p90, mx, _ = await run(g)
        infl = sum(1 for a, b in zip(p90, c_p90) if b > 0 and a > 1.10 * b)
        imp = sum(1 for m in mx if m > ceiling)
        tot_infl += infl
        print(f"RESULT G{g}_inflated_p90_days={infl} days_of_{DAYS} (peak {max(p90):.2f} vs control {max(c_p90):.2f} kWh)")
        print(f"RESULT G{g}_impossible_occurrence_days={imp} days_of_{DAYS}")
    print(f"RESULT inflated_p90_days_total={tot_infl} day_cells_of_{DAYS * len(GS)}")
    print(f"RESULT tank_ceiling_kwh={ceiling:.2f} kWh")


asyncio.run(main())
p, t = time.process_time() - _p0, time.thread_time() - _t0
print(f"RESULT thread_factor={p / t if t else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    print("RESULT swapins=" + [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1])
except Exception:
    print("RESULT swapins=na")
