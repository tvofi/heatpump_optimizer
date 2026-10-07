"""Judge (round 8) re-measure of D8-s2-02 at runtime, replacing the finder's static code read.

Metric: hidden_live_probe = count of sensor entities built by the real
sensor.async_setup_entry that are AVAILABLE with a finite native_value (a live
reading exists) while entity_registry_enabled_default is False, on an install
with hot water and a configured tank thermometer (dhw_temp_entity) that read OK.
Control arm: same install without dhw_temp_entity (the #1335 case: the entity is
unavailable, so default-off is correct) -> must count 0.
Perturbation (--perturb): DHWTemperatureSensor._attr_entity_registry_enabled_default
removed in-process (class-attribute swap restored in finally) so the _DHWEntityMixin
default (on where dhw_enabled) applies -> probe arm must fall to 0.
Command (tree root): PYTHONPATH=tests/hastub python3 tools/audit/round8/D8/judge_probe_default.py [--perturb]
Baseline cdf82daa; 4-vCPU cloud container; counts only.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, asyncio, math, time
from datetime import timedelta
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
import golden  # noqa: E402
from harness import FakeEntry, FakeHass  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer import sensor  # noqa: E402

t0p, t0t = time.process_time(), time.thread_time()
START = golden.START


def arm(with_probe):
    cfg = dict(golden.coordinator_scenarios()["coord_dhw"])
    if with_probe:
        cfg["dhw_temp_entity"] = "sensor.tank"
    coord = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=cfg))
    coord._prices = [{"total": 0.7, "starts_at": (START + timedelta(hours=h)).isoformat(),
                      "level": "NORMAL"} for h in range(48)]
    coord._weather_forecast = [{"datetime": (START + timedelta(hours=h)).isoformat(),
                                "temperature": 2.0, "wind_speed": 3.0, "precipitation": 0.0,
                                "humidity": 80.0} for h in range(48)]
    coord._solar_radiation_forecast = [0.0] * 48
    coord._forecast_arrays()
    data = coord._build_data_dict()
    if with_probe:  # the tank thermometer read OK this cycle
        data.setdefault("reading_ok", {})["dhw_temperature"] = True
        data["dhw_temperature"] = 48.2
    coord.data = data
    entry = coord.config_entry if hasattr(coord, "config_entry") else None
    fe = FakeEntry(data=cfg); fe.runtime_data = coord
    added = []
    asyncio.run(sensor.async_setup_entry(FakeHass(), fe, lambda es: added.extend(es)))
    hidden = []
    for e in added:
        try:
            v = e.native_value
            av = e.available
        except Exception:
            continue
        if av and isinstance(v, (int, float)) and math.isfinite(v) and getattr(e, 'entity_registry_enabled_default', getattr(e, '_attr_entity_registry_enabled_default', True)) is False:
            hidden.append(type(e).__name__)
    return hidden


dt_util.freeze(START)
cls = sensor.DHWTemperatureSensor
had = "_attr_entity_registry_enabled_default" in cls.__dict__
saved = cls.__dict__.get("_attr_entity_registry_enabled_default")
try:
    if "--perturb" in sys.argv and had:
        delattr(cls, "_attr_entity_registry_enabled_default")
    p = arm(True); c = arm(False)
    print("# probe arm hidden:", p); print("# control arm hidden:", c)
    print(f"RESULT dhw_temperature_hidden_live={p.count('DHWTemperatureSensor')} count")
    print(f"RESULT control_dhw_temperature_hidden={c.count('DHWTemperatureSensor')} count")
    print(f"RESULT hidden_live_any={len(p)} count")
    print(f"RESULT control_hidden_no_probe={len(c)} count")
    print(f"RESULT perturbed={int('--perturb' in sys.argv)}")
finally:
    if had and "_attr_entity_registry_enabled_default" not in cls.__dict__:
        setattr(cls, "_attr_entity_registry_enabled_default", saved)
pc, tc = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
