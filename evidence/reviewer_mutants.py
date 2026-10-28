#!/usr/bin/env python3
"""R10-SAV-COMFORT (#2492) mutation proof: each mutant applied in turn, the savings checks re-run, restored.

The checks are the "3L-G7 -- monthly savings history" section of tests/features.py (which holds
the #2255 and #2492 checks), extracted and run alone so a mutant costs a minute, not the full
script; a mutant of the coordinator's read of ``held_cost`` runs the whole of tests/features.py,
because its check (#2257's advisor degree) solves through a coordinator, and so does the duty
ledger's re-freeze (M23, in the pump-arbiter section); the card mutant (M24) regenerates
tests/plan_view.py's payload and runs tests/card.mjs. Each mutant replaces one
predicate of the fix with its pre-fix or degenerate form; a mutant no check fails is printed with
failing=0. M0 is the unmutated null run. Run it on a scratch copy of the tree: it rewrites a
production file per mutant and restores it in a `finally`.

    python3 dev/audit/harnesses/r10_sav_comfort_mutants.py <repo> [M1 M2 ...]
"""
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
PKG = ROOT / "custom_components/heatpump_optimizer"
FULL = ["tests/features.py"]
SECTION = """
import sys
sys.path.insert(0, 'tests')
from datetime import timedelta
import numpy as np
from harness import Results
from profiles import solve_inputs
R = Results('2492 section')
src = open('tests/features.py').read()
start = src.index('R.section("3L-G7 \\u2014 monthly savings history")')
end = src.index('import inspect as _sav_inspect', start)
exec(compile(src[start:end], 'features_2492', 'exec'))
sys.exit(R.close('2492'))
"""
CARD = ["-c", "import subprocess, sys; subprocess.run([sys.executable, 'tests/plan_view.py'], "
        "capture_output=True, check=True); sys.exit(subprocess.run(['node', 'tests/card.mjs']).returncode)"]
SECTION = ["-c", SECTION]
M = [
 ("X1 space path matches against the start room (room_temps[:-1])",
  "        reference_targets = _comfort_matched_targets(comfort_targets, room_temps[1:])\n        if reference_targets",
  "        reference_targets = _comfort_matched_targets(comfort_targets, room_temps[:-1])\n        if reference_targets"),
 ("X2 hot-water held_cost drops the DHW baseline",
  ")[0] + baseline_dhw)\n", ")[0])\n"),
 ("X3 calibration inverted (model over meter)",
  '        return self.line(month, "savings_actual")["kwh"] / plan_kwh\n',
  '        return plan_kwh / max(self.line(month, "savings_actual")["kwh"], 1e-9)\n', "ledger.py", SECTION),
 ("X4 shortfall is the max step shortfall, not the mean",
  "    shortfall = float(np.mean(comfort_targets - delivered))\n",
  "    shortfall = float(np.max(comfort_targets - delivered))\n"),
]
only = sys.argv[2:]
for name, old, new, *where in [("M0 unmutated", "", "")] + M:
    if only and name.split()[0] not in only:
        continue
    path = PKG / (where[0] if where else "optimizer.py")
    runner = where[1] if len(where) > 1 else FULL if where else SECTION
    orig = path.read_text()
    if old:
        assert orig.count(old) == 1, name
        path.write_text(orig.replace(old, new))
    try:
        out = subprocess.run([sys.executable, *runner], cwd=ROOT,
                             capture_output=True, text=True,
                             env={"PYTHONPATH": "tests/hastub:tests:custom_components",
                                  "PATH": f"{pathlib.Path(sys.executable).parent}:{os.environ.get('PATH', '')}"})
    finally:
        path.write_text(orig)
    fails = [l.strip() for l in out.stdout.splitlines() if l.strip().startswith("FAIL")]
    print(f"{name}: rc={out.returncode} failing={len(fails)}", flush=True)
    for l in fails:
        print(f"    {l[:150]}", flush=True)
