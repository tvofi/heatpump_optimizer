"""D12 verify-v3 (round 9): the config- and options-flow seams of D12-s1-02 and
D12-s3-01, driven through REAL Home Assistant core, not tests/hastub.

Metric (one line): per seam, whether the entry's effective config after an
untouched submit through the real FlowManager / OptionsFlowManager makes
thermal_model._dhw_enabled_from_config True (and, for the wizard, whether
ThermalParameters.from_config gives two_zone_enabled True) on a path where no
answer affirmed that plant. RESULT seams_inventing=<n> of the seams driven.

"Untouched submit" is built the way the real frontend builds it: the step's
data_schema is serialised with voluptuous_serialize + cv.custom_serializer
(what HA's flow HTTP view sends), and the initial form data is computed from
that serialisation as the frontend's computeInitialHaFormData does
(suggested_value, else default; sections recurse; required booleans false).
The real FlowManager then applies data_schema(user_input) itself.

Seams:
  opt_hot_water         options menu init > hot_water, untouched, over a no-DHW entry
  opt_hot_water_tank    options init > advanced > hot_water_tank, untouched
  opt_comfort           options init > comfort, untouched (null control: no plant key)
  cfg_wizard_thermal    initial flow user > user_sensors > (menu) temperature ... thermal > zones > dhw > ... (s3's path 6)
  cfg_finish_now        initial flow user > user_sensors > finish_now (null control)
Perturbation (--perturb): thermal_model._dhw_enabled_from_config honours only
an explicit dhw_enabled (patched in memory); every DHW seam must go to 0.

Run:  PYTHONPATH=<numpy/scipy dir> /home/claude/havenv/bin/python tools/audit/round9/D12/verify-v3/realha_flows.py [--perturb]
      (no tests/hastub on the path: homeassistant is the real 2026.2.3 package in /home/claude/havenv;
       numpy/scipy/threadpoolctl are linked from /home/claude/venv into a scratch dir.)
Expected (baseline): opt_hot_water, opt_hot_water_tank, cfg_wizard_thermal invent (3), controls do not;
--perturb: DHW inventions 0 (the wizard keeps two_zone). Exact.
Baseline SHA: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (+ round-9 evidence, 6f51db2c).
Machine: G2-V3 cloud container, 4 vCPU, CPython 3.14.0rc2, HA core 2026.2.3.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import logging
import shutil
import sys
import tempfile
import time

REPO = os.getcwd()
assert "hastub" not in os.environ.get("PYTHONPATH", ""), "run WITHOUT tests/hastub"

# Environment shim, not a production change: mashumaro 3.22 (a real-HA
# dependency in /home/claude/havenv) still calls issubclass(x, typing.ByteString),
# which CPython 3.14 removed; without this HA core does not import at all here.
import abc as _abc  # noqa: E402
import typing as _typing  # noqa: E402
if not hasattr(_typing, "ByteString"):
    class _ByteString(_abc.ABC):
        pass
    for _t in (bytes, bytearray, memoryview):
        _ByteString.register(_t)
    _typing.ByteString = _ByteString

import homeassistant  # noqa: E402
from homeassistant import config_entries, core, loader  # noqa: E402
from homeassistant.const import __version__ as HA_VERSION  # noqa: E402
from homeassistant.helpers import config_validation as cv  # noqa: E402
from homeassistant.helpers import device_registry as dr  # noqa: E402
from homeassistant.helpers import entity_registry as er  # noqa: E402
from homeassistant.helpers import issue_registry as ir  # noqa: E402
import voluptuous_serialize  # noqa: E402

assert "hastub" not in homeassistant.__file__, homeassistant.__file__
logging.basicConfig(level=logging.ERROR)
PERTURB = "--perturb" in sys.argv
DOMAIN = "heatpump_optimizer"


def initial_data(serialised):
    """The frontend's computeInitialHaFormData over a serialised schema."""
    data = {}
    for field in serialised:
        name = field["name"]
        desc = field.get("description") or {}
        if desc.get("suggested_value") is not None:
            data[name] = desc["suggested_value"]
        elif "default" in field:
            data[name] = field["default"]
        elif field.get("type") == "expandable":
            data[name] = initial_data(field["schema"])
        elif not field.get("required"):
            continue
        elif field.get("type") == "boolean":
            data[name] = False
        elif field.get("type") == "string":
            data[name] = ""
        elif field.get("type") == "integer":
            data[name] = field.get("valueMin", 0)
        elif field.get("type") == "select":
            opts = field.get("options") or []
            if opts:
                o = opts[0]
                data[name] = o[0] if isinstance(o, (list, tuple)) else o
        elif "selector" in field:
            sel = field["selector"]
            if "boolean" in sel:
                data[name] = False
            elif "text" in sel:
                data[name] = ""
            elif "number" in sel:
                data[name] = sel["number"].get("min", 0)
    return data


def untouched(result, overrides=None):
    schema = result.get("data_schema")
    if schema is None:
        return {}
    ser = voluptuous_serialize.convert(schema, custom_serializer=cv.custom_serializer)
    data = initial_data(ser)
    data.update(overrides or {})
    return data


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
    # Environment shim: the manifest's 'http' dependency needs hass.auth and a
    # web server, neither of which a flow touches; mark it loaded so the real
    # FlowManager proceeds. Every flow/schema/validation step below is real HA.
    hass.config.components.add("http")
    return hass


