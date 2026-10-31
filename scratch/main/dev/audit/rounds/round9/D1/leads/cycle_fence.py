"""D1-s2-51: a best-effort subsystem raise on the cycle path fails the solve / the whole cycle.

Metric: over 3 consecutive cycles per arm, count (a) async_run_optimization returns
'solve_failed' although a plan was produced and published (quiet arm: raise inside
ComfortLearner.record_quiet_period, reached via coordinator._record_quiet_comfort_period),
and (b) _async_update_data cycles that raise, plus sibling steps skipped
(_command_frequency, _async_drive_pumps, _async_save_accuracy, _async_save_energy_totals,
_async_watch_learning_drift) (arbiter arm: raise inside pump_arbiter.apply, reached via
coordinator._apply_action). Count key: the coordinator's own return value / raised
exception and spy call counts on the production methods.
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/leads/cycle_fence.py [--fence] [--no-inject]
Expected: quiet_solve_failed=3 (plan published 3, counter left at 1 because the success path
  zeroes it before the raise, so the solve_failures repair never fires); arbiter_cycles_failed=3,
  arbiter_skipped_steps=15 (exact). --fence -> 0/0; --no-inject (null control) -> 0/0.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, machine B10 cloud container (4 cores), CPython 3.14.0rc2.
The injected raise stands in for any learner/arbiter fault; D1-s3-03's non-numeric
pump_duty set-point is one real producer for the arbiter seam.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _rig  # noqa: E402  (thread pin inside, before numpy)
import asyncio
from heatpump_optimizer import const, coordinator as coord_mod, pump_arbiter
from heatpump_optimizer.comfort_learning import ComfortLearner

FENCE = "--fence" in sys.argv
INJECT = "--no-inject" not in sys.argv


def quiet_arm():
    _rig.freeze()
    cfg = _rig.base_config(**{const.CONF_COMFORT_LEARNING_ENABLED: True})
    hass, entry, coord = _rig.make_coord(cfg)
    calls = {"n": 0}
    orig = ComfortLearner.record_quiet_period

    def boom(self, *a, **k):
        calls["n"] += 1
        if INJECT:
            raise RuntimeError("injected learner fault")
        return orig(self, *a, **k)
    ComfortLearner.record_quiet_period = boom
    if FENCE:
        seam = coord._record_quiet_comfort_period

        def fenced():
            try:
                seam()
            except Exception:  # noqa: BLE001
                pass
        coord._record_quiet_comfort_period = fenced
    failed = published = 0
    try:
        async def run():
            nonlocal failed, published
            await coord._update_current_state()
            for _ in range(3):
                ret = await coord.async_run_optimization()
                failed += ret == "solve_failed"
                published += coord._optimization_result is not None
        asyncio.run(run())
    finally:
        ComfortLearner.record_quiet_period = orig
    print(f"RESULT quiet_calls={calls['n']} count")
    print(f"RESULT quiet_solve_failed={failed} cycles_of_3")
    print(f"RESULT quiet_plan_published={published} cycles_of_3")
    print(f"RESULT quiet_solve_failures_counter={coord._solve_failures} count")


def arbiter_arm():
    _rig.freeze()
    hass, entry, coord = _rig.make_coord()
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
        if INJECT:
            raise TypeError("injected arbiter fault (D1-s3-03 shape)")
        return await orig_apply(c, now)

    async def fenced(c, now=None):
        try:
            return await raising(c, now)
        except Exception:  # noqa: BLE001
            return None
    pump_arbiter.apply = fenced if FENCE else raising
    failed = 0
    try:
        async def run():
            nonlocal failed
            for _ in range(3):
                try:
                    await coord._async_update_data()
                except Exception:  # noqa: BLE001
                    failed += 1
        asyncio.run(run())
    finally:
        pump_arbiter.apply = orig_apply
    skipped = sum(3 - v for v in reached.values())
    print(f"RESULT arbiter_cycles_failed={failed} cycles_of_3")
    print(f"RESULT arbiter_skipped_steps={skipped} of_15")
    print("RESULT arbiter_reached=" + ",".join(f"{k}:{v}" for k, v in reached.items()))


quiet_arm()
arbiter_arm()
_rig.tail()
