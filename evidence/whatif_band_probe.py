"""Reviewer's probe (not the finder's): the band the what-if (async_simulate,
base=None) solves on, against the live plan's, with a learned store.
Run from a worktree root:
  PYTHONPATH=tests/hastub:custom_components:tests python3 whatif_band_probe.py
"""
import asyncio, importlib.util, sys, os
from unittest import mock
spec = importlib.util.spec_from_file_location("h", os.path.join(os.getcwd(), "dev/audit/harnesses/r10_cop_gate_top.py"))
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
cmod, dt_util = h.cmod, h.dt_util
seen = []
async def rec(hass, optimizer, inputs):
    seen.append(float(optimizer.model.params.max_electrical_power))
    return await h._inline(hass, optimizer, inputs)
for label, n in (("no store", 0), ("store 12 @ 0.5 (learned)", 12)):
    dt_util.freeze(h.RIG_NOW)
    c = h._rig("probe_" + str(n), h.FLOW, False)
    hub_max = float(cmod._ctx_of(c)._thermal_params.max_electrical_power)
    if n:
        c._accuracy.draw = h.store([0.5 * hub_max] * n, dt_util.now().timestamp() - 60.0)
    seen.clear()
    with mock.patch.object(cmod, "_await_optimize", rec):
        asyncio.run(c.async_run_optimization())
        live = list(seen); seen.clear()
        out = asyncio.run(c.async_simulate({"target_temp": 21.5}))
        sim = list(seen)
    print(f"whatif: {label:26s} hub {hub_max} live solve max {live} what-if solve max {sim} "
          f"error {out.get('error') if isinstance(out, dict) else None}")
    dt_util.freeze(None)
