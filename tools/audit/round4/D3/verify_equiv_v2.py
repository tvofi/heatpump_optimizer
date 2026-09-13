#!/usr/bin/env python3
"""D3 round-4 verify-0-2 -- equivalence probes for M22 (tariff.py:507) and
M32 (optimizer.py:1549).

METRIC: max absolute output difference between the original function and the
mutant variant (the pool's exact `new` line applied to the function source,
exec'd in the module's own namespace), over adversarial inputs that maximise
the mutant's chance of mattering: k at/near/above the array size, and
lookahead windows that run past the end of the array.

RUN (from the repository root):
    PYTHONPATH=tests/hastub python3 tools/audit/round4/D3/verify_equiv_v2.py

EXPECTED: RESULT m22_max_abs_diff_int_k=<float> (equivalence for every integer
k >= 1 iff 0.0 or numerically negligible), RESULT m22_fractional_k_diff=<float>
(the only shape that can differ), RESULT m32_weights_identical=<bool>.

BASELINE: pool drawn at 7dd68dd327fe3dbfb09f3bd0fe38910c58877697.
MACHINE: 8-core Apple M1, 8 GB, macOS 25.6.0, python 3.11, OpenBLAS.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import inspect
import sys

sys.path.insert(0, "custom_components")

import numpy as np  # noqa: E402


def variant(module, fn_name: str, old: str, new: str):
    """The same function with one line swapped, exec'd in the module's ns."""
    import textwrap
    src = textwrap.dedent(inspect.getsource(getattr(module, fn_name)))
    core_old, core_new = old.strip(), new.strip()
    lines = src.splitlines(True)
    hits = [i for i, ln in enumerate(lines) if ln.strip() == core_old]
    assert len(hits) == 1, f"{core_old!r} not unique in {fn_name}: {len(hits)}"
    lines[hits[0]] = lines[hits[0]].replace(core_old, core_new)
    mod = sys.modules[module.__module__] if isinstance(module, type) else module
    ns = dict(vars(mod))
    exec(compile("".join(lines), f"<{fn_name}-mutant>", "exec"), ns)
    return ns[fn_name]


# --- M22: tariff._smooth_topk_sum, clamp line dropped -----------------------
import heatpump_optimizer.tariff as tariff  # noqa: E402

orig_topk = tariff._smooth_topk_sum
mut_topk = variant(tariff, "_smooth_topk_sum",
                   "    k = max(1, min(int(k), x.size))", "    pass")

rng = np.random.default_rng(20260912)
cases = []
for size in (1, 2, 3, 5, 24, 96):
    for style in ("separated", "tied", "onehot"):
        x = {
            "separated": rng.uniform(0.1, 9.0, size),
            "tied": np.full(size, 4.0),
            "onehot": np.where(np.arange(size) == size // 2, 8.0, 0.5),
        }[style]
        for k in list(range(1, size * 3 + 1)) + [size, size + 1, size * 2]:
            cases.append((x, int(k)))
        cases.append((x, 1))
max_diff_int = 0.0
worst = None
for x, k in cases:
    a = orig_topk(x, k, 0.05)
    b = mut_topk(x, k, 0.05)
    d = abs(a - b)
    if d > max_diff_int:
        max_diff_int, worst = d, (x.tolist()[:4], k, a, b)
frac_diff = abs(orig_topk(np.array([3.0, 1.0]), 0.5, 0.05)
                - mut_topk(np.array([3.0, 1.0]), 0.5, 0.05))

print(f"RESULT m22_cases={len(cases)} count")
print(f"RESULT m22_max_abs_diff_int_k={max_diff_int:.3e} max_abs_diff worst={worst}")
print(f"RESULT m22_fractional_k_diff={frac_diff:.6f} abs_diff (k=0.5, unreachable from callers)")

# Also: through peak_cost the k is pre-clamped at tariff.py:593 before the
# call at :601 -- show it on a plateau case (the only path that reaches 507).
from heatpump_optimizer.tariff import peak_cost  # noqa: E402
plateau = np.full(24, 7.0)
print(f"RESULT m22_peak_cost_plateau_paths="
      f"{peak_cost(plateau, np.zeros(24), 6.0, 20.0, 60, 1.0, 3):.6f}")

# --- M32: optimizer._anticipatory_weights, end-clamp dropped ----------------
from heatpump_optimizer.optimizer import HeatPumpOptimizer  # noqa: E402

orig_w = HeatPumpOptimizer._anticipatory_weights
mut_w = variant(HeatPumpOptimizer, "_anticipatory_weights",
                "            end = min(i + lookahead, n_steps)",
                "            end = (i + lookahead)")

identical = True
for n_steps, dt in ((10, 0.25), (5, 0.25), (96, 0.25), (24, 1.0), (8, 2.0), (6, 8.0), (4, 16.0)):
    solar = rng.uniform(0.0, 2.0, n_steps)
    loss = rng.uniform(0.8, 1.6, n_steps)
    a = orig_w(None, n_steps, dt, solar, loss)
    b = mut_w(None, n_steps, dt, solar, loss)
    same = np.array_equal(a, b)
    identical = identical and same
    print(f"  n_steps={n_steps} dt={dt} lookahead={int(8 / dt)} identical={same}")
print(f"RESULT m32_weights_identical={identical} bool")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
