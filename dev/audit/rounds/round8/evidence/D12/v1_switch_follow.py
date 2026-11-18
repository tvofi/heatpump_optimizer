"""D12 v1 -- does the heat-pump switch entity FOLLOW the plan, per accepted domain?

Metric (v1, one line): over every domain topology.ASSIGNABLE_KEYS accepts for
heat_pump_switch_entity, times both initial entity states (on / off), the number
of (domain, initial) runs in which, after one full coordinator cycle, the mapped
entity's state does not equal what the delivered action commanded
(coordinator._current_action["heat_pump_on"]), under an emulation of Home
Assistant's entity-service routing: `<d>.turn_on/turn_off` acts only on `<d>.*`
entities (HA's entity_service_call collects candidates from the domain's own
EntityComponent and logs the rest as "missing"), and `homeassistant.turn_*`
dispatches by the target entity's own domain.

Differs from the finder's s1_actuation.py: the domain set is read from
production (not hard-coded), the slot is filled directly through entry options
(not the assign_entity service), the coordinator is constructed bare (no
ha_setup_entry), and the key is the entity's resulting STATE, not the
(service-domain, entity-domain) pair of the recorded call.

Command (from tree root):
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 tools/audit/round8/D12/v1_switch_follow.py [--fix-arm]
Expected at baseline cdf82daa: RESULT not_following_runs=2 of 6 (exact) -- one
per non-switch domain (input_boolean, climate), in the run whose initial state
differs from the command; RESULT null_switch_not_following=0.
Perturbation (--fix-arm): one-line production edit in coordinator._apply_action,
service domain "switch" -> switch_entity.split(".")[0] (a DIFFERENT fix from the
finder's "homeassistant"), applied in memory, restored in finally -> to_zero.
Machine: 4-vCPU cloud Linux container (audit round 8 fan-out), seat D12-v1.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import inspect
import sys
import textwrap
import time
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

from heatpump_optimizer import const, topology  # noqa: E402
from heatpump_optimizer import coordinator as cmod  # noqa: E402
from heatpump_optimizer.optimizer import optimize_in_process  # noqa: E402

KEY = const.CONF_HEAT_PUMP_SWITCH_ENTITY
ON_STATE = {"switch": "on", "input_boolean": "on", "climate": "heat"}
NOW = datetime(2026, 1, 14, 17, 7, tzinfo=timezone.utc)  # a peak hour


def build_hass(entity_id, initial_on):
    start = NOW.replace(minute=0)
    dom = entity_id.split(".")[0]
    hass = FakeHass({
        "sensor.prices": FakeState("0.5", attributes={"raw_today": [
            {"start": (start + timedelta(hours=h)).isoformat(),
             "value": 1.3 if h < 3 else 0.3}
            for h in range(48)]}),
        "sensor.indoor": FakeState("21.0", unit="°C"),
        "sensor.outdoor": FakeState("-2.0", unit="°C"),
        entity_id: FakeState(ON_STATE[dom] if initial_on else "off"),
    })

    async def forecasts(call):
        return {call.data["entity_id"]: {"forecast": [
            {"datetime": (start + timedelta(hours=h)).isoformat(),
             "temperature": -3.0, "wind_speed": 3.0, "precipitation": 0.0,
             "humidity": 85.0} for h in range(48)]}}
    hass.services.async_register("weather", "get_forecasts", forecasts)

    # HA entity-service routing emulation.
    def setter(owner, on):
        async def handler(call):
            ids = call.data.get("entity_id")
            ids = [ids] if isinstance(ids, str) else list(ids or [])
            for eid in ids:
                d = eid.split(".")[0]
                if owner != "homeassistant" and d != owner:
                    continue  # HA: referenced entity not in this component -> "missing", no-op
                st = hass.states.get(eid)
                if st is not None:
                    st.state = ON_STATE.get(d, "on") if on else "off"
        return handler
    for owner in ("switch", "input_boolean", "climate", "homeassistant"):
        hass.services.async_register(owner, "turn_on", setter(owner, True))
        hass.services.async_register(owner, "turn_off", setter(owner, False))
    return hass


async def one(entity_id, initial_on):
    hass = build_hass(entity_id, initial_on)
    cfg = {
        "name": "Home",
        const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_ENTITY,
        const.CONF_PRICE_ENTITY: "sensor.prices",
        const.CONF_WEATHER_ENTITY: "weather.home",
        const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
        const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
        const.CONF_DHW_ENABLED: False,
    }
    entry = FakeEntry(data=cfg, options={KEY: entity_id})
    coord = cmod.HeatPumpOptimizerCoordinator(hass, entry)
    await coord._async_update_data()
    want_on = bool((coord._current_action or {}).get("heat_pump_on", False))
    got = hass.states.get(entity_id).state
    got_on = got != "off"
    calls = [(d, s, (p or {}).get("entity_id")) for d, s, p in hass.services.calls
             if s in ("turn_on", "turn_off")]
    try:
        await coord.async_shutdown()
    except Exception:  # noqa: BLE001
        pass
    return want_on, got, got_on, calls, coord._optimization_result is not None


def patch_fix():
    src = textwrap.dedent(inspect.getsource(cmod.HeatPumpOptimizerCoordinator._apply_action))
    needle = '"switch",\n'
    assert src.count(needle) == 1, "fix-arm needle"
    src = src.replace(needle, 'switch_entity.split(".")[0],\n', 1)
    ns = {}
    exec(compile(src, cmod.__file__, "exec"), cmod.__dict__, ns)
    orig = cmod.HeatPumpOptimizerCoordinator._apply_action
    cmod.HeatPumpOptimizerCoordinator._apply_action = ns["_apply_action"]
    return orig


def main():
    fix = "--fix-arm" in sys.argv
    domains = topology.ASSIGNABLE_KEYS[KEY]
    real_solve, real_now = cmod._await_optimize, dt_util.now

    async def inline(hass, optimizer, state, *a, **k):
        return optimize_in_process(optimizer, state, a, k)
    cmod._await_optimize = inline
    dt_util.now = lambda *a, **k: NOW
    orig = patch_fix() if fix else None
    t0p, t0t = time.process_time(), time.thread_time()
    bad = null_bad = runs = 0
    try:
        for dom in domains:
            for init in (True, False):
                runs += 1
                want, got, got_on, calls, plan = asyncio.run(one(f"{dom}.heat_pump", init))
                miss = want != got_on
                bad += miss
                if dom == "switch":
                    null_bad += miss
                print(f"  {dom:<14} initial={'on ' if init else 'off'} commanded_on={want} "
                      f"state_after={got:<5} follows={not miss} plan={plan} calls={calls}")
    finally:
        cmod._await_optimize, dt_util.now = real_solve, real_now
        if orig is not None:
            cmod.HeatPumpOptimizerCoordinator._apply_action = orig
    pc, tc = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT arm={'fix' if fix else 'baseline'}")
    print(f"RESULT accepted_domains={','.join(domains)}")
    print(f"RESULT not_following_runs={bad} of {runs}")
    print(f"RESULT null_switch_not_following={null_bad}")
    print(f"RESULT thread_factor={pc / tc if tc else float('nan'):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    with open("/proc/vmstat") as fh:
        sw = [l for l in fh if l.startswith("pswpin")]
    print(f"RESULT swapins={sw[0].split()[1] if sw else 0}")


if __name__ == "__main__":
    main()
