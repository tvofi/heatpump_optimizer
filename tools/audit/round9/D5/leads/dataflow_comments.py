"""D5-s2-51: two optimizer comments describe a data flow the code does not have.

(a) HeatPumpOptimizer._warm_start_starts' docstring calls the handed plan 'the same problem one
    step later'; coordinator._warm_seeded hands the previous power_schedule unshifted. Metric: the
    index offset between the handed _prev_shipped_plan and the previous plan re-aligned to the new
    solve's clock, after one 30-min re-plan (steps are 15 min). Count key: the array
    _warm_seeded attaches to the optimizer the coordinator solves with.
(b) OptimizationResult.buffer_temp_trajectory's comment says 'the model stashes the series on
    itself for the terminal-cost term'. Metric: sequence-valued attribute writes on the
    ThermalModel during one valved solve (buffer_is_store True), run in-process (the harness routes
    _await_process inline so the spy sees the solve). Count key: ThermalModel.__setattr__.
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D5/leads/dataflow_comments.py
Expected: handed_offset_steps=0 while elapsed_steps=2 (misaligned by 2); model_sequence_writes=0
(no stash). Perturbation: --shift (in memory, _warm_seeded drops the elapsed steps and pads the
tail, the alignment the docstring describes) -> handed_offset_steps=2.
Null control for (b): the same counter sees a planted stash (--plant) -> 1.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, machine B10 cloud container.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "D1", "leads"))
import _rig  # noqa: E402
import asyncio
from datetime import timedelta
import numpy as np
from heatpump_optimizer import const, coordinator as cm
from heatpump_optimizer.thermal_model import ThermalModel

SHIFT = "--shift" in sys.argv
PLANT = "--plant" in sys.argv


def warm_start_offset():
    _rig.freeze()
    hass, entry, coord = _rig.make_coord()
    captured = {}
    orig = cm._warm_seeded

    def spy(c, optimizer):
        out = orig(c, optimizer)
        if SHIFT and getattr(optimizer, "_prev_shipped_plan", None) is not None:
            p = optimizer._prev_shipped_plan
            optimizer._prev_shipped_plan = np.concatenate([p[2:], np.repeat(p[-1:], 2)])
        captured["plan"] = getattr(optimizer, "_prev_shipped_plan", None)
        return out
    cm._warm_seeded = spy
    try:
        async def go():
            await coord._update_current_state()
            await coord.async_run_optimization()
            first = np.asarray(coord._optimization_result.power_schedule, dtype=float)
            _rig.freeze(_rig.NOW + timedelta(minutes=30))
            _rig.inject_series(coord, _rig.NOW + timedelta(minutes=30))
            await coord.async_run_optimization()
            return first
        first = asyncio.run(go())
    finally:
        cm._warm_seeded = orig
    handed = captured["plan"]
    # which shift k makes handed[i] == first[i + k] over the overlap?
    best = min(range(0, 5), key=lambda k: float(np.abs(handed[:len(first) - k] - first[k:]).sum()))
    return best


def model_stash():
    _rig.freeze()
    cfg = _rig.base_config(**{const.CONF_MIXING_VALVE_MODE: "manual", const.CONF_BUFFER_TANK_VOLUME: 300.0})
    hass, entry, coord = _rig.make_coord(cfg)
    writes = []
    orig = ThermalModel.__setattr__

    def spy(self, name, value):
        if isinstance(value, (list, tuple, np.ndarray)) and len(value) > 8:
            writes.append(name)
        return orig(self, name, value)
    ThermalModel.__setattr__ = spy
    orig_proc = cm._await_process

    async def inproc(hass_, fn, *args):  # solve on this interpreter so the spy sees the model
        return fn(*args)
    cm._await_process = inproc
    try:
        async def go():
            await coord._update_current_state()
            if PLANT:
                coord._thermal_model.last_buffer_trajectory = [40.0] * 97
            await coord.async_run_optimization()
        asyncio.run(go())
    finally:
        ThermalModel.__setattr__ = orig
        cm._await_process = orig_proc
    res = coord._optimization_result
    return len(writes), bool(coord._thermal_params.buffer_is_store), len(res.buffer_temp_trajectory or [])


off = warm_start_offset()
print(f"RESULT handed_offset_steps={off}")
print("RESULT elapsed_steps=2")
n, store, ntraj = model_stash()
print(f"RESULT model_sequence_writes={n} (buffer_is_store={int(store)}, buffer_temp_trajectory len={ntraj})")
_rig.tail()
