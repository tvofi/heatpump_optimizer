#!/usr/bin/env python3
"""D6-s3-01: the setup wizard's device pre-fill page renders a refusal without
the description placeholders its own en.json text reads.

Metric (one line): placeholders named by en.json's config.step.device_prefill
(and the error strings the render carries) that the rendered form's
description_placeholders do not supply, per arm.
Key: the count is keyed on what the production seam delivers
(`result["description_placeholders"]` of the form
`HeatPumpOptimizerConfigFlow.async_step_device_prefill` returns), never on the
en.json text alone; an honest fix that supplies the keys moves it to 0.

Run (from the export root):
    PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D6/s3/prefill_placeholders.py [--perturb]

Expected at baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (box B3, linux):
    RESULT config_refusal_missing=2 count        (found, backup_heater_type; exact)
    RESULT config_refusal_unrenderable_units=1 count  (the description sentence holding {backup_heater_type}; exact)
    RESULT config_pick_missing=0, config_preview_missing=0         (exact)
    RESULT options_refusal_missing=0 count       (null control: the sibling options page; exact)
    RESULT config_refusal_changed_vs_preview=3   (found, backup_heater_type dropped; matched_sources
                                                  re-told as "–" for a device the preview resolved; exact)
--perturb (in memory, the fix's shape: the config refusal keeps the preview's
notes the way the options page's `_prefill` tuple does) -> config_refusal_missing=0.

Instrumented symbol:
    heatpump_optimizer.config_flow:HeatPumpOptimizerConfigFlow.async_step_device_prefill
    (its refusal branch `self._device_prefill_form(_prefill_schema(keys, saved), {}, errors)`).
A missing placeholder is user-visible: Home Assistant's frontend formats a
flow description with IntlMessageFormat and shows "Translation error: ..." in
place of the text when a variable is not provided. This harness counts the
missing keys and also tries Python's own `str.format_map` on each en.json
string of the step, the strict analogue of that render.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio  # noqa: E402
import json  # noqa: E402
import pathlib  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from unittest import mock  # noqa: E402

ROOT = pathlib.Path.cwd()
sys.path[:0] = [str(ROOT / "tests"), str(ROOT / "custom_components"), str(ROOT / "tools/devices")]

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
import gen_device_fixtures  # noqa: E402
from heatpump_optimizer import config_flow, const, device_prefill, modbus_prefill  # noqa: E402

EN = json.loads((ROOT / "custom_components/heatpump_optimizer/translations/en.json").read_text())
FIXTURE = gen_device_fixtures.load("tuya_heat_pump_000004k4z6.json")
DEVICE_ID = "dev_rotenso"
STATES = {  # the same live states tests/config_flow_steps.py seeds for this fixture
    "outdoor_ambient_temperature_t4": ("sensor", "-3.5"),
    "dhw_tank_temperature": ("sensor", "48.0"),
    "outlet_water_temperature_t1": ("sensor", "35.2"),
    "heat_exchanger_inlet_water_temperature_tin": ("sensor", "30.1"),
    "night_mode_silent": ("switch", "off"),
    "dhw_setpoint": ("number", "50"),
}
# A refusal both pages share: a hot water set-point 4 K above the shipped 45 degC
# minimum (DHW_MIN_TEMP_SETPOINT_MARGIN is 5 K) -> errors["base"] = "dhw_min_too_close".
REFUSED = {const.CONF_DHW_SETPOINT: 49.0}


def seeded_hass():
    from homeassistant.helpers import device_registry as dr
    from homeassistant.helpers import entity_registry as er
    hass = FakeHass(states={})
    dr.async_get(hass).add(DEVICE_ID, name=FIXTURE["device_name"])
    reg = er.async_get(hass)
    for row in FIXTURE["records"]:
        reg.add(row["entity_id"], unique_id=row["unique_id"], device_id=DEVICE_ID,
                platform="tuya_heat_pump", original_name=row["original_name"],
                original_device_class=row["device_class"], unit_of_measurement=row["unit"])
    slug = FIXTURE["device_name"].lower().replace(" ", "_")
    for name, (domain, value) in STATES.items():
        hass.states.set(f"{domain}.{slug}_{name}", FakeState(value))
    return hass


def strings(node):
    if isinstance(node, dict):
        for v in node.values():
            yield from strings(v)
    elif isinstance(node, str):
        yield node


def measure(kind, result):
    """(missing placeholder names, en.json strings that fail to format) for one render."""
    step = EN[kind]["step"][result["step_id"]]
    texts = list(strings(step)) + [EN[kind]["error"][e] for e in (result.get("errors") or {}).values()]
    want = {p for t in texts for p in re.findall(r"\{(\w+)\}", t)}
    given = dict(result.get("description_placeholders") or {})
    bad = 0
    for t in texts:
        try:
            t.format_map(given)
        except KeyError:
            bad += 1
    return sorted(want - set(given)), bad


async def config_arms():
    flow = config_flow.HeatPumpOptimizerConfigFlow()
    flow.hass = seeded_hass()
    pick = await flow.async_step_device_prefill(None)
    preview = await flow.async_step_device_prefill({config_flow._PREFILL_DEVICE: DEVICE_ID})
    refusal = await flow.async_step_device_prefill(dict(REFUSED))
    assert refusal.get("errors") == {"base": "dhw_min_too_close"}, refusal.get("errors")
    return pick, preview, refusal


async def options_arms():
    hass = seeded_hass()
    entry = FakeEntry(data={}, options={}, entry_id="d6s3")
    hass.config_entries.entries.append(entry)
    flow = config_flow.HeatPumpOptimizerOptionsFlow(entry)
    flow.hass = hass
    await flow.async_step_modbus_prefill(None)
    await flow.async_step_modbus_prefill({config_flow._PREFILL_DEVICE: DEVICE_ID})
    refusal = await flow.async_step_modbus_prefill(dict(REFUSED))
    assert refusal.get("errors") == {"base": "dhw_min_too_close"}, refusal.get("errors")
    return refusal


def main():
    perturb = "--perturb" in sys.argv
    t0p, t0t = time.process_time(), time.thread_time()
    real = config_flow.HeatPumpOptimizerConfigFlow._device_prefill_form

    def kept_notes(self, schema, notes, errors):
        # The fix's shape: the refusal keeps the page's read-notes, as the
        # options page's refusal does from its `_prefill` tuple.
        return real(self, schema, {**modbus_prefill.notes({}), **notes}, errors)

    ctx = (mock.patch.object(config_flow.HeatPumpOptimizerConfigFlow, "_device_prefill_form", kept_notes)
           if perturb else mock.patch.object(config_flow, "__name__", config_flow.__name__))
    with ctx:
        pick, preview, refusal = asyncio.run(config_arms())
    opt = asyncio.run(options_arms())
    for name, kind, res in (("config_pick", "config", pick), ("config_preview", "config", preview),
                            ("config_refusal", "config", refusal), ("options_refusal", "options", opt)):
        missing, bad = measure(kind, res)
        print(f"   {name}: step={res.get('step_id')} errors={res.get('errors')} missing={missing}")
        print(f"RESULT {name}_missing={len(missing)} count")
        print(f"RESULT {name}_unrenderable_units={bad} count")
    # The preview's account of the read, re-told by the refusal: keys the
    # preview supplied that the refusal drops or rewrites (a resolved device
    # re-described as "–", nothing matched).
    pv, rf = preview.get("description_placeholders") or {}, refusal.get("description_placeholders") or {}
    changed = sorted(k for k in pv if rf.get(k) != pv[k])
    print(f"   config_refusal vs preview: changed={[(k, pv[k], rf.get(k)) for k in changed]}")
    print(f"RESULT config_refusal_changed_vs_preview={len(changed)} count")
    print(f"RESULT perturbed={int(perturb)}")
    dp, dt = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={dp / dt if dt > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        swap = next(int(l.split()[1]) for l in open("/proc/vmstat") if l.startswith("pswpin"))
    except (OSError, StopIteration):
        swap = -1
    print(f"RESULT swapins={swap}")


if __name__ == "__main__":
    main()
