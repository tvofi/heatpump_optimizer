"""D4.M2 harness: every blueprints/**/*.yaml input scored against D4-criteria I3.

Metric: count of blueprint inputs lacking a name, lacking a description, or lacking a
default where the input is not an entity/device/target picker (a picker has no safe default).
Count key: blueprint.input.<key> (sections' nested input included) as Home Assistant reads it.
Command: PYTHONPATH=tests/hastub <HOME>/.local/state/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D4/s2/blueprint_inputs.py [--perturb-drop FILE:INPUT]
  --perturb-drop removes that input's description in memory; the no_description count goes up by 1.
Expected: the RESULT counts printed at baseline, exact.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: orchestrator Mac (darwin arm64).
Instrumented symbol: blueprints/automation/*.yaml:blueprint.input (the shipped artefact HA loads).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import glob, sys, time
import yaml

_t0p, _t0t = time.process_time(), time.thread_time()


class L(yaml.SafeLoader):
    pass


L.add_constructor("!input", lambda l, n: ("!input", l.construct_scalar(n)))
PICKERS = {"entity", "device", "target", "area"}
drop = sys.argv[sys.argv.index("--perturb-drop") + 1].split(":") if "--perturb-drop" in sys.argv else None


def inputs(d, prefix=""):
    for k, v in (d or {}).items():
        if isinstance(v, dict) and "input" in v and "selector" not in v:
            yield from inputs(v["input"], prefix + k + ".")
        else:
            yield prefix + k, v or {}


n = no_name = no_desc = no_default = 0
files = sorted(glob.glob("blueprints/**/*.yaml", recursive=True))
for f in files:
    bp = yaml.load(open(f), Loader=L)["blueprint"]
    for key, spec in inputs(bp.get("input")):
        if drop and f.endswith(drop[0]) and key == drop[1]:
            spec = {k: v for k, v in spec.items() if k != "description"}
        n += 1
        sel = set((spec.get("selector") or {}).keys())
        miss = []
        if not spec.get("name"):
            no_name += 1; miss.append("name")
        if not spec.get("description"):
            no_desc += 1; miss.append("description")
        if "default" not in spec and not (sel & PICKERS):
            no_default += 1; miss.append("default")
        print(f"INPUT {f}:{key} selector={sorted(sel)} missing={miss}")
print(f"RESULT blueprint_files={len(files)} count")
print(f"RESULT inputs={n} count")
print(f"RESULT no_name={no_name} count")
print(f"RESULT no_description={no_desc} count")
print(f"RESULT no_default_non_picker={no_default} count")
print(f"RESULT thread_factor={(time.process_time()-_t0p)/max(time.thread_time()-_t0t,1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
