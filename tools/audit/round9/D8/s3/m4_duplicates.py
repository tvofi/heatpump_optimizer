"""D8-s3 / D8.M4 -- enabled-by-default entities that publish another enabled entity's value.

Metric (one line): over the 5 golden coordinator topologies x 3 input cycles
(indoor 21.4 / 20.1 / 22.7 degC, outdoor -3 / -8 / 2 degC), the number of
unordered pairs of enabled-by-default numeric sensors with the same unit whose
native_value is equal in every cycle of every topology while it changes
between cycles (a byte-for-byte duplicate, not a coincidence).
Count key: native_value as the platform delivers it via async_setup_entry,
and the registry default read as tests/entities.py:registry_default reads it.

Command (repo root):
    PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python tools/audit/round9/D8/s3/m4_duplicates.py
    ... --perturb  (in memory: UpperFloorTempSensor._attr_entity_registry_enabled_default = False)
Expected: duplicate_enabled_pairs=1 (exact); --perturb -> 0 (to_zero).
Null control: the same pairs with the registry-default filter removed
(duplicate_pairs_any_default) stays 1 under --perturb while the enabled count
falls to 0 -- the move is the default, not the value. (Lower Floor Temperature
also falls back to the room reading but is unavailable without its probe, so
it never enters either count.)
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: cloud container B4 (linux).
Instrumented: heatpump_optimizer.sensor:UpperFloorTempSensor.native_value,
heatpump_optimizer.sensor:IndoorTempSensor.native_value, every sensor via
heatpump_optimizer.sensor:async_setup_entry.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio
import itertools
import sys
import time
from datetime import timedelta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import roster  # noqa: E402
import golden  # noqa: E402
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import sensor, const  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

if "--perturb" in sys.argv:
    sensor.UpperFloorTempSensor._attr_entity_registry_enabled_default = False

t0p, t0t = time.process_time(), time.thread_time()
CYCLES = [(21.4, -3.0), (20.1, -8.0), (22.7, 2.0)]


def series(config):
    """entity_id -> (enabled, unit, [value per cycle]) over CYCLES."""
    config = {**config, const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
              const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor"}
    hass = FakeHass()
    entry = FakeEntry(data=config)
    dt_util.freeze(golden.START)
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    out = {}
    try:
        for c, (indoor, outdoor) in enumerate(CYCLES):
            dt_util.freeze(golden.START + timedelta(hours=c))
            hass.states.set("sensor.indoor", FakeState(str(indoor)))
            hass.states.set("sensor.outdoor", FakeState(str(outdoor)))
            coord._prices = [
                {"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
                 "starts_at": (golden.START + timedelta(hours=h)).isoformat(),
                 "level": "NORMAL"} for h in range(48)]
            coord._weather_forecast = [
                {"datetime": (golden.START + timedelta(hours=h)).isoformat(),
                 "temperature": outdoor, "wind_speed": 3.0,
                 "precipitation": 0.0, "humidity": 85.0} for h in range(48)]
            coord._solar_radiation_forecast = [0.0] * 48
            asyncio.run(coord._update_current_state())
            coord._forecast_arrays()
            coord.data = coord._build_data_dict()
            for plat, e in roster.collect(hass, entry, coord):
                if plat != "sensor":
                    continue
                v = e.native_value if e.available else None
                rec = out.setdefault(e.entity_id, [roster.enabled_default(e),
                                                   getattr(e, "_attr_native_unit_of_measurement", None), []])
                rec[2].append(v if isinstance(v, (int, float)) and not isinstance(v, bool) else None)
    finally:
        dt_util.freeze(None)
    return out


def dup_pairs(runs, need_enabled):
    ids = sorted(runs[0])
    pairs = []
    for a, b in itertools.combinations(ids, 2):
        ok = True
        for r in runs:
            ea, ua, va = r[a]
            eb, ub, vb = r[b]
            if need_enabled and not (ea and eb):
                ok = False
                break
            if ua != ub or None in va or va != vb or len(set(va)) < 2:
                ok = False
                break
        if ok:
            pairs.append((a, b))
    return pairs


runs = [series(cfg) for cfg in golden.coordinator_scenarios().values()]
pairs = dup_pairs(runs, True)
anyd = dup_pairs(runs, False)
for a, b in pairs:
    print(f"DUPLICATE_ENABLED {a} == {b}")
for a, b in anyd:
    print(f"duplicate_any_default {a} == {b}")
print(f"RESULT topologies={len(runs)} count")
print(f"RESULT duplicate_enabled_pairs={len(pairs)} count")
print(f"RESULT duplicate_pairs_any_default={len(anyd)} count")
pc, tc = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = next(int(l.split()[1]) for l in open("/proc/vmstat") if l.startswith("pswpin "))
except Exception:
    sw = -1
print(f"RESULT swapins={sw}")
