#!/usr/bin/env python3
"""D3-s1 (box D3-top6): the k <= 0 guard of tariff._smooth_topk_sum, which the full gate does not pin.

Metric (one line): scalar_k0 = tariff._smooth_topk_sum(values, 0, tau) on a fixed 6-window excess
vector (expected 0.0 by the guard's contract); batch_k0 = the same through _smooth_topk_sum_batch
(the sibling guard); mismatch = 1 when scalar_k0 != batch_k0, else 0.
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/d931_probe.py [--mutant]
Expected at the baseline: scalar_k0=0.0, batch_k0=0.0, mismatch=0. With --mutant (R10 C2 M31, the
line `if x.size == 0 or k <= 0:` -> `k < 0`, applied in memory to a copy of the module source):
scalar_k0 = 1.473806 (the smooth top-1 of the 1.5 peak), mismatch=1. The full gate on that mutant (fullgate.py, key
d931ab195b940b0c) failed no check beyond its null control, so no suite check reads this value.
Instrumented symbol: custom_components.heatpump_optimizer.tariff:_smooth_topk_sum (and
_smooth_topk_sum_batch as the null arm, whose own guard is untouched).
Perturbation: --mutant moves scalar_k0 from 0.0 up to 1.473806 and mismatch 0 -> 1. Production callers (tariff.py L982, L1204) clamp k to >= 1 first, so the guard is unreachable there.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: owner macOS arm64. Counts/values exact.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import importlib.util
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT))
SRC = ROOT / "custom_components/heatpump_optimizer/tariff.py"
OLD = "    if x.size == 0 or k <= 0:"
NEW = "    if x.size == 0 or k < 0:"


def load(mutant: bool):
    import custom_components.heatpump_optimizer as pkg  # noqa: F401  (package context)
    # The baseline's own source (git show), so a gate's committed mutant in this worktree never leaks in.
    import subprocess
    text = subprocess.run(["git", "show", "92d38ecb640bd462f2e19c0814d0f0b7df1ee692:custom_components/heatpump_optimizer/tariff.py"],
                          cwd=ROOT, check=True, capture_output=True, text=True).stdout
    if mutant:
        lines = text.split("\n")
        idx = [i for i, ln in enumerate(lines) if ln == OLD]
        assert idx, "guard line not found"
        lines[idx[0]] = NEW  # the first occurrence is _smooth_topk_sum (L744)
        text = "\n".join(lines)
    spec = importlib.util.spec_from_loader("custom_components.heatpump_optimizer.tariff_probe", loader=None)
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = "custom_components.heatpump_optimizer"
    sys.modules[spec.name] = mod
    exec(compile(text, str(SRC), "exec"), mod.__dict__)
    return mod


def main() -> int:
    mutant = "--mutant" in sys.argv
    t = load(mutant)
    x = np.array([0.2, 1.5, 0.7, 0.0, 1.1, 0.4])
    s = float(t._smooth_topk_sum(x, 0, t._PEAK_SMOOTH_TAU))
    b = float(np.asarray(t._smooth_topk_sum_batch(x[None, :], 0, t._PEAK_SMOOTH_TAU)).ravel()[0])
    print(f"RESULT scalar_k0={s:.6f}")
    print(f"RESULT batch_k0={b:.6f}")
    print(f"RESULT mismatch={int(abs(s - b) > 1e-12)}")
    print("RESULT thread_factor=1.00")
    return 0


if __name__ == "__main__":
    sys.exit(main())
