"""V2 (independent) harness for D1-s3-01.

Metric (one line): for the card's datetime-local string (YYYY-MM-DDTHH:MM, no
offset) passed through the production SERVICE_SCHEMA_SET_AWAY and
HeatPumpOptimizerCoordinator.async_set_away, the number of the next 6
coordinator._resolve_away() calls that raise, per arm: naive+active,
aware(+offset)+active (control), naive+inactive (control), naive+active with
_parse_return_time normalising a naive result to local (fix, in memory).
Count key: exceptions out of production _resolve_away / async_set_away.
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/verify-v2/u1_away_card.py
Expected: naive_active 6 of 6 and set_away_raised=1; the three other arms 0 (+-0).
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: cloud box G1-V2, 4 vCPU Linux, CPython 3.14.0rc2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("HASTUB_TZ", "Europe/Stockholm")
import asyncio, sys, time, logging
from datetime import timedelta
from unittest import mock
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
_p0, _t0 = time.process_time(), time.thread_time()
logging.disable(logging.CRITICAL)
from harness import FakeEntry, FakeHass, FakeState  # noqa
from homeassistant.util import dt as dt_util  # noqa
from heatpump_optimizer import away, services  # noqa
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa

_orig_parse = away._parse_return_time


def _fixed_parse(raw):
    d = _orig_parse(raw)
    return dt_util.as_local(d) if d is not None and d.tzinfo is None else d


def arm(naive, active, fix=False):
    hass = FakeHass({"sensor.indoor": FakeState("21.0"), "sensor.outdoor": FakeState("-2.0")})
    c = HeatPumpOptimizerCoordinator(hass, FakeEntry(data={"indoor_temp_entity": "sensor.indoor",
                                                           "outdoor_temp_entity": "sensor.outdoor"}))
    c._away_state.migrated_helpers = True
    ret = dt_util.now() + timedelta(days=2)
    raw = ret.strftime("%Y-%m-%dT%H:%M") if naive else ret.isoformat()
    ctx = mock.patch.object(away, "_parse_return_time", _fixed_parse) if fix else mock.patch.object(away, "_noop_", None, create=True)
    set_raised = 0
    with ctx:
        for payload in ({"active": active}, {"return_time": raw}):
            data = services.SERVICE_SCHEMA_SET_AWAY(payload)
            try:
                asyncio.run(c.async_set_away(**data, refresh=False))
            except Exception:  # noqa: BLE001
                set_raised += 1
        raised = 0
        for _ in range(6):
            try:
                c._resolve_away()
            except Exception:  # noqa: BLE001
                raised += 1
    return set_raised, raised, c._away_state.override_return_iso


for name, kw in (("naive_active", dict(naive=True, active=True)),
                 ("aware_active", dict(naive=False, active=True)),
                 ("naive_inactive", dict(naive=True, active=False)),
                 ("naive_active_fix", dict(naive=True, active=True, fix=True))):
    s, r, iso = arm(**kw)
    print(f"RESULT {name}_set_away_raised={s} count_of_2")
    print(f"RESULT {name}_resolve_raised={r} count_of_6 (stored {iso})")
p, t = time.process_time() - _p0, time.thread_time() - _t0
print(f"RESULT thread_factor={p / t if t else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    print("RESULT swapins=" + [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1])
except Exception:
    print("RESULT swapins=na")
