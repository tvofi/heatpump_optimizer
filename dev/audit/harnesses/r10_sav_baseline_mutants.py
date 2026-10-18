#!/usr/bin/env python3
"""R10-SAV-BASELINE (#2255) mutation proof: each mutant applied in turn, the #2255 checks re-run, restored.

The checks are the "3L-G7 -- monthly savings history" section of tests/features.py (which holds
the #2255 checks), extracted and run alone so a mutant costs minutes, not the full script. Each
mutant replaces one predicate of the fix with its pre-fix or degenerate form; a mutant no check
fails is printed with failing=0. M0 is the unmutated null run. Run it on a scratch copy of the
tree: it rewrites a production file per mutant and restores it in a `finally`.

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
start = src.index('R.section("3L-G7 \u2014 monthly savings history")')
end = src.index('import inspect as _sav_inspect', start)
exec(compile(src[start:end], 'features_2255', 'exec'))
sys.exit(R.close('2255'))
"""
M = [
 ("M1 baseline starts from the plan's state", "optimizer.py",
  "        state = _thermostat_held_state(\n            self.model, initial_state, weather,\n            _baseline_target(comfort_targets, 0, self.config.target_temp),\n        )\n",
  "        state = initial_state\n"),
 ("M2 held slab without its demand term", "optimizer.py",
  "        slab_temperature=target + max(0.0, q_floor) / model.params.slab_heat_transfer_floored,", "        slab_temperature=target,"),
 ("M3 row actual from savings_actual", "ledger.py",
  "            actual_sek = self.month_cost(key)\n", '            actual_sek = float(self.line(key, "savings_actual")["sek"])\n'),
 ("M4 coverage factor -> calendar day", "ledger.py",
  "            return max(1.0, month_hours(now) / settled)\n", "            return pro_rata_factor(now)\n"),
 ("M5 savings priced at spot only", "ledger.py",
  "            spot=spot + fee_per_kwh,\n", "            spot=spot,\n"),
 ("M6 capacity extrapolated", "ledger.py",
  "                actual_sek = (actual_sek - capacity) * factor + capacity\n", "                actual_sek = actual_sek * factor\n"),
 ("M7 metered energy without immersion", "ledger.py",
  'ENERGY_LINES = ("spot", "immersion")\n', 'ENERGY_LINES = ("spot",)\n'),
 ("M9 no start settlement (space path)", "optimizer.py",
  "        ) - self._start_gap_cost(\n            initial_state, weather, comfort_targets, prices, outdoor_temps,\n            space_caps, h.humidity, baseline_cost,  # the space-only reference\n        )\n",
  "        )\n"),
 ("M10 start debit unbounded", "optimizer.py",
  "        return capped - min(surplus_above_caps, max(0.0, space_baseline_cost))", "        return capped - surplus_above_caps"),
 ("M11 start settled at the caps only", "optimizer.py",
  "        return capped - min(surplus_above_caps, max(0.0, space_baseline_cost))", "        return capped"),
 ("M12 DHW path bounds the start by baseline_cost", "optimizer.py",
  "            float(energy_cost_of(baseline_power)),\n", "            baseline_cost,\n"),
 ("M8 settled hours never folded", "ledger.py",
  "        if dt > 0:\n            self.observe_meta_mean(when, SETTLED_HOURS_META, dt)\n",
  "        if False:\n            self.observe_meta_mean(when, SETTLED_HOURS_META, dt)\n"),
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