class _OK:
    class _Resp:
        status = 200

        async def json(self):
            return {"data": {"viewer": {"name": "Home"}}}

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return False

    def post(self, *a, **k):
        return self._Resp()


REQUIRED = {"name": "Heat Pump Optimizer", "tibber_token": "tok", "weather_entity": "weather.home"}


async def drive_config(hass, menu_choices):
    """Initial flow through the REAL flow manager; menus take menu_choices in order."""
    mgr = hass.config_entries.flow
    res = await mgr.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    trail = []
    choices = list(menu_choices)
    for _ in range(40):
        t = res["type"]
        if t == "create_entry":
            return res, trail
        if t == "abort":
            raise RuntimeError(f"abort {res.get('reason')} after {trail}")
        if t == "menu":
            step = choices.pop(0)
            trail.append(step)
            res = await mgr.async_configure(res["flow_id"], {"next_step_id": step})
            continue
        step = res["step_id"]
        trail.append(step)
        ov = dict(REQUIRED) if step == "user" else {}
        res = await mgr.async_configure(res["flow_id"], untouched(res, ov))
        if res.get("errors"):
            raise RuntimeError(f"errors {res['errors']} at {step}")
    raise RuntimeError(f"flow did not finish: {trail}")


async def drive_options(hass, entry, menu_path, page):
    mgr = hass.config_entries.options
    res = await mgr.async_init(entry.entry_id)
    for step in menu_path:
        assert res["type"] == "menu", res
        res = await mgr.async_configure(res["flow_id"], {"next_step_id": step})
    assert res["type"] == "form" and res["step_id"] == page, (res["type"], res.get("step_id"))
    posted = untouched(res)
    res = await mgr.async_configure(res["flow_id"], posted)
    # leave the flow: after_save may return a menu; close it
    if res["type"] in ("menu", "form"):
        mgr.async_abort(res["flow_id"])
    return {**entry.data, **entry.options}


async def main():
    tmp = tempfile.mkdtemp(prefix="realha_d12_")
    os.symlink(os.path.join(REPO, "custom_components"), os.path.join(tmp, "custom_components"))
    sys.path.insert(0, tmp)
    # the same module objects HA's loader imports (custom_components.<domain>)
    from custom_components.heatpump_optimizer import config_flow, const, thermal_model  # noqa: E402

    if PERTURB:
        thermal_model._dhw_enabled_from_config = lambda c: bool(c.get(const.CONF_DHW_ENABLED, False))
    config_flow.async_get_clientsession = lambda hass, verify_ssl=True: _OK()
    hass = await make_hass(tmp)

    def flags(cfg):
        p = thermal_model.ThermalParameters.from_config(cfg)
        return bool(thermal_model._dhw_enabled_from_config(cfg)), bool(p.two_zone_enabled)

    out = {}
    # the wizard paths first (one entry at a time: the flow aborts already_configured)
    for seam, menus in (("cfg_wizard_thermal", ["temperature", "thermal"]),
                        ("cfg_wizard_describe", ["temperature", "building_describe"])):
        try:
            r2, t2 = await drive_config(hass, list(menus))
            e2 = r2["result"]
            out[seam] = (t2, flags({**e2.data, **e2.options}), sorted(k for k in e2.data if k.startswith("dhw") or "zone" in k))
            await hass.config_entries.async_remove(e2.entry_id)
        except Exception as exc:  # noqa: BLE001
            out[seam] = (["ERROR", repr(exc)[:300]], (None, None), [])

    # the entry "Finish setup now" creates, through the real flow
    res, trail = await drive_config(hass, ["finish_now"])
    entry = res["result"]
    out["cfg_finish_now"] = (trail, flags({**entry.data, **entry.options}), sorted(k for k in entry.data if k.startswith("dhw")))

    # options seams over the no-DHW entry; a fresh copy of the entry per seam
    for seam, path, page in (
        ("opt_comfort", ["comfort"], "comfort"),
        ("opt_hot_water", ["hot_water"], "hot_water"),
        ("opt_hot_water_tank", ["advanced", "hot_water_tank"], "hot_water_tank"),
    ):
        hass.config_entries.async_update_entry(entry, options={})
        before = flags({**entry.data, **entry.options})
        try:
            cfg = await drive_options(hass, entry, path, page)
            out[seam] = (path, flags(cfg), sorted(k for k in entry.options if k.startswith("dhw")), before)
        except Exception as exc:  # noqa: BLE001
            out[seam] = (["ERROR", repr(exc)[:300]], (None, None), [], before)

    inventing = 0
    for seam, rec in out.items():
        trail, (dhw, tz), keys = rec[0], rec[1], rec[2]
        control = seam in ("cfg_finish_now", "opt_comfort")
        inv = []
        if dhw:
            inv.append("dhw")
        if tz and seam.startswith("cfg_"):
            inv.append("two_zone")
        if inv and not control:
            inventing += 1
        print(f"SEAM {seam}: trail={' > '.join(map(str, trail))} dhw_enabled={dhw} two_zone={tz} stored_plant_keys={keys} invents={inv or '-'}")
        print(f"RESULT {seam}_invents={int(bool(inv))} flag")
    print(f"RESULT ha_version={HA_VERSION}")
    print(f"RESULT seams_inventing={inventing} count")
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
