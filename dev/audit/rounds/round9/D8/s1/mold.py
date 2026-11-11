#!/usr/bin/env python3
"""D8-s1 (audit round 9), D8.M2: Mold Floor Breach in the DHW-only cell.

METRIC: MoldFloorBreachBinarySensor.is_on and its floor_c/shortfall_c after two
  real cycles in coord_dhw+tuya_dhw_only with the room at the given temperature.
RUN:   PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D8/s1/mold.py
EXPECTED at 1936d5ca72a06556eeed4e8e5bf3dea520e517e1: see REPORT.md.
MACHINE: B6 cloud container, 4 CPU, CPython 3.14.0rc2.
"""
import os, sys, asyncio, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matrix as M
from homeassistant.util import dt as dt_util

t_cpu, t_thr = time.process_time(), time.thread_time()
cfg = {**M.topologies()["coord_dhw"], **M.FEATURES["tuya_dhw_only"]}
for room in (21.4, 16.0):
    hass, coord, ents, _ = M.build(cfg)
    mold = next(e for e in ents if e._attr_translation_key == "mold_floor_breach")
    for c in range(2):
        now = M.T0 + c * M.STEP
        dt_util.freeze(now)
        M.set_inputs(hass, {**M.INPUTS[c], "sensor.indoor": room - 0.3 * c}, now)
        coord.data = asyncio.run(coord._async_update_data())
    print(f"  room={room}: on={mold.is_on} attrs={mold.extra_state_attributes}")
    print(f"RESULT mold_on_room_{str(room).replace('.', '_')}={int(mold.is_on)} bool")
    dt_util.freeze(None)
cpu, thr = time.process_time() - t_cpu, time.thread_time() - t_thr
print(f"RESULT thread_factor={cpu / thr if thr else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=" + [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1])
