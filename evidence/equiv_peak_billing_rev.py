#!/usr/bin/env python3
"""ARCH2-s2: P5 changes no capacity charge -- the record family against the baseline's, bit for bit.

Metric: count of (function, case) pairs whose float differs (repr) between the baseline tree's
        peak_cost / peak_cost_smooth / peak_cost_batch (positional arguments) and the working tree's
        (one PeakBilling record), over a seeded grid: window 15/60, dt 0.25, offsets 0..3, k 1..4,
        factors none/masked, distinct days on/off, plateaus (ties) and random plans, 4-row batches.
Count key: the returned floats, repr-compared (exact).
Instrumented symbols: tariff:peak_cost, tariff:peak_cost_smooth, tariff:peak_cost_batch.
Command:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch2-s2/equiv_peak_billing.py
          (run with P5 or the union applied to the working tree)
Perturbation: change ``bill.peaks_averaged`` to ``bill.peaks_averaged + 1`` in tariff._peak_charge;
          the mismatch count rises from 0.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


import os
REPO = Path(os.environ["EQ_HEAD"])
BASELINE = "9061fbd3d710d5894b7083d8a58b8203f9e7aa97"
sys.path.insert(0, str(REPO / "tools" / "audit"))

PROBE = r'''
import json, sys
import numpy as np
sys.path.insert(0, sys.argv[1])
from heatpump_optimizer import tariff as T
rec = hasattr(T, "PeakBilling")
rng = np.random.default_rng(7)
out = []
for win in (15, 60):
    for off in range(4):
        for k in (1, 2, 3, 4):
            for masked in (False, True):
                for dd in (True, False):
                    for kind in ("rand", "plateau"):
                        n = 96
                        plan = rng.uniform(0, 6, n) if kind == "rand" else np.where(rng.uniform(0, 1, n) > 0.6, 5.0, 1.0)
                        rows = np.stack([plan, plan * 0.9, np.roll(plan, 3), plan + 0.5])
                        base = np.full(n, 0.7)
                        nw = T.metering_windows(np.zeros(n), win, 0.25, off).size
                        fac = np.where(np.arange(nw) % 5 == 0, 0.5, 1.0) if masked else None
                        days = np.arange(nw) * win // 1440
                        args = (2.5, 20.0, win, 0.25, k, off)
                        kw = dict(window_factors=fac, window_days=days, distinct_days=dd)
                        if rec:
                            b = T.PeakBilling(*args, **kw)
                            vals = [T.peak_cost(plan, base, b), T.peak_cost_smooth(plan, base, b),
                                    *T.peak_cost_batch(rows, base, b).tolist()]
                        else:
                            vals = [T.peak_cost(plan, base, *args, **kw), T.peak_cost_smooth(plan, base, *args, **kw),
                                    *T.peak_cost_batch(rows, base, *args, **kw).tolist()]
                        out.append([repr(float(v)) for v in vals])
print(json.dumps(out))
'''


def run(pkg_parent: Path) -> list:
    r = subprocess.run([sys.executable, "-c", PROBE, str(pkg_parent)], capture_output=True, text=True,
                       env={"PYTHONPATH": str(REPO / "tests" / "hastub"), "OMP_NUM_THREADS": "1",
                            "PATH": "/usr/bin:/bin"})
    if r.returncode:
        raise SystemExit(r.stderr[-2000:])
    return json.loads(r.stdout)


def main() -> int:
    old = run(Path(os.environ["EQ_BASE"]) / "custom_components")
    new = run(REPO / "custom_components")
    pairs = sum(len(c) for c in old)
    bad = sum(1 for a, b in zip(old, new) for x, y in zip(a, b) if x != y)
    print(f"RESULT cases={len(old)} count")
    print(f"RESULT values_compared={pairs} count")
    print(f"RESULT mismatches={bad} count")
    return 1 if bad or len(old) != len(new) else 0


if __name__ == "__main__":
    raise SystemExit(main())
