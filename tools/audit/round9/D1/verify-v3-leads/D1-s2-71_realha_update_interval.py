"""V3 verify of D1-s2-71 (P11): build the REAL HeatPumpOptimizerCoordinator against genuine
Home Assistant 2026.2.3 (no tests/hastub) at the same 4 configured intervals the finder used,
and read back coordinator.update_interval from the real DataUpdateCoordinator base class.

Metric: of 4 configured optimization_interval cells (5, 15, 30, 60 min), count whose
coordinator.update_interval is readable and equals timedelta(minutes=cell) after the real
HeatPumpOptimizerCoordinator.__init__ over the REAL upstream DataUpdateCoordinator.

Command (real half, no tests/hastub on the path):
    PYTHONPATH=custom_components:tests /root/venvha/bin/python \
        tools/audit/round9/D1/verify-v3-leads/D1-s2-71_realha_update_interval.py
Expected: matching_cells=4 of 4 (upstream DataUpdateCoordinator.__init__ stores
self.update_interval = update_interval verbatim), against the stub's
unreadable_cells=4 of 4 / matching_cells=0 of 4 (l3_update_interval.py). This is the real-HA
half of the reach check the finding's class_guess (P11) rests on.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Home Assistant 2026.2.3 (venvha).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
import asyncio
import tempfile
import resource

_T0 = (time.process_time(), time.thread_time())

import typing
typing.ByteString = bytes  # CPython 3.14 compat shim, per SUBSEAT.md

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from datetime import timedelta  # noqa: E402
import homeassistant.core as core  # noqa: E402
from harness import FakeEntry  # noqa: E402 (no hastub dependency: only imports ConfigEntryState)
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer.const import (  # noqa: E402
    CONF_OPTIMIZATION_INTERVAL, CONF_INDOOR_TEMP_ENTITY, CONF_OUTDOOR_TEMP_ENTITY,
)

MISSING = object()
CELLS = (5, 15, 30, 60)
unreadable = matching = ctl = 0


async def build(minutes):
    d = tempfile.mkdtemp()
    hass = core.HomeAssistant(d)
    hass.states = core.StateMachine(hass.bus, hass.loop)
    hass.states.async_set("sensor.indoor", "21.0")
    hass.states.async_set("sensor.outdoor", "-3.0")
    entry = FakeEntry(data={
        CONF_OPTIMIZATION_INTERVAL: minutes,
        CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
        CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    })
    return HeatPumpOptimizerCoordinator(hass, entry)


for minutes in CELLS:
    coord = asyncio.run(build(minutes))
    got = getattr(coord, "update_interval", MISSING)
    unreadable += got is MISSING
    matching += got == timedelta(minutes=minutes)
    ctl += (getattr(coord, "name", MISSING) is not MISSING
            and getattr(coord, "config_entry", MISSING) is not MISSING)
    print(f"cell interval={minutes:3d} min update_interval={'<absent>' if got is MISSING else got}")

print(f"RESULT real_unreadable_cells={unreadable} of {len(CELLS)} count")
print(f"RESULT real_matching_cells={matching} of {len(CELLS)} count")
print(f"RESULT real_null_control_kept_attrs_readable={ctl} of {len(CELLS)} count")

cpu = time.process_time() - _T0[0]
thr = time.thread_time() - _T0[1]
print(f"RESULT thread_factor={(cpu / thr) if thr else 1.0:.3f}")
try:
    load1 = os.getloadavg()[0]
except OSError:
    load1 = -1.0
print(f"RESULT load1={load1}")
ru = resource.getrusage(resource.RUSAGE_SELF)
print(f"RESULT swapins={ru.ru_minflt}")
