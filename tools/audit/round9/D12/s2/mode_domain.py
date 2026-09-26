"""D12-s2 (round 9, D12.M3): the pump-duty arbiter writes the operating mode
with ``select.select_option`` whatever domain the mode slot holds, while the
slot accepts ``select``, ``input_select`` and ``sensor``
(``topology.ASSIGNABLE_KEYS["heat_pump_mode_entity"]``, the config flow's
picker and ``assign_entity``). On an ``input_select`` the write reaches no
entity, the mode never changes, and the arbiter raises its "pump does not hold
a write" repair against a pump that was never written.

Metric (one line): misrouted_mode_writes = mode-slot service calls issued by
``pump_arbiter.apply`` whose service domain differs from the target entity's
domain (a call Home Assistant resolves against no entity), over 9 arbitration
ticks, 7 minutes apart, across a 4-step plan (space, space, DHW, space), per mode-slot domain.
Consequence metrics: ticks_mode_wrong = arbitration ticks at which
the mode entity does not show the arbiter's desired mode; repair_raised = the
``pump_write_ignored`` issue was created.

Count key: the calls the production seam ``pump_arbiter._write`` hands to
``hass.services.async_call`` (FakeServices.calls) -- not the configured domain.
The harness models Home Assistant's routing explicitly (the P11 caution): it
registers ``select.select_option`` acting only on ``select.*`` targets and
``input_select.select_option`` acting only on ``input_select.*`` targets, as
core does for entity services; there is no ``sensor.select_option``.

Cells (mode-slot domain): select (null control), input_select, sensor
(device_class enum, carrying ``options``). All three are accepted by the slot.
Driven through a real ``HeatPumpOptimizerCoordinator`` over ``tests/harness``.

Perturbation (--perturb): a one-line production edit applied in memory: in
``pump_arbiter._write`` the literal ``"select",`` service domain becomes
``entity.split(".", 1)[0],`` (route by the target's own domain, as
``coordinator._on_off_service`` already does for the switch slot, #1526).
Expected: input_select misrouted_mode_writes 5 -> 0 and ticks_mode_wrong 9 -> 0 (DOWN); the sensor cell keeps ticks_mode_wrong=9 (a read-only slot is not fixed by routing: its property half is "control must not write a read-only slot").

Run:   PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D12/s2/mode_domain.py [--perturb]
Expected (baseline): RESULT select_misrouted_mode_writes=0, input_select_misrouted_mode_writes=5 (+-1),
       input_select_ticks_mode_wrong=9, input_select_repair_raised=1, sensor the same, failing_mode_domains=2
Baseline SHA: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1
Machine: box B7 cloud container, Linux 6.18, 4 vCPU; counts only.
Root rule: run from the repository root; relative tests/ and custom_components/.
"""
import os

for _threads in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_threads, "1")

import argparse
import asyncio
import inspect
import sys
import tempfile
import textwrap
import time
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

T0 = datetime(2026, 1, 10, 6, 0, tzinfo=timezone.utc)
OPTIONS = ["Heating", "DHW (Hot Water)", "Heating + DHW", "Cooling", "Cooling + DHW"]


class ServiceNotFound(Exception):
    pass


def _install_ha_routing(hass):
    """Home Assistant's entity-service routing, stated rather than assumed."""
    from harness import FakeServices

    services = hass.services

    def _selector(domain):
        async def _handler(call):
            for eid in [call.data.get("entity_id")] if isinstance(call.data.get("entity_id"), str) else call.data.get("entity_id", []):
                if eid.split(".", 1)[0] != domain:
                    continue  # core: an entity service targets its own domain only
                st = hass.states.get(eid)
                if st is not None and call.data.get("option") in (st.attributes or {}).get("options", []):
                    st.state = call.data["option"]
        return _handler

    async def _number(call):
        st = hass.states.get(call.data.get("entity_id"))
        if st is not None:
            st.state = str(call.data.get("value"))

    services.async_register("select", "select_option", _selector("select"))
    services.async_register("input_select", "select_option", _selector("input_select"))
    services.async_register("number", "set_value", _number)

    orig = services.async_call

    async def _call(domain, service, data=None, **kw):
        if service not in services._registry.get(domain, {}):
            services.calls.append((domain, service, data))
            raise ServiceNotFound(f"{domain}.{service}")
        return await orig(domain, service, data, **kw)

    services.async_call = _call


