"""Non-finding probe (lead from D1-s4): 'nan'/'inf' strings in the thermal-learning store's
internal_gains_profile never reach the solver.

Metric: of 4 hostile 24-slot gain profiles (all 'nan', one 'inf', one '-Infinity', one float nan
written by the stub's json), count loads after which coord._internal_gains_profile holds a
non-finite value. Count key: the loaded profile (production loader
HeatPumpOptimizerCoordinator._async_load_thermal_learning through QuarantiningStore.async_load).
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/leads/gains_nan_probe.py [--raw]
Expected: nonfinite=0 of 4. --raw (perturbation: bypass the store's _sanitize) -> 4 of 4.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, machine B10 cloud container.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _rig  # noqa: E402
import asyncio, json, math
from homeassistant.helpers import storage
from heatpump_optimizer import store as store_mod

RAW = "--raw" in sys.argv
if RAW:
    store_mod._sanitize = lambda v: v
PROFILES = [["nan"] * 24, ["1.0"] * 23 + ["inf"], ["-Infinity"] + [0.5] * 23, [float("nan")] + [0.5] * 23]


def run():
    _rig.freeze()
    bad = 0
    for prof in PROFILES:
        storage._reset_store_disk()
        hass, entry, coord = _rig.make_coord()
        key = coord._thermal_learning_store._key
        storage._DISK[key] = json.dumps({"internal_gains_profile": prof})
        asyncio.run(coord._async_load_thermal_learning())
        p = coord._internal_gains_profile
        bad += p is not None and not all(math.isfinite(float(g)) for g in p)
    print(f"RESULT nonfinite={bad} of_{len(PROFILES)}")


run()
_rig.tail()
