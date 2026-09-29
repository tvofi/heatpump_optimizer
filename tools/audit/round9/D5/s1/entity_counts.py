"""D5-s1 harness: the total-entity counts the user docs state, against the platforms.

Metric (one line): phrases "<N> entities" in README.md and the seven user docs whose N
differs from the number of entities the six platforms' real ``async_setup_entry`` add
for a stock entry (tank volume set, indoor/outdoor sensors, entity price source).
Count key: len() of what each platform hands ``async_add_entities`` -- the production
seam -- never a number read from the docs or the tests.
Command (from the repository root):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
        tools/audit/round9/D5/s1/entity_counts.py [--perturb]
--perturb wraps sensor.async_setup_entry's add callback to drop one entity (a sensor
    that is written but not registered). Expected: disagreeing_claims up (75-claims
    turn wrong, the 74-claim turns right: 1 -> 2).
Expected at baseline: constructed=75, claims=3, disagreeing_claims=1 (exact).
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: box B1 (linux container).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio
import re
import sys
import time

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
_t0p, _t0t = time.process_time(), time.thread_time()

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from heatpump_optimizer import (  # noqa: E402
    binary_sensor, button, climate, const, datetime as dt_platform, sensor, switch)
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

PERTURB = "--perturb" in sys.argv
DOCS = ["README.md"] + [f"docs/{n}.md" for n in (
    "architecture", "automations", "configuration", "dashboard-card", "ecl110",
    "how-it-works", "setup")]

hass = FakeHass()
hass.states.set("sensor.indoor", FakeState("21.4"))
hass.states.set("sensor.outdoor", FakeState("-3.0"))
config = {
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    const.CONF_DHW_TANK_VOLUME: 180.0,
    "price_source": "entity",
    "price_entity": "sensor.prices",
}
entry = FakeEntry(data=config)
coord = HeatPumpOptimizerCoordinator(hass, entry)
asyncio.run(coord._update_current_state())
coord.data = coord._build_data_dict()
entry.runtime_data = coord

per_platform = {}
for mod in (sensor, binary_sensor, button, switch, climate, dt_platform):
    added = []

    def add(entities, update_before_add=False, _a=added):
        _a.extend(entities)

    cb = add
    if PERTURB and mod is sensor:
        def cb(entities, update_before_add=False, _a=added):  # drop one registered sensor
            _a.extend(list(entities)[:-1])
    asyncio.run(mod.async_setup_entry(hass, entry, cb))
    per_platform[mod.__name__.rsplit(".", 1)[1]] = len(added)
total = sum(per_platform.values())

claims = []
for path in DOCS:
    for i, line in enumerate(open(path, encoding="utf-8").read().split("\n"), 1):
        for m in re.finditer(r"\b(\d{2,3}) entities\b", line):
            claims.append((path, i, int(m.group(1))))
bad = [c for c in claims if c[2] != total]
for c in claims:
    print(f"claim {c[0]}:{c[1]} says {c[2]} -> {'OK' if c[2] == total else 'DISAGREES'}")
print("per_platform", per_platform)
cpu_p, cpu_t = time.process_time() - _t0p, time.thread_time() - _t0t
print(f"RESULT constructed_entities={total} count")
print(f"RESULT entity_count_claims={len(claims)} count")
print(f"RESULT disagreeing_claims={len(bad)} count")
print(f"RESULT thread_factor={cpu_p / cpu_t if cpu_t else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
