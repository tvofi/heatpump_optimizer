"""D12 verify-v2 for D12-s2-02: the pump-duty mode write's service domain against the slot's domain.

Metric (two parts, count keys named):
 (a) accepted_control_domains: of the mode-slot domains topology.ASSIGNABLE_KEYS
     lists for heat_pump_mode_entity, how many the options page entities_pump
     saves (no form errors) together with pump_duty_mode = "control". Key: the
     options flow's own result (errors / stored options).
 (b) misrouted: one call of the production pump_arbiter._write(coord, "mode",
     <desired>, now) per domain on a real HeatPumpOptimizerCoordinator; count
     the hass.services.async_call calls whose service domain differs from the
     target entity's domain (Home Assistant resolves an entity service only
     against its own domain's entities). Key: FakeServices.calls.

Perturbation --route: pump_arbiter._write's service-domain literal replaced in
memory by the target's own domain (source edit + exec of the one function),
expected misrouted for input_select -> 0.

Run:  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D12/verify-v2/v2_mode_write.py [--route]
Expected: accepted_control_domains = 3 of 3; misrouted = 2 (input_select, sensor) of 3; --route: input_select 0.
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: G2-V2 cloud container, 4 vCPU, CPython 3.14.0rc2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import inspect
import logging
import sys
import textwrap
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from v2_flowlib import post_untouched  # noqa: E402
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import config_flow as cf, const, topology  # noqa: E402
from heatpump_optimizer import pump_arbiter as pa  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from golden import START  # noqa: E402

logging.disable(logging.CRITICAL)
DOMAINS = list(topology.ASSIGNABLE_KEYS[const.CONF_HEAT_PUMP_MODE_ENTITY])
OPTIONS = ["Heating", "Hot water", "Standby"]

if "--route" in sys.argv:
    src = textwrap.dedent(inspect.getsource(pa._write))
    assert src.count('"select",\n') == 1
    src = src.replace('"select",\n', 'entity.split(".", 1)[0],\n', 1)
    ns = {}
    exec(compile(src, pa.__file__, "exec"), pa.__dict__, ns)
    pa._write = ns["_write"]


def state_of(domain):
    attrs = {"options": OPTIONS}
    if domain == "sensor":
        attrs["device_class"] = "enum"
    return FakeState("Heating", attributes=attrs)


async def accepted(domain):
    ent = f"{domain}.pump_mode"
    entry = FakeEntry(data={"tibber_token": "x", "weather_entity": "weather.home"})
    flow = cf.HeatPumpOptimizerOptionsFlow(entry)
    flow.hass = FakeHass({ent: state_of(domain)})
    form = await flow.async_step_entities_pump(None)
    post = post_untouched(form)
    flat = cf._flatten_section_input(post)
    flat[const.CONF_HEAT_PUMP_MODE_ENTITY] = ent
    flat[const.CONF_PUMP_DUTY_MODE] = "control"
    r = await flow.async_step_entities_pump(flat)
    stored = {**entry.data, **entry.options}
    ok = (not r.get("errors")) and stored.get(const.CONF_PUMP_DUTY_MODE) == "control" \
        and stored.get(const.CONF_HEAT_PUMP_MODE_ENTITY) == ent
    return ok, r.get("errors")


def misrouted(domain):
    ent = f"{domain}.pump_mode"
    cfg = {"tibber_token": "x", "weather_entity": "weather.home",
           const.CONF_HEAT_PUMP_MODE_ENTITY: ent, const.CONF_PUMP_DUTY_MODE: "control"}
    hass = FakeHass({ent: state_of(domain)})
    coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=cfg))
    st = hass.states.get(ent)
    desired = next(k for k in sorted(set(filter(None, (pa.pump_mode.resolve(o) for o in OPTIONS))))
                   if pa._option_for(st, k) != "Heating")
    n0 = len(hass.services.calls)
    dt_util.freeze(START)
    try:
        asyncio.run(pa._write(coord, "mode", desired, START))
    finally:
        dt_util.freeze(None)
    calls = [c for c in hass.services.calls[n0:] if (c[2] or {}).get("entity_id") == ent]
    bad = sum(1 for d, _s, _data in calls if d != domain)
    return len(calls), bad, desired


def main():
    t0, tt0 = time.process_time(), time.thread_time()
    acc = 0
    mis_domains = 0
    for d in DOMAINS:
        ok, errs = asyncio.run(accepted(d))
        acc += ok
        n, bad, desired = misrouted(d)
        mis_domains += bad > 0
        print(f"DOMAIN {d}: control_saved={ok} errors={errs} mode_write_calls={n} misrouted={bad} desired={desired}")
        print(f"RESULT {d}_misrouted_mode_writes={bad} of {n} calls")
    print(f"RESULT accepted_control_domains={acc} of {len(DOMAINS)}")
    print(f"RESULT domains_with_misrouted_write={mis_domains} of {len(DOMAINS)}")
    pc, tc = time.process_time() - t0, time.thread_time() - tt0
    print(f"RESULT thread_factor={pc / max(tc, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [ln for ln in open('/proc/vmstat') if ln.startswith('pswpin')][0].split()[1]
    except Exception:  # noqa: BLE001
        sw = "na"
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
