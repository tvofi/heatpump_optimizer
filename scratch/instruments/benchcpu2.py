"""benchcpu, one line per solve: the same seeded solve sequence at both ends,
so the two arms can be paired solve by solve instead of compared by medians.

usage: benchcpu2.py <tree-root> <harness-dir> [n]
"""
import importlib.util
import sys
import time

import numpy as np

ROOT, HDIR = sys.argv[1], sys.argv[2]
N = int(sys.argv[3]) if len(sys.argv) > 3 else 10
sys.path[:0] = [ROOT + "/tests", ROOT + "/tests/hastub",
                ROOT + "/custom_components", HDIR]

spec = importlib.util.spec_from_file_location("bufharness", HDIR + "/r10_buffer_store.py")
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)

for arm in ("owner_buffer_spread", "null_flat_nobuffer"):
    buffer_l, kind = h.ARMS[arm]
    rng = np.random.default_rng(2500)
    out = []
    for i in range(N):
        hourly = rng.uniform(0.4, 3.0, size=24)
        prices = np.repeat(hourly, 4) if kind == "spread" else h.FLAT
        outdoor = float(rng.uniform(-15.0, 8.0))
        t0 = time.process_time()
        h.solve(buffer_l, prices, outdoor)
        out.append(time.process_time() - t0)
    print(f"{arm} n={N} total {sum(out):.3f} cpu_s  per-solve "
          + " ".join(f"{v:.3f}" for v in out))
