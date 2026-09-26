"""D10-s2-01 verify-v1: preset-mode translation/icon coverage, measured from the files.

Metric: for the climate entity class climate:HeatPumpOptimizerClimate, count
  custom_presets    = preset_modes not in HA core's standard preset set
                      (none, eco, away, boost, comfort, home, sleep, activity);
  preset_paths_<f>  = JSON paths in <f> (strings.json, translations/*.json,
                      icons.json) whose path contains "preset_mode" anywhere,
                      under any key -- not only under the entity's own
                      translation_key, so a table filed under a wrong key still
                      counts as present;
  uncovered_<f>     = custom presets that appear as a leaf key under none of
                      those paths.
Count key: the class's _attr_preset_modes (the value HA reads) and the shipped
files' contents.
Perturbation: --perturb en_only adds a preset_mode table (auto, economy) to
translations/en.json in memory only. Expected: uncovered_en 2 -> 0, every other
file stays 2 (the count is per file, not a global flag).
Null control: the standard presets (comfort, boost) count 0 at baseline.

Run (repo root):
  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D10/verify-v1/preset_tables.py [--perturb en_only]
Expected +-0 (counts). Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (evidence
tree 6f51db2c). Machine: 4-core Linux cloud container, shared. Root rule: cwd.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

sys.path.insert(0, "custom_components")
from heatpump_optimizer import climate  # noqa: E402

STD = {"none", "eco", "away", "boost", "comfort", "home", "sleep", "activity"}
P = Path("custom_components/heatpump_optimizer")
files = {"strings": P / "strings.json", "icons": P / "icons.json"}
files.update({f"tr_{p.stem}": p for p in sorted((P / "translations").glob("*.json"))})
data = {k: json.loads(v.read_text()) for k, v in files.items()}
if "--perturb" in sys.argv and "en_only" in sys.argv:
    data["tr_en"].setdefault("entity", {}).setdefault("climate", {})["x"] = {
        "state_attributes": {"preset_mode": {"state": {"auto": "Auto", "economy": "Economy"}}}}

presets = list(climate.HeatPumpOptimizerClimate._attr_preset_modes)
custom = [p for p in presets if p not in STD]
tk = getattr(climate.HeatPumpOptimizerClimate, "_attr_translation_key", None)
print(f"preset_modes={presets} class_translation_key={tk!r}")
print(f"RESULT custom_presets={len(custom)} count ({','.join(custom)})")
print(f"RESULT standard_presets_control={len([p for p in presets if p in STD])} count (need no table)")


def leaves_under_preset(o, path=()):
    out = set()
    if isinstance(o, dict):
        for k, v in o.items():
            if "preset_mode" in path and not isinstance(v, dict):
                out.add(k)
            out |= leaves_under_preset(v, path + (k,))
    return out


for name, d in data.items():
    keys = leaves_under_preset(d)
    miss = [p for p in custom if p not in keys]
    print(f"RESULT preset_leaf_keys_{name}={len(keys)} count")
    print(f"RESULT uncovered_{name}={len(miss)} count ({','.join(miss)})")
tp, tt = time.process_time(), time.thread_time()
print(f"RESULT thread_factor={tp / tt if tt else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
with open("/proc/vmstat") as fh:
    print("RESULT swapins=" + next(l.split()[1] for l in fh if l.startswith("pswpin")))
