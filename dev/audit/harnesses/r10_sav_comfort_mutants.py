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
 ("M11 the start is handed the tank-inclusive end",
  "            caps, h.humidity, space_baseline_cost, house_end,\n",
  "            caps, h.humidity, space_baseline_cost, end,\n"),
 ("M12 space-path settlement held at the unmatched schedule",
  "            h, weather, reference_targets, baseline_end, optimized_end, baseline_cost,\n",
  "            h, weather, comfort_targets, baseline_end, optimized_end, baseline_cost,\n"),
 ("M13 a cold start credited uncapped",
  "        return max(min(capped, uncapped), -displaced)\n", "        return max(uncapped, -displaced)\n"),
 ("M14 space-path held_cost read after the matching",
  "        held_cost = float(energy_cost_of(baseline_power))\n        reference_targets = _comfort_matched_targets(comfort_targets, room_temps[1:])\n        if reference_targets is not comfort_targets:\n            baseline_power, baseline_end = self._compute_baseline_power(\n                weather, initial_state, dt, reference_targets,\n            )\n",
  "        reference_targets = _comfort_matched_targets(comfort_targets, room_temps[1:])\n        if reference_targets is not comfort_targets:\n            baseline_power, baseline_end = self._compute_baseline_power(\n                weather, initial_state, dt, reference_targets,\n            )\n        held_cost = float(energy_cost_of(baseline_power))\n"),
 ("M15 hot-water held_cost is the matched baseline_cost",
  "        held_cost = baseline_cost if reference_targets is comfort_targets else float(\n",
  "        held_cost = baseline_cost if True else float(\n"),
 ("M16 the advisor's degree reads baseline_cost again (whole features.py)",
  "                simulated.held_cost - result.held_cost, horizon_hours), 2),\n",
  "                simulated.baseline_cost - result.baseline_cost, horizon_hours), 2),\n",
  "coordinator.py"),
 # Carries 2-5 (the owner's baseline specification, card equality, the re-freeze).
 ("M17 the thermostat is never calibrated",
  "                1.0 if calibration is None else calibration\n", "                1.0\n", "ledger.py", SECTION),
 ("M18 the plan line is never booked",
  "        if calibrated and planned_kw is not None and np.isfinite(planned_kw):\n",
  "        if False:\n", "ledger.py", SECTION),
 ("M19 a month begun without the plan line gains one",
  '        calibrated = SAVINGS_PLAN_LINE in lines or "savings_baseline" not in lines\n',
  "        calibrated = True\n", "ledger.py", SECTION),
 ("M20 no calibration floor",
  "plan_kwh < MIN_CALIBRATION_KWH:\n", "plan_kwh <= 0.0:\n", "ledger.py", SECTION),
 ("M21 the row's actual is the bill again",
  '            actual_sek = self.line(key, "savings_actual")["sek"]\n',
  "            actual_sek = billed_total(self.month_summary(key))[0]\n", "ledger.py", SECTION),
 ("M22 the settlement hands the ledger no plan draw",
  '            planned_kw=pending.get("power"),\n', "            planned_kw=None,\n", "ledger.py", SECTION),
 ("M23 the duty ledger keeps the first tick's plan (whole features.py)",
  '    elif row["plan"] is not inp.plan:\n', "    elif False:\n", "pump_arbiter.py"),
 ("M24 the tab's Baseline column reads the actual (tests/card.mjs)",
  "        <td class=\"num\">${money(row.baseline_sek)}</td>\n",
  "        <td class=\"num\">${money(row.actual_sek)}</td>\n", "www/heatpump-optimizer-card.js", CARD),
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
