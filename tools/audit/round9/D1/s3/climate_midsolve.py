"""D1-s3 M4: the thermostat publishes the away setback as the user's target
while a solve is in the executor.

away.apply_setback writes the setback into the LIVE ctx._opt_config.target_temp
before the solve is dispatched and restore_setback takes it off after the
executor await returns. climate.HeatPumpOptimizerClimate.target_temperature
("the comfort target the user asked for") reads that live field, so any state
write inside the window -- the peak guard's event-driven
_async_peak_guard_transition -> async_update_listeners is one -- publishes it.

Metric: max |published climate target_temperature - configured target| over the
state writes a coordinator listener performs while the solve is awaited (C).
Count key: the value the production entity property returns at write time.

Run:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/s3/climate_midsolve.py [--null] [--perturb]
  --null     away override off (expect 0.0).
  --perturb  in-memory fix: the entity property reads the configured target
             (ctx._config[CONF_TARGET_TEMP]) instead of the live solve config
             (expect 0.0).
Expected (default arm): max_published_deviation=5.00 C (21.0 configured,
16.0 away setback -- DEFAULT_AWAY_TEMPERATURE), after_solve_deviation=0.00. Exact.
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: box B5 (cloud container, linux).
The solve itself is the production _await_optimize, wrapped (not replaced):
the mid-solve write is issued from the loop at the await, as HA's loop would.
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
from heatpump_optimizer import coordinator as coordinator_mod  # noqa: E402
from heatpump_optimizer import climate as climate_mod  # noqa: E402
from heatpump_optimizer.const import CONF_TARGET_TEMP, DEFAULT_TARGET_TEMP  # noqa: E402

NULL = "--null" in sys.argv
PERTURB = "--perturb" in sys.argv
_c0, _t0 = time.process_time(), time.thread_time()
T0 = datetime(2026, 10, 2, 8, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE)


async def main():
    hass = FakeHass({"sensor.indoor": FakeState("21.4"), "sensor.outdoor": FakeState("-3.0")})
    entry = FakeEntry(data={"indoor_temp_entity": "sensor.indoor",
                            "outdoor_temp_entity": "sensor.outdoor",
                            "dhw_tank_volume": 180.0}, entry_id="climsolve")
    c = coordinator_mod.HeatPumpOptimizerCoordinator(hass, entry)
    c._away_state.migrated_helpers = True
    c._prices = [{"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
                  "starts_at": (T0 + timedelta(hours=h)).isoformat(), "level": "NORMAL"}
                 for h in range(48)]
    c._weather_forecast = [{"datetime": (T0 + timedelta(hours=h)).isoformat(),
                            "temperature": -5.0, "wind_speed": 3.0,
                            "precipitation": 0.0, "humidity": 85.0} for h in range(48)]
    dt_util.freeze(T0)
    await c._update_current_state()
    if not NULL:
        await c.async_set_away(active=True, return_time=(T0 + timedelta(days=3)).isoformat(),
                               refresh=False)
    configured = float(c.target_temperature)
    ent = climate_mod.HeatPumpOptimizerClimate(c, entry)
    published = []
    c.async_add_listener(lambda: published.append(ent.target_temperature))
    in_solve = []
    orig = coordinator_mod._await_optimize

    async def _wrapped(*a, **k):
        n0 = len(published)
        await c._async_peak_guard_transition()   # an event-driven write mid-solve
        in_solve.extend(published[n0:])
        return await orig(*a, **k)

    with mock.patch.object(coordinator_mod, "_await_optimize", _wrapped):
        dt_util.freeze(T0 + timedelta(minutes=15))
        status = await c.async_run_optimization()
    after = ent.target_temperature
    dev = max((abs(v - configured) for v in in_solve), default=float("nan"))
    return status, configured, in_solve, dev, abs(after - configured)


def _configured_target(self):
    return float(self.coordinator._ctx._config.get(CONF_TARGET_TEMP, DEFAULT_TARGET_TEMP))

if PERTURB:
    with mock.patch.object(climate_mod.HeatPumpOptimizerClimate, "target_temperature",
                           property(_configured_target)):
        status, configured, in_solve, dev, after = asyncio.run(main())
else:
    status, configured, in_solve, dev, after = asyncio.run(main())
print(f"arm={'perturb' if PERTURB else 'null' if NULL else 'default'} solve_status={status} "
      f"configured={configured} published_mid_solve={in_solve}")
print(f"RESULT max_published_deviation={dev:.2f} C")
print(f"RESULT after_solve_deviation={after:.2f} C")
cpu, thr = time.process_time() - _c0, time.thread_time() - _t0
print(f"RESULT thread_factor={cpu / thr if thr else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
except Exception:
    sw = 'na'
print(f"RESULT swapins={sw}")
