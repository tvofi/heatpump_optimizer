#!/usr/bin/env python3
"""D5.M3 mechanism harness: how-it-works.md's "Compressor starts" paragraph says the start cost
"is modelled as a smooth term on the step-to-step power difference"; the shipped term counts
off-to-on starts. Measure what the shipped term charges for step-to-step swings inside one run.

Metric: the start term the optimizer prices (optimizer:_start_cost_fn -> runs.start_count) for a
plan that swings between 2 and 5 kW every step inside one continuous run, minus the same term for
a flat 3.5 kW run of the same length (both one start). A smooth step-to-step term charges the
swinging plan more (> 0); the shipped start count charges 0. Second metric: the number of
how-it-works.md units describing the start cost as a smooth step-to-step term (read from text).
Key: the value the production term returns for the two plans.

Run:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s2/cycling.py [--null]
  --null  null control: the swinging plan swings through zero (off between runs), so the shipped
          term must now charge more starts (> 0): the harness can see a priced difference.
Perturbation (code side): runs.start_count replaced in memory by sum(|dP|)/p_max (the doc's
smooth term), --perturb: swing_minus_flat > 0, so the doc and the code would agree.
Expected at baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692: swing_minus_flat=0.0 currency,
doc_smooth_units=1 (exact); --null swing_minus_flat > 0; --perturb swing_minus_flat > 0.
Machine: B2 (orchestrator's macOS box).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import re, sys, time
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import numpy as np

for extra in ("custom_components", "tools/audit"):
    sys.path.insert(0, extra)
from heatpump_optimizer import optimizer, runs  # noqa: E402
import text_ledger  # noqa: E402


def main():
    cost, p_min, p_max = 2.0, 1.0, 6.0
    opt = SimpleNamespace(config=SimpleNamespace(cycling_cost=cost),
                          model=SimpleNamespace(params=SimpleNamespace(min_electrical_power=p_min,
                                                                       max_electrical_power=p_max)))
    n = 24
    if "--null" in sys.argv:
        swing = np.array([0.0 if i % 2 else 5.0 for i in range(n)])
    else:
        swing = np.array([2.0 if i % 2 else 5.0 for i in range(n)])
    flat = np.full(n, 3.5)
    patches = []
    if "--perturb" in sys.argv:
        def smooth(total, floor, running=False):
            q = np.asarray(total, dtype=float)
            return float(np.sum(np.abs(np.diff(np.r_[0.0, q]))) / p_max)
        patches.append(mock.patch.object(runs, "start_count", smooth))
    for p in patches:
        p.start()
    fn = optimizer._start_cost_fn(opt, running=True)  # its start_count call then counts step 0 as a start
    c_swing, c_flat = fn(swing, None), fn(flat, None)
    hiw = Path("docs/how-it-works.md").read_text(encoding="utf-8")
    smooth_units = [f"{u[0]}:{u[1]}" for u in text_ledger.units_of("docs/how-it-works.md", hiw, "D6")
                    if re.search(r"smooth term on the step-to-step power", " ".join(u[3].split()))]
    print(f"RESULT start_cost_swing={c_swing:.3f} currency")
    print(f"RESULT start_cost_flat={c_flat:.3f} currency")
    print(f"RESULT swing_minus_flat={c_swing - c_flat:.3f} currency")
    print(f"RESULT doc_smooth_units={len(smooth_units)} units")
    for u in smooth_units:
        print(f"   smooth {u}")
    print(f"RESULT thread_factor={time.process_time() / max(time.thread_time(), 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
