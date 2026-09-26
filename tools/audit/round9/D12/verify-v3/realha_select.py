"""D12 verify-v3 (round 9): real-Home-Assistant reachability for D12-s2-02 and
D12-s2-01 -- no tests/hastub on the path.

Metrics (one line each):
  s2-02: mode_writes_not_applied = number of the three mode-slot domains the
         config flow accepts (select, input_select, sensor) on which the
         production seam pump_arbiter._write, run against a REAL hass with the
         real `select` and `input_select` integrations loaded, leaves the target
         state unchanged after one write of a different option. The null
         control is the select cell (must apply).
  s2-01: onoff_min_eq_max_accepted = 1 when the REAL OptionsFlowManager saves
         the thermal_model page with heat_pump_min_power == heat_pump_max_power
         (6.0 kW) without an error, 0 otherwise; and the production
         _power_to_heat_pump_schedule on that saved config marks a 1.2 kW plan
         step off (RESULT onoff_1p2kW_step_on).
Perturbation --perturb: pump_arbiter._write's hard-coded service domain is
routed by the target's own domain (in memory); input_select must then apply
(mode_writes_not_applied 2 -> 1; the sensor cell stays unapplied, it has no
select_option service at all).

Run:  PYTHONPATH=<numpy/scipy dir> /home/claude/havenv/bin/python tools/audit/round9/D12/verify-v3/realha_select.py [--perturb]
Expected: baseline mode_writes_not_applied=2 (input_select, sensor), --perturb 1; onoff accepted 1, 1.2 kW step on=False. Exact.
Baseline SHA: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (+ round-9 evidence 6f51db2c).
Machine: G2-V3 cloud container, 4 vCPU, CPython 3.14.0rc2, HA core 2026.2.3.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import abc as _abc
import typing as _typing

# Environment shim (see realha_flows.py): mashumaro 3.22 vs CPython 3.14.
if not hasattr(_typing, "ByteString"):
    class _ByteString(_abc.ABC):
        pass
    for _t in (bytes, bytearray, memoryview):
        _ByteString.register(_t)
    _typing.ByteString = _ByteString

import asyncio  # noqa: E402
import logging  # noqa: E402
import shutil  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402
from datetime import datetime, timezone  # noqa: E402
from types import SimpleNamespace  # noqa: E402

REPO = os.getcwd()
assert "hastub" not in os.environ.get("PYTHONPATH", ""), "run WITHOUT tests/hastub"

import homeassistant  # noqa: E402
from homeassistant import config_entries, core, loader  # noqa: E402
from homeassistant.const import __version__ as HA_VERSION  # noqa: E402
from homeassistant.helpers import device_registry as dr  # noqa: E402
from homeassistant.helpers import entity_registry as er  # noqa: E402
from homeassistant.helpers import issue_registry as ir  # noqa: E402
from homeassistant.setup import async_setup_component  # noqa: E402

assert "hastub" not in homeassistant.__file__
logging.basicConfig(level=logging.ERROR)
PERTURB = "--perturb" in sys.argv
OPTIONS = ["Heating", "DHW only", "Heating + DHW"]


async def make_hass(tmp):
    hass = core.HomeAssistant(tmp)
    hass.config.skip_pip = True
    await hass.config.async_set_time_zone("Europe/Stockholm")
    loader.async_setup(hass)
    await dr.async_load(hass)
    await er.async_load(hass)
    await ir.async_load(hass)
    hass.config_entries = config_entries.ConfigEntries(hass, {})
    await hass.config_entries.async_initialize()
    hass.set_state(core.CoreState.running)
    hass.config.components.add("http")  # shim: a flow never touches the web server
    return hass


async def main():
    tmp = tempfile.mkdtemp(prefix="realha_d12s_")
    os.symlink(os.path.join(REPO, "custom_components"), os.path.join(tmp, "custom_components"))
    sys.path.insert(0, tmp)
    from custom_components.heatpump_optimizer import config_flow, optimizer, pump_arbiter, thermal_model  # noqa: E402

    hass = await make_hass(tmp)
    assert await async_setup_component(hass, "input_select", {"input_select": {
        "pump_mode": {"options": OPTIONS, "initial": "Heating + DHW"}}})
    # the real select integration, with one real select entity via the demo-free template? No platform
    # is needed for the routing question: the component and its entity service exist once it loads.
    assert await async_setup_component(hass, "select", {})
    await hass.async_block_till_done()
    # a real select entity: a minimal SelectEntity added through the real EntityComponent
    from homeassistant.components.select import DOMAIN as SELECT_DOMAIN, SelectEntity  # noqa: E402
    from homeassistant.helpers.entity_component import EntityComponent  # noqa: E402

    class _Sel(SelectEntity):
        _attr_options = OPTIONS
        _attr_current_option = "Heating + DHW"
        _attr_name = "pump_mode"
        entity_id = "select.pump_mode"

        async def async_select_option(self, option):
            self._attr_current_option = option
            self.async_write_ha_state()

    comp: EntityComponent = hass.data["entity_components"][SELECT_DOMAIN] if "entity_components" in hass.data else hass.data[SELECT_DOMAIN]
    await comp.async_add_entities([_Sel()])
    hass.states.async_set("sensor.pump_mode", "Heating + DHW", {"options": OPTIONS, "device_class": "enum"})
    await hass.async_block_till_done()

    if PERTURB:
        import inspect
        src = inspect.getsource(pump_arbiter._write).replace('"select",\n', 'entity.split(".", 1)[0],\n', 1)
        ns = {}
        exec(compile(src, pump_arbiter.__file__, "exec"), pump_arbiter.__dict__, ns)
        pump_arbiter._write = ns["_write"]

    not_applied = 0
    now = datetime(2026, 1, 15, 10, 0, tzinfo=timezone.utc)
    for ent in ("select.pump_mode", "input_select.pump_mode", "sensor.pump_mode"):
        before = hass.states.get(ent).state
        coord = SimpleNamespace(hass=hass, _config={"heat_pump_mode_entity": ent})
        held = pump_arbiter.ArbiterState() if hasattr(pump_arbiter, "ArbiterState") else None
        orig = (pump_arbiter.state_for, pump_arbiter._persist)
        pump_arbiter.state_for = lambda c, _h=held: _h
        async def _nop(c):
            return None
        pump_arbiter._persist = _nop
        err = None
        try:
            await pump_arbiter._write(coord, "mode", "DHW", now)
        except Exception as exc:  # noqa: BLE001
            err = repr(exc)
        finally:
            pump_arbiter.state_for, pump_arbiter._persist = orig
        await hass.async_block_till_done()
        after = hass.states.get(ent).state
        applied = after != before
        recorded = bool(held and held.written.get("mode"))
        not_applied += int(not applied)
        print(f"CELL {ent}: before={before!r} after={after!r} applied={applied} arbiter_recorded_write={recorded} raised={err}")
        print(f"RESULT {ent.split('.')[0]}_applied={int(applied)} flag")
    print(f"RESULT mode_writes_not_applied={not_applied} count")
    print(f"RESULT service_select_select_option_exists={int(hass.services.has_service('select', 'select_option'))} flag")
    print(f"RESULT service_input_select_select_option_exists={int(hass.services.has_service('input_select', 'select_option'))} flag")
    print(f"RESULT service_sensor_select_option_exists={int(hass.services.has_service('sensor', 'select_option'))} flag")

    # s2-01: min == max through the real options flow
    config_flow.async_get_clientsession = lambda hass, verify_ssl=True: None
    entry = config_entries.ConfigEntry(
        data={"name": "HPO", "tibber_token": "t", "weather_entity": "weather.home"},
        domain="heatpump_optimizer", minor_version=1, options={}, source="user", title="HPO",
        unique_id=None, version=1, discovery_keys={}, subentries_data=None)
    await hass.config_entries.async_add(entry)
    await hass.async_block_till_done()
    mgr = hass.config_entries.options
    res = await mgr.async_init(entry.entry_id)
    for step in ("advanced", "thermal_model"):
        if res["type"] == "menu":
            res = await mgr.async_configure(res["flow_id"], {"next_step_id": step})
    import voluptuous_serialize
    from homeassistant.helpers import config_validation as cv
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from realha_flows import initial_data  # noqa: E402  (the frontend's initial-data rule)
    posted = initial_data(voluptuous_serialize.convert(res["data_schema"], custom_serializer=cv.custom_serializer))

    def put(d):
        for k, v in d.items():
            if isinstance(v, dict):
                put(v)
        if "heat_pump_min_power" in d or "heat_pump_max_power" in d:
            d["heat_pump_min_power"] = 6.0
            d["heat_pump_max_power"] = 6.0
            return True
        return any(put(v) for v in d.values() if isinstance(v, dict))
    placed = put(posted)
    if not placed and any(f["name"] == "heat_pump_max_power" for f in voluptuous_serialize.convert(res["data_schema"], custom_serializer=cv.custom_serializer)):
        posted.update({"heat_pump_min_power": 6.0, "heat_pump_max_power": 6.0})
        placed = True
    if not placed:
        # sections: put them into the section that holds the key in the serialised schema
        for f in voluptuous_serialize.convert(res["data_schema"], custom_serializer=cv.custom_serializer):
            if f.get("type") == "expandable" and any(s["name"] == "heat_pump_max_power" for s in f["schema"]):
                posted.setdefault(f["name"], {}).update({"heat_pump_min_power": 6.0, "heat_pump_max_power": 6.0})
    res2 = await mgr.async_configure(res["flow_id"], posted)
    errs = res2.get("errors") or {}
    saved = {**entry.data, **entry.options}
    accepted = int(not errs and saved.get("heat_pump_min_power") == 6.0 and saved.get("heat_pump_max_power") == 6.0)
    print(f"CELL onoff: errors={errs} saved_min={saved.get('heat_pump_min_power')} saved_max={saved.get('heat_pump_max_power')} next={res2['type']}")
    print(f"RESULT onoff_min_eq_max_accepted={accepted} flag")
    if res2["type"] in ("menu", "form"):
        mgr.async_abort(res2["flow_id"])
    params = thermal_model.ThermalParameters.from_config(saved)
    opt = optimizer.HeatPumpOptimizer(thermal_model.ThermalModel(params), optimizer.OptimizationConfig())
    import numpy as np
    on = opt._power_to_heat_pump_schedule(np.array([1.2, 6.0, 0.0]))
    print(f"CELL onoff schedule for [1.2, 6.0, 0.0] kW: {on}")
    print(f"RESULT onoff_1p2kW_step_on={int(bool(on[0]))} flag")
    print(f"RESULT ha_version={HA_VERSION}")
    await hass.async_stop(force=True)
    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    t0, tt0 = time.process_time(), time.thread_time()
    asyncio.run(main())
    pc, tc = time.process_time() - t0, time.thread_time() - tt0
    print(f"RESULT thread_factor={pc / max(tc, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")][0].split()[1]
    except Exception:  # noqa: BLE001
        sw = "na"
    print(f"RESULT swapins={sw}")
