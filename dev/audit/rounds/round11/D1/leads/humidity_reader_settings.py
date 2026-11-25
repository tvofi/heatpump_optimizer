"""D1-s2-52: the indoor-humidity read ignores the entry's staleness settings.

Metric: over two configuration arms (staleness watchdog switched off; age
scale 3.0), the number of arms where the coordinator's real
HeatPumpOptimizerCoordinator._indoor_humidity_value returns None for a humidity
reading aged 1.5x its scale-1 limit, while an InputReader built with the entry's
own staleness_watchdog_enabled / staleness_max_age_scale (as the two other
coordinator readers build it) delivers the value. Count key: the value
_indoor_humidity_value delivers (None vs a number), not any input attribute.
Null control: the default arm (watchdog on, scale 1.0) at the same age -- both
withhold, so the disagreement is 0; and a fresh reading in every arm -- both
deliver (fresh_disagree=0).
Run:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/leads/humidity_reader_settings.py [--perturb]
  --perturb replaces coordinator.InputReader in memory with one that takes the
  entry's enabled/scale (the one-line fix at coordinator.py:9175); config_arms_disagree
  must go to 0.
Expected: config_arms_disagree=2 (exact), null_disagree=0, fresh_disagree=0.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (planted finder export
audit-r11-leads-px), machine: owner's macOS box (B8).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
from datetime import timedelta

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
from harness import FakeHass, FakeState, FakeEntry  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import coordinator as coord_mod, inputs  # noqa: E402
from heatpump_optimizer.const import CONF_INDOOR_HUMIDITY_ENTITY  # noqa: E402

c0, t0 = time.process_time(), time.thread_time()
PERTURB = "--perturb" in sys.argv
_Real = inputs.InputReader


def coordinator(cfg, age_min):
    now = dt_util.utcnow()
    stamp = now - timedelta(minutes=age_min)
    states = {"sensor.rh": FakeState("55.0", last_updated=stamp, unit="%")}
    base = {"tibber_token": "x", "weather_entity": "weather.home",
            "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
            "indoor_humidity_entity": "sensor.rh", **cfg}
    hass = FakeHass(states)
    return coord_mod.HeatPumpOptimizerCoordinator(hass, FakeEntry(data=base)), hass


def configured_value(c, hass):
    ec = getattr(c, "_ctx", c)._config
    r = _Real(hass, ec, enabled=ec.staleness_watchdog_enabled,
              scale=ec.staleness_max_age_scale).read(
        CONF_INDOOR_HUMIDITY_ENTITY, entity_id="sensor.rh")
    return r.value if r.ok else None


def production_value(c):
    if PERTURB:
        ec = getattr(c, "_ctx", c)._config

        def _fixed(hass, config, **kw):
            kw.setdefault("enabled", ec.staleness_watchdog_enabled)
            kw.setdefault("scale", ec.staleness_max_age_scale)
            return _Real(hass, config, **kw)
        saved = coord_mod.InputReader
        coord_mod.InputReader = _fixed
        try:
            return c._indoor_humidity_value()
        finally:
            coord_mod.InputReader = saved
    return c._indoor_humidity_value()


# Scale-1 limit for this on-change source (no re-report seen).
probe, _h = coordinator({}, 0)
limit = inputs.max_age_for(CONF_INDOOR_HUMIDITY_ENTITY, 1.0, on_change=True)
stale_age = 1.5 * limit
arms = {
    "watchdog_off": {"staleness_watchdog_enabled": False},
    "scale_3": {"staleness_max_age_scale": 3.0},
}
null_arm = {"default": {}}
disagree = null_dis = fresh_dis = 0
for name, cfg in arms.items():
    c, hass = coordinator(cfg, stale_age)
    p, q = production_value(c), configured_value(c, hass)
    print(f"arm {name}: age {stale_age:.0f} min production={p} configured={q}")
    disagree += (p is None) != (q is None)
for name, cfg in {**arms, **null_arm}.items():
    c, hass = coordinator(cfg, 1.0)
    p, q = production_value(c), configured_value(c, hass)
    fresh_dis += (p is None) != (q is None)
for name, cfg in null_arm.items():
    c, hass = coordinator(cfg, stale_age)
    p, q = production_value(c), configured_value(c, hass)
    print(f"null {name}: production={p} configured={q}")
    null_dis += (p is None) != (q is None)

print(f"RESULT limit_scale1={limit:.0f} min")
print(f"RESULT config_arms_disagree={disagree} count")
print(f"RESULT null_disagree={null_dis} count")
print(f"RESULT fresh_disagree={fresh_dis} count")
cpu, th = time.process_time() - c0, time.thread_time() - t0
print(f"RESULT thread_factor={cpu / th if th else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    import resource
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap}")
except Exception:
    print("RESULT swapins=0")
