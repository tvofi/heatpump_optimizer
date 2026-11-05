#!/usr/bin/env python3
"""R10-CI-SLIM card C2: grade one recorded push window with a tree's ci_ratchet and ci_budgets.json.

    python3 dev/audit/harnesses/r10_ci_slim/c2_replay.py TREE RUNS.json

TREE is a checkout (this one, or a merge-base worktree for the control); RUNS.json a
`--gather-runs` listing (dev/audit/harnesses/r10_hotfix_ci_critpath_4/runs.json). Prints the
critical_path_minutes and script_runs_per_push lines and the GREW count for the recorded window, a
planted +10 critical-path growth, and a planted +1 script-run growth.
"""
from pathlib import Path
tree = Path(sys.argv[1]); runs = Path(sys.argv[2])
sys.path.insert(0, str(tree / "tests"))
import importlib.util
spec = importlib.util.spec_from_file_location("cr", tree / "tests" / "ci_ratchet.py"); cr = importlib.util.module_from_spec(spec); spec.loader.exec_module(cr)
budgets = json.loads((tree / "tests" / "ci_budgets.json").read_text())
cp = cr.critical_path_minutes(runs)
derived = {k: v for k, v in budgets.items() if k not in cr.METADATA_KEYS and not k.endswith("_band")}
for label, d in (("recorded window", {**derived, "critical_path_minutes": cp}),
                 ("planted cp growth +10", {**derived, "critical_path_minutes": cp + 10}),
                 ("planted counter growth (script_runs_per_push +1)", {**derived, "critical_path_minutes": cp,
                  "script_runs_per_push": derived["script_runs_per_push"] + 1})):
    lines, grew = cr.compare(budgets, d)
    print(f"{tree.name} {label}: grew={grew}; " + "; ".join(l.strip() for l in lines if "critical_path" in l or "script_runs_per_push" in l))
