"""Reviewer's CPU / call-count probe for #2445 (out of tree). Imports the census harness's cells verbatim."""
import sys, time, importlib.util
import numpy as np
spec = importlib.util.spec_from_file_location("census", sys.argv[1]); census = importlib.util.module_from_spec(spec); spec.loader.exec_module(census)
from heatpump_optimizer import optimizer as om
calls = {"relaxed": 0, "ms": 0}
orig_rel, orig_ms = om._relaxed_starts, om._multi_start_minimize
def rel(*a, **k):
    out = orig_rel(*a, **k); calls["relaxed"] += len(out) > len(a[6]); return out
def ms(*a, **k):
    calls["ms"] += 1; return orig_ms(*a, **k)
om._multi_start_minimize = ms
cells = [(tz, dhw, 1.0, out, 30.0) for tz in (False, True) for dhw in (False, True) for out in (-4.0, 2.0)]
for tag, prices in (("spread", census.SPREAD), ("flat", census.FLAT)):
    for cell in cells:
        row = []
        for relaxed in (False, True):
            best = 1e9
            for _ in range(3):
                calls.update(relaxed=0, ms=0)
                om._relaxed_starts = rel
                t = time.process_time(); census.solve(cell, prices, relaxed); best = min(best, time.process_time() - t)
            row.append((best, dict(calls)))
        (c0, k0), (c1, k1) = row
        print(f"{tag} tz={cell[0]:d} dhw={cell[1]:d} out={cell[3]:+.0f}: control {c0:.2f}s fix {c1:.2f}s delta {c1-c0:+.2f}s ratio {c1/c0:.2f}  multistarts {k1['ms']} relaxed-passes {k1['relaxed']}", flush=True)
