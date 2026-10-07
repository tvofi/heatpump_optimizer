"""D4-s2 harness: number fields whose own default sits off the field's step grid.

Metric (one line): over every NumberSelector the real config and options flows
render (initial flow at defaults; options flow at defaults and after the
building questionnaire's derived values are stored), the number of fields whose
rendered value Chromium's native <input type=number min max step> reports as
validity.stepMismatch -- plus, per field, the value one spinner click (stepUp) lands on.

Count key: the (min, max, step, value) the production selector config and marker
DELIVER (``selector.config`` and the voluptuous default / ``suggested_value``),
measured by the browser's own step algorithm (step base = min). Inference
boundary: there is no Home Assistant frontend here; that HA's number selector in
box mode forwards min/max/step to a native number input (ha-textfield) is inferred,
not measured.

Command (from the export root; Playwright from tests/pwlane's lock):
    npm ci --prefix "$TMPDIR/pw" (after copying tests/pwlane/package*.json there)
    NODE_PATH=$TMPDIR/pw/node_modules PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers \
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=tests/hastub \
      /home/claude/venv314/bin/python tools/audit/round9/D4/s2/step_grid.py [--perturb]
    --perturb  one-line production edit, applied in memory to config_flow.py's source:
               in ``_number``, ``"step": step,`` -> ``"step": step if slider else "any",``
               (a box field takes any value) -> off_grid_fields goes to 0.

Expected at baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (tolerance exact, counts):
    RESULT off_grid_defaults=8 (fields at their shipped default), RESULT off_grid_derived=4 (questionnaire defaults derived and stored)
    null control: RESULT off_grid_slider_fields=0 (slider fields, whose min is on their grid);
    RESULT out_of_range_values=0
Machine: B9 cloud container (4 cores, Linux, Chromium 1194 headless); counts are contention-immune.
"""
from __future__ import annotations

import os

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import asyncio
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass  # noqa: E402

import golden  # noqa: E402
import heatpump_optimizer  # noqa: E402,F401
from heatpump_optimizer import const  # noqa: E402

_P0 = time.process_time()
_T0 = time.thread_time()
PERTURB = "--perturb" in sys.argv
SRC = pathlib.Path("custom_components/heatpump_optimizer/config_flow.py")

if PERTURB:
    text = SRC.read_text()
    old = '        "step": step,\n'
    assert text.count(old) == 1, "perturbation anchor moved"
    text = text.replace(old, '        "step": step if slider else "any",\n')
    spec = importlib.util.spec_from_loader("heatpump_optimizer.config_flow", loader=None)
    cf = importlib.util.module_from_spec(spec)
    cf.__file__ = str(SRC)
    cf.__package__ = "heatpump_optimizer"
    sys.modules["heatpump_optimizer.config_flow"] = cf
    exec(compile(text, str(SRC), "exec"), cf.__dict__)
else:
    from heatpump_optimizer import config_flow as cf  # noqa: E402


def _walk(schema):
    for key, value in (schema.schema.items() if schema else []):
        inner = golden._nested_schema(value)
        if inner is not None:
            yield from _walk(inner)
        else:
            yield key, value


def _value(key):
    try:
        return key.default()
    except Exception:
        return (getattr(key, "description", None) or {}).get("suggested_value")


def _collect(arm, flow_name, step, result, into):
    for key, value in _walk(result.get("data_schema")):
        if type(value).__name__ != "NumberSelector":
            continue
        cfg = dict(value.config)
        val = _value(key)
        if val is None or cfg.get("min") is None:
            continue
        into.append({
            "arm": arm, "page": f"{flow_name}.{step}", "key": str(getattr(key, "schema", key)),
            "min": cfg["min"], "max": cfg.get("max"), "step": cfg.get("step", 1),
            "mode": str(cfg.get("mode")), "value": val,
        })


fields: list[dict] = []
DATA = {"tibber_token": "x", "weather_entity": "weather.home"}

init = cf.HeatPumpOptimizerConfigFlow()
init.hass = FakeHass()
for step in ("user", "user_sensors", "quick_setup", "temperature", "building_describe",
             "building_extras", "thermal", "zones", "dhw", "weather_sensitivity"):
    _collect("defaults", "config", step, asyncio.run(getattr(init, f"async_step_{step}")()), fields)

flow = cf.HeatPumpOptimizerOptionsFlow(FakeEntry(data=DATA, options={const.CONF_WOOD_FURNACE_ENABLED: True}))
flow.hass = FakeHass()
for step in cf.HeatPumpOptimizerOptionsFlow._MENU_LABELS:
    _collect("defaults", "options", step, asyncio.run(getattr(flow, f"async_step_{step}")()), fields)

# The derived arm: the questionnaire's shipped defaults, derived by the production
# helper and stored, as the building page's save does; the expert pages then show them.
answers = {
    const.CONF_BUILDING_STRUCTURE: "timber_slab", const.CONF_BUILDING_ERA: "1980_2005",
    const.CONF_BUILDING_FOUNDATION: "none", const.CONF_HEATED_AREA: 140.0,
    const.CONF_UPPER_EMITTER: "radiators", const.CONF_LOWER_EMITTER: "floor",
}
derived = cf._derive_preset(answers, {})
dflow = cf.HeatPumpOptimizerOptionsFlow(FakeEntry(data=DATA, options=dict(derived)))
dflow.hass = FakeHass()
for step in ("thermal_model", "thermal_model_zones"):
    got: list[dict] = []
    _collect("derived", "options", step, asyncio.run(getattr(dflow, f"async_step_{step}")()), got)
    fields.extend(r for r in got if r["key"] in derived)

tmp = pathlib.Path(tempfile.mkdtemp(prefix="d4s2-step-"))
(tmp / "in.json").write_text(json.dumps(fields, default=str))
env = {**os.environ}
env.setdefault("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")
subprocess.run(
    ["node", "tools/audit/round9/D4/s2/step_grid.mjs", str(tmp / "in.json"), str(tmp / "out.json")],
    check=True, env=env,
)
measured = json.loads((tmp / "out.json").read_text())

seen = set()
by_arm: dict[str, int] = {"defaults": 0, "derived": 0}
slider_bad = 0
box_total = slider_total = 0
for row in measured:
    ident = (row["arm"], row["key"], row["value"])
    if ident in seen:
        continue
    seen.add(ident)
    is_slider = "slider" in row["mode"].lower()
    slider_total += is_slider
    box_total += not is_slider
    if row["stepMismatch"]:
        by_arm[row["arm"]] += 1
        slider_bad += is_slider
        print(f"#   {row['arm']:8} {row['page']}.{row['key']}: value={row['value']} "
              f"min={row['min']} step={row['step']} -> one spinner click gives {row['afterStepUp']}")
print(f"# distinct fields measured: box={box_total} slider={slider_total} perturb={PERTURB}")
print(f"RESULT off_grid_defaults={by_arm['defaults']} count")
print(f"RESULT off_grid_derived={by_arm['derived']} count")
print(f"RESULT off_grid_slider_fields={slider_bad} count")
print(f"RESULT out_of_range_values={sum(1 for r in measured if not (r['min'] <= r['value'] <= (r['max'] if r['max'] is not None else float('inf'))))} count")

_p, _t = time.process_time() - _P0, time.thread_time() - _T0
print(f"RESULT thread_factor={(_p / _t) if _t > 0 else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    _swap = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")]
    print(f"RESULT swapins={_swap[0].split()[1] if _swap else 0}")
except OSError:
    print("RESULT swapins=0")
