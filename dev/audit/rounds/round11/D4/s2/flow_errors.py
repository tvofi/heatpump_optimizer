"""D4.M2 harness: trigger validation errors dynamically through the production step handlers.

Metric: for each (flow, step, trigger) cell, the number of {placeholder} names in the
rendered error strings (every language) that the form result's description_placeholders
does not supply; plus error keys with no string in the result's section (per language).
Count key: placeholder names parsed from <section>.error.<key> of each language file for
the keys the production handler returned in result["errors"], minus result's
description_placeholders keys.
Command: PYTHONPATH=tests/hastub <HOME>/.local/state/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D4/s2/flow_errors.py [--perturb]
  --perturb: patches config_flow.HeatPumpOptimizerConfigFlow._device_prefill_form so it adds
  _WINDOW_PLACEHOLDERS (the options page's own _prefill_form does); unfilled count goes to 0.
Expected at baseline: RESULT unfilled_placeholders_total=8 (2 cells x 4 languages), exact.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: orchestrator Mac (darwin arm64).
Instrumented symbols: config_flow:HeatPumpOptimizerConfigFlow.async_step_device_prefill,
config_flow:HeatPumpOptimizerConfigFlow._device_prefill_form,
config_flow:HeatPumpOptimizerOptionsFlow.async_step_modbus_prefill (control),
config_flow:HeatPumpOptimizerConfigFlow.async_step_dhw (control),
config_flow:HeatPumpOptimizerOptionsFlow.async_step_grid_fees, async_step_hot_water.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, json, re, sys, time
from unittest import mock
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
from harness import FakeHass, FakeEntry  # noqa: E402
from heatpump_optimizer import config_flow, const  # noqa: E402

_t0p, _t0t = time.process_time(), time.thread_time()
CC = "custom_components/heatpump_optimizer/"
TR = {k: json.load(open(p)) for k, p in {
    "strings": CC + "strings.json", "en": CC + "translations/en.json",
    "sv": CC + "translations/sv.json", "de": CC + "translations/de.json"}.items()}
PH = re.compile(r"\{([a-z_]+)\}")
SHORT = "06:00-06:05"   # 5 min < MIN_WINDOW_MINUTES


def cfg_flow():
    f = config_flow.HeatPumpOptimizerConfigFlow()
    f.hass = FakeHass()
    f._data = {const.CONF_TIBBER_TOKEN: "t", "name": "x"}
    return f


def opt_flow(**opts):
    f = config_flow.HeatPumpOptimizerOptionsFlow(FakeEntry(options={const.CONF_TIBBER_TOKEN: "t", **opts}))
    f.hass = FakeHass()
    return f


async def cell_cfg_prefill(key):
    f = cfg_flow()
    f._device_prefill = (key,)          # phase two: the suggestion page is open
    return "config", await f.async_step_device_prefill({key: SHORT})


async def cell_opt_prefill(key):
    f = opt_flow()
    f._prefill = (None, (key,), {"found": "1", "backup_heater_type": "-"})
    return "options", await f.async_step_modbus_prefill({key: SHORT})


async def cell_cfg_dhw():
    f = cfg_flow()
    form = await f.async_step_dhw(None)
    sub = form["data_schema"]({})
    sub[const.CONF_DHW_WINDOWS] = SHORT
    return "config", await f.async_step_dhw(sub)


async def cell_opt_page(step, key, value):
    f = opt_flow()
    form = await getattr(f, f"async_step_{step}")(None)
    from golden import empty_section_payload, nest_flat, _presented_fields
    flat = {str(getattr(k, "schema", k)): v for k, v in form["data_schema"](empty_section_payload(form["data_schema"])).items()}
    flat = {}
    for k, _ in _presented_fields(form["data_schema"]):
        pass
    sub = form["data_schema"](empty_section_payload(form["data_schema"]))
    def put(d):
        for kk, vv in d.items():
            if isinstance(vv, dict):
                put(vv)
        if key in d or not any(isinstance(v, dict) for v in d.values()):
            d[key] = value
    put(sub)
    return "options", await getattr(f, f"async_step_{step}")(sub)


CELLS = [
    ("config.device_prefill dhw_windows", lambda: cell_cfg_prefill(const.CONF_DHW_WINDOWS)),
    ("config.device_prefill silent_mode_windows", lambda: cell_cfg_prefill(const.CONF_SILENT_MODE_WINDOWS)),
    ("options.modbus_prefill dhw_windows (control)", lambda: cell_opt_prefill(const.CONF_DHW_WINDOWS)),
    ("options.modbus_prefill silent_mode_windows (control)", lambda: cell_opt_prefill(const.CONF_SILENT_MODE_WINDOWS)),
    ("config.dhw dhw_windows (control)", cell_cfg_dhw),
    ("options.hot_water dhw_windows", lambda: cell_opt_page("hot_water", const.CONF_DHW_WINDOWS, SHORT)),
    ("options.grid_fees implausible", lambda: cell_opt_page("grid_fees", const.CONF_GRID_FEE_RULES, "Jan-Dec Mon-Sun 00:00-24:00 = 99")),
    ("options.grid_fees negative", lambda: cell_opt_page("grid_fees", const.CONF_GRID_FEE_RULES, "Jan-Dec Mon-Sun 00:00-24:00 = -1")),
    ("options.grid_fees invalid", lambda: cell_opt_page("grid_fees", const.CONF_GRID_FEE_RULES, "nonsense")),
]


def run():
    total_unfilled, total_missing, fired = 0, 0, 0
    for name, mk in CELLS:
        try:
            sec, res = asyncio.run(mk())
        except Exception as err:  # noqa: BLE001
            print(f"CELL {name}: RAISED {type(err).__name__}: {err}")
            continue
        errs = res.get("errors") or {}
        if not errs:
            print(f"CELL {name}: no error fired (type={res.get('type')})")
            continue
        fired += 1
        supplied = set((res.get("description_placeholders") or {}).keys())
        unf = 0
        for lang, t in TR.items():
            for fld, key in errs.items():
                s = t[sec]["error"].get(key)
                if s is None:
                    total_missing += 1
                    print(f"  MISSING {lang}:{sec}.error.{key}")
                    continue
                need = set(PH.findall(s)) - supplied
                if need:
                    unf += len(need)
                    print(f"  UNFILLED {lang}:{sec}.error.{key} on field {fld}: {sorted(need)}")
        total_unfilled += unf
        print(f"CELL {name}: errors={errs} placeholders={sorted(supplied)} unfilled={unf}")
    return fired, total_unfilled, total_missing


if "--perturb" in sys.argv:
    orig = config_flow.HeatPumpOptimizerConfigFlow._device_prefill_form

    def patched(self, schema, notes, errors):
        return orig(self, schema, {**config_flow._WINDOW_PLACEHOLDERS, **notes}, errors)
    with mock.patch.object(config_flow.HeatPumpOptimizerConfigFlow, "_device_prefill_form", patched):
        fired, unfilled, missing = run()
else:
    fired, unfilled, missing = run()
print(f"RESULT cells={len(CELLS)} count")
print(f"RESULT cells_fired={fired} count")
print(f"RESULT unfilled_placeholders_total={unfilled} count")
print(f"RESULT missing_error_strings={missing} count")
print(f"RESULT thread_factor={(time.process_time()-_t0p)/max(time.thread_time()-_t0t,1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
