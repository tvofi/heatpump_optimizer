#!/usr/bin/env python3
"""R10-SAV-BASELINE (#2255) mutation proof: each mutant applied in turn, the #2255 checks re-run, restored.

The checks are the "3L-G7 -- monthly savings history" section of tests/features.py (which holds
the #2255 checks), extracted and run alone so a mutant costs minutes, not the full script. Each
mutant replaces one predicate of the fix with its pre-fix or degenerate form; a mutant no check
fails is printed with failing=0. M0 is the unmutated null run. Run it on a scratch copy of the
tree: it rewrites a production file per mutant and restores it in a `finally`.

Anchors are the line the fix now has, not the line it had when this proof was written: every
anchor below is unique in the tree it names, and the harness asserts that before writing. Three
mutants are retired, with the reason printed beside the run (``RETIRED``): their predicate is not
in the tree any more, so there is nothing left for them to degenerate.

    PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_baseline_mutants.py <repo> [M1 M2 ...]
"""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
PKG = ROOT / "custom_components/heatpump_optimizer"
SECTION = """
import sys
sys.path.insert(0, 'tests')
from datetime import timedelta
import numpy as np
from harness import Results
from profiles import solve_inputs
R = Results('2255 section')
src = open('tests/features.py').read()
start = src.index('R.section("3L-G7 — monthly savings history")')
end = src.index('import inspect as _sav_inspect', start)
exec(compile(src[start:end], 'features_2255', 'exec'))
sys.exit(R.close('2255'))
"""
M = [
 ("M1 baseline starts from the plan's state", "optimizer.py",
  "        state = _thermostat_held_state(self.model, initial_state, weather, targets[0])\n",
  "        state = initial_state\n"),
 ("M2 held slab without its demand term", "optimizer.py",
  "        slab_temperature=target + max(0.0, q_floor) / model.params.slab_heat_transfer_floored,", "        slab_temperature=target,"),
 ("M4 coverage factor -> calendar day", "ledger.py",
  "        return max(1.0, month_hours(now) / settled)\n", "        return pro_rata_factor(now)\n"),
 ("M5 savings priced at spot only", "ledger.py",
  "            spot=spot + fee_per_kwh,\n", "            spot=spot,\n"),
 ("M17 no plan line books, so the row never calibrates", "ledger.py",
  "        if calibrated and planned_kw is not None and np.isfinite(planned_kw):\n",
  "        if False:\n"),
 ("M7 metered energy without immersion", "ledger.py",
  'ENERGY_LINES = ("spot", "immersion")\n', 'ENERGY_LINES = ("spot",)\n'),
 ("M9 no start settlement (space path)", "optimizer.py",
  "        return end - self._start_gap_cost(\n"
  "            h.initial_state, weather, reference_targets, h.prices, h.outdoor_temps,\n"
  "            caps, h.humidity, space_baseline_cost, house_end,\n"
  "        )\n",
  "        return end\n"),
 ("M10 start debit unbounded", "optimizer.py",
  "        return max(min(capped, uncapped), -displaced)\n", "        return min(capped, uncapped)\n"),
 ("M11 start settled at the caps only", "optimizer.py",
  "        return max(min(capped, uncapped), -displaced)\n", "        return capped\n"),
 ("M12 DHW path bounds the start by baseline_cost", "optimizer.py",
  "            float(energy_cost_of(baseline_power)),\n", "            baseline_cost,\n"),
 ("M13 coverage factor unclamped", "ledger.py",
  "        return max(1.0, month_hours(now) / settled)\n", "        return month_hours(now) / settled\n"),
 ("M14 negative thermostat cost unclamped", "optimizer.py",
  "        displaced = max(0.0, space_baseline_cost) + max(0.0, -end_cost)\n",
  "        displaced = space_baseline_cost + max(0.0, -end_cost)\n"),
 ("M15 start surplus unclamped", "optimizer.py",
  "        return max(min(capped, uncapped), -displaced)\n", "        return max(uncapped, -displaced)\n"),
 ("M16 held slab below target", "optimizer.py",
  "        slab_temperature=target + max(0.0, q_floor) / model.params.slab_heat_transfer_floored,",
  "        slab_temperature=target + q_floor / model.params.slab_heat_transfer_floored,"),
 ("M8 settled hours never folded", "ledger.py",
  "        if dt > 0:\n            self.observe_meta_mean(when, SETTLED_HOURS_META, dt)\n",
  "        if False:\n            self.observe_meta_mean(when, SETTLED_HOURS_META, dt)\n"),
]

#: Mutants whose predicate the owner's one-basis acceptance removed from the
#: tree: the month row's actual is the metered savings line (not the bill,
#: ``month_cost`` is gone) and the capacity line is in neither column. The
#: degenerate form is now the required behaviour, so the mutant would assert
#: the fix's own answer; the checks pin it instead.
RETIRED = [
 ("M3 row actual from savings_actual", "the row's actual IS that line since #2492"),
 ("M6 capacity extrapolated", "capacity is in neither column since #2492"),
]

only = sys.argv[2:]
for name, f, old, new in [("M0 unmutated", "ledger.py", "", "")] + M:
    if only and name.split()[0] not in only:
        continue
    path = PKG / f
    orig = path.read_text()
    if old:
        assert orig.count(old) == 1, name
        path.write_text(orig.replace(old, new))
    try:
        out = subprocess.run([sys.executable, "-c", SECTION], cwd=ROOT, capture_output=True, text=True,
                             env={"PYTHONPATH": "tests/hastub:tests:custom_components", "PATH": "/usr/bin:/bin"})
    finally:
        path.write_text(orig)
    fails = [l.strip() for l in out.stdout.splitlines() if l.strip().startswith("FAIL")]
    print(f"{name}: rc={out.returncode} failing={len(fails)}", flush=True)
    for l in fails:
        print(f"    {l[:150]}", flush=True)
for name, why in RETIRED:
    if only and name.split()[0] not in only:
        continue
    print(f"{name}: RETIRED ({why})", flush=True)
