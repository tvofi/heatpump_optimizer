"""D1-s3 M3/M2: a boost channel's "two-hour maximum" is an absolute instant,
never bounded against the clock it is read with.

Metric: hours a space boost stays live on the action (boost.apply ->
action["boost_space"]), sampled every 15 min up to a 72 h cap, after
(a) set at T0 then the wall clock steps back by J hours (NTP correcting a
fast clock), J in {0, 1, 6, 24}; (b) restored from a store whose "until" is
far in the future (2099). Count key: the flag production's overlay delivers.

Run:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/s3/boost_unbounded.py [--perturb]
  --perturb  in-memory fix: BoostState.expire also drops an end more than
             BOOST_HOURS after now. Expected then: jump0=2.0 (unchanged),
             jump1/6/24=0.0 and restore_2099=0.0 (a bound-violating end is
             dropped; a clamp-to-now+2h fix would read 2.0 instead -- either
             way every arm is <= 2.0).
Expected (default): jump0=2.0 h (null control), jump1=3.0, jump6=8.0, jump24=26.0,
restore_2099=72.0 (the cap: never expires). Exact.
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: box B5 (cloud container, linux).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("HASTUB_TZ", "Europe/Stockholm")
import sys
import time
import json
import asyncio
import logging
from datetime import datetime, timedelta
from unittest import mock
logging.disable(logging.CRITICAL)

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
from harness import FakeHass, FakeEntry, FakeState  # noqa: E402
from homeassistant.helpers import storage as _storage  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import boost  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

PERTURB = "--perturb" in sys.argv
CAP_H = 72
_c0, _t0 = time.process_time(), time.thread_time()
T0 = datetime(2026, 1, 10, 6, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE)
_n = iter(range(10**6))


def _coord():
    c = HeatPumpOptimizerCoordinator(
        FakeHass({"sensor.indoor": FakeState("21.4"), "sensor.outdoor": FakeState("-3.0")}),
        FakeEntry(data={"indoor_temp_entity": "sensor.indoor",
                        "outdoor_temp_entity": "sensor.outdoor",
                        "dhw_tank_volume": 180.0}, entry_id=f"b{next(_n)}"))
    return c


def _live_hours(c, start):
    live = 0
    for k in range(CAP_H * 4):
        dt_util.freeze(start + timedelta(minutes=15 * k))
        c._current_action = {"mode": "eco", "power": 0.5}
        boost.apply(c)
        if c._current_action.get("boost_space"):
            live += 1
        else:
            break
    return live / 4.0


async def main():
    out = {}
    for j in (0, 1, 6, 24):
        c = _coord()
        dt_util.freeze(T0)
        await boost.set_channel(c, "space", True, refresh=False)
        out[f"jump{j}"] = _live_hours(c, T0 - timedelta(hours=j))
    c = _coord()
    _storage._DISK[f"heatpump_optimizer_{c.entry.entry_id}_boost"] = json.dumps(
        {"space": {"until": datetime(2099, 1, 1, tzinfo=dt_util.DEFAULT_TIME_ZONE).isoformat()}})
    dt_util.freeze(T0)
    await boost.restore(c)
    out["restore_2099"] = _live_hours(c, T0)
    return out


_orig_expire = boost.BoostState.expire


def _expire_bounded(self, now):
    _orig_expire(self, now)
    for ch, end in list(self.until.items()):
        if end - now > timedelta(hours=boost.BOOST_HOURS):
            self.until.pop(ch, None)

if PERTURB:
    with mock.patch.object(boost.BoostState, "expire", _expire_bounded):
        res = asyncio.run(main())
else:
    res = asyncio.run(main())
print(f"arm={'perturb' if PERTURB else 'default'}")
for k, v in res.items():
    print(f"RESULT {k}_live_hours={v:.2f} h")
cpu, thr = time.process_time() - _c0, time.thread_time() - _t0
print(f"RESULT thread_factor={cpu / thr if thr else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
except Exception:
    sw = 'na'
print(f"RESULT swapins={sw}")
