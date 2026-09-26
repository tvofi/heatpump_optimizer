"""D10-s1-03 verify-v1: what the transient classification costs on steady cycles.

Metric: over N=6 consecutive steady cycles
(coordinator:HeatPumpOptimizerCoordinator._fetch_tibber_prices) against a
Tibber endpoint that answers 401 every time, count
  revoked_posts   = Tibber POSTs made after the first 401 (the token is
                    already known revoked and the reauth flow already started);
  reauth_started  = entry.async_start_reauth calls;
  auth_class      = cycles whose escaping exception is named
                    ConfigEntryAuthFailed.
Upstream DataUpdateCoordinator stops scheduling refreshes after a
ConfigEntryAuthFailed; UpdateFailed keeps the schedule, so revoked_posts is the
number of polls upstream's auth arm would not have made (N-1 at most).
Count key: the session's own POST counter and the exception class escaping the
production fetch.
Perturbation: --status 200 (endpoint accepts; payload empty so the fetch still
fails as a non-auth error). Expected: reauth_started 1 -> 0 (the auth verdict
is keyed on the status). Null control: --status 500 gives reauth_started 0.

Run (repo root):
  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D10/verify-v1/auth_polls.py [--status 401|403|500|200]
Expected at 401: revoked_posts=5, reauth_started=1, auth_class=0 (+-0).
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (evidence tree 6f51db2c).
Machine: 4-core Linux cloud container, shared. Root rule: cwd.
"""
from __future__ import annotations

import os

for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_var, "1")

import argparse  # noqa: E402
import asyncio  # noqa: E402
import logging  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer import coordinator as cm  # noqa: E402

logging.disable(logging.CRITICAL)
ap = argparse.ArgumentParser()
ap.add_argument("--status", type=int, default=401)
STATUS = ap.parse_args().status
N = 6


class _Resp:
    def __init__(self, status):
        self.status = status

    async def json(self):
        return None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


class _Session:
    posts = 0

    def post(self, *a, **k):
        _Session.posts += 1
        return _Resp(STATUS)


cm.async_get_clientsession = lambda hass, verify_ssl=True: _Session()


async def main():
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.0"))
    entry = FakeEntry(data={const.CONF_TIBBER_TOKEN: "revoked",
                            const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor"})
    starts = []
    entry.async_start_reauth = lambda h: starts.append(1)
    coord = cm.HeatPumpOptimizerCoordinator(hass, entry)
    classes = []
    first_fail_posts = None
    for _ in range(N):
        try:
            await coord._fetch_tibber_prices()
            classes.append("none")
        except Exception as err:  # noqa: BLE001
            classes.append(type(err).__name__)
            if first_fail_posts is None:
                first_fail_posts = _Session.posts
    print(f"status={STATUS} cycles={N} classes={sorted(set(classes))} posts={_Session.posts}")
    revoked = _Session.posts - (first_fail_posts or 0) if starts else 0
    print(f"RESULT revoked_posts={revoked} count")
    print(f"RESULT reauth_started={len(starts)} count")
    print(f"RESULT auth_class={sum(c == 'ConfigEntryAuthFailed' for c in classes)} cycles")


t0p, t0t = time.process_time(), time.thread_time()
asyncio.run(main())
dp, dt = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={dp / dt if dt else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
with open("/proc/vmstat") as fh:
    print("RESULT swapins=" + next(l.split()[1] for l in fh if l.startswith("pswpin")))
