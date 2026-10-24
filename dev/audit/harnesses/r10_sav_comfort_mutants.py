#!/usr/bin/env python3
"""R10-SAV-COMFORT (#2492) mutation proof: each mutant applied in turn, the savings checks re-run, restored.

The checks are the "3L-G7 -- monthly savings history" section of tests/features.py (which holds
the #2255 and #2492 checks), extracted and run alone so a mutant costs a minute, not the full
script. Each mutant replaces one predicate of the fix with its pre-fix or degenerate form; a mutant
no check fails is printed with failing=0. M0 is the unmutated null run. Run it on a scratch copy
of the tree: it rewrites optimizer.py per mutant and restores it in a `finally`.

    python3 dev/audit/harnesses/r10_sav_comfort_mutants.py <repo> [M1 M2 ...]
"""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
OPT = ROOT / "custom_components/heatpump_optimizer/optimizer.py"
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
M = [
 ("M1 space path keeps the unmatched reference",
  "        if reference_targets is not comfort_targets:\n", "        if False:\n"),
 ("M2 hot-water path reference at the schedule",
  "            weather, initial_state, dt, reference_targets,\n            coil_draws=",
  "            weather, initial_state, dt, comfort_targets,\n            coil_draws="),
 ("M3 shortfall never applied", "    if not shortfall > 0.0:\n", "    if True:\n"),
 ("M4 per-step min instead of the mean shift",
  "    return comfort_targets - shortfall\n", "    return np.minimum(comfort_targets, delivered)\n"),
 ("M5 two-zone reference reads the floor the slab feeds (hot-water path)",
  "        reference_targets = _comfort_matched_targets(comfort_targets, room_temps[1:])\n        baseline_power,",
  "        reference_targets = _comfort_matched_targets(comfort_targets, lower_temps[1:])\n        baseline_power,"),
 ("M6 start debit unbounded",
  "        return max(min(capped, uncapped), -displaced)\n", "        return min(capped, uncapped)\n"),
 ("M7 the #2411 rule: only the debit past the caps bounded",
  "        return max(min(capped, uncapped), -displaced)\n",
  "        return capped - min(max(0.0, capped - uncapped), max(0.0, space_baseline_cost))\n"),
 ("M8 bound without the end credit",
  "        displaced = max(0.0, space_baseline_cost) + max(0.0, -end_cost)\n",
  "        displaced = max(0.0, space_baseline_cost)\n"),
 ("M9 an end charge widens the bound",
  "max(0.0, -end_cost)\n", "-end_cost\n"),
 ("M10 negative thermostat cost unclamped",
  "        displaced = max(0.0, space_baseline_cost) +", "        displaced = space_baseline_cost +"),
 ("M11 hot-water path hands the tank-inclusive end",
  "            self._deferred_energy_cost(\n                baseline_end, optimized_end, prices, outdoor_temps,\n                caps=space_caps, humidity=h.humidity,\n            ),\n",
  "            self._deferred_energy_cost(\n                baseline_end, optimized_end, prices, outdoor_temps,\n                caps=space_caps, humidity=h.humidity, include_dhw=True,\n            ),\n"),
 ("M12 space-path start held at the unmatched schedule",
  "            initial_state, weather, reference_targets, prices, outdoor_temps,\n            space_caps, h.humidity, baseline_cost,",
  "            initial_state, weather, comfort_targets, prices, outdoor_temps,\n            space_caps, h.humidity, baseline_cost,"),
 ("M13 a cold start credited uncapped",
  "        return max(min(capped, uncapped), -displaced)\n", "        return max(uncapped, -displaced)\n"),
]

only = sys.argv[2:]
for name, old, new in [("M0 unmutated", "", "")] + M:
    if only and name.split()[0] not in only:
        continue
    orig = OPT.read_text()
    if old:
        assert orig.count(old) == 1, name
        OPT.write_text(orig.replace(old, new))
    try:
        out = subprocess.run([sys.executable, "-c", SECTION], cwd=ROOT, capture_output=True, text=True,
                             env={"PYTHONPATH": "tests/hastub:tests:custom_components", "PATH": "/usr/bin:/bin"})
    finally:
        OPT.write_text(orig)
    fails = [l.strip() for l in out.stdout.splitlines() if l.strip().startswith("FAIL")]
    print(f"{name}: rc={out.returncode} failing={len(fails)}", flush=True)
    for l in fails:
        print(f"    {l[:150]}", flush=True)
