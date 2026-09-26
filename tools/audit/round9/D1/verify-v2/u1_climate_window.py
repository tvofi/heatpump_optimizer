"""V2 (independent) harness for D1-s3-04.

Metric (one line): |climate.target_temperature - configured target|, read from
the production HeatPumpOptimizerClimate property at the moment the cycle awaits
the solve (inside a pass-through wrapper of production _await_optimize, no
state write forced), with away active vs away off, and the same read
immediately after async_run_optimization returns.
Count key: the production property's value (what any async_write_ha_state in
that window would publish).
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/verify-v2/u1_climate_window.py
Expected: away_mid=5.00 C, away_after=0.00, off_mid=0.00, off_after=0.00 (exact).
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: cloud box G1-V2, 4 vCPU Linux, CPython 3.14.0rc2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("HASTUB_TZ", "Europe/Stockholm")
import asyncio, sys, time, logging
from datetime import datetime, timedelta
from unittest import mock
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
_p0, _t0 = time.process_time(), time.thread_time()
logging.disable(logging.CRITICAL)
from harness import FakeHass, FakeEntry, FakeState  # noqa
from homeassistant.util import dt as dt_util  # noqa
from heatpump_optimizer import coordinator as cm, climate  # noqa
from heatpump_optimizer.const import CONF_TARGET_TEMP, DEFAULT_TARGET_TEMP  # noqa

T0 = datetime(2026, 11, 3, 9, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE)


async def arm(away):
    hass = FakeHass({"sensor.indoor": FakeState("21.0"), "sensor.outdoor": FakeState("-1.0")})
    entry = FakeEntry(data={"indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor"},
                      entry_id=f"u1cl{int(away)}")
    c = cm.HeatPumpOptimizerCoordinator(hass, entry)
    c._away_state.migrated_helpers = True
    c._prices = [{"total": 1.0 + 0.3 * ((h // 6) % 2), "starts_at": (T0 + timedelta(hours=h)).isoformat()}
                 for h in range(48)]
    c._weather_forecast = [{"datetime": (T0 + timedelta(hours=h)).isoformat(), "temperature": -1.0,
                            "wind_speed": 2.0, "precipitation": 0.0, "humidity": 80.0} for h in range(48)]
    dt_util.freeze(T0)
    await c._update_current_state()
    if away:
        await c.async_set_away(active=True, return_time=(T0 + timedelta(days=4)).isoformat(), refresh=False)
    ent = climate.HeatPumpOptimizerClimate(c, entry)
    configured = float(c._ctx._config.get(CONF_TARGET_TEMP, DEFAULT_TARGET_TEMP))
    seen = []
    orig = cm._await_optimize

    async def wrap(*a, **k):
        seen.append(ent.target_temperature)
        return await orig(*a, **k)
    with mock.patch.object(cm, "_await_optimize", wrap):
        dt_util.freeze(T0 + timedelta(minutes=10))
        await c.async_run_optimization()
    after = ent.target_temperature
    dt_util.freeze(None)
    return abs(seen[0] - configured) if seen else float("nan"), abs(after - configured), configured, seen


for away in (True, False):
    mid, after, conf, seen = asyncio.run(arm(away))
    tag = "away" if away else "off"
    print(f"# {tag}: configured={conf} mid_reads={seen}")
    print(f"RESULT {tag}_mid_deviation={mid:.2f} C")
    print(f"RESULT {tag}_after_deviation={after:.2f} C")
cm._shutdown_process_pool()
p, t = time.process_time() - _p0, time.thread_time() - _t0
print(f"RESULT thread_factor={p / t if t else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    print("RESULT swapins=" + [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1])
except Exception:
    print("RESULT swapins=na")
