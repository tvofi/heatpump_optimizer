"""V2 (independent) for D1-s2-51: drive the two unfenced cycle-path seams with REAL producers of
a raise (stored state), not an injected exception.

Metric: over 4 consecutive cycles per arm, (Q) async_run_optimization calls returning
'solve_failed' while coord._optimization_result is set, when the comfort learner's last_update
was restored NAIVE through ComfortLearner.from_dict (comfort_learning.py from_dict keeps a naive
ISO stamp; _decay then subtracts it from the aware now inside record_quiet_period);
(A) _async_update_data calls that raise, and cycles on which _async_save_energy_totals and
_async_save_accuracy are not reached, when pump_duty_mode='control' and the pump-duty store holds
a 'written' record stamped NAIVE (pump_arbiter._load keeps it; hold() subtracts it from the aware
now inside pump_arbiter.apply, the first line of _apply_action).
Count key: the coordinator's own return value / raised exception and spy counts on the
production save methods. Null control: the same stored records stamped aware (--aware) -> 0.
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/verify-v2/leads_cycle_producers.py [--aware]
Expected: Q quiet_learner_raised=0, solve_failed_with_plan=0 of 4 (the naive stamp never reaches
_decay on this rig: record_quiet_period returns at its flatness gate, planned span/band > 0.25 on
every price/weather/band variant tried); A cycles_failed=4 of 4, saves_not_reached=8 of 8 (exact);
--aware -> 0, 0, 0.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: cloud box G1-V2, 4 vCPU Linux, CPython 3.14.0rc2.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import leads_rig as rig  # noqa: E402  (thread pin inside, before numpy)
import asyncio
from datetime import timedelta
from harness import FakeState
from homeassistant.helpers import storage
from heatpump_optimizer import const
from heatpump_optimizer.comfort_learning import ComfortLearner

AWARE = "--aware" in sys.argv
N = 4


def stamp(delta_h):
    t = rig.NOW + timedelta(hours=delta_h)
    return t.isoformat() if AWARE else t.replace(tzinfo=None).isoformat()


def arm_quiet():
    rig.freeze()
    storage._reset_store_disk()
    cfg = rig.config(**{const.CONF_COMFORT_LEARNING_ENABLED: True})
    hass, entry, coord = rig.coordinator(cfg)
    d = coord._comfort_learner.as_dict()
    d["last_update"] = stamp(-6)
    coord._comfort_learner = ComfortLearner.from_dict(d, coord._comfort_learner.configured_weight)
    raised = {"n": 0}
    orig = ComfortLearner.record_quiet_period

    def spy(self, *a, **k):
        try:
            return orig(self, *a, **k)
        except Exception:
            raised["n"] += 1
            raise
    ComfortLearner.record_quiet_period = spy
    failed_with_plan = 0
    try:
        async def go():
            nonlocal failed_with_plan
            await coord._update_current_state()
            for _ in range(N):
                ret = await coord.async_run_optimization()
                failed_with_plan += (ret == "solve_failed" and coord._optimization_result is not None)
        asyncio.run(go())
    finally:
        ComfortLearner.record_quiet_period = orig
    print(f"RESULT quiet_learner_raised={raised['n']} of_{N}")
    print(f"RESULT quiet_solve_failed_with_plan={failed_with_plan} cycles_of_{N}")
    print(f"RESULT quiet_solve_failures_counter={coord._solve_failures}")


def arm_arbiter():
    rig.freeze()
    storage._reset_store_disk()
    cfg = rig.config(**{const.CONF_PUMP_DUTY_MODE: "control",
                        const.CONF_DHW_SETPOINT_ENTITY: "number.dhw_sp",
                        const.CONF_DHW_TEMP_ENTITY: "sensor.tank"})
    hass = rig.hass_with(states={
        "number.dhw_sp": FakeState("50", last_updated=rig.NOW - timedelta(minutes=2), unit="°C"),
        "sensor.tank": FakeState("47.0", last_updated=rig.NOW - timedelta(minutes=2), unit="°C")})
    hass, entry, coord = rig.coordinator(cfg, hass=hass)
    storage._DISK[f"{const.DOMAIN}_{entry.entry_id}_pump_duty"] = (
        '{"written": {"dhw_setpoint": [45.0, "%s"]}}' % stamp(-2))
    reached = {"_async_save_energy_totals": 0, "_async_save_accuracy": 0}
    for name in reached:
        real = getattr(coord, name)

        async def spy(*a, _n=name, _r=real, **k):
            reached[_n] += 1
            return await _r(*a, **k)
        setattr(coord, name, spy)
    failed = 0
    errs = set()

    async def go():
        nonlocal failed
        for _ in range(N):
            try:
                await coord._async_update_data()
            except Exception as err:  # noqa: BLE001
                failed += 1
                errs.add(f"{type(err).__name__}:{str(err)[:60]}")
    asyncio.run(go())
    not_reached = sum(N - v for v in reached.values())
    print(f"RESULT arbiter_cycles_failed={failed} cycles_of_{N}")
    print(f"RESULT arbiter_saves_not_reached={not_reached} of_{2 * N}")
    print("RESULT arbiter_errors=" + ("|".join(sorted(errs)) or "none"))


arm_quiet()
arm_arbiter()
print(f"RESULT stored_stamps={'aware' if AWARE else 'naive'}")
rig.tail()
