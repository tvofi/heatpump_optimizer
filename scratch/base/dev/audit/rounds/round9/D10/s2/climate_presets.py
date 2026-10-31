#!/usr/bin/env python3
"""D10.M1 entity-translations / icon-translations (Gold): climate preset modes.

Metric: number of preset modes the climate entity publishes (keyed on the
entity's own preset_modes, the value HA reads) that are neither one of Home
Assistant's standard climate presets (translated and iconed by the climate
component itself) nor translated/iconed by this integration under
entity.climate.<translation_key>.state_attributes.preset_mode.state in
strings.json / translations/<lang>.json / icons.json.

Command (from the export root):
  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D10/s2/climate_presets.py [--perturb eco|translate]
Expected at baseline: untranslated_presets_en=2, untranslated_presets_sv=2,
uniconed_presets=2 (exact).  Perturbation --perturb eco (preset "economy"
renamed to HA's standard "eco" in memory) -> 1 (down); --perturb translate
(a translation_key plus an in-memory preset_mode state table carrying the two
custom presets) -> 0 (to_zero).
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: 4-CPU Linux cloud container.
Instrumented symbol: heatpump_optimizer.climate:HeatPumpOptimizerClimate
(preset_modes / translation_key as built by climate.async_setup_entry).
HA's standard preset set is homeassistant/components/climate/const.py PRESET_*
(none, eco, away, boost, comfort, home, sleep, activity), which is exactly the
key set of core's climate/strings.json entity_component._.state_attributes.
preset_mode.state (fetched 2026-09-26 from home-assistant/core dev).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse, asyncio, json, sys, tempfile, time
from pathlib import Path
from unittest import mock

os.environ.setdefault("HPO_PLANDATA", str(Path(tempfile.mkdtemp()) / "plandata.json"))
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
ap = argparse.ArgumentParser(); ap.add_argument("--perturb", default="", choices=("", "eco", "translate"))
args = ap.parse_args()

import golden  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
import heatpump_optimizer.coordinator as cm  # noqa: E402
from heatpump_optimizer import climate  # noqa: E402

HA_STANDARD = {"none", "eco", "away", "boost", "comfort", "home", "sleep", "activity"}
P = Path("custom_components/heatpump_optimizer")
langs = {"strings": json.loads((P / "strings.json").read_text()),
         "en": json.loads((P / "translations/en.json").read_text()),
         "sv": json.loads((P / "translations/sv.json").read_text())}
icons = json.loads((P / "icons.json").read_text())

made = []
_orig = cm.HeatPumpOptimizerCoordinator.__init__
def _init(self, *a, **k):
    _orig(self, *a, **k); made.append(self)
cm.HeatPumpOptimizerCoordinator.__init__ = _init
dt_util.freeze(golden.START)
golden._capture_coordinator(golden.coordinator_scenarios()["coord_all_features"])
coord = made[0]
entry = coord.entry
entry.runtime_data = coord

patches = []
if args.perturb == "eco":
    patches.append(mock.patch.object(climate.HeatPumpOptimizerClimate, "_attr_preset_modes",
                                     [("eco" if p == "economy" else p) for p in climate.HeatPumpOptimizerClimate._attr_preset_modes]))
if args.perturb == "translate":
    patches.append(mock.patch.object(climate.HeatPumpOptimizerClimate, "_attr_translation_key", "optimizer", create=True))
    table = {"state_attributes": {"preset_mode": {"state": {"auto": "Auto", "economy": "Economy"}}}}
    for d in langs.values():
        d.setdefault("entity", {}).setdefault("climate", {})["optimizer"] = table
    icons.setdefault("entity", {}).setdefault("climate", {})["optimizer"] = {"state_attributes": {"preset_mode": {"state": {"auto": "mdi:auto-mode", "economy": "mdi:leaf"}}}}
for p in patches:
    p.start()

added = []
asyncio.run(climate.async_setup_entry(coord.hass, entry, lambda es, *a, **k: added.extend(es)))
ent = [e for e in added if isinstance(e, climate.HeatPumpOptimizerClimate)][0]
presets = list(getattr(ent, "preset_modes", None) or ent._attr_preset_modes)
tk = getattr(ent, "_attr_translation_key", None)
print(f"preset_modes={presets} translation_key={tk!r} has_entity_name={getattr(ent, '_attr_has_entity_name', None)} name={getattr(ent, '_attr_name', 'unset')!r}")

def table_for(d):
    if tk is None:
        return {}
    return d.get("entity", {}).get("climate", {}).get(tk, {}).get("state_attributes", {}).get("preset_mode", {}).get("state", {})

custom = [p for p in presets if p not in HA_STANDARD]
for lang in ("strings", "en", "sv"):
    miss = [p for p in custom if p not in table_for(langs[lang])]
    print(f"RESULT untranslated_presets_{lang}={len(miss)} count ({','.join(miss)})")
unic = [p for p in custom if p not in table_for(icons)]
print(f"RESULT uniconed_presets={len(unic)} count ({','.join(unic)})")
# Where it shows: driving the mode to economy publishes that raw token as preset_mode.
coord._mode = "economy"
try:
    shown = ent.preset_mode
except Exception as e:  # pragma: no cover
    shown = f"ERR {e}"
print(f"RESULT preset_mode_when_economy={shown!r} (raw token the frontend must render)")
print(f"RESULT thread_factor={time.process_time()/max(time.thread_time(),1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print(f"RESULT swapins={[l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]}")
