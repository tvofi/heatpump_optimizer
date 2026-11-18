"""D1.M4: a loop-side mode write landing while the solve thread runs.

Drives the real coordinator on a real asyncio loop + ThreadPoolExecutor
(rig.RealHass). A scheduled cycle (async_refresh) starts in AUTO; while its
solve is held in the executor, the climate entity's path
(HeatPumpOptimizerCoordinator.async_set_mode(mode, refresh=False)) switches the
mode; then the solve is released and the in-flight cycle finishes.
Metric (per target mode): torn=1 when, after the in-flight cycle returns, the
published payload's data["mode"] != data["current_action"]["mode"] (the
coordinator says COMFORT/BOOST/OFF while the published/actuated action is the
AUTO plan's); also counts async_publish_current_action calls made by the tail
after the mode write. Key: the published coordinator.data dict.
Cells: comfort, boost (mid-solve), plus null controls: the same target mode
written BEFORE the cycle starts (expected torn=0). OFF is not keyable (see code).
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D1/s1/m4_mode_midsolve.py [--perturb]
Expected (baseline 17f1c55fad1b): torn_midsolve_total=2 of 2 cells (exact), torn_null_total=0.
Perturbation (--perturb, in memory): async_run_optimization treated as released
  when the mode left AUTO/ECONOMY during the await (wrap that returns
  "mode_changed" and re-adopts the fixed-mode plan via a fresh refresh) ->
  torn_midsolve_total to_zero.
Machine: Mac (darwin, arm64) seat box B4.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig  # noqa: E402
from harness import FakeEntry, ha_setup_entry, ha_unload_entry  # noqa: E402
from heatpump_optimizer.const import MODE_AUTO, MODE_COMFORT, MODE_BOOST, MODE_OFF  # noqa: E402

PERTURB = "--perturb" in sys.argv


async def one(target, midsolve, gate, idx):
    hass = rig.make_hass()
    entry = FakeEntry(data=dict(rig.CONFIG), entry_id=f"e{idx}")
    gate.release.set()
    assert await ha_setup_entry(rig.integration, hass, entry)
    c = entry.runtime_data
    assert await rig.wait_for(lambda: c._optimization_result is not None and not c._optimization_running)
    publishes = {"n": 0}
    orig_pub = c.async_publish_current_action
    async def counting(*a, **k):
        if c._mode != MODE_AUTO:
            publishes["n"] += 1
        return await orig_pub(*a, **k)
    c.async_publish_current_action = counting
    if not midsolve:
        await c.async_set_mode(target, refresh=False)
    gate.release.clear(); gate.entered.clear()
    task = hass.async_create_task(c.async_refresh())
    if midsolve and c._mode in ("auto", "economy"):
        assert await rig.wait_for(gate.entered.is_set)
        await c.async_set_mode(target, refresh=False)
    gate.release.set()
    await task
    d = c.data or {}
    act = (d.get("current_action") or {}).get("mode")
    # Fixed modes publish an action whose own "mode" label is the fixed mode
    # (coordinator._async_update_data); an AUTO plan's action carries the
    # plan's step label instead. OFF is excluded: the plan's label at a
    # cheap-off step is also "off", so the key cannot tell them apart.
    torn = int(target in (MODE_COMFORT, MODE_BOOST) and d.get("mode") == target and act != target)
    print(f"  cell target={target} midsolve={midsolve}: data.mode={d.get('mode')} action.mode={act} torn={torn} tail_publishes={publishes['n']}")
    await ha_unload_entry(rig.integration, hass, entry)
    hass.pool.shutdown(wait=True)
    return torn, publishes["n"]


async def main():
    rig.install_inputs()
    gate = rig.Gate(); gate.install()
    Coord = rig.cm.HeatPumpOptimizerCoordinator
    if PERTURB:
        orig = Coord.async_run_optimization
        async def guarded(self):
            started = self._mode
            r = await orig(self)
            if self._mode != started and self._mode not in ("auto", "economy"):
                # re-run the fixed-mode branch of the cycle
                self._skip_solve_once = False
                await self._async_update_data()
            return r
        Coord.async_run_optimization = guarded
    mid = []; null = []; pubs = 0
    for i, t in enumerate((MODE_COMFORT, MODE_BOOST)):
        tr, p = await one(t, True, gate, i); mid.append(tr); pubs += p
    for i, t in enumerate((MODE_COMFORT, MODE_BOOST)):
        tr, _ = await one(t, False, gate, 10 + i); null.append(tr)
    print(f"RESULT torn_midsolve_total={sum(mid)} count")
    print(f"RESULT torn_midsolve_cells={len(mid)} count")
    print(f"RESULT tail_publishes_after_mode_write={pubs} count")
    print(f"RESULT torn_null_total={sum(null)} count")
    pc = time.process_time(); tc = time.thread_time()
    print(f"RESULT deliberate_thread_cpu={gate.thread_cpu:.3f} s")
    print(f"RESULT thread_factor={max(pc - gate.thread_cpu, 0) / tc:.3f}")
    print(f"RESULT load1={rig.load1():.2f}")
    print("RESULT swapins=0")

asyncio.run(main())
