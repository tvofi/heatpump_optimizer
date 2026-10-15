"""D9-s1 solves_per_cycle + loop_thread_work over real coordinator cycles.

Metrics:
 * solves_per_cycle = entries into optimizer._multi_start_minimize during one
   HeatPumpOptimizerCoordinator._async_update_data(), split by the job the
   coordinator handed to coordinator._await_process (fn.__name__) and, for
   optimize_in_process, by the coordinator method that called _await_optimize.
 * loop_thread_work = time.thread_time() on the calling (loop) thread across
   the cycle MINUS the thread time spent inside the jobs handed to
   _await_process and FakeHass.async_add_executor_job (which this rig runs
   inline), i.e. the work that stays on the loop. Ratio to
   tests/stress.py:reference_solve thread CPU.
Key: counts keyed on the production seam _multi_start_minimize entries.
Command: PYTHONPATH=tests/hastub /Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python dev/audit/rounds/round10/D9/s1/cycle.py [--cycles N] [--perturb noshadow]
Expected (17f1c55fad1b, Darwin arm64): counts exact; CPU provisional +-30%.
Perturbation: --cycles 2 doubles the per-run total (per-cycle count stable);
--perturb noshadow stubs coordinator method async_run_what_if_shadow-family
(whatever non-main caller is found) to drop the non-main count to 0.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, asyncio, argparse, inspect, collections
from datetime import datetime, timedelta, timezone
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
import numpy as np
from harness import FakeHass, FakeState, FakeEntry
from homeassistant.util import dt as dt_util
from heatpump_optimizer import coordinator as cm, optimizer as om, const

ap = argparse.ArgumentParser()
ap.add_argument("--cycles", type=int, default=3)
ap.add_argument("--perturb", default="none")
a = ap.parse_args()
NOW = datetime(2026, 1, 15, 6, 0, tzinfo=timezone.utc)

counts = collections.Counter()
tag = ["(none)"]
_msm = om._multi_start_minimize
def msm(*x, **k):
    counts[tag[-1] if isinstance(tag, list) else tag] += 1
    return _msm(*x, **k)
om._multi_start_minimize = msm

off = [0.0]
async def await_process(hass, fn, *args):
    caller = "?"
    for fr in inspect.stack()[1:6]:
        if fr.function not in ("_await_process", "_await_off_loop", "_await_optimize"):
            caller = fr.function; break
    tag.append(f"{fn.__name__}<-{caller}")
    t = time.thread_time()
    try:
        return fn(*args)
    finally:
        off[0] += time.thread_time() - t
        tag.pop()
cm._await_process = await_process

def make(extra):
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.0"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    _ex = hass.async_add_executor_job
    async def ex(fn, *args):
        t = time.thread_time()
        try:
            return await _ex(fn, *args)
        finally:
            off[0] += time.thread_time() - t
    hass.async_add_executor_job = ex
    entry = FakeEntry(data={const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
                            const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor", **extra},
                      entry_id="e1")
    c = cm.HeatPumpOptimizerCoordinator(hass, entry)
    c._prices = [{"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
                  "starts_at": (NOW + timedelta(hours=h - 2)).isoformat(), "level": "NORMAL"}
                 for h in range(50)]
    c._weather_forecast = [{"datetime": (NOW + timedelta(hours=h)).isoformat(),
                            "temperature": -5.0, "wind_speed": 3.0, "precipitation": 0.0,
                            "humidity": 85.0} for h in range(48)]
    async def noop(*_a, **_k): return None
    c._fetch_tibber_prices = noop; c._fetch_weather_forecast = noop; c._fetch_solar_forecast = noop
    return c

CONFIGS = {
    "dhw": {const.CONF_DHW_TANK_VOLUME: 180.0},
    "space_only": {},
    "two_zone_dhw": {const.CONF_DHW_TANK_VOLUME: 180.0, "upper_floor_thermal_mass": 3.0,
                     "lower_floor_thermal_mass": 8.0, "upper_floor_heat_loss": 0.08,
                     "lower_floor_heat_loss": 0.07},
    "all_features": {const.CONF_DHW_TANK_VOLUME: 200.0, "peak_tariff_enabled": True,
                     "peak_tariff_price_per_kw": 45.0, "pv_enabled": True, "pv_peak_kw": 8.0,
                     "pv_export_price": 0.3, "away_enabled": True,
                     "external_heat_detection_enabled": True, "comfort_learning_enabled": True,
                     "system_identification_enabled": True, "compressor_cycling_cost": 0.5},
}
import stress
ref = sorted(stress.reference_solve()[2] for _ in range(3))[1]
print(f"RESULT reference_solve_thread_ms={ref:.1f} ms (provisional)")
dt_util.freeze(NOW)
t0p, t0t = time.process_time(), time.thread_time()
try:
    for name, extra in CONFIGS.items():
        c = make(extra)
        for i in range(a.cycles):
            dt_util.freeze(NOW + timedelta(minutes=15 * i))
            counts.clear(); off[0] = 0.0
            t = time.thread_time()
            try:
                asyncio.run(c._async_update_data())
            except Exception as e:
                print(f"# {name} cycle {i} raised {type(e).__name__}: {e}")
            tot = time.thread_time() - t
            loop_ms = (tot - off[0]) * 1e3
            for k, v in sorted(counts.items()):
                print(f"RESULT {name}.c{i}.solves[{k}]={v} count")
            print(f"RESULT {name}.c{i}.solves_total={sum(counts.values())} count")
            print(f"RESULT {name}.c{i}.loop_thread_ms={loop_ms:.1f} ms (provisional)")
            print(f"RESULT {name}.c{i}.offloaded_thread_ms={off[0]*1e3:.1f} ms (provisional)")
            print(f"RESULT {name}.c{i}.loop_share_of_ref={loop_ms/ref:.3f} ratio (provisional)")
finally:
    dt_util.freeze(None)
pc, tc = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pc/tc:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
import resource
print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap}")
