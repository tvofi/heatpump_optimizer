"""V2 (independent) for D1-s2-71: every keyword the integration passes to DataUpdateCoordinator,
read back on the hastub base class versus the REAL HA 2026.2.3 base class.

Metric: over 6 configured cells (optimization_interval 1, 7, 20, 45, 120 min and the key absent,
i.e. DEFAULT_OPTIMIZATION_INTERVAL) x every keyword the real HeatPumpOptimizerCoordinator.__init__
passes to DataUpdateCoordinator.__init__ (captured by a spy on the stub base __init__), count
(cell, keyword) pairs where the REAL homeassistant.helpers.update_coordinator.DataUpdateCoordinator
of HA 2026.2.3 -- constructed in a subprocess on a real HomeAssistant(config_dir) with the captured
arguments -- exposes the attribute equal to the passed value while the stub-built coordinator does
not. Count key: getattr(coordinator, <keyword>) on each side.
Command: LEADS_HA_ROOT=<root> PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/verify-v2/leads_update_interval_realha.py [--perturb]
Expected: keywords_passed=name,config_entry,update_interval; divergent_pairs=6 of 18 (exact:
update_interval in every cell; name and config_entry readable on both). --perturb (the stub
__init__ keeps update_interval, in memory) -> 0 of 18.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: cloud box G1-V2, 4 vCPU Linux, CPython 3.14.0rc2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json
import resource
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import leads_realha  # noqa: E402

T0 = (time.process_time(), time.thread_time())
from homeassistant.helpers import update_coordinator as uc  # noqa: E402  (stub)
from harness import FakeHass, FakeEntry  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer.const import CONF_OPTIMIZATION_INTERVAL  # noqa: E402

PERTURB = "--perturb" in sys.argv
_orig = uc.DataUpdateCoordinator.__init__
CAPTURED = []


def spy(self, hass, logger, **kw):
    CAPTURED.append(kw)
    _orig(self, hass, logger, **kw)
    if PERTURB:
        self.update_interval = kw.get("update_interval")


uc.DataUpdateCoordinator.__init__ = spy
CELLS = (1, 7, 20, 45, 120, None)
MISSING = object()
stub_rows = []
for minutes in CELLS:
    data = {} if minutes is None else {CONF_OPTIMIZATION_INTERVAL: minutes}
    entry = FakeEntry(data=data)
    coord = HeatPumpOptimizerCoordinator(FakeHass({}), entry)
    kw = CAPTURED[-1]
    row = {}
    for k, v in kw.items():
        got = getattr(coord, k, MISSING)
        row[k] = (got is not MISSING and got is v) or (got is not MISSING and got == v)
    stub_rows.append((kw, row))
uc.DataUpdateCoordinator.__init__ = _orig

REAL = r'''
import asyncio, json, logging, sys, tempfile
from datetime import timedelta
logging.disable(logging.CRITICAL)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
cells = json.loads(sys.stdin.read())
async def main():
    hass = HomeAssistant(tempfile.mkdtemp())
    out = []
    for c in cells:
        kw = {"name": c["name"], "config_entry": None,
              "update_interval": timedelta(seconds=c["update_interval_s"])}
        d = DataUpdateCoordinator(hass, logging.getLogger("x"), **kw)
        out.append({k: (hasattr(d, k) and getattr(d, k) == v) for k, v in kw.items()})
    print(json.dumps(out))
asyncio.run(main())
'''
payload = []
for kw, _ in stub_rows:
    extra = set(kw) - {"name", "config_entry", "update_interval"}
    if extra:
        sys.exit(f"integration passes keywords this harness does not map: {extra}")
    payload.append({"name": kw["name"], "update_interval_s": kw["update_interval"].total_seconds()})
real_rows = json.loads(leads_realha.run_real(REAL, json.dumps(payload)))

div = total = 0
for minutes, (kw, srow), rrow in zip(CELLS, stub_rows, real_rows):
    for k in kw:
        total += 1
        d = bool(rrow[k]) and not srow[k]
        div += d
    print(f"RESULT cell_{minutes if minutes is not None else 'default'}min: "
          + " ".join(f"{k}:real={int(rrow[k])},stub={int(srow[k])}" for k in kw))
print("RESULT keywords_passed=" + ",".join(stub_rows[0][0]))
print(f"RESULT divergent_pairs={div} of_{total}")
print(f"RESULT perturbed={int(PERTURB)}")
pc, tc = time.process_time() - T0[0], time.thread_time() - T0[1]
print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_majflt}")