def _perturb(pa):
    src = inspect.getsource(pa._write)
    edited = src.replace('"select",\n', 'entity.split(".", 1)[0],\n', 1)
    assert edited != src, "perturbation anchor not found"
    ns = dict(pa.__dict__)
    exec(textwrap.dedent(edited), ns)
    pa._write = ns["_write"]


def run_cell(domain, perturb):
    from harness import FakeEntry, FakeHass, FakeState
    from heatpump_optimizer import pump_arbiter as pa
    from heatpump_optimizer import pump_mode
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator

    mode_eid = f"{domain}.pump_mode"
    attrs = {"options": list(OPTIONS)}
    if domain == "sensor":
        attrs["device_class"] = "enum"
    states = {
        mode_eid: FakeState("Heating + DHW", attributes=attrs),
        "number.dhw_set": FakeState("53", attributes={"min": 40, "max": 63}),
        "number.water_set": FakeState("35", attributes={"min": 25, "max": 63}),
    }
    cfg = {
        "tibber_token": "x",
        "weather_entity": "weather.home",
        "pump_duty_mode": "control",
        "heat_pump_mode_entity": mode_eid,
        "dhw_setpoint_entity": "number.dhw_set",
        "space_setpoint_entity": "number.water_set",
        "space_setpoint_unit": "flow",
        "heat_pump_min_power": 1.0,
    }
    hass = FakeHass(states)
    _install_ha_routing(hass)
    coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=cfg, entry_id=f"md_{domain}_{int(perturb)}"))
    coord._mode = "auto"
    coord._current_action = {"mode": "eco"}
    duties = "ssds"
    coord._optimization_result = SimpleNamespace(
        timestamps=[T0 + timedelta(minutes=15 * i) for i in range(len(duties))],
        power_schedule=[2.0 if c == "s" else 0.0 for c in duties],
        dhw_power_schedule=[2.0 if c == "d" else 0.0 for c in duties],
        optimal_setpoints=[21.0 for _ in duties],
    )
    created = []
    orig_issue = pa.setpoint_check.create_issue

    def _spy(hass_, domain_, issue_id, **kw):
        created.append(issue_id)
        return orig_issue(hass_, domain_, issue_id, **kw)

    pa.setpoint_check.create_issue = _spy
    misrouted = wrong = 0
    try:
        for minute in range(0, 60, 7):  # 9 ticks, 7 min apart: past ECHO_GRACE_S
            now = T0 + timedelta(minutes=minute, seconds=5)
            before = len(hass.services.calls)
            asyncio.run(pa.apply(coord, now))
            for d, svc, data in hass.services.calls[before:]:
                eid = (data or {}).get("entity_id")
                if eid == mode_eid and d != eid.split(".", 1)[0]:
                    misrouted += 1
            want = pa.desired(coord, pa.step_duty(coord._optimization_result, now, pa._on_kw(coord)), now).mode
            shown = pump_mode.resolve(hass.states.get(mode_eid).state)
            if want is not None and shown != want:
                wrong += 1
    finally:
        pa.setpoint_check.create_issue = orig_issue
        pa.release_listeners(coord)
    return misrouted, wrong, int(pa.ISSUE_IGNORED in created)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", action="store_true")
    args = ap.parse_args()
    tmp = tempfile.mkdtemp(prefix="d12s2_md_")
    os.environ.setdefault("HPO_PLANDATA", tmp)
    from heatpump_optimizer import pump_arbiter as pa

    if args.perturb:
        _perturb(pa)
    t0p, t0t = time.process_time(), time.thread_time()
    fails = 0
    for domain in ("select", "input_select", "sensor"):
        misrouted, wrong, repair = run_cell(domain, args.perturb)
        fails += bool(misrouted or wrong)
        print(f"RESULT {domain}_misrouted_mode_writes={misrouted} calls")
        print(f"RESULT {domain}_ticks_mode_wrong={wrong} ticks")
        print(f"RESULT {domain}_repair_raised={repair} flag")
    print(f"RESULT failing_mode_domains={fails} cells")
    proc, thr = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={proc / max(thr, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    swap = 0
    try:
        with open("/proc/vmstat") as fh:
            for line in fh:
                if line.startswith("pswpin "):
                    swap = int(line.split()[1])
    except OSError:
        pass
    print(f"RESULT swapins={swap}")


if __name__ == "__main__":
    main()
