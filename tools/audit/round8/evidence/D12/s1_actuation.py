"""D12 s1 -- control-surface actuation routing across the heat-pump axis.

Metric: over one full coordinator cycle per control surface, the number of
actuation service calls the integration issues whose service domain cannot
route to the target entity under Home Assistant's entity-service rule (a
``<domain>.<service>`` call resolves only ``<domain>.*`` entities; the
``homeassistant`` and ``mqtt`` domains are domain-generic). Key: the
(service domain, entity_id) pairs recorded by FakeServices.async_call as
``coordinator:_apply_action`` / ``_command_frequency`` /
``_command_valve_target`` / ``_async_drive_pumps`` deliver them -- not the
config.

Each surface is mapped the way the product lets a user map it: the heat-pump
switch slot for input_boolean and climate is filled through the integration's
own ``heatpump_optimizer.assign_entity`` service (``services:handle_assign_entity``,
which validates against ``topology.ASSIGNABLE_KEYS``), then the entry is set
up again with the stored options (what the options reload does) and one cycle
runs.

Command (from tree root):
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 tools/audit/round8/D12/s1_actuation.py [--fix-arm]
Expected at baseline cdf82daa: RESULT unroutable_writes=2 calls (exact), from the
input_boolean and climate heat-pump-switch surfaces; RESULT surfaces_unactuated=2.
Null control: the switch.* surface (the only domain the config flow's picker
offers) -> 0 unroutable writes.
Perturbation (--fix-arm): the one-line production edit "switch" ->
"homeassistant" in coordinator._apply_action's async_call, applied in memory to
the source and restored in finally -> unroutable_writes to_zero.
Machine: 4-vCPU cloud Linux container (audit round 8 fan-out).
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
from datetime import timedelta

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass, FakeState, ha_setup_entry  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

import heatpump_optimizer as integration  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer import coordinator as coordinator_mod  # noqa: E402
from heatpump_optimizer.optimizer import optimize_in_process  # noqa: E402

GENERIC = {"homeassistant", "mqtt", "weather", "persistent_notification"}
NON_ACTUATION = {"weather", "persistent_notification", "heatpump_optimizer"}

BASE = {
    "name": "Home",
    const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_ENTITY,
    const.CONF_PRICE_ENTITY: "sensor.prices",
    const.CONF_WEATHER_ENTITY: "weather.home",
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    const.CONF_DHW_ENABLED: False,
}


def states(now):
    start = now.replace(minute=0, second=0, microsecond=0)
    return {
        "sensor.prices": FakeState("0.5", attributes={"raw_today": [
            {"start": (start + timedelta(hours=h)).isoformat(),
             "value": round(0.5 + 0.4 * ((h % 24) in (7, 8, 17, 18, 19)) + 0.05 * (h % 3), 3)}
            for h in range(48)]}),
        "sensor.indoor": FakeState("21.0", unit="°C"),
        "sensor.outdoor": FakeState("-2.0", unit="°C"),
        "switch.heat_pump": FakeState("on"),
        "input_boolean.heat_pump": FakeState("on"),
        "climate.heat_pump": FakeState("heat", attributes={"temperature": 21.0}),
        "number.compressor_freq": FakeState("50", attributes={"min": 20, "max": 120}),
        "number.valve": FakeState("35"),
        "sensor.valve_target": FakeState("21.0", unit="°C"),
    }


# surface name -> (config additions, assign via service?: (key, entity) or None)
SURFACES = {
    "switch (config-flow picker)": ({const.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.heat_pump"}, None),
    "input_boolean (assign_entity)": ({}, (const.CONF_HEAT_PUMP_SWITCH_ENTITY, "input_boolean.heat_pump")),
    "climate (assign_entity)": ({}, (const.CONF_HEAT_PUMP_SWITCH_ENTITY, "climate.heat_pump")),
    "number freq control": ({const.CONF_COMPRESSOR_FREQ_ENTITY: "number.compressor_freq",
                             const.CONF_FREQ_CONTROL_MODE: "control"}, None),
    "valve smart_write number": ({const.CONF_MIXING_VALVE_MODE: "smart_write",
                                  const.CONF_MIXING_VALVE_WRITE_ENTITY: "number.valve",
                                  const.CONF_MIXING_VALVE_TARGET_ENTITY: "sensor.valve_target"}, None),
    "ecl110 mqtt": ({const.CONF_ECL110_DISPLACE_SET_TOPIC: "ecl110/displace/set"}, None),
}


def _hass(now):
    hass = FakeHass(states(now))
    start = now.replace(minute=0, second=0, microsecond=0)

    async def _forecasts(call):
        return {call.data["entity_id"]: {"forecast": [
            {"datetime": (start + timedelta(hours=h)).isoformat(),
             "temperature": -4.0 + 4.0 * (h % 24) / 24.0, "wind_speed": 3.0,
             "precipitation": 0.0, "humidity": 85.0}
            for h in range(48)]}}

    hass.services.async_register("weather", "get_forecasts", _forecasts)
    return hass


async def run_surface(name, extra, assign, now):
    cfg = {**BASE, **extra}
    options = {}
    assign_ok = None
    if assign is not None:
        hass0 = _hass(now)
        e0 = FakeEntry(data=dict(cfg), entry_id="assign")
        await ha_setup_entry(integration, hass0, e0)
        try:
            await hass0.services.async_call(
                "heatpump_optimizer", "assign_entity",
                {"key": assign[0], "entity_id": assign[1]}, blocking=True)
            assign_ok = True
        except Exception as err:  # noqa: BLE001
            assign_ok = f"refused: {err}"
        options = dict(e0.options)
        await e0.runtime_data.async_shutdown()
    hass = _hass(now)
    entry = FakeEntry(data=dict(cfg), options=options, entry_id="run")
    await ha_setup_entry(integration, hass, entry)
    coord = entry.runtime_data
    n0 = len(hass.services.calls)
    await coord._async_update_data()
    calls = hass.services.calls[n0:]
    act = []
    for dom, svc, data in calls:
        if dom in NON_ACTUATION:
            continue
        eid = (data or {}).get("entity_id") or (data or {}).get("topic")
        act.append((dom, svc, eid))
    bad = [c for c in act if c[0] not in GENERIC
           and isinstance(c[2], str) and c[2].split(".", 1)[0] != c[0]]
    await coord.async_shutdown()
    return {"surface": name, "assign": assign_ok, "calls": act, "unroutable": bad,
            "plan": coord._optimization_result is not None}


def patch_fix():
    """The perturbation: route the heat-pump switch through 'homeassistant'."""
    src = textwrap.dedent(inspect.getsource(coordinator_mod.HeatPumpOptimizerCoordinator._apply_action))
    import re
    pat = re.compile(r'"switch",(\s+)"turn_on" if heat_pump_on else "turn_off",')
    assert pat.search(src), "fix-arm needle not found"
    src = pat.sub(r'"homeassistant",\1"turn_on" if heat_pump_on else "turn_off",', src, count=1)
    ns = {}
    exec(compile(src, coordinator_mod.__file__, "exec"), coordinator_mod.__dict__, ns)
    orig = coordinator_mod.HeatPumpOptimizerCoordinator._apply_action
    coordinator_mod.HeatPumpOptimizerCoordinator._apply_action = ns["_apply_action"]
    return orig


def main():
    fix = "--fix-arm" in sys.argv
    real_solve = coordinator_mod._await_optimize

    async def solve_inline(hass, optimizer, state, *positional, **keywords):
        return optimize_in_process(optimizer, state, positional, keywords)

    coordinator_mod._await_optimize = solve_inline
    now = dt_util.now().replace(minute=7, second=0, microsecond=0)
    real_now = dt_util.now
    dt_util.now = lambda *a, **k: now
    orig = patch_fix() if fix else None
    t0p, t0t = time.process_time(), time.thread_time()
    rows = []
    try:
        for name, (extra, assign) in SURFACES.items():
            row = asyncio.run(run_surface(name, extra, assign, now))
            rows.append(row)
            print(f"  {name:<32} assign={row['assign']} plan={row['plan']} "
                  f"unroutable={len(row['unroutable'])} calls={row['calls']}")
    finally:
        coordinator_mod._await_optimize = real_solve
        dt_util.now = real_now
        if orig is not None:
            coordinator_mod.HeatPumpOptimizerCoordinator._apply_action = orig
    pc, tc = time.process_time() - t0p, time.thread_time() - t0t
    null = [r for r in rows if r["surface"].startswith("switch")][0]
    print(f"RESULT arm={'fix' if fix else 'baseline'}")
    print(f"RESULT surfaces={len(rows)} surfaces")
    print(f"RESULT unroutable_writes={sum(len(r['unroutable']) for r in rows)} calls")
    print(f"RESULT surfaces_unactuated={sum(1 for r in rows if r['unroutable'])} surfaces")
    print(f"RESULT null_control_switch_unroutable={len(null['unroutable'])} calls")
    print(f"RESULT thread_factor={pc / tc if tc else float('nan'):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    with open("/proc/vmstat") as fh:
        sw = [l for l in fh if l.startswith("pswpin")]
    print(f"RESULT swapins={sw[0].split()[1] if sw else 0}")


if __name__ == "__main__":
    main()
