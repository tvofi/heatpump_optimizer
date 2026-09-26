"""V3 verify of D1-s2-51: reproduce the finder's quiet-learner and arbiter fault injection on a
REAL HeatPumpOptimizerCoordinator over genuine Home Assistant 2026.2.3 (no tests/hastub), rather
than on the stub. The bug is pure Python control flow (try/except placement in coordinator.py),
so this checks it is not somehow masked or altered by the stub's DataUpdateCoordinator/executor
behaviour.

Metric: over 3 cycles per arm -- quiet arm: async_run_optimization returns 'solve_failed' although
a plan was published, when ComfortLearner.record_quiet_period raises; arbiter arm:
_async_update_data raises and N of 15 sibling steps (5 x 3 cycles) are skipped, when
pump_arbiter.apply raises.

Command (no tests/hastub on the path):
    PYTHONPATH=custom_components:tests /root/venvha/bin/python \
        tools/audit/round9/D1/verify-v3-leads/D1-s2-51_realha_cycle_fence.py
Expected: quiet_solve_failed=3 of 3 (plan published 3 of 3); arbiter_cycles_failed=3 of 3,
arbiter_skipped_steps=15 of 15 -- identical to the stub run, because the mechanism is a
try/except gap in coordinator.py with no stub dependency.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Home Assistant 2026.2.3 (venvha).
"""
import sys
sys.path.insert(0, "tools/audit/round9/D1/verify-v3-leads")
import _realha_rig as rig  # noqa: E402 (thread pin + shim inside, before numpy)
import asyncio  # noqa: E402
from heatpump_optimizer import pump_arbiter  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer.comfort_learning import ComfortLearner  # noqa: E402


async def quiet_arm():
    stops = rig.freeze_now()
    try:
        coord = await rig.abuild_coordinator(config={const.CONF_COMFORT_LEARNING_ENABLED: True})
        calls = {"n": 0}
        orig = ComfortLearner.record_quiet_period

        def boom(self, *a, **k):
            calls["n"] += 1
            raise RuntimeError("injected learner fault")
        ComfortLearner.record_quiet_period = boom
        failed = published = 0
        try:
            await coord._update_current_state()
            for _ in range(3):
                ret = await coord.async_run_optimization()
                failed += ret == "solve_failed"
                published += coord._optimization_result is not None
        finally:
            ComfortLearner.record_quiet_period = orig
        print(f"RESULT real_quiet_calls={calls['n']} count")
        print(f"RESULT real_quiet_solve_failed={failed} cycles_of_3")
        print(f"RESULT real_quiet_plan_published={published} cycles_of_3")
    finally:
        for p in stops:
            p.stop()


async def arbiter_arm():
    stops = rig.freeze_now()
    try:
        coord = await rig.abuild_coordinator()
        orig_apply = pump_arbiter.apply
        reached = {k: 0 for k in ("_command_frequency", "_async_drive_pumps", "_async_save_accuracy",
                                   "_async_save_energy_totals", "_async_watch_learning_drift")}
        for name in reached:
            real = getattr(coord, name)

            def spy(*a, _n=name, _r=real, **k):
                reached[_n] += 1
                return _r(*a, **k)
            setattr(coord, name, spy)

        async def raising(c, now=None):
            raise TypeError("injected arbiter fault (D1-s3-03 shape)")
        pump_arbiter.apply = raising
        failed = 0
        try:
            for _ in range(3):
                try:
                    await coord._async_update_data()
                except Exception:  # noqa: BLE001
                    failed += 1
        finally:
            pump_arbiter.apply = orig_apply
        skipped = sum(3 - v for v in reached.values())
        print(f"RESULT real_arbiter_cycles_failed={failed} cycles_of_3")
        print(f"RESULT real_arbiter_skipped_steps={skipped} of_15")
        print("RESULT real_arbiter_reached=" + ",".join(f"{k}:{v}" for k, v in reached.items()))
    finally:
        for p in stops:
            p.stop()


asyncio.run(quiet_arm())
asyncio.run(arbiter_arm())
rig.tail()
