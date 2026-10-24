import os, sys, json, inspect, textwrap
root = sys.argv[1]
os.chdir(root)
for part in ("custom_components", os.path.join("tests", "hastub"), "tests"):
    sys.path.insert(0, os.path.join(root, part))
sys.argv = [sys.argv[0]]
import stress
from heatpump_optimizer import optimizer as _opt
PACKAGE = os.path.dirname(os.path.abspath(_opt.__file__))
combos = [dict(season="winter", two_zone=False, dhw=False, pin_off_steps=(90,), label="winter/1z/space/pin-off"),
          dict(season="summer", two_zone=True, dhw=True, pin_off_steps=(90,), label="summer/2z/dhw/pin-off")]
for combo in combos:
    label = combo.pop("label")
    run, files = stress.production_calls(lambda: stress.build_case(**combo), PACKAGE)
    print("RESULT", label, "calls", sum(files.values()), "evals", int(run["solver_evals"]),
          "simulate", int(run.get("solver_simulate_steps") or 0), "objective", float(run["result"].objective_value),
          json.dumps({k: v for k, v in sorted(files.items()) if k in ("thermal_model.py", "optimizer.py")}))
