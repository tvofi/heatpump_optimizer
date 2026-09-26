"""V2 (independent) harness for D1-s3-05.

Metric (one line): minutes a boost channel set by production BoostState.set
stays active (production BoostState.active, 1-min sampling) beyond BOOST_HOURS
after the wall clock steps back J, for J in {0, 1 min, 10 min, 1 h, 24 h};
plus, for a stored until X ahead of now, whether production boost.restore's
acceptance rule keeps it (X in {1 h, 2 h, 3 h, 365 d}) via BoostState.active
at restore time + BOOST_HOURS + 1 min.
Count key: BoostState.active return values.
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/verify-v2/u1_boost_overrun.py
Expected: overrun_min = J in minutes exactly (0, 1, 10, 60, 1440); restore_live_past_cap for X=3 h and 365 d
  (2 of 4), 0 for X <= 2 h.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: cloud box G1-V2, 4 vCPU Linux, CPython 3.14.0rc2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("HASTUB_TZ", "Europe/Stockholm")
import asyncio, json, sys, time, logging
from datetime import datetime, timedelta, timezone
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
_p0, _t0 = time.process_time(), time.thread_time()
logging.disable(logging.CRITICAL)
from harness import FakeHass, FakeEntry, FakeState  # noqa
from homeassistant.util import dt as dt_util  # noqa
from homeassistant.helpers import storage as _storage  # noqa
from heatpump_optimizer import boost  # noqa
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa

T0 = datetime(2026, 2, 1, 7, 0, tzinfo=timezone.utc)
for j in (0, 1, 10, 60, 1440):
    b = boost.BoostState()
    b.set("space", True, T0)
    start = T0 - timedelta(minutes=j)
    m = 0
    while b.active("space", start + timedelta(minutes=m)) and m < 5000:
        m += 1
    print(f"RESULT J{j}min_overrun_min={m - boost.BOOST_HOURS * 60} minutes (live {m} min)")

kept = 0
for i, x in enumerate((60, 120, 180, 365 * 1440)):
    c = HeatPumpOptimizerCoordinator(FakeHass({"sensor.indoor": FakeState("21"), "sensor.outdoor": FakeState("0")}),
                                     FakeEntry(data={"indoor_temp_entity": "sensor.indoor",
                                                     "outdoor_temp_entity": "sensor.outdoor"}, entry_id=f"u1b{i}"))
    now = dt_util.now()
    _storage._DISK[f"heatpump_optimizer_{c.entry.entry_id}_boost"] = json.dumps(
        {"space": {"until": (now + timedelta(minutes=x)).isoformat()}})
    boost.held_for(c).until.clear()
    asyncio.run(boost.restore(c))
    live = boost.held_for(c).active("space", now + timedelta(hours=boost.BOOST_HOURS, minutes=1))
    kept += int(live)
    print(f"RESULT restore_X{x}min_live_past_cap={int(live)}")
print(f"RESULT restore_live_past_cap={kept} count_of_4")
p, t = time.process_time() - _p0, time.thread_time() - _t0
print(f"RESULT thread_factor={p / t if t else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    print("RESULT swapins=" + [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1])
except Exception:
    print("RESULT swapins=na")
