"""D1-s3 M6: a tz-less return_time from the set_away service wedges every cycle.

The card's away strip is an <input type="datetime-local">, whose value is a
tz-less "YYYY-MM-DDTHH:MM" string sent verbatim as set_away's return_time
(www/heatpump-optimizer-card.js, data-away-return); services.yaml's own example
is tz-less too. away._parse_return_time returns a naive datetime for it, and
away.expire_override compares it with Home Assistant's always-aware now.

Metric: of K=6 consecutive cycles after the service call, the number in which
the coordinator's per-cycle away resolution (HeatPumpOptimizerCoordinator.
_resolve_away -> away.expire_override) raises; plus whether the service call
itself raised. Count key: an exception escaping the production call.

Run:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/s3/away_naive_return.py [--aware-input] [--perturb]
  --aware-input  null control: the same instant with an explicit offset (expect 0).
  --perturb      in-memory fix: away._parse_return_time normalises a naive
                 result with dt_util.as_local (expect 0).
Expected (default arm): service_raised=1, failed_cycles=6 of 6 (exact), both
for "return first, then toggle on" and for "toggle on, then set return";
solves_failed=2 of 2 through HeatPumpOptimizerCoordinator.async_run_optimization
(its fence turns the TypeError into "solve_failed"). Both controls: all 0.
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: box B5 (cloud container, linux).
The stub clock is made aware (HASTUB_TZ) because real HA's dt_util.now() is.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("HASTUB_TZ", "Europe/Stockholm")
import sys
import time
import asyncio
import logging
from datetime import datetime, timedelta
from unittest import mock
logging.disable(logging.CRITICAL)

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
from harness import FakeHass, FakeEntry, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import away  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

AWARE = "--aware-input" in sys.argv
PERTURB = "--perturb" in sys.argv
K = 6
_c0, _t0 = time.process_time(), time.thread_time()
T0 = datetime(2026, 10, 2, 8, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE)
RET = T0 + timedelta(days=3)
RAW = RET.isoformat() if AWARE else RET.strftime("%Y-%m-%dT%H:%M")  # datetime-local


def _coord(i):
    hass = FakeHass({"sensor.indoor": FakeState("21.4"), "sensor.outdoor": FakeState("-3.0")})
    c = HeatPumpOptimizerCoordinator(hass, FakeEntry(data={
        "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
        "dhw_tank_volume": 180.0}, entry_id=f"away{i}"))
    c._away_state.migrated_helpers = True
    # golden.py's deterministic 48 h inputs, so a real solve can run.
    c._prices = [{"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
                  "starts_at": (T0 + timedelta(hours=h)).isoformat(), "level": "NORMAL"}
                 for h in range(48)]
    c._weather_forecast = [{"datetime": (T0 + timedelta(hours=h)).isoformat(),
                            "temperature": -5.0, "wind_speed": 3.0,
                            "precipitation": 0.0, "humidity": 85.0} for h in range(48)]
    return c


async def _solves(i):
    """The production solve entry point, twice, after the card's call."""
    c = _coord(100 + i)
    dt_util.freeze(T0)
    await c._update_current_state()
    try:
        await c.async_set_away(active=True, return_time=RAW, refresh=False)
    except Exception:
        pass
    failed = 0
    for k in range(1, 3):
        dt_util.freeze(T0 + timedelta(minutes=15 * k))
        if await c.async_run_optimization() == "solve_failed":
            failed += 1
    return failed, c._solve_failures


async def _scenario(i, order):
    c = _coord(i)
    dt_util.freeze(T0)
    raised = 0
    calls = ([dict(return_time=RAW), dict(active=True)] if order == "return_then_on"
             else [dict(active=True), dict(return_time=RAW)])
    for kw in calls:
        try:
            await c.async_set_away(**kw, refresh=False)
        except Exception:
            raised = 1
    failed = 0
    for k in range(1, K + 1):
        dt_util.freeze(T0 + timedelta(minutes=15 * k))
        try:
            c._resolve_away()
        except Exception:
            failed += 1
    return raised, failed


_orig = away._parse_return_time


def _fixed(raw):
    d = _orig(raw)
    return dt_util.as_local(d) if d is not None and d.tzinfo is None else d


async def main():
    out = {}
    for i, order in enumerate(("return_then_on", "on_then_return")):
        out[order] = await _scenario(i, order)
    out["solve"] = await _solves(0)
    return out

if PERTURB:
    with mock.patch.object(away, "_parse_return_time", _fixed):
        res = asyncio.run(main())
else:
    res = asyncio.run(main())
print(f"arm={'perturb' if PERTURB else 'aware-input' if AWARE else 'default'} return_time={RAW!r}")
sf, streak = res.pop("solve")
print(f"RESULT solves_failed={sf} count_of_2")
print(f"RESULT solve_failure_streak={streak} count")
for order, (raised, failed) in res.items():
    print(f"RESULT {order}_service_raised={raised} count")
    print(f"RESULT {order}_failed_cycles={failed} count_of_{K}")
cpu, thr = time.process_time() - _c0, time.thread_time() - _t0
print(f"RESULT thread_factor={cpu / thr if thr else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
except Exception:
    sw = 'na'
print(f"RESULT swapins={sw}")
