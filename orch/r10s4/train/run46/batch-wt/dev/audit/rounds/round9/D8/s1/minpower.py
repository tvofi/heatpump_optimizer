#!/usr/bin/env python3
"""D8-s1 (audit round 9), D8.M2: published pump power against the plan's own on/off.

METRIC: over every step of one real solve's horizon, the number of steps at
  which Recommended Power (``CurrentPowerSensor.native_value``) publishes more
  than 0.05 kW while Heat Pump Action (``HeatPumpActionSensor.native_value``)
  publishes "off" -- i.e. the plan's own ``heat_pump_on`` is False. Each step is
  made current with the production ``get_current_action(result, step)`` and
  published through ``_build_data_dict``, exactly as a cycle at that instant.
KEY: the value both entities return, never the payload.
RUN:   PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D8/s1/minpower.py
       [--perturb]   commanded_power_kw -> 0 when the action's heat_pump_on is False
EXPECTED at 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (exact counts): see REPORT.md;
  the null arm (heat_pump_min_power 0.2 kW, on-threshold 0.1 kW) is the control.
MACHINE: B6 cloud container, 4 CPU, CPython 3.14.0rc2.
"""
from __future__ import annotations

import os
import sys
import asyncio
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matrix as M  # thread pin + tz first
from homeassistant.util import dt as dt_util
from heatpump_optimizer import entity as ent_mod
from heatpump_optimizer import sensor

CELLS = ["coord_minimal", "coord_dhw", "coord_two_zone", "coord_grid_fee", "coord_all_features"]
MIN_POWERS = [0.2, 0.6, 1.0, 1.5]


def main() -> int:
    if "--perturb" in sys.argv:
        real = ent_mod.commanded_power_kw

        def gated(action):
            if action and action.get("heat_pump_on") is False:
                return 0.0 if action.get("power") is not None else None
            return real(action)
        sensor.commanded_power_kw = gated
    t_cpu, t_thr = time.process_time(), time.thread_time()
    grid: dict[tuple[str, float], tuple[int, int, float]] = {}
    for cell in CELLS:
        for pmin in MIN_POWERS:
            cfg = {**M.topologies()[cell], "heat_pump_min_power": pmin}
            hass, coord, ents, _ = M.build(cfg)
            by = {e._attr_translation_key: e for e in ents}
            dt_util.freeze(M.T0)
            M.set_inputs(hass, M.INPUTS[0], M.T0)
            coord.data = asyncio.run(coord._async_update_data())
            result = coord._optimization_result
            bad, steps, worst = 0, 0, 0.0
            for ts in result.timestamps:
                coord._current_action = coord._optimizer.get_current_action(result, ts)
                coord.data = coord._build_data_dict()
                steps += 1
                rec = by["recommended_power"].native_value
                state = by["heat_pump_action"].native_value
                if state == "off" and isinstance(rec, (int, float)) and rec > 0.05:
                    bad += 1
                    worst = max(worst, rec)
            dt_util.freeze(None)
            grid[(cell, pmin)] = (bad, steps, worst)
            print(f"  {cell:20s} min_power={pmin:3.1f}: {bad:3d}/{steps} steps publish power while 'off' (max {worst:.2f} kW)", flush=True)
    for pmin in MIN_POWERS:
        vals = [grid[(c, pmin)][0] for c in CELLS]
        tag = str(pmin).replace(".", "_")
        print(f"RESULT power_while_off_min{tag}={sum(vals)} count (steps, {len(CELLS)} cells)")
        print(f"RESULT power_while_off_min{tag}_range={min(vals)}..{max(vals)} count per cell")
        drop = sum(vals) - max(vals)
        print(f"RESULT power_while_off_min{tag}_drop_max_cell={drop} count")
    worst = max(v[2] for v in grid.values())
    print(f"RESULT worst_published_kw_while_off={worst:.2f} kW")
    cpu, thr = time.process_time() - t_cpu, time.thread_time() - t_thr
    print(f"RESULT thread_factor={cpu / thr if thr else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=" + [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1])
    return 0


if __name__ == "__main__":
    sys.exit(main())
