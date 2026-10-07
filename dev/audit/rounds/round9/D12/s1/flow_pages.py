"""D12-s1: does an untouched options page invent plant on a minimal install? (D12.M2)

Metric: number of options-flow pages (steps of config_flow._OPTION_FIELDS)
whose untouched submit -- the form's own schema defaults posted back -- changes
a derived plant flag of the stored config: ThermalParameters.from_config's
dhw_enabled / two_zone_enabled / topology_layout / wood_tank_configured,
wood_fuel.wood_furnace_on, or pv_enabled. Count key: the flags derived from
the options the flow actually stored (HeatPumpOptimizerOptionsFlow._save_or_menu).
Perturbation: stub config_flow._omit_unstored_defaults to identity -> count up.

Run:  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D12/s1/flow_pages.py [--no-omit]
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: box B6 container.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio
import logging
import sys
import time

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
from harness import FakeEntry, FakeHass  # noqa: E402
from heatpump_optimizer import config_flow  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402
from heatpump_optimizer.wood_fuel import wood_furnace_on  # noqa: E402

logging.disable(logging.CRITICAL)
if "--no-omit" in sys.argv:
    config_flow._omit_unstored_defaults = lambda ui, cur: ui

BASE = {"tibber_token": "x", "weather_entity": "weather.home",
        "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor"}


def flags(cfg):
    p = ThermalParameters.from_config(cfg)
    return {"dhw": p.dhw_enabled, "two_zone": p.two_zone_enabled,
            "layout": p.topology_layout, "wood_tank": p.wood_tank_configured,
            "wood_on": wood_furnace_on(cfg), "pv": bool(cfg.get("pv_enabled"))}


def defaults_of(result):
    out = {}
    schema = result.get("data_schema")
    if schema is None:
        return out

    def walk(sch):
        for marker, value in sch.schema.items():
            inner = getattr(value, "schema", None)
            if hasattr(inner, "schema") and isinstance(getattr(inner, "schema", None), dict):
                walk(inner)
                continue
            d = getattr(marker, "default", None)
            key = str(getattr(marker, "schema", marker))
            if callable(d):
                try:
                    v = d()
                except Exception:  # noqa: BLE001
                    continue
                out[key] = v
            else:
                sv = (getattr(marker, "description", None) or {}).get("suggested_value")
                if sv is not None:
                    out[key] = sv
    walk(schema)
    return out


async def one(step):
    hass = FakeHass()
    entry = FakeEntry(data=dict(BASE))
    flow = config_flow.HeatPumpOptimizerOptionsFlow(entry)
    flow.hass = hass
    handler = getattr(flow, f"async_step_{step}", None)
    if handler is None:
        return None, "no handler"
    form = await handler(None)
    if form.get("type") != "form" and str(form.get("type")) != "FlowResultType.FORM":
        return None, f"not a form: {form.get('type')}"
    posted = defaults_of(form)
    before = flags({**entry.data, **entry.options})
    try:
        await handler(posted)
    except Exception as e:  # noqa: BLE001
        return None, f"submit raised {type(e).__name__}: {e}"
    after = flags({**entry.data, **entry.options})
    return {k: (before[k], after[k]) for k in before if before[k] != after[k]}, None


def main():
    t0, tt0 = time.process_time(), time.thread_time()
    steps = list(dict.fromkeys(r.step for r in config_flow._OPTION_FIELDS if r.step))
    changed, skipped = 0, 0
    for step in steps:
        diff, why = asyncio.run(one(step))
        if why:
            skipped += 1
            print(f"skip {step}: {why}")
            continue
        if diff:
            changed += 1
            print(f"INVENTS {step}: {diff}")
        else:
            print(f"ok {step}")
    print(f"RESULT option_pages={len(steps)} count")
    print(f"RESULT pages_skipped={skipped} count")
    print(f"RESULT pages_inventing_plant={changed} count")
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
