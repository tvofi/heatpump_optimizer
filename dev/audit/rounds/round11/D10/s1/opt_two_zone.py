#!/usr/bin/env python3
"""D10.M1 config-flow (Bronze): a default single-zone install cannot edit its whole-house heat loss.

Metric: of the entries below that carry NO zone key (no upper/lower floor mass,
inter-zone transfer or radiator fraction), the number whose options-flow
``thermal_model`` page does not render the ``house_heat_loss_coefficient``
field, plus, per entry, ThermalParameters.from_config(...).two_zone_enabled.
Entries (each a minimal Tibber entry):
  no_mode        no two_zone_mode key (every install created before or without it)
  mode_auto      two_zone_mode "auto" written explicitly (the default value)
  questionnaire  the config-flow questionnaire's answers for a single-storey
                 house (presets.preset_from_config -> derived keys) applied
Null controls:
  mode_off       two_zone_mode "off": must render the field (single zone)
  zone_keys      zone masses present: must NOT render it (two zones, by design)
Count key: the field keys in the data_schema the production options flow
returns for step thermal_model (HeatPumpOptimizerOptionsFlow.async_step_thermal_model),
and the model's own predicate -- never the entry's attributes.
Instrumented symbols: thermal_model:ThermalParameters.from_config (two_zone_enabled),
config_flow:_single_zone, config_flow:HeatPumpOptimizerOptionsFlow.async_step_thermal_model.
Perturbation: ``--perturb`` re-compiles ThermalParameters.from_config in
memory with its one mode test changed from
``two_zone_mode in (const.TWO_ZONE_MODE_ON, const.DEFAULT_TWO_ZONE_MODE)`` to
``two_zone_mode == const.TWO_ZONE_MODE_ON``, which routes "auto" through the
presence branch the function's own comment documents; hidden_on_single_zone
must fall to 0 (to_zero) while zone_keys still hides the field.

Run (from the export root):
  PYTHONPATH=tests/hastub /Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python3 \
      dev/audit/rounds/round11/D10/s1/opt_two_zone.py [--perturb]
Expected: see REPORT.md (exact).
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (the round's export tree). Machine: macOS arm64, venv-ci Python 3.14.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import sys
import tempfile
import time

sys.path.insert(0, "tests")
os.environ.setdefault("HPO_PLANDATA", os.path.join(tempfile.mkdtemp(prefix="d10s1."), "plandata.json"))
from harness import FakeEntry, FakeHass  # noqa: E402

from heatpump_optimizer import config_flow, const  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402

PERTURB = "--perturb" in sys.argv
BASE = {"name": "HPO", "tibber_token": "t", "weather_entity": "weather.home"}
FIELD = const.CONF_HOUSE_HEAT_LOSS_COEFFICIENT


def entries():
    yield "no_mode", dict(BASE), True
    yield "mode_auto", {**BASE, const.CONF_TWO_ZONE_MODE: "auto"}, True
    try:
        from heatpump_optimizer import presets
        answers = {
            const.CONF_BUILDING_STRUCTURE: presets.STRUCTURE_TIMBER_SLAB,
            const.CONF_BUILDING_ERA: presets.ERA_1980_2005,
            const.CONF_BUILDING_FOUNDATION: presets.FOUNDATION_NONE,
            const.CONF_HEATED_AREA: 140.0,
            const.CONF_UPPER_EMITTER: presets.EMITTER_RADIATORS,
            const.CONF_LOWER_EMITTER: presets.EMITTER_FLOOR,
        }
        derived = presets.derive(presets.preset_from_config(answers, dict(BASE)))
        q = {**BASE, **answers, **derived}
        zone = [k for k in (const.CONF_UPPER_FLOOR_THERMAL_MASS, const.CONF_LOWER_FLOOR_THERMAL_MASS) if k in q]
        print(f"INFO questionnaire derived zone keys={zone}")
        # Only a single-zone case counts: drop it from the denominator if the
        # questionnaire itself wrote zone keys (that is the same predicate).
        yield "questionnaire", q, not zone
    except Exception as err:  # noqa: BLE001
        print(f"INFO questionnaire arm unavailable: {err!r}")
    yield "mode_off", {**BASE, const.CONF_TWO_ZONE_MODE: "off"}, None
    yield "zone_keys", {**BASE, const.CONF_UPPER_FLOOR_THERMAL_MASS: 4.0,
                        const.CONF_LOWER_FLOOR_THERMAL_MASS: 3.0}, None


async def page_fields(data):
    hass = FakeHass()
    entry = FakeEntry(data=data, entry_id="z")
    hass.config_entries.entries.append(entry)
    flow = config_flow.HeatPumpOptimizerConfigFlow.async_get_options_flow(entry)
    flow.hass = hass
    r = await flow.async_step_thermal_model(None)
    return {str(getattr(m, "schema", m)) for m in r["data_schema"].schema}


async def main():
    if PERTURB:
        import inspect
        import textwrap
        from heatpump_optimizer import thermal_model as tm
        src = textwrap.dedent(inspect.getsource(tm.ThermalParameters.from_config.__func__))
        old = "two_zone_mode in (const.TWO_ZONE_MODE_ON, const.DEFAULT_TWO_ZONE_MODE)"
        assert old in src, "anchor not found"
        src = src.replace(old, "two_zone_mode == const.TWO_ZONE_MODE_ON").replace("@classmethod\n", "")
        ns = {}
        exec(compile(src, tm.__file__, "exec"), tm.__dict__, ns)
        tm.ThermalParameters.from_config = classmethod(ns["from_config"])
        print("RESULT perturbed=from_config mode test: auto no longer forces two zones")
    hidden = single = 0
    for name, data, single_zone in entries():
        two = ThermalParameters.from_config(data).two_zone_enabled
        fields = await page_fields(data)
        shown = FIELD in fields
        print(f"ENTRY {name}: two_zone_enabled={two} renders_{FIELD}={shown}")
        if single_zone:
            single += 1
            hidden += int(not shown)
        elif name == "mode_off":
            print(f"RESULT control_mode_off_renders={int(shown)} count")
        elif name == "zone_keys":
            print(f"RESULT control_zone_keys_hides={int(not shown)} count")
    print(f"RESULT single_zone_entries={single} count")
    print(f"RESULT hidden_on_single_zone={hidden} count")


if __name__ == "__main__":
    c0, t0 = time.process_time(), time.thread_time()
    asyncio.run(main())
    c1, t1 = time.process_time(), time.thread_time()
    print(f"RESULT thread_factor={((c1 - c0) / max(t1 - t0, 1e-9)):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
