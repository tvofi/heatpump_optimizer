"""Verifier D1#1, V2 for D1-s2-52: the humidity read vs the entry's staleness settings, over an age grid.

Metric: over arms {watchdog off, scale 2.0, scale 3.0} x ages {1.2, 1.8, 2.5}x the scale-1 limit,
the number of cells where _indoor_humidity_value returns None while the coordinator's own
indoor-TEMPERATURE reader setup (InputReader with the entry's enabled/scale) would deliver a
reading of the same age for the humidity key. Null: the default arm (on, 1.0) -> 0 cells.
Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/verify-1/v2_s2_52_humidity.py
"""
import os
import sys
from datetime import timedelta

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
from harness import FakeHass, FakeState, FakeEntry  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import coordinator as cm, inputs  # noqa: E402
from heatpump_optimizer import const as C  # noqa: E402

KEY = C.CONF_INDOOR_HUMIDITY_ENTITY
probe = inputs.InputReader(FakeHass({}), {})
lim = None
for name in ("INPUT_ON_CHANGE_MAX_AGE_MINUTES", "INPUT_MAX_AGE_MINUTES"):
    lim = getattr(C, name, {}).get(KEY) or lim
print(f"limits: max_age={C.INPUT_MAX_AGE_MINUTES.get(KEY)} on_change={getattr(C, 'INPUT_ON_CHANGE_MAX_AGE_MINUTES', {}).get(KEY)}")


def cell(cfg, age):
    now = dt_util.utcnow()
    st = {"sensor.rh": FakeState("55.0", last_updated=now - timedelta(minutes=age), unit="%")}
    base = {"tibber_token": "x", "weather_entity": "weather.home", "indoor_temp_entity": "sensor.indoor",
            "outdoor_temp_entity": "sensor.outdoor", "indoor_humidity_entity": "sensor.rh", **cfg}
    h = FakeHass(st)
    c = cm.HeatPumpOptimizerCoordinator(h, FakeEntry(data=base))
    ec = getattr(c, "_ctx", c)._config
    r = inputs.InputReader(h, ec, enabled=ec.staleness_watchdog_enabled,
                           scale=ec.staleness_max_age_scale).read(KEY, entity_id="sensor.rh")
    return c._indoor_humidity_value(), (r.value if r.ok else None)


# the effective scale-1 limit as InputReader applies it: smallest age the default reader withholds
lo, hi = 1, 100000
while lo < hi:
    m = (lo + hi) // 2
    if cell({}, m)[1] is None:
        hi = m
    else:
        lo = m + 1
L1 = lo
print(f"effective scale-1 withhold age = {L1} min")
arms = {"watchdog_off": {"staleness_watchdog_enabled": False}, "scale2": {"staleness_max_age_scale": 2.0},
        "scale3": {"staleness_max_age_scale": 3.0}}
hits = 0
for name, cfg in arms.items():
    for f in (1.2, 1.8, 2.5):
        prod, conf = cell(cfg, int(L1 * f))
        d = prod is None and conf is not None
        hits += d
        print(f"{name} age={int(L1 * f)} production={prod} configured={conf} disagree={d}")
null = sum(int(cell({}, int(L1 * f))[0] is None and cell({}, int(L1 * f))[1] is not None) for f in (1.2, 1.8, 2.5))
print(f"RESULT cells_withheld_against_entry_settings={hits} of 9")
print(f"RESULT null_default_disagree={null} of 3")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
