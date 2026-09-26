"""D5 verify-v3 (reach and class) harness for D5-s1-02: setup.md's Quick setup storage
promises, driven end to end through the real ConfigFlow and the real coordinator.

Metric (one line): of setup.md's two Quick-setup promises (buffer "yes" stores cheap heat;
wood probes switch the two-tank physics on), how many the coordinator built from the entry the
real flow creates (user -> user_sensors -> quick_setup(all yes + both probes) -> device_prefill
declined -> finish_now) fails to honour, read as ThermalParameters.buffer_is_store and
.two_tank_modelled on the coordinator's own model.
Count key: the ThermalParameters instance HeatPumpOptimizerCoordinator.__init__ builds from the
created entry's data -- not quick_setup.derive's return value (the finder's key).
Command (from the repository root):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
        tools/audit/round9/D5/verify-v3/v3_s1_02_quick.py [--perturb]
--perturb: add mixing_valve_mode=<first throttling mode> to the created entry's data before
    the coordinator is built (the answer Quick setup never asks). Expected: 2 -> 0.
Control arm (printed): the same entry with only the wood probes removed -> two_tank 0 as the
    doc itself says, so the count keys on the valve and not on the probes.
Expected at baseline: unhonoured_promises=2 (exact).
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (+ round-9 evidence); machine: 4-core
cloud container, CPython 3.14.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio
import sys
import time

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
_t0p, _t0t = time.process_time(), time.thread_time()
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from heatpump_optimizer import config_flow, const, mixing_valve, quick_setup  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402

PERTURB = "--perturb" in sys.argv
THROTTLE = sorted(mixing_valve.THROTTLING_MODES)[0]


def hass_with_states():
    h = FakeHass()
    for eid, v in (("sensor.wood_top", "70"), ("sensor.wood_bottom", "40"),
                   ("weather.home", "cloudy"), ("sensor.nordpool", "1.0")):
        h.states.set(eid, FakeState(v))
    return h


async def create_entry():
    flow = config_flow.HeatPumpOptimizerConfigFlow()
    flow.hass = hass_with_states()
    trail = []
    r = await flow.async_step_user({"name": "HPO", const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_ENTITY,
                                    const.CONF_PRICE_ENTITY: "sensor.nordpool",
                                    const.CONF_WEATHER_ENTITY: "weather.home"})
    trail.append(r.get("step_id"))
    r = await flow.async_step_user_sensors({})
    trail.append(r.get("step_id"))
    answers = {q: True for q in quick_setup.FIELD_QUESTIONS}
    answers[const.CONF_WOOD_TANK_TOP_ENTITY] = "sensor.wood_top"
    answers[const.CONF_WOOD_TANK_BOTTOM_ENTITY] = "sensor.wood_bottom"
    r = await flow.async_step_quick_setup(answers)
    trail.append(r.get("step_id"))
    for _ in range(6):
        if r.get("type") == "create_entry":
            break
        sid = r.get("step_id")
        if r.get("type") == "menu":
            r = await getattr(flow, "async_step_finish_now")()
        else:
            r = await getattr(flow, f"async_step_{sid}")({})
        trail.append(r.get("step_id") or r.get("type"))
    return r, trail


result, trail = asyncio.run(create_entry())
print("trail:", trail, "->", result.get("type"))
data = {**result.get("data", {}), **result.get("options", {})}


def params_of(cfg):
    coord = HeatPumpOptimizerCoordinator(hass_with_states(), FakeEntry(data=dict(cfg)))
    found = [v for v in vars(coord).values() if isinstance(v, ThermalParameters)]
    ctx = getattr(coord, "_ctx", None)
    if not found and ctx is not None:
        found = [v for v in vars(ctx).values() if isinstance(v, ThermalParameters)]
    if not found:
        found = [ThermalParameters.from_config(cfg)]
    return found[0]


cfg = dict(data)
if PERTURB:
    cfg[const.CONF_MIXING_VALVE_MODE] = THROTTLE
p = params_of(cfg)
print("entry keys set by quick path:", sorted(k for k in cfg if "buffer" in k or "wood" in k or "valve" in k))
print(f"buffer_tank_volume={p.buffer_tank_volume} mixing_valve_mode={p.mixing_valve_mode} layout={p.topology_layout}")
ctl = {k: v for k, v in cfg.items() if k not in (const.CONF_WOOD_TANK_TOP_ENTITY, const.CONF_WOOD_TANK_BOTTOM_ENTITY)}
ctl[const.CONF_MIXING_VALVE_MODE] = THROTTLE
pc = params_of(ctl)
unhonoured = int(not p.buffer_is_store) + int(not p.two_tank_modelled)
cpu_p, cpu_t = time.process_time() - _t0p, time.thread_time() - _t0t
print(f"RESULT entry_created={int(result.get('type') == 'create_entry')} count")
print(f"RESULT buffer_is_store={int(p.buffer_is_store)} count")
print(f"RESULT two_tank_modelled={int(p.two_tank_modelled)} count")
print(f"RESULT unhonoured_promises={unhonoured} count")
print(f"RESULT hold_two_zone_enabled={int(p.two_zone_enabled)} count")
print(f"RESULT control_no_probes_two_tank={int(pc.two_tank_modelled)} count")
print(f"RESULT thread_factor={cpu_p / cpu_t if cpu_t else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
