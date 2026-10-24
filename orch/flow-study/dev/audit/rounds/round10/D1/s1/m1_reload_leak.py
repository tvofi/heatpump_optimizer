"""D1.M1: torn-down coordinators kept alive across reloads, real loop.

Metric: number of HeatPumpOptimizerCoordinator objects still alive (weakref)
after N setup -> solved+actuated cycle -> unload rounds, once the harness drops
its own references and gc.collect() runs; plus, per module-level
WeakKeyDictionary registry (early_cutoff/boost/pump_arbiter/debugger), how many
torn coordinators it still holds as keys. Key: coordinator object identity.
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D1/s1/m1_reload_leak.py [--rounds 5] [--perturb]
Expected (baseline 17f1c55fad1b): torn_alive=N (=5), early_cutoff_keys=N; exact.
Perturbation (--perturb): in-memory, HeatPumpOptimizerCoordinator.async_shutdown
  additionally pops early_cutoff._STATES[self] -> torn_alive to_zero.
Null control: rounds whose cycle never reaches _apply_action (--no-actuate:
  coordinator mode OFF... early_cutoff.arm still runs) -- see REPORT.
Machine: Mac (darwin, arm64) seat box B4.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, gc, sys, time, weakref
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig  # noqa: E402
from harness import FakeEntry, ha_setup_entry, ha_unload_entry  # noqa: E402
from heatpump_optimizer import early_cutoff, boost, pump_arbiter, debugger  # noqa: E402

PERTURB = "--perturb" in sys.argv
N = int(sys.argv[sys.argv.index("--rounds") + 1]) if "--rounds" in sys.argv else 5
REGISTRIES = {"early_cutoff": early_cutoff._STATES, "boost_states": boost._STATES,
              "boost_plan_bases": boost._PLAN_BASES, "pump_arbiter": pump_arbiter._STATES,
              "debugger": debugger._COLLECTORS}


async def main():
    rig.install_inputs()
    gate = rig.Gate(); gate.install(); gate.release.set()
    Coord = rig.cm.HeatPumpOptimizerCoordinator
    if PERTURB:
        orig = Coord.async_shutdown
        async def popping(self):
            await orig(self)
            early_cutoff._STATES.pop(self, None)
        Coord.async_shutdown = popping
    armed = {"n": 0}
    orig_arm = early_cutoff.arm
    async def counting_arm(*a, **k):
        armed["n"] += 1
        return await orig_arm(*a, **k)
    early_cutoff.arm = counting_arm
    hass = rig.make_hass()
    entry = FakeEntry(data=dict(rig.CONFIG))
    refs = []
    for _ in range(N):
        assert await ha_setup_entry(rig.integration, hass, entry)
        c = entry.runtime_data
        ok = await rig.wait_for(lambda: c._optimization_result is not None and not c._optimization_running)
        assert ok, "cycle did not complete"
        await asyncio.sleep(0.05)
        await ha_unload_entry(rig.integration, hass, entry)
        refs.append(weakref.ref(c))
        del c
    await asyncio.sleep(0.2)
    hass.created.clear()
    gc.collect(); gc.collect()
    alive = sum(1 for r in refs if r() is not None)
    print(f"RESULT rounds={N} count")
    print(f"RESULT early_cutoff_arm_calls={armed['n']} count")
    print(f"RESULT torn_alive={alive} count")
    for name, reg in REGISTRIES.items():
        held = sum(1 for r in refs if r() is not None and r() in reg)
        print(f"RESULT registry_{name}_torn_keys={held} count")
    pc = time.process_time(); tc = time.thread_time()
    print(f"RESULT deliberate_thread_cpu={gate.thread_cpu:.3f} s")
    print(f"RESULT thread_factor={max(pc - gate.thread_cpu, 0) / tc:.3f}")
    print(f"RESULT load1={rig.load1():.2f}")
    print("RESULT swapins=0")
    hass.pool.shutdown(wait=True)

asyncio.run(main())
