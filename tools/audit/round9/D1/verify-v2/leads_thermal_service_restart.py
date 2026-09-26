"""V2 (independent) for D1-s2-53: set_thermal_parameters through the SERVICE HANDLER, then a
restart, on my own value grid and a deeper footprint.

Metric: of the 28 SERVICE_SCHEMA_SET_THERMAL_PARAMS fields, each called alone through
services.handle_set_thermal_params (the registered handler, after the schema coerces the value)
with a value at ~75 % of the schema range (25 % where a cross-field rule refuses 75 %; booleans flipped, dhw_windows '05:30-06:30'), count the
fields whose call changed coordinator state and whose change is absent after a restart on the same
entry and store disk with every startup load landed. Footprint (mine): every int/float/str/bool
reachable at depth <= 3 from the coordinator through heatpump_optimizer objects (e.g.
_ctx._thermal_params, _ctx._opt_config, _thermal_model.params) that the call changed.
Count key: the restarted coordinator's own values at those paths.
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/verify-v2/leads_thermal_service_restart.py [--persist]
Expected: changed_fields=27 of 28, lost=25 of changed (exact; dhw_cooling_rate and buffer_cooling_rate
survive, dhw_windows leaves no scalar footprint); --persist (the call's fields also written to entry.options,
the fix shape) -> lost=0.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: cloud box G1-V2, 4 vCPU Linux, CPython 3.14.0rc2.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import leads_rig as rig  # noqa: E402  (thread pin inside)
import asyncio
from harness import FakeHass, FakeEntry, FakeServiceCall
from homeassistant.config_entries import ConfigEntryState
from homeassistant.helpers import storage
from heatpump_optimizer import const, services

PERSIST = "--persist" in sys.argv
SCHEMA = services.SERVICE_SCHEMA_SET_THERMAL_PARAMS


def pick(key, frac=0.75):
    validator = SCHEMA.schema[key]
    name = str(key)
    if name in ("dhw_schedule_enabled", "dhw_legionella_enabled"):
        return None  # flipped against the booted value below
    if name == "dhw_windows":
        return "05:30-06:30"
    rng = None
    for v in getattr(validator, "validators", []):
        if hasattr(v, "min") and hasattr(v, "max"):
            rng = (v.min if v.min is not None else 0.0, v.max)
    if rng is None:
        for v in getattr(validator, "validators", []):
            for w in getattr(v, "validators", []):
                if hasattr(w, "min") and hasattr(w, "max"):
                    rng = (w.min if w.min is not None else 0.0, w.max)
    lo, hi = rng if rng else (0.0, 10.0)
    return SCHEMA({name: lo + frac * (hi - lo)})[name]


class LoopHass(FakeHass):
    def async_create_task(self, coro):
        return asyncio.Task(coro, loop=asyncio.get_running_loop(), eager_start=True)


def walk(c, depth=3):
    """Scalars reachable from the coordinator through heatpump_optimizer objects, depth <= 3."""
    out, seen = {}, set()

    def rec(obj, path, d):
        if id(obj) in seen or d > depth:
            return
        seen.add(id(obj))
        for k, v in vars(obj).items():
            if k.startswith("_store") or k in ("_last_update_success_time",):
                continue
            if isinstance(v, (int, float, str, bool)):
                out[path + (k,)] = v
            elif (hasattr(v, "__dict__") and not isinstance(v, type)
                  and type(v).__module__.startswith("heatpump_optimizer")):
                rec(v, path + (k,), d + 1)
    rec(c, (), 1)
    return out


async def boot(options):
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
    hass = LoopHass()
    hass.states.set("sensor.room", rig.FakeState("20.6"))
    hass.states.set("sensor.out", rig.FakeState("-7.5"))
    cfg = rig.config(**{const.CONF_DHW_TANK_VOLUME: 200.0})
    entry = FakeEntry(data=cfg, options=dict(options))
    c = HeatPumpOptimizerCoordinator(hass, entry)
    rig.no_fetch(c)
    rig.series(c)

    async def _no_refresh(*a, **k):
        return None
    c.async_request_refresh = _no_refresh
    await asyncio.sleep(0.05)
    for t in list(getattr(c, "_background_tasks", ())):
        await t
    entry.state = ConfigEntryState.LOADED
    entry.runtime_data = c
    hass.config_entries.entries.append(entry)
    return hass, c


async def one(field, frac=0.75):
    storage._reset_store_disk()
    hass, a = await boot({})
    value = pick(field, frac)
    if value is None:
        value = not bool(a._thermal_params.__dict__.get(field, a._config.get(field, False)))
        value = SCHEMA({field: value})[field]
    s0 = walk(a)
    try:
        await services.handle_set_thermal_params(hass, FakeServiceCall(const.DOMAIN, "set_thermal_parameters", {field: value}))
    except services.ServiceValidationError:
        if frac == 0.75:
            return await one(field, 0.25)  # a cross-field rule refused 75 %: retry at 25 % of the range
        raise
    for t in list(getattr(a, "_background_tasks", ())):
        await t
    s1 = walk(a)
    foot = [k for k in s1 if s0.get(k) != s1[k]]
    if not foot:
        return None
    _, b = await boot({field: value} if PERSIST else {})
    s2 = walk(b)
    return all(s2.get(k) == s1[k] for k in foot)


def main():
    rig.freeze()
    fields = [str(k) for k in SCHEMA.schema]
    changed = lost = 0
    lost_names = []
    for f in fields:
        r = asyncio.run(one(f))
        if r is None:
            continue
        changed += 1
        if not r:
            lost += 1
            lost_names.append(f)
    print(f"RESULT fields={len(fields)}")
    print(f"RESULT changed_fields={changed} of_{len(fields)}")
    print(f"RESULT lost={lost} of_changed")
    print("RESULT lost_fields=" + (",".join(lost_names) or "none"))
    print(f"RESULT persisted_arm={int(PERSIST)}")


main()
rig.tail()
